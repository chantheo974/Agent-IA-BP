"""One immutable snapshot for four formats and controlled Excel round trips."""
from __future__ import annotations
import datetime as dt
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from xml.etree import ElementTree as ET

from .storage import atomic_json, canonical, confined, digest, now, uid
from .vendor import input_engine as core

IDENTITY='docProps/custom.xml'
PROPERTY_NAME='TCA_BP_Export'
CUSTOM_NS='http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
VARIANT_NS='http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
PACKAGE_NS='http://schemas.openxmlformats.org/package/2006/relationships'
TYPE_NS='http://schemas.openxmlformats.org/package/2006/content-types'

def identified_copy(source,exported,identity):
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(exported,'w',compression=zipfile.ZIP_DEFLATED) as dst:
        props=ET.fromstring(src.read(IDENTITY)) if IDENTITY in src.namelist() else ET.Element('{'+CUSTOM_NS+'}Properties')
        for prop in list(props):
            if prop.get('name')==PROPERTY_NAME: props.remove(prop)
        pid=max((int(p.get('pid','1')) for p in props),default=1)+1
        prop=ET.SubElement(props,'{'+CUSTOM_NS+'}property',{'fmtid':'{D5CDD505-2E9C-101B-9397-08002B2CF9AE}','pid':str(pid),'name':PROPERTY_NAME})
        ET.SubElement(prop,'{'+VARIANT_NS+'}lpwstr').text=canonical(identity)
        content=ET.fromstring(src.read('[Content_Types].xml'))
        if not any(c.get('PartName')=='/'+IDENTITY for c in content):
            ET.SubElement(content,'{'+TYPE_NS+'}Override',{'PartName':'/'+IDENTITY,'ContentType':'application/vnd.openxmlformats-officedocument.custom-properties+xml'})
        rels=ET.fromstring(src.read('_rels/.rels'))
        if not any(r.get('Type')==CUSTOM_NS for r in rels):
            ids={r.get('Id') for r in rels}; rid='rIdTCAExport'
            while rid in ids: rid+='1'
            ET.SubElement(rels,'{'+PACKAGE_NS+'}Relationship',{'Id':rid,'Type':CUSTOM_NS,'Target':IDENTITY})
        replacements={IDENTITY:ET.tostring(props,encoding='utf-8',xml_declaration=True),'[Content_Types].xml':ET.tostring(content,encoding='utf-8',xml_declaration=True),'_rels/.rels':ET.tostring(rels,encoding='utf-8',xml_declaration=True)}
        for item in src.infolist():
            if item.filename not in replacements: dst.writestr(item,src.read(item.filename))
        for name,data in replacements.items(): dst.writestr(name,data)

def read_identity(archive):
    if IDENTITY not in archive.namelist(): raise ValueError('Origine inconnue : utiliser un Excel exporté par les Livrables de ce dossier.')
    props=ET.fromstring(archive.read(IDENTITY))
    values=[p.find('{'+VARIANT_NS+'}lpwstr') for p in props if p.get('name')==PROPERTY_NAME]
    if len(values)!=1 or values[0] is None: raise ValueError('Identité de l’export absente ou ambiguë.')
    return json.loads(values[0].text)

def _calendar_questions(d,case_id,questions):
    """Calendar fields remain readable when the guided questionnaire hides a sheet."""
    missing={'model_start_date','active_horizon_years'}-{q.get('field_id') for q in questions}
    if not missing:return questions
    bindings=[b for b in d.bindings(case_id) if b.get('field_id') in missing]
    def read(wb,row):
        states=json.loads(row.get('field_states','{}'))
        found=[]
        for binding in bindings:
            item={k:binding.get(k) for k in ('field_id','label','sheet','cell','value_type','unit')}
            state=states.get(item['sheet']+'!'+item['cell'],{})
            value=wb.value(item['sheet'],item['cell'])
            item.update(value=value,status=state.get('status','HYPOTHESE' if value is not None else 'NON_RENSEIGNE'),
                        evidence_id=state.get('evidence'))
            found.append(item)
        return found
    return [*questions,*d.work._read(case_id,read)]

