"""Versioned compressed storage retains exact logical and physical evidence."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

from tests.test_model_versions import fixture
from tca_bp.model_components import read_component
from tca_bp.model_registry import ModelRegistry, model_pin
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core


class ModelCompressionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.engine=fixture(self.root/'source')
        self.registry=ModelRegistry(self.root/'archives',self.root)

    def test_same_size_restored_timestamp_tamper_is_detected_in_loaded_process(self):
        pin=self.registry.register(self.engine);self.registry.resolve(pin)
        target=self.root/'archives'/pin['model_ref']/'modele.json'
        stat=target.stat();raw=target.read_bytes();target.write_bytes(raw.replace(b'100',b'999',1))
        os.utime(target,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        self.assertEqual(target.stat().st_size,stat.st_size)
        with self.assertRaisesRegex(ValueError,'modifié'):self.registry.resolve(pin)

    def test_model_open_closes_zip_on_corrupt_styles_xml_or_unexpected_interruption(self):
        for error in (IndexError('style index'),ET.ParseError('sheet XML'),RuntimeError('unexpected'),KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__):
                book=core.Workbook(self.engine.template_path)
                expected=ValueError if isinstance(error,(IndexError,ET.ParseError)) else type(error)
                with patch('tca_bp.model_engine.core.Workbook',return_value=book),\
                     patch('tca_bp.model_engine.core.verify_model'),\
                     patch.object(self.engine,'_cell_protection_signature',side_effect=error):
                    with self.assertRaises(expected):self.engine._open(self.engine.template_path)
                self.assertIsNone(book.z.fp)

    def test_gzip_roundtrip_checks_stored_and_logical_hash_without_disk_expansion(self):
        source=self.engine.model_dir/'classification_cellules.json'
        raw=canonical({'fixture':'example-data '*150000}).encode();source.write_bytes(raw)
        pin=self.registry.register(self.engine);folder=self.root/'archives'/pin['model_ref']
        seal=self.registry.verify(pin)
        self.assertEqual(seal['schema'],'tca-bp-model-archive/2')
        self.assertFalse((folder/source.name).exists())
        compressed=folder/(source.name+'.gz')
        self.assertLess(compressed.stat().st_size,len(raw)//10)
        self.assertEqual(read_component(folder/source.name),raw)
        self.assertEqual(self.registry.register(self.registry.resolve(pin)),pin)
        before=compressed.read_bytes();stat=compressed.stat()
        changed=bytearray(before);changed[4]^=1;compressed.write_bytes(changed)
        os.utime(compressed,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        with self.assertRaisesRegex(ValueError,'modifié'):self.registry.verify(pin)
        compressed.write_bytes(before)
        # Even a coherent physical hash cannot attest a false uncompressed size.
        forged=json.loads((folder/'seal.json').read_text(encoding='utf-8'))
        forged['storage'][source.name]['size']=7
        unsigned={k:v for k,v in forged.items() if k!='model_ref'}
        forged['model_ref']=hashlib.sha256(canonical(unsigned).encode()).hexdigest()
        (folder/'seal.json').write_text(canonical(forged),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Décompression'):read_component(folder/source.name)

    def test_plain_v1_archive_is_read_without_implicit_migration(self):
        description=self.registry.describe(self.engine)
        seal={k:v for k,v in description.items() if k not in ('model_ref','storage')}
        seal['schema']='tca-bp-model-archive/1'
        seal['model_ref']=hashlib.sha256(canonical(seal).encode()).hexdigest()
        folder=self.root/'archives'/seal['model_ref'];folder.mkdir(parents=True)
        for name in seal['files']:shutil.copyfile(self.engine.model_dir/name,folder/name)
        (folder/'seal.json').write_text(canonical(seal),encoding='utf-8')
        pin=model_pin(seal);engine=self.registry.resolve(pin)
        self.assertEqual(engine.schema,self.engine.schema)
        self.assertEqual(self.registry.register(engine),pin)
        self.assertEqual(self.registry.verify(pin)['schema'],'tca-bp-model-archive/1')


if __name__=='__main__':unittest.main()
