"""Build a versioned generic BP from a locally supplied reference, using stdlib.

Source workbooks are never saved. Only the output directory is written. The
generated template contains no calculated financial caches; native calculation
and business qualifications are separate acceptance steps.
"""
from __future__ import annotations
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from .vendor import input_engine as core
from .privacy import PRIVATE_TOKEN_HASHES, private_fragment_found, audit_workbook_documentation

MODEL_ID = 'tca-bp-template/1'
BUILD_VERSION = '1.1.2'
NS = core.NS
N = core.N
CELL = '{'+NS+'}c'
SOURCE_SHA = 'ce6111716ad7f758128e6358567f3311118533acc64cbe6d0fa56a1d68721308'
TECHNICAL_NAMES = ('ISP_WACC_',)
# Fingerprints of redaction tokens audited in the local reference. No personal
# names or original narrative are distributed in this migration code.
REDACTED_TOKEN_HASHES = PRIVATE_TOKEN_HASHES
OUTPUTS = ('Compte de Résultat','Bilan','Flux de trésorerie','Plan de financement',
           'KPI Dashboard','Valorisation','Sensi Analyses','Sensi Graphiques')
VALUATION_GUARDS = {
    ('Valorisation','B55'): 'IF(ISNUMBER($D$7),"Pre-money DCF (taux = "&ROUND($D$7*100,2)&" %)","Pre-money DCF (taux non renseigné)")',
    ('Valorisation','D59'): 'IF(AND(ISNUMBER($D$57),ISNUMBER($D$14),$D$14>0),IF(D58>0,$D$14/D58,"Non déterminé"),"Non renseigné")',
    ('Contrôles','C121'): 'IF(AND(ISNUMBER(Valorisation!$D$57),ISNUMBER(\'Financement E&S\'!$F$7)),Valorisation!$D$57-\'Financement E&S\'!$F$7,"Non renseigné")',
    ('Contrôles','N121'): 'IF(ISNUMBER($C121),IF(ABS($C121)<=$C$7,"✓ OK","⚠ le registre et la synthèse divergent"),"Non contrôlé : références de valorisation absentes")',
}


def _vba_decompress(data):
    """Read MS-OVBA compressed source; no VBA execution or writeback."""
    if not data or data[0]!=1:raise ValueError('Not compressed VBA')
    out=bytearray();pos=1
    while pos+2<=len(data):
        header=int.from_bytes(data[pos:pos+2],'little');size=(header&0xfff)+3
        if ((header>>12)&7)!=3:raise ValueError('Invalid VBA chunk')
        end=min(pos+size,len(data));pos+=2;start=len(out)
        if not header&0x8000:
            out.extend(data[pos:end]);pos=end;continue
        while pos<end:
            flags=data[pos];pos+=1
            for bit in range(8):
                if pos>=end:break
                if flags&(1<<bit):
                    if pos+2>end:raise ValueError('Truncated VBA token')
                    token=int.from_bytes(data[pos:pos+2],'little');pos+=2
                    bits=max(4,(len(out)-start-1).bit_length());mask=0xffff>>bits
                    length=(token&mask)+3;offset=(token>>(16-bits))+1
                    if offset>len(out)-start:raise ValueError('Invalid VBA offset')
                    for _ in range(length):out.append(out[-offset])
                else:out.append(data[pos]);pos+=1
                if len(out)>2_000_000:raise ValueError('VBA source bound exceeded')
    return bytes(out)


def _audit_vba(data):
    from .vendor.vba_fingerprint import _vendor
    modules=0;source_hashes=[]
    with _vendor().OleFileIO(io.BytesIO(data)) as ole:
        for path in ole.listdir(streams=True,storages=False):
            if len(path)!=2 or path[0]!='VBA' or path[1].startswith(('_','dir')):continue
            stream=ole.openstream(path).read();found=False
            for offset,b in enumerate(stream):
                if b!=1:continue
                try:source=_vba_decompress(stream[offset:])
                except (ValueError,IndexError,OverflowError):continue
                if b'Attribute VB_Name' not in source:continue
                text=source.decode('cp1252',errors='replace');found=True;modules+=1
                # Block embedded credentials without copying or displaying them.
                if re.search(r'(?i)\b(?:password|passwd|pwd|api[_ ]?key|secret|token)\s*(?::=|=)\s*"[^"\r\n]+"',text):
                    raise ValueError('Un secret littéral est embarqué dans le VBA de référence : régénération du module requise, valeur non extraite.')
                if re.search(r'(?im)^\s*(?:(?:Public|Private)\s+)?Sub\s+(?:Workbook_Open|Auto_Open)\s*\(',text):
                    raise ValueError('Une macro automatique existe dans la référence : qualification requise avant distribution.')
                source_hashes.append(core.sha(source));break
            if not found:raise ValueError('Source VBA illisible : qualification manuelle requise avant conservation.')
    return {'modules_read':modules,'source_sha256':source_hashes,'literal_secret_detected':False,'auto_open_detected':False,'executed':False}


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def serialize_xml(root, original: bytes):
    """Retain prefix bindings referenced by markup-compatibility attributes.

    ElementTree preserves expanded element/attribute names but does not know
    that mc:Ignorable and Requires contain namespace prefixes. Dropping those
    declarations makes a well-formed XML package unreadable by Excel.
    """
    data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    declared=dict(re.findall(rb'xmlns:([A-Za-z_][\w.-]*)="([^"]+)"',original))
    start=re.search(rb'<(?!\?)[^>]+>',data)
    opening=start[0]
    additions=[]
    for prefix,uri in declared.items():
        if not re.search(rb'xmlns:'+re.escape(prefix)+rb'=',opening):
            additions.append(b' xmlns:'+prefix+b'="'+uri+b'"')
    if additions:
        ending=b'/>' if opening.endswith(b'/>') else b'>'
        opening=opening[:-len(ending)]+b''.join(additions)+ending
        data=data[:start.start()]+opening+data[start.end():]
    return data