def _report_calendar(profile, questions, date_system, series, annual_metrics):
    """The exported calendar belongs to the calculated revision, not a pending profile."""
    fields={}
    for identifier in ('model_start_date','active_horizon_years'):
        matches=[q for q in questions if q.get('field_id')==identifier]
        if len(matches)!=1:
            raise ValueError('Calendrier du classeur absent ou ambigu : '+identifier)
        fields[identifier]=matches[0]
    years=fields['active_horizon_years'].get('value')
    if type(years) not in (int,float) or not 1<=years<=10 or int(years)!=years:
        raise ValueError('Horizon calculé entier de 1 à 10 ans requis pour les livrables.')
    raw=fields['model_start_date'].get('value')
    try:
        if isinstance(raw,str):
            start=dt.date.fromisoformat(raw)
            if raw!=start.isoformat():raise ValueError()
        elif type(raw) in (int,float) and date_system in (1900,1904):
            if raw<0 or int(raw)!=raw or (date_system==1900 and raw in (0,60)):
                raise ValueError()
            epoch=dt.date(1904,1,1) if date_system==1904 else dt.date(1899,12,30)
            start=epoch+dt.timedelta(days=int(raw)+(1 if date_system==1900 and 0<raw<60 else 0))
        else:raise ValueError()
    except (ValueError,OverflowError):
        raise ValueError('Date de début du classeur invalide ; vérifier le calendrier avant les livrables.') from None
    years=int(years)
    expected_periods=[f'{year:04d}-{month:02d}' for year in range(start.year,start.year+years) for month in range(1,13)]
    annual_periods=sorted({str(m.get('period')) for m in annual_metrics})
    if (not series or any(s.get('categories')!=expected_periods for s in series)
            or annual_periods!=[str(start.year+i) for i in range(years)]):
        raise ValueError('Le calendrier des résultats diffère de celui du classeur ; vérifier et recalculer la révision.')
    warnings=[]
    if any(profile.get(k)!=v for k,v in (('start_year',start.year),('years',years))):
        warnings.append(f'Le calendrier du profil diffère de la révision calculée. Ce rapport utilise les années {start.year}–{start.year+years-1} du classeur ; le profil enregistré reste inchangé.')
    effective={**profile,'start_year':start.year,'years':years}
    calendar={'start_date':start.isoformat(),'start_year':start.year,'years':years,
              'periods':expected_periods,'source_fields':[fields[k] for k in fields]}
    return effective,calendar,warnings

