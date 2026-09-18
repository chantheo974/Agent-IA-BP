from pathlib import Path
import tempfile
import unittest
from tests.test_model_versions import fixture
from tca_bp.web_model import initial_profile
from tca_bp.web_model_profile import seal_profile
from tca_bp.web_validation import prepare_native_operations


class InputContractsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.engine=fixture(self.root/'model')
        self.profile=initial_profile(self.engine,self.engine.template_path)

    def tearDown(self):self.temp.cleanup()

    def prepare(self,ops,profile=None):
        return prepare_native_operations(self.engine,self.engine.template_path,profile or self.profile,ops)

    def test_existing_numeric_constraint_follows_inserted_row(self):
        operations=[{'type':'insert_rows','sheet':'Inputs','index':1,'count':1},
                    {'type':'set_value','sheet':'Inputs','cell':'A2','value':101,'evidence_id':'source'}]
        with self.assertRaisesRegex(ValueError,'maximum'):
            self.prepare(operations)
        operations[-1]['value']=50
        self.assertEqual(self.prepare(operations)[-1]['value'],50)

    def test_date_serialization_is_native_numeric_and_leaves_user_proposal_intact(self):
        self.profile['origin_schema']['cells']['Inputs']['A1']={'kind':'date','fill':None}
        self.profile=seal_profile(self.profile)
        operations=[{'type':'set_value','sheet':'Inputs','cell':'A1','value':'2027-01-01','evidence_id':'source'}]
        self.assertEqual(self.prepare(operations)[0]['value'],46388)
        self.assertEqual(operations[0]['value'],'2027-01-01')
        operations[0]['value']='2027-02-31'
        with self.assertRaisesRegex(ValueError,'Date inexistante'):
            self.prepare(operations)

    def test_new_free_cells_remain_available_for_explicit_workspace_editing(self):
        ops=[{'type':'set_value','sheet':'Inputs','cell':'C10','value':'Annotation','evidence_id':'source'}]
        self.assertEqual(self.prepare(ops),ops)


if __name__=='__main__':unittest.main()
