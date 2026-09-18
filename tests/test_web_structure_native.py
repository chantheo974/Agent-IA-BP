"""Exercise the actual supervisor with a bounded fake worker; no Excel claim."""
import io
import json
import queue
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tca_bp.storage import digest
from tca_bp.web_structure import _run_native


class Stream(io.StringIO):
    def close(self):self.saved=self.getvalue();super().close()


class Process:
    def __init__(self,args,*,bad_receipt=False,events=None,**kwargs):
        request=json.loads(Path(args[-1]).read_text(encoding='utf-8'))
        self.request=request;self.returncode=None;self.killed=False
        self.stdin=Stream();self.stderr=io.StringIO('')
        messages=events or [{'event':'owned_process','pid':4321},{'event':'progress'},{'event':'saved'}]
        self.stdout=io.StringIO('\n'.join(json.dumps(m) for m in messages)+'\n')
        Path(request['output']).write_bytes(b'fictitious output')
        receipt={'source_sha256':digest(request['source']),'output_sha256':digest(request['output']),
                 'macros_enabled':False,'reference_repairs':request['reference_repairs']}
        if bad_receipt:receipt.pop('macros_enabled')
        Path(request['receipt']).write_text(json.dumps(receipt),encoding='utf-8')
    def poll(self):return self.returncode
    def wait(self,timeout=None):self.returncode=0;return 0
    def kill(self):self.killed=True;self.returncode=-1


class Owned:
    def __init__(self,pid):self.pid=pid;self.terminated=False;self.closed=False
    def terminate(self):self.terminated=True
    def close(self):self.closed=True


class StructureNativeSupervisor(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'source.xlsm';self.source.write_bytes(b'fictitious source')
    def run_worker(self,*,bad_receipt=False,previous=(),owner_error=False,events=None):
        self.process=None;self.owned=None
        def process(*args,**kwargs):
            self.process=Process(*args,bad_receipt=bad_receipt,events=events,**kwargs);return self.process
        def own(pid):
            if owner_error:raise ValueError('No process handle')
            self.owned=Owned(pid);return self.owned
        with patch('tca_bp.web_structure.subprocess.Popen',side_effect=process),\
             patch('tca_bp.wacc_native.existing_excel_pids',return_value=set(previous)),\
             patch('tca_bp.wacc_native.OwnedExcelProcess',side_effect=own):
            return _run_native(self.source,self.root/'output.xlsm',[],timeout=1)
    def test_handshake_receipt_and_successful_cleanup(self):
        result=self.run_worker()
        self.assertIs(result['macros_enabled'],False)
        self.assertEqual(json.loads(self.process.stdin.saved),{'operation':'ownership_confirmed'})
        self.assertFalse(self.owned.terminated);self.assertTrue(self.owned.closed)
        self.assertFalse(self.process.killed)
    def test_existing_pid_is_never_owned_or_killed(self):
        with self.assertRaisesRegex(ValueError,'dédiée'):self.run_worker(previous=[4321])
        self.assertIsNone(self.owned);self.assertTrue(self.process.stdin.closed)
        self.assertFalse(self.process.killed)
    def test_ownership_failure_releases_worker_by_eof(self):
        with self.assertRaisesRegex(ValueError,'handle'):self.run_worker(owner_error=True)
        self.assertTrue(self.process.stdin.closed);self.assertFalse(self.process.killed)
    def test_absent_macro_attestation_refuses_receipt_and_terminates_only_owned(self):
        with self.assertRaisesRegex(ValueError,'incohérent'):self.run_worker(bad_receipt=True)
        self.assertTrue(self.owned.terminated);self.assertTrue(self.owned.closed)
    def test_failure_after_ownership_terminates_only_owned(self):
        events=[{'event':'owned_process','pid':4321},{'event':'error','error':'native failure'}]
        with self.assertRaisesRegex(ValueError,'native failure'):self.run_worker(events=events)
        self.assertTrue(self.owned.terminated);self.assertTrue(self.process.killed)
    def test_timeout_after_handshake_terminates_only_owned(self):
        class TimeoutQueue:
            calls=0
            def put(self,message):pass
            def get(self,timeout=None):
                self.calls+=1
                if self.calls==1:return {'event':'owned_process','pid':4321}
                raise queue.Empty
        with patch('tca_bp.web_structure.queue.Queue',return_value=TimeoutQueue()):
            with self.assertRaisesRegex(ValueError,'Délai maximal'):self.run_worker()
        self.assertTrue(self.owned.terminated);self.assertTrue(self.owned.closed)


if __name__=='__main__':unittest.main()
