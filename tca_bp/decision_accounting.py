"""Versioned suggestions from the user's PCG mapping, never automatic postings."""
from decimal import Decimal,InvalidOperation
import json
from pathlib import Path
import re

REFERENCE=Path(__file__).parent/'resources'/'pcg_reference_20260913.json'
LEGACY_PREFIXES=('675','775','777','79')
MODERN_REVIEW_PREFIXES=('649','657','747','757','7587')

def catalog():
    data=json.loads(REFERENCE.read_text(encoding='utf-8'))
    if data.get('schema')!='tca-pcg-reference/1': raise ValueError('Référentiel comptable incompatible.')
    accounts=data.get('accounts',[])
    if len({a['compte'] for a in accounts})!=len(accounts): raise ValueError('Compte dupliqué dans le référentiel.')
    return data

def suggest(account,balance,year):
    if not isinstance(account,str) or not 2<=len(account)<=60: raise ValueError('Le compte doit être un identifiant texte.')
    if type(year) is not int or not 1900<=year<=2200: raise ValueError('Exercice comptable requis.')
    normalized=re.sub(r'[\s\u00a0\u202f]+','',account).upper()
    if not re.match(r'^\d{2}',normalized): raise ValueError('Numéro de compte non reconnu.')
    try: amount=Decimal(str(balance))
    except InvalidOperation: raise ValueError('Solde numérique requis (débit positif, crédit négatif).')
    if not amount.is_finite(): raise ValueError('Solde fini requis.')
    data=catalog()
    candidates=sorted((a for a in data['accounts'] if normalized.startswith(a['compte'])),key=lambda a:len(a['compte']),reverse=True)
    match=candidates[0] if candidates else None
    warnings=[]
    if year>=2025 and normalized.startswith(LEGACY_PREFIXES+MODERN_REVIEW_PREFIXES):
        warnings.append('REFORME_PCG_CORRESPONDANCE_A_REVOIR')
    if match is None: warnings.append('COMPTE_HORS_REFERENCE')
    poste=(match['poste_solde_debiteur'] if amount>=0 else match['poste_solde_crediteur']) if match else None
    post=next((p for p in data['posts'] if p['code']==poste),None)
    return {'account':account,'normalized_account':normalized,'matched_prefix':match['compte'] if match else None,
            'label':match['libelle'] if match else None,'balance':str(amount),'year':year,
            'post':post,'reference_version':data['version'],'sources':data['sources'],
            'status':'A_REVOIR' if warnings else 'A_CONFIRMER','warnings':warnings,
            'applied':False,'note':'Qualifier le compte et ses auxiliaires à cet arrêté. Cette correspondance ne transforme pas un solde en encaissement ou décaissement.'}
