"""Own one isolated local server for the real cockpit browser recipe."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--read-only-case', help='Copie fictive calculée de la recette native 24 kEUR ; aucune écriture navigateur.')
parser.add_argument('--data-dir', type=Path, help='Répertoire de la recette native, requis avec --read-only-case.')
args = parser.parse_args()
if bool(args.read_only_case) != bool(args.data_dir):
    parser.error('--read-only-case et --data-dir doivent être fournis ensemble.')
if args.data_dir and not (args.data_dir / 'tca_bp.sqlite3').is_file():
    parser.error('Le répertoire de la recette calculée ne contient pas sa base SQLite.')
read_only = bool(args.read_only_case)
test_file = 'tests/live-cockpit-outputs.spec.ts' if read_only else 'tests/live-cockpit.spec.ts'
expected_status = 'PASS_REAL_CALCULATED_COCKPIT_READ_ONLY' if read_only else 'PASS_REAL_COCKPIT_SOURCE_AND_DRAFT'
run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
folder = root / 'runtime' / (('live_cockpit_outputs_' if read_only else 'live_cockpit_ui_') + run_id)
folder.mkdir(exist_ok=False)
port = 8794 if read_only else 8791
data_dir = args.data_dir.resolve() if args.data_dir else folder / 'data'
with socket.socket() as probe:
    if probe.connect_ex(('127.0.0.1', port)) == 0:
        raise RuntimeError('Le port de recette est occupé ; aucun serveur existant ne sera arrêté.')

def hashes():
    paths = list((root / 'frontend' / 'dist').rglob('*'))
    paths += list((root / 'frontend' / 'src').rglob('*'))
    paths += list((root / 'frontend').glob('*.json'))
    paths += list((root / 'frontend').glob('*config.ts'))
    paths += list((root / 'tca_bp').glob('*.py'))
    return {str(path.relative_to(root)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.is_file()}

before = hashes()
receipt = {'status': 'RUNNING', 'run_id': run_id, 'port': port, 'data_dir': str(data_dir), 'read_only_browser': read_only, 'sources_and_build_before': before}
server = None
try:
    with (folder / 'server.log').open('wb') as server_log:
        server = subprocess.Popen([sys.executable, '-X', 'utf8', '-B', '-m', 'tca_bp.web_server', '--no-browser', '--port', str(port), '--data-dir', str(data_dir)], cwd=root, stdout=server_log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        receipt['server_pid'] = server.pid
        deadline = time.monotonic() + 90
        while True:
            if server.poll() is not None:
                raise RuntimeError('Le serveur de recette a quitté pendant le démarrage.')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/cases', timeout=3) as response:
                    if response.status == 200: break
            except Exception:
                if time.monotonic() >= deadline: raise
                time.sleep(0.4)
        env = dict(os.environ, TCA_WEB_LIVE_URL=f'http://127.0.0.1:{port}', TCA_WEB_LIVE_RUN_ID='cockpit-' + run_id)
        if read_only: env['TCA_COCKPIT_NATIVE_CASE'] = args.read_only_case
        node = shutil.which('node')
        if not node: raise RuntimeError('Node requis pour la recette de développement.')
        command = [node, str(root / 'frontend/node_modules/playwright/cli.js'), 'test', test_file, '--config', 'playwright.live.config.ts']
        print(json.dumps({'event': 'recipe_started', 'folder': str(folder), 'server_pid': server.pid}), flush=True)
        result = subprocess.run(command, cwd=root / 'frontend', env=env, timeout=300, capture_output=True)
        (folder / 'playwright.log').write_bytes(result.stdout + result.stderr)
        receipt['browser_exit_code'] = result.returncode
        artifacts = root / 'frontend' / 'test-results' / ('live-cockpit-' + run_id)
        if artifacts.exists(): shutil.copytree(artifacts, folder / 'browser')
        found = list((folder / 'browser').rglob('receipt.json'))
        receipt['browser_receipts'] = [str(path.relative_to(folder)) for path in found]
        receipt['sources_and_build_after'] = hashes()
        receipt['sources_and_build_unchanged'] = before == receipt['sources_and_build_after']
        if result.returncode:
            print((result.stdout + result.stderr).decode('utf-8', errors='replace')[-12000:], flush=True)
            raise RuntimeError('La recette navigateur réelle n’a pas réussi.')
        if len(found) != 1: raise RuntimeError('Reçu du navigateur absent ou ambigu.')
        inner = json.loads(found[0].read_text(encoding='utf-8'))
        if inner['status'] != expected_status: raise RuntimeError('Statut de recette inattendu.')
        if not receipt['sources_and_build_unchanged']: raise RuntimeError('Les sources ou le build ont changé pendant la recette.')
        receipt['status'] = expected_status
except Exception as exc:
    receipt['status'] = 'FAILED'
    receipt['error'] = str(exc)
    raise
finally:
    if server is not None:
        server.terminate()
        try: server.wait(timeout=15)
        except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=10)
        receipt['owned_server_stopped'] = server.poll() is not None
    (folder / 'validation.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'status': receipt['status'], 'receipt': str(folder / 'validation.json'), 'owned_server_stopped': receipt.get('owned_server_stopped')}, ensure_ascii=False), flush=True)