def build_report(d,case_id,payload,progress):
    from .decision_reports import generate_reports
    from .decision_model import read_series,read_annual_metrics,scenario_list
    with d.store.case_lock(case_id):
        row=d.check_revision(case_id,payload.get('expected_revision'))
        source=d.app._workbook(row)
        case=d.app.get_case(case_id)
        if not case.get('outputs_current'):
            raise ValueError('Recalculer et qualifier cette révision avant de générer les livrables chiffrés.')
        report_id=uid('report_')
        folder=d.store.case_dir(case_id)/'livrables'/report_id
        folder.mkdir(parents=True,exist_ok=False)
        metrics=d.metrics(case_id)
        snapshot={'id':report_id,'title':row['name'],'as_of':now(),'case_id':case_id,'revision':row['revision'],'workbook_sha256':row['sha256'],
                  'profile':d.profile(case_id),'metrics':metrics,'annual_metrics':read_annual_metrics(d,case_id),'series':read_series(d,case_id),
                  'scenarios':[{'name':s['name'],'case_id':s['case_id'],'metrics':d.metrics(s['case_id']),'annual_metrics':read_annual_metrics(d,s['case_id'])} for s in scenario_list(d,case_id)],
                  'capital':d.latest(case_id,'capitalization',{}).get('result',{}),
                  'sources':[{'id':s['id'],'label':s['title'],'sha256':s['sha256']} for s in case['sources']],
                  'limitations':[m['label']+' : à compléter' for m in metrics if m['value'] is None
                                 and not (m.get('id')=='cash_break_date' and m.get('status')=='CALCULE')]}
        from .decision_actuals import actuals_view
        snapshot['actuals']=actuals_view(d,case_id)
        with zipfile.ZipFile(source) as archive:
            properties=ET.fromstring(archive.read('xl/workbook.xml')).find('{'+core.NS+'}workbookPr')
            snapshot['excel_date_system']=1904 if properties is not None and properties.get('date1904') in ('1','true') else 1900
        questions=d.questionnaire(case_id)['questions']
        snapshot['hypotheses']=[{k:q.get(k) for k in ('field_id','label','sheet','cell','value','value_type','unit','status','evidence_id','required')} for q in questions if q.get('value') is not None or q.get('required')]
        snapshot['entered_profile']=snapshot['profile']
        snapshot['profile'],snapshot['calendar'],calendar_warnings=_report_calendar(
            snapshot['entered_profile'],_calendar_questions(d,case_id,questions),snapshot['excel_date_system'],snapshot['series'],snapshot['annual_metrics'])
        snapshot['limitations'].extend(calendar_warnings)
        snapshot['sensitivities']=d.objects(case_id,'sensitivity')
        atomic_json(folder/'snapshot.json',snapshot)
        progress({'message':'Génération des quatre livrables depuis le même instantané.'})
        generated=generate_reports(snapshot,folder)
        exported=folder/'TCA_BP.xlsm'
        identity={'format':'TCA_BP_EXPORT_1','report_id':report_id,'case_id':case_id,'revision':row['revision'],'workbook_sha256':row['sha256'],'snapshot_sha256':generated['snapshot_sha256']}
        # Preserve every original package member, including VBA. The identity is
        # an additional non-executable part, bound to the server's export receipt.
        identified_copy(source,exported,identity)
        files={'xlsm':exported,**{key:Path(generated[key]) for key in ('pdf','docx','pptx')}}
        record={'snapshot':str((folder/'snapshot.json').relative_to(d.store.case_dir(case_id))),
                'snapshot_sha256':digest(folder/'snapshot.json'),'identity':identity,'source_workbook':row['workbook'],
                'formats':list(files),'files':{k:{'path':str(v.relative_to(d.store.case_dir(case_id))),'sha256':digest(v)} for k,v in files.items()},
                'warnings':snapshot['limitations']}
        with d.store.connection() as db:
            d.work._snapshot_version(row,db)
            result=d.save(case_id,'report',record,status='READY',object_id=report_id,db=db)
        return result

def report_file(d,case_id,report_id,format):
    report=d.get(case_id,report_id,'report')
    if format=='snapshot':
        item={'path':report['snapshot'],'sha256':report['snapshot_sha256']}
    else:
        if format not in report.get('files',{}): raise ValueError('Format inconnu ou livrable incomplet.')
        item=report['files'][format]
    path=confined(d.store.case_dir(case_id),item['path'])
    if not path.is_file() or digest(path)!=item['sha256']: raise ValueError('Le livrable a changé depuis sa génération.')
    return path

def _signature(wb):
    """Formula/structure fingerprints exclude cached results and input values."""
    result={}
    for sheet in wb.sheets:
        name=sheet if isinstance(sheet,str) else sheet['name']
        root,cells=wb.sheet(name)[:2]
        formulas={}
        for address,cell in cells.items():
            f=cell.find('m:f',core.N)
            if f is None: continue
            attrs={k:v for k,v in f.attrib.items() if k not in ('ca','aca')}
            if f.get('t') in (None,'normal','shared'):
                attrs={k:v for k,v in attrs.items() if k not in ('si','ref','t')}
            formulas[address]=(wb.formula(name,address),attrs)
        structure=[]
        for tag in ('mergeCells','dataValidations','sheetProtection','autoFilter','tableParts','drawing','legacyDrawing','cols'):
            node=root.find('m:'+tag,core.N)
            if tag=='mergeCells' and node is not None:
                structure.append((tag,sorted(c.get('ref') for c in node)))
            else: structure.append((tag,core.canonical_xml(node)))
        result[name]={'formulas':formulas,'structure':structure,'rows':[r.get('r') for r in root.findall('m:sheetData/m:row',core.N)]}
    return {'sheets':result,'order':list(wb.sheets),'date1904':wb.date1904,
            'defined_names':core.canonical_xml(wb.wb.find('m:definedNames',core.N)),
            'workbook_protection':core.canonical_xml(wb.wb.find('m:workbookProtection',core.N)),
            'external_references':core.canonical_xml(wb.wb.find('m:externalReferences',core.N))}