def ranges_cells(ranges):
    for span in ranges:
        ends=span.replace('$','').split(':')
        _,c1,r1=core.coord(ends[0]);_,c2,r2=core.coord(ends[-1])
        for row in range(r1,r2+1):
            for col in range(c1,c2+1):yield core.colname(col)+str(row)


REFERENCE_RX=re.compile(r"(?<![\w.])(?:(?P<sheet>'(?:[^']|'')+'|[A-Za-z_][\w ]*)!)?(?P<range>\$?[A-Z]{1,3}\$?[1-9]\d*(?::\$?[A-Z]{1,3}\$?[1-9]\d*)?)(?![\w]|\s*\()")


def formula_references(formula, sheet):
    """Extract literal A1 ranges, including local ranges, outside string values.

    Dynamic INDIRECT/OFFSET and table expressions remain explicitly qualified
    by native testing; this is a static dependency index, not an Excel parser.
    """
    clean=re.sub(r'"(?:[^"]|"")*"','""',formula)
    result=[]
    for match in REFERENCE_RX.finditer(clean):
        span=match['range'];first=span.split(':')[0]
        try:
            _,col,row=core.coord(first)
            if col>16384 or row>1048576:continue
        except ValueError:continue
        target=match['sheet'] or sheet
        if target.startswith("'"):target=target[1:-1].replace("''", "'")
        value="'"+target.replace("'", "''")+"'!"+span
        if value not in result:result.append(value)
    return result


def native_execution_metadata(wb, schema):
    """Décrire les mécanismes réellement présents, sans les exécuter ni les certifier."""
    from .sensitivity_native import scenarios
    expected_names = {'Mode':'D107', 'Candidat':'D136', 'Calcule':'D135', 'Residual':'D137',
                      'Equity':'D40', 'ValiditeEntrees':'D138', 'Croissance':'D8',
                      'Iterations':'D142', 'DateCalcul':'D143', 'StatutCalcul':'D141',
                      'EmpreinteCourante':'D155', 'EmpreinteSauvee':'D156'}
    actual_names = {node.get('name'):node for node in wb.wb.findall('m:definedNames/m:definedName',N)
                    if node.get('name','').startswith('ISP_WACC_')}
    if set(actual_names) != {'ISP_WACC_'+name for name in expected_names}:
        raise ValueError('Les douze noms WACC doivent faire l’objet d’une migration explicite.')
    names=[]
    for short, address in expected_names.items():
        name='ISP_WACC_'+short;node=actual_names[name]
        if (node.get('localSheetId') is not None or
                (node.text or '').replace('$','').replace("'",'') != 'Valorisation!'+address):
            raise ValueError('Nom WACC déplacé ou de portée incompatible : '+name)
        names.append({'name':name,'sheet':'Valorisation','cell':address,'workbook_scoped':True})
    writes=['D136','D141','D142','D143','D156']
    if set(schema.get('native_outputs',{}).get('Valorisation',[])) != set(writes):
        raise ValueError('Le contrat des cinq sorties WACC a changé.')
    def protection(sheet, address):
        node=wb.sheet(sheet)[1][address]
        p=wb.xfs[int(node.get('s','0'))].find('m:protection',N)
        return {'locked':p is None or p.get('locked','1') not in ('0','false'),
                'has_formula':wb.formula(sheet,address) is not None,
                'business_input':address in schema.get('cells',{}).get(sheet,{})}
    write_contract={cell:protection('Valorisation',cell) for cell in writes}
    if any(item['has_formula'] or item['locked'] or item['business_input'] for item in write_contract.values()):
        raise ValueError('Sortie native WACC devenue formule, verrouillée ou entrée métier.')
    def node(sheet, address):
        formula=wb.formula(sheet,address)
        return {'sheet':sheet,'cell':address,'formula':formula,
                'references':formula_references(formula or '',sheet),
                'formula_sha256':core.sha((formula or '').encode())}
    local_cells=['D7','D8','D9','D15','D17','D34','D35','D36','D37','D38','D39','D40',
                 'D107','D108','D111','D112','D113','D114','D115','D116','D117','D118','D119',
                 'D120','D121','D122','D123','D124','D126','D127','D128','D129','D130','D131',
                 'D132','D133','D134','D135','D136','D137','D138','D139','D140','D144','D155']
    local_cells += [column+str(row) for row in (26,31,32,33) for column in 'DEFGHIJKLM']
    fingerprint_parts=[node('Valorisation',address) for address in ('J155','J156','J157','J158')]
    refs=list(dict.fromkeys(ref for fragment in fingerprint_parts for ref in fragment['references']))
    wacc={'schema':'tca-native-wacc-contract/1','executed':False,'native_validation':'NOT_EXECUTED',
          'preferred_method':'LOCAL_SCALAR_SOLVER','macros_enabled':False,'defined_names':names,
          'modes':{'Manuel':{'input':'D108','output':'D7'},
                   'Structure cible':{'leverage_input':'D124','calculated_rate':'D135','output':'D7'},
                   'Itération':{'candidate':'D136','output':'D7','mode_must_be_preselected_and_sourced':True}},
          'formula_nodes':[node('Valorisation',cell) for cell in local_cells],
          'calculation_stages':[['D136'],['D7'],['D32:M32','D36'],['D33:M33','D37'],['D34'],
                                ['D38'],['D40'],['D128'],['D129'],['D130','D133','D134'],['D131'],['D135'],['D137']],
          'cashflow_inputs':['D26:M26','D31:M31','D35'],
          'closing_boundary':{'date':'D15','cash':'D126','gross_debt':'D127','convention':'BEFORE_MONTH_OF_CLOSING'},
          'write_contract':{'sheet':'Valorisation','allowed_cells':writes,'effective_protection':write_contract,
                            'mode_write_allowed':False,'arbitrary_macro_or_cell_write_allowed':False,
                            'source_never_overwritten':True,'global_circular_iteration_allowed':False},
          'owner_preconditions':{'is_tax':'Valorisation!D9','market':['D111','D112','D113','D116'],
                                 'market_sources':['E112','E113','E116'], 'primes':['D117','D118','D119'],
                                 'risk_qualification':['D120','D121','D122','D123','D139'],
                                 'comparables':'Comparables!B117:N136','comparables_guard':'Comparables!D141',
                                 'bfr_guards':['BFR!E48','BFR!E49'],'zero_requires_explicit_owner_evidence':True},
          'solver':{'method':'LOG_GRID_AND_BISECTION','grid_intervals':80,'max_evaluations':180,
                    'max_bisections':80,'residual_tolerance':1e-10,'residual_consistency_tolerance':1e-12,
                    'domain_lower':'max(g+2e-6,-1+2e-6)','domain_upper':5,
                    'seed':.25,'seed_is_market_assumption':False,'equity_must_be_positive':True,
                    'calculated_rate_must_exceed_growth_by':1e-6,'global_uniqueness_proven':False},
          'freshness':{'current':'D155','saved':'D156','diagnostic':'D144','parts':fingerprint_parts,
                       'references':refs,'reference_count':len(refs),'format':'EXCEL_TYPE_LENGTH_VALUE',
                       'is_cryptographic_hash':False,'workbook_and_input_sha_required_by_service':True,
                       'rate_D7_alone_is_not_proof':True},
          'legacy_vba':{'module':'ISP_WACC','noninteractive_entry':'ResoudreWACC_ISP',
                        'interactive_entry_not_allowed':'CalculerWACC_ISP',
                        'legacy_function_can_change_mode':True,'execution_claimed':False}}
    wacc['literal_dependency_edges']=[{'source':ref,'target':"'Valorisation'!"+item['cell']}
                                      for item in wacc['formula_nodes'] for ref in item['references']]
    table_specs=[('tornado','D25','D25:G33',['C18'],'C25:C33','D24:G24',9),
                 ('volume','C40','C40:D45',['C8'],'B40:B45','C39:D39',6),
                 ('volume_aides','D50','D50:F52',['C14','C8'],'C50:C52 / D49:F49','C49',9)]
    tables=[]
    for name,anchor,rectangle,inputs,axes,outputs,count in table_specs:
        formula=wb.sheet('Sensi Analyses')[1][anchor].find('m:f',N)
        if formula is None or formula.get('t')!='dataTable' or formula.get('ref')!=rectangle:
            raise ValueError('Table native déplacée : '+anchor)
        instrument_guards={address:protection('Sensi Analyses',address) for address in inputs}
        if any(not item['locked'] or item['has_formula'] or item['business_input'] for item in instrument_guards.values()):
            raise ValueError('Pilote de table ouvert à la saisie ou devenu formule.')
        selected=[item for item in scenarios() if item['table']==name]
        tables.append({'id':name,'sheet':'Sensi Analyses','anchor':anchor,'range':rectangle,'inputs':inputs,
                       'native_attributes':dict(formula.attrib),'axes':axes,
                       'row_input':'C14' if name=='volume_aides' else None,
                       'column_input':inputs[-1],'scalar_output_range':outputs,
                       'scalar_output_formulas':[node('Sensi Analyses',address) for address in ranges_cells([outputs])],
                       'scenarios':selected,'scalar_count':count,'result_count':sum(len(s['targets']) for s in selected),
                       'driver_protection':instrument_guards,'native_validation':'NOT_EXECUTED'})
    sensitivity={'schema':'tca-native-sensitivity-contract/1','tables':3,'comparisons':57,'scalar_copies':24,
                 'composition_nodes':[node('Sensi Analyses','E'+str(row)) for row in range(8,17)],
                 'percentage_composition':'(1+base)*(1+shock)-1','financing_delay_composition':'ADDITIVE_MONTHS',
                 'scenario_source':'Sensi TCA!C15','horizon_source':'Control!C59','cash_minimum_source':'Sensi TCA!C32:L32',
                 'frozen_point_check_is_insufficient':'Sensi Analyses!B4',
                 'table_calculation_mode':'AUTOMATIC_WITH_TABLES','scalar_calculation_mode':'AUTO_NO_TABLE',
                 'technical_copy_writes':['C8','C14','C18'],'business_write_api_expanded':False,
                 'restoration':'ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE','absolute_tolerance_eur':.01,
                 'reject_degenerate_axes':True,'native_validation':'NOT_EXECUTED'}
    return {'wacc':wacc,'native_tables':tables,'sensitivity':sensitivity}


