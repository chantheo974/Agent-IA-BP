"""Catalogue sémantique contrôlé, ajouté en lecture au manifeste scellé.

Il qualifie la signification d'un champ, pas la vérité de sa valeur, son taux
légal ni son admissibilité fiscale. Une définition absente ou incompatible
interdit la proposition de ce champ ; les autres champs restent utilisables.
"""
from copy import deepcopy
import hashlib
import json
import re

from .field_semantics_data import DEFINITIONS, VERSION
from ._field_semantics_basis import BASIS


def _canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def _hash(value):
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _shape(schema, field):
    specs = schema.get('cells', {}).get(field['sheet'], {})
    return {key:field.get(key) for key in ('id','sheet','kind','cells','choices','constraints')} | {
        'defaults':{address:specs.get(address,{}).get('default_formula') for address in field.get('cells',[])}}


def applies(schema):
    """Ce catalogue porte sur la famille BP ; pas sur un modèle externe arbitraire."""
    return str(schema.get('model_id','')).startswith('tca-bp-') or any(f.get('id') in DEFINITIONS for f in schema.get('fields',[]))


def contract_digest():
    return _hash({'version':VERSION,'definitions':DEFINITIONS,'basis':BASIS})


def enrich_catalog(schema, *, workbook=None):
    """Retourner des copies enrichies, sans modifier champs/cellules du schéma.

    Les propriétaires métier sont nommés explicitement ; les références A1 des
    809 défauts sont conservées intégralement. Les dépendances aval générales
    restent interrogeables dans le graphe scellé de la même version.
    """
    result = []
    fields = schema.get('fields',[])
    ids = {f.get('id') for f in fields}
    relevant = applies(schema)
    digest = contract_digest()
    witness_state = {}
    for anchor, expected in BASIS['witnesses'].items():
        if workbook is None:
            witness_state[anchor] = False
        else:
            sheet, address = anchor.rsplit('!',1)
            try:
                formula = workbook.formula(sheet,address)
                actual = {'formula':formula,'value':workbook.value(sheet,address) if formula is None else None}
                witness_state[anchor] = actual == expected
            except (KeyError,ValueError):
                witness_state[anchor] = False
    for raw in fields:
        field = deepcopy(raw)
        ident = field.get('id')
        definition = DEFINITIONS.get(ident)
        reference = BASIS['fields'].get(ident)
        problems = []
        if not relevant:
            problems.append('CATALOGUE_METIER_HORS_PERIMETRE')
        elif definition is None or reference is None:
            problems.append('DEFINITION_NON_ETABLIE')
        else:
            if _hash(_shape(schema,field)) != reference['shape_sha256']:
                problems.append('CONTRAT_CHAMP_MODIFIE')
            if any(owner not in ids for owner in definition['dependencies']):
                problems.append('PROPRIETAIRE_ABSENT_DU_CATALOGUE')
            if any(not witness_state[a] for a in definition['anchors']):
                problems.append('PREUVE_ASSIETTE_MODIFIEE_OU_ABSENTE')
        known = definition is not None and reference is not None
        established = relevant and known and not problems
        spec = definition if known else {'unit':'NON_ETABLIE','basis':'Signification à établir par TCA.','dependencies':[],
                                         'calendar':'NON_ETABLI','note':'','anchors':[]}
        cell_specs = schema.get('cells',{}).get(field.get('sheet'),{})
        defaults = deepcopy(reference['default_sources']) if known else {}
        # Liste exacte des défauts de la carte, sans permission déduite d'une couleur.
        actual_defaults = [c for c in field.get('cells',[]) if cell_specs.get(c,{}).get('default_formula') is not None]
        register = schema.get('registers',{}).get(field.get('sheet'),{})
        required_columns = set(register.get('required',[]))
        required_cells = [c for c in field.get('cells',[]) if re.sub(r'\d','',c) in required_columns
                          or cell_specs.get(c,{}).get('allow_blank') is False]
        policy = {'write':'VALEUR_LITERAL_AUTORISEE_PAR_CARTE_SEULEMENT',
                  'blank':'NON_RENSEIGNE ; jamais converti implicitement en zéro',
                  'zero': 'VALEUR_EXPLICITE_DANS_LE_DOMAINE' if field.get('kind') in ('number','integer','percent') else 'SANS_OBJET_NUMERIQUE',
                  'inactive':'DECLARATION_DOCUMENTEE ; ne neutralise jamais une valeur positive par métadonnée',
                  'source_required':True,'formula_input':'INTERDITE',
                  'default_override':'ACCORD_EXPLICITE_ET_SOURCE;CELLULE_PRESENTE_DANS_DEFAULT_CELLS' if actual_defaults else 'AUCUN_DEFAUT_A_REMPLACER',
                  'default_cells':actual_defaults,
                  'required_cells_when_record_active':required_cells,
                  'conditional_completeness':'REGLES_CENTRALES_DU_MODELE_ET_QUALIFICATIONS_PAR_PERIMETRE',
                  'constraints':deepcopy(field.get('constraints') or {}),
                  'choices':deepcopy(field.get('choices'))}
        if ident and ident.startswith('offer_capacity_'):
            policy['zero'] = 'AUCUNE_CONTRAINTE_DE_CAPACITE ; pas production nulle'
        semantic = {'version':VERSION,'contract_sha256':digest,
                    'status':'ETABLI_MODELE' if established else 'REEXAMEN_REQUIS' if relevant else 'HORS_PERIMETRE',
                    'can_propose':established,'blocking_reasons':problems,
                    'unit':spec['unit'],'basis':spec['basis'],
                    'dependencies':{'business_owners':[{'field_id':owner,'binding':'CELLULE_OU_LIGNE_METIER_CORRESPONDANTE'} for owner in spec['dependencies']],
                                    'calculated_defaults':defaults,
                                    'downstream':{'artifact':'graphe_dependances.json','sheet':field.get('sheet'),'cells':deepcopy(field.get('cells',[])),
                                                  'direction':'CONSOMMATEURS_AVAL','dynamic_references':'REVUE_EXPLICITE_REQUISE'}},
                    'calendar':{'domain':spec['calendar'],'owners':list(CAL_OWNER for CAL_OWNER in ('model_start_date','active_horizon_years') if CAL_OWNER in spec['dependencies']),
                                'legacy_year_ids_are_offsets':bool(ident and (ident.startswith('offer_') or ident.startswith('cogs_margin_')))},
                    'policy':policy,'note':spec['note'],
                    'evidence':{'reviewed_template_sha256':BASIS['template_sha256'],'reviewed_schema_sha256':BASIS['schema_sha256'],
                                'source_label':reference['source_label'] if known else None,
                                'review_method':'DEFINITION_EXPLICITE_PAR_IDENTIFIANT;CARTE_ET_FORMULES_AUDITEES',
                                'review_author':'REVUE_TECHNIQUE_CODEX;PAS_APPROBATION_FISCALE_OU_CLIENT',
                                'proof_scope':'Contrat de champ et interprétation documentée ; témoins ciblés supplémentaires si présents. Aucun oracle financier déduit du nombre de témoins.',
                                'field_contract_matches':known and _hash(_shape(schema,field))==reference['shape_sha256'],
                                'witnesses':[{'address':anchor,'matches':witness_state[anchor],'expected':deepcopy(BASIS['witnesses'][anchor])} for anchor in spec['anchors']]},
                    'client_value_qualification':'TOUJOURS_DISTINCTE_ET_SOURCEE;AUCUNE_REGLE_FISCALE_CERTIFIEE'}
        field.update(unit=semantic['unit'],basis=semantic['basis'],semantics=semantic)
        result.append(field)
    return result


def validate_updates(catalog, updates):
    """Refuser seulement les champs BP dont la sémantique est non établie."""
    by_cell = {(f['sheet'],cell):f for f in catalog for cell in f.get('cells',[])}
    for update in updates:
        field = by_cell.get((update.get('sheet'),update.get('cell')))
        if not field:  # le moteur central conserve le refus de toute cellule hors carte
            continue
        semantic = field.get('semantics',{})
        if semantic.get('status') == 'REEXAMEN_REQUIS':
            raise ValueError('Sémantique du champ à réexaminer : '+field['id']+' — '+', '.join(semantic['blocking_reasons']))


def summary(catalog):
    states = {}
    for field in catalog:
        status = field.get('semantics',{}).get('status','NON_ETABLIE')
        states[status] = states.get(status,0)+1
    return {'version':VERSION,'contract_sha256':contract_digest(),'fields':len(catalog),'states':states,
            'all_established':bool(catalog) and states.get('ETABLI_MODELE')==len(catalog),
            'financial_or_legal_validation':False}
