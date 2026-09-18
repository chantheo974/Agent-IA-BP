"""Les scripts pilotant Excel et l'installation doivent s'analyser sous Windows PowerShell 5.1.

Windows PowerShell traite les guillemets typographiques (U+2018, U+2019, U+201C,
U+201D) comme des délimiteurs de chaîne : un seul suffit à rendre tout le script
inanalysable. Sans BOM, il lit par ailleurs le fichier en page de code ANSI et
les messages accentués deviennent illisibles.
"""
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = sorted(ROOT.glob('*.ps1')) + sorted((ROOT / 'tca_bp').glob('*.ps1'))
TYPOGRAPHIC = {'\u2018', '\u2019', '\u201c', '\u201d'}


class PowerShellScriptTests(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertGreaterEqual(len(SCRIPTS), 6)

    def test_accented_scripts_declare_utf8_and_avoid_typographic_quotes(self):
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                raw = script.read_bytes()
                text = raw.decode('utf-8-sig')
                found = sorted(TYPOGRAPHIC & set(text))
                self.assertEqual(found, [], f"{script.name} : guillemet typographique {found}")
                if any(byte > 127 for byte in raw.replace(b'\xef\xbb\xbf', b'', 1)):
                    self.assertTrue(raw.startswith(b'\xef\xbb\xbf'), f'{script.name} : BOM UTF-8 requis')

    @unittest.skipIf(os.name != 'nt', 'Analyseur Windows PowerShell requis')
    def test_scripts_parse_with_windows_powershell(self):
        shell = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        if not shell.is_file():
            self.skipTest('powershell.exe absent')
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                quoted = "'" + str(script).replace("'", "''") + "'"
                command = ('$errors=$null;'
                           f'[System.Management.Automation.Language.Parser]::ParseFile({quoted},[ref]$null,[ref]$errors)|Out-Null;'
                           'if($errors.Count){Write-Output $errors[0].Message;exit 1};exit 0')
                done = subprocess.run([str(shell), '-NoProfile', '-NonInteractive', '-Command', command],
                                      capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
                self.assertEqual(done.returncode, 0, f'{script.name} : {done.stdout.strip()}')


if __name__ == '__main__':
    unittest.main()
