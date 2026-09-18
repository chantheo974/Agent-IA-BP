import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import install_ocr


class InstallerTests(unittest.TestCase):
    def test_missing_and_different_runtime_never_execute_or_replace(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / 'personal.txt').write_text('preserve', encoding='utf-8')
            self.assertEqual(install_ocr.inspect_runtime(target)['status'], 'ABSENT_OR_DIFFERENT')
            with patch.object(install_ocr, 'runtime_path', return_value=target), patch.object(install_ocr.subprocess, 'run') as run:
                with self.assertRaises(RuntimeError):
                    install_ocr.install()
                run.assert_not_called()
            self.assertEqual((target/'personal.txt').read_text(encoding='utf-8'), 'preserve')

    def test_pinned_download_refuses_mismatch(self):
        class Response(io.BytesIO):
            def geturl(self):
                return 'https://example.invalid/file'
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(install_ocr.urllib.request, 'urlopen', return_value=Response(b'bad payload')):
                with self.assertRaises(RuntimeError):
                    install_ocr._download('https://example.invalid/file',Path(directory)/'payload','0'*64)

    def test_existing_verified_runtime_is_idempotent(self):
        with (patch.object(install_ocr, 'runtime_path', return_value=Path('fixture')),
              patch.object(install_ocr, 'inspect_runtime', return_value={'status':'READY'}),
              patch.object(install_ocr, '_download') as download):
            self.assertTrue(install_ocr.install()['already_installed'])
            download.assert_not_called()
