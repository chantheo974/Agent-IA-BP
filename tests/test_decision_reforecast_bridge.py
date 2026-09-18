"""Independent ledger arithmetic and cache/admission guards, without Excel."""
from copy import deepcopy
from decimal import Decimal
from types import SimpleNamespace
import unittest
import threading
from unittest.mock import patch

from tca_bp.decision_reforecast import plan_reforecast, read_reforecast, prepare_reforecast, reforecast_requirements, _col, _formula_key, _original_model_basis
from tca_bp.decision_reforecast_bridge import augment_plan, bridge_diagnostics, physical_locations, ACCOUNTS, SCHEMA
from tca_bp.web_blocks import expand_operations


def fixture():
    periods=[f'2026-{i:02d}' for i in range(1,13)]
    series=[{'id':key,'categories':periods,'values':[100]*12,'unit':'EUR'} for key in ('cash','revenue','receipts','payments')]
    values={'cash':200,'revenue':80,'receipts':70,'payments':50,'receivables':20,'inventory':5,'payables':12,'debt':47,'assets':300,'liabilities':100,'equity':200,'net_income':15}
    rows=[{'period':'2026-01','metric':key,'value':str(value),'kind':'flow' if key in ('revenue','receipts','payments','net_income') else 'balance','unit':'EUR','evidence_id':'s'} for key,value in values.items()]
    actuals={'cutoff':'2026-01-31','status':'CONFIRME','rows':rows}
    budget={'source_sha256':'b'*64,'series':deepcopy(series)}
    model_locations={s['id']:{p:('Modèle fictif',_col(20+i)+str(row)) for i,p in enumerate(periods)} for s,row in zip(series,[321,88,301,320])}
    monthly={p:{key:{'required':[f"'Modèle fictif'!{_col(20+i)}{row}"],'expression':f"'Modèle fictif'!{_col(20+i)}{row}"} for key,row in [('cash',321),('receivables',338),('inventory',340),('payables',339),('debt',400)]} for i,p in enumerate(periods)}
    annual={'2026':{key:{'required':[f"'Bilan fictif'!D{row}"],'expression':f"'Bilan fictif'!D{row}"} for key,row in [('assets',4),('liabilities',46),('equity',25),('net_income_ytd',85)]}}
    policies={key:{'treatment':'carry','terminal':'carry_remaining','evidence_id':'s','reason':'Écart maintenu explicitement pour cette recette fictive.'} for key in ACCOUNTS}
    for key in ('cash','equity','inventory','receivables','payables','debt'):
        policies[key]['treatment']='scheduled'
    for key in ('receivables','payables','debt'):policies[key]['terminal']='zero'
    def entry(account,debit,credit,flow=None):return {'account':account,'debit':debit,'credit':credit,**({'cash_flow':flow} if flow else {})}
    events=[{'id':'collect','period':'2026-02','evidence_id':'s','reason':'Encaissement de la seule créance supplémentaire','kind':'balance_transfer','entries':[entry('cash',10,0,'receipts'),entry('receivables',0,10)]},
        {'id':'pay','period':'2026-02','evidence_id':'s','reason':'Règlement de la seule dette fournisseur supplémentaire','kind':'balance_transfer','entries':[entry('payables',5,0),entry('cash',0,5,'payments')]},
        {'id':'debt','period':'2026-02','evidence_id':'s','reason':'Remboursement du seul principal supplémentaire','kind':'balance_transfer','entries':[entry('debt',7,0),entry('cash',0,7,'payments')]},
        {'id':'loss','period':'2026-02','evidence_id':'s','reason':'Dépréciation fictive de stock de deux euros, effet fiscal explicitement nul dans ce témoin','kind':'profit_loss','tax_treatment':'no_tax_effect_confirmed','entries':[entry('equity',2,0),entry('inventory',0,2)]}]
    bridge={'schema':SCHEMA,'basis':'NET_ADJUSTMENTS_TO_CURRENT_MODEL','workbook_sha256':'a'*64,
        'baseline_cutoff':{key:{'value':value,'evidence_id':'s'} for key,value in [('assets',200),('liabilities',80),('equity',120),('net_income_ytd',10)]},'policies':policies,'events':events}
    return actuals,budget,series,model_locations,{'monthly':monthly,'annual':annual},bridge