def refresh_dependency_graph(model_dir: Path):
    """Regenerate the static graph from the generated template, never a client."""
    folder=Path(model_dir);wb=core.Workbook(folder/'TCA_BP_Trame_generique.xlsm')
    schema=json.loads((folder/'modele.json').read_text(encoding='utf-8'))
    records=[];graph={};names=wb.wb.findall('m:definedNames/m:definedName',N)
    named={n.get('name') for n in names if n.get('name')}
    try:
        core.verify_model(wb,schema)
        for sheet in wb.sheets:
            deps=set()
            for addr,node in wb.sheet(sheet)[1].items():
                f=node.find('m:f',N)
                if f is None:continue
                formula=wb.formula(sheet,addr);refs=formula_references(formula,sheet)
                for ref in refs:
                    target=ref.split('!',1)[0][1:-1].replace("''", "'")
                    if target in wb.sheets and target!=sheet:deps.add(target)
                tokens=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9.]*\b',re.sub(r'"(?:[^"]|"")*"','',formula)))
                records.append({'sheet':sheet,'cell':addr,'formula_sha256':core.sha(formula.encode()),
                                'references':refs,'defined_names':sorted(tokens&named),'kind':f.get('t','normal')})
            graph[sheet]=sorted(deps);wb._sheet_cache.pop(sheet,None)
        existing_path=folder/'graphe_dependances.json'
        existing=json.loads(existing_path.read_text(encoding='utf-8')) if existing_path.exists() else {}
        existing.update(schema='tca-bp-dependencies/v1',model_id=schema['model_id'],sheets=graph,cells=records,
                        defined_names=[dict(n.attrib,text=n.text or '') for n in names])
        existing.update(native_execution_metadata(wb,schema))
        existing.setdefault('macro',{}).update(preserved=True,sha256=core.sha(wb.z.read('xl/vbaProject.bin')),
                                               outputs=schema['native_outputs'],executed=False,contract='wacc')
        existing['limits']=list(dict.fromkeys(existing.get('limits',[])+['Literal A1 and named references indexed; dynamic references, whole-column expressions and VBA need separate qualification']))
        temp=folder/'_graphe_building.json';dump(temp,existing);os.replace(temp,existing_path)
        return {'sheets':len(graph),'formula_nodes':len(records),'reference_edges':sum(len(r['references']) for r in records)}
    finally:wb.close()


