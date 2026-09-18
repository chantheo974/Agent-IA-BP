"""A changed shared anchor must not change or orphan unaffected followers."""
import unittest
from xml.etree import ElementTree as ET
from tca_bp.model_build import _materialize_orphaned_shared_formulas, NS, N


class SharedMigrationTests(unittest.TestCase):
    def worksheet(self, cells):
        return ('<worksheet xmlns="'+NS+'"><sheetData><row r="1">'+cells+'</row></sheetData></worksheet>').encode()

    def test_replaced_anchor_preserves_each_effective_follower_and_unrelated_groups(self):
        raw=self.worksheet('<c r="A1"><f>IF(B1="Oui",1,NA())</f></c>'
            '<c r="B1" s="4"><f t="shared" si="7"/><v>99</v></c>'
            '<c r="C1"><f t="shared" si="7"/></c>'
            '<c r="D1"><f t="shared" si="8" ref="D1:E1">A2+1</f></c>'
            '<c r="E1"><f t="shared" si="8"/></c>'
            '<c r="F1"><f t="dataTable" ref="F1:G2" dt2D="1"/></c>')
        calls=[]
        def effective(address):
            calls.append(address);return {'B1':'C1+1','C1':'D1+1'}[address]
        changed=_materialize_orphaned_shared_formulas(raw,effective)
        cells={c.get('r'):c for c in ET.fromstring(changed).findall('.//m:c',N)}
        self.assertEqual(calls,['B1','C1'])
        for address,expected in [('B1','C1+1'),('C1','D1+1')]:
            self.assertEqual(cells[address].find('m:f',N).text,expected)
            self.assertEqual(cells[address].find('m:f',N).attrib,{})
            self.assertIsNone(cells[address].find('m:v',N))
        self.assertEqual(cells['B1'].get('s'),'4')
        for fragment in (b'<f>IF(B1="Oui",1,NA())</f>',b'<f t="shared" si="8"/>',b'<f t="dataTable" ref="F1:G2" dt2D="1"/>'):
            self.assertIn(fragment,changed)
        self.assertEqual(_materialize_orphaned_shared_formulas(changed,effective),changed)

    def test_unchanged_group_is_byte_preserved_and_no_source_read(self):
        raw=self.worksheet('<c r="A1"><f t="shared" si="0" ref="A1:B1">C1+1</f></c><c r="B1"><f t="shared" si="0"/></c>')
        def forbidden(address):raise AssertionError(address)
        self.assertEqual(_materialize_orphaned_shared_formulas(raw,forbidden),raw)

    def test_absent_effective_formula_or_group_id_refused(self):
        raw=self.worksheet('<c r="B1"><f t="shared" si="0"/></c>')
        with self.assertRaisesRegex(ValueError,'effective source'):_materialize_orphaned_shared_formulas(raw,lambda address:None)
        with self.assertRaisesRegex(ValueError,'identifiant'):_materialize_orphaned_shared_formulas(raw.replace(b' si="0"',b''),lambda address:'A1')


if __name__=='__main__':unittest.main()
