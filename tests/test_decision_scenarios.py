"""Decision orchestration guards; no native financial calculation is simulated as proof."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tca_bp.decision_model import evaluate_copy,run_sensitivity


class FinancialReads(unittest.TestCase):
    def workspace(self, current=True, years=10):
        names=[('Control','Paramètres'),('Modèle financier','Trésorerie'),
               ('Compte de Résultat','Résultats'),('Valorisation','Valeur'),('Revenue','Ventes')]
        profile={'sheets':[{'id':str(i),'original_name':old,'name':new,'deleted':False,
                           'transforms':[{'type':'insert_rows','index':100,'count':2},
                                         {'type':'insert_columns','index':20,'count':1}] if i==1 else []}
                          for i,(old,new) in enumerate(names)]}
        class Engine:
            accesses=0
            @property
            def profile(self):
                self.accesses+=1
                # A financial read may take snapshots for its two bounded
                # subreads, but never scale copies with the number of cells.
                if self.accesses>2: raise AssertionError('Profil recopié par cellule')
                return deepcopy(profile)
        engine=Engine(); calls=[]
        def value(sheet,cell):
            calls.append((sheet,cell))
            if sheet=='Paramètres': return {'C10':46023,'C59':years}[cell]
            if (sheet,cell)==('Trésorerie','Z323'): return None
            return 42
        wb=SimpleNamespace(date1904=False,value=value)
        scopes={key:{'scenario_ready':True,'status':'QUALIFIE'} for key in ('CA','CASH','COGS','DCF')}
        d=SimpleNamespace(app=SimpleNamespace(engine_for_case=lambda c:engine,
                get_case=lambda c:{'outputs_current':current,'qualified_availability':scopes}),
            work=SimpleNamespace(_read=lambda c,action:action(wb,{})),profile=lambda c:{})
        return d,engine,calls,profile

    def test_ten_year_series_use_one_profile_and_follow_renamed_shifted_cells(self):
        from tca_bp.decision_model import read_series
        d,engine,calls,_=self.workspace()
        result=read_series(d,'case')
        self.assertEqual(engine.accesses,1)
        self.assertEqual(result[0]['categories'][0],'2026-01')
        self.assertEqual(result[0]['categories'][-1],'2035-12')
        self.assertEqual(len(result[0]['values']),120)
        self.assertEqual(result[0]['values'][:6],[42]*5+[None])
        self.assertIn(('Trésorerie','U323'),calls)
        self.assertIn(('Ventes','P282'),calls)
        self.assertIn(('Ventes','P283'),calls)
        self.assertIn(('Ventes','P284'),calls)
        self.assertNotIn(('Trésorerie','U88'),calls)
        self.assertNotIn(('Modèle financier','T321'),calls)

    def test_metrics_and_annual_reads_keep_missing_values_and_qualification(self):
        from tca_bp.decision_model import read_metrics,read_annual_metrics
        for reader in (read_metrics,read_annual_metrics):
            with self.subTest(reader=reader.__name__):
                d,engine,_,_=self.workspace(current=False)
                result=reader(d,'case')
                self.assertEqual(engine.accesses,2)
                self.assertTrue(all(item['value'] is None for item in result))
        d,_,_,_=self.workspace()
        result={item['id']:item for item in read_metrics(d,'case')}
        self.assertEqual(result['revenue']['value'],42)
        self.assertIsNone(result['cash_min']['value'])
        self.assertIsNone(result['financing_need']['value'])

    def test_resolver_snapshot_is_isolated_and_deleted_owner_is_refused(self):
        from tca_bp.decision_model import location_resolver
        _,engine,_,profile=self.workspace()
        resolve=location_resolver(engine)
        profile['sheets'][1]['deleted']=True
        self.assertEqual(resolve('Modèle financier','T321'),('Trésorerie','U323'))
        new_resolve=location_resolver(engine)
        with self.assertRaisesRegex(ValueError,'supprimée'):
            new_resolve('Modèle financier','T321')
        self.assertEqual(location_resolver(SimpleNamespace())('Control','C10'),('Control','C10'))


class ScenarioProtocols(unittest.TestCase):
    def test_valuation_trial_requires_its_own_wacc_proof_after_recalculation(self):
        calls=[]
        d=SimpleNamespace(propose=lambda *a:{'id':'draft'},
            work=SimpleNamespace(preview=lambda *a:{'approval_token':'reviewed'},apply=lambda *a:calls.append(('apply',a[2]))),
            app=SimpleNamespace(recalculate=lambda c:calls.append(('calculate',c)),solve_wacc=lambda c:calls.append(('wacc',c))),
            metrics=lambda *a:[{'id':'valuation','value':123}])
        with patch('tca_bp.decision_model.create_scenario',return_value={'case_id':'isolated'}):
            result=evaluate_copy(d,'reference',{'sheet':'Inputs','cell':'A1'},12,'Essai',lambda p:None,target_metric='valuation')
        self.assertEqual(calls,[('apply','reviewed'),('calculate','isolated'),('wacc','isolated')])
        self.assertEqual(result[1][0]['value'],123)

    def test_cancel_arriving_during_point_is_retained_and_resume_skips_that_point(self):
        axes=[{'field_id':'price','values':[10,20]}]
        objects={'campaign':{'id':'campaign','revision':0,'base_sha256':'same','axes':axes,'metric':'cash_min','points':[],'cancel_requested':False}}
        created=[];cancel_first=[True]
        def save(case,kind,payload,**options):
            objects['campaign']={**deepcopy(payload),'id':'campaign','status':options.get('status','RUNNING')}
            return deepcopy(objects['campaign'])
        def metrics(case):
            if case!='reference' and cancel_first[0]:
                objects['campaign']['cancel_requested']=True;cancel_first[0]=False
            return [{'id':'cash_min','value':100}]
        def scenario(*a,**k):
            created.append('trial'+str(len(created)))
            return {'case_id':created[-1]}
        d=SimpleNamespace(require_space=lambda *a,**k:None,save=save,get=lambda *a:deepcopy(objects['campaign']),metrics=metrics,
            propose=lambda *a:{'id':'draft'},app=SimpleNamespace(_row=lambda c:{'sha256':'same'},recalculate=lambda c:None),
            work=SimpleNamespace(jobs=SimpleNamespace(stop=SimpleNamespace(is_set=lambda:False)),
                preview=lambda *a:{'approval_token':'reviewed'},apply=lambda *a:None))
        payload={'campaign_id':'campaign','metric':'cash_min','axes':[{'field_id':'price','values':[10,20]}]}
        with patch('tca_bp.decision_model._lever',return_value={'sheet':'Inputs','cell':'A1'}),patch('tca_bp.decision_model.create_scenario',side_effect=scenario):
            first=run_sensitivity(d,'reference',payload,lambda p:None)
            self.assertEqual(first['status'],'INTERRUPTED')
            self.assertEqual(len(first['points']),1)
            objects['campaign']['cancel_requested']=False
            second=run_sensitivity(d,'reference',payload,lambda p:None)
        self.assertEqual(second['status'],'COMPLETE')
        self.assertEqual(len(created),2)
        self.assertEqual([p['values'] for p in second['points']],[[10],[20]])

    def test_resume_cannot_mix_changed_axes_or_target_with_completed_points(self):
        from unittest.mock import Mock
        axes=[{'field_id':'price','values':[10,20]}]
        campaign={'id':'campaign','revision':0,'base_sha256':'same','axes':axes,'metric':'cash_min',
                  'points':[{'values':[10],'case_id':'retained','metrics':[{'id':'cash_min','value':100}]}]}
        d=SimpleNamespace(require_space=Mock(),get=lambda *a:deepcopy(campaign),save=Mock(),
            metrics=lambda *a:[{'id':'cash_min','value':100},{'id':'revenue','value':200}],
            app=SimpleNamespace(_row=lambda c:{'sha256':'same'}))
        changes=[{'axes':[{'field_id':'price','values':[10,30]}]}, {'metric':'revenue'}]
        with patch('tca_bp.decision_model._lever',return_value={'sheet':'Inputs','cell':'A1'}), \
             patch('tca_bp.decision_model.create_scenario') as create:
            for change in changes:
                with self.subTest(change=change),self.assertRaisesRegex(ValueError,'immuables'):
                    run_sensitivity(d,'reference',{'campaign_id':'campaign','metric':'cash_min','axes':axes,**change},lambda p:None)
        create.assert_not_called();d.save.assert_not_called()
        self.assertEqual(campaign['points'][0]['case_id'],'retained')

    def test_fractional_integer_axis_is_refused_before_campaign_or_scenario_creation(self):
        from unittest.mock import Mock
        d=SimpleNamespace(save=Mock(),get=Mock(),require_space=Mock())
        with patch('tca_bp.decision_model._lever',return_value={'sheet':'Inputs','cell':'A1','kind':'integer'}), \
             patch('tca_bp.decision_model.create_scenario') as create, self.assertRaisesRegex(ValueError,'valeurs entières'):
            run_sensitivity(d,'reference',{'axes':[{'field_id':'volume','values':[10,10.5]}]},lambda p:None)
        create.assert_not_called();d.save.assert_not_called();d.get.assert_not_called()


if __name__=='__main__':unittest.main()
