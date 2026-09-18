"""Analyse de développement : composants à revoir, sans droit d'écriture.

La propagation interfeuille est volontairement conservatrice. Les références
littérales sont localisées ; INDIRECT/OFFSET, VBA et objets exigent une recette.
"""
from __future__ import annotations
from .model_components import component_path, component_exists, read_component

import hashlib
import json
from pathlib import Path
import re

from .model_build import formula_references
from .model_registry import ModelRegistry
from .vendor import input_engine as core


def _dynamic_functions(formula):
    # Les chaînes Excel et les noms de feuilles cités ne sont pas des appels.
    expression = re.sub(r'"(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'', '', formula or '')
    return sorted({name.upper() for name in re.findall(
        r'(?<![\w.])(?:_xlfn\.)?(INDIRECT|OFFSET)\s*\(', expression, re.I)})


def _reference(value):
    match = re.fullmatch(r"'((?:[^']|'')+)'!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?", value)
    if not match:
        return None
    sheet, first, row, last, end = match.groups()
    _, c1, r1 = core.coord(first + row)
    _, c2, r2 = core.coord((last or first) + (end or row))
    return sheet.replace("''", "'"), min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2)


def _contains(reference, sheet, cell):
    parsed = _reference(reference)
    if parsed is None or parsed[0] != sheet:
        return False
    _, col, row = core.coord(cell)
    return parsed[1] <= col <= parsed[3] and parsed[2] <= row <= parsed[4]


