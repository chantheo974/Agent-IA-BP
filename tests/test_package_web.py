"""Verify complete web packages without including any client document."""
import json
import hashlib
import shutil
import unittest
import zipfile
from tca_bp.initial_model import CONFIG, ARCHIVES, SCHEMA, initial_engine
from tca_bp.model_registry import ModelRegistry, model_pin
from tca_bp.storage import atomic_json,canonical
from tests.test_model_versions import fixture
from tools import package_web as package
from tests import test_package_app as fixtures


class WebPackageTests(unittest.TestCase):
    write=fixtures.PackageTests.write
    rewrite=fixtures.PackageTests.rewrite
    tearDown=fixtures.PackageTests.tearDown
    def setUp(self):
        fixtures.PackageTests.setUp(self)
        for name in package.ROOT|package.WEB_CODE:
            self.write(name,b'{}' if name.endswith('.json') else b'# Fixture web\n')
        self.write('frontend/dist/index.html',b'<script type="module" src="/assets/main.js"></script>')
        self.write('frontend/dist/assets/main.js',b'import("./workshop.js");')
        self.write('frontend/dist/assets/workshop.js',b'export const title="Fixture";')
        self.write('frontend/node_modules/fictif/package.json',b'{"name":"fictif","version":"1"}')
        self.write('frontend/node_modules/fictif/LICENSE',b'License fixture')

    def test_build_verify_required_modules_and_no_overwrite(self):
        result=package.build(self.root,self.output)
        self.assertEqual(result['status'],'VERIFIE')
        self.assertEqual(result['package_sha256'],package.verify(self.output)['package_sha256'])
        with zipfile.ZipFile(self.output) as archive:
            self.assertTrue(package.WEB_REQUIRED.issubset(archive.namelist()))
            manifest=json.loads(archive.read(package.MANIFEST))
            self.assertFalse(manifest['node_required_at_runtime'])
            self.assertIn('tca_bp/decision_actuals.py',archive.namelist())
            self.assertIn('tools/install_ocr.py',archive.namelist())
        before=self.output.read_bytes()
        with self.assertRaises((ValueError,FileExistsError)): package.build(self.root,self.output)
        self.assertEqual(before,self.output.read_bytes())

    def test_missing_lazy_chunk_and_altered_archive_refused(self):
        (self.root/'frontend/dist/assets/workshop.js').unlink()
        with self.assertRaisesRegex(ValueError,'manquante'): package.build(self.root,self.output)
        self.write('frontend/dist/assets/workshop.js',b'export const title="Fixture";')
        package.build(self.root,self.output)
        altered=self.rewrite(self.output,lambda parts:parts.update({'frontend/dist/assets/main.js':b'ALTERED'}))
        with self.assertRaisesRegex(ValueError,'Empreinte'): package.verify(altered)

    def test_cockpit_sprite_requires_its_license_and_provenance(self):
        self.write('frontend/dist/icone/iconoir-sprite.svg', b'<svg xmlns="http://www.w3.org/2000/svg"/>')
        with self.assertRaises(ValueError):
            package.build(self.root, self.output)
        for name in package.COPIED_ASSET_NOTICES:
            self.write(name, b'MIT Iconoir fixture attribution')
        package.build(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertTrue(package.COPIED_ASSET_NOTICES.issubset(archive.namelist()))
            self.assertIn('tca_bp/cockpit_simulations.py', archive.namelist())

    def test_private_files_excluded_and_path_escape_refused(self):
        self.write('runtime/web_settings.json',b'NE_PAS_LIVRER')
        self.write('exemple/client.xlsm',b'NE_PAS_LIVRER')
        package.build(self.root,self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertFalse(any('NE_PAS_LIVRER' in archive.read(n).decode('utf-8',errors='ignore') for n in archive.namelist()))
        for name in ('../credentials','frontend/dist/../../credentials','frontend/dist/con.js','frontend/dist/.env'):
            self.assertFalse(package.allowed(name))

    def test_selected_initial_archive_is_complete_pinned_and_never_substituted(self):
        engine=fixture(self.root/'candidate',model_id='fixture/initial')
        pin=ModelRegistry(self.root/ARCHIVES,self.root).register(engine)
        atomic_json(self.root/CONFIG,{'schema':SCHEMA,**pin})
        package.build(self.root,self.output)
        with zipfile.ZipFile(self.output) as archive:
            manifest=json.loads(archive.read(package.MANIFEST))
            self.assertEqual(manifest['initial_model'],pin)
            self.assertIn(ARCHIVES+'/'+pin['model_ref']+'/seal.json',archive.namelist())
            self.assertIn(package.base.MODEL_PREFIX+package.base.TEMPLATE,archive.namelist())
        selected=self.root/ARCHIVES/pin['model_ref']/package.base.TEMPLATE
        selected.write_bytes(selected.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'modifié'):
            package.collect(self.root)

    def test_valid_initial_seal_with_unicode_escaped_private_provenance_is_not_collected(self):
        engine=fixture(self.root/'candidate',model_id='fixture/initial')
        # An actual compressed optional component: describe preserves its
        # storage metadata, unlike an unknown top-level seal attribute.
        atomic_json(engine.model_dir/'graphe_dependances.json',{'padding':'x'*(1024*1024)})
        registry=ModelRegistry(self.root/ARCHIVES,self.root)
        original=registry.register(engine)
        original_folder=self.root/ARCHIVES/original['model_ref']
        seal=json.loads((original_folder/'seal.json').read_text(encoding='utf-8'))
        storage=seal['storage']['graphe_dependances.json']
        self.assertEqual(storage['codec'],'gzip')
        storage['provenance']=r'C:\Users\FICTITIOUS_PRIVATE\build'
        unsigned={key:value for key,value in seal.items() if key!='model_ref'}
        seal['model_ref']=hashlib.sha256(canonical(unsigned).encode()).hexdigest()
        selected=model_pin(seal)
        destination=self.root/ARCHIVES/selected['model_ref']
        shutil.copytree(original_folder,destination)
        raw=canonical(seal).replace('Users',r'\u0055sers').encode('utf-8')
        self.assertFalse(package.base.PERSONAL_PATH.search(raw))
        self.assertIn('Users',json.loads(raw)['storage']['graphe_dependances.json']['provenance'])
        (destination/'seal.json').write_bytes(raw)
        atomic_json(self.root/CONFIG,{'schema':SCHEMA,**selected})
        # This is a valid immutable pin, not a deliberately broken hash that
        # would be rejected before any privacy/content check is exercised.
        loaded=initial_engine(self.root)
        self.assertEqual(model_pin(registry.describe(loaded)),selected)
        registry.verify(selected)
        with self.assertRaisesRegex(ValueError,'portable|priv|personnel|provenance'):
            package.collect(self.root)
        self.assertFalse(self.output.exists())
