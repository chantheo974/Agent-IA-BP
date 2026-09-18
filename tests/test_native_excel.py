"""Supervision du recalcul ordinaire simulée ; aucune application native."""
import io
import json
import math
from pathlib import Path
import queue
import tempfile
import unittest
from unittest.mock import patch
from tca_bp import native_excel as native
from tca_bp.storage import digest


def receipt_values(source_sha='source',output_sha='output',tables=False,pid=72):
    return {'status':'RECALCULE','method':'CalculateFullRebuild','application':'Microsoft Excel','version':'SIMULEE',
            'source_sha256':source_sha,'output_sha256':output_sha,'calculation_state':0,
            'macros_enabled':False,'events_enabled':False,'iteration_enabled':False,'iteration_initial':False,
            'source_preserved':True,'save_reopen_verified':True,'owned_process_confirmed':True,
            'dedicated_instance_verified':True,'links_update_requested':False,'wacc_macro':'NON_EXECUTEE',
            'sensitivity_tables':'RECALCUL_DEMANDE' if tables else 'NON_VERIFIEES',
            'economic_validation':'NON_EFFECTUEE','include_tables':tables,'base_cell_writes':[],
            'owned_excel_pid':pid}


class ReceiptTests(unittest.TestCase):
    def test_valid_receipts_keep_table_request_distinct_from_validation(self):
        for tables in (False,True):native.validate_receipt(receipt_values(tables=tables),'source','output',tables,72)

    def test_bool_flags_hashes_states_and_scope_are_strict(self):
        mutations={'status':'TABLES_VERIFIEES','method':'VBA','application':'Other','version':None,
                   'source_sha256':'changed','output_sha256':'changed','calculation_state':False,
                   'macros_enabled':0,'events_enabled':0,'iteration_enabled':0,'iteration_initial':0,
                   'source_preserved':1,'save_reopen_verified':'true','owned_process_confirmed':1,
                   'dedicated_instance_verified':'true','links_update_requested':0,'wacc_macro':'EXECUTEE',
                   'sensitivity_tables':'VERIFIEES','economic_validation':'CERTIFIE','include_tables':0,
                   'base_cell_writes':['D136'],'owned_excel_pid':True}
        for key,value in mutations.items():
            with self.subTest(key=key),self.assertRaises(ValueError):
                native.validate_receipt({**receipt_values(),key:value},'source','output',False,72)
        for key,value in [('calculation_state',0.0),('owned_excel_pid',72.0)]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                native.validate_receipt({**receipt_values(),key:value},'source','output',False,72)


class Owned:
    def __init__(self):self.terminated=False;self.closed=False
    def terminate(self):self.terminated=True
    def close(self):self.closed=True


class Worker:
    def __init__(self,source,output,receipt,*,changes=None,stall=False,error=None,pid=72,tables=False):
        self.source=source;self.output=output;self.receipt=receipt;self.changes=changes or {};self.stall=stall
        self.error=error;self.pid=pid;self.tables=tables;self.returncode=None;self.killed=False;self.sent=[]
        self.events=queue.Queue();self.events.put({'event':'owned_process','pid':pid})
        self.stdout=self.lines();self.stderr=io.StringIO();self.stdin=self
    def lines(self):
        while True:
            event=self.events.get()
            if event is None:return
            yield json.dumps(event)+'\n'
    def write(self,text):
        self.sent.append(json.loads(text))
        if self.sent[-1]!={'operation':'ownership_confirmed'}:raise AssertionError('Commande libre interdite.')
        if self.stall:return
        if self.error:self.events.put({'event':'error','error':self.error})
        else:
            self.output.write_bytes(b'COPIE_FACTICE_DE_TEST')
            value=receipt_values(digest(self.source),digest(self.output),tables=self.tables,pid=self.pid)
            value.update(self.changes)
            self.receipt.write_text(json.dumps(value),encoding='utf-8')
            self.events.put({'event':'saved'})
        self.returncode=0;self.events.put(None)
    def flush(self):pass
    def close(self):
        self.input_closed=True
        if self.returncode is None:
            self.returncode=0;self.events.put(None)
    def poll(self):return self.returncode
    def wait(self,timeout):return self.returncode
    def kill(self):self.killed=True;self.returncode=-9;self.events.put(None)


class RecalculationProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name);self.source=self.folder/'source.xlsm'
        self.output=self.folder/'output.xlsm';self.receipt=self.folder/'receipt.json'
        self.source.write_bytes(b'SOURCE_FACTICE_INCHANGEABLE');self.source_sha=digest(self.source)
        self.owned=Owned()
        self.proof={'constant_input_signature':'inputs','mechanical_signature':'mechanics','vba_compatibility_signature':'vba'}

    def run_worker(self,worker,*,previous=None,after=None,timeout=3,tables=False):
        self.factory=lambda pid:self.owned
        with patch.object(native,'available',return_value=True), \
             patch.object(native,'workbook_proof',side_effect=[self.proof,after or self.proof]), \
             patch.object(native,'_process_helpers',return_value=(self.factory,lambda:previous or set())), \
             patch.object(native.subprocess,'Popen',return_value=worker):
            return native.recalculate(self.source,self.output,self.receipt,timeout=timeout,include_tables=tables)

    def test_success_keeps_source_inputs_and_nonadopted_receipt(self):
        worker=Worker(self.source,self.output,self.receipt)
        result=self.run_worker(worker)
        self.assertEqual(worker.sent,[{'operation':'ownership_confirmed'}])
        self.assertTrue(result['inputs_unchanged']);self.assertFalse(result['adopted'])
        self.assertFalse(self.owned.terminated);self.assertTrue(self.owned.closed)
        self.assertEqual(digest(self.source),self.source_sha)

    def test_preexisting_process_is_never_acknowledged_or_terminated(self):
        worker=Worker(self.source,self.output,self.receipt)
        with self.assertRaisesRegex(ValueError,'préexistante'):self.run_worker(worker,previous={72})
        self.assertFalse(worker.sent);self.assertTrue(worker.input_closed)
        self.assertFalse(worker.killed)
        self.assertFalse(self.owned.terminated);self.assertFalse(self.owned.closed)
        self.assertFalse(self.output.exists());self.assertEqual(digest(self.source),self.source_sha)

    def test_timeout_terminates_only_the_owned_handle(self):
        worker=Worker(self.source,self.output,self.receipt,stall=True)
        with self.assertRaisesRegex(ValueError,'délai'):self.run_worker(worker,timeout=1)
        self.assertTrue(self.owned.terminated);self.assertTrue(self.owned.closed);self.assertTrue(worker.input_closed)
        self.assertFalse(self.output.exists());self.assertEqual(digest(self.source),self.source_sha)

    def test_worker_iteration_failure_cannot_save(self):
        worker=Worker(self.source,self.output,self.receipt,error='Itération circulaire globale active')
        with self.assertRaisesRegex(ValueError,'Itération'):self.run_worker(worker)
        self.assertFalse(self.output.exists());self.assertTrue(self.owned.terminated)

    def test_malformed_proof_and_changed_inputs_are_rejected(self):
        worker=Worker(self.source,self.output,self.receipt,changes={'save_reopen_verified':'false'})
        with self.assertRaises(ValueError):self.run_worker(worker)
        self.assertTrue(self.owned.terminated)
        self.assertFalse(json.loads((self.folder/'receipt.echec.json').read_text(encoding='utf-8'))['adopted'])

    def test_semantic_change_cannot_be_adopted(self):
        worker=Worker(self.source,self.output,self.receipt)
        with self.assertRaisesRegex(ValueError,'entrées'):
            self.run_worker(worker,after={**self.proof,'constant_input_signature':'changed'})
        self.assertEqual(digest(self.source),self.source_sha)
        self.assertTrue(self.owned.terminated)

    def test_invalid_timeout_flags_and_paths_never_start_native(self):
        with patch.object(native.subprocess,'Popen') as launch,patch.object(native,'available',return_value=True):
            for timeout in (False,0,3601,math.inf):
                with self.subTest(timeout=timeout),self.assertRaises(ValueError):
                    native.recalculate(self.source,self.output,self.receipt,timeout=timeout)
            with self.assertRaises(ValueError):native.recalculate(self.source,self.output,self.receipt,include_tables='false')
            with self.assertRaises(ValueError):native.recalculate(self.source,self.output,self.output)
            launch.assert_not_called()


if __name__=='__main__':unittest.main()
