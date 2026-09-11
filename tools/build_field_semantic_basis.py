"""Figer les preuves du catalogue complémentaire après relecture TCA.

Outil interne : ne se lance jamais à l'import ni dans le pack client. Il ne
modifie ni le classeur, ni son manifeste, ni ses données. La version explicite
ci-dessous constitue la référence de la revue sémantique 1.0.0.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tca_bp.field_semantics_data import DEFINITIONS, VERSION
from tca_bp.model_build import formula_references
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core


def shape(schema, field):
    cells = schema.get('cells', {}).get(field['sheet'], {})
    return {key: field.get(key) for key in ('id','sheet','kind','cells','choices','constraints')} | {
        'defaults': {address: cells.get(address, {}).get('default_formula')
                     for address in field.get('cells', [])}}


def main():
    folder = ROOT / 'models/generic-v1-release-1.1.2'
    receipt = json.loads((folder / 'build_receipt.json').read_text(encoding='utf-8'))
    expected = 'e4c1c5fd256359f52a18e3b68b958058e1295b4bb6b1a0a97abc9e2b815b2c12'
    if receipt['template_sha256'] != expected or digest(folder/'TCA_BP_Trame_generique.xlsm') != expected:
        raise ValueError('La référence relue de cette version sémantique a changé.')
    schema = json.loads((folder/'modele.json').read_text(encoding='utf-8'))
    if digest(folder/'modele.json') != receipt['schema_sha256']:
        raise ValueError('Schéma de référence modifié.')
    fields = schema['fields']
    if set(DEFINITIONS) != {f['id'] for f in fields} or len(fields) != 297:
        raise ValueError('Chaque identifiant doit avoir exactement une définition revue.')
    anchors = sorted({a for d in DEFINITIONS.values() for a in d['anchors']})
    workbook = core.Workbook(folder/'TCA_BP_Trame_generique.xlsm')
    try:
        witnesses = {}
        for anchor in anchors:
            sheet, address = anchor.rsplit('!',1)
            formula = workbook.formula(sheet,address)
            witnesses[anchor] = {'formula': formula, 'value': workbook.value(sheet,address) if formula is None else None}
        entries = {}
        for field in fields:
            owners = {}
            for address in field['cells']:
                spec = schema['cells'][field['sheet']][address]
                formula = spec.get('default_formula')
                if formula is not None:
                    owners[address] = {'formula': formula, 'references': formula_references(formula, field['sheet']),
                                       'dynamic_or_named_references_require_review': any(t in formula.upper() for t in ('INDIRECT(', 'OFFSET('))}
            entries[field['id']] = {'shape_sha256':core.sha(canonical(shape(schema,field)).encode()),
                                    'source_label':field['label'], 'default_sources': owners}
    finally:
        workbook.close()
    basis = {'version':VERSION, 'template_sha256':expected, 'schema_sha256':receipt['schema_sha256'],
             'fields':entries, 'witnesses':witnesses,
             'limits':['Semantic contract, not confirmation of a client value or statutory rule.',
                       'Formula witnesses concern dimensions and bases; local calendar rewrites outside witnesses do not invalidate the catalogue.',
                       'Dynamic references require explicit review; the extracted dependency graph remains a separate sealed artifact.']}
    text = '"""Preuves générées de la revue sémantique ; outil interne : tools/build_field_semantic_basis.py."""\nimport json\n\nBASIS = json.loads(r\'\'\'' + json.dumps(basis,ensure_ascii=False,indent=2) + '\'\'\')\n'
    output = ROOT/'tca_bp/_field_semantics_basis.py'
    output.write_text(text,encoding='utf-8')
    print(json.dumps({'fields':len(entries),'witnesses':len(witnesses),'default_cells':sum(len(e['default_sources']) for e in entries.values()),'output':str(output)},ensure_ascii=False))


if __name__ == '__main__':
    main()
