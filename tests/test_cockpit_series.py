"""Recognition, invoices and receipts are different source series, not aliases."""
from types import SimpleNamespace
import unittest

from tca_bp.decision_model import read_series


class CockpitSeriesTests(unittest.TestCase):
    def workspace(self, current=True):
        # Deliberately divergent months: recognition over four months, invoice
        # deposit/final and customer receipts delayed by one month.
        values={('Control','C10'):46023,('Control','C59'):1}
        from tca_bp.vendor.input_engine import colname
        for offset in range(12):
            for row,series in ((282,[120]*4),(283,[96,0,0,384]),(284,[0,96,0,0,384])):
                values['Revenue',colname(16+offset)+str(row)]=series[offset] if offset<len(series) else 0
            values['Modèle financier',colname(20+offset)+'88']=90000+offset
            values['Modèle financier',colname(20+offset)+'301']=1000+offset
            values['Modèle financier',colname(20+offset)+'320']=100
            values['Modèle financier',colname(20+offset)+'321']=10000+offset
        wb=SimpleNamespace(date1904=False,value=lambda sheet,cell:values.get((sheet,cell)))
        scopes={key:{'scenario_ready':True,'status':'QUALIFIE'} for key in ('CA','CASH')}
        case={'revision':7,'outputs_current':current,'qualified_availability':scopes}
        d=SimpleNamespace(app=SimpleNamespace(engine_for_case=lambda _:SimpleNamespace(),get_case=lambda _:case),
            profile=lambda _:{},work=SimpleNamespace(_read=lambda _,callback:callback(wb,{})))
        return d,values

    def test_distinct_series_keep_source_period_unit_and_revision(self):
        d,_=self.workspace()
        result={series['id']:series for series in read_series(d,'fictitious')}
        self.assertEqual(result['revenue']['values'][:5],[120,120,120,120,0])
        self.assertEqual(result['billed_revenue']['values'][:5],[96,0,0,384,0])
        self.assertEqual(result['customer_receipts']['values'][:5],[0,96,0,0,384])
        self.assertEqual(result['receipts']['values'][0],1000)
        self.assertEqual(result['receipts']['label'],'Encaissements totaux')
        self.assertEqual(result['revenue']['sources'][0],{'sheet':'Revenue','cell':'P282'})
        for series in result.values():
            self.assertEqual(series['unit'],'EUR')
            self.assertEqual(series['revision'],7)
            self.assertEqual(series['case_id'],'fictitious')
            self.assertEqual(series['categories'][0],'2026-01')
            self.assertEqual(len(series['values']),12)

    def test_missing_and_stale_values_are_never_replaced_with_billing_or_zero(self):
        d,values=self.workspace()
        del values['Revenue','P282']
        result={series['id']:series for series in read_series(d,'fictitious')}
        self.assertIsNone(result['revenue']['values'][0])
        self.assertEqual(result['billed_revenue']['values'][0],96)
        stale,_=self.workspace(current=False)
        self.assertTrue(all(value is None for series in read_series(stale,'fictitious') for value in series['values']))
