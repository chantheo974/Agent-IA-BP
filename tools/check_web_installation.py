from pathlib import Path
import hashlib, json, re, sys, time, uuid, zipfile, shutil, subprocess
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlsplit, unquote
from importlib.metadata import version
import tca_bp

import argparse
parser_args=argparse.ArgumentParser()
parser_args.add_argument('--installation',required=True)
parser_args.add_argument('--archive',required=True)
parser_args.add_argument('--archive-sha256',required=True)
parser_args.add_argument('--base-url',default='http://127.0.0.1:8788')
args=parser_args.parse_args()
root=Path(args.installation).resolve()
archive=Path(args.archive).resolve()
assert hashlib.sha256(archive.read_bytes()).hexdigest()==args.archive_sha256.lower()

receipt_dir = root / 'recette-installation'
base=args.base_url.rstrip('/')
assert urlsplit(base).hostname=='127.0.0.1' and urlsplit(base).scheme=='http'
manifest = json.loads((root / 'WEB_PACKAGE_MANIFEST.json').read_text(encoding='utf-8-sig'))
pin_keys=('model_id','model_ref','template_sha256','schema_sha256')
initial_pin=manifest.get('initial_model')
assert isinstance(initial_pin,dict) and set(initial_pin)==set(pin_keys) and all(initial_pin.values()), 'Le pack final doit déclarer le modèle initial complet.'
initial_config=json.loads((root/'models/initial-web.json').read_text(encoding='utf-8-sig'))
assert initial_config['schema']=='tca-bp-initial-model/1'
assert {key:initial_config.get(key) for key in pin_keys}==initial_pin
initial_archive=(root/'models/web-initial'/initial_pin['model_ref']).resolve()
assert initial_archive.is_relative_to(root/'models/web-initial') and initial_archive.is_dir()
expected_files={item['path'] for item in manifest['files']}
assert len(expected_files)==len(manifest['files'])
with zipfile.ZipFile(archive) as package:
    names=package.namelist()
    assert len(names)==len(set(names))==len({name.casefold() for name in names})
    assert set(names)==expected_files|{'WEB_PACKAGE_MANIFEST.json'}, 'Le manifeste doit couvrir exactement tous les fichiers du ZIP.'
    assert package.read('WEB_PACKAGE_MANIFEST.json')==(root/'WEB_PACKAGE_MANIFEST.json').read_bytes()
    archive_entries=len(names)
log=[]
def http(path, method='GET', body=None):
    req=Request(base+path, data=None if body is None else json.dumps(body).encode(), method=method, headers={'Content-Type':'application/json'})
    with urlopen(req, timeout=90) as r:
        raw=r.read(); log.append({'method':method,'path':path,'status':r.status,'bytes':len(raw)})
        return raw, dict(r.headers)
def api(path, method='GET', body=None): return json.loads(http(path,method,body)[0])
def sha(data): return hashlib.sha256(data).hexdigest()
started=datetime.now(timezone.utc).isoformat()
assert Path(tca_bp.__file__).resolve().is_relative_to(root), 'Le package importé ne vient pas du dossier extrait.'
assert Path(sys.executable).resolve().is_relative_to(root/'.venv'), 'Le serveur doit utiliser son environnement extrait.'
files=[]
for item in manifest['files']:
    path=(root/item['path']).resolve(); assert path.is_relative_to(root)
    raw=path.read_bytes(); assert len(raw)==item['size'] and sha(raw)==item['sha256'], item['path']
    files.append(item['path'])
generic_template=root/'models/generic-v1/TCA_BP_Trame_generique.xlsm'
generic_template_sha256=sha(generic_template.read_bytes())
assert generic_template_sha256==manifest['template_sha256']
assert initial_pin['template_sha256']!=generic_template_sha256, 'Le modèle initial corrigé doit rester distinct de generic-v1.'
health=api('/api/health')
assert health['version']==manifest['version']==tca_bp.__version__==version('tca-bp')
html=http('/')[0].decode(); pending=[urljoin(base+'/', ref) for ref in re.findall(r'(?:src|href)="([^"]+)"',html)]
assets=[]; seen=set()
while pending:
    url=pending.pop()
    if url in seen: continue
    seen.add(url); parsed=urlsplit(url)
    assert parsed.netloc==urlsplit(base).netloc and parsed.scheme=='http', 'Ressource externe inattendue.'
    content,headers=http(parsed.path)
    local=(root/'frontend'/'dist'/unquote(parsed.path).lstrip('/')).resolve()
    assert local.is_relative_to(root/'frontend'/'dist') and local.is_file()
    assert sha(content)==sha(local.read_bytes()), parsed.path
    assets.append({'path':parsed.path,'sha256':sha(content),'bytes':len(content)})
    if parsed.path.endswith('.js'):
        pending += [urljoin(url, ref) for ref in re.findall(r'\bimport\(\s*["\']([^"\']+)["\']',content.decode())]
