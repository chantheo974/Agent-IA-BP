import unittest
from tca_bp.web_blocks import expand_operations, compact_setters, ExpandedOperations


class BlockTests(unittest.TestCase):
    def block(self,rows,**kwargs):
        return {'type':'set_block','sheet':'Test','start_cell':'B3','rows':rows,'evidence_id':'source_a',**kwargs}

    def test_values_formulas_holes_zero_and_clear_have_exact_coordinates(self):
        result=expand_operations([self.block([[{'value':0},None,{'formula':'=B3*2','evidence_id':'source_b'}],
                                             [{'value':None,'status':'NON_RENSEIGNE'},{'value':5,'status':'CONFIRME'},None]])])
        self.assertEqual([o['cell'] for o in result],['B3','D3','B4','C4'])
        self.assertEqual(result[0]['value'],0)
        self.assertIsNone(result[2]['value'])
        self.assertEqual(result[1]['evidence_id'],'source_b')
        self.assertEqual(result[3]['status'],'CONFIRME')

    def test_rectangles_nested_operations_bounds_and_number_injection_refused(self):
        cases=[self.block([[{'value':1}],[]]),self.block([[{'type':'delete_sheet','value':1}]]),
               self.block([[{'value':'=1+1'}]]),self.block([[{'value':float('nan')}]]),
               self.block([[{'value':1},{'value':2}]],start_cell='XFD1'),
               self.block([[{'value':None,'status':'CONFIRME'}]]),self.block([[{'formula':'1+1'}]]),
               self.block([[None]]),self.block([[{'value':1}]],evidence_id='')]
        for block in cases:
            with self.subTest(block=block),self.assertRaises(ValueError):expand_operations([block])

    def test_large_block_is_bounded_but_raw_large_list_remains_refused(self):
        block=self.block([[{'value':i} for i in range(100)] for _ in range(50)])
        expanded=expand_operations([block])
        self.assertEqual(len(expanded),5000)
        self.assertIsInstance(expanded,ExpandedOperations)
        self.assertEqual(len(expand_operations(expanded)),5000)
        with self.assertRaises(ValueError):expand_operations(list(expanded))
        with self.assertRaises(ValueError):expand_operations([block]*5)

    def test_compaction_preserves_evidence_duplicates_and_structural_order(self):
        original=[{'type':'set_value','sheet':'Test','cell':f'A{i}','value':i,'evidence_id':f'source_{i%2}'} for i in range(1,11)]
        original += [{'type':'insert_rows','sheet':'Test','index':1,'count':1},
                     {'type':'set_value','sheet':'Test','cell':'A1','value':21,'evidence_id':'source_b'},
                     {'type':'set_value','sheet':'Test','cell':'A1','value':22,'evidence_id':'source_b'}]
        compact=compact_setters(original)
        self.assertEqual(compact[0]['type'],'set_block')
        self.assertEqual(expand_operations(compact),original)


if __name__=='__main__':unittest.main()
