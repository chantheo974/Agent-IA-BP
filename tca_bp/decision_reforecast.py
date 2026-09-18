"""Propose sourced monthly actuals and a bounded reforecast on managed sheets.

Version 2 adds an explicit journal of net corrections and annual balance
controls. Original model formulas and immutable budget remain untouched. Every
operation uses the shared draft -> native preview -> explicit approval -> apply
workflow; the bridge is tied to the original model used for its checkpoint.
"""
from __future__ import annotations

import calendar
import datetime as dt
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import re

from .web_blocks import compact_setters, expand_operations, MAX_ENVELOPES

ACTUAL_MARKER = "TCA_ACTUALS_MATRIX_V1"
FORECAST_MARKER = "TCA_REFORECAST_MATRIX_V1"
ACTUAL_SHEET = "TCA Réalisé"
FORECAST_SHEET = "TCA Actualisé"
METRICS = [
    ("revenue", "flow", "Chiffre d’affaires"),
    ("receipts", "flow", "Encaissements"),
    ("payments", "flow", "Décaissements"),
    ("cash", "balance", "Trésorerie de clôture"),
    ("assets", "balance", "Total actif"),
    ("liabilities", "balance", "Passifs hors capitaux propres"),
    ("equity", "balance", "Capitaux propres"),
    ("receivables", "balance", "Créances clients"),
    ("payables", "balance", "Dettes fournisseurs"),
    ("inventory", "balance", "Stock"),
    ("debt", "balance", "Dette financière"),
    ("net_income", "flow", "Résultat net mensuel"),
    ("volume", "volume", "Volume")]
MODEL_ROWS = {"cash": 321, "revenue": 88, "receipts": 301, "payments": 320}


def _col(index):
    result = ""
    while index:
        index, char = divmod(index - 1, 26)
        result = chr(65 + char) + result
    return result


def _ref(sheet, cell):
    if not re.fullmatch(r"[A-Z]{1,3}[1-9]\d{0,6}", cell):
        raise ValueError("Adresse de raccord invalide")
    return "'" + sheet.replace("'", "''") + "'!" + cell


def _decimal(value):
    if isinstance(value, bool) or value is None:
        raise ValueError("Montant réalisé numérique requis")
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("Montant réalisé numérique requis") from None
    if not number.is_finite() or not math.isfinite(float(number)):
        raise ValueError("Montant réalisé fini requis")
    return number


def _formula_key(formula):
    # Excel can remove optional apostrophes around simple sheet names. Never
    # rewrite a quoted text literal, an address, an operator or a number.
    parts=re.split(r'("(?:[^"]|"")*")',(formula or '').strip().removeprefix('='))
    return ''.join(part if i%2 else re.sub(r"'([^\W\d]\w*)'!",r'\1!',part) for i,part in enumerate(parts))