def _date_literal(wb,sheet,cell,value):
    element=wb.sheet(sheet)[1].get(cell)
    kind=element.get('t','n') if element is not None else 'n'
    return kind,element.findtext('m:v',namespaces=core.N) if kind=='n' and element is not None else value


def _import_date(wb,sheet,cell,value):
    """Convert a date input to the ISO contract, without rounding an Excel time."""
    if value is None: return None
    location=f'{sheet}!{cell}'
    kind,literal=_date_literal(wb,sheet,cell,value)
    minimum,maximum=dt.date(1900,3,1),dt.date(2100,12,31)
    if kind=='n':
        try: serial=Decimal(literal)
        except (InvalidOperation,TypeError): raise ValueError(f'Date Excel invalide : {location}.') from None
        if not serial.is_finite() or serial!=serial.to_integral_value():
            raise ValueError(f'Date Excel entière requise, sans fraction de journée : {location}.')
        if not wb.date1904 and serial==60:
            raise ValueError(f'Date inexistante : le 29 février 1900 Excel ({location}).')
        epoch=dt.date(1904,1,1) if wb.date1904 else dt.date(1899,12,30)
        if not (minimum-epoch).days<=serial<=(maximum-epoch).days:
            raise ValueError(f'Date hors bornes prises en charge (1900-03-01 à 2100-12-31) : {location}.')
        date=epoch+dt.timedelta(days=int(serial))
    elif kind in ('s','inlineStr','str','d') and isinstance(value,str):
        try: date=dt.date.fromisoformat(value)
        except ValueError: raise ValueError(f'Date ISO YYYY-MM-DD valide requise : {location}.') from None
        if value!=date.isoformat(): raise ValueError(f'Date ISO YYYY-MM-DD requise : {location}.')
    else: raise ValueError(f'Date Excel ou ISO requise : {location}.')
    if not minimum<=date<=maximum:
        raise ValueError(f'Date hors bornes prises en charge (1900-03-01 à 2100-12-31) : {location}.')
    return date.isoformat()


def _calculated_output_cells(wb):
    """Only bounded, anchored OOXML array/dataTable result cells are caches.

    Formula attributes (including ref/r1/r2) are checked by _signature first.
    Inputs, table axes and anchors never acquire an exemption from this helper.
    """
    result={}
    for sheet in wb.sheets:
        cells=wb.sheet(sheet)[1]; outputs=set(); protected=set()
        for anchor,element in cells.items():
            formula=element.find('m:f',core.N)
            if formula is None or formula.get('t') not in ('array','dataTable'): continue
            reference=formula.get('ref','')
            if ':' not in reference: continue  # Single-cell formulas are handled normally.
            try:
                first,last=reference.split(':')
                _,left,top=core.coord(first); _,right,bottom=core.coord(last)
                _,column,row=core.coord(anchor)
                if not (1<=left<=right<=16384 and 1<=top<=bottom<=1048576): continue
                if (left,top)!=(column,row) or (right-left+1)*(bottom-top+1)>20000: continue
                if formula.get('t')=='dataTable':
                    flags=('dt2D','dtr','del1','del2')
                    if any(formula.get(flag,'0') not in ('0','1','false','true') for flag in flags): continue
                    if any(formula.get(flag) in ('1','true') for flag in ('del1','del2')): continue
                    keys=('r1','r2') if formula.get('dt2D') in ('1','true') else ('r1',)
                    drivers=set()
                    for key in keys:
                        _,col,r=core.coord(formula.get(key,''))
                        if not (1<=col<=16384 and 1<=r<=1048576): raise ValueError('Invalid table driver')
                        drivers.add(core.colname(col)+str(r))
                    protected.update(drivers)
                    # Substitution values and their result formulas border the
                    # output rectangle; protect them even if another ref overlaps.
                    if top>1: protected.update(core.colname(col)+str(top-1) for col in range(left,right+1))
                    if left>1: protected.update(core.colname(left-1)+str(r) for r in range(top,bottom+1))
                elif not (formula.text or '').strip(): continue
            except (ValueError,TypeError): continue
            protected.add(anchor)
            outputs.update(core.colname(col)+str(r) for r in range(top,bottom+1) for col in range(left,right+1))
        result[sheet]=outputs-protected
    return result