def invalidate_caches(raw: bytes) -> bytes:
    """Remove formula values, preserving formula nodes and native table anchors."""
    def one(m):
        c=m[0]
        if re.search(rb'<f(?:\s|>)',c):
            c=re.sub(rb'<v\b[^>]*?(?:/>|>.*?</v>)',b'',c,flags=re.S)
            c=re.sub(rb'<is\b[^>]*?(?:/>|>.*?</is>)',b'',c,flags=re.S)
        return c
    return core.CELL_RX.sub(one,raw)


def invalidate_chart(raw: bytes) -> bytes:
    # Keep references, series, formatting and axis definitions. Excel repopulates
    # the caches. No source financial values remain in chart cache nodes.
    return re.sub(rb'<(?:\w+:)?(?:numCache|strCache)\b[^>]*>.*?</(?:\w+:)?(?:numCache|strCache)>',
                  b'',raw,flags=re.S)


def _source_assets(root: Path):
    sources=list((root/'exemple'/'01_Previsionnels').glob('*Pilotage_protege.xlsm'))
    archives=list((root/'exemple'/'03_Agent_de_saisie').glob('*.zip'))
    if len(sources)!=1 or len(archives)!=1:
        raise ValueError('La construction nécessite une référence locale unique et son pack de saisie dans exemple/. Aucun dossier client ne sert de référence.')
    if core.sha(sources[0].read_bytes())!=SOURCE_SHA:
        raise ValueError('La référence locale a changé : révision et migration explicites requises.')
    with zipfile.ZipFile(archives[0]) as z:
        names=[x for x in z.namelist() if x.endswith('/scripts/isp_modele_pilotage.json')]
        if len(names)!=1:raise ValueError('Manifeste de référence introuvable ou ambigu.')
        seed=json.loads(z.read(names[0]))
    if seed.get('source_sha256')!=SOURCE_SHA:
        raise ValueError('Le manifeste de référence ne correspond pas au classeur local.')
    return sources[0],seed


def _migrations(wb):
    mapping={};records=[]
    for row in range(15,28):
        number=row-14
        for col,new in [('A',f'OFFRE_{number:02d}'),('B',f'Offre {number:02d}')]:
            old=wb.value('Assumptions',f'{col}{row}')
            if isinstance(old,str) and old:
                mapping[old]=new
                records.append({'sheet':'Assumptions','cell':f'{col}{row}',
                                'old_value_sha256':core.sha(old.encode()),'new_value':new,
                                'policy':'stable_id' if col=='A' else 'display_label'})
    # These remain technical catalog options; specific equipment is generalized.
    for row in range(98,122):
        old=wb.value('Assumptions',f'B{row}')
        if old:
            new=old.replace('propulsion','technique').replace(' en vol','').replace('R&D / série','recherche / production')
            if old!=new:mapping[old]=new
    return mapping,records


def _clean_text(text,mapping):
    if not isinstance(text,str):return text
    for old,new in sorted(mapping.items(),key=lambda x:-len(x[0])):text=text.replace(old,new)
    # A legacy technical namespace is retained because the preserved macro uses
    # it. All visible company names and personal/source narrative are removed.
    text=re.sub(r'\bISP\b(?!_WACC)', 'TCA BP',text)
    text=text.replace('MAB','référentiel').replace('IOFM','guide').replace('VF livrée','référence enregistrée')
    text=re.sub(r'intercepteurs?', 'unités installées',text,flags=re.I)
    if private_fragment_found(text, REDACTED_TOKEN_HASHES) or re.search(r'stockanalysis|BCE du|calibr|05/09|09-10/09|mail client|plan de trésorerie client|30\s*%|800\s?000|1[,.]2\s*M',text,re.I):
        return 'À documenter et valider pour le dossier courant.'
    return text


def _clean_formula(formula,mapping):
    if not formula:return formula
    for old,new in sorted(mapping.items(),key=lambda x:-len(x[0])):formula=formula.replace(old,new)
    # Only quoted display text is generalized, never references or operators.
    return re.sub(r'"(?:[^"]|"")*"',lambda m:'"'+_clean_text(m[0][1:-1],mapping).replace('"','""')+'"',formula)


