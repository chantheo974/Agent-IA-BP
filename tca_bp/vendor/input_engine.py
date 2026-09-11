#!/usr/bin/env python3
"""TCA BP: deterministic input writer. No network or VBA execution.

Uses Python and the bundled read-only OLE parser. It edits a copy of selected
OOXML input cells and calculation indexes, and checks model semantics before output.
"""
from __future__ import annotations
import argparse, calendar, copy, datetime as dt, decimal, hashlib, json, math, os
import posixpath, re, sys, tempfile, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION = '1.1.0'
SCHEMA_SHA256 = '339e46d63ed9d1bc1192624f98bad2f614dd0ee313a3d47e6c995a4d75b59704'
RESOLVER_SHA256 = 'b4f772b37cb0c8a1d4dd17098915804e6958512665abab0187b92d710ab22ffc'
VBA_FINGERPRINT_SHA256 = 'e783c46aaa0ce480fcf23a6f11b0fca6c72b6a182066bfff30c86d3eade95da6'
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
N = {'m': NS}
LIMIT = 600 * 1024 * 1024
CELL_RX = re.compile(rb'<(?:\w+:)?c\b[^>]*?\br="([A-Z]+[1-9][0-9]*)"[^>]*?(?:/>|>.*?</(?:\w+:)?c>)', re.S)

class Refusal(ValueError):
    pass