def impact_report(engine, changes):
    """Lier l'impact à une copie exacte et distinguer observation et estimation."""
    folder = Path(engine.model_dir)
    registry = ModelRegistry(folder, engine.project_root)
    source = registry.describe(engine)  # Lecture seule : aucune archive créée.
    binding = {'model_id': source['model_id'], 'model_ref': source['model_ref'],
               'source_template_sha256': source['template_sha256'],
               'source_schema_sha256': source['schema_sha256'],
               'source_kind': source['kind'], 'graph_derivation_verified': False}
    graph_path = folder / 'graphe_dependances.json'
    if not component_exists(graph_path):
        return {'schema': 'tca-bp-maintenance-impact/1', 'status': 'GRAPHE_ABSENT',
                **binding, 'graph_sha256': None,
                'coverage_complete': False, 'limits': ['Impact non déterminé sans graphe de cette version.']}
    payload = read_component(graph_path)
    graph_sha = hashlib.sha256(payload).hexdigest()
    if source['files'].get('graphe_dependances.json', graph_sha) != graph_sha:
        raise ValueError("Le graphe a changé pendant l'analyse d'impact.")
    graph = json.loads(payload)
    if graph.get('model_id') != engine.model_id:
        raise ValueError('Le graphe de maintenance appartient à une autre version.')
    edges = graph.get('sheets')
    if not isinstance(edges, dict) or any(not isinstance(v, list) for v in edges.values()):
        raise ValueError('Graphe de maintenance invalide.')
    targets = {(c['sheet'], c['cell']) for c in changes}
    if any(sheet not in edges for sheet, _ in targets):
        raise ValueError('Une feuille modifiée manque au graphe de maintenance.')
    affected = {sheet for sheet, _ in targets}
    while True:
        expanded = affected | {s for s, sources in edges.items() if affected.intersection(sources)}
        if affected == expanded:
            break
        affected = expanded
    # Les dépendances NOUVELLES doivent être présentées même si elles n'étaient
    # pas dans le graphe d'origine. Elles n'inversent pas les arêtes aval.
    upstream = sorted({r for change in changes for r in formula_references(change['new_formula'], change['sheet'])})
    direct = []
    dynamic = set()
    proposed_dynamic = []
    for change in changes:
        functions = _dynamic_functions(change['new_formula'])
        if functions:
            dynamic.add((change['sheet'], change['cell']))
            proposed_dynamic.append({'sheet': change['sheet'], 'cell': change['cell'], 'functions': functions})
    nodes_by_sheet = {s: 0 for s in affected}
    for node in graph.get('cells', []):
        sheet, cell = node.get('sheet'), node.get('cell')
        if sheet in affected:
            nodes_by_sheet[sheet] += 1
        references = node.get('references', [])
        causes = sorted({s + '!' + c for s, c in targets
                         if any(_contains(ref, s, c) for ref in references)})
        if causes:
            direct.append({'sheet': sheet, 'cell': cell, 'depends_on': causes})
    names = []
    for name in graph.get('defined_names', []):
        refs = formula_references(name.get('text', ''), '')
        exact = [s + '!' + c for s, c in targets if any(_contains(ref, s, c) for ref in refs)]
        linked = sorted({_reference(r)[0] for r in refs if _reference(r) and _reference(r)[0] in affected})
        if exact or linked:
            names.append({'name': name.get('name'), 'localSheetId': name.get('localSheetId'),
                          'references': refs, 'direct_targets': exact, 'affected_sheets': linked})
    tables = []
    for table in graph.get('native_tables', []):
        if table.get('sheet') in affected:
            tables.append({key: table.get(key) for key in ('id', 'sheet', 'range', 'inputs', 'axes')})
    macro = graph.get('macro', {})
    wacc_affected = bool(set(macro.get('outputs', {})).intersection(affected))
    schema = getattr(engine, 'schema', {})
    inputs = schema.get('cells', {})
    key_fields = [dict(id=field['id'], sheet=field['sheet'], ranges=field.get('ranges', []))
                  for field in schema.get('fields', [])
                  if field['sheet'] in affected and any(k in field['id'] for k in ('catalog', 'offer', 'category'))]
    constants = []
    validations = []
    objects = []
    workbook = engine._open(engine.template_path)
    try:
        for sheet in sorted(affected):
            if sheet not in workbook.sheets:
                raise ValueError('Le graphe référence une feuille absente du classeur.')
            tree, cells, _ = workbook.sheet(sheet)
            for cell, node in cells.items():
                formula = workbook.formula(sheet, cell)
                if _dynamic_functions(formula):
                    dynamic.add((sheet, cell))
            for validation in tree.findall('m:dataValidations/m:dataValidation', core.N):
                validations.append({'sheet': sheet, 'range': validation.get('sqref'),
                                    'type': validation.get('type'),
                                    'formulas': [c.text for c in validation if c.tag.rsplit('}', 1)[-1] in ('formula1', 'formula2')]})
            for tag in ('drawing', 'legacyDrawing', 'legacyDrawingHF', 'oleObjects', 'controls'):
                if tree.find('m:' + tag, core.N) is not None:
                    objects.append({'sheet': sheet, 'type': tag, 'qualification': 'REVUE_DU_COMPOSANT_REQUISE'})
            workbook._sheet_cache.pop(sheet, None)
        for reference in upstream:
            parsed = _reference(reference)
            if parsed is None or parsed[0] not in workbook.sheets:
                continue
            sheet, c1, r1, c2, r2 = parsed
            # Une plage volumineuse est signalée sans parcourir des millions
            # de cellules inexistantes. La liste des constantes n'est pas une
            # autorisation de modifier ce rectangle.
            _, cells, _ = workbook.sheet(sheet)
            count = 0
            sample = []
            for cell in cells:
                _, col, row = core.coord(cell)
                if c1 <= col <= c2 and r1 <= row <= r2 and cell not in inputs.get(sheet, {}) and workbook.formula(sheet, cell) is None:
                    count += 1
                    if len(sample) < 20:
                        sample.append(cell)
            if count:
                constants.append({'reference': reference, 'protected_constant_count': count,
                                  'sample_cells': sample, 'sample_truncated': count > len(sample)})
            workbook._sheet_cache.pop(sheet, None)
    finally:
        workbook.close()
    final_source = registry.describe(engine)
    # Le modèle réel inclut le graphe dans son sceau ; un adaptateur injecté
    # conserve une empreinte séparée du graphe. Aucun des deux ne certifie sa
    # dérivation ni la résolution complète des références dynamiques.
    final_graph_sha = final_source['files'].get('graphe_dependances.json')
    if final_graph_sha is None:
        final_graph_sha = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    if source != final_source or graph_sha != final_graph_sha:
        raise ValueError("Le modèle ou le graphe a changé pendant l'analyse d'impact.")
    return {'schema': 'tca-bp-maintenance-impact/1', 'status': 'ANALYSE_STATIQUE',
            **binding, 'graph_sha256': graph_sha,
            'propagation': 'CONSERVATRICE_PAR_FEUILLE', 'coverage_complete': False,
            'affected_sheets': sorted(affected), 'formula_nodes_by_sheet': nodes_by_sheet,
            'direct_formula_dependants': direct, 'new_upstream_references': upstream,
            'defined_names': names, 'native_tables': tables,
            'wacc': {'affected': wacc_affected, 'outputs': macro.get('outputs', {}) if wacc_affected else {},
                     'native_validation_required': wacc_affected},
            'catalogue_keys_to_review': key_fields, 'protected_constants_referenced': constants,
            'validations_to_review': validations, 'objects_to_review': objects,
            'dynamic_references_to_review': [{'sheet': s, 'cell': c} for s, c in sorted(dynamic)],
            'proposed_dynamic_references_to_review': proposed_dynamic,
            'required_checks': ['Différences exactes du paquet et maintien des zones hors impact.',
                                'Oracles économiques indépendants des cellules modifiées et de leurs consommateurs.',
                                *(['Revue des références dynamiques présentes ou introduites.'] if dynamic else []),
                                *(['Preuve distincte des tables natives affectées.'] if tables else []),
                                *(['Preuve de résolution locale WACC affectée.'] if wacc_affected else [])],
            'limits': ['La propagation par feuille surestime volontairement certains impacts.',
                       'Les empreintes identifient les composants analysés ensemble ; elles ne prouvent pas la dérivation du graphe.',
                       'Les références dynamiques, objets et VBA ne sont pas prouvés par une analyse statique.',
                       'Cette analyse ne donne aucun droit de modification de structure ou de constante.']}