def _schema(seed,wb,mapping):
    schema=copy.deepcopy(seed)
    for key in ['signature','native_vba_variants','vba_comparison','source_name','forbid_tca_filename']:
        schema.pop(key,None)
    schema.update(schema='tca-bp-model/v1',model_id=MODEL_ID,build_version=BUILD_VERSION,
                  source_sha256=SOURCE_SHA,calculation_policy='NO_FINANCIAL_CACHE_BEFORE_NATIVE_AND_QUALIFICATIONS')
    for reg in schema['registers'].values():
        reg.pop('preserved_template_values',None);reg.pop('template_defaults_by_cell',None)
    # Existing field ids are stable API identifiers. Period labels become relative
    # to C10; legacy year suffixes remain aliases, not fixed calendar constraints.
    for field in schema['fields']:
        field['label']=_clean_text(field['label'],mapping)
        field['label']=re.sub(r'202[6-9]|203[0-5]',lambda m:'A'+str(int(m[0])-2025),field['label'])
        field['notes']=[_clean_text(x,mapping) for x in field.get('notes',[])]
        field['choices']=[_clean_text(x,mapping) for x in field['choices']] if field.get('choices') else None
        field['cells']=list(ranges_cells(field['ranges']))
    for sheet,cells in schema['cells'].items():
        for addr,spec in cells.items():
            spec['label']=_clean_text(spec.get('label',''),mapping)
            if spec.get('choices'):spec['choices']=[_clean_text(x,mapping) for x in spec['choices']]
            if spec.get('default_formula'):spec['default_formula']=_clean_formula(spec['default_formula'],mapping)
            spec['classification']='calculated_default' if spec.get('default_formula') else 'client_input'
            spec['initial_state']='NON_RENSEIGNE'
    horizon=schema['cells']['Control']['C59'];horizon['allow_blank']=False;horizon['max']=10
    schema['calendar']={'date_cell':'Control!C10','active_years_cell':'Control!C59',
                        'technical_years':10,'start_year':2026,'policy':'YEAR_START_INPUT',
                        'tax_rules_require_review':True}
    additions=[('model_start_date','Control',['C10'],'Date de début du modèle','date',{'allow_blank':False}),
               ('capex_catalog_years','Assumptions',['C98:C121'],"Durées proposées par le catalogue CAPEX",'number',{'min_exclusive':0}),
               ('capex_catalog_rd_share','Assumptions',['D98:D121'],'Quote-part R&D proposée par le catalogue CAPEX','number',{'min':0,'max':1}),
               ('financing_rd_default','Assumptions',['D130:D145'],'Quote-part R&D par catégorie de financement','number',{'min':0,'max':1})]
    for fid,sheet,spans,label,kind,constraints in additions:
        addresses=list(ranges_cells(spans))
        schema['fields'].append({'id':fid,'sheet':sheet,'ranges':spans,'cells':addresses,'label':label,
                                 'kind':kind,'choices':None,'notes':[], 'constraints':constraints})
        for addr in addresses:
            schema['cells'].setdefault(sheet,{})[addr]={'field_id':fid,'kind':kind,'label':label,'fill':wb.fill(sheet,addr),
                                                       'allow_blank':True,'classification':'client_assumption','initial_state':'NON_RENSEIGNE',**constraints}
    schema['native_outputs']={'Valorisation':['D136','D141','D142','D143','D156']}
    schema['native_table_outputs']={'Sensi Analyses':[]}
    for span in ['D25:G33','C40:D45','D50:F52']:
        schema['native_table_outputs']['Sensi Analyses'].extend(ranges_cells([span]))
    schema['technical_names_retained']=['ISP_WACC_*']
    return schema


def _initial_value(sheet,addr,value,schema,mapping):
    """Classify every constant; return action, replacement and rationale."""
    from .template_documentation import DOCUMENTARY_REPLACEMENTS
    if (sheet,addr) in DOCUMENTARY_REPLACEMENTS:
        return 'sanitize_documentation',DOCUMENTARY_REPLACEMENTS[(sheet,addr)],'explicit_documentary_review'
    _,col,row=core.coord(addr)
    allowed=addr in schema['cells'].get(sheet,{})
    if sheet=='Control' and addr in {'C10','C13','C24','C59'}:
        return 'technical_default',{'C10':46023,'C13':30,'C24':1,'C59':5}[addr],'calendar_or_neutral_control'
    if sheet=='Assumptions' and 15<=row<=27:
        if col==1:return 'migrate_key',f'OFFRE_{row-14:02d}','stable_offer_id'
        if col==2:return 'generic_label',f'Offre {row-14:02d}','display_label_separate_from_id'
        if col==3:return 'module_inactive',0,'explicit_inactive_offer'
        if col in (30,31):return 'remove_client_documentation',None,'source_notes'
    if sheet=='Assumptions' and ((4<=row<=7 and col in (7,8)) or (66<=row<=93 and col in (7,8,9)) or (row==126 and col in (3,7,8))):
        if (row in range(4,8) and col==7) or (row>=66 and col==8):return 'qualification_reset','NON_RENSEIGNE','qualification_not_inherited'
        if row==126 and col==3:return 'generic_label',"Trésorerie d'ouverture à renseigner depuis une source du dossier",'opening_evidence'
        return 'remove_client_documentation',None,'source_status_or_comment'
    if sheet=='Assumptions' and addr=='D89':return 'remove_legacy_assumption',None,'obsolete_tax_memo'
    if sheet=='Assumptions' and 98<=row<=121 and col==5:return 'remove_client_documentation',None,'catalog_comment'
    if sheet=='Sensi TCA' and row in range(19,24):
        if col in (4,7):return 'remove_client_baseline',None,'no_baseline_in_new_file'
        if col==2:return 'calendar_migration',None,'replace_with_calendar_formula'
    if sheet=='Sensi Analyses' and addr in schema['native_table_outputs'][sheet]:return 'remove_native_cache',None,'native_table_result'
    if sheet=='Valorisation' and addr in schema['native_outputs'][sheet]:
        return 'reset_native_state','NON_EXECUTE' if addr=='D141' else None,'macro_output_invalidated'
    if sheet=='Valorisation' and addr=='D112':return 'remove_market_formula',None,'market_source_must_be_supplied_for_each_dossier'
    if sheet=='Valorisation' and addr=='E111':
        return 'remove_client_documentation','Documenter la date de référence, les sources de marché, leurs dates de consultation et la devise propres au dossier.','no_inherited_market_verification'
    if sheet=='Valorisation' and addr=='B79':
        return 'remove_client_documentation',"La position dans le cycle du secteur et le stade de développement doivent être documentés pour le dossier courant, à la date de valorisation.",'no_inherited_sector_assessment'
    if sheet=='Valorisation' and (addr in ('D64','E64','F64') or addr in {f'C{r}' for r in range(65,70)}):
        return 'technical_sensitivity_axis',value,'illustrative_grid_only_not_central_market_assumption'
    if allowed:
        if sheet=='Sensi TCA' and addr=='C15':return 'technical_default','Central','neutral_scenario'
        if sheet in ('Sensi TCA','Sensi Analyses') and isinstance(value,(int,float)):
            return 'technical_default',0,'neutral_sensitivity_input'
        if sheet=='Comparables' and col==3 and 117<=row<=136:return 'module_inactive','Non','unselected_comparable'
        return 'clear_client_input',None,'new_dossier_requires_evidence'
    if sheet=='Comparables':
        if (25<=row<=32 or 40<=row<=64 or 72<=row<=96 or 117<=row<=136) and col>=2:
            return 'clear_comparable_record',None,'sector_and_market_data_not_generic'
        if addr in ('A1','A2','A23') or (5<=row<=9 and col==2):
            return 'generic_label',{'A1':'COMPARABLES : références propres au dossier','A2':'Documenter le panel, les dates, unités, sources et critères de proximité. Aucun panel hérité.','A23':'Indices sectoriels à renseigner et sourcer.'}.get(addr,f'Proximité {6-row+4} : critère à documenter'),'sector_neutral'
    if sheet=='Previsionnel' and addr=='A1':return 'generic_label','TCA BP : trame générique','generic_cover'
    if sheet=='Revenue' and addr=='B291':
        return 'generic_label',"Livraisons de l'offre 05",'remove_source_product_brand'
    if sheet=='DATA Contrats' and addr=='A1':
        return 'generic_label','DATA CONTRATS — registre des contrats du dossier','remove_source_company_name'
    if sheet=='DATA Contrats' and addr=='A2':
        return 'generic_label',"Documenter chaque contrat, ses quantités, son prix unitaire, ses dates et ses conditions de facturation. Les prix négociés peuvent varier d'un client à l'autre.",'remove_source_market_examples'
    clean=_clean_text(value,mapping)
    return ('sanitize_documentation' if clean!=value else 'retain_technical_constant'),clean,'structural_label_or_calculation_constant'