def insist(condition, message):
    if not condition:
        raise Refusal(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def packed(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')

def blank(value):
    return value is None or (isinstance(value,str) and not value.strip())

def colnum(col):
    n = 0
    for x in col:
        n = n * 26 + ord(x.upper()) - 64
    return n

def colname(n):
    insist(1 <= n <= 16384, 'Référence de colonne hors Excel.')
    s = ''
    while n:
        n, r = divmod(n-1, 26)
        s = chr(65+r) + s
    return s

def coord(a):
    m = re.fullmatch(r'(\$?)([A-Za-z]{1,3})(\$?)([1-9][0-9]*)', a)
    insist(m is not None, 'Adresse de cellule invalide : ' + a)
    return m, colnum(m[2]), int(m[4])

def translate_formula(formula, origin, target):
    """Translate shared A1 formulas, leaving quoted literals/sheet names intact.

    A verified read-only comparison against openpyxl's Translator is part of the
    release tests. Unsupported shared structured references fail closed.
    """
    _, oc, orow = coord(origin); _, tc, tr = coord(target)
    dc, dr = tc-oc, tr-orow
    parts = re.split(r'("(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'|\[[^\]]*\])', formula)
    insist(not any(re.search(r'[A-Za-z_][A-Za-z0-9_.]*:[A-Za-z_][A-Za-z0-9_.]*!',parts[i]) for i in range(0,len(parts),2)), 'Référence 3D partagée non prise en charge.')
    def move(m):
        a = m.group(0)
        cm, c, r = coord(a)
        if c > 16384 or r > 1048576:
            return a
        c += 0 if cm[1] else dc
        r += 0 if cm[3] else dr
        insist(1 <= c <= 16384 and 1 <= r <= 1048576, 'Translation partagée hors limites.')
        return cm[1]+colname(c)+cm[3]+str(r)
    def move_col(m):
        def one(a):
            c=colnum(a.lstrip('$'))
            return a if a.startswith('$') else colname(c+dc)
        return one(m[1])+':'+one(m[2])
    def move_row(m):
        def one(a):
            if a.startswith('$'):return a
            row=int(a)+dr
            insist(1<=row<=1048576,'Translation de ligne entière hors limites.')
            return str(row)
        return one(m[1])+':'+one(m[2])
    for i in range(0, len(parts), 2):
        t=parts[i]
        t=re.sub(r'(?<![A-Za-z0-9_.$])\$?[A-Za-z]{1,3}\$?[1-9][0-9]*(?![A-Za-z0-9_.!]|\s*\()', move, t)
        t=re.sub(r'(?<![A-Za-z0-9_.$])(\$?[A-Za-z]{1,3}):(\$?[A-Za-z]{1,3})(?![A-Za-z0-9_.])',move_col,t)
        t=re.sub(r'(?<![A-Za-z0-9_.$])(\$?[1-9][0-9]*):(\$?[1-9][0-9]*)(?![A-Za-z0-9_.])',move_row,t)
        parts[i]=t
    return ''.join(parts)

def canonical_number(value):
    try:
        d=decimal.Decimal(str(value))
        insist(d.is_finite(), 'Nombre non fini.')
        return format(d.normalize(), 'f')
    except decimal.InvalidOperation:
        raise Refusal('Nombre invalide.')

def canonical_xml(node):
    if node is None:
        return None
    return [node.tag, sorted(node.attrib.items()), node.text or '', [canonical_xml(c) for c in node]]

class Workbook:
    def __init__(self, path):
        self.path=Path(path)
        self.bytes=self.path.read_bytes()
        self.hash=sha(self.bytes)
        insist(zipfile.is_zipfile(self.path), 'Classeur chiffré ou non OOXML : utiliser une copie XLSM non chiffrée.')
        self.z=zipfile.ZipFile(self.path)
        entries=self.z.infolist(); names=[i.filename for i in entries]
        insist(len(names)==len(set(names)), 'Membres ZIP dupliqués.')
        insist(sum(i.file_size for i in entries)<=LIMIT, 'Classeur trop volumineux pour cette version du moteur.')
        insist(not any(n.startswith('_xmlsignatures/') for n in names), 'Signature de document OOXML : la saisie l’invaliderait.')
        insist('xl/vbaProject.bin' in names, 'Ce fichier n’est pas le modèle XLSM attendu.')
        self.wb=ET.fromstring(self.z.read('xl/workbook.xml'))
        pr=self.wb.find('m:workbookPr',N)
        self.date1904=pr is not None and pr.get('date1904','0') in ('1','true')
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))}
        self.sheets={}
        for s in self.wb.findall('m:sheets/m:sheet',N):
            target=rels[s.get('{'+REL+'}id')]
            self.sheets[s.get('name')]={'part':target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join('xl',target)), 'state':s.get('state','visible')}
        self.strings=[]
        if 'xl/sharedStrings.xml' in names:
            self.strings=[''.join(n.itertext()) for n in []]
            self.strings=[''.join(t.text or '' for t in si.iter('{'+NS+'}t')) for si in ET.fromstring(self.z.read('xl/sharedStrings.xml'))]
        styles=ET.fromstring(self.z.read('xl/styles.xml'))
        self.fills=list(styles.find('m:fills',N)); self.xfs=list(styles.find('m:cellXfs',N))
        self._sheet_cache={}
        self._signature_cache={}
    def close(self):
        self.z.close()
    def sheet(self,name):
        insist(name in self.sheets, 'Feuille inconnue : '+name)
        if name not in self._sheet_cache:
            root=ET.fromstring(self.z.read(self.sheets[name]['part']))
            cells={c.get('r'):c for c in root.findall('m:sheetData/m:row/m:c',N)}
            shared={}
            for addr,c in cells.items():
                f=c.find('m:f',N)
                if f is not None and f.get('t')=='shared' and f.text:
                    shared[f.get('si')]=(addr,f.text)
            self._sheet_cache[name]=(root,cells,shared)
        return self._sheet_cache[name]
    def formula(self,name,addr):
        _,cells,shared=self.sheet(name)
        c=cells.get(addr)
        if c is None:return None
        f=c.find('m:f',N)
        if f is None:return None
        if f.get('t')=='shared':
            insist(f.get('si') in shared,'Formule partagée sans ancre : '+name+'!'+addr)
            origin,text=shared[f.get('si')]
            return translate_formula(text,origin,addr)
        return f.text or ''
    def value(self,name,addr):
        c=self.sheet(name)[1].get(addr)
        if c is None:return None
        v=c.find('m:v',N); typ=c.get('t','n')
        if typ=='inlineStr':return ''.join(t.text or '' for t in c.iter('{'+NS+'}t'))
        if v is None or v.text is None:return None
        if typ=='s':return self.strings[int(v.text)]
        if typ=='b':return v.text=='1'
        if typ in ('str','e','d'):return v.text
        return float(v.text) if any(x in v.text.lower() for x in ('.','e')) else int(v.text)
    def fill(self,name,addr):
        c=self.sheet(name)[1].get(addr)
        if c is None:return None
        xf=self.xfs[int(c.get('s','0'))]
        p=self.fills[int(xf.get('fillId','0'))].find('m:patternFill',N)
        if p is None:return None
        fg=p.find('m:fgColor',N)
        return {'pattern':p.get('patternType'), 'fg':{} if fg is None else dict(fg.attrib)}
    def snapshot(self,name,addr):
        return {'value':self.value(name,addr),'formula':self.formula(name,addr)}
    def semantic_signature(self,schema):
        key=sha(packed([[(s,sorted(v)) for s,v in schema['cells'].items()],schema.get('native_outputs',{}),schema.get('native_table_outputs',{})]))
        if key in self._signature_cache:return copy.deepcopy(self._signature_cache[key])
        records=[]; per_sheet={}; count=0
        for name,sh in self.sheets.items():
            root,cells,_=self.sheet(name); h=hashlib.sha256()
            allowed=schema['cells'].get(name,{})
            for addr,c in sorted(cells.items(),key=lambda p:(coord(p[0])[2],coord(p[0])[1])):
                if addr in allowed:continue
                f=self.formula(name,addr)
                if f is not None:
                    node=c.find('m:f',N)
                    attrs={k:v for k,v in node.attrib.items() if k not in ('si','ref','t','ca','aca')}
                    if node.get('t') not in (None,'normal','shared'):
                        attrs.update({k:v for k,v in node.attrib.items() if k not in ('ca','aca')})
                    record=[addr,'formula',f,attrs];count+=1
                else:
                    value=self.value(name,addr)
                    if addr in schema.get('native_outputs',{}).get(name,[]):continue
                    if addr in schema.get('native_table_outputs',{}).get(name,[]):continue
                    if value is None:continue
                    record=[addr,'value',canonical_number(value) if isinstance(value,(float,int)) and not isinstance(value,bool) else value]
                h.update(packed(record));h.update(b'\n')
            structure={}
            for tag in ['mergeCells','dataValidations','tableParts','sheetProtection']:
                node=copy.deepcopy(root.find('m:'+tag,N))
                if tag=='mergeCells' and node is not None:
                    node[:]=sorted(node,key=lambda c:packed(canonical_xml(c)))
                structure[tag]=canonical_xml(node)
            per_sheet[name]={'cells':h.hexdigest(),'structure':sha(packed(structure))}
            records.append([name,sh['state'],per_sheet[name]])
            self._sheet_cache.pop(name,None)
        defined=[dict(x.attrib,text=x.text or '') for x in self.wb.findall('m:definedNames/m:definedName',N) if not x.get('name','').startswith(('_xlnm.Print_','_xlnm._FilterDatabase'))]
        vba=self.z.read('xl/vbaProject.bin')
        vba_hash=sha(vba);vba_strict=vba_hash
        if vba.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):
            fp_path=Path(__file__).with_name('vba_fingerprint.py')
            insist(sha(fp_path.read_bytes())==VBA_FINGERPRINT_SHA256,'Le lecteur VBA ne correspond pas au pack scellé.')
            from .vba_fingerprint import fingerprint, compatibility_fingerprint
            vba_strict=fingerprint(vba)
            vba_hash=compatibility_fingerprint(vba)
        book_protection=canonical_xml(self.wb.find('m:workbookProtection',N))
        result={'sheets':per_sheet,'sheet_order':list(self.sheets),'defined_names':sha(packed(defined)), 'vba':vba_hash,'vba_strict':vba_strict,'protected_formula_count':count,'date1904':self.date1904,'workbook_protection':book_protection,'overall':sha(packed([records,defined,self.date1904,book_protection]))}
        self._signature_cache[key]=copy.deepcopy(result)
        return result
    def input_signature(self,schema):
        data=[]
        for s,entries in schema['cells'].items():
            for a in sorted(entries):
                f=self.formula(s,a);v=self.value(s,a)
                data.append([s,a,'formula',f] if f is not None else [s,a,'value',canonical_number(v) if isinstance(v,(int,float)) and not isinstance(v,bool) else v])
        return sha(packed(data))