def roundtrip(d,case_id,path,expected_revision=None):
    row=d.check_revision(case_id,expected_revision)
    from .decision_documents import _zip
    if path.stat().st_size>50*1024*1024: raise ValueError('Classeur trop volumineux.')
    with _zip(path.read_bytes()) as archive:
        identity=read_identity(archive)
    if identity.get('case_id')!=case_id: raise ValueError('Cet Excel provient d’un autre dossier.')
    report=d.get(case_id,identity.get('report_id'),'report')
    if identity!=report.get('identity'): raise ValueError('L’identité ou la révision de cet export a été modifiée.')
    if identity['revision']!=row['revision'] or identity['workbook_sha256']!=row['sha256']:
        raise ValueError('Cet export est périmé. Repartir de la révision courante pour éviter un conflit.')
    baseline=report_file(d,case_id,report['id'],'xlsm')
    original=core.Workbook(baseline); incoming=core.Workbook(path)
    updates=[]
    try:
        if _signature(original)!=_signature(incoming): raise ValueError('Formule ou structure modifiée : le réimport accepte uniquement les entrées reconnues.')
        allowed={(f['sheet'],f['cell']):f for f in d.bindings(case_id)}
        calculated=_calculated_output_cells(original)
        for name in original.sheets:
            if not isinstance(name,str): name=name['name']
            oldcells=original.sheet(name)[1]; newcells=incoming.sheet(name)[1]
            for cell in set(oldcells)|set(newcells):
                old=original.value(name,cell); new=incoming.value(name,cell)
                spec=allowed.get((name,cell))
                is_date=spec is not None and spec.get('kind',spec.get('value_type'))=='date'
                # Comparing floats alone could hide a fractional date rounded to
                # the original serial. Inspect its exact XML literal as well.
                if old==new and (not is_date or _date_literal(original,name,cell,old)==_date_literal(incoming,name,cell,new)): continue
                elem=oldcells.get(cell)
                if elem is not None and elem.find('m:f',core.N) is not None: continue
                if spec is None and cell in calculated.get(name,set()): continue
                if (name,cell) not in allowed: raise ValueError(f'Entrée non reconnue modifiée : {name}!{cell}.')
                if is_date:
                    new=_import_date(incoming,name,cell,new)
                    try: old=_import_date(original,name,cell,old)
                    except ValueError: pass  # An invalid old entry may be corrected.
                    if old==new: continue
                updates.append({'type':'set_value','sheet':name,'cell':cell,'value':new,'status':'CONFIRME','reason':'Réimport de l’export '+report['id']})
        # Native binary parts cannot be replaced under an input-only operation.
        protected=lambda z:{part for part in z.namelist() if part.startswith(('xl/vba','xl/activeX/','xl/embeddings/','xl/externalLinks/','xl/connections'))}
        if protected(original.z)!=protected(incoming.z): raise ValueError('Un composant natif du classeur a été ajouté ou supprimé.')
        for part in protected(original.z):
            old_binary,new_binary=original.z.read(part),incoming.z.read(part)
            if old_binary==new_binary: continue
            if part=='xl/vbaProject.bin' and all(b.startswith(bytes.fromhex('d0cf11e0a1b11ae1')) for b in (old_binary,new_binary)):
                from .vendor.vba_fingerprint import compatibility_fingerprint
                if compatibility_fingerprint(old_binary)==compatibility_fingerprint(new_binary): continue
            raise ValueError('Un composant natif du classeur a changé.')
    finally:
        original.z.close(); incoming.z.close()
    if not updates: return {'status':'IDENTIQUE','changes':[]}
    source=d.app.add_source(case_id,path=path,title='Excel réimporté — '+report['id'])
    for op in updates: op['evidence_id']=source['id']
    return d.propose(case_id,updates,expected_revision)