def _new_cell(raw,value,kind='text',formula=None):
    if formula is not None:
        opening=re.match(rb'<c\b([^>]*?)(?:/?>)',raw)
        attrs=re.sub(rb'\s+t="[^"]*"',b'',opening[1])
        escaped=formula.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        return b'<c'+attrs+b'><f>'+escaped.encode()+b'</f></c>'
    return core.xml_cell(raw,value,kind)


def _protect_inputs(raw,addresses):
    # The source already has protected sheets. New input styles are cloned below;
    # only cells explicitly added by the catalog need their style changed.
    return raw


def build_model(project_root: Path, output_dir: Path|None=None, *, force=False) -> dict:
    from .model_qualification_guards import guard_formula, remove_inherited_protection_credentials
    root=Path(project_root).resolve();out=Path(output_dir or root/'models'/'generic-v1').resolve()
    if out==root or root/'exemple'==out or (root/'exemple') in out.parents:
        raise ValueError('La sortie de construction doit être séparée des sources.')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'build_receipt.json').exists() and not force:
        return json.loads((out/'build_receipt.json').read_text(encoding='utf-8'))
    source,seed=_source_assets(root);before_hash=core.sha(source.read_bytes());wb=core.Workbook(source)
    vba_audit=_audit_vba(wb.z.read('xl/vbaProject.bin'))
    mapping,migration_records=_migrations(wb);schema=_schema(seed,wb,mapping)
    policies=[];formula_records=[];sheet_graph={};replacements={};removed=set()
    additions={(s,a) for s,cs in schema['cells'].items() for a in cs if a not in seed['cells'].get(s,{})}
    styles=ET.fromstring(wb.z.read('xl/styles.xml'));xfs=styles.find('m:cellXfs',N);newstyles={}
    for s,a in sorted(additions):
        cell=wb.sheet(s)[1].get(a)
        old=int(cell.get('s','0')) if cell is not None else 0
        if old not in newstyles:
            xf=copy.deepcopy(xfs[old]);p=xf.find('m:protection',N)
            if p is None:p=ET.SubElement(xf,'{'+NS+'}protection')
            p.set('locked','0');xf.set('applyProtection','1');newstyles[old]=len(xfs);xfs.append(xf)
    xfs.set('count',str(len(xfs)));ET.register_namespace('',NS)
    replacements['xl/styles.xml']=serialize_xml(styles,wb.z.read('xl/styles.xml'))
    for sheet,sh in wb.sheets.items():
        rootxml,cells,shared=wb.sheet(sheet);deps=set();counts={}
        def replace(m):
            addr=m[1].decode();node=cells[addr];fn=node.find('m:f',N);raw=m[0]
            formula=fn.text if fn is not None else None
            # Explicit maintenance migrations: date driver, baseline display and
            # startup notice. None is a client assumption, not a numerical zero.
            if (sheet,addr) in [('Control','C10'),('Valorisation','D112')]:fn=None
            if fn is not None:
                rawformula=wb.formula(sheet,addr) or ''
                clean=_clean_formula(rawformula,mapping)
                for ref in re.findall(r"(?:'((?:[^']|'')+)'|([A-Za-z_][\w ]*))!",clean):
                    target=(ref[0] or ref[1]).replace("''", "'")
                    if target in wb.sheets:deps.add(target)
                if sheet=='Sensi TCA' and 19<=core.coord(addr)[2]<=23:
                    r=core.coord(addr)[2];column=core.coord(addr)[1]
                    if column in (5,8):
                        lhs,rhs=('C','D') if column==5 else ('F','G')
                        clean=f'IF(ISNUMBER({rhs}{r}),{lhs}{r}-{rhs}{r},"n.a.")'
                    elif column==9:clean=f'IF(AND(ISNUMBER(D{r}),ISNUMBER(G{r})),IF(AND(ABS(E{r})<0.01,ABS(H{r})<0.01),"Conforme à la référence","Écart à la référence"),"AUCUNE_REFERENCE")'
                if sheet=='Contrôles' and addr in ('C114','C115','N114','N115'):
                    ref='D' if addr.endswith('114') else 'G'
                    clean=f'IF(COUNT(\'Sensi TCA\'!${ref}$19:${ref}$23)<5,"n.a.",{clean})' if addr.startswith('C') else f'IF(ISNUMBER(C{addr[1:]}),IF(ABS(C{addr[1:]})<=$C$7,"Conforme à la référence","Écart à la référence"),"Aucune référence enregistrée")'
                if sheet=='DATA COGS' and core.coord(addr)[1]==22 and 15<=core.coord(addr)[2]<=27:
                    r=core.coord(addr)[2]
                    clean=clean.replace(f'AND($D{r}="Manuel",$L{r}=0)',f'AND($D{r}="Manuel",OR(NOT(ISNUMBER($L{r})),$L{r}<0))')
                if sheet=='Contrôles' and addr=='C76':
                    prefix='(Assumptions!$C$15:$C$27=1)*(\'DATA COGS\'!$D$15:$D$27="Manuel")'
                    costs="'DATA COGS'!$L$15:$L$27"
                    clean=f'SUMPRODUCT({prefix}*(1-ISNUMBER({costs})))+SUMPRODUCT({prefix}*({costs}<0))'
                if (sheet,addr) in VALUATION_GUARDS:clean=VALUATION_GUARDS[sheet,addr]
                clean=guard_formula(sheet,addr,clean)
                if clean!=rawformula:
                    # Changed shared members are materialized independently; their
                    # calculation identity remains included in the new signature.
                    raw=_new_cell(raw,None,formula=clean)
                    formula=clean
                if formula is not None and _clean_formula(formula,mapping)!=formula:
                    fnode=copy.deepcopy(fn);fnode.text=_clean_formula(formula,mapping)
                    fragment=ET.tostring(fnode,encoding='utf-8').replace((' xmlns="'+NS+'"').encode(),b'')
                    raw=re.sub(rb'<f\b[^>]*?(?:/>|>.*?</f>)',lambda _:fragment,raw,count=1,flags=re.S)
                formula_records.append({'sheet':sheet,'cell':addr,'formula_sha256':core.sha(clean.encode()),
                                        'references':list(dict.fromkeys(re.findall(r"(?:'(?:[^']|'')+'|[A-Za-z_][\w ]*)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?",clean))),
                                        'kind':fn.get('t','normal')})
                policies.append({'sheet':sheet,'cell':addr,'class':'calculated_default' if addr in schema['cells'].get(sheet,{}) else 'calculation','action':'preserve_formula_remove_cache'})
                # No stale calculated strings/numbers from the previous dossier.
                raw=invalidate_caches(raw)
            else:
                value=wb.value(sheet,addr)
                action,new,why=_initial_value(sheet,addr,value,schema,mapping)
                if value is not None or addr in schema['cells'].get(sheet,{}) or action not in ('retain_technical_constant',):
                    policies.append({'sheet':sheet,'cell':addr,'class':action,'action':'clear' if new is None else 'retain_or_replace','reason':why})
                if sheet=='Sensi TCA' and 19<=core.coord(addr)[2]<=23 and core.coord(addr)[1]==2:
                    raw=_new_cell(raw,None,formula=f'YEAR(Control!$C$10)+{core.coord(addr)[2]-19}')
                else:
                    kind='number' if isinstance(new,(int,float)) and not isinstance(new,bool) else 'text'
                    raw=_new_cell(raw,new,kind)
                if addr in schema['cells'].get(sheet,{}):
                    schema['cells'][sheet][addr]['initial_state']='INACTIF' if action=='module_inactive' else 'PARAMETRE_TECHNIQUE' if action=='technical_default' else 'NON_RENSEIGNE'
            if (sheet,addr) in additions:
                old=int(node.get('s','0'));style=str(newstyles[old]).encode()
                if re.search(rb'\bs="\d+"',raw):raw=re.sub(rb'\bs="\d+"',b's="'+style+b'"',raw,count=1)
                else:raw=raw.replace(b'<c ',b'<c s="'+style+b'" ',1)
            return raw
        raw=core.CELL_RX.sub(replace,wb.z.read(sh['part']))
        raw=remove_inherited_protection_credentials(raw)
        raw=re.sub(rb'<hyperlinks\b[^>]*>.*?</hyperlinks>',b'',raw,flags=re.S)
        raw=re.sub(rb'<(?:headerFooter|legacyDrawingHF)\b[^>]*?(?:/>|>.*?</(?:headerFooter|legacyDrawingHF)>)',b'',raw,flags=re.S)
        # New inputs were already materialized in the reference; fail closed if
        # a future model changes this contract rather than silently skipping them.
        missing=[a for s,a in additions if s==sheet and a not in cells]
        if missing:raise ValueError('Entrées nouvelles absentes du XML : '+sheet+' '+str(missing))
        replacements[sh['part']]=raw;sheet_graph[sheet]=sorted(deps)
        wb._sheet_cache.pop(sheet,None)
    # Preserve number/formula mechanics, remove unused source strings and media.
    replacements['xl/sharedStrings.xml']=b'<?xml version="1.0" encoding="UTF-8"?><sst xmlns="'+NS.encode()+b'" count="0" uniqueCount="0"/>'
    for name in wb.z.namelist():
        if name.startswith('xl/charts/') and name.endswith('.xml'):
            replacements[name]=invalidate_chart(wb.z.read(name))
        if name.startswith('xl/media/') or 'comments' in name.lower() or 'persons/person' in name.lower():removed.add(name)
        if name.startswith('docProps/'):
            if name.endswith('core.xml'):
                replacements[name]=b'<?xml version="1.0"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>TCA Conseil</dc:creator><dc:title>Trame BP generique</dc:title></cp:coreProperties>'
            elif name.endswith('custom.xml'):removed.add(name)
            else:
                rx=ET.fromstring(wb.z.read(name))
                for e in rx.iter():
                    if e.text:e.text=_clean_text(e.text,mapping)
                replacements[name]=serialize_xml(rx,wb.z.read(name))
        if name.startswith('xl/drawings/') and name.endswith('.xml') and '/_rels/' not in name:
            rx=ET.fromstring(wb.z.read(name))
            for child in list(rx):
                if any(x.tag.endswith('}pic') for x in child.iter()):rx.remove(child)
            for e in rx.iter():
                if e.text:e.text=_clean_text(e.text,mapping)
            replacements[name]=serialize_xml(rx,wb.z.read(name))
    # Remove metadata relationships to deleted parts and any external hyperlinks.
    for name in wb.z.namelist():
        if name.endswith('.rels'):
            rx=ET.fromstring(wb.z.read(name));changed=False
            for child in list(rx):
                typ=child.get('Type','')
                if any(typ.endswith('/'+x) for x in ['image','comments','threadedComment','person','custom-properties']) or child.get('TargetMode')=='External':
                    rx.remove(child);changed=True
            if changed:replacements[name]=ET.tostring(rx,encoding='utf-8',xml_declaration=True)
    content=ET.fromstring(wb.z.read('[Content_Types].xml'))
    for child in list(content):
        if child.get('PartName','').lstrip('/') in removed:content.remove(child)
    replacements['[Content_Types].xml']=ET.tostring(content,encoding='utf-8',xml_declaration=True)
    # C10 became a scalar; its inherited calculation chain entry must disappear.
    chain,_=core.patch_calculation_chain(wb,[{'sheet':'Control','cell':'C10'},{'sheet':'Valorisation','cell':'D112'}])
    if chain is not None:replacements['xl/calcChain.xml']=chain
    book=wb.z.read('xl/workbook.xml')
    book=remove_inherited_protection_credentials(book)
    book=re.sub(rb'<(?:\w+:)?(?:absPath|revisionPtr)\b[^>]*?(?:/>|>.*?</(?:\w+:)?(?:absPath|revisionPtr)>)',b'',book,flags=re.S)
    replacements['xl/workbook.xml']=core.mark_for_native_calculation(book)
    tmp=out/'_building.xlsm';template=out/'TCA_BP_Trame_generique.xlsm'
    try:
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as zout:
            for info in wb.z.infolist():
                if info.filename not in removed:zout.writestr(copy.copy(info),replacements.get(info.filename,wb.z.read(info.filename)))
        check=core.Workbook(tmp)
        try:
            for sheet,cs in schema['cells'].items():
                for addr,spec in cs.items():
                    spec['fill']=check.fill(sheet,addr)
                    f=check.formula(sheet,addr)
                    if f is not None:spec['default_formula']=f
                    else:spec.pop('default_formula',None)
            schema['signature']=check.semantic_signature(schema)
            schema['template_sha256']=check.hash
            counts={'sheets':len(check.sheets),'fields':len(schema['fields']),'input_cells':sum(map(len,schema['cells'].values())),
                    'protected_formulas':schema['signature']['protected_formula_count'],
                    'formula_defaults':sum('default_formula' in x for cs in schema['cells'].values() for x in cs.values())}
            if counts['sheets']!=33:raise ValueError('La migration doit conserver exactement 33 feuilles.')
        finally:check.close()
        if core.sha(source.read_bytes())!=before_hash:raise ValueError('La source a changé pendant la construction.')
        privacy_audit=audit_workbook_documentation(tmp)
        if privacy_audit['status']!='PASS':
            dump(out/'privacy_audit.json',privacy_audit)
            raise ValueError('Fragment documentaire privé résiduel : consulter les localisations dans privacy_audit.json.')
        os.replace(tmp,template)
    finally:
        wb.close()
        if tmp.exists():tmp.unlink()
    schema['template_name']=template.name
    dump(out/'catalogue_champs.json',schema['fields'])
    dump(out/'classification_cellules.json',{'schema':'tca-bp-classification/v1','policy_version':BUILD_VERSION,'cells':policies})
    dump(out/'migrations.json',{'schema':'tca-bp-migrations/v1','keys':migration_records,
         'qualification_formula_revision':{'ATELIER_CIR_IS':['C67:M68','C86:M86','C90:M90'],'Valorisation':['D138'],
                                          'policy':'No favorable fallback for unknown capital/CVAE status; owner D9 must exist'},
         'protection_policy':'SHEET_FLAGS_RETAINED_WITHOUT_INHERITED_CREDENTIALS',
         'technical_names_retained':list(TECHNICAL_NAMES),'formula_changes':['Control!C10 becomes a scalar date input','Valorisation!D112 becomes an empty sourced market input','Sensi TCA!B19:B23 use the date driver','Baseline comparisons are unavailable until an actual reference exists','DATA COGS!V15:V27 and Contrôles!C76 distinguish explicit zero manual cost from missing or negative cost','Valorisation!B55,D59 and Contrôles!C121,N121 report unavailable valuation inputs without spurious Excel errors','quoted legacy labels migrated explicitly'],
         'removed_parts':sorted(removed),'no_original_values_in_report':True})
    dump(out/'graphe_dependances.json',{'schema':'tca-bp-dependencies/v1','sheets':sheet_graph,'cells':formula_records,
         'defined_names':[dict(n.attrib,text=n.text or '') for n in ET.fromstring(replacements['xl/workbook.xml']).findall('m:definedNames/m:definedName',N)],
         'native_tables':[{'sheet':'Sensi Analyses','range':'D25:G33','inputs':['C18']}, {'sheet':'Sensi Analyses','range':'C40:D45','inputs':['C8']},{'sheet':'Sensi Analyses','range':'D50:F52','inputs':['C14','C8']}],
         'macro':{'preserved':True,'sha256':core.sha(replacements.get('xl/vbaProject.bin',zipfile.ZipFile(source).read('xl/vbaProject.bin'))),'outputs':schema['native_outputs'],'executed':False},
         'limits':['String-based references and macro dependencies need native qualification','Fiscal annual rules inherited require explicit jurisdiction and date review']})
    dump(out/'modele.json',schema)
    receipt={'schema':'tca-bp-build/v1','model_id':MODEL_ID,'build_version':BUILD_VERSION,'template_path':str(template),
             'schema_path':str(out/'modele.json'),'source_sha256':before_hash,'source_unchanged':True,
             'template_sha256':core.sha(template.read_bytes()),'schema_sha256':core.sha((out/'modele.json').read_bytes()),
             'counts':counts,'vba_static_audit':vba_audit,'privacy_audit':privacy_audit,'financial_results_status':'UNAVAILABLE','native_calculation':'NOT_EXECUTED',
             'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
             'limitations':['No statutory rate or eligibility is assumed for a new dossier','Formula-level native behavior and VBA execution require native validation','Legacy technical WACC namespace retained for binary compatibility']}
    dump(out/'build_receipt.json',receipt)
    refresh_dependency_graph(out)
    return receipt
