from copy import deepcopy
import unittest
from xml.etree import ElementTree as ET

from tca_bp.decision_offers import (extended_origin_schema, plan_extension, rewrite_clone_formula, materialize_extension)
from tca_bp.vendor import input_engine as core
from tca_bp.formula_bindings import bind_index_literals
from tca_bp.web_model_profile import refresh_profile, map_location, seal_profile
from tca_bp.web_structure import plan_operations
from tca_bp.web_chat import validate_operations


def profile():
    spec={'kind':'text','field_id':'employee_name','label':'Nom','allow_blank':True}
    schema={'cells':{'Effectifs':{'B116':spec}},'registers':{'Effectifs':{
        'start_row':17,'end_row':116,'identity_columns':['B'],'required':['B']}},
        'business_rules':[{'sheet':'Effectifs','type':'required_record','rows':list(range(17,117)),
                           'trigger':['B'],'cols':['B']} ]}
    return refresh_profile({'schema':'tca-bp-web-profile/1','version':1,
        'origin_schema':schema,'origin_catalogue':[{'id':'employee_name','sheet':'Effectifs','cells':['B116']}],
        'sheets':[{'id':'staff','name':'Effectifs','original_name':'Effectifs','index':1,'deleted':False,'transforms':[]}],
        'base_agents':[],'formula_changes':[],'value_changes':[],'operations':[]})


class RepeatableBindings(unittest.TestCase):
    def test_register_extension_has_owners_rules_and_geometry_then_follows_rename(self):
        before=profile();original=deepcopy(before['origin_schema'])
        ops,after=plan_operations(before,[{'type':'extend_register','sheet':'Effectifs','count':2,'evidence_id':'src'}])
        self.assertEqual(before['origin_schema'],original)
        self.assertEqual(after['origin_schema'],original)
        self.assertEqual(map_location(after,'Effectifs','B116')['cell'],'B118')
        self.assertEqual(map_location(after,'Effectifs','B900001')['cell'],'B116')
        self.assertEqual(map_location(after,'Effectifs','B900002')['cell'],'B117')
        self.assertEqual(map_location(after,'Effectifs','A900002')['cell'],'A117')
        self.assertEqual(map_location(after,'Effectifs','B117',reverse=True)['cell'],'B900002')
        logical=extended_origin_schema(after)
        self.assertEqual(logical['registers']['Effectifs']['extra_rows'],[900001,900002])
        self.assertIn(900002,logical['business_rules'][0]['rows'])
        _,moved=plan_operations(after,[{'type':'insert_rows','sheet':'Effectifs','index':1,'count':1},
                                     {'type':'rename_sheet','sheet':'Effectifs','name':'Equipe'}])
        self.assertEqual(map_location(moved,'Effectifs','B900001')['sheet'],'Equipe')
        self.assertEqual(map_location(moved,'Effectifs','B900001')['cell'],'B117')
        self.assertEqual(set(moved['fields'][0]['cells']),{'B117','B118','B119'})

    def test_free_row_is_not_a_business_record_and_deleted_owner_is_not_reassigned(self):
        before=profile();_,free=plan_operations(before,[{'type':'insert_rows','sheet':'Effectifs','index':116,'count':1}])
        self.assertIsNone(map_location(free,'Effectifs','B116',reverse=True))
        _,extended=plan_operations(before,[{'type':'extend_register','sheet':'Effectifs','count':1,'evidence_id':'src'}])
        _,removed=plan_operations(extended,[{'type':'delete_rows','sheet':'Effectifs','index':116,'count':1}])
        self.assertIsNone(map_location(removed,'Effectifs','B900001'))
        self.assertTrue(any(d['cell']=='B900001' for d in removed['deleted_owners']))

    def test_copied_formula_keeps_absolute_own_inputs_and_global_ranges(self):
        before=profile();ops,after=plan_operations(before,[{'type':'extend_register','sheet':'Effectifs','count':1,'evidence_id':'src'}])
        self.assertEqual(rewrite_clone_formula('$B$116+SUM(B17:B116)', 'Effectifs',before,after,ops[0]['clones']),
                         '$B$116+SUM(B17:B117)')
        self.assertEqual(rewrite_clone_formula('"B116"&B116', 'Effectifs',before,after,ops[0]['clones']),
                         '"B116"&B116')

    def test_business_scope_and_evidence_required(self):
        operation={'type':'extend_register','sheet':'Effectifs','count':1,'evidence_id':'src'}
        context={'case_id':'c','sources':[{'id':'src','case_id':'c'}]}
        self.assertEqual(validate_operations([operation],{'sheet':'Effectifs','allow_structure':True},context),[operation])
        for scope in ({'sheet':'Effectifs'}, {'sheet':'Effectifs','allow_structure':True,'range':'B116'}):
            with self.assertRaises(ValueError):validate_operations([operation],scope,context)
        with self.assertRaises(ValueError):plan_operations(profile(),[{**operation,'count':True}])
        with self.assertRaises(ValueError):plan_operations(profile(),[{**operation,'clones':[]}])

    def test_business_merge_is_complete_and_only_anchor_is_written(self):
        before=profile()
        ops,after=plan_operations(before,[{'type':'extend_register','sheet':'Effectifs','count':1,'evidence_id':'src'}])
        class Book:
            merge='B116:C116'
            def sheet(self,sheet):
                root=ET.fromstring('<worksheet xmlns="'+core.NS+'"><mergeCells><mergeCell ref="'+self.merge+'"/></mergeCells></worksheet>')
                return root,{'B116':None,'C116':None},{}
            def formula(self,*args):return None
            def value(self,*args):return 'Existing employee'
        book=Book()
        operation,_=materialize_extension(book,before,after,ops[0])
        self.assertEqual(operation['cells'],[{'sheet':'Effectifs','cell':'B116','value':None}])
        book.merge='B116:C117'
        with self.assertRaisesRegex(ValueError,'fusion traverse'):
            materialize_extension(book,before,after,ops[0])


class PositionalReferenceBindings(unittest.TestCase):
    def test_insert_inside_index_binds_target_but_whole_range_translation_does_not(self):
        before=profile()
        _,after=plan_operations(before,[{'type':'insert_rows','sheet':'Effectifs','index':100,'count':1}])
        formula='INDEX(Effectifs!$B$1:$Z$120,116,0)'
        fixed=bind_index_literals(formula,'Effectifs',before,after)
        self.assertIn("ROW('Effectifs'!$B$116)-ROW('Effectifs'!$B$1)+1",fixed)
        self.assertEqual(bind_index_literals('"INDEX(B1:Z120,116,1)"','Effectifs',before,after),'"INDEX(B1:Z120,116,1)"')
        _,shifted=plan_operations(before,[{'type':'insert_rows','sheet':'Effectifs','index':1,'count':1}])
        self.assertEqual(bind_index_literals(formula,'Effectifs',before,shifted),formula)

    def test_deleted_index_target_becomes_real_reference_to_expose_ref_error(self):
        before=profile();_,after=plan_operations(before,[{'type':'delete_rows','sheet':'Effectifs','index':116,'count':1}])
        fixed=bind_index_literals('INDEX(B1:Z120,116,1)','Effectifs',before,after)
        self.assertIn("ROW('Effectifs'!$B$116)",fixed)


if __name__=='__main__':unittest.main()
