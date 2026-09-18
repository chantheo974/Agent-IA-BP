"""Read-only inventory of the three user supplied accounting references."""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import posixpath

def audit(root,output):
    files=[root/'Nomenclature_PCG_Mapping_Previsionnel.xlsx',root/'nomenclature excel comptabilité.md',root/'nomenclature_pcg.csv']
    result={'sources':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]}
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}; rel='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    sheets={}
    with zipfile.ZipFile(files[0]) as z:
        book=ET.fromstring(z.read('xl/workbook.xml'))
        targets={x.get('Id'):x.get('Target') for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist(): strings=[''.join(t.text or '' for t in x.findall('.//m:t',ns)) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        for sheet in book.findall('m:sheets/m:sheet',ns):
            target=targets[sheet.get('{'+rel+'}id')]; part=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            xml=ET.fromstring(z.read(part)); rows=[]; formulas=[]; errors=[]
            for row in xml.findall('m:sheetData/m:row',ns):
                values={}
                for cell in row.findall('m:c',ns):
                    v=cell.find('m:v',ns); value=v.text if v is not None else None
                    if cell.get('t')=='s' and value is not None: value=strings[int(value)]
                    elif cell.get('t')=='inlineStr': value=''.join(t.text or '' for t in cell.findall('.//m:t',ns))
                    f=cell.find('m:f',ns)
                    if f is not None: formulas.append({'cell':cell.get('r'),'formula':f.text,'cached':value})
                    if cell.get('t')=='e': errors.append({'cell':cell.get('r'),'error':value})
                    if value is not None or f is not None: values[cell.get('r')]=value
                if values: rows.append(values)
            sheets[sheet.get('name')]={'rows':rows,'formulas':formulas,'errors':errors,'dimension':xml.find('m:dimension',ns).get('ref')}
    result['sheets']=sheets
    text=files[2].read_text(encoding='utf-8-sig'); rows=list(csv.DictReader(text.splitlines(),delimiter=';'))
    result['csv']={'columns':list(rows[0]),'rows':rows,'duplicate_accounts':sorted({r['compte'] for r in rows if sum(x['compte']==r['compte'] for x in rows)>1})}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sources':result['sources'],'sheets':{k:{'rows':len(v['rows']),'formulas':len(v['formulas']),'errors':v['errors'],'sample':v['rows'][:9]} for k,v in sheets.items()},'csv_count':len(rows),'duplicate_accounts':result['csv']['duplicate_accounts']},ensure_ascii=False))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('source_dir',type=Path); p.add_argument('output',type=Path); args=p.parse_args(); audit(args.source_dir,args.output)
