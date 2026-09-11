"""Cycles de trois dossiers neufs et fictifs, sans appel Excel.

Complète le parcours du §8 : décisions nulles explicites, saisie incomplète,
activation, calendrier, scénario, reprise et refus. Ne prouve aucun résultat
financier ; les recettes natives conservent leurs reçus et périmètres distincts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tca_bp.model_engine import ModelEngine
from tca_bp.model_registry import model_pin
from tca_bp.service import Application
from tca_bp.storage import atomic_json, canonical, digest, uid
from tools.financial_cases_common import common_updates


def target_directory(root, output):
    """Aucun espace préexistant ou dossier client ne peut recevoir la recette."""
    root, output = Path(root).resolve(), Path(output).resolve()
    if (not output.is_relative_to(root / 'runtime') or output.parent != root / 'runtime'
            or not output.name.startswith('recette_cycle_') or output.exists()):
        raise ValueError('Un nouveau répertoire recette_cycle_* directement sous runtime est requis.')
    return output


def definition(key, year=2030):
    horizon = {'services': 1, 'fabrication': 10, 'recherche': 3}[key]
    start, end = f'{year}-01-01', f'{year+horizon-1}-12-31'
    if key == 'services':
        sheet, module = 'DATA Contrats', 'DATA Contrats'
        partial = {'contract_client': 'Donneur ordre fictif cycle services'}
        values = {**partial, 'contract_offer': 'Offre 01', 'contract_quantity': 1,
            'contract_unit_price': 120000, 'contract_start': start, 'contract_end': end,
            'contract_recognition': 'Etalee sur la duree', 'contract_invoicing': "Au fil de l'eau",
            'contract_status': 'Signe', 'contract_weight': 1, 'contract_deposit_rate': 0,
            'contract_milestone_rate': 0, 'contract_vat_regime': 'Exonéré / hors champ', 'contract_vat_rate': 0}
        boundary = ('DATA Contrats', 'I14')
    elif key == 'fabrication':
        sheet, module = 'DATA CAPEX', 'DATA CAPEX'
        partial = {'data_capex_b13_b72': 'Machine fictive cycle fabrication'}
        values = {**partial, 'data_capex_c13_c72': "Machines-outils et équipements d'atelier",
            'data_capex_d13_d72': 12000, 'data_capex_e13_e72': end,
            'data_capex_g13_g72': 'Non', 'data_capex_i13_i72': 'Cash'}
        for field, value in {'data_capex_f13_f72': 3, 'data_capex_h13_h72': 0,
                            'data_capex_m13_m72': 'Corporelle', 'data_capex_n13_n72': 'Non',
                            'data_capex_o13_o72': 'Non'}.items():
            values[field] = {'value': value, 'status': 'CONFIRME', 'override_default': True,
                            'reason': 'Convention explicite du cycle fictif : actif Cash amorti trois ans sans subvention ni part R&D.'}
        boundary = ('DATA CAPEX', 'E13')
    else:
        sheet, module = 'Financement Dette', 'Financement Dette'
        partial = {'financement_dette_b3_b42': 'Prêt fictif cycle recherche'}
        values = {**partial, 'financement_dette_c3_c42': 120000,
            'financement_dette_d3_d42': 0, 'financement_dette_e3_e42': 2,
            'financement_dette_f3_f42': 'Amortissement constant', 'financement_dette_h3_h42': 0,
            'financement_dette_i3_i42': end, 'financement_dette_j3_j42': 'Pret bancaire'}
        boundary = ('Financement Dette', 'I3')
    zero = common_updates(horizon, start) + [{'sheet': 'Valorisation', 'cell': 'D16', 'value': year + horizon - 1}]
    zero += [{'sheet': 'Sensi Analyses', 'cell': 'F' + str(row), 'value': 0} for row in range(8, 17)]
    offer = None if key == 'recherche' else {'price': 120000 if key == 'services' else 200,
        'manual_unit_cost': 0 if key == 'services' else 80, 'annual_capacity': 0 if key == 'services' else 1200,
        'forecast_units': 0, 'payment_delay_and_deposit': 0, 'offer_coefficient': 1,
        'active': 'Oui', 'recognition_coefficient': 1}
    return {'key': key, 'horizon': horizon, 'year': year, 'start': start, 'end': end,
            'sheet': sheet, 'module': module, 'partial': partial, 'values': values,
            'zero_values': zero, 'offer_convention': offer,
            'dialogue': {'services': 'Ajouter un contrat client', 'fabrication': 'Ajouter une immobilisation CAPEX',
                         'recherche': 'Ajouter une dette bancaire'}[key],
            'boundary': boundary, 'scenario': {'services': 'Prudent', 'fabrication': 'Dégradé', 'recherche': 'Sans subventions'}[key]}


def run(*, model_dir: Path, expected_sha256: str, output: Path | None = None, project_root=ROOT):
    root, model_dir = Path(project_root).resolve(), Path(model_dir).resolve()
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        raise ValueError('Empreinte exacte SHA-256 du modèle requise.')
    engine = ModelEngine(root, model_dir)
    receipt = engine.ensure_built()
    if receipt.get('template_sha256') != expected_sha256 or digest(engine.template_path) != expected_sha256:
        raise ValueError('Le modèle ne correspond pas à l’empreinte explicitement demandée.')
    output = output or root / 'runtime' / ('recette_cycle_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uid()[:6])
    folder = target_directory(root, output)
    report = {'schema': 'tca-workflow-lifecycle/1', 'status': 'EN_COURS',
        'created_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'model_id': receipt['model_id'],
        'model_template_sha256': expected_sha256, 'schema_sha256': receipt['schema_sha256'],
        'build_version': receipt.get('build_version'), 'native_excel_executed': False,
        'financial_results_verified': False, 'cases': [], 'checks': [],
        'scope': 'Cycles de saisie, calendrier, scénario, sources, journal, modèles et reprise sur copies neuves. Aucun résultat Excel ni montant financier calculé n’est validé ici.'}
    app = Application(root, folder, engine=engine)
    app.initialize()
    manifest = folder / 'cycle_recette.json'

    def check(name, condition, actual=None, expected=None):
        report['checks'].append({'name': name, 'passed': bool(condition), 'actual': actual, 'expected': expected})
        atomic_json(manifest, report)
        if not condition:
            raise AssertionError(name + ' : ' + repr(actual))

    def updates(case, values, label):
        return [{'sheet': sh, 'cell': cell, 'value': value, 'status': 'NON_RENSEIGNE' if value is None else 'CONFIRME',
            'evidence': case['source_id'], 'reason': 'Convention du cycle fictif : ' + label,
            'replace_existing': True, 'override_default': True} for sh, cell, value in values]

    def batch(case, values, label):
        before = app.get_case(case['id'])
        plan = app.prepare_changes(case['id'], updates(case, values, label), case['id'] + '_' + label)
        result = app.apply_plan(case['id'], plan['id'])
        after = app.get_case(case['id'])
        check(case['id'] + '_' + label + '_revision_unique', after['revision'] == before['revision'] + 1)
        case['steps'].append({'stage': label, 'revision': after['revision'], 'sha256': after['sha256'], 'plan_id': plan['id']})
        return plan, result

    def refused(case, label, action):
        before = app.get_case(case['id'])
        try:
            action()
        except ValueError as error:
            after = app.get_case(case['id'])
            unchanged = after['revision'] == before['revision'] and after['sha256'] == before['sha256'] and digest(Path(before['workbook_path'])) == before['sha256']
            check(case['id'] + '_' + label, unchanged, str(error), 'Refus explicite, version et fichier inchangés')
        else:
            check(case['id'] + '_' + label, False, 'Action acceptée à tort', 'Refus')

    def values_at(case, addresses):
        current = app.get_case(case['id'])
        wb = app.engine_for_case(case['id'])._open(Path(current['workbook_path']))
        try:
            return {sh + '!' + cell: wb.value(sh, cell) for sh, cell in addresses}
        finally:
            wb.close()

    try:
        definitions = [definition(key) for key in ('services', 'fabrication', 'recherche')]
        for spec in definitions:
            case_id = 'test_cycle_' + spec['key']
            current = app.create_case('Organisation fictive ' + spec['key'], 'Cycle fictif ' + spec['key'], case_id=case_id)
            marker = 'PIECE_EXCLUSIVEMENT_FICTIVE_' + spec['key'].upper()
            document = (marker + '\nAucun client réel. Les zéros de cette recette constituent des décisions explicites. '
                'Aucune offre active, aucun stock, salarié, investissement, financement ou aide au départ. '
                'Les prix et coûts inconnus restent absents ; aucune qualification fiscale réelle n’est affirmée. '
                'L’activité sera activée progressivement par les seules valeurs ci-dessous. Les sorties financières restent indisponibles avant un recalcul indépendant.\n'
                + json.dumps(spec, ensure_ascii=False, indent=2))
            source = app.add_source(case_id, text=document, title='Convention fictive du cycle ' + spec['key'])
            case = {'id': case_id, 'key': spec['key'], 'source_id': source['id'], 'marker': marker,
                    'initial_sha256': current['sha256'], 'model_pin': model_pin(current), 'steps': []}
            report['cases'].append(case)
            check(case_id + '_trame_exacte', current['sha256'] == expected_sha256)
        for spec, case in zip(definitions, report['cases']):
            print('Cycle fictif : ' + spec['key'] + ' — activité nulle explicite', flush=True)
            common = spec['zero_values']
            zero_plan, _ = batch(case, [(v['sheet'], v['cell'], v['value']) for v in common], 'zero_explicite')
            for module in ('CA', 'COGS', 'STOCK', 'CIR', *engine.schema['registers']):
                app.declare_qualification(case['id'], {'module': module, 'state': 'INACTIF', 'status': 'CONFIRME',
                    'evidence': case['source_id'], 'reason': 'Le périmètre est explicitement sans activité dans cette étape fictive.'})
            observed = values_at(case, [('Assumptions', 'C' + str(row)) for row in range(15, 28)] + [('Assumptions', 'F15')])
            check(case['id'] + '_zero_n_est_pas_absence', all(observed['Assumptions!C' + str(row)] == 0 for row in range(15, 28)) and observed['Assumptions!F15'] is None, observed)
            assessed = app.qualifications(case['id'])
            case['zero_qualification'] = {name: value['status'] for name, value in assessed['scopes'].items()}
            check(case['id'] + '_aucune_sortie_annoncee', all(not v['available'] for v in assessed['scopes'].values()))

            print('Cycle fictif : ' + spec['key'] + ' — registre incomplet puis activation', flush=True)
            before = app.get_case(case['id'])
            partial = app.prepare_record(case['id'], spec['sheet'], spec['partial'], case['source_id'], case['id'] + '_partiel')
            after = app.get_case(case['id'])
            check(case['id'] + '_partiel_questions_sans_ecriture', partial['status'] == 'A_COMPLETER' and bool(partial.get('questions'))
                  and after['sha256'] == before['sha256'] and after['revision'] == before['revision'],
                  {'status': partial['status'], 'questions': len(partial.get('questions', []))})
            dialogue = app.route(case['id'], spec['dialogue'])
            pending = [q for q in app.get_case(case['id'])['questions'] if q['status'] == 'OUVERTE']
            check(case['id'] + '_question_enregistree', bool(pending))
            app.answer_question(case['id'], pending[0]['id'], 'Réponse fictive explicite ; les valeurs du registre sont : ' + canonical(spec['values']))
            check(case['id'] + '_reponse_source_sans_ecriture', app.get_case(case['id'])['sha256'] == before['sha256'])
            for module in (spec['module'], *(['CA', 'COGS'] if spec['key'] != 'recherche' else [])):
                app.declare_qualification(case['id'], {'module': module, 'state': 'ACTIF', 'status': 'CONFIRME',
                    'evidence': case['source_id'], 'reason': 'Activation progressive explicitement décidée pour la recette fictive.'})
            if spec['key'] != 'recherche':
                offer_spec = spec['offer_convention']
                price, cost, capacity = offer_spec['price'], offer_spec['manual_unit_cost'], offer_spec['annual_capacity']
                offer = [('Assumptions', 'C15', 1), ('Assumptions', 'D15', 'forfait' if spec['key'] == 'services' else 'unité'),
                    ('Assumptions', 'E15', 'Oui'), ('Assumptions', 'F15', price),
                    *[('Assumptions', col + '15', 0) for col in ('K', 'L', 'M', 'U', 'V', 'W', 'X', 'Y')],
                    *[('Assumptions', col + '15', capacity) for col in ('P', 'Q', 'R')],
                    ('Assumptions', 'Z15', 1), ('DATA COGS', 'D15', 'Manuel'), ('DATA COGS', 'L15', cost)]
                batch(case, offer, 'activation_offre')
            record_values = {field: value if isinstance(value, dict) else {'value': value, 'status': 'CONFIRME'} for field, value in spec['values'].items()}
            plan = app.prepare_record(case['id'], spec['sheet'], record_values, case['source_id'], case['id'] + '_registre_complet')
            check(case['id'] + '_registre_complet_pret', plan['status'] == 'PRET_A_APPLIQUER', plan.get('questions', []))
            before = app.get_case(case['id'])
            app.apply_plan(case['id'], plan['id'])
            after = app.get_case(case['id'])
            case['steps'].append({'stage': 'registre_complet', 'revision': after['revision'], 'sha256': after['sha256'], 'plan_id': plan['id']})
            check(case['id'] + '_registre_revision_unique', after['revision'] == before['revision'] + 1)

            end_serial = (dt.date.fromisoformat(spec['end']) - dt.date(1899, 12, 30)).days
            address = spec['boundary']
            read = values_at(case, [('Control', 'C59'), ('Valorisation', 'D16'), address])
            check(case['id'] + '_borne_calendrier_persistee', read['Control!C59'] == spec['horizon']
                  and read['Valorisation!D16'] == spec['year'] + spec['horizon'] - 1 and read[address[0] + '!' + address[1]] == end_serial, read)
            for label, vals in [('horizon_zero', [('Control', 'C59', 0)]), ('horizon_onze', [('Control', 'C59', 11)]),
                                ('debut_non_janvier', [('Control', 'C10', f"{spec['year']}-02-01")]),
                                ('sortie_hors_horizon', [('Valorisation', 'D16', spec['year'] + spec['horizon'])])]:
                refused(case, label, lambda v=vals, label=label: app.prepare_changes(case['id'], updates(case, v, label)))

            print('Cycle fictif : ' + spec['key'] + ' — scénario et reprise', flush=True)
            stale = app.prepare_changes(case['id'], updates(case, [('Control', 'C13', 31)], 'plan qui deviendra périmé'))
            _, scenario = batch(case, [('Sensi TCA', 'C15', spec['scenario'])], 'scenario')
            check(case['id'] + '_scenario_persiste', values_at(case, [('Sensi TCA', 'C15')])['Sensi TCA!C15'] == spec['scenario'])
            refused(case, 'plan_perime_refuse', lambda: app.apply_plan(case['id'], stale['id']))

            # Injection délibérée dans un plan fictif neuf uniquement. Le journal
            # de création, le modèle scellé et tous les classeurs sont conservés.
            wrong = app.prepare_changes(case['id'], updates(case, [('Control', 'C13', 31)], 'mauvaise version simulée'))
            with app.store.connection() as db:
                row = db.execute('SELECT payload FROM plans WHERE id=?', (wrong['id'],)).fetchone()
                altered = json.loads(row['payload'])
                altered['template_sha256'] = '0' * 64
                db.execute('UPDATE plans SET payload=? WHERE id=?', (canonical(altered), wrong['id']))
            refused(case, 'mauvaise_version_refusee', lambda: app.apply_plan(case['id'], wrong['id']))
            case['fault_injection'] = {'plan_id': wrong['id'], 'only_changed': 'plans.payload.template_sha256', 'workbook_changed': False}
            other = next(c for c in report['cases'] if c['id'] != case['id'])
            cross = updates(case, [('Control', 'C13', 31)], 'source étrangère simulée')
            cross[0]['evidence'] = other['source_id']
            refused(case, 'source_autre_dossier_refusee', lambda: app.prepare_changes(case['id'], cross))

            before = app.get_case(case['id'])
            restarted = Application(root, folder, engine=ModelEngine(root, model_dir))
            replay = restarted.apply_plan(case['id'], zero_plan['id'])
            current = restarted.get_case(case['id'])
            check(case['id'] + '_reprise_et_rejeu_sans_doublon', replay['status'] == 'DEJA_APPLIQUE'
                  and current['revision'] == before['revision'] and current['sha256'] == before['sha256']
                  and model_pin(current) == case['model_pin'])
            check(case['id'] + '_sources_et_journal_repris', bool(current['history']) and any(s['id'] == case['source_id'] for s in current['sources']))
            check(case['id'] + '_calculs_toujours_indisponibles', current['calculation_status'] == 'A_RECALCULER' and not current['outputs_current']
                  and not any(event['kind'] in ('RECALCUL_EXCEL', 'WACC_RESOLU', 'SENSIBILITES_VERIFIEES') for event in current['history']))
            exported = Path(app.export_report(case['id']))
            text = exported.read_text(encoding='utf-8')
            check(case['id'] + '_isolation_pieces', all(other['marker'] not in text for other in report['cases'] if other['id'] != case['id']))
            case.update(final_revision=current['revision'], final_sha256=current['sha256'], workbook_path=current['workbook_path'],
                        history_events=len(current['history']), report_path=str(exported), report_sha256=digest(exported))
            atomic_json(manifest, report)
        check('trois_dossiers_isoles', len(app.list_cases()) == 3)
        check('modele_partage_une_archive', len([p for p in (folder / 'modeles').iterdir() if p.is_dir() and not p.name.startswith('.')]) == 1)
        check('trame_originale_inchangee', digest(engine.template_path) == expected_sha256)
        report.update(status='SUCCES_LOGICIEL_SANS_EXCEL', finished_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                      checks_passed=len(report['checks']), data_dir=str(folder))
        atomic_json(manifest, report)
        print(json.dumps({'status': report['status'], 'checks': len(report['checks']), 'report': str(manifest)}, ensure_ascii=False), flush=True)
        return report
    except BaseException as error:
        report.update(status='ECHEC_A_INSPECTER', error=str(error))
        atomic_json(manifest, report)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    run(model_dir=args.model_dir, expected_sha256=args.expected_sha256, output=args.output)
