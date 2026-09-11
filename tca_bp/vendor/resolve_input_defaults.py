"""Résolution pure de 8 défauts de saisie CAPEX ; aucun accès/écriture Excel."""
from datetime import date, datetime, timedelta
from calendar import monthrange
from math import isfinite, floor

DEFAULT_COLUMNS=('F','H','J','K','M','N','O','P')
SOFTWARE=('Logiciels de conception et simulation','Logiciels de gestion (PLM, MES, ERP)')

def blank(x):return x is None or x==''
def excel_number(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and isfinite(x)
def excel_n(x):
    if isinstance(x,bool):return int(x)
    return x if excel_number(x) else 0
def numeric_reference(x):return 0 if x is None else x
def excel_round_positive(x):return floor(x+0.5)
def as_date(x):
    if isinstance(x,datetime):return x.date()
    if isinstance(x,date):return x
    if not excel_number(x) or x<=0:raise ValueError('Date Excel numérique invalide')
    # Epoch Excel1900 ; dates de travail2026+, pas le29/02/1900 fictif.
    return date(1899,12,30)+timedelta(days=floor(x))
def last_month_of_lease(acquisition,months):
    d=as_date(acquisition);n=d.year*12+d.month-1+months
    year,month=divmod(n,12);return date(year,month+1,1)-timedelta(days=1)
def resolve_capex_row(row_values, formula_columns, catalog, default_lease_rate):
    """Formula_columns = formules d'origine préalablement vérifiées par le moteur.

    row_values contient des valeurs scalaires (ou des caches que l'on IGNORE pour
    formula_columns). catalog est ordonné [{label,years,rd_share},...]. Aucun
    parsing/eval d'une formule Excel arbitraire n'est autorisé dans cette API.
    Les overrides scalaires déjà approuvés restent dans row_values.
    """
    fs=set(formula_columns)
    if fs-set(DEFAULT_COLUMNS):raise ValueError('Colonne formule non prise en charge')
    v=dict(row_values);c=v.get('C');b=v.get('B');mode=v.get('I')
    hit=next((x for x in catalog if isinstance(c,str) and isinstance(x.get('label'),str) and c.casefold()==x['label'].casefold()),None)
    if 'F'in fs:v['F']=''if blank(c)or hit is None else numeric_reference(hit.get('years'))
    if 'H'in fs:v['H']=''if blank(c)else (0 if v.get('G')=='Non'else (numeric_reference(hit.get('rd_share'))if hit else 0))
    if 'J'in fs:v['J']=''if mode!='Crédit-bail'or excel_n(v.get('F'))==0 else excel_n(v.get('F'))
    if 'K'in fs:v['K']=''if mode!='Crédit-bail'else numeric_reference(default_lease_rate)
    if 'M'in fs:v['M']=''if blank(b)else ('Incorporelle'if c in SOFTWARE else 'Corporelle')
    for col in ['N','O']:
        if col in fs:v[col]=''if blank(b)or mode!='Crédit-bail'else 'Non'
    if 'P'in fs:
        v['P']=''
        j=v.get('J')
        if not blank(b)and mode=='Crédit-bail'and excel_number(j)and j>0 and abs(j*12-excel_round_positive(j*12))<1e-8:
            try:v['P']=last_month_of_lease(v.get('E'),excel_round_positive(j*12)).isoformat()
            except (ValueError,OverflowError,TypeError):pass
    return v

def validate_capex_local(v,catalog):
    """Garde métier minimale de la saisie, distincte du diagnostic Excel global."""
    issues=[]
    if blank(v.get('B')):
        return ['orphan_or_missing_title']if any(not blank(v.get(c))for c in 'CDEGI')else []
    if v.get('C')not in [x['label']for x in catalog]:issues.append('unknown_capex_type')
    for c in ['D','F']:
        if not excel_number(v.get(c))or v[c]<=0:issues.append(c+'_must_be_positive_number')
    try:as_date(v.get('E'))
    except (ValueError,OverflowError,TypeError):issues.append('invalid_acquisition_date')
    if v.get('G')not in ['Oui','Non']:issues.append('rd_yes_no_required')
    h=v.get('H')
    if not excel_number(h)or not 0<=h<=1:issues.append('rd_share_0_1_required')
    elif v.get('G')=='Non'and h!=0:issues.append('rd_non_requires_zero')
    elif v.get('G')=='Oui'and h<=0:issues.append('rd_oui_requires_positive')
    if v.get('I')not in ['Cash','Crédit-bail']:issues.append('funding_mode_required')
    if v.get('M')not in ['Corporelle','Incorporelle']:issues.append('asset_nature_required')
    if v.get('I')=='Crédit-bail':
        j=v.get('J');k=v.get('K')
        if not excel_number(j)or j<=0 or abs(j*12-excel_round_positive(j*12))>=1e-8:issues.append('lease_whole_positive_months_required')
        if not excel_number(k)or k<0:issues.append('lease_nonnegative_numeric_rate_required')
        for c in ['N','O']:
            if v.get(c)not in ['Oui','Non']:issues.append(c+'_yes_no_required')
        try:
            end=date.fromisoformat(v['P'])if isinstance(v.get('P'),str)else as_date(v.get('P'))
            if end<as_date(v.get('E')):issues.append('operating_end_before_start')
        except (ValueError,OverflowError,TypeError):issues.append('operating_end_required')
    return issues
