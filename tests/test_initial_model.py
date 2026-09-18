from pathlib import Path
import tempfile
import unittest

from tca_bp.initial_model import CONFIG, ARCHIVES, SCHEMA, initial_engine
from tca_bp.model_registry import ModelRegistry, model_pin
from tca_bp.service import Application
from tca_bp.storage import atomic_json
from tests.test_model_versions import fixture


class InitialModelTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='tca-initial-')
        self.root=Path(self.temp.name)
        self.old=fixture(self.root/'models/generic-v1',model_id='tca-bp-template/1')
        self.new=fixture(self.root/'candidate',multiple=3,maximum=10,model_id='fixture/new')

    def tearDown(self):self.temp.cleanup()

    def select(self):
        pin=ModelRegistry(self.root/ARCHIVES,self.root).register(self.new)
        atomic_json(self.root/CONFIG,{'schema':SCHEMA,**pin})
        return pin

    def test_new_default_keeps_existing_dossier_model_and_sources_after_restart(self):
        old=Application(self.root,self.root/'data')
        a=old.create_case('Fictif','Avant mise à jour',case_id='old')
        source=old.add_source('old',text='Source à conserver.')
        selected=self.select()
        fresh=Application(self.root,self.root/'data')
        b=fresh.create_case('Fictif','Nouvelle trame',case_id='new')
        self.assertEqual(model_pin(b),selected)
        self.assertEqual(model_pin(fresh.get_case('old')),model_pin(a))
        self.assertEqual(fresh.inspect('old','Inputs',['B1'])['cells']['B1']['current']['formula'],'A1*2')
        self.assertEqual(fresh.inspect('new','Inputs',['B1'])['cells']['B1']['current']['formula'],'A1*3')
        self.assertEqual(fresh.get_case('old')['sources'][0]['id'],source['id'])

    def test_missing_or_altered_selected_model_never_falls_back(self):
        pin=self.select()
        template=self.root/ARCHIVES/pin['model_ref']/'TCA_BP_Trame_generique.xlsm'
        before=template.read_bytes()
        template.write_bytes(before+b'changed')
        with self.assertRaisesRegex(ValueError,'modifié'):initial_engine(self.root)
        template.unlink()
        with self.assertRaises(ValueError):initial_engine(self.root)
        self.assertTrue(self.old.template_path.is_file())

    def test_unknown_configuration_and_path_like_pin_refused(self):
        pin=self.select()
        atomic_json(self.root/CONFIG,{'schema':SCHEMA,**pin,'path':'../outside'})
        with self.assertRaises(ValueError):initial_engine(self.root)
        atomic_json(self.root/CONFIG,{'schema':SCHEMA,**pin,'model_ref':'../outside'})
        with self.assertRaises(ValueError):initial_engine(self.root)


if __name__=='__main__':unittest.main()
