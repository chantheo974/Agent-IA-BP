"""Scellement de variantes réservé au dépôt de développement TCA."""
from __future__ import annotations
import copy
import datetime as dt
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET
from .model_build import dump, formula_references, invalidate_chart
from .vendor import input_engine as core


def reseal_variant(self, workbook: Path, output_dir: Path, model_id: str, expected_changes: list[dict]):
    """Seal an explicit formula-only evolution; never replace a reference.

    The complete package is compared, including input values, cell styles,
    validation, protections and VBA. Shared formula serialization and cached
    formula values alone may differ without representing a rule change.
    """
    self.ensure_built()
    if not isinstance(model_id,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]{2,95}',model_id) or '..' in model_id or model_id==self.model_id:
        raise ValueError('Nouvel identifiant de variante requis.')
    out=Path(output_dir).resolve()
    if out.exists() or out==self.model_dir or out in self.model_dir.parents or self.model_dir in out.parents:
        raise ValueError('La variante exige un nouveau répertoire distinct de la référence.')
    if not isinstance(expected_changes,list) or not 1<=len(expected_changes)<=100:
        raise ValueError('Décrire de 1 à 100 changements explicites de formules.')
    expected={}
    for item in expected_changes:
        if not isinstance(item,dict):raise ValueError('Description de formule invalide.')
        key=(item.get('sheet'),item.get('cell'))
        old,new=item.get('old_formula'),item.get('new_formula')
        if key in expected or not all(isinstance(v,str) and v for v in (*key,old,new)) or old==new:
            raise ValueError('Changement incomplet, dupliqué ou sans effet.')
        if len(new)>8192 or new.startswith('=') or re.search(r'\[|\]|(?:WEBSERVICE|HYPERLINK|RTD|DDE|CALL|REGISTER|EXEC)\s*\(',new,re.I):
            raise ValueError('Formule externe ou non autorisée dans une variante.')
        core.coord(key[1]);expected[key]=(old,new)
    before=self._open(self.template_path);after=None
    try:
        after=core.Workbook(Path(workbook))
        if list(before.sheets)!=list(after.sheets) or before.date1904!=after.date1904:
            raise ValueError('Structure ou calendrier technique modifié hors proposition.')
        observed={};sheet_parts={s['part'] for s in before.sheets.values()}
        if set(before.z.namelist())!=set(after.z.namelist()):raise ValueError('Les composants du classeur ont changé hors proposition.')
        for sheet in before.sheets:
            br,bc,_=before.sheet(sheet);ar,ac,_=after.sheet(sheet)
            if set(bc)!=set(ac):raise ValueError('Ajout ou suppression de cellule hors proposition : '+sheet)
            # Normalize formula nodes in copies; every other XML feature is
            # compared semantically so styles and inputs cannot be smuggled.
            left=copy.deepcopy(br);right=copy.deepcopy(ar)
            for tree,wb in ((left,before),(right,after)):
                for node in tree.findall('m:sheetData/m:row/m:c',core.N):
                    addr=node.get('r');f=node.find('m:f',core.N)
                    if f is not None:
                        if f.get('t') in (None,'normal','shared'):
                            f.attrib={k:v for k,v in f.attrib.items() if k not in ('t','si','ref','ca','aca')}
                        f.text='FORMULA'
                        for tag in ('v','is'):
                            value=node.find('m:'+tag,core.N)
                            if value is not None:node.remove(value)
                        node.attrib.pop('t',None)
            if core.canonical_xml(left)!=core.canonical_xml(right):raise ValueError('Valeur, style ou structure modifiée hors formule : '+sheet)
            for addr in bc:
                old,new=before.formula(sheet,addr),after.formula(sheet,addr)
                if old!=new:
                    if old is None or new is None:raise ValueError('Conversion entrée/formule hors de ce parcours.')
                    observed[sheet,addr]=(old,new)
            before._sheet_cache.pop(sheet,None);after._sheet_cache.pop(sheet,None)
        if observed!=expected:raise ValueError('Les différences de formules ne correspondent pas exactement à la proposition.')
        for name in before.z.namelist():
            if name in sheet_parts or name=='xl/calcChain.xml':continue
            a,b=before.z.read(name),after.z.read(name)
            if name=='xl/workbook.xml':
                roots=[ET.fromstring(x) for x in (a,b)]
                for root in roots:
                    node=root.find('m:calcPr',core.N)
                    if node is not None:root.remove(node)
                same=core.canonical_xml(roots[0])==core.canonical_xml(roots[1])
            elif name.startswith('xl/charts/') and name.endswith('.xml'):
                same=invalidate_chart(a)==invalidate_chart(b)
            else:same=a==b
            if not same:raise ValueError('Composant modifié hors proposition : '+name)
        schema=copy.deepcopy(self.schema)
        schema.update(model_id=model_id,source_model_id=self.model_id,source_template_sha256=before.hash,
                      qualification_status='EXPERIMENTALE',template_sha256=after.hash)
        for (sheet,addr),(_,new) in observed.items():
            if addr in schema['cells'].get(sheet,{}):schema['cells'][sheet][addr]['default_formula']=new
        schema['signature']=after.semantic_signature(schema)
        core.verify_model(after,schema)
        if core.sha(before.path.read_bytes())!=before.hash or core.sha(after.path.read_bytes())!=after.hash:
            raise ValueError('Un classeur a changé pendant le scellement.')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.mkdir(exist_ok=False)
        template=out/self.template_path.name
        with template.open('xb') as handle:handle.write(after.bytes)
        dump(out/'modele.json',schema);dump(out/'catalogue_champs.json',schema['fields'])
        graph=json.loads((self.model_dir/'graphe_dependances.json').read_text(encoding='utf-8'))
        for cell in graph['cells']:
            key=(cell['sheet'],cell['cell'])
            if key in observed:
                new=observed[key][1];cell['formula_sha256']=core.sha(new.encode())
                cell['references']=formula_references(new,cell['sheet'])
                named={n['name'] for n in graph.get('defined_names',[]) if 'name' in n}
                cell['defined_names']=sorted(set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9.]*\b',new))&named)
        # Add new explicit dependencies conservatively; retaining a previous
        # edge can overestimate impact, never conceal a downstream sheet.
        for (sheet,_),(_,new) in observed.items():
            for quoted,plain in re.findall(r"(?:'((?:[^']|'')+)'|([A-Za-z_][\w ]*))!",new):
                dep=(quoted or plain).replace("''", "'")
                if dep in before.sheets and dep not in graph['sheets'][sheet]:graph['sheets'][sheet].append(dep)
        graph['model_id']=model_id;graph['source_model_id']=self.model_id
        graph.setdefault('limits',[]).append('Variant graph retains previous edges conservatively.')
        dump(out/'graphe_dependances.json',graph)
        for name in ('classification_cellules.json','migrations.json'):
            source=self.model_dir/name
            if source.is_file():(out/name).write_bytes(source.read_bytes())
        counts=copy.deepcopy(self._receipt['counts']);counts['protected_formulas']=schema['signature']['protected_formula_count']
        receipt={'schema':'tca-bp-build/v1','model_id':model_id,'source_model_id':self.model_id,
                 'source_template_sha256':before.hash,'template_path':str(template),'schema_path':str(out/'modele.json'),
                 'template_sha256':after.hash,'schema_sha256':core.sha((out/'modele.json').read_bytes()),'counts':counts,
                 'qualification_status':'EXPERIMENTALE','native_calculation':'NOT_EXECUTED','financial_results_status':'UNAVAILABLE',
                 'exact_formula_changes':len(observed),'source_unchanged':True,
                 'created_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
        dump(out/'build_receipt.json',receipt)
        return receipt
    except (OSError,KeyError,TypeError,zipfile.BadZipFile,ET.ParseError) as exc:
        raise ValueError('Scellement refusé : '+str(exc)) from exc
    finally:
        before.close()
        if after:after.close()
