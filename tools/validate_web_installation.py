"""Extract, install and inspect the final pack in a fresh directory with spaces.

Development recipe only: no Excel work, no provider call, no npm. The browser
verifier uses the existing development Playwright installation. Only the server
created by this recipe is stopped, and all installation files are retained.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import socket
import stat
import subprocess
import time
from urllib.request import urlopen
import uuid
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--archive-sha256', required=True)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    archive = Path(args.archive).resolve(strict=True)
    expected = args.archive_sha256.lower()
    assert len(expected) == 64 and all(c in '0123456789abcdef' for c in expected)
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected, 'Empreinte ZIP inattendue.'
    with socket.socket() as probe:
        assert probe.connect_ex(('127.0.0.1', 8788)) != 0, 'Le port 8788 est deja occupe ; aucun serveur existant ne sera arrete.'

    task_runtime = (repository / 'runtime').resolve(strict=True)
    target = (task_runtime / ('Installation web cockpit 050 ' + datetime.now().strftime('%Y%m%d_%H%M%S') + ' ' + uuid.uuid4().hex[:6])).resolve()
    assert target.is_relative_to(task_runtime) and target != task_runtime and not target.exists()
    target.mkdir()
    receipt = target / 'recette-installation'
    receipt.mkdir()
    print('INSTALLATION=' + str(target), flush=True)
    (task_runtime / 'final_web_installation_current.txt').write_text(str(target), encoding='utf-8')

    with zipfile.ZipFile(archive) as package:
        entries = package.infolist()
        names = [item.filename for item in entries]
        assert len(names) == len({name.casefold() for name in names}), 'Entrees ZIP dupliquees.'
        manifest = json.loads(package.read('WEB_PACKAGE_MANIFEST.json'))
        declared = [item['path'] for item in manifest['files']]
        assert len(declared) == len(set(declared))
        assert set(names) == set(declared) | {'WEB_PACKAGE_MANIFEST.json'}, 'Couverture du manifeste incomplete.'
        resolved = []
        for entry in entries:
            relative = PurePosixPath(entry.filename)
            assert not entry.is_dir() and not relative.is_absolute()
            assert '\\' not in entry.filename and ':' not in entry.filename
            assert all(part not in ('', '.', '..') for part in entry.filename.split('/'))
            file_type = stat.S_IFMT(entry.external_attr >> 16)
            assert file_type in (0, stat.S_IFREG), 'Composant ZIP non ordinaire refuse.'
            destination = (target / Path(*relative.parts)).resolve()
            assert destination.is_relative_to(target) and destination != target
            resolved.append((entry, destination))
        for entry, destination in resolved:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with package.open(entry) as source, destination.open('xb') as output:
                shutil.copyfileobj(source, output)
    print('EXTRACTION_VERIFIEE=' + str(len(names)) + ' fichiers', flush=True)
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)
    environment['PYTHONUTF8'] = '1'
    hidden = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    installer_command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(repository / 'tools/check_web_installation.ps1'), '-Target', str(target)]
    with (receipt / 'install.log').open('wb') as output:
        installed = subprocess.run(installer_command, cwd=target, env=environment, stdout=output, stderr=subprocess.STDOUT, creationflags=hidden)
    assert installed.returncode == 0, 'Installation refusee : consulter recette-installation/install.log.'
    print('INSTALLATEUR_PASS_SANS_NPM', flush=True)

    python = target / '.venv/Scripts/python.exe'
    server_command = [str(python), '-X', 'utf8', '-m', 'tca_bp.web_server', '--no-browser', '--port', '8788', '--data-dir', str(receipt / 'data')]
    start = datetime.now(timezone.utc).isoformat()
    with (receipt / 'server.log').open('wb') as server_log:
        server = subprocess.Popen(server_command, cwd=target, env=environment, stdout=server_log, stderr=subprocess.STDOUT, creationflags=hidden)
        (receipt / 'server-process.json').write_text(json.dumps({'pid': server.pid, 'started_at': start, 'command': server_command, 'cwd': str(target), 'owned_by_this_recipe': True}, ensure_ascii=False, indent=2), encoding='utf-8')
        try:
            deadline = time.monotonic() + 180
            while True:
                assert server.poll() is None, 'Le serveur extrait s est arrete au demarrage.'
                try:
                    with urlopen('http://127.0.0.1:8788/api/health', timeout=5) as response:
                        assert response.status == 200
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Le serveur extrait ne repond pas sur 8788.')
                    time.sleep(1)
            print('SERVEUR_EXTRAIT_PRET=http://127.0.0.1:8788', flush=True)
            verify = [str(python), '-X', 'utf8', str(repository / 'tools/check_web_installation.py'), '--installation', str(target), '--archive', str(archive), '--archive-sha256', expected, '--base-url', 'http://127.0.0.1:8788']
            with (receipt / 'verification.log').open('wb') as output:
                result = subprocess.run(verify, cwd=target, env=environment, stdout=output, stderr=subprocess.STDOUT, creationflags=hidden)
            assert result.returncode == 0, 'Verification refusee : consulter recette-installation/verification.log.'
            print('VALIDATION_PASS=' + str(receipt / 'validation.json'), flush=True)
        finally:
            if server.poll() is None:
                server.terminate()
                try:
                    server.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=10)
            (receipt / 'server-stopped.json').write_text(json.dumps({'pid': server.pid, 'stopped_at': datetime.now(timezone.utc).isoformat(), 'exit_code': server.returncode, 'only_owned_process_stopped': True, 'financial_jobs_executed': False}, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
