"""Capture repeatable validation output without PowerShell stderr conversion."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid


def source_manifest(root):
    """Identify the implementation and tests actually present during this run."""
    paths = [root / 'pyproject.toml']
    for directory in ('tca_bp', 'tests'):
        paths.extend(path for path in (root / directory).rglob('*')
                     if path.is_file() and path.suffix in {'.py', '.ps1', '.json'}
                     and '__pycache__' not in path.parts)
    files = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(set(paths))}
    serialized = json.dumps(files, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return {'sha256': hashlib.sha256(serialized).hexdigest(), 'files': files}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    folder=root/'runtime'/('validation_web_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir(parents=True)
    command=[sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-v']
    if not args.all:command+=['-p','test_web*.py']
    start=dt.datetime.now(dt.timezone.utc)
    before=source_manifest(root)
    (folder/'sources_before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
    print(str(folder),flush=True)
    with (folder/'tests.txt').open('wb') as output:
        result=subprocess.run(command,cwd=root,stdout=output,stderr=subprocess.STDOUT)
    after=source_manifest(root)
    (folder/'sources_after.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
    changed=sorted(name for name in before['files'].keys() | after['files'].keys()
                   if before['files'].get(name)!=after['files'].get(name))
    receipt={'status':'FAIL' if result.returncode else 'SOURCES_CHANGED' if changed else 'PASS','exit_code':result.returncode,
             'started_at':start.isoformat(),'finished_at':dt.datetime.now(dt.timezone.utc).isoformat(),
             'scope':'FULL' if args.all else 'WEB','log_sha256':hashlib.sha256((folder/'tests.txt').read_bytes()).hexdigest(),
             'source_sha256_before':before['sha256'],'source_sha256_after':after['sha256'],
             'source_files_count':len(before['files']),'changed_source_files':changed,
             'covers':['tests Python unittest'],
             'not_covered':['parcours navigateur Playwright (npm test dans frontend)',
                            'construction et vérification du pack web (tools/package_web.py)',
                            'calculs Excel natifs (tools/validate_web_native.py)',
                            'connexion au fournisseur IA réel'],
             'notice':"Ce reçu atteste l'exécution des tests Python seulement ; il ne vaut pas recette de livraison."}
    (folder/'validation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({**receipt,'folder':str(folder)},indent=2))
    return result.returncode or (2 if changed else 0)


if __name__=='__main__':raise SystemExit(main())