def plan_reforecast(actuals: dict, budget: dict, series: list[dict], model_locations: dict,
                    *, existing: dict | None = None, source_id: str | None = None) -> dict:
    """Pure operation planner, also usable by independent deterministic tests.

model_locations maps metric -> YYYY-MM -> (physical sheet, physical cell).
existing maps managed sheet name -> {marker,cells:{A1:{value,formula}}}; names
may have been renamed, provided the owning marker remains in A1. No new formula
replaces an existing model formula. No default zero fills an absent actual.
"""
    try:
        cutoff_date = dt.date.fromisoformat(actuals.get("cutoff", ""))
    except (ValueError, TypeError):
        raise ValueError("Un réalisé validé avec un arrêté mensuel est requis") from None
    if cutoff_date.day != calendar.monthrange(cutoff_date.year, cutoff_date.month)[1]:
        raise ValueError("L’arrêté doit être le dernier jour du mois")
    cutoff = cutoff_date.strftime("%Y-%m")
    if not budget.get("source_sha256") or not budget.get("series"):
        raise ValueError("Figer le budget initial avant de préparer l’actualisé")
    if actuals.get("status", "CONFIRME") != "CONFIRME" or not actuals.get("rows"):
        raise ValueError("Adopter le réalisé avant de préparer son raccord")
    if actuals.get("diagnostics"):
        raise ValueError("Résoudre les diagnostics de conversion du réalisé")
    model_series = {s["id"]: s for s in series if s.get("id") in MODEL_ROWS}
    if set(model_series) != set(MODEL_ROWS):
        raise ValueError("Les quatre séries mensuelles du modèle sont requises")
    periods = model_series["cash"].get("categories", [])
    if (not periods or len(periods) > 120 or len(set(periods)) != len(periods)
            or periods != sorted(periods) or cutoff not in periods
            or any(not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", p) for p in periods)):
        raise ValueError("Calendrier mensuel unique et ordonné, arrêté dans l’horizon de 1 à 120 mois requis")
    for metric, serie in model_series.items():
        if serie.get("categories") != periods or len(serie.get("values", [])) != len(periods):
            raise ValueError("Les calendriers des séries doivent être identiques")
        if serie.get("unit", "EUR") != "EUR":
            raise ValueError("Les séries financières de raccord doivent être en EUR")
        if set(model_locations.get(metric, {})) != set(periods):
            raise ValueError("Cartographie physique incomplète pour " + metric)
    # Validate every source row before any operation is persisted.
    lookup = {}
    kinds = {metric: kind for metric, kind, _ in METRICS}
    for row in actuals["rows"]:
        period, metric, kind, unit = (row.get(k) for k in ("period", "metric", "kind", "unit"))
        if not isinstance(period, str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period) or period > cutoff:
            raise ValueError("Une période réalisée est invalide ou postérieure à l’arrêté")
        if metric not in kinds or kinds[metric] != kind:
            raise ValueError("Poste ou nature non pris en charge par le raccord : " + str(metric))
        if metric != "volume" and unit != "EUR":
            raise ValueError("Raccord financier en EUR uniquement, sans conversion implicite")
        if metric == "volume" and (not isinstance(unit, str) or not unit):
            raise ValueError("Unité de volume requise")
        key = (period, metric)
        if key in lookup:
            raise ValueError("Deux observations visent le même mois et le même poste")
        evidence = row.get("evidence_id") or source_id
        if not isinstance(evidence, str) or not evidence:
            raise ValueError("Une source vérifiée est requise pour chaque observation réalisée")
        lookup[key] = {**row, "number": _decimal(row.get("value")), "evidence_id": evidence}
    all_periods = sorted(set(periods) | {p for p, _ in lookup})
    if len(all_periods) > 240:
        raise ValueError("Historique et prévision limités à 240 mois pour ce raccord")
    existing = existing or {}
    def sheet_name(marker, fallback):
        candidates = [name for name, info in existing.items() if info.get("marker") == marker]
        if len(candidates) > 1:
            raise ValueError("Plusieurs feuilles portent la même identité de raccord")
        if candidates:
            return candidates[0]
        if fallback in existing:
            raise ValueError("La feuille " + fallback + " existe sans identité de raccord reconnue")
        return fallback
    actual_name = sheet_name(ACTUAL_MARKER, ACTUAL_SHEET)
    forecast_name = sheet_name(FORECAST_MARKER, FORECAST_SHEET)
    first_source = source_id or next(iter(lookup.values()))["evidence_id"]
    if not isinstance(first_source, str) or not first_source:
        raise ValueError("Source de préparation requise")
    operations, targets = [], set()
    for name, role in ((actual_name, "Réalisé mensuel validé avec provenance documentaire et distinction flux et soldes"),
                       (forecast_name, "Raccord mensuel au réalisé et aux formules courantes du modèle, bilan futur non reconstruit")):
        if name not in existing:
            operations.append({"type": "add_sheet", "name": name, "role": role,
                               "evidence_id": first_source, "reason": "Préparation du raccord au réalisé"})
    def write(sheet, cell, value, *, formula=False, evidence=None):
        targets.add((sheet, cell))
        operations.append({"type": "set_formula" if formula else "set_value", "sheet": sheet, "cell": cell,
                           "formula" if formula else "value": value, "evidence_id": evidence or first_source,
                           "reason": "Raccord mensuel explicite au réalisé validé"})
    actual_row = {metric: index + 6 for index, (metric, _, _) in enumerate(METRICS)}
    actual_col = {period: _col(index + 4) for index, period in enumerate(all_periods)}
    actual_hash = hashlib.sha256(json.dumps(actuals["rows"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    for sheet, marker in ((actual_name, ACTUAL_MARKER), (forecast_name, FORECAST_MARKER)):
        write(sheet, "A1", marker)
        write(sheet, "A2", "Arrêté")
        write(sheet, "B2", cutoff_date.isoformat())
        write(sheet, "A3", "Empreinte du réalisé" if sheet == actual_name else "Empreinte du budget initial")
        write(sheet, "B3", actual_hash if sheet == actual_name else budget["source_sha256"])
        write(sheet, "A4", "Les blancs restent absents. Les soldes ne sont pas des flux." if sheet == actual_name else
              "Raccord de trésorerie seul. Bilan futur et effets des soldes BFR à qualifier.")
        write(sheet, "A5", "Poste")
        write(sheet, "B5", "Nature")
        write(sheet, "C5", "Unité")
    for period, column in actual_col.items():
        write(actual_name, column + "5", period)
    for metric, kind, label in METRICS:
        row = actual_row[metric]
        write(actual_name, "A" + str(row), label)
        write(actual_name, "B" + str(row), kind)
        units = {v["unit"] for (p, m), v in lookup.items() if m == metric}
        if len(units) > 1:
            raise ValueError("Plusieurs unités pour le même poste réalisé")
        write(actual_name, "C" + str(row), next(iter(units), "unités" if metric == "volume" else "EUR"))
    for (period, metric), observation in lookup.items():
        write(actual_name, actual_col[period] + str(actual_row[metric]), float(observation["number"]), evidence=observation["evidence_id"])
    diagnostics = []
    for metric in MODEL_ROWS:
        missing = [period for period in periods if period <= cutoff and (period, metric) not in lookup]
        if missing:
            diagnostics.append({"code": "HISTORIQUE_INCOMPLET", "metric": metric, "periods": missing,
                                "message": "Les mois réalisés absents restent #N/A dans l’actualisé."})
    forecast_rows = {"revenue": 6, "receipts": 7, "payments": 8, "cash": 9}
    cutoff_cash = _ref(actual_name, actual_col[cutoff] + str(actual_row["cash"]))
    model_cash_cutoff = _ref(*model_locations["cash"][cutoff])
    for metric, row in forecast_rows.items():
        write(forecast_name, "A" + str(row), next(label for m, _, label in METRICS if m == metric))
        write(forecast_name, "B" + str(row), kinds[metric])
        write(forecast_name, "C" + str(row), "EUR")
        for index, period in enumerate(periods):
            column = _col(index + 4)
            if metric == "revenue":
                write(forecast_name, column + "5", period)
            actual_ref = _ref(actual_name, actual_col[period] + str(actual_row[metric]))
            model_ref = _ref(*model_locations[metric][period])
            if period <= cutoff:
                formula = f"=IF(COUNT({actual_ref})=1,{actual_ref},NA())"
            elif metric == "cash":
                formula = f"=IF(COUNT({cutoff_cash},{model_ref},{model_cash_cutoff})=3,{cutoff_cash}+{model_ref}-{model_cash_cutoff},NA())"
            else:
                formula = f"=IF(COUNT({model_ref})=1,{model_ref},NA())"
            write(forecast_name, column + str(row), formula, formula=True)
    # One accounting equality at the actual cut-off. No favourable future
    # balance or future working-capital settlement is fabricated.
    balance_refs = []
    for index, metric in enumerate(("assets", "liabilities", "equity"), 11):
        write(forecast_name, "A" + str(index), next(label for m, _, label in METRICS if m == metric) + " à l’arrêté")
        reference = _ref(actual_name, actual_col[cutoff] + str(actual_row[metric]))
        write(forecast_name, "B" + str(index), f"=IF(COUNT({reference})=1,{reference},NA())", formula=True)
        balance_refs.append(reference)
    write(forecast_name, "A14", "Contrôle actif moins passifs moins capitaux propres")
    write(forecast_name, "B14", f"=IF(COUNT({','.join(balance_refs)})=3,{balance_refs[0]}-{balance_refs[1]}-{balance_refs[2]},NA())", formula=True)
    balance_values = [lookup.get((cutoff, metric)) for metric in ("assets", "liabilities", "equity")]
    if all(balance_values):
        residual = balance_values[0]["number"] - balance_values[1]["number"] - balance_values[2]["number"]
        balance_status = "EQUILIBRE_ARITHMETIQUE" if abs(residual) <= Decimal("0.01") else "DESEQUILIBRE"
        if balance_status == "DESEQUILIBRE":
            diagnostics.append({"code": "BILAN_DESEQUILIBRE", "difference": str(residual)})
    else:
        residual, balance_status = None, "DONNEES_MANQUANTES"
        diagnostics.append({"code": "BILAN_INCOMPLET", "message": "Actif, passifs hors capitaux propres et capitaux propres requis à l’arrêté."})
    if (cutoff, "cash") not in lookup:
        diagnostics.append({"code": "CASH_ARRETE_MANQUANT", "message": "La trésorerie future reste #N/A jusqu’à une trésorerie réelle sourcée à l’arrêté."})
    diagnostics.append({"code": "BFR_ET_BILAN_FUTUR_NON_RECONSTRUITS",
                        "message": "Le raccord conserve les flux futurs du modèle. Les effets de soldes réels différents sur règlements clients, fournisseurs, stocks, dette et bilan futur restent à modéliser explicitement."})
    for name in (actual_name, forecast_name):
        for cell, value in existing.get(name, {}).get("cells", {}).items():
            if (name, cell) not in targets and (value.get("value") is not None or value.get("formula")):
                write(name, cell, None)
    atomic_count = len(operations)
    if atomic_count > MAX_ENVELOPES:
        operations = compact_setters(operations)
    # A large monthly history is represented by bounded blocks, never truncated
    # or admitted by raising the limit for arbitrary flat operation lists.
    expanded = expand_operations(operations)
    if len(expanded) != atomic_count:
        raise ValueError("La compaction du raccord a changé le nombre d’opérations")
    return {"schema_version": "tca-reforecast/1", "operations": operations,
            "atomic_operation_count": atomic_count, "envelope_count": len(operations),
            "sheets": {"actuals": actual_name, "reforecast": forecast_name}, "cutoff": cutoff_date.isoformat(),
            "actuals_sha256": actual_hash, "budget_sha256": budget["source_sha256"], "diagnostics": diagnostics,
            "balance_at_cutoff": {"status": balance_status, "residual": None if residual is None else str(residual)},
            "forecast_balance_status": "NON_RECONSTRUIT", "cash_method": "REALISE_ARRETE_PLUS_VARIATION_MODELE_FUTURE",
            "financial_validation": "RACCORD_PARTIEL_A_RECALCULER_ET_VALIDER", "applied": False}


def _original_model_basis(workbook):
    """Hash original constants/formulas, excluding caches and managed sheets.

    A changed historical model invalidates the sourced interim checkpoint.
    Native recalculation alone cannot invalidate this basis. Data-table result
    caches are excluded but the table anchor and its formula remain included.
    """
    from .decision_reforecast_bridge import MARKER
    from .vendor import input_engine as core
    digest=hashlib.sha256()
    def record(item):
        digest.update(json.dumps(item,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode('utf8'))
        digest.update(b'\n')
    record(['original-model-basis/1',bool(getattr(workbook,'date1904',False))])
    for sheet in workbook.sheets:
        if workbook.value(sheet,'A1') in (ACTUAL_MARKER,FORECAST_MARKER,MARKER):continue
        record(['sheet',sheet]);cells=workbook.sheet(sheet)[1];table_outputs=set()
        for node in cells.values():
            if not hasattr(node,'find'):continue
            formula=node.find('m:f',core.N)
            if formula is not None and formula.get('t')=='dataTable' and formula.get('ref'):
                ends=formula.get('ref').replace('$','').split(':')
                if len(ends) not in (1,2):raise ValueError('Rectangle de table native invalide')
                _,left,top=core.coord(ends[0]);_,right,bottom=core.coord(ends[-1])
                if (right<left or bottom<top or right>16384 or bottom>1048576
                        or (right-left+1)*(bottom-top+1)>10000):
                    raise ValueError('Rectangle de table native hors périmètre borné')
                table_outputs.update(_col(column)+str(row) for row in range(top,bottom+1) for column in range(left,right+1))
        for address in sorted(cells):
            formula=workbook.formula(sheet,address)
            if formula is not None:
                node=cells[address];f=node.find('m:f',core.N) if hasattr(node,'find') else None
                attributes={k:v for k,v in f.attrib.items() if k not in ('ca','aca')} if f is not None and f.get('t') in ('array','dataTable') else None
                record([sheet,address,'formula',_formula_key(formula),attributes])
            elif address not in table_outputs:
                value=workbook.value(sheet,address)
                if value is None:continue
                kind=type(value).__name__
                if type(value) in (int,float):kind='number';value=core.canonical_number(value)
                record([sheet,address,'constant',kind,value])
    if hasattr(workbook,'wb'):
        for node in workbook.wb.findall('m:definedNames/m:definedName',core.N):
            record(['name',dict(node.attrib),_formula_key(node.text)])
    return digest.hexdigest()


def prepare_reforecast(d, case_id, body) -> dict:
    """Persist a shared web draft. Never creates a preview, approves or applies.

body: expected_revision, optional actuals_id and source_id (fallback evidence).
The caller can later run work.preview and explicit approval on the returned id.
"""
    from .decision_model import read_series, location_resolver
    from .vendor import input_engine as core
    # Decision intents share this reentrant lock. add_operations itself owns
    # the filesystem case transaction lock and checks the exact revision.
    with d.lock:
        row = d.check_revision(case_id, body.get("expected_revision"))
        draft = d.work.draft(case_id)
        if draft.get("operations"):
            raise ValueError("Terminer ou abandonner le brouillon courant avant de préparer le raccord au réalisé")
        actuals = d.latest(case_id, "actuals", {})
        if body.get("actuals_id") and body["actuals_id"] != actuals.get("id"):
            raise ValueError("Le réalisé validé a changé depuis la demande")
        budget = d.latest(case_id, "budget", {})
        fallback = body.get("source_id")
        sources = {r.get("evidence_id") or fallback for r in actuals.get("rows", [])}
        if fallback:
            sources.add(fallback)
        if None in sources or "" in sources:
            raise ValueError("Citer une source pour chaque observation réalisée avant le raccord")
        for source in sources:
            d.source(case_id, source)
        series = read_series(d, case_id)
        engine = d.app.engine_for_case(case_id)
        resolve = location_resolver(engine)
        model_locations = {s["id"]: {period: resolve("Modèle financier", core.colname(20 + i) + str(MODEL_ROWS[s["id"]]))
                          for i, period in enumerate(s["categories"])} for s in series if s.get("id") in MODEL_ROWS}
        def existing_sheets(workbook, ignored):
            from .decision_reforecast_bridge import MARKER, SHEET
            found = {}
            for raw_name in workbook.sheets:
                name = raw_name if isinstance(raw_name, str) else raw_name["name"]
                marker = workbook.value(name, "A1")
                if marker in (ACTUAL_MARKER, FORECAST_MARKER, MARKER) or name in (ACTUAL_SHEET, FORECAST_SHEET, SHEET):
                    cells = workbook.sheet(name)[1]
                    found[name] = {"marker": marker, "cells": {address: {"value": workbook.value(name, address),
                                             "formula": workbook.formula(name, address)} for address in cells}}
            return found
        existing = d.work._read(case_id, existing_sheets)
        plan = plan_reforecast(actuals, budget, series, model_locations, existing=existing, source_id=fallback)
        from .decision_reforecast_bridge import augment_plan, physical_locations
        plan['_model_locations'] = model_locations
        plan = augment_plan(plan, actuals, budget, series, physical_locations(engine, series[0]['categories']),
                            body.get('bridge', {}), existing=existing, source_id=fallback, workbook_sha256=row['sha256'])
        plan['bridge_source_ids']=sorted(set(plan['bridge_source_ids'])|sources)
        plan['original_model_sha256']=d.work._read(case_id,lambda workbook,ignored:_original_model_basis(workbook))
        for source in plan['bridge_source_ids']:
            d.source(case_id, source)
        prepared = d.propose(case_id, plan["operations"], row["revision"])
        receipt = {key: value for key, value in plan.items() if key != "operations"}
        receipt.update(draft_id=prepared["id"], source_revision=row["revision"], source_sha256=row["sha256"], actuals_id=actuals.get("id"))
        saved = d.save(case_id, "reforecast_preparation", receipt, status="DRAFT")
        return {**prepared, "reforecast": {**receipt, "receipt_id": saved["id"]}}


def reforecast_requirements(d, case_id):
    """Read-only UI contract: sources for interim balances, direct December links."""
    from .decision_reforecast_bridge import bridge_diagnostics, physical_locations, BASELINE_FIELDS, SCHEMA
    from .decision_model import read_series
    row=d.check_revision(case_id,None)
    actuals=d.latest(case_id,'actuals',{})
    saved=next(iter(d.objects(case_id,'reforecast_preparation')),{})
    bridge=saved.get('bridge',{})
    series=read_series(d,case_id);periods=series[0]['categories'];cutoff=actuals.get('cutoff','')
    locations=physical_locations(d.app.engine_for_case(case_id),periods)
    baseline=[]
    def linked_value(workbook,ignored):
        values={}
        from .decision_model import location_resolver
        engine=d.app.engine_for_case(case_id)
        resolve=location_resolver(engine)
        year=cutoff[:4];first=int(periods[0][:4]);col=_col(4+int(year)-first)
        def value(sheet,cell):
            sheet,cell=resolve(sheet,cell);result=workbook.value(sheet,cell)
            return result if type(result) in (int,float) and math.isfinite(result) else None
        values['assets']=value('Bilan',col+'4');values['equity']=value('Bilan',col+'25')
        total=value('Bilan',col+'24')
        values['liabilities']=total-values['equity'] if total is not None and values['equity'] is not None else None
        values['net_income_ytd']=value('Compte de Résultat',col+'85')
        return values
    linked=cutoff[5:7]=='12' and cutoff[:4] in locations['annual']
    values=d.work._read(case_id,linked_value) if linked and d.app.get_case(case_id).get('outputs_current') else {}
    for key,label in BASELINE_FIELDS.items():
        entry=bridge.get('baseline_cutoff',{}).get(key,{})
        baseline.append({'id':key,'label':label,'value':values.get(key) if linked else entry.get('value'),
                         'linked':linked,'required':not linked,'evidence_id':entry.get('evidence_id')})
    assessment=bridge_diagnostics(actuals,bridge,periods,row['sha256'])
    return {'schema':SCHEMA,'workbook_sha256':row['sha256'],'cutoff':cutoff,'baseline_fields':baseline,'periods':periods,
            'questions':assessment['questions'],'accounts':assessment['required_accounts'],'bridge':bridge}


def read_reforecast(d,case_id):
    """Read managed caches only; stale, edited or incomplete bridges stay blocked."""
    from .decision_reforecast_bridge import MARKER, _sha
    actuals=d.latest(case_id,'actuals',{});budget=d.latest(case_id,'budget',{})
    candidates=d.objects(case_id,'reforecast_preparation')
    def active_hashes(workbook,ignored):
        return {workbook.value(sheet,'B6') for sheet in workbook.sheets if workbook.value(sheet,'A1')==MARKER}
    active=d.work._read(case_id,active_hashes)
    prepared=next((p for p in candidates if p.get('bridge_sha256') in active),{})
    blocked={'forecast_series':[],'annual_balance':[],'diagnostics':[], 'forecast_status':'A_PREPARER'}
    if not prepared or prepared.get('schema_version')!='tca-reforecast/2':return blocked
    case=d.app.get_case(case_id)
    diagnostics=[]
    if not case.get('outputs_current'):diagnostics.append({'code':'RECALCUL_REQUIS','message':'Recalculer la révision adoptée avant de lire l’actualisé.'})
    qualification=case.get('qualified_availability') or {}
    if any(not qualification.get(scope,{}).get('scenario_ready') for scope in ('CA','COGS','CASH','FISCALITE')):
        diagnostics.append({'code':'MODELE_SOURCE_A_QUALIFIER','message':'Qualifier les hypothèses et résultats CA, COGS, trésorerie et fiscalité du modèle avant d’utiliser le raccord.'})
    if (prepared.get('actuals_sha256')!=_sha(actuals.get('rows',[])) or prepared.get('cutoff')!=actuals.get('cutoff')
            or prepared.get('budget_sha256')!=budget.get('source_sha256')):
        diagnostics.append({'code':'RACCORD_OBSOLETE','message':'Le réalisé, son arrêté ou le budget ont changé. Préparer un nouveau raccord.'})
    if prepared.get('questions'):diagnostics.append({'code':'DONNEES_RACCORD_MANQUANTES','message':'Compléter les décisions et sources du pont avant de préparer une nouvelle version.','questions':prepared['questions']})
    sources=set(prepared.get('bridge_source_ids',[]))|{row.get('evidence_id') for row in actuals.get('rows',[])}
    for source in sources:
        if not source:
            diagnostics.append({'code':'SOURCE_RACCORD_INDISPONIBLE','message':'Une observation réalisée ne possède pas de source identifiable.'});break
        try:d.source(case_id,source)
        except (ValueError,OSError):diagnostics.append({'code':'SOURCE_RACCORD_INDISPONIBLE','message':'Une source du pont est absente ou a changé.'});break
    names=prepared['sheets']; periods=prepared['periods']; years=prepared['annual_years']
    def read(workbook,ignored):
        local=[]
        def num(sheet,cell):
            value=workbook.value(sheet,cell)
            return value if type(value) in (int,float) and math.isfinite(value) else None
        if (any(name not in workbook.sheets for name in names.values())
                or workbook.value(names['bridge'],'A1')!=MARKER):
            return [],[],[{'code':'FEUILLES_RACCORD_ABSENTES','message':'Adopter le brouillon ou préparer à nouveau les feuilles gérées.'}]
        if not prepared.get('original_model_sha256') or prepared['original_model_sha256']!=_original_model_basis(workbook):
            local.append({'code':'MODELE_RACCORD_MODIFIE','message':'Le modèle utilisé pour le checkpoint a changé, ou son empreinte manque. Préparer et valider un nouveau raccord avec les nouvelles hypothèses.'})
        if any(workbook.value(names['bridge'],cell)!=expected for cell,expected in [('B2',prepared['cutoff'][:7]),('B4',prepared['actuals_sha256']),('B5',prepared['budget_sha256']),('B6',prepared['bridge_sha256'])]):
            local.append({'code':'IDENTITE_RACCORD_MODIFIEE','message':'Les identifiants du pont ont changé.'})
        for expected in prepared.get('managed_contract',[]):
            sheet,cell=expected['sheet'],expected['cell']
            if 'formula' in expected:
                valid=_formula_key(workbook.formula(sheet,cell))==_formula_key(expected['formula'])
            else:valid=workbook.formula(sheet,cell) is None and workbook.value(sheet,cell)==expected['value']
            if not valid:
                local.append({'code':'CONTENU_RACCORD_MODIFIE','message':'Une donnée ou formule du pont a changé après sa préparation. Préparer et valider un nouveau raccord.','sheet':sheet,'cell':cell});break
        if num(names['bridge'],'B8')!=1:local.append({'code':'CONTROLE_PONT_NON_VALIDE','message':'Le pont présente une donnée absente, un événement déséquilibré ou un écart terminal non résolu.'})
        forecast=[]
        for metric,row,label in [('revenue',6,'Chiffre d’affaires actualisé'),('receipts',7,'Encaissements actualisés'),('payments',8,'Décaissements actualisés'),('cash',9,'Trésorerie actualisée'),('receivables',16,'Créances clients'),('inventory',17,'Stocks'),('payables',18,'Dettes fournisseurs'),('debt',19,'Dette financière')]:
            values=[num(names['reforecast'],_col(i+4)+str(row)) for i in range(len(periods))]
            forecast.append({'id':metric,'label':label,'unit':'EUR','categories':periods,'values':values,'status':'CACHES_DU_RACCORD'})
            if any(value is None for value in values):local.append({'code':'SERIE_RACCORD_INCOMPLETE','metric':metric,'message':'Des résultats de '+metric+' sont absents ou en erreur.'})
        by_metric={item['id']:item['values'] for item in forecast}
        for i,period in enumerate(periods):
            if i==0 or period<=prepared['cutoff'][:7]:continue
            values=[by_metric['cash'][i],by_metric['cash'][i-1],by_metric['receipts'][i],by_metric['payments'][i]]
            if all(value is not None for value in values) and abs(values[0]-values[1]-values[2]+values[3])>.01:
                local.append({'code':'CONTINUITE_CASH_NON_VALIDEE','period':period,'message':'Les caches de trésorerie ne se raccordent pas aux encaissements et décaissements. Vérifier les flux du modèle et les corrections du pont.'})
        annual=[]
        for i,year in enumerate(years):
            col=_col(i+4)
            row={'period':year,**{key:num(names['reforecast'],col+str(r)) for key,r in [('assets',33),('liabilities',34),('equity',35),('net_income',36),('balance_check',37),('model_balance_check',38)]}}
            annual.append(row)
            if any(row[key] is None for key in row if key!='period') or any(abs(row[key])>.01 for key in ('balance_check','model_balance_check') if row[key] is not None):
                local.append({'code':'BILAN_ANNUEL_NON_VALIDE','period':year,'message':'Le bilan annuel actualisé ou le bilan modèle ne passe pas son contrôle.'})
        return forecast,annual,local
    forecast,annual,local=d.work._read(case_id,read);diagnostics.extend(local)
    status='EXPLICABLE' if not diagnostics else 'A_COMPLETER_OU_RECALCULER'
    # Unqualified numbers are not presented as usable forecast data.
    if diagnostics:
        forecast=[{**s,'values':[None]*len(s['values']),'status':status} for s in forecast]
        annual=[{**r,**{key:None for key in r if key!='period'}} for r in annual]
    else:forecast=[{**s,'status':status} for s in forecast]
    return {'forecast_series':forecast,'annual_balance':annual,'diagnostics':diagnostics,'forecast_status':status,
            'cutoff':prepared['cutoff'],'source_revision':prepared['source_revision'],'bridge_sha256':prepared['bridge_sha256']}
