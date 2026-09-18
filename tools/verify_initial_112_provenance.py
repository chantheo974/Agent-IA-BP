"""Verify the clean 1.1.2 candidate and emit preparation evidence only."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from tca_bp.storage import atomic_json,digest
from tca_bp.vendor.input_engine import Workbook
from tca_bp.web_model import ProfileEngine
from tca_bp.web_structure import _formula_key,vba_preservation
from tca_bp.wacc_fingerprint_migration import verified_fingerprint_exemptions
from tca_bp.dcf_calendar_migration import verified_calendar_exemptions
from tca_bp.fiscal_calendar_migration import verified_fiscal_calendar_exemptions
from tools.package_app import PERSONAL_PATH,private_fragment_found
from tools.rebuild_initial_from_112 import EXPECTED


def verify_native_guards_and_cash(recipe_folder, report, engine):
    from tca_bp.service import Application
    from tca_bp.vendor.input_engine import colname
    fixture=Path(report['qualified_fixture']).resolve()
    if fixture.parent!=ROOT/'runtime':raise ValueError('Dossier fictif de recette hors runtime.')
    native=json.loads((fixture/'validation_service_wacc.json').read_text(encoding='utf-8'))
    if native.get('status')!='SUCCES' or native.get('template_sha256')!=digest(engine.template_path):
        raise ValueError('La preuve native ne correspond pas au modèle contrôlé.')
    app=Application(ROOT,fixture,engine=engine)
    current=app.get_case('test_qualifications_wacc');path=Path(current['workbook_path'])
    workbook_sha=digest(path)
    if workbook_sha!=native['native_service_receipt']['output_sha256']:
        raise ValueError('La copie courante diffère de la sortie native vérifiée.')
    wb=Workbook(path);guards=[];monthly=[]
    try:
        active={67:False,68:'Taux normal',86:1,90:'Valider les loyers corporels > 6 mois et la VA fiscale'}
        inactive={67:False,68:'INACTIF_HORS_HORIZON',86:0,90:'INACTIF_HORS_HORIZON'}
        for index,col in enumerate('CDEFGHIJKLM'):
            for row in (67,68,86,90):
                expected=(active if index<3 else inactive)[row];actual=wb.value('ATELIER_CIR_IS',col+str(row))
                expected_type=(type(actual) is bool if row==67 else
                               type(actual) in (int,float) if row==86 else type(actual) is str)
                passed=actual==expected and expected_type
                guards.append({'cell':col+str(row),'actual':actual,'expected':expected,'passed':passed})
        for index in range(36):
            cell=colname(20+index)+'321';actual=wb.value('Modèle financier',cell);expected=106000+6000*index
            monthly.append({'cell':cell,'actual':actual,'expected':expected,
                            'passed':type(actual) in (int,float) and abs(actual-expected)<.01})
        alert=wb.value('KPI Dashboard','E68')
    finally:wb.close()
    result={'schema':'tca-initial-112-native-oracles/1','workbook_sha256':workbook_sha,
        'native_receipt_sha256':digest(fixture/'validation_service_wacc.json'),
        'historical_guard_oracles':guards,'monthly_cash':monthly,'cash_alert':alert,
        'all_passed':all(x['passed'] for x in guards+monthly) and alert=='Non atteint dans le plan'}
    atomic_json(recipe_folder/'additional_monthly_diagnostics.json',result)
    if not result['all_passed']:raise ValueError('Un oracle natif supplémentaire de calendrier ou trésorerie échoue.')
    return result


def run(recipe_folder):
    recipe_folder=Path(recipe_folder).resolve()
    if recipe_folder.parent!=ROOT/'runtime' or not recipe_folder.name.startswith('recette_calendrier_fiscal_'):
        raise ValueError('Répertoire de recette privée explicitement désigné requis.')
    report=json.loads((recipe_folder/'validation.json').read_text(encoding='utf-8'))
    if report.get('status')!='SUCCES' or not all(report.get('checks',{}).values()):
        raise ValueError('Recette complète réussie requise avant préparation.')
    source=ROOT/'models'/'generic-v1'/'TCA_BP_Trame_generique.xlsm'
    engine=ProfileEngine(ROOT,recipe_folder/'model');engine.ensure_built()
    if digest(source)!=EXPECTED or engine.profile['origin_template_sha256']!=EXPECTED:
        raise ValueError('La provenance doit rester exactement celle du modèle 1.1.2.')
    left,right=Workbook(source),Workbook(engine.template_path)
    changes=[];literals=[];guards=[]
    try:
        same_sheets=list(left.sheets)==list(right.sheets)
        for sheet in left.sheets:
            for cell in set(left.sheet(sheet)[1])|set(right.sheet(sheet)[1]):
                a,b=left.formula(sheet,cell),right.formula(sheet,cell)
                if _formula_key(a)!=_formula_key(b):
                    changes.append({'sheet':sheet,'cell':cell,'old_formula':a,'new_formula':b})
                if a is None and b is None and left.value(sheet,cell)!=right.value(sheet,cell):
                    literals.append({'sheet':sheet,'cell':cell,'old_value':left.value(sheet,cell),'new_value':right.value(sheet,cell)})
            if sheet=='ATELIER_CIR_IS':
                for row in (67,68,86,90):
                    for col in 'CDEFGHIJKLM':
                        cell=col+str(row)
                        guards.append({'sheet':sheet,'cell':cell,'preserved':left.formula(sheet,cell)==right.formula(sheet,cell)})
            left._sheet_cache.pop(sheet,None);right._sheet_cache.pop(sheet,None)
        certified=(verified_fingerprint_exemptions(engine.profile,right)
                   |verified_calendar_exemptions(engine.profile,right)
                   |verified_fiscal_calendar_exemptions(engine.profile,right))
        exact=len(changes)==71 and len(certified)==71 and {c['sheet']+'!'+c['cell'] for c in changes}==certified
        vba=vba_preservation(left.z.read('xl/vbaProject.bin'),right.z.read('xl/vbaProject.bin'))
    finally:left.close();right.close()
    if (not exact or not same_sheets or not all(g['preserved'] for g in guards) or not vba['preserved']
            or literals!=[{'sheet':'Valorisation','cell':'D141','old_value':'NON_EXECUTE','new_value':None}]):
        raise ValueError('La comparaison exhaustive dépasse les 71 corrections certifiées et la seule invalidation native.')
    proof={'schema':'tca-model-calendar-original-diff/1','original_sha256':EXPECTED,
        'candidate_sha256':digest(engine.template_path),'same_sheets':same_sheets,'formula_change_count':len(changes),
        'exact_71_formulas':exact,'literal_changes':literals,'vba':vba,'changes':changes,
        'origin_build_version':'1.1.2','guard_count':44,'historical_guards':guards,
        'profile_origin_sha256':engine.profile['origin_template_sha256']}
    atomic_json(recipe_folder/'original_model_diff.json',proof)
    scan={'json':{},'xlsm':{}}
    for path in (recipe_folder/'model').glob('*.json'):
        decoded=json.dumps(json.loads(path.read_text(encoding='utf-8-sig')),ensure_ascii=False)
        scan['json'][path.name]={'personal_path':bool(PERSONAL_PATH.search(decoded.encode('utf-8'))),
                                 'private_fragment':private_fragment_found(decoded)}
    with zipfile.ZipFile(engine.template_path) as z:
        for name in z.namelist():
            if name.endswith(('.xml','.rels','.vml')):
                raw=z.read(name)
                found={'personal_path':bool(PERSONAL_PATH.search(raw)),
                       'private_fragment':private_fragment_found(raw.decode('utf-8-sig'))}
                if any(found.values()):scan['xlsm'][name]=found
    atomic_json(recipe_folder/'portable_model_scan.json',scan)
    extra=verify_native_guards_and_cash(recipe_folder,report,engine)
    print(json.dumps({'same_sheets':same_sheets,'exact_71_formulas':exact,'historical_guards_preserved':44,
        'candidate_sha256':proof['candidate_sha256'],'vba':vba,'scan':scan,
        'native_guard_oracles':len(extra['historical_guard_oracles']),
        'native_monthly_oracles':len(extra['monthly_cash']),'supplement_passed':extra['all_passed']},ensure_ascii=False),flush=True)
    return proof


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('recipe_folder',type=Path)
    run(parser.parse_args().recipe_folder)