assert any('/assets/index-' in a['path'] and a['path'].endswith('.js') for a in assets)
case=api('/api/cases','POST',{'client_name':'Entreprise fictive installation du pack','name':'Recette du pack final '+datetime.now().strftime('%H%M%S')})
case_id=case.get('id') or case['case']['id']
profile={'name':'Entreprise fictive','activity':'services','start_year':2026,'years':2,'business_model':'services','activity_start_month':4,'objectives':'Vérifier installation et profil uniquement.'}
result=api('/api/cases/'+case_id+'/profile','PUT',{'expected_revision':0,'request_id':'install_'+uuid.uuid4().hex,'profile':profile})
saved=api('/api/cases/'+case_id+'/profile')
assert saved['profile']['years']==2 and saved['profile']['activity_start_month']==4
current=api('/api/cases/'+case_id)
assert current['revision']==0
case_pin={key:current.get(key) for key in pin_keys}
assert case_pin==initial_pin, 'Le nouveau dossier doit utiliser le modèle initial exact déclaré dans le pack.'
sheets=api('/api/cases/'+case_id+'/sheets')
assert len(sheets['sheets'])==33
agents=api('/api/cases/'+case_id+'/agents')
assert len(agents['agents'])==33
jobs=api('/api/cases/'+case_id+'/jobs')
assert not jobs['jobs'], 'Aucun travail Excel ou IA ne doit avoir été lancé.'
node=shutil.which('node')
assert node, 'Node sert uniquement au vérificateur navigateur de développement ; le pack n’en dépend pas.'
navigation_script=Path(__file__).with_name('verify_installed_cockpit.cjs')
navigation_run=subprocess.run([node,str(navigation_script),base,case_id,str(receipt_dir)],capture_output=True)
(receipt_dir/'navigation-browser.log').write_bytes(navigation_run.stdout+navigation_run.stderr)
assert navigation_run.returncode==0, 'La navigation réelle des six espaces a échoué ; voir navigation-browser.log.'
navigation=json.loads((receipt_dir/'navigation-cockpit.json').read_text(encoding='utf-8'))
assert navigation['status']=='PASS' and [space['label'] for space in navigation['spaces']]==['Entreprise','Documents','Prévisionnel','Scénarios','Réalisé','Livrables']
parser=json.loads((receipt_dir/'powershell-parser.json').read_text(encoding='utf-8-sig'))
assert len(parser)==6 and all(not s['errors'] for s in parser)
install_log=(receipt_dir/'install.log').read_bytes()
# Windows PowerShell writes its own messages with the console code page while
# Python emits UTF-8. Verify the ASCII marker without assuming one log encoding.
assert b'INSTALLER_COMPLETED_WITHOUT_NPM' in install_log
ocr_start=install_log.index(b'{\r\n  "status":')
ocr_end=install_log.index(b'\r\n}\r\n',ocr_start)+4
ocr=json.loads(install_log[ocr_start:ocr_end].decode('utf-8'))
assert ocr['status']=='READY' and set(ocr['languages'])=={'fra','eng'}
assert len(ocr['files'])==3 and all(item['matches'] for item in ocr['files'])
(receipt_dir/'ocr-installation.json').write_text(json.dumps(ocr,ensure_ascii=False,indent=2),encoding='utf-8')
assert not (receipt_dir/'npm-attempted.txt').exists()
receipt={'status':'PASS','scope':'INSTALLATION_PACK_SANS_EXCEL_SANS_IA','archive':archive.name,'archive_sha256':args.archive_sha256.lower(),'manifest_files_verified':len(files),'archive_entries':archive_entries,'manifest_covers_archive_exactly':True,'initial_model':initial_pin,'created_case_pin':case_pin,'generic_v1_template_sha256':generic_template_sha256,'initial_model_distinct_from_generic_v1':True,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'installation':str(root),'python':sys.version,'executable':sys.executable,'imported_package':tca_bp.__file__,'version':tca_bp.__version__,'installer_exit_code':0,'powershell_scripts_parsed':len(parser),'npm_called':False,'compiled_assets_verified':assets,'health':health,'case_id':case_id,'profile':saved['profile'],'sheets':len(sheets['sheets']),'agents':len(agents['agents']),'financial_revision':current['revision'],'jobs_created':0,'logs':log,'limits':['Ce reçu valide uniquement le contenu installé et le lancement local ; les recettes financières sont séparées.','Aucun calcul financier Excel exécuté.','Aucun fournisseur IA contacté.','OCR déjà installé sous le compte Windows : contrôle des composants réutilisés, sans preuve de téléchargement sur un poste vierge.']}
receipt['limits'][-1]=('OCR existant vérifié par empreintes ; aucun nouveau téléchargement.' if ocr['already_installed'] else 'OCR installé sous le compte Windows courant, exécutable et modèles français/anglais vérifiés par empreintes ; aucun document scanné traité par cette recette.')
receipt['ocr_installation']=ocr
receipt['guided_spaces_opened']=[space['label'] for space in navigation['spaces']]
receipt['browser_navigation_receipt']='navigation-cockpit.json'
(receipt_dir/'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(receipt_dir/'http-checks.log').write_text('\n'.join(json.dumps(line,ensure_ascii=False) for line in log),encoding='utf-8')
print(json.dumps({'status':receipt['status'],'receipt':str(receipt_dir/'validation.json'),'case_id':case_id,'version':receipt['version'],'files':len(files),'assets':len(assets),'npm_called':False},ensure_ascii=False,indent=2))
