"""Case context, private specialist audit and repeated draft boundary checks."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from tca_bp.service import Application
from tca_bp.storage import canonical
from tca_bp.vendor import input_engine as core
from tca_bp.web_chat import ChatError
from tca_bp.web_workspace import WebWorkspace
from tests.test_service import FakeEngine


class WebContextTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.app=Application(self.root,self.root/'data',engine=FakeEngine(self.root))
        self.app.create_case('Client A','Dossier A',case_id='case_a')
        self.work=WebWorkspace(self.app)
        self.addCleanup(self.work.close)
        self.windows=[]
        def cells(case_id,sheet,row=1,column=1,rows=100,columns=26):
            self.windows.append((row,column,rows,columns))
            return {'sheet':sheet,'revision':self.app._row(case_id)['revision'],
                    'cells':[{'cell':core.colname(c)+str(r),'row':r,'column':c,'value':r+c,
                              'formula':None,'source':None,'calculation_status':'A_RECALCULER'}
                             for r in range(row,row+rows) for c in range(column,column+columns)]}
        self.work.cells=cells
        self.work.agents=lambda case_id:[{'id':'agent_entries','sheet':'Entrées','role':'Qualifier les entrées.'}]

    def test_entire_selected_window_scanned_and_provider_omissions_reported(self):
        context=self.work.chat_context('case_a',{'sheet':'Entrées','range':'A1:GR5'},'Explique les valeurs sélectionnées.')
        self.assertEqual(sum(rows*columns for _,_,rows,columns in self.windows),1000)
        self.assertEqual(context['selection_summary']['scanned_cell_count'],1000)
        self.assertEqual(context['selection_summary']['included_cell_count'],500)
        self.assertEqual(context['selection_summary']['omitted_cell_count'],500)
        self.assertEqual(len(context['cells']),500)
        self.assertFalse(context['selection_summary']['whole_sheet_scope'])

    def test_sheet_scope_does_not_claim_to_read_entire_sheet(self):
        context=self.work.chat_context('case_a',{'sheet':'Entrées'},'Explique cette feuille.')
        summary=context['selection_summary']
        self.assertTrue(summary['whole_sheet_scope'])
        self.assertEqual(summary['ranges_read'],['A1:Z80'])
        self.assertEqual(summary['scanned_cell_count'],2080)
        self.assertIn('extraits',summary['note'])

    def test_sources_are_useful_excerpts_with_current_request_first(self):
        source=self.app.add_source('case_a',text='Introduction. '*600+'SALAIRE brut documenté de 2 000 euros. '+'Fin. '*300,title='Salaires et recrutements')
        context=self.work.chat_context('case_a',{'sheet':'Entrées','range':'A1:B2'},'Examine le salaire brut.')
        self.assertEqual(context['sources'][0]['id'],context['user_source_id'])
        excerpt=next(item for item in context['sources'] if item['id']==source['id'])
        self.assertIn('SALAIRE brut',excerpt['text'])
        self.assertGreater(excerpt['excerpt_start'],0)
        self.assertLessEqual(len(excerpt['text']),3000)
        self.assertTrue(excerpt['excerpt_only'])
        self.assertNotIn('path',excerpt)
        self.assertEqual(excerpt['case_id'],'case_a')

    def test_context_detects_workbook_change_during_window_read(self):
        real=self.work.cells
        def stale(*args,**kwargs):
            value=real(*args,**kwargs)
            value['revision']+=1
            return value
        self.work.cells=stale
        with self.assertRaisesRegex(ValueError,'changé'):
            self.work.chat_context('case_a',{'sheet':'Entrées','range':'A1:B2'},'Explique.')

    def test_field_contract_and_register_are_available_to_agents(self):
        catalog=self.app.engine.catalog()
        self.app.engine_for_case=lambda case_id:SimpleNamespace(catalog=lambda:catalog,schema={'registers':{'Entrées':{'start_row':1,'end_row':20,'required':['A','B']}}})
        context=self.work.chat_context('case_a',{'sheet':'Entrées','range':'A1:B2'},'Complète le registre.')
        self.assertEqual(context['fields'][0]['id'],'amount')
        self.assertEqual(context['register']['required'],['A','B'])

    def test_queued_chat_bound_to_old_revision_refused_before_creating_source(self):
        previous=self.app._row('case_a')
        with self.app.store.connection() as db:
            db.execute('UPDATE cases SET revision=1 WHERE id=?',('case_a',))
        with self.assertRaisesRegex(ValueError,'depuis l’envoi'):
            self.work.run_job({'case_id':'case_a','kind':'chat','id':'job_test'},
                              {'message':'Change la cellule','selection':{'sheet':'Entrées'},
                               'expected_revision':previous['revision'],'source_sha256':previous['sha256']},lambda event:None)
        self.assertEqual(self.work.messages('case_a'),[])
        self.assertEqual(self.app.get_case('case_a')['sources'],[])

    def test_revalidation_refuses_persisted_operation_outside_original_scope(self):
        draft=self.work.add_operations('case_a',[{'type':'set_value','sheet':'Entrées','cell':'A1','value':7}],{'sheet':'Entrées','range':'A1:A2'})
        payload={'operations':deepcopy(draft['operations'])}
        self.assertEqual(self.work._validate_draft_operations('case_a',payload)[0]['value'],7)
        payload['operations'][0]['cell']='B5'
        with self.assertRaisesRegex(ValueError,'sélectionnées'):
            self.work._validate_draft_operations('case_a',payload)
        payload['operations'][0]['cell']='A1'
        payload['operations'][0].pop('_scope')
        with self.assertRaisesRegex(ValueError,'périmètre'):
            self.work._validate_draft_operations('case_a',payload)

    def test_revalidation_rechecks_changed_source_bytes(self):
        draft=self.work.add_operations('case_a',[{'type':'set_value','sheet':'Entrées','cell':'A1','value':7}],{'sheet':'Entrées','range':'A1:A2'})
        evidence=draft['operations'][0]['evidence_id']
        with self.app.store.connection() as db:
            db.execute('UPDATE sources SET text=? WHERE id=?',('source changée après aperçu',evidence))
        with self.assertRaisesRegex(ValueError,'changé'):
            self.work._validate_draft_operations('case_a',{'operations':draft['operations']})

    def test_specialist_transcript_survives_provider_failure_and_is_private(self):
        transcript={'agent_id':'agent_entries','task':'Relire le salaire',
                    'provider_messages':[{'role':'assistant','content':'Donnée analysée.','reasoning_content':'opaque_private_specialist_reasoning'}]}
        history=[{'role':'user','content':'Expliquer'},{'role':'assistant','content':'','reasoning_content':'opaque_private_coordinator_reasoning'}]
        class InterruptedChat:
            def run(self,message,selection,context,**kwargs):
                kwargs['checkpoint'](history)
                kwargs['tool_checkpoint'](transcript)
                raise ChatError('Fournisseur interrompu.',code='PROVIDER_NETWORK',retryable=True,
                                provider_messages=history,tool_runs=[transcript])
        self.work.chat=InterruptedChat()
        with self.assertRaises(ChatError):
            self.work.run_job({'case_id':'case_a','kind':'chat','id':'job_test'},
                              {'message':'Expliquer','selection':{'sheet':'Entrées','range':'A1:B2'}},lambda event:None)
        with self.app.store.connection() as db:
            transcripts=db.execute('SELECT * FROM web_tool_runs WHERE case_id=?',('case_a',)).fetchall()
            self.assertEqual(len(transcripts),1)
            self.assertIn('opaque_private_specialist_reasoning',transcripts[0]['private_context'])
            message=db.execute("SELECT * FROM web_messages WHERE role='assistant'").fetchone()
            self.assertEqual(message['status'],'FAILED')
            self.assertIn('opaque_private_coordinator_reasoning',message['private_context'])
        public=canonical(self.work.messages('case_a'))
        self.assertNotIn('opaque_private',public)
        self.assertEqual(self.work.draft('case_a')['status'],'EMPTY')


if __name__=='__main__':
    unittest.main()
