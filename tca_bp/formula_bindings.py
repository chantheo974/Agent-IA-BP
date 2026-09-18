"""Turn positional INDEX literals into references before geometric edits."""
from __future__ import annotations

import re
from .vendor import input_engine as core
from .web_model_profile import cell_parts, map_between_profiles

_INDEX = re.compile(r"\bINDEX\(\s*(?:(?P<sheet>'(?:[^']|'')+'|[A-Za-z_][\w .]*)!)?"
                    r"(?P<start>\$?[A-Z]{1,3}\$?[1-9]\d*):(?P<end>\$?[A-Z]{1,3}\$?[1-9]\d*)"
                    r"\s*,\s*(?P<row>\d+)\s*,\s*(?P<column>\d+)\s*\)",re.I)


def bind_index_literals(formula, sheet, before, after):
    """Keep existing INDEX targets through insertions inside their source area.

    Only literal A1 rectangular INDEX(array, integer, integer) is rewritten.
    Zero row/column selectors retain Excel's full-row/full-column behavior.
    Each replacement is equivalent before the edit and then follows Excel's
    native reference updates. Quoted string content is never executable text.
    """
    clean=re.sub(r'"(?:[^"]|"")*"',lambda m:' '*len(m[0]),formula)
    edits=[]
    for match in _INDEX.finditer(clean):
        start=cell_parts(match['start']);end=cell_parts(match['end'])
        name=match['sheet'] or sheet
        if name.startswith("'"):name=name[1:-1].replace("''", "'")
        name=next((s['name'] for s in before['sheets'] if s['name'].casefold()==name.casefold()),name)
        row,column=int(match['row']),int(match['column'])
        if row>end[1]-start[1]+1 or column>end[0]-start[0]+1:continue
        try:
            first=map_between_profiles(before,after,name,match['start'])
            target_cell=core.colname(start[0]+max(column-1,0))+str(start[1]+max(row-1,0))
            target=map_between_profiles(before,after,name,target_cell)
        except ValueError:
            continue
        f=cell_parts(first['cell']) if first else None
        t=cell_parts(target['cell']) if target else None
        qualifier="'"+name.replace("'","''")+"'!"
        origin=qualifier+'$'+core.colname(start[0])+'$'+str(start[1])
        destination=qualifier+'$'+core.colname(start[0]+max(column-1,0))+'$'+str(start[1]+max(row-1,0))
        if row and (not f or not t or t[1]-f[1]+1!=row):
            edits.append((match.start('row'),match.end('row'),'ROW('+destination+')-ROW('+origin+')+1'))
        if column and (not f or not t or t[0]-f[0]+1!=column):
            edits.append((match.start('column'),match.end('column'),'COLUMN('+destination+')-COLUMN('+origin+')+1'))
    for start,end,value in sorted(edits,reverse=True):formula=formula[:start]+value+formula[end:]
    return formula


def structural_index_repairs(workbook, before, after):
    result=[]
    # OOXML shared members are read through their expanded logical formula.
    for sheet in workbook.sheets:
        for address,node in workbook.sheet(sheet)[1].items():
            if node.find('m:f',core.N) is None:continue
            formula=workbook.formula(sheet,address)
            if not formula or 'INDEX(' not in formula.upper():continue
            rewritten=bind_index_literals(formula,sheet,before,after)
            if rewritten!=formula:
                result.append({'sheet':sheet,'cell':address,'before':formula,'after':rewritten})
        workbook._sheet_cache.pop(sheet,None)
    return result
