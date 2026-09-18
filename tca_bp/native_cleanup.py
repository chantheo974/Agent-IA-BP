"""Close the dedicated worker without guessing which Excel process it owns."""
from __future__ import annotations

import subprocess
import threading


def finish_native_process(process, owned, complete, *, grace_seconds=10):
    """EOF lets a worker finish its COM creation and close its own instance.

    Before ownership acknowledgement the worker cannot touch a workbook. If COM
    creation is still pending, killing PowerShell would orphan the new Excel
    process. Keep that worker alive to reach EOF/finally and reap it in the
    background. Never enumerate and kill newly appeared Excel PIDs.
    """
    try:
        try:
            if process.stdin and not getattr(process.stdin, 'closed', False):
                process.stdin.close()
        except (OSError, ValueError):
            pass
        if not complete and owned:
            owned.terminate()
            if process.poll() is None:
                process.kill()
        try:
            process.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            if owned:
                process.kill()
                process.wait(timeout=10)
            else:
                def reap():
                    process.wait()
                threading.Thread(target=reap, daemon=True, name='tca-native-eof-cleanup').start()
    finally:
        if owned:
            owned.close()
