from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from tca_bp.service import Application
from tca_bp.web_workspace import WebWorkspace
from tca_bp.web_server import create_app
from tca_bp.storage import digest
from tca_bp.decision_actuals import preview_actuals,read_import
from tests.test_service import FakeEngine


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.app=Application(self.root,self.root/'data',engine=FakeEngine(self.root))
        self.app.create_case('Fictif','Services',case_id='case_a')
        self.app.create_case('Fictif B','Négoce',case_id='case_b')
        self.work=WebWorkspace(self.app)
        self.api=create_app(self.app,workspace=self.work,start_jobs=False)
        self.d=self.api.state.decision
        self.client=TestClient(self.api,base_url='http://127.0.0.1:8765')

    def tearDown(self):
        self.client.close(); self.work.close(); self.tmp.cleanup()

    def test_schema_backup_and_profile_calendar_validation(self):
        self.assertEqual(len(list((self.root/'data'/'backups').glob('*.sqlite3'))),1)
        body={'profile':{'activity':'Services','start_year':2027,'years':10,'activity_start_month':4},'expected_revision':0,'request_id':'profile_1'}
        result=self.client.put('/api/cases/case_a/profile',json=body)
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(self.client.put('/api/cases/case_a/profile',json=body).json(),result.json())
        self.assertEqual(self.d.profile('case_a')['years'],10)
        invalid={**body,'request_id':'profile_2','profile':{**body['profile'],'years':11}}
        failed=self.client.put('/api/cases/case_a/profile',json=invalid)
        self.assertEqual(failed.status_code,409)
        self.assertTrue(failed.json()['review_required'])
        self.assertEqual(self.app._row('case_a')['revision'],0)

    def test_qualification_is_sourced_previewed_and_declared_once(self):
        source=self.app.add_source('case_a',text='Convention fictive : aucun salarié pour ce test.')
        body={'declaration':{'module':'Effectifs','state':'INACTIF','status':'CONFIRME','evidence':source['id'],'reason':'Aucun salarié dans ce dossier fictif.'},'expected_revision':0}
        preview=self.d.qualification_preview('case_a',body)
        self.assertFalse(self.d.qualification_view('case_a')['declarations'])
        self.d.qualification_apply('case_a',{'approval_token':preview['approval_token']})
        self.d.qualification_apply('case_a',{'approval_token':preview['approval_token']})
        with self.app.store.connection() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM history WHERE case_id='case_a' AND kind='QUALIFICATION_DECLAREE'").fetchone()[0],1)
        self.assertEqual(self.app._row('case_a')['revision'],0)
        with self.assertRaises(ValueError): self.d.qualification_preview('case_b',body)

    def test_guided_dates_keep_iso_until_native_preparation(self):
        fields=[{'id':'date','field_id':'date','sheet':'Entrées','cell':'A1','kind':'date'}]
        with patch.object(self.d,'bindings',return_value=fields):
            draft=self.d.answers('case_a',{'answers':[{'field_id':'date','value':'2027-01-01'}]})
        self.assertEqual(draft['operations'][0]['value'],'2027-01-01')

    def test_calendar_migration_api_prepares_sourced_draft_once_and_preserves_workbook(self):
        self._calendar_migration_transport('dcf_calendar_migration','plan_calendar_migration','dcf-calendar')

    def test_fiscal_migration_api_prepares_sourced_draft_once_and_preserves_workbook(self):
        self._calendar_migration_transport('fiscal_calendar_migration','plan_fiscal_calendar_migration','fiscal-calendar')

    def _calendar_migration_transport(self,module,function,route):
        before=self.app._row('case_a')['sha256']
        def plan(engine,workbook,evidence_id):
            return {'status':'PROPOSED','operations':[{'type':'set_formula','sheet':'Entrées','cell':'A1',
                    'formula':'=SUM(1,2)','evidence_id':evidence_id,'reason':'Témoin de transport ; aucune validation financière.'}]}
        body={'expected_revision':0,'request_id':'calendar_migration'}
        with patch('tca_bp.'+module+'.'+function,side_effect=plan) as prepare:
            first=self.client.post('/api/cases/case_a/model/'+route,json=body)
            self.assertEqual(first.status_code,200,first.text)
            repeated=self.client.post('/api/cases/case_a/model/'+route,json=body)
            self.assertEqual(repeated.json(),first.json())
            self.assertEqual(prepare.call_count,1)
            refused=self.client.post('/api/cases/case_a/model/'+route,json={**body,'request_id':'different'})
            self.assertEqual(refused.status_code,409,refused.text)
            self.assertEqual(prepare.call_count,1)
        draft=self.work.draft('case_a')
        self.assertEqual(draft['operations'][0]['formula'],'=SUM(1,2)')
        self.d.source('case_a',draft['operations'][0]['evidence_id'])
        self.assertEqual(self.app._row('case_a')['revision'],0)
        self.assertEqual(self.app._row('case_a')['sha256'],before)
        self.assertEqual(digest(self.app._workbook(self.app._row('case_a'))),before)

    def test_cross_case_intents_and_uncertain_write_never_reexecuted(self):
        calls=[]
        def action(): calls.append(1); return {'saved':True}
        body={'request_id':'same','value':1}
        self.d.request('case_a','operation',body,action)
        self.d.request('case_a','operation',body,action)
        self.d.request('case_b','operation',body,action)
        self.assertEqual(len(calls),2)
        with self.assertRaisesRegex(ValueError,'contenu différent'):
            self.d.request('case_a','different',body,action)
        def interrupted(): calls.append(1); raise RuntimeError('after commit')
        with self.assertRaises(ValueError): self.d.request('case_a','partial',{'request_id':'partial'},interrupted)
        with self.assertRaises(ValueError): self.d.request('case_a','partial',{'request_id':'partial'},interrupted)
        self.assertEqual(len(calls),3)
        self.assertEqual(self.d.intent('case_a','partial')['status'],'REVIEW_REQUIRED')
        with self.assertRaises(ValueError): self.d.review_intent('case_a','partial',{'expected_revision':0,'reviewed':False})
        review=self.d.intent_review('case_a','partial')
        reviewed=self.d.review_intent('case_a','partial',{'expected_revision':0,'approval_token':review['approval_token']})
        self.assertFalse(reviewed['reexecuted'])
        with self.assertRaises(ValueError): self.d.request('case_a','partial',{'request_id':'partial'},interrupted)
        self.assertEqual(len(calls),3)

    def test_capitalization_preview_apply_source_revision_and_repeat(self):
        original=digest(Path(self.app.get_case('case_a')['workbook_path']))
        body={'shareholders':[{'name':'Fondatrice','shares':1000}], 'rounds':[{'name':'Seed','pre_money':4000000,'investment':1000000,'pool_percent':10,'pool_timing':'before'}]}
        preview=self.d.capitalization('case_a',body)
        self.assertIsNone(self.d.latest('case_a','capitalization'))
        saved=self.d.adopt_object('case_a','capitalization',{'approval_token':preview['approval_token']})
        self.assertEqual(saved,self.d.adopt_object('case_a','capitalization',{'approval_token':preview['approval_token']}))
        with self.assertRaises(ValueError): self.d.adopt_object('case_b','capitalization',{'approval_token':preview['approval_token']})
        self.assertEqual(original,digest(Path(self.app.get_case('case_a')['workbook_path'])))
        second=self.d.capitalization('case_a',body)
        with self.app.store.connection() as db: db.execute('UPDATE cases SET revision=1 WHERE id=?',('case_a',))
        with self.assertRaises(ValueError): self.d.adopt_object('case_a','capitalization',{'approval_token':second['approval_token']})

    def test_scenario_copies_pinned_current_workbook_and_sources(self):
        source=self.app.add_source('case_a',text='Contrat fictif confirmé.')
        self.app.declare_qualification('case_a',{'module':'Effectifs','state':'INACTIF','status':'CONFIRME','evidence':source['id'],'reason':'Aucun recrutement dans la référence.'})
        parent=self.app.get_case('case_a')
        scenario=self.d.create_scenario('case_a',{'name':'Recrutement','expected_revision':0})
        child=self.app.get_case(scenario['case_id'])
        self.assertEqual(child['model_ref'],parent['model_ref'])
        self.assertEqual(child['sha256'],parent['sha256'])
        self.assertNotEqual(child['sources'][0]['id'],source['id'])
        self.assertEqual(child['sources'][0]['sha256'],source['sha256'])
        self.assertEqual(child['revision'],0)
        self.assertEqual(child['calculation_status'],'A_RECALCULER')
        self.assertEqual(len(self.work.versions(child['id'])['versions']),1)
        inherited=self.app._qualification_basis(self.app._row(child['id']))['declarations']['Effectifs']
        self.assertEqual(inherited['state'],'INACTIF')
        self.assertEqual(inherited['case_id'],child['id'])
        self.assertEqual(inherited['evidence'],child['sources'][0]['id'])
        self.assertEqual(inherited['origin']['case_id'],'case_a')
        with self.app.store.connection() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM history WHERE case_id=? AND kind='RECALCUL_EXCEL'",(child['id'],)).fetchone()[0],0)

    def test_actuals_missing_ambiguous_duplicate_and_cross_source(self):
        row={'period':'2027-01','metric':'revenue','kind':'flow','value':1250.5,'unit':'EUR'}
        body={'rows':[row],'cutoff':'2027-01-31'}
        preview=preview_actuals(self.d,'case_a',body)
        self.assertEqual(preview['changes'][0]['new'],'1250.5')
        self.assertIsNone(self.d.latest('case_a','actuals'))
        ambiguous=preview_actuals(self.d,'case_a',{**body,'rows':[{**row,'value':'1,250'}]})
        self.assertEqual(ambiguous['diagnostics'][0]['code'],'CONVERSION_AMBIGUE')
        for changes in ({'rows':[{**row,'value':None}]},{'rows':[row,row]},{'cutoff':'2027-01-15'},{'rows':[{**row,'metric':'cash'}]}):
            with self.assertRaises(ValueError): preview_actuals(self.d,'case_a',{**body,**changes})
        source=self.app.add_source('case_b',text='Autre dossier')
        with self.assertRaises(ValueError): preview_actuals(self.d,'case_a',{**body,'source_id':source['id']})

    def test_csv_and_xlsx_columns_are_read_without_macros(self):
        mapping={'period':'Mois','metric':'Poste','value':'Montant'}
        path=self.root/'actuals.csv'; path.write_text('Mois;Poste;Montant\n2027-01;revenue;1250,50\n',encoding='utf-8')
        columns,rows=read_import(path,mapping,'fr')
        self.assertEqual(rows[0]['value'],'1250,50')
        import xlsxwriter
        path=self.root/'actuals.xlsx'; book=xlsxwriter.Workbook(path); sheet=book.add_worksheet()
        sheet.write_row(0,0,['Mois','Poste','Montant']); sheet.write_row(1,0,['2027-01','revenue',1250.5]); book.close()
        columns,rows=read_import(path,mapping,'fr')
        self.assertEqual(rows[0]['value'],1250.5)

    def test_questionnaire_answers_join_existing_draft_and_reject_ambiguous_field(self):
        self.work.add_operations('case_a',[{'type':'set_value','sheet':'Entrées','cell':'A1','value':1}],{'sheet':'Entrées'})
        result=self.d.answers('case_a',{'answers':[{'field_id':'second','sheet':'Entrées','cell':'A2','value':3}],'expected_revision':0})
        self.assertEqual(len(result['operations']),2)
        self.assertEqual(self.app._row('case_a')['revision'],0)
        with self.assertRaises(ValueError): self.d.answers('case_a',{'answers':[{'field_id':'unknown','value':3}]})

    def test_large_block_persisted_revalidated_sources_and_scope(self):
        from tca_bp.web_blocks import ExpandedOperations
        source=self.app.add_source('case_a',text='Historique mensuel fictif sourcé')
        block={'type':'set_block','sheet':'Entrées','start_cell':'C1','rows':[[{'value':i}] for i in range(2100)],'evidence_id':source['id']}
        draft=self.work.add_operations('case_a',[block],{'sheet':'Entrées'})
        self.assertEqual(len(draft['operations']),2100)
        payload=json.loads(self.work._draft_row('case_a')['payload'])
        operations=self.work._validate_draft_operations('case_a',payload)
        self.assertIsInstance(operations,ExpandedOperations)
        self.assertEqual(len(operations),2100)
        self.assertEqual(operations[-1]['cell'],'C2100')
        payload['bounded_blocks']=False
        with self.assertRaises(ValueError): self.work._validate_draft_operations('case_a',payload)
        with self.assertRaises(ValueError): self.work.add_operations('case_b',[block],{'sheet':'Entrées'})
        with self.assertRaises(ValueError): self.work.add_operations('case_a',[block],{'sheet':'Entrées','range':'C1:C10'})

    def test_object_adoption_hook_rolls_back_budget_and_actuals_together(self):
        preview=self.d.preview_object('case_a','actuals',{'rows':[]},0)
        def interrupted(row,db):
            self.d.save('case_a','budget',{'source_sha256':row['sha256']},db=db)
            raise ValueError('Interruption avant adoption')
        with self.assertRaises(ValueError): self.d.adopt_object('case_a','actuals',preview,before_adopt=interrupted)
        self.assertIsNone(self.d.latest('case_a','budget'))
        self.assertIsNone(self.d.latest('case_a','actuals'))
        self.assertFalse((self.app.store.case_dir('case_a')/'.transaction.lock').exists())

    def test_missing_cash_or_model_cutoff_never_publishes_future_cash(self):
        from tca_bp.decision_actuals import actuals_view
        periods=['2027-01','2027-02']
        series=[{'id':'cash','categories':periods,'values':[100,110]}]
        self.d.save('case_a','actuals',{'cutoff':'2027-01-31','rows':[]})
        with patch('tca_bp.decision_model.read_series',return_value=series):
            self.assertEqual(actuals_view(self.d,'case_a')['forecast_series'][0]['values'],[None,None])
        self.d.save('case_a','actuals',{'cutoff':'2027-01-31','rows':[{'period':'2027-01','metric':'cash','value':'200'}]})
        with patch('tca_bp.decision_model.read_series',return_value=series):
            self.assertEqual(actuals_view(self.d,'case_a')['forecast_series'][0]['values'],[200,None])
        with patch('tca_bp.decision_model.read_series',return_value=[{**series[0],'values':[None,110]}]):
            self.assertEqual(actuals_view(self.d,'case_a')['forecast_series'][0]['values'],[200,None])

    def test_first_actuals_cannot_freeze_unqualified_or_missing_budget_and_later_correction_preserves_it(self):
        from tca_bp.decision_actuals import apply_actuals
        rows=[{'period':'2027-01','metric':'revenue','kind':'flow','value':100,'unit':'EUR'}]
        preview=preview_actuals(self.d,'case_a',{'rows':rows,'cutoff':'2027-01-31'})
        case={'outputs_current':True,'qualified_availability':{}}
        series=[{'id':key,'categories':['2027-01','2027-02'],'values':[100,120]} for key in ('cash','revenue','receipts','payments')]
        with patch.object(self.app,'get_case',return_value=case),patch('tca_bp.decision_model.read_series',return_value=series),patch.object(self.d,'metrics',return_value=[]),patch('tca_bp.decision_actuals.actuals_view',return_value={}):
            with self.assertRaisesRegex(ValueError,'qualifier'):apply_actuals(self.d,'case_a',preview)
            self.assertIsNone(self.d.latest('case_a','budget'))
            self.assertIsNone(self.d.latest('case_a','actuals'))
            case['qualified_availability']={key:{'scenario_ready':True} for key in ('CA','COGS','CASH','FISCALITE')}
            series[0]['values'][1]=None
            with self.assertRaisesRegex(ValueError,'séries mensuelles'):apply_actuals(self.d,'case_a',preview)
            self.assertIsNone(self.d.latest('case_a','budget'))
            series[0]['values'][1]=120
            apply_actuals(self.d,'case_a',preview)
            budget=self.d.latest('case_a','budget')
            corrected=preview_actuals(self.d,'case_a',{'rows':[{**rows[0],'value':110}],'cutoff':'2027-01-31'})
            case['outputs_current']=False
            apply_actuals(self.d,'case_a',corrected)
            self.assertEqual(self.d.latest('case_a','budget'),budget)
            self.assertEqual(self.d.latest('case_a','actuals')['rows'][0]['value'],'110')
if __name__=='__main__': unittest.main()
