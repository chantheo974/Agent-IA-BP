"""Build a separate local web pack; preserve the earlier Windows archive."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path,PurePosixPath
import posixpath
import re
import sys
import tempfile
from urllib.parse import urlsplit,unquote
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import package_app as base
from tca_bp import __version__
from tca_bp.storage import now
from tca_bp.initial_model import CONFIG as INITIAL_CONFIG, ARCHIVES as INITIAL_ARCHIVES, configured_pin, initial_engine
from tca_bp.model_registry import ModelRegistry, REQUIRED as MODEL_REQUIRED, OPTIONAL as MODEL_OPTIONAL, model_pin
from tca_bp.model_components import read_component

MANIFEST='WEB_PACKAGE_MANIFEST.json'
COPIED_ASSET_NOTICES={'frontend/dist/icone/LICENSE-ICONOIR.txt','frontend/dist/icone/SOURCE.md'}
ROOT={'Lancer_TCA_BP_Web.cmd','Installer_TCA_BP_Web.ps1','docs/ATELIER_WEB.md','docs/RECETTE_WEB.md',
      'docs/SUIVI_AUDITS_0.4.0.md','docs/RECETTE_BLOCS_METIER_0.4.0.md','docs/AUDIT_NOMENCLATURE_PCG_2026-09-13.md',
      'docs/RECETTE_WACC_CALENDRIER_0.4.0.md','docs/RECETTE_REALISE_0.4.0.md',
      'tools/install_ocr.py','tca_bp/resources/pcg_reference_20260913.json','docs/INTEGRATION_COCKPIT.md',
      'docs/RECETTE_COCKPIT_0.5.0.md','docs/RECETTE_COCKPIT_DEMO_2026-09-18.md'}
WEB_CODE=frozenset('tca_bp/'+name for name in (
    'web_server.py','web_workspace.py','web_jobs.py','web_settings.py','web_chat.py',
    'web_cells.py','web_charts.py','web_lock.py','web_validation.py','web_model.py','web_model_profile.py',
    'web_structure.py','web_structure_worker.ps1',
    'decision_api.py','decision_workspace.py','decision_model.py','decision_finance.py','decision_documents.py','decision_reports.py',
    'cockpit_api.py','cockpit_workspace.py','cockpit_simulations.py',
    'decision_actuals.py','decision_reforecast.py','decision_reforecast_bridge.py','decision_exports.py','decision_accounting.py','decision_offers.py','formula_bindings.py','web_blocks.py','wacc_fingerprint_migration.py','dcf_calendar_migration.py','fiscal_calendar_migration.py'))
WEB_REQUIRED=WEB_CODE|ROOT|base.CLIENT_CODE|base.ROOT_FILES|base.VENDOR_REQUIRED|{
    'frontend/dist/index.html','frontend/THIRD_PARTY_NOTICES.txt',
    '00_LIRE_AVANT_UTILISATION.txt',base.NOTICE,'.vscode/mcp.json'}|{
    base.MODEL_PREFIX+name for name in base.MODEL_FILES}|{
    f'agents/agent_{i:02d}.json' for i in range(1,34)}
WINDOWS_RESERVED={'con','prn','aux','nul',*(f'com{i}' for i in range(1,10)),*(f'lpt{i}' for i in range(1,10))}


def initial_allowed(name):
    if name == INITIAL_CONFIG:
        return True
    parts=PurePosixPath(name).parts
    if len(parts)!=4 or '/'.join(parts[:2])!=INITIAL_ARCHIVES or not re.fullmatch('[0-9a-f]{64}',parts[2]):
        return False
    names=MODEL_REQUIRED|MODEL_OPTIONAL
    return parts[3] in names|{'seal.json'}|{n+'.gz' for n in names if n.endswith('.json')}


def _check_initial_json(raw,name):
    # Decode JSON escapes before looking for private provenance. Hash validity
    # alone does not imply that a legitimately sealed archive is distributable.
    decoded=json.dumps(json.loads(raw),ensure_ascii=False)
    if base.PERSONAL_PATH.search(decoded.encode('utf-8')) or base.private_fragment_found(decoded):
        raise ValueError('Provenance non portable ou fragment privé dans le modèle initial : '+name)


def _initial_content(root):
    """Return exactly the sealed initial variant, with its portable provenance."""
    # TEMP may use a Windows short name or a junction. Compare descendants
    # against the same canonical root as configured_pin/initial_engine; keep
    # _regular_file's checks on internal links and escaping files unchanged.
    root=Path(root).resolve()
    pin=configured_pin(root)
    if pin is None:
        return {},None
    config_raw=base._regular_file(root,Path(root)/INITIAL_CONFIG)
    _check_initial_json(config_raw,INITIAL_CONFIG)
    engine=initial_engine(root)
    registry=ModelRegistry(Path(root)/INITIAL_ARCHIVES,root)
    seal=registry.verify(pin)
    if model_pin(registry.describe(engine))!=pin:
        raise ValueError('Le modèle initial a changé durant la préparation.')
    directory=engine.model_dir
    files={INITIAL_CONFIG:config_raw}
    for path in directory.iterdir():
        name=path.relative_to(root).as_posix()
        if not initial_allowed(name):raise ValueError('Composant initial non autorisé.')
        files[name]=base._regular_file(root,path)
        if path.name=='seal.json':_check_initial_json(files[name],name)
    for name in seal['files']:
        raw=read_component(directory/name)
        if name.endswith('.json'):
            _check_initial_json(raw,name)
        elif name==base.TEMPLATE:
            base._check_content({base.MODEL_PREFIX+base.TEMPLATE:raw})
    return files,pin


def _verify_initial(files):
    members={name:raw for name,raw in files.items() if initial_allowed(name)}
    if not members:return None
    if INITIAL_CONFIG not in members:raise ValueError('Sélection du modèle initial absente.')
    with tempfile.TemporaryDirectory(prefix='tca-initial-verification-') as temp:
        root=Path(temp)
        for name,raw in members.items():
            path=root/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)
        verified,pin=_initial_content(root)
        if verified!=members:raise ValueError('Des composants initiaux ne sont pas couverts par la sélection.')
        return pin


def allowed(name):
    p=PurePosixPath(name)
    if (not name or name!=p.as_posix() or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name
            or any(ord(char)<32 for char in name)
            or any(part.rstrip(' .')!=part for part in p.parts)
            or any(part.split('.')[0].casefold() in WINDOWS_RESERVED for part in p.parts)
            or any(part.casefold() in base.FORBIDDEN or part.startswith('.env') for part in p.parts)):
        return False
    return (name in ROOT|COPIED_ASSET_NOTICES|{MANIFEST,'00_LIRE_AVANT_UTILISATION.txt','frontend/THIRD_PARTY_NOTICES.txt'}
            or initial_allowed(name)
            or base.allowed_name(name)
            or name in WEB_CODE
            or name.startswith('frontend/dist/') and p.suffix in ('.html','.js','.css','.svg','.woff','.woff2','.png'))


def _check_web_content(files):
    missing=WEB_REQUIRED-files.keys()
    if missing:
        raise ValueError('Composant web requis absent : '+', '.join(sorted(missing)))
    if 'frontend/dist/icone/iconoir-sprite.svg' in files and not COPIED_ASSET_NOTICES <= files.keys():
        raise ValueError('La licence et la provenance Iconoir doivent accompagner les icônes.')
    base._check_content(files)
    for name,raw in files.items():
        if PurePosixPath(name).suffix in ('.js','.css','.html','.svg','.ps1','.cmd'):
            if base.PERSONAL_PATH.search(raw) or base.private_fragment_found(raw.decode('utf-8-sig')):
                raise ValueError('Un fragment privé ou chemin personnel subsiste dans un composant web : '+name)
    # Check the production entry and literal Vite lazy imports. This is an
    # asset-closure check, not a claim to parse arbitrary JavaScript programs.
    for name,raw in files.items():
        if not name.startswith('frontend/dist/') or not name.endswith(('.html','.js','.css')):
            continue
        text=raw.decode('utf-8-sig');refs=[]
        if name.endswith('.html'):
            refs+=re.findall(r'\b(?:src|href)\s*=\s*[\"\']([^\"\']+)',text,re.I)
        if name.endswith('.js'):
            refs+=re.findall(r'\bimport\s*\(\s*[\"\']([^\"\']+)',text)
        if name.endswith('.css'):
            refs+=re.findall(r'url\(\s*[\"\']?([^\"\')\s]+)',text)
        for ref in refs:
            parsed=urlsplit(ref)
            if parsed.scheme or parsed.netloc or not parsed.path:continue
            target=unquote(parsed.path)
            target=posixpath.normpath('frontend/dist/'+target.lstrip('/')) if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
            if target not in files:
                raise ValueError('Ressource compilée manquante : '+target)


def collect(root):
    root=Path(root).resolve()
    files,receipt=base.collect_files(root)
    initial_files,_=_initial_content(root)
    files.update(initial_files)
    for name in ROOT:
        files[name]=base._regular_file(root,root/name)
    for name in WEB_CODE:
        files[name]=base._regular_file(root,root/name)
    frontend=root/'frontend'/'dist'
    if not (frontend/'index.html').is_file():
        raise ValueError('Compiler l’interface web avant de préparer le pack.')
    for path in frontend.rglob('*'):
        if path.is_file():
            name=path.relative_to(root).as_posix()
            if not allowed(name):
                raise ValueError('Artefact web non prévu : '+name)
            files[name]=base._regular_file(root,path)
    notices=[]
    modules=root/'frontend'/'node_modules'
    if not modules.is_dir():
        raise ValueError('Dépendances frontend absentes : leurs licences sont requises pour distribuer le build.')
    for path in sorted(modules.glob('**/package.json')):
        if any(part in ('test','tests','fixtures','examples') for part in path.relative_to(modules).parts):
            continue
        try:
            package=json.loads(base._regular_file(root,path))
        except (ValueError,OSError):
            continue
        licenses=[x for x in path.parent.iterdir() if x.is_file() and x.name.lower().startswith(('license','licence','copying'))]
        if licenses and package.get('name'):
            notices.append(f"{package['name']} {package.get('version','')}\n"+'\n'.join(base._regular_file(root,x).decode('utf-8',errors='replace') for x in licenses))
    if not notices:
        raise ValueError('Les notices des dépendances frontend sont absentes.')
    files['frontend/THIRD_PARTY_NOTICES.txt']='\n\n'.join(notices).encode('utf-8')
    files['README.md']=base._client_readme(files['docs/ATELIER_WEB.md'],source_document='docs/ATELIER_WEB.md')
    files['00_LIRE_AVANT_UTILISATION.txt']=('TCA BP WEB - ATELIER EXCEL LOCAL\n\n'
        '1. Extraire tout le ZIP dans un dossier local.\n'
        '2. Installer Python 3.14 et disposer de Microsoft Excel.\n'
        '3. Exécuter Installer_TCA_BP_Web.ps1 (connexion Internet pour les dépendances Python).\n'
        '4. Ouvrir Lancer_TCA_BP_Web.cmd : l’atelier s’ouvre dans le navigateur.\n'
        '5. Enregistrer la clé API dans Réglages pour connecter le chat.\n\n'
        'L’interface est déjà compilée : Node n’est pas requis à l’utilisation.\n'
        'Les fichiers restent locaux ; les extraits du chat sont envoyés au fournisseur configuré.\n'
        'Les saisies sont préparées en brouillon puis appliquées après aperçu.\n'
        'Lire README.md pour les versions, la reprise, le recalcul et les limites.\n').encode('utf-8')
    files[base.NOTICE]=files['00_LIRE_AVANT_UTILISATION.txt']
    if not all(allowed(name) for name in files):
        raise ValueError('Le pack contient un fichier non autorisé.')
    _check_web_content(files)
    return files,receipt


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if archive.testzip() or len(names)!=len(set(names)) or len(names)!=len({n.casefold() for n in names}) or not all(allowed(n) for n in names):
            raise ValueError('Archive web invalide.')
        if any(info.is_dir() or ((info.external_attr>>16)&0o170000) not in (0,0o100000) for info in archive.infolist()):
            raise ValueError('Le pack ne peut contenir que des fichiers ordinaires, jamais des liens.')
        manifest=json.loads(archive.read(MANIFEST))
        if manifest.get('schema')!='tca-bp-web-package/1':
            raise ValueError('Manifeste web incompatible.')
        expected={x['path'] for x in manifest['files']}
        if expected != set(names)-{MANIFEST} or len(expected)!=len(manifest['files']):
            raise ValueError('Le manifeste ne couvre pas le pack entier.')
        for item in manifest['files']:
            raw=archive.read(item['path'])
            if len(raw)!=item['size'] or base.digest(raw)!=item['sha256']:
                raise ValueError('Empreinte de fichier incorrecte.')
        files={n:archive.read(n) for n in expected}
        _check_web_content(files)
        base._validate_model(files)
        initial_pin=_verify_initial(files)
        if manifest.get('initial_model')!=initial_pin:
            raise ValueError('Le manifeste décrit un autre modèle initial.')
        return {'status':'VERIFIE','files':len(expected),'package_sha256':base.digest(Path(path).read_bytes()),'distribution':'WEB_LOCAL'}


def build(root,output):
    root=Path(root).resolve()
    output=base._output_path(root,output)
    files,receipt=collect(root)
    initial_pin=configured_pin(root)
    manifest={'schema':'tca-bp-web-package/1','version':__version__,'created_at':now(),'model_id':receipt['model_id'],
              'initial_model':initial_pin,
              'template_sha256':receipt['template_sha256'],'python_required':'>=3.14','node_required_at_runtime':False,
              'files':[{'path':name,'size':len(raw),'sha256':base.digest(raw)} for name,raw in sorted(files.items())]}
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.web-pack-',suffix='.zip',dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for name,raw in sorted(files.items()):
                archive.writestr(name,raw)
            archive.writestr(MANIFEST,base.json_bytes(manifest))
        result=verify(temp)
        os.link(temp,output)
        return {**result,'path':str(output)}
    finally:
        Path(temp).unlink(missing_ok=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output',type=Path)
    group.add_argument('--verify',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.verify) if args.verify else build(Path(__file__).resolve().parents[1],args.output),ensure_ascii=False,indent=2))
