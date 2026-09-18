"""Prepare a portable initial archive after the exact native recipe succeeds.

Only Excel's local absPath metadata is removed. No financial formula/input or
existing dossier is changed; no initial-model configuration is selected here.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tca_bp.storage import atomic_json,digest
from tca_bp.vendor.input_engine import Workbook
from tca_bp.web_model import ProfileEngine,seal_profile_model
from tca_bp.web_model_profile import seal_profile
from tca_bp.web_structure import _formula_key,vba_preservation
from tca_bp.model_registry import ModelRegistry,model_pin
from tools.package_app import PERSONAL_PATH


def same_financial_contents(left_path,right_path):
    left,right=Workbook(left_path),Workbook(right_path)
    try:
        if list(left.sheets)!=list(right.sheets):raise ValueError('Les feuilles ont changé.')
        for sheet in left.sheets:
            for cell in set(left.sheet(sheet)[1])|set(right.sheet(sheet)[1]):
                a,b=left.formula(sheet,cell),right.formula(sheet,cell)
                if _formula_key(a)!=_formula_key(b):raise ValueError('Une formule a changé pendant la portabilisation.')
                if a is None and b is None and left.value(sheet,cell)!=right.value(sheet,cell):
                    raise ValueError('Une valeur a changé pendant la portabilisation.')
            left._sheet_cache.pop(sheet,None);right._sheet_cache.pop(sheet,None)
        vba=vba_preservation(left.z.read('xl/vbaProject.bin'),right.z.read('xl/vbaProject.bin'))
        if not vba['preserved']:raise ValueError('Les composants VBA ont changé.')
        return {'all_formulas_equal':True,'all_literals_equal':True,'same_sheets':True,'vba':vba}
    finally:left.close();right.close()


def run(recipe_folder, *, output_name='initial_web_model_0.4.0'):
    recipe_folder=Path(recipe_folder).resolve()
    if recipe_folder.parent!=ROOT/'runtime' or not recipe_folder.name.startswith('recette_calendrier_fiscal_'):
        raise ValueError('Répertoire de recette identifié requis.')
    report=json.loads((recipe_folder/'validation.json').read_text(encoding='utf-8'))
    diff=json.loads((recipe_folder/'original_model_diff.json').read_text(encoding='utf-8'))
    scan=json.loads((recipe_folder/'portable_model_scan.json').read_text(encoding='utf-8'))
    if (report.get('status')!='SUCCES' or not all(report.get('checks',{}).values())
            or len(report.get('oracles',[]))!=8 or len(report.get('fiscal_cash_oracles',[]))!=15):
        raise ValueError('Recette native complète avec 23 oracles requise.')
    if (diff.get('formula_change_count')!=71 or diff.get('exact_71_formulas') is not True
            or diff.get('literal_changes')!=[{'sheet':'Valorisation','cell':'D141','old_value':'NON_EXECUTE','new_value':None}]):
        raise ValueError('Différence au modèle original non conforme aux 71 corrections et à l’invalidation native.')
    if any(any(value.values()) for value in scan.get('json',{}).values()):
        raise ValueError('Un JSON du modèle contient encore une donnée privée ou un chemin personnel.')
    if scan.get('xlsm')!={'xl/workbook.xml':{'personal_path':True,'private_fragment':False}}:
        raise ValueError('Le diagnostic de portabilité XLSM diffère du seul absPath attendu.')
    engine=ProfileEngine(ROOT,recipe_folder/'model');engine.ensure_built()
    if digest(engine.template_path)!=diff['candidate_sha256']:raise ValueError('Le modèle candidat a changé.')
    if not isinstance(output_name,str) or re.fullmatch(r'initial_web_model_[A-Za-z0-9_.-]+',output_name) is None:
        raise ValueError('Un nom de préparation borné sous runtime est requis.')
    output=ROOT/'runtime'/output_name
    output.mkdir(exist_ok=False)
    portable=output/'portable.xlsm';removed=0
    with zipfile.ZipFile(engine.template_path) as source,zipfile.ZipFile(portable,'w') as target:
        for info in source.infolist():
            raw=source.read(info.filename)
            if info.filename=='xl/workbook.xml':
                tree=ET.fromstring(raw)
                nodes=list(tree.iter('{http://schemas.microsoft.com/office/spreadsheetml/2010/11/ac}absPath'))
                if len(nodes)!=1 or set(nodes[0].attrib)!={'url'} or not PERSONAL_PATH.search(nodes[0].get('url','').encode()):
                    raise ValueError('Métadonnée locale Excel différente du seul absPath attendu.')
                raw,removed=re.subn(rb'<(?:[A-Za-z_]\w*:)?absPath\b[^>]*?/>',b'',raw)
                if removed!=1:raise ValueError('Suppression de métadonnée non bornée.')
                ET.fromstring(raw)
            target.writestr(info,raw)
    equivalence=same_financial_contents(engine.template_path,portable)
    profile=engine.profile
    profile=seal_profile({**profile,'parent_profile_sha256':profile['profile_sha256'],
                         'current_workbook_sha256':digest(portable)})
    built=seal_profile_model(engine,portable,profile,output/'model')
    # A profile build normally already omits paths. Drop any future build-path
    # field on this new unarchived copy, and reject paths in other metadata.
    receipt_path=output/'model'/'build_receipt.json'
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    for key,value in list(receipt.items()):
        if isinstance(value,str) and PERSONAL_PATH.search(value.encode()):
            if not key.endswith('_path'):raise ValueError('Chemin privé hors des métadonnées de construction.')
            del receipt[key]
    atomic_json(receipt_path,receipt)
    for path in (output/'model').glob('*.json'):
        if PERSONAL_PATH.search(path.read_bytes()):raise ValueError('Chemin personnel dans le modèle portable.')
    with zipfile.ZipFile(portable) as z:
        for name in z.namelist():
            if name.endswith(('.xml','.rels','.vml')) and PERSONAL_PATH.search(z.read(name)):
                raise ValueError('Chemin personnel XML subsistant.')
    standalone=ProfileEngine(ROOT,output/'model');standalone.ensure_built()
    registry=ModelRegistry(ROOT/'models'/'web-initial',ROOT)
    pin=model_pin(registry.register(standalone));registry.verify(pin)
    archived=registry.resolve(pin);archived.ensure_built()
    proof={'schema':'tca-initial-web-model-preparation/1','status':'PREPARED_NOT_SELECTED',
           'pin':pin,'original_sha256':diff['original_sha256'],'tested_model_sha256':diff['candidate_sha256'],
           'portable_sha256':digest(portable),'removed_abs_path_nodes':removed,'equivalence':equivalence,
           'native_recipe_sha256':digest(recipe_folder/'validation.json'),
           'original_diff_sha256':digest(recipe_folder/'original_model_diff.json'),
           'financial_formula_changes':71,'fictitious_business_inputs_in_model':False,
           'dossier_qualification_transfer':False,'native_calculation_proof_transfer':False,
           'self_contained_archive':True,'native_recipe_applies_to_financial_formulas_only':True}
    atomic_json(output/'validation.json',proof)
    atomic_json(output/'initial-web.json',{'schema':'tca-bp-initial-model/1',**pin})
    print(json.dumps({'status':proof['status'],'pin':pin,'report':str(output/'validation.json')},ensure_ascii=False),flush=True)
    return proof


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('recipe_folder',type=Path)
    parser.add_argument('--output-name',default='initial_web_model_0.4.0')
    args=parser.parse_args();run(args.recipe_folder,output_name=args.output_name)