def load_schema(path):
    raw=Path(path).read_bytes()
    insist(sha(raw)==SCHEMA_SHA256,'Le manifeste ne correspond pas à la version scellée du moteur.')
    schema=json.loads(raw.decode('utf-8'))
    insist(schema.get('schema')=='isp-pilotage-model/v1','Schéma de modèle incompatible.')
    return schema

def canonical_vba_signature(actual,schema):
    """Match only explicitly audited compilations bound to this exact model."""
    expected=schema['signature']['vba'];variants=schema.get('native_vba_variants',[])
    insist(isinstance(variants,list) and len(variants)<=32,'Liste de variantes VBA invalide.')
    known=set()
    for variant in variants:
        insist(isinstance(variant,dict),'Variante VBA invalide.')
        insist(variant.get('fingerprint_schema')=='isp-vba-project-metadata/v1','Version de comparaison VBA inconnue.')
        insist(variant.get('reference_source_sha256')==schema['source_sha256'] and variant.get('canonical_vba_fingerprint')==expected and variant.get('canonical_model_signature')==schema['signature']['overall'],'Variante VBA liée à un autre modèle.')
        fp=variant.get('compatibility_fingerprint')
        insist(isinstance(fp,str) and re.fullmatch(r'[0-9a-f]{64}',fp) is not None and fp not in known,'Empreinte de variante VBA invalide ou dupliquée.')
        known.add(fp)
    return expected if actual==expected or actual in known else actual


def verify_model(wb,schema):
    if schema.get('forbid_tca_filename'):
        insist(not re.search(r'(?:^|[^A-Za-z])TCA(?:[^A-Za-z]|$)',wb.path.stem,re.I),'Utiliser le Pilotage fourni, pas la version TCA calibrée.')
    actual=wb.semantic_signature(schema); expected=schema['signature']
    for key in ('sheet_order','defined_names','vba','protected_formula_count','overall'):
        observed=canonical_vba_signature(actual[key],schema) if key=='vba' else actual[key]
        insist(observed==expected[key], 'Modèle différent ou mécanique modifiée ('+key+'). Ne pas adapter automatiquement la liste blanche.')
    for name,entries in schema['cells'].items():
        for addr,spec in entries.items():
            f=wb.formula(name,addr)
            if f is not None:
                insist(spec.get('default_formula')==f, 'Formule de saisie inconnue : '+name+'!'+addr)
    return actual

def public_spec(spec):
    return {k:v for k,v in spec.items() if k not in ('fill',)}

def write_json_exclusive(path,value,protected=()):
    path=Path(path)
    insist(all(path.resolve()!=Path(p).resolve() for p in protected),'La sortie JSON ne peut remplacer un fichier de travail ou du moteur.')
    insist(not path.exists(),'La sortie existe déjà : choisir un nouveau nom.')
    with path.open('x',encoding='utf-8') as f:
        f.write(json.dumps(value,ensure_ascii=False,indent=2))

def context(wb,schema):
    sig=verify_model(wb,schema)
    registers={}
    for name,reg in schema.get('registers',{}).items():
        free=[];used=[]
        for row in range(reg['start_row'],reg['end_row']+1):
            vacant=True
            for col in reg['identity_columns']:
                addr=col+str(row);f=wb.formula(name,addr);value=wb.value(name,addr)
                if f is not None:
                    # Known defaults do not constitute an occupied record.
                    if f!=schema['cells'].get(name,{}).get(addr,{}).get('default_formula'):vacant=False
                elif value is not None and value!=reg.get('template_defaults_by_cell',{}).get(addr,reg.get('preserved_template_values',{}).get(col,object())):vacant=False
            (free if vacant else used).append(row)
        registers[name]={'occupied_rows':used,'first_free_row':free[0] if free else None,'free_count':len(free),'required_columns':reg.get('required',[])}
    return {'schema':'isp-pilotage-context/v1','model_id':schema['model_id'],'source_name':wb.path.name,'source_sha256':wb.hash,'sheets':len(wb.sheets),'protected_formulas':sig['protected_formula_count'],'active_years':wb.value('Control','C59'),'start_excel_date':wb.value('Control','C10'),'input_count':sum(len(v) for v in schema['cells'].values()),'registers':registers,'calculation_status':'CACHES_NON_CERTIFIES_PAR_CETTE_LECTURE','instructions':'Lire les champs utiles via inspect --sheet NOM --cells A1,B1. Ne pas choisir une ligne libre de mémoire.'}

def inspect(wb,schema,sheet=None,cells=None):
    sig=verify_model(wb,schema)
    names=[sheet] if sheet else list(schema['cells'])
    out={'schema':'isp-pilotage-inspection/v1','source_name':wb.path.name,'source_sha256':wb.hash,'model_id':schema['model_id'], 'verified_protected_formulas':sig['protected_formula_count'],'inputs':{}}
    for name in names:
        insist(name in schema['cells'],'Aucune saisie autorisée dans cette feuille.')
        selection=cells.split(',') if cells else schema['cells'][name]
        out['inputs'][name]={a:{**public_spec(schema['cells'][name][a]),'current':wb.snapshot(name,a)} for a in selection if a in schema['cells'][name]}
    return out

def resume(wb,schema,receipt):
    verify_model(wb,schema)
    insist(receipt.get('schema')=='isp-pilotage-receipt/v1','Le journal fourni ne correspond pas au format attendu.')
    insist(receipt.get('model_id')==schema['model_id'],'Ce journal appartient à un autre modèle.')
    match=wb.input_signature(schema)==receipt.get('output_input_signature')
    insist(match,'Le classeur et le journal ne contiennent pas les mêmes saisies. Identifier la dernière copie ou documenter les modifications manuelles avant un nouveau lot.')
    exact=wb.hash==receipt.get('output_sha256')
    return {'schema':'isp-pilotage-resume/v1','valid':True,'model_id':schema['model_id'],'source_name':wb.path.name,'source_sha256':wb.hash,'inputs_match_receipt':True,'binary_matches_receipt':exact,'status':'COPIE_IDENTIQUE' if exact else 'MEMES_SAISIES_FICHIER_REENREGISTRE','calculation_status':'NON_CERTIFIE_PAR_CE_CONTROLE','notice':'Les mêmes saisies et la mécanique protégée sont présentes. Un réenregistrement natif peut changer les caches et le fichier binaire ; ce contrôle ne certifie pas le recalcul ni l’exécution VBA.'}

