from copy import deepcopy
from decimal import Decimal
import unittest

from tca_bp.decision_reforecast import (plan_reforecast, ACTUAL_MARKER, FORECAST_MARKER, METRICS, _col)
from tca_bp.web_blocks import expand_operations


def fixture():
    periods=['2026-01','2026-02','2026-03']
    series=[{'id':metric,'categories':periods,'values':values,'unit':'EUR'} for metric,values in
            [('revenue',[100,110,120]),('receipts',[90,100,115]),('payments',[60,80,70]),('cash',[130,150,195])]]
    rows=[]
    for metric,kind,value in [('revenue','flow','80'),('receipts','flow','70'),('payments','flow','50'),('cash','balance','200'),
                               ('assets','balance','500'),('liabilities','balance','300'),('equity','balance','200')]:
        rows.append({'period':'2026-01','metric':metric,'kind':kind,'value':value,'unit':'EUR','evidence_id':'source_fictive'})
    actuals={'id':'actuals_fictive','status':'CONFIRME','cutoff':'2026-01-31','rows':rows}
    budget={'source_sha256':'a'*64,'series':deepcopy(series)}
    locations={s['id']:{p:('Modèle renommé',f'{chr(84+i)}{row}') for i,p in enumerate(periods)}
               for s,row in zip(series,[88,301,320,321])}
    return actuals,budget,series,locations


class ReforecastTests(unittest.TestCase):
    def test_operations_are_only_managed_sheets_and_cash_is_a_difference(self):
        actuals,budget,series,locations=fixture()
        before=deepcopy((actuals,budget,series,locations))
        result=plan_reforecast(actuals,budget,series,locations)
        self.assertEqual((actuals,budget,series,locations),before)
        self.assertFalse(result['applied'])
        self.assertEqual(result['balance_at_cutoff'],{'status':'EQUILIBRE_ARITHMETIQUE','residual':'0'})
        self.assertEqual(result['forecast_balance_status'],'NON_RECONSTRUIT')
        changes={(o.get('sheet'),o.get('cell')):o for o in result['operations'] if o['type'].startswith('set_')}
        cash=changes[('TCA Actualisé','E9')]['formula']
        self.assertEqual(cash,"=IF(COUNT('TCA Réalisé'!D9,'Modèle renommé'!U321,'Modèle renommé'!T321)=3,'TCA Réalisé'!D9+'Modèle renommé'!U321-'Modèle renommé'!T321,NA())")
        # Independent cash oracle: actual close200 plus forecast future cash
        # movement150-130 =220, not actual200+forecast150=350.
        self.assertEqual(Decimal('200')+(Decimal('150')-Decimal('130')),Decimal('220'))
        self.assertEqual({o['sheet'] for o in result['operations'] if 'sheet' in o},{'TCA Réalisé','TCA Actualisé'})
        self.assertTrue(all(o.get('evidence_id')=='source_fictive' for o in result['operations']))
        self.assertNotIn('IFERROR', '\n'.join(o.get('formula','') for o in result['operations']))

    def test_missing_history_zero_and_unbalanced_actuals_remain_distinct(self):
        actuals,budget,series,locations=fixture()
        actuals['rows']=[r for r in actuals['rows'] if r['metric'] not in ('cash','payments')]
        next(r for r in actuals['rows'] if r['metric']=='revenue')['value']='0'
        next(r for r in actuals['rows'] if r['metric']=='assets')['value']='501'
        result=plan_reforecast(actuals,budget,series,locations)
        changes={(o.get('sheet'),o.get('cell')):o for o in result['operations'] if o['type'].startswith('set_')}
        self.assertEqual(changes[('TCA Réalisé','D6')]['value'],0)
        self.assertNotIn(('TCA Réalisé','D9'),changes)
        self.assertIn('NA()',changes[('TCA Actualisé','E9')]['formula'])
        self.assertEqual(result['balance_at_cutoff']['residual'],'1')
        self.assertIn('CASH_ARRETE_MANQUANT',[d['code'] for d in result['diagnostics']])

    def test_source_unit_period_duplicates_and_unowned_sheet_refused(self):
        for change in ['source','unit','period','duplicate','unowned']:
            actuals,budget,series,locations=fixture()
            options={}
            if change=='source':actuals['rows'][0]['evidence_id']=None
            if change=='unit':actuals['rows'][0]['unit']='USD'
            if change=='period':actuals['rows'][0]['period']='2026-02'
            if change=='duplicate':actuals['rows'].append(deepcopy(actuals['rows'][0]))
            if change=='unowned':options['existing']={'TCA Réalisé':{'marker':'USER_DATA','cells':{}}}
            with self.subTest(change=change), self.assertRaises(ValueError):
                plan_reforecast(actuals,budget,series,locations,**options)

    def test_renamed_owned_sheets_and_stale_cells_follow_preview(self):
        actuals,budget,series,locations=fixture()
        existing={'Réalisé renommé':{'marker':ACTUAL_MARKER,'cells':{'X99':{'value':123,'formula':None}}},
                  'Actualisé renommé':{'marker':FORECAST_MARKER,'cells':{}}}
        result=plan_reforecast(actuals,budget,series,locations,existing=existing)
        self.assertFalse(any(o['type']=='add_sheet' for o in result['operations']))
        cleared=next(o for o in result['operations'] if o.get('cell')=='X99')
        self.assertIsNone(cleared['value'])
        self.assertEqual(cleared['sheet'],'Réalisé renommé')
        self.assertTrue(any("'Réalisé renommé'!" in o.get('formula','') for o in result['operations']))

    def test_dense_ten_years_preserve_every_observation_and_formula(self):
        periods=[f'{year}-{month:02d}' for year in range(2026,2036) for month in range(1,13)]
        series=[{'id':metric,'categories':periods,'values':[100]*120,'unit':'EUR'}
                for metric in ('revenue','receipts','payments','cash')]
        rows=[{'period':period,'metric':metric,'kind':kind,'unit':'unités' if metric=='volume' else 'EUR',
               'value':str(month*100+number),'evidence_id':f'source_fictive_{metric}'}
              for month,period in enumerate(periods) for number,(metric,kind,_) in enumerate(METRICS)]
        actuals={'status':'CONFIRME','cutoff':'2035-12-31','rows':rows}
        budget={'source_sha256':'b'*64,'series':deepcopy(series)}
        locations={metric:{period:('Modèle fictif',_col(20+i)+str(row)) for i,period in enumerate(periods)}
                   for metric,row in [('revenue',88),('receipts',301),('payments',320),('cash',321)]}
        result=plan_reforecast(actuals,budget,series,locations)
        self.assertGreater(result['atomic_operation_count'],2000)
        self.assertLessEqual(result['envelope_count'],2000)
        self.assertTrue(any(op['type']=='set_block' for op in result['operations']))
        expanded=expand_operations(result['operations'])
        self.assertEqual(len(expanded),result['atomic_operation_count'])
        self.assertEqual(sum(op['type']=='set_formula' for op in expanded),484)
        values={(op.get('sheet'),op.get('cell')):op for op in expanded if op['type']=='set_value'}
        for i,period in enumerate(periods):
            for j,(metric,_,_) in enumerate(METRICS):
                cell=values[('TCA Réalisé',_col(4+i)+str(6+j))]
                self.assertEqual(cell['value'],i*100+j)
                self.assertEqual(cell['evidence_id'],f'source_fictive_{metric}')
        self.assertEqual(len(rows),1560)
        self.assertEqual(result['forecast_balance_status'],'NON_RECONSTRUIT')


if __name__=='__main__':unittest.main()
