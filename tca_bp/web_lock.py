"""Process-wide serialization shared by local web and MCP Excel operations."""
from __future__ import annotations
import contextlib
import functools
import os
import threading

_thread_lock=threading.RLock()


@contextlib.contextmanager
def excel_lock():
    with _thread_lock:
        if os.name!='nt':
            yield
            return
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateMutexW.argtypes=(ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR)
        kernel.CreateMutexW.restype=wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD)
        kernel.WaitForSingleObject.restype=wintypes.DWORD
        kernel.ReleaseMutex.argtypes=(wintypes.HANDLE,)
        kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
        handle=kernel.CreateMutexW(None,False,'Local\\TCA_BP_Excel_Queue_v1')
        if not handle:
            raise ValueError('Impossible de réserver le moteur Excel.')
        acquired=False
        try:
            result=kernel.WaitForSingleObject(handle,3600000)
            if result not in (0,0x80):
                raise ValueError('Un calcul Excel est encore en cours. Relancer ce travail ensuite.')
            acquired=True
            yield
        finally:
            if acquired:
                kernel.ReleaseMutex(handle)
            kernel.CloseHandle(handle)


def serialized_excel(function):
    @functools.wraps(function)
    def run(*args,**kwargs):
        with excel_lock():
            return function(*args,**kwargs)
    return run


class ServerLease:
    """An OS-held file lock releases on crash; no stale-PID deletion needed."""
    def __init__(self,path):
        self.path=path
        self.stream=None

    def acquire(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        stream=self.path.open('a+b')
        stream.seek(0,2)
        if not stream.tell():
            stream.write(b'0');stream.flush()
        stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            stream.close()
            raise ValueError('Un serveur TCA BP Web utilise déjà ces dossiers.') from None
        self.stream=stream

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream=None