def normalize_change(wb,schema,change):
    required={'sheet','cell','value','reason','expected'}
    insist(required <= set(change),'Changement incomplet : feuille, cellule, valeur, raison et état attendu requis.')
    insist(not(set(change)-required-{'override_default','replace_existing','evidence'}),'Clé de changement inconnue.')
    name,addr=change['sheet'],change['cell']
    spec=schema['cells'].get(name,{}).get(addr)
    insist(spec is not None,'Cellule hors liste blanche : '+str(name)+'!'+str(addr))
    insist(wb.fill(name,addr)==spec['fill'],'La couleur de saisie a changé : '+name+'!'+addr)
    insist(isinstance(change['reason'],str) and len(change['reason'].strip())>=8,'Justification métier requise.')
    actual=wb.snapshot(name,addr)
    insist(packed(actual)==packed(change['expected']),'La cellule a changé depuis la préparation : '+name+'!'+addr)
    if actual['formula'] is not None:
        insist(spec.get('default_formula')==actual['formula'] and change.get('override_default') is True,'Remplacement du défaut calculé à justifier explicitement : '+name+'!'+addr)
    elif actual['value'] is not None and actual['value']!=change['value']:
        insist(change.get('replace_existing') is True,'Valeur existante : préciser explicitement son remplacement dans le plan.')
    value=change['value'];kind=spec['kind']
    insist(spec.get('allow_blank',True) or not blank(value),'Ce champ ne peut pas être laissé vide.')
    if value is None:
        insist(spec.get('allow_blank',True),'Ce champ ne peut pas être vidé.')
    elif kind in ('number','integer','percent'):
        insist(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value),'Nombre JSON fini requis : '+name+'!'+addr)
        insist(kind!='integer' or int(value)==value,'Entier requis : '+name+'!'+addr)
        insist('min' not in spec or value>=spec['min'],'Valeur sous le minimum : '+name+'!'+addr)
        insist('max' not in spec or value<=spec['max'],'Valeur au-dessus du maximum : '+name+'!'+addr)
        insist('min_exclusive' not in spec or value>spec['min_exclusive'],'Valeur sous la borne exclusive : '+name+'!'+addr)
        insist('max_exclusive' not in spec or value<spec['max_exclusive'],'Valeur au-dessus de la borne exclusive : '+name+'!'+addr)
        insist(not spec.get('whole_months') or abs(value*12-round(value*12))<1e-8,'Durée attendue en nombre entier de mois : '+name+'!'+addr)
        if spec.get('max_ref'):
            rs,ra=spec['max_ref'].split('!')
            insist(value<=wb.value(rs,ra),'Valeur au-dessus de la capacité du modèle : '+name+'!'+addr)
    elif kind=='date':
        insist(isinstance(value,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',value),'Date ISO YYYY-MM-DD requise.')
        try:d=dt.date.fromisoformat(value)
        except ValueError:raise Refusal('Date inexistante : '+value)
        insist(dt.date(1900,3,1)<=d<=dt.date(2100,12,31),'Date hors bornes prises en charge.')
    else:
        insist(isinstance(value,str) and len(value)<=32767,'Texte Excel valide requis.')
        insist(not any(ord(x)<32 and x not in '\t\r\n' for x in value),'Caractère XML interdit.')
        insist(not re.search(r'\[?à\s*compléter\]?|\[TODO\]',value,re.I),'Les informations manquantes vont dans les questions, jamais dans le classeur.')
    if value is not None and spec.get('choices') and not spec.get('choices_source'):
        insist(value in spec['choices'],'Valeur hors liste pour '+name+'!'+addr+' : '+str(value))
    return dict(change,kind=kind)

def excel_serial(value,date1904=False):
    return (dt.date.fromisoformat(value)-(dt.date(1904,1,1) if date1904 else dt.date(1899,12,30))).days

def prospective_value(wb,changes,sheet,cell):
    for c in changes:
        if c['sheet']==sheet and c['cell']==cell:
            return excel_serial(c['value'],wb.date1904) if c['kind']=='date' and c['value'] is not None else c['value']
    return wb.value(sheet,cell)

def business_checks(wb,schema,changes):
    """Rules apply to affected records; unrelated historical alerts remain visible."""
    pv=lambda s,a:prospective_value(wb,changes,s,a)
    affected={(c['sheet'],coord(c['cell'])[2]) for c in changes}
    errors=[]
    horizon=pv('Control','C59')
    insist(isinstance(horizon,(int,float)) and not isinstance(horizon,bool) and math.isfinite(horizon) and int(horizon)==horizon and 1<=horizon<=10,
           'Horizon actif requis : entier de 1 à 10. Le vide n’est pas un horizon.')
    for change in changes:
        spec=schema['cells'][change['sheet']][change['cell']]
        if spec.get('choices_source') and change['value'] is not None:
            src=spec['choices_source'];start,end=src['range'].split(':');cm,_,first=coord(start);_,_,last=coord(end)
            choices=[pv(src['sheet'],cm[2]+str(r)) for r in range(first,last+1)]
            if change['value'] not in choices:errors.append(change['sheet']+'!'+change['cell']+' : libellé absent du catalogue courant.')
    for rule in schema.get('business_rules',[]):
        s=rule['sheet'];rows=rule.get('rows',[])
        for r in rows:
            if (s,r) not in affected:continue
            if rule['type']=='date_order':
                a,b=pv(s,rule['start']+str(r)),pv(s,rule['end']+str(r))
                if a is not None and b is not None and a>b:errors.append(s+f' ligne {r} : fin antérieure au début.')
            elif rule['type']=='sum_100':
                # Une offre explicitement inactive n'a pas encore de modalités
                # de facturation. Son activation prospective rétablit la règle.
                if s=='Assumptions' and 15<=r<=27 and pv(s,'C'+str(r))==0:
                    continue
                values=[pv(s,c+str(r)) for c in rule['cols']]
                if not all(isinstance(x,(float,int)) and not isinstance(x,bool) for x in values) or abs(sum(values)-1)>1e-8:errors.append(s+f' ligne {r} : pourcentages absents ou différents de 100 %.')
            elif rule['type']=='sum_at_most_100':
                values=[pv(s,c+str(r)) or 0 for c in rule['cols']]
                if sum(values)>1+1e-8:errors.append(s+f' ligne {r} : acomptes et jalons au-dessus de 100 %.')
            elif rule['type']=='required_record':
                active=any(not blank(pv(s,c+str(r))) for c in rule['trigger'])
                if rule.get('activation',{}).get('positive'):
                    av=pv(s,rule['activation']['column']+str(r))
                    active=isinstance(av,(float,int)) and av>0
                if active:
                    missing=[c+str(r) for c in rule['cols'] if blank(pv(s,c+str(r)))]
                    if missing:errors.append(s+f' ligne {r} : informations requises absentes '+','.join(missing))
    changed={(c['sheet'],c['cell']):c for c in changes}
    numeric=lambda x:isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
    for s,r in affected:
        v=lambda col:pv(s,col+str(r))
        if s=='DATA Contrats' and 14<=r<=413:
            if v('R')=='Previsionnel':errors.append(f'Contrat {r} : un objectif commercial va dans Assumptions, pas au statut Previsionnel.')
            if v('K')=='Acompte et solde':
                for part,datecol in [('L','M'),('N','O')]:
                    if numeric(v(part)) and v(part)>0 and blank(v(datecol)):errors.append(f'Contrat {r} : date {datecol} requise pour la tranche {part}.')
                solde=1-(v('L') or 0)-(v('N') or 0)
                if solde>1e-8 and blank(v('Q')):errors.append(f'Contrat {r} : date du solde Q requise.')
            if v('AL')=='Exonéré / hors champ' and v('AM') not in (None,0):errors.append(f'Contrat {r} : TVA exonérée incompatible avec un taux positif.')
        elif s=='Assumptions' and 15<=r<=27 and (s,'B'+str(r)) in changed:
            old=wb.value(s,'B'+str(r));new=v('B')
            if old!=new:
                leftover=[k for k in range(14,414) if pv('DATA Contrats','C'+str(k))==old]
                if leftover:errors.append(f'Offre {r} : le renommage laisserait des contrats liés à l’ancien libellé, lignes '+','.join(map(str,leftover)))
        elif s=='DATA CAPEX' and 13<=r<=72:
            resolver_path=Path(__file__).with_name('resolve_input_defaults.py')
            insist(sha(resolver_path.read_bytes())==RESOLVER_SHA256,'Le résolveur de défauts ne correspond pas au pack scellé.')
            try:
                from .resolve_input_defaults import resolve_capex_row,validate_capex_local
            except ImportError:raise Refusal('Ressource resolve_input_defaults.py absente ; reprendre le pack intact.')
            insist(not wb.date1904,'Résolveur CAPEX livré pour le système de dates 1900 du Pilotage.')
            values={col:v(col) for col in ['B','C','D','E','F','G','H','I','J','K','M','N','O','P']}
            fcols=[col for col in ['F','H','J','K','M','N','O','P'] if (s,col+str(r)) not in changed and wb.formula(s,col+str(r)) is not None]
            catalog=[{'label':pv('Assumptions','B'+str(k)),'years':pv('Assumptions','C'+str(k)),'rd_share':pv('Assumptions','D'+str(k))} for k in range(98,122)]
            effective=resolve_capex_row(values,fcols,catalog,pv('Assumptions','D91'))
            errors.extend(f'CAPEX {r} : '+x for x in validate_capex_local(effective,catalog))
        elif s=='Financement Dette' and 3<=r<=42:
            if numeric(v('C')) and v('C')>0 and v('F')=='Amortissement constant':
                if not numeric(v('H')) or not numeric(v('E')) or not 0<=v('H')<v('E'):errors.append(f'Dette {r} : différé explicite, positif ou nul, strictement inférieur à la durée.')
        elif s=='SUBVENTION_INVEST' and 3<=r<=23 and numeric(v('C')) and v('C')>0:
            if not numeric(v('G')) or not numeric(v('I')) or abs(v('G')+v('I')-1)>1e-8:errors.append(f'Subvention {r} : acompte + solde doivent faire 100 %.')
            for part,datecol in [('G','H'),('I','J')]:
                if numeric(v(part)) and v(part)>0 and blank(v(datecol)):errors.append(f'Subvention {r} : date {datecol} manquante.')
            if blank(v('K')) and blank(v('H')):errors.append(f'Subvention {r} : début de reprise K requis si la date H est absente.')
        elif s=='ATELIER_CIR_IS' and 143<=r<=155:
            if v('D')=='Exonéré / hors champ' and v('E')!=0:errors.append(f'TVA ligne {r} : Exonéré / hors champ exige un taux explicite de zéro.')
        elif s=='DATA COGS' and 15<=r<=27:
            if v('D')=='Manuel' and (not numeric(v('L')) or v('L')<0):errors.append(f'COGS {r} : coût manuel L explicite, positif ou nul, requis.')
            if v('D')=='Cible':
                margin_cols=['M','N','O','P','Q','X','Y','Z','AA','AB'][:int(pv('Control','C59'))]
                for col in margin_cols:
                    if not numeric(v(col)) or v(col)+(v('J') or 0)+(v('K') or 0)>1+1e-8:errors.append(f'COGS {r} : marge {col} et coûts J/K incohérents.')
        elif s=='Comparables' and 117<=r<=136 and v('C')=='Oui':
            missing=[col for col in ['B','D','E','F','G','J','K','L','M'] if blank(v(col))]
            if missing:errors.append(f'Comparable {r} retenu : champs requis absents '+','.join(missing))
            if not numeric(v('E')) or v('E')<=0:errors.append(f'Comparable {r} : capitalisation positive requise.')
            if not numeric(v('F')) or v('F')<0:errors.append(f'Comparable {r} : dette positive ou nulle requise.')
            if not numeric(v('G')) or not 0<=v('G')<1:errors.append(f'Comparable {r} : IS attendu dans [0 ; 1[.')
            if v('L') not in ('Hebdomadaire','Mensuelle') or not numeric(v('M')) or not 2<=v('M')<=5:errors.append(f'Comparable {r} : fréquence et fenêtre 2–5 ans requises.')
    calendar_sheets={'Valorisation','Control','DATA Financement','Financement E&S','Sensi TCA','Sensi Analyses'}
    if any(c['sheet'] in calendar_sheets for c in changes) and 'calendar' in schema:
        start_value=pv('Control','C10')
        insist(numeric(start_value),'Date de début du modèle requise.')
        start_date=dt.date(1899,12,30)+dt.timedelta(days=int(start_value))
        insist(start_date.month==1 and start_date.day==1,'Le modèle annuel commence le 1er janvier.')
        start_year=start_date.year;active_years=pv('Control','C59')
        end_year=start_year+int(active_years)-1
        exit_year=pv('Valorisation','D16') if ('Valorisation','D16') in changed or wb.formula('Valorisation','D16') is None else end_year
        if not numeric(exit_year) or int(exit_year)!=exit_year or not start_year<=exit_year<=end_year:errors.append('Année de sortie VC hors horizon actif : ajuster D16 ou l’horizon, sans modifier les formules.')
        dates=[pv('DATA Financement','E'+str(r)) for r in range(14,414) if pv('DATA Financement','C'+str(r))==pv('Assumptions','B134')]
        dates=[x for x in dates if numeric(x) and x>0]
        if dates:
            shift=pv('Financement E&S','J7')
            if ('Financement E&S','J7') not in changed and wb.formula('Financement E&S','J7') is not None:
                scenario=pv('Sensi TCA','C15');scenario_row=next((r for r in range(72,79) if pv('Sensi TCA','B'+str(r))==scenario),None)
                insist(scenario_row is not None,'Scénario de financement inconnu.')
                shift=(pv('Sensi TCA','K'+str(scenario_row)) or 0)+(pv('Sensi Analyses','E16') or 0)
            if not numeric(shift) or int(shift)!=shift:errors.append('Décalage de financement attendu en mois entiers.')
            else:
                initial=dt.date(1899,12,30)+dt.timedelta(days=int(min(dates)))
                months=initial.year*12+initial.month-1+int(shift);year,month=divmod(months,12);month+=1
                if not start_year<=year<=end_year:errors.append('Closing de Série A hors horizon actif : revoir date, décalage ou horizon.')
                elif numeric(exit_year) and exit_year<year:errors.append('Année de sortie VC antérieure au closing de Série A.')
    if any(c['sheet']=='Valorisation' for c in changes):
        v=lambda a:pv('Valorisation',a)
        if v('D107')=='Manuel' and numeric(v('D108')) and numeric(v('D8')) and v('D108')<=v('D8'):errors.append('Valorisation : le taux manuel doit dépasser la croissance terminale.')
        if v('D107')=='Structure cible' and not numeric(v('D124')):errors.append('Valorisation : D/E cible D124 requis.')
        if numeric(v('D118')) and v('D118')>0 and (v('D120')=='Flux' or v('D121')!='Non'):errors.append('Valorisation : prime spécifique et abattement des flux incompatibles ou non confirmés.')
        if numeric(v('D119')) and v('D119')>0 and v('D123')!='Non':errors.append('Valorisation : prime d’illiquidité et DLOM incompatibles ou non confirmés.')
    if any(c['sheet']=='Assumptions' and c['cell'].startswith('B') for c in changes):
        labels=[pv('Assumptions','B'+str(r)) for r in range(15,28)]
        if len({str(x).strip().casefold() for x in labels})!=len(labels):errors.append('Les libellés des 13 offres doivent rester uniques.')
    insist(not errors,' ; '.join(errors))

def prepare_plan(wb,schema,request):
    verify_model(wb,schema)
    insist(request.get('schema')=='isp-pilotage-plan/v1','Format du plan incorrect.')
    insist(request.get('model_id')==schema['model_id'],'Identifiant de modèle incorrect.')
    insist(request.get('source_sha256')==wb.hash,'Le plan ne vise pas cette version du classeur.')
    raw=request.get('changes');insist(isinstance(raw,list) and 0<len(raw)<=2000,'Prévoir entre 1 et 2 000 écritures par lot.')
    insist(all(isinstance(c,dict) for c in raw),'Chaque écriture doit être un objet JSON.')
    insist(len({(c.get('sheet'),c.get('cell')) for c in raw})==len(raw),'Cellule dupliquée dans le plan.')
    changes=[normalize_change(wb,schema,c) for c in raw]
    business_checks(wb,schema,changes)
    return changes

def xml_cell(original,value,kind,formula=None,date1904=False):
    opening=re.match(rb'<((?:\w+:)?c)\b([^>]*?)(/?>)',original)
    insist(opening is not None,'Cellule XML invalide.')
    prefix=opening.group(1).decode('ascii')
    insist(':' not in prefix,'Préfixe XML de cellule non pris en charge : aucune sortie produite.')
    esc=lambda s:str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
    if formula is not None:
        replacement=('<f>'+esc(formula)+'</f>').encode('utf-8')
        patched,count=re.subn(rb'<f\b[^>]*?(?:/>|>.*?</f>)',lambda m:replacement,original,count=1,flags=re.S)
        insist(count==1,'Formule à matérialiser introuvable.')
        return patched
    attrs=re.sub(rb'\s+t="[^"]*"',b'',opening.group(2))
    inner=b'' if opening.group(3)==b'/>' else original[opening.end():-4]
    # Preserve extension/metadata children verbatim, even in edited input cells.
    rest=re.sub(rb'<(f|v|is)\b[^>]*?(?:/>|>.*?</\1>)',b'',inner,flags=re.S)
    body=''
    if value is not None:
        if kind=='date':body='<v>'+str(excel_serial(value,date1904))+'</v>'
        elif kind in ('number','integer','percent'):body='<v>'+canonical_number(value)+'</v>'
        else:
            attrs+=b' t="inlineStr"';body='<is><t xml:space="preserve">'+esc(value)+'</t></is>'
    content=body.encode('utf-8')+rest
    return b'<c'+attrs+(b'>'+content+b'</c>' if content else b'/>')

def patch_sheet(wb,name,changes):
    raw=wb.z.read(wb.sheets[name]['part'])
    planned={c['cell']:c for c in changes}
    nodes={m.group(1).decode():m.group(0) for m in CELL_RX.finditer(raw)}
    insist(all(a in nodes for a in planned),'Une cellule attendue est absente du XML : adaptation manuelle nécessaire.')
    replacements={}; materialized=[]
    _,cells,shared=wb.sheet(name)
    # If an edited cell anchors a shared formula, materialize the remaining
    # members to equivalent formulas. Their semantics and caches are verified.
    for addr in planned:
        f=cells[addr].find('m:f',N)
        if f is not None and f.get('t')=='shared' and f.text:
            si=f.get('si')
            for other,c in cells.items():
                of=c.find('m:f',N)
                if other not in planned and of is not None and of.get('t')=='shared' and of.get('si')==si:
                    form=wb.formula(name,other)
                    replacements[other]=xml_cell(nodes[other],None,'number',formula=form)
                    materialized.append(other)
    for addr,c in planned.items():replacements[addr]=xml_cell(nodes[addr],c['value'],c['kind'],date1904=wb.date1904)
    patched=CELL_RX.sub(lambda m:replacements.get(m.group(1).decode(),m.group(0)),raw)
    ET.fromstring(patched)
    return patched,materialized

def mark_for_native_calculation(raw):
    # Keep automatic-except-tables mode; ask Excel to refresh on its next opening.
    m=re.search(rb'<calcPr\b[^>]*(?:/>|>.*?</calcPr>)',raw,re.S)
    insist(m is not None,'Paramètre Excel calcPr absent : aucune sortie produite.')
    node=ET.fromstring(m.group(0));node.set('fullCalcOnLoad','1')
    # Remove an inherited flag too: forcing every later calculation is persistent.
    node.attrib.pop('forceFullCalc',None)
    if node.get('calcMode')=='manual':node.set('calcMode','autoNoTable')
    fragment=ET.tostring(node,encoding='utf-8',short_empty_elements=True)
    return raw[:m.start()]+fragment+raw[m.end():]

def patch_calculation_chain(wb,changes):
    """Remove only entries for input defaults replaced by constants.

    Keeping these entries makes native Excel refuse the file. Preserve remaining
    entries byte for byte, adding an inherited sheet id only when removal of its
    predecessor would otherwise change its meaning. No formulas are calculated.
    """
    if 'xl/calcChain.xml' not in wb.z.namelist():return None,[]
    ids={s.get('name'):s.get('sheetId') for s in wb.wb.findall('m:sheets/m:sheet',N)}
    removed={(ids[c['sheet']],c['cell']) for c in changes if wb.formula(c['sheet'],c['cell']) is not None}
    raw=wb.z.read('xl/calcChain.xml')
    if not removed:return raw,[]
    current_id=None;retained_id=None;removed_entries=[]
    def patch(m):
        nonlocal current_id,retained_id
        node=ET.fromstring(m[0]);current_id=node.get('i',current_id)
        insist(current_id is not None,'Index de calcul sans identifiant de feuille.')
        if (current_id,node.get('r')) in removed:
            removed_entries.append({'sheet_id':current_id,'cell':node.get('r')});return b''
        cell=m[0]
        if node.get('i') is None and current_id!=retained_id:
            cell=cell[:-2]+(' i="'+current_id+'"/>').encode('ascii')
        retained_id=current_id
        return cell
    result=re.sub(rb'<c\b[^>]*/>',patch,raw)
    ET.fromstring(result)
    return result,removed_entries

def verify_transaction(before,after,schema,changes,expected_parts):
    insist(set(before.z.namelist())==set(after.z.namelist()),'Un membre du package a disparu ou a été ajouté.')
    diff=[]
    for n in before.z.namelist():
        if before.z.read(n)!=after.z.read(n):diff.append(n)
    insist(set(diff)==set(expected_parts),'Modification inattendue de membres ZIP : '+str(diff))
    b=before.semantic_signature(schema);a=after.semantic_signature(schema)
    insist(b==a,'Une formule ou un élément protégé du modèle a changé.')
    for change in changes:
        value=excel_serial(change['value'],after.date1904) if change['kind']=='date' and change['value'] is not None else change['value']
        insist(after.value(change['sheet'],change['cell'])==value,'Valeur finale incorrecte.')
        insist(after.formula(change['sheet'],change['cell']) is None,'Formule indésirable dans une cellule saisie.')
        insist(before.fill(change['sheet'],change['cell'])==after.fill(change['sheet'],change['cell']),'Couleur de saisie perdue.')
    # Detect nonplanned edits even inside a changed worksheet, including other
    # editable cells that are excluded from the model fingerprint.
    planned={(c['sheet'],c['cell']) for c in changes}
    for name in {c['sheet'] for c in changes}:
        bc=before.sheet(name)[1];ac=after.sheet(name)[1]
        insist(set(bc)==set(ac),'Des cellules ont été insérées ou supprimées.')
        for addr in bc:
            if (name,addr) not in planned:
                insist(before.snapshot(name,addr)==after.snapshot(name,addr),'Cellule non demandée modifiée : '+name+'!'+addr)
                insist(bc[addr].attrib==ac[addr].attrib,'Attributs non demandés modifiés : '+name+'!'+addr)
                b_extra=[canonical_xml(c) for c in bc[addr] if c.tag!='{'+NS+'}f']
                a_extra=[canonical_xml(c) for c in ac[addr] if c.tag!='{'+NS+'}f']
                insist(b_extra==a_extra,'Métadonnées de cellule non demandées modifiées : '+name+'!'+addr)
    return {'changed_zip_members':diff,'protected_formula_count':a['protected_formula_count'],'vba_sha256':sha(after.z.read('xl/vbaProject.bin')),'vba_content_fingerprint':a.get('vba_strict',a['vba']),'vba_compatibility_fingerprint':a['vba'],'vba_canonical_fingerprint':canonical_vba_signature(a['vba'],schema),'model_signature':a['overall'],'all_other_zip_members_identical':True,'nonplanned_cell_values_and_formulas_unchanged':True}

def apply(wb,schema,plan,out):
    out=Path(out)
    receipt=out.with_suffix('.journal.json')
    insist(out.suffix.lower()=='.xlsm','La copie doit conserver le format .xlsm.')
    insist(out.resolve()!=wb.path.resolve(),'Le fichier source ne doit jamais être écrasé.')
    insist(not out.exists(),'La destination existe déjà : choisir un nouveau nom versionné.')
    insist(not receipt.exists(),'Le journal de destination existe déjà : choisir un nouveau nom versionné.')
    insist(out.parent.is_dir(),'Le dossier de destination doit déjà exister.')
    changes=prepare_plan(wb,schema,plan)
    replacements={}; equivalent={}
    for name in {c['sheet'] for c in changes}:
        data,group=patch_sheet(wb,name,[c for c in changes if c['sheet']==name])
        replacements[wb.sheets[name]['part']]=data
        if group:equivalent[name]=group
    workbook_xml=mark_for_native_calculation(wb.z.read('xl/workbook.xml'))
    if workbook_xml!=wb.z.read('xl/workbook.xml'):replacements['xl/workbook.xml']=workbook_xml
    chain,chain_removed=patch_calculation_chain(wb,changes)
    if chain is not None and chain!=wb.z.read('xl/calcChain.xml'):replacements['xl/calcChain.xml']=chain
    fd,tmp=tempfile.mkstemp(suffix='.xlsm',prefix='.isp_check_',dir=out.parent);os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w') as zout:
            zout.comment=wb.z.comment
            for info in wb.z.infolist():zout.writestr(copy.copy(info),replacements.get(info.filename,wb.z.read(info.filename)))
        after=Workbook(tmp)
        try:
            checks=verify_transaction(wb,after,schema,changes,replacements)
            new_hash=after.hash
            new_input_signature=after.input_signature(schema)
        finally:after.close()
        insist(sha(wb.path.read_bytes())==wb.hash,'La source a changé pendant le traitement : sortie abandonnée.')
        result={'schema':'isp-pilotage-receipt/v1','engine_version':VERSION,'engine_sha256':sha(Path(__file__).read_bytes()),'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'model_id':schema['model_id'],'source_name':wb.path.name,'source_sha256':wb.hash,'output_name':out.name,'output_sha256':new_hash,'output_input_signature':new_input_signature,'changes':changes,'equivalent_shared_formula_serialization':equivalent,'checks':checks,'native_calculation':'PENDING_EXCEL','notice':'Saisies appliquées ; résultats calculés en cache non actualisés. Ouvrir la copie dans Excel, F9, puis bouton WACC si les entrées pertinentes ont changé en mode Itération. Aucun calcul Excel ou VBA exécuté par ce moteur.'}
        result['calculation_chain_defaults_removed']=chain_removed
        # Prepare both files fully, then publish exclusively. No existing path
        # can be overwritten; a failed second publication removes our first.
        jfd,jtmp=tempfile.mkstemp(suffix='.json',prefix='.isp_receipt_',dir=out.parent)
        os.close(jfd);published=[]
        try:
            Path(jtmp).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            os.link(tmp,out);published.append(out)
            os.link(jtmp,receipt);published.append(receipt)
        except OSError:
            for pth in reversed(published):pth.unlink()
            raise
        finally:
            if Path(jtmp).exists():Path(jtmp).unlink()
        return result
    finally:
        if Path(tmp).exists():Path(tmp).unlink()

def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,default=Path(__file__).with_name('isp_modele_pilotage.json'))
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('context');a.add_argument('workbook',type=Path);a.add_argument('--out',type=Path)
    a=sub.add_parser('inspect');a.add_argument('workbook',type=Path);a.add_argument('--sheet');a.add_argument('--cells');a.add_argument('--out',type=Path)
    a=sub.add_parser('resume');a.add_argument('workbook',type=Path);a.add_argument('receipt',type=Path);a.add_argument('--out',type=Path)
    a=sub.add_parser('check');a.add_argument('workbook',type=Path);a.add_argument('plan',type=Path);a.add_argument('--out',type=Path)
    a=sub.add_parser('apply');a.add_argument('workbook',type=Path);a.add_argument('plan',type=Path);a.add_argument('output',type=Path)
    args=p.parse_args();wb=None
    try:
        schema=load_schema(args.model);wb=Workbook(args.workbook)
        if args.command=='context':result=context(wb,schema)
        elif args.command=='inspect':result=inspect(wb,schema,args.sheet,args.cells)
        elif args.command=='resume':result=resume(wb,schema,json.loads(args.receipt.read_text(encoding='utf-8-sig')))
        else:
            plan=json.loads(args.plan.read_text(encoding='utf-8'))
            if args.command=='check':result={'valid':True,'source_sha256':wb.hash,'changes':prepare_plan(wb,schema,plan),'native_calculation':'NOT_EXECUTED'}
            else:result=apply(wb,schema,plan,args.output)
        if getattr(args,'out',None):write_json_exclusive(args.out,result,[args.workbook,args.model,Path(__file__)]+([args.plan] if hasattr(args,'plan') else [])+([args.receipt] if hasattr(args,'receipt') else []))
        else:print(json.dumps(result,ensure_ascii=False,indent=2))
    except (Refusal,KeyError,ValueError,OSError,ET.ParseError,zipfile.BadZipFile) as e:
        print(json.dumps({'status':'REFUSÉ','reason':str(e),'no_authorized_output':True},ensure_ascii=False),file=sys.stderr)
        return 2
    finally:
        if wb:wb.close()
    return 0

if __name__=='__main__':sys.exit(main())
