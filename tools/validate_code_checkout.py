"""Tester le code distribué dans une copie dépourvue de trame et de sources."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = ('tca_bp', 'tests', 'tools', 'docs', 'agents', '.vscode', '.github')
ROOT_FILES = ('.gitattributes', '.gitignore', 'README.md', 'pyproject.toml', 'run_mcp.py',
              'Installer_TCA_BP.ps1', 'Lancer_TCA_BP.cmd')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    target = ROOT / 'runtime' / ('code_checkout_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8])
    target.mkdir(parents=True, exist_ok=False)
    checkout = target / 'checkout'
    checkout.mkdir()
    files = [ROOT / name for name in ROOT_FILES]
    for name in DIRECTORIES:
        files.extend(p for p in (ROOT / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'))
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in files}
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Lien ou source hors du projet refusé.')
        output = checkout / path.relative_to(ROOT)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(path.read_bytes())
    if any(sha(checkout / name) != value or sha(ROOT / name) != value for name, value in before.items()):
        raise ValueError('Le code a changé pendant sa copie : recette non lancée.')
    env = os.environ.copy()
    for name in ('PYTHONPATH', 'TCA_TEST_MODEL_DIR'):
        env.pop(name, None)
    env['PYTHONNOUSERSITE'] = '1'
    env['PYTHONUTF8'] = '1'
    witness = subprocess.run([sys.executable, '-c',
        'import pathlib,tca_bp;assert pathlib.Path(tca_bp.__file__).resolve().parent == pathlib.Path.cwd()/"tca_bp";print(tca_bp.__version__)'],
        cwd=checkout, env=env, capture_output=True, text=True, encoding='utf8', check=True)
    report = {'schema': 'tca-bp-code-checkout-validation/1', 'status': 'EN_COURS',
              'python': sys.version, 'checkout': str(checkout), 'source_files': before,
              'version': witness.stdout.strip(), 'original_documents_included': False,
              'model_included': False, 'native_excel_executed': False}
    receipt = target / 'validation.json'
    def save():
        receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    save()
    for label, args in (('tests', ['-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                        ('gui', ['-m', 'tca_bp.gui', '--smoke'])):
        print('Code isolé : ' + label, flush=True)
        log = target / (label + '.txt')
        with log.open('w', encoding='utf8') as stream:
            process = subprocess.run([sys.executable, '-X', 'utf8', *args], cwd=checkout, env=env,
                                     stdout=stream, stderr=subprocess.STDOUT, timeout=900)
        output = log.read_text(encoding='utf8')
        ran = re.search(r'Ran (\d+) tests? in ([\d.]+)s', output)
        skips = re.search(r'skipped=(\d+)', output)
        report[label] = {'exit_code': process.returncode, 'log': str(log), 'sha256': sha(log),
                         'tests_run': int(ran[1]) if ran else None,
                         'skipped': int(skips[1]) if skips else 0}
        save()
        if process.returncode:
            report['status'] = 'ECHEC'
            save()
            print(json.dumps({'status': report['status'], 'receipt': str(receipt), 'step': label}), flush=True)
            return False
    changed = [name for name, value in before.items() if sha(ROOT / name) != value]
    report['source_files_changed_during_tests'] = changed
    report['status'] = 'SUCCES_COPIE_FIGEE'
    save()
    print(json.dumps({'status': report['status'], 'receipt': str(receipt), 'tests': report['tests'],
                      'code_changed_since_snapshot': changed}), flush=True)
    return True


if __name__ == '__main__':
    raise SystemExit(0 if run() else 2)