def planned():
    actuals,budget,series,model_locations,locations,bridge=fixture()
    plan=plan_reforecast(actuals,budget,series,model_locations)
    plan['_model_locations']=model_locations
    result=augment_plan(plan,actuals,budget,series,locations,bridge,workbook_sha256='a'*64)
    return result,actuals,budget


class BridgeTests(unittest.TestCase):
    def test_physical_locations_share_one_profile_for_ten_years_and_keep_transforms(self):
        profile={'sheets':[{'id':str(index),'original_name':name,'name':name+" d'essai",
            'transforms':[{'type':'insert_rows','index':10,'count':3},
                          {'type':'insert_columns','index':4,'count':2}]}
            for index,name in enumerate(('Modèle financier','BFR','Bilan','Compte de Résultat'))]}
        class Engine:
            reads=0
            @property
            def profile(self):
                self.reads+=1
                return deepcopy(profile)
        engine=Engine()
        periods=[f'{year}-{month:02d}' for year in range(2026,2036) for month in range(1,13)]
        result=physical_locations(engine,periods)
        self.assertEqual(engine.reads,1)
        self.assertEqual(len(result['monthly']),120)
        def expected(sheet,column,row):
            return "'"+(sheet+" d'essai").replace("'","''")+"'!"+_col(column+2)+str(row+3 if row>=10 else row)
        for index,period in enumerate(periods):
            item=result['monthly'][period]
            for metric,sheet,column,row in [('cash','Modèle financier',20+index,321),
                    ('receivables','BFR',16+index,10),('inventory','BFR',16+index,11),('payables','BFR',16+index,17)]:
                target=expected(sheet,column,row)
                self.assertEqual(item[metric],{'required':[target],'expression':target})
            debt=[expected('Modèle financier',20+index,row) for row in (292,299,315,317)]
            self.assertEqual(item['debt'],{'required':debt,'expression':debt[0]+'+'+debt[1]+'-'+debt[2]+'-'+debt[3],'rollforward':True})
        for index,year in enumerate(range(2026,2036)):
            item=result['annual'][str(year)]
            assets=expected('Bilan',4+index,4);total=expected('Bilan',4+index,24);equity=expected('Bilan',4+index,25)
            income=expected('Compte de Résultat',4+index,85)
            self.assertEqual(item,{'assets':{'required':[assets],'expression':assets},
                'liabilities':{'required':[total,equity],'expression':total+'-'+equity},
                'equity':{'required':[equity],'expression':equity},'net_income_ytd':{'required':[income],'expression':income}})
        # A new read sees the new profile and still refuses a deleted owner.
        profile['sheets'][0]['transforms'].append({'type':'delete_rows','index':324,'count':1})
        with self.assertRaisesRegex(ValueError,'supprimée'):
            physical_locations(engine,periods)
        self.assertEqual(engine.reads,2)

    def test_independent_double_entry_oracles_and_no_second_model_cash(self):
        plan,actuals,budget=planned()
        self.assertEqual(plan['questions'],[])
        self.assertEqual(plan['schema_version'],'tca-reforecast/2')
        # Independent opening differences and four manual balanced entries.
        delta={'cash':Decimal(70),'receivables':Decimal(10),'inventory':Decimal(0),'other_assets':Decimal(20),
               'payables':Decimal(5),'debt':Decimal(7),'other_liabilities':Decimal(8),'equity':Decimal(80)}
        delta['cash']+=10-5-7;delta['receivables']-=10;delta['payables']-=5;delta['debt']-=7
        delta['inventory']-=2;delta['equity']-=2
        self.assertEqual(Decimal(150)+delta['cash'],Decimal(218))
        self.assertEqual(Decimal(200)+(Decimal(100)+10)-(Decimal(80)+5+7),Decimal(218))
        assets=250+sum(delta[k] for k in ('cash','receivables','inventory','other_assets'))
        liabilities=90+sum(delta[k] for k in ('payables','debt','other_liabilities'))
        equity=160+delta['equity']
        self.assertEqual((assets,liabilities,equity),(Decimal(336),Decimal(98),Decimal(238)))
        self.assertEqual(assets-liabilities-equity,0)
        self.assertEqual(40-10+15-2,43)
        changes={(o.get('sheet'),o.get('cell')):o for o in expand_operations(plan['operations']) if 'cell' in o}
        cash=changes[('TCA Actualisé','E9')]['formula']
        self.assertIn("'Modèle fictif'!U321+'TCA Raccord'!I14",cash)
        self.assertNotIn("'TCA Réalisé'!D9+",cash)
        income=changes[('TCA Actualisé','D36')]['formula']
        self.assertIn("-'TCA Raccord'!B29+'TCA Raccord'!B35",income)
        self.assertIn('"profit_loss"',income)
        self.assertEqual({o['sheet'] for o in expand_operations(plan['operations']) if 'sheet' in o},{'TCA Réalisé','TCA Actualisé','TCA Raccord'})
        self.assertEqual(budget['source_sha256'],'b'*64)
        self.assertTrue(all(len(o['formula'])<=8192 for o in expand_operations(plan['operations']) if o['type']=='set_formula'))

    def test_all_managed_sheets_exist_before_any_formula_targets_them(self):
        from tca_bp.model_build import formula_references
        plan,_,_=planned();existing={'Modèle fictif','Bilan fictif'};setters=False
        for operation in expand_operations(plan['operations']):
            if operation['type']=='add_sheet':
                self.assertFalse(setters,'A generated sheet was created after a setter')
                existing.add(operation['name'])
            else:
                setters=True;self.assertIn(operation['sheet'],existing)
                if operation['type']=='set_formula':
                    for reference in formula_references(operation['formula'],operation['sheet']):
                        sheet=reference.rsplit('!',1)[0][1:-1].replace("''", "'")
                        self.assertIn(sheet,existing,'Formula points to a sheet not created yet')

    def test_structure_diagnostic_rejects_an_externalized_bridge_reference(self):
        import tempfile,zipfile
        from pathlib import Path
        from tests.test_model_versions import fixture as model_fixture
        from tca_bp.web_structure import workbook_diagnostics
        with tempfile.TemporaryDirectory(prefix='tca-bridge-reference-') as temporary:
            root=Path(temporary);engine=model_fixture(root/'source');output=root/'externalized.xlsm'
            with zipfile.ZipFile(engine.template_path) as source,zipfile.ZipFile(output,'w') as target:
                for item in source.infolist():
                    raw=source.read(item.filename)
                    if item.filename=='xl/workbook.xml':
                        for old,new in [('Inputs','TCA Actualisé'),('Control','TCA Réalisé'),('Assumptions','TCA Raccord')]:
                            raw=raw.replace(('name="'+old+'"').encode(),('name="'+new+'"').encode())
                    if item.filename=='xl/worksheets/sheet1.xml':
                        raw=raw.replace(b'<f>A1*2</f>',b"<f>'[1]TCA Raccord'!B8</f>")
                    target.writestr(item,raw)
            result=workbook_diagnostics(output)
            self.assertEqual(set(result['sheet_names']),{'TCA Actualisé','TCA Réalisé','TCA Raccord'})
            self.assertTrue(any(error['code']=='MISSING_SHEET_REFERENCE' and error.get('referenced_sheet')=='[1]TCA Raccord' for error in result['errors']))

    def test_missing_schedules_sources_checkpoint_and_cash_classification_are_questions(self):
        actuals,budget,series,model,locations,bridge=fixture()
        missing=deepcopy(bridge)
        del missing['baseline_cutoff']['equity'];del missing['policies']['debt'];missing['events'][0]['entries'][0].pop('cash_flow')
        result=bridge_diagnostics(actuals,missing,series[0]['categories'],'a'*64)
        self.assertFalse(result['ready'])
        fields={q['field'] for q in result['questions']}
        self.assertIn('baseline_cutoff.equity.evidence_id',fields)
        self.assertIn('policies.debt.treatment',fields)
        self.assertIn('events.collect.cash_flow',fields)
        original=deepcopy(missing)
        base=plan_reforecast(actuals,budget,series,model);base['_model_locations']=model
        plan=augment_plan(base,actuals,budget,series,locations,missing,workbook_sha256='a'*64)
        self.assertEqual(missing,original)
        fields={(op.get('sheet'),op.get('cell')):op for op in expand_operations(plan['operations']) if 'cell' in op}
        self.assertIsNone(fields[('TCA Raccord','B9')]['value'])
        self.assertIsNone(fields[('TCA Raccord','B28')]['value'])
        self.assertIn('NA()',fields[('TCA Actualisé','E9')]['formula'])

    def test_unbalanced_journal_hidden_equity_and_unknown_account_refused(self):
        actuals,_,series,_,_,bridge=fixture()
        for kind in ('unbalanced','hidden_equity','unknown','past'):
            changed=deepcopy(bridge)
            if kind=='unbalanced':changed['events'][0]['entries'][0]['debit']=11
            if kind=='hidden_equity':changed['events'][3]['kind']='balance_transfer'
            if kind=='unknown':changed['events'][0]['entries'][0]['account']='assumed_tax'
            if kind=='past':changed['events'][0]['period']='2026-01'
            with self.subTest(kind=kind),self.assertRaises(ValueError):bridge_diagnostics(actuals,changed,series[0]['categories'],'a'*64)
        changed=deepcopy(bridge);changed['events'][3].pop('tax_treatment')
        self.assertFalse(bridge_diagnostics(actuals,changed,series[0]['categories'],'a'*64)['ready'])

    def test_native_cache_reader_rejects_stale_actuals_unqualified_or_managed_edits(self):
        plan,actuals,budget=planned()
        plan.update(source_revision=2,status='DRAFT')
        fields={(o['sheet'],o['cell']):o for o in expand_operations(plan['operations']) if o['type'] in ('set_formula','set_value')}
        cache={key:1 for key,o in fields.items() if o['type']=='set_formula'}
        for i in range(12):cache['TCA Actualisé',_col(4+i)+'9']=200
        for row,value in [(33,336),(34,98),(35,238),(36,43),(37,0),(38,0)]:cache['TCA Actualisé','D'+str(row)]=value
        class Workbook:
            sheets={'TCA Réalisé':{},'TCA Actualisé':{},'TCA Raccord':{}}
            def formula(self,sheet,cell):return fields.get((sheet,cell),{}).get('formula','').removeprefix('=') or None
            def value(self,sheet,cell):
                op=fields.get((sheet,cell),{})
                return cache.get((sheet,cell)) if op.get('type')=='set_formula' else op.get('value')
        wb=Workbook();plan['original_model_sha256']=_original_model_basis(wb)
        case={'outputs_current':True,'qualified_availability':{key:{'scenario_ready':True} for key in ('CA','COGS','CASH','FISCALITE')}}
        d=SimpleNamespace(latest=lambda case_id,kind,default:{} if kind not in ('actuals','budget') else actuals if kind=='actuals' else budget,
            objects=lambda case_id,kind:[plan],app=SimpleNamespace(get_case=lambda case_id:case),
            work=SimpleNamespace(_read=lambda case_id,fn:fn(wb,None)),source=lambda case_id,source:{'id':source})
        self.assertEqual(read_reforecast(d,'fake')['forecast_status'],'EXPLICABLE')
        cache['TCA Actualisé','E9']=201
        self.assertIn('CONTINUITE_CASH_NON_VALIDEE',[x['code'] for x in read_reforecast(d,'fake')['diagnostics']])
        cache['TCA Actualisé','E9']=200
        basis=plan['original_model_sha256'];plan['original_model_sha256']='changed'
        refused=read_reforecast(d,'fake')
        self.assertIn('MODELE_RACCORD_MODIFIE',[x['code'] for x in refused['diagnostics']])
        self.assertTrue(all(v is None for s in refused['forecast_series'] for v in s['values']))
        plan['original_model_sha256']=basis
        case['outputs_current']=False
        result=read_reforecast(d,'fake');self.assertNotEqual(result['forecast_status'],'EXPLICABLE')
        self.assertTrue(all(v is None for s in result['forecast_series'] for v in s['values']))
        case['outputs_current']=True
        actuals['rows'][0]['value']='201'
        self.assertIn('RACCORD_OBSOLETE',[x['code'] for x in read_reforecast(d,'fake')['diagnostics']])
        actuals['rows'][0]['value']='200'
        fields['TCA Raccord','C60']['value']=999
        self.assertIn('CONTENU_RACCORD_MODIFIE',[x['code'] for x in read_reforecast(d,'fake')['diagnostics']])

    def test_ten_years_debt_rollforward_is_bounded_and_complete(self):
        actuals,budget,series,model,_,bridge=fixture()
        periods=[f'{year}-{month:02d}' for year in range(2026,2036) for month in range(1,13)]
        for s in series:s.update(categories=periods,values=[100]*120)
        model={s['id']:{p:('Modèle financier',_col(20+i)+str(row)) for i,p in enumerate(periods)} for s,row in zip(series,[321,88,301,320])}
        base=plan_reforecast(actuals,budget,series,model);base['_model_locations']=model
        locations=physical_locations(SimpleNamespace(profile=None),periods)
        plan=augment_plan(base,actuals,budget,series,locations,bridge,workbook_sha256='a'*64)
        expanded=expand_operations(plan['operations'])
        formulas=[o['formula'] for o in expanded if o['type']=='set_formula']
        self.assertEqual(len(plan['annual_years']),10)
        self.assertTrue(all(len(f)<=8192 for f in formulas))
        self.assertLessEqual(len(plan['operations']),2000)
        self.assertGreater(plan['atomic_operation_count'],2000)
        last=next(o for o in expanded if o.get('sheet')=='TCA Raccord' and o.get('cell')==_col(9+119)+'50')
        self.assertIn(_col(9+118)+'50',last['formula'])
        self.assertIn('EI315',last['formula'])

    def test_wrapper_creates_only_shared_draft_and_retains_sourced_bridge(self):
        actuals,budget,series,_,_,bridge=fixture();calls={}
        blank=SimpleNamespace(sheets={})
        class Engine:
            reads=0
            @property
            def profile(self):
                self.reads+=1
                return None
        engine=Engine()
        def propose(case_id,ops,revision):calls['ops']=ops;calls['revision']=revision;return {'id':'shared_draft'}
        def save(case_id,kind,payload,**kwargs):calls['saved']=(kind,payload,kwargs);return {'id':'prep_receipt'}
        d=SimpleNamespace(lock=threading.RLock(),check_revision=lambda c,r:{'revision':4,'sha256':'a'*64},
            work=SimpleNamespace(draft=lambda c:{'operations':[]},_read=lambda c,f:f(blank,None)),
            latest=lambda c,k,default:actuals if k=='actuals' else budget,
            source=lambda c,s:{'id':s},app=SimpleNamespace(engine_for_case=lambda c:engine),
            propose=propose,save=save)
        with patch('tca_bp.decision_model.read_series',return_value=series):
            result=prepare_reforecast(d,'fictitious',{'expected_revision':4,'bridge':bridge})
        self.assertEqual(result['id'],'shared_draft')
        self.assertEqual(calls['saved'][0],'reforecast_preparation')
        self.assertEqual(calls['saved'][2]['status'],'DRAFT')
        self.assertEqual(calls['saved'][1]['bridge']['basis'],'NET_ADJUSTMENTS_TO_CURRENT_MODEL')
        self.assertEqual(result['reforecast']['questions'],[])
        self.assertEqual(calls['revision'],4)
        self.assertEqual(engine.reads,2)  # One snapshot for each independent mapping batch.

    def test_december_baseline_reads_renamed_owners_with_one_profile_per_batch(self):
        profile={'sheets':[{'id':str(index),'original_name':name,'name':name+' renommé',
            'transforms':[{'type':'insert_rows','index':10,'count':3},
                          {'type':'insert_columns','index':4,'count':2}]}
            for index,name in enumerate(('Modèle financier','BFR','Bilan','Compte de Résultat'))]}
        class Engine:
            reads=0
            @property
            def profile(self):
                self.reads+=1
                return deepcopy(profile)
        engine=Engine();seen=[]
        values={('Bilan renommé','F4'):500,('Bilan renommé','F28'):200,
                ('Bilan renommé','F27'):500,('Compte de Résultat renommé','F88'):15}
        def value(sheet,cell):
            seen.append((sheet,cell))
            return values[(sheet,cell)]
        d=SimpleNamespace(check_revision=lambda c,r:{'sha256':'a'*64},
            latest=lambda c,k,default:{'cutoff':'2026-12-31','rows':[]},objects=lambda c,k:[],
            app=SimpleNamespace(engine_for_case=lambda c:engine,get_case=lambda c:{'outputs_current':True}),
            work=SimpleNamespace(_read=lambda c,f:f(SimpleNamespace(value=value),None)))
        periods=[f'2026-{month:02d}' for month in range(1,13)]
        with patch('tca_bp.decision_model.read_series',return_value=[{'categories':periods}]):
            result=reforecast_requirements(d,'fictitious')
        self.assertEqual(engine.reads,2)  # Physical locations, then the linked balances.
        self.assertEqual(set(seen),set(values))
        self.assertEqual({x['id']:x['value'] for x in result['baseline_fields']},
                         {'assets':500,'liabilities':300,'equity':200,'net_income_ytd':15})
        self.assertTrue(all(x['linked'] and not x['required'] for x in result['baseline_fields']))

    def test_only_optional_sheet_quotes_are_normalized(self):
        self.assertEqual(_formula_key("='Feuille'!A1+1"),_formula_key('Feuille!A1+1'))
        self.assertNotEqual(_formula_key('="\'Feuille\'!A1"'),_formula_key('="Feuille!A1"'))
        self.assertNotEqual(_formula_key("='Feuille'!A1+1"),_formula_key('Feuille!A1+2'))

    def test_original_model_changes_invalidate_checkpoint_but_caches_do_not(self):
        from xml.etree import ElementTree as ET
        from tca_bp.vendor.input_engine import NS
        cells={'A1':ET.fromstring('<c/>'),'B1':ET.fromstring('<c/>'),'C1':ET.fromstring('<c/>')}
        values={'A1':'Fictitious original','B1':20,'C1':40};formula={'C1':'B1*2'}
        class Workbook:
            sheets={'Original':{}}
            def value(self,s,c):return values.get(c)
            def formula(self,s,c):return formula.get(c)
            def sheet(self,s):return None,cells,{}
        wb=Workbook();initial=_original_model_basis(wb)
        values['C1']=200
        self.assertEqual(_original_model_basis(wb),initial)
        values['B1']=21
        self.assertNotEqual(_original_model_basis(wb),initial)
        values['B1']=20;formula['C1']='B1*3'
        self.assertNotEqual(_original_model_basis(wb),initial)
        formula['C1']='B1*2';values['B1']='20'
        self.assertNotEqual(_original_model_basis(wb),initial)

    def test_native_table_flags_and_result_caches_do_not_change_model_basis(self):
        from xml.etree import ElementTree as ET
        from tca_bp.vendor.input_engine import NS,N
        nodes={'A1':ET.fromstring('<c/>'),'B2':ET.fromstring('<c xmlns="'+NS+'"><f t="dataTable" ref="B2:C3" r1="E1" ca="1" aca="1"/></c>'),
               'C2':ET.fromstring('<c/>'),'B3':ET.fromstring('<c/>'),'C3':ET.fromstring('<c/>')}
        values={'A1':'Original','B2':1,'C2':2,'B3':3,'C3':4}
        class Workbook:
            sheets={'Original':{}}
            def value(self,s,c):return values.get(c)
            def formula(self,s,c):return '' if c=='B2' else None
            def sheet(self,s):return None,nodes,{}
        wb=Workbook();initial=_original_model_basis(wb)
        f=nodes['B2'].find('m:f',N);f.attrib.pop('ca');f.attrib.pop('aca')
        values['C2']=12345
        self.assertEqual(_original_model_basis(wb),initial)
        f.set('r1','E2')
        self.assertNotEqual(_original_model_basis(wb),initial)
        f.set('ref','B2:XFD1048576')
        with self.assertRaisesRegex(ValueError,'borné'):_original_model_basis(wb)


if __name__=='__main__':unittest.main()
