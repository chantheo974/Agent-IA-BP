"""Préparer un dossier fictif qualifié sur une version exactement désignée.

Aucun appel COM, aucun recalcul et aucune adoption de version par date. Les
sources sont des conventions mathématiques de recette, jamais des règles de
droit ou des hypothèses proposées à un client réel.
"""
from __future__ import annotations

import datetime as dt
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tca_bp.calculation_operations import _preflight
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.storage import atomic_json, digest, uid
from tools.financial_cases_common import common_updates, merge_updates
from tools.financial_cases_wacc import cases

EXPECTED_RELEASE_SHA = '3ce93e17fdad0f9a41f1c1830fb1f8c64aff0291b04ef772362c81f7883d47b9'


def prepare(model_dir: Path | None = None, expected_sha256: str | None = None) -> dict:
    if model_dir is None:
        model_dir = ROOT / 'models' / 'generic-v1-release'
        expected_sha256 = expected_sha256 or EXPECTED_RELEASE_SHA
    elif expected_sha256 is None:
        raise ValueError('Une version explicitement sélectionnée exige son empreinte attendue.')
    model_dir = model_dir.resolve()
    if len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ValueError('Empreinte SHA-256 attendue invalide.')
    from tca_bp.web_model import ProfileEngine
    engine_class = ProfileEngine if (model_dir / 'web_profile.json').is_file() else ModelEngine
    engine = engine_class(ROOT, model_dir)
    if digest(engine.template_path) != expected_sha256:
        raise ValueError('La recette attend la version finale explicitement désignée ; aucun modèle choisi implicitement.')
    case = cases()[0]
    folder = ROOT / 'runtime' / ('recette_qualifications_service_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uid()[:6])
    if folder.exists():
        raise ValueError('La recette doit créer un nouvel espace.')
    app = Application(ROOT, folder, engine=engine)
    case_id = 'test_qualifications_wacc'
    app.create_case('Organisation exclusivement fictive de recette', 'Qualifications, WACC et DCF fictifs', case_id=case_id)
    prefix = ('RECETTE LOGICIELLE ENTIÈREMENT FICTIVE. CONFIRME signifie que la valeur est fixée dans ce jeu de test, '
              'pas qu’un client réel ou un professionnel a validé un taux légal. Aucune pièce client, source de marché réelle, '
              'conclusion fiscale ni recommandation d’investissement. ')
    documents = {
        'business': prefix + '\n'.join(case['events'][:2]) + '\n'
            'Calendrier2026–2028. Une offre active, aucune commande dans le registre : ventes prévisionnelles uniquement. '
            'Les objectifs sont1 200unités chaqueannée, les prix100EUR, les coûts matière40EUR/unité. '
            'Capacité0 signifie dans ce modèle absence de plafond industriel pour cette offre. '
            'Règlements clients et fournisseurs immédiats ; aucun acompte, aucun jalon. '
            'Aucun stock, créance, dettefournisseur, acompte, produit à recevoir ou matériel installé à l’ouverture. '
            'Aucune trésorerie à l’ouverture, aucune indexation de prix/coûts/inflation. '
            'Central est le scénario retenu et les chocs additionnels sont neutres. '
            'Aucun salarié, aucun CAPEX, aucune dette, aucune subvention d’investissement. '
            'Un financement SERIE A de100000EUR est injecté au1janvier2026, sans partR&D ni décalage de closing.',
        'fiscal': prefix + 'Convention purement mathématique : IS, CIR, C3S, CFE et TVA nuls afin d’isoler les flux. '
            'Aucune exonération réelle revendiquée. Capital/détention non admissibles au taux réduit ; aucune exonération '
            'de taxe additionnelle CVAE, mais CA120000 inférieur au seuil fictif1000000. '
            'Aucun loyer, valeur locative, autre CAde groupe, solde fiscal antérieur, dépenseR&D ou aideR&D. '
            'Taux fiscaux du scénario explicitement0, remboursementCIR sansobjet au mois1. '
            'TVAmensuelle sansremboursement ; versementmois+1, remboursementthéorique+3mois ; '
            'seuils760 et150 fixés comme données de cette recette, sans prétention juridique. '
            'La qualification Confirmé de TVA décrit seulement cette convention de test, du01/01/2026au31/12/2028.',
        'charges': prefix + 'Les13 natures de charges externes du modèle sont exclues de ce cas simplifié. '
            'Pour chaque ligne32à44 : basefixe, coûtparETP, coûtparunité, quotedeCA, partdesimmobilisationsbrutes '
            'etpartdesstocks sont explicitement0. Aucun de ces0n’est déduit d’une absence de réponse ; ils constituent '
            'la définition du scénario sansfraisexternes. La matérialité économique de cette société fictive n’est pas évaluée.',
        'valuation': prefix + '\n'.join(case['events'][2:]) + '\n'
            'Le comparable fictif a un bêta1,2, une capitalisation1000000, aucune dette et un tauxIS0. '
            'Ses observations sont mensuelles sur3ans, date01/01/2026. Le tauxsansrisque est3%, la prime5%, '
            'le coûtdedette0 et toutes primes additionnelles0. MéthodeTaux, aucun haircutde flux ni DLOM, '
            'aucune décote multiple de taille. Le WACC théorique indépendant vaut0,03+1,2×0,05=0,09. '
            'Le BFR terminal est nul dans ce cas à règlementsimmédiats, sansstock ni soldeouverture ; '
            'sa normalisation reste à contrôler par BFR!E49 aprèscalcul. Le moduleDCF est actif, sa croissance terminale2%.',
    }
    sources = {name: app.add_source(case_id, text=text, title='Convention fictive : ' + name)['id'] for name, text in documents.items()}
    expenses = [{'sheet': 'Charges_Externes', 'cell': f'{column}{row}', 'value': 0}
                for row in range(32, 45) for column in ('E', 'F', 'G', 'H', 'K', 'L')]
    neutral_shocks = [{'sheet': 'Sensi Analyses', 'cell': f'F{row}', 'value': 0} for row in range(8, 17)]
    values = merge_updates(common_updates(3, '2026-01-01'), case['updates'], expenses, neutral_shocks)
    updates = []
    for update in values:
        sheet, cell = update['sheet'], update['cell']
        fiscal_parameter = sheet == 'Assumptions' and cell.startswith('D') and cell[1:].isdigit() and (68 <= int(cell[1:]) <= 88 or cell == 'D93')
        source = 'fiscal' if sheet == 'ATELIER_CIR_IS' or fiscal_parameter else 'valuation' if sheet in ('Valorisation', 'Comparables') else 'charges' if sheet == 'Charges_Externes' else 'business'
        updates.append({**update, 'status': 'NON_RENSEIGNE' if update['value'] is None else 'CONFIRME',
                        'evidence': sources[source], 'reason': 'Valeur explicitement fixée dans la convention fictive ' + source,
                        'replace_existing': True, 'override_default': True})
    atomic_json(folder / 'fixture_updates.json', {'model_sha256': expected_sha256, 'updates': updates, 'sources': sources})
    print('Préparation du lot fictif complet : ' + str(len(updates)) + ' valeurs', flush=True)
    plan = app.prepare_changes(case_id, updates, 'qualification_fixture_v1')
    applied = app.apply_plan(case_id, plan['id'])
    for module in ('CA', 'COGS', 'DATA Financement', 'STOCK', 'CIR', 'DATA Contrats', 'Effectifs', 'DATA CAPEX', 'Financement Dette', 'SUBVENTION_INVEST', 'BFR_TERMINAL', 'REGLES_FISCALES'):
        state = 'ACTIF' if module in ('CA', 'COGS', 'DATA Financement', 'BFR_TERMINAL', 'REGLES_FISCALES') else 'INACTIF'
        source = 'fiscal' if module in ('CIR', 'REGLES_FISCALES') else 'valuation' if module == 'BFR_TERMINAL' else 'business'
        declaration = {'module': module, 'state': state, 'status': 'CONFIRME', 'evidence': sources[source],
                       'reason': 'Décision explicite de la recette fictive : ' + module + ' ' + state + '. Aucune qualification réelle.'}
        if module == 'REGLES_FISCALES':
            declaration.update(jurisdiction='Convention mathématique fictive — aucun droit fiscal réel revendiqué',
                               valid_from='2026-01-01', valid_to='2028-12-31')
        app.declare_qualification(case_id, declaration)
    assessment = app.qualifications(case_id)
    atomic_json(folder / 'qualification_avant_natif.json', assessment)
    issues = {name: scope['blockers'] + scope['hypotheses'] for name, scope in assessment['scopes'].items()}
    expected_only = all(not issues[name] for name in ('CA', 'COGS', 'CASH', 'FISCALITE')) and [item['code'] for item in issues['DCF']] == ['WACC_NON_VERIFIE']
    oracles = list(case['oracles']) + [
        {'id': 'wacc_mathematique', 'sheet': 'Valorisation', 'cell': 'D7', 'expected': case['wacc_expected'], 'tolerance': 1e-8, 'reason': '3% + bêta1,2 × prime5%, dette et primes supplémentairesnulles.'},
        {'id': 'DCF_flux_independants', 'sheet': 'Valorisation', 'cell': 'D40', 'expected': case['equity_expected'], 'tolerance': 0.02, 'reason': '3flux72000EUR actualisésà9% + terminal72000×1,02/(9%-2%), àclosing01/01/2026.'},
    ]
    result = {'schema': 'tca-bp-qualified-fixture/1', 'status': 'PRET_AVANT_WACC_NATIF' if expected_only else 'QUALIFICATION_A_COMPLETER',
              'runtime_dir': str(folder), 'case_id': case_id, 'model_dir': str(model_dir), 'model_sha256': expected_sha256,
              'source_sha256': applied['output_sha256'], 'native_executed': False, 'sources': sources,
              'case_revision': app.get_case(case_id)['revision'], 'updates_count': len(updates), 'issues': issues, 'oracles_after_wacc': oracles,
              'next_operation': 'Application(..., engine=ProfileEngine(root, model_dir) if web_profile.json exists else ModelEngine(root, model_dir)).solve_wacc(case_id)',
              'note': 'Recette fictive privée. Aucun résultat disponible avant preuve native ; aucune publication ni modification des originaux.'}
    atomic_json(folder / 'preparation.json', result)
    if expected_only:
        _preflight(assessment, 'wacc')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', type=Path, help='Version scellée exacte ; aucune recherche de version récente.')
    parser.add_argument('--expected-sha256', help='Empreinte attendue obligatoire avec --model-dir.')
    args = parser.parse_args()
    if args.model_dir is not None and args.expected_sha256 is None:
        parser.error('--expected-sha256 est obligatoire avec --model-dir')
    prepare(args.model_dir, args.expected_sha256)
