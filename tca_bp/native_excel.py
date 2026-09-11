"""Recalcul sur une nouvelle copie par une instance Excel dédiée, macros désactivées."""
from __future__ import annotations

import json
import hashlib
import math
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

from .storage import atomic_json, digest


def available() -> bool:
    if os.name != "nt":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Excel.Application"):
            return True
    except OSError:
        return False


def _process_helpers():
    # Chargement après initialisation du module : wacc_native importe available.
    # Les workers WACC/sensibilités en cours ne sont ni modifiés ni rechargés.
    from .wacc_native import OwnedExcelProcess, existing_excel_pids
    return OwnedExcelProcess, existing_excel_pids


def workbook_proof(path):
    """Signature sémantique et constantes persistées, hors résultats de tables.

    Le service vérifie en plus le modèle scellé, son catalogue et les protections
    effectives des cellules avant toute adoption. Les cinq constantes WACC ne
    sont pas exclues : un recalcul ordinaire ne peut les écrire.
    """
    from .vendor import input_engine as core
    wb=core.Workbook(Path(path))
    try:
        outputs={}
        for name in wb.sheets:
            cells=set()
            for node in wb.sheet(name)[1].values():
                formula=node.find('m:f',core.N)
                if formula is None or formula.get('t')!='dataTable':continue
                ends=formula.get('ref','').replace('$','').split(':')
                if len(ends)!=2:raise ValueError('Rectangle de table native invalide.')
                _,c1,r1=core.coord(ends[0]);_,c2,r2=core.coord(ends[1])
                if c2<c1 or r2<r1 or (c2-c1+1)*(r2-r1+1)>10000:
                    raise ValueError('Périmètre de table native incompatible avec le recalcul borné.')
                cells.update(core.colname(c)+str(r) for r in range(r1,r2+1) for c in range(c1,c2+1))
            outputs[name]=sorted(cells)
            wb._sheet_cache.pop(name,None)
        schema={'cells':{},'native_outputs':{},'native_table_outputs':outputs}
        signature=wb.semantic_signature(schema)
        constants=hashlib.sha256()
        for name in wb.sheets:
            for address in sorted(wb.sheet(name)[1]):
                if address in outputs[name] or wb.formula(name,address) is not None:continue
                value=wb.value(name,address)
                if value is None:continue
                if isinstance(value,(int,float)) and not isinstance(value,bool):value=core.canonical_number(value)
                constants.update(core.packed([name,address,value]));constants.update(b'\n')
            wb._sheet_cache.pop(name,None)
        return {'constant_input_signature':constants.hexdigest(), 'mechanical_signature':signature['overall'],
                'vba_compatibility_signature':signature['vba'], 'date1904':wb.date1904,
                'formula_count':signature['protected_formula_count'],'table_outputs':outputs}
    finally:wb.close()


def validate_receipt(result, source_sha, output_sha, include_tables, pid):
    expected_tables='RECALCUL_DEMANDE' if include_tables else 'NON_VERIFIEES'
    if (result.get('status')!='RECALCULE' or result.get('method')!='CalculateFullRebuild'
            or result.get('application')!='Microsoft Excel' or not isinstance(result.get('version'),str) or not result['version']
            or result.get('source_sha256')!=source_sha or result.get('output_sha256')!=output_sha
            or result.get('calculation_state')!=0 or type(result.get('calculation_state')) is not int
            or result.get('macros_enabled') is not False or result.get('events_enabled') is not False
            or result.get('iteration_enabled') is not False or result.get('iteration_initial') is not False
            or result.get('source_preserved') is not True or result.get('save_reopen_verified') is not True
            or result.get('owned_process_confirmed') is not True or result.get('dedicated_instance_verified') is not True
            or result.get('links_update_requested') is not False or result.get('wacc_macro')!='NON_EXECUTEE'
            or result.get('sensitivity_tables')!=expected_tables or result.get('economic_validation')!='NON_EFFECTUEE'
            or result.get('include_tables') is not include_tables or result.get('base_cell_writes')!=[]
            or result.get('owned_excel_pid')!=pid or type(result.get('owned_excel_pid')) is not int):
        raise ValueError('Le reçu natif est incomplet ou incompatible avec le recalcul demandé.')


def recalculate(source: Path, output: Path, receipt: Path, *, include_tables: bool = False, timeout: int = 300) -> dict:
    if not isinstance(include_tables,bool):raise ValueError('Le choix de recalcul des tables doit être booléen.')
    if (not isinstance(timeout,(int,float)) or isinstance(timeout,bool) or not math.isfinite(timeout)
            or not 1<=timeout<=3600):raise ValueError('Délai natif requis entre 1 et 3 600 secondes.')
    if not available():
        raise ValueError("Microsoft Excel n'est pas disponible sur ce poste. La copie reste à recalculer.")
    source,output,receipt=(Path(p).resolve() for p in (source,output,receipt))
    if (len({source,output,receipt})!=3 or output.exists() or receipt.exists()
            or source.suffix.lower()!='.xlsm' or output.suffix.lower()!='.xlsm'):
        raise ValueError("Le recalcul exige une nouvelle destination, sans remplacer une version.")
    source_sha=digest(source)
    before=workbook_proof(source)
    if digest(source)!=source_sha:raise ValueError('Source modifiée pendant le précontrôle natif.')
    script = Path(__file__).with_name("recalculate.ps1")
    windows = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    ps_home = windows / "System32" / "WindowsPowerShell" / "v1.0"
    args = [str(ps_home / "powershell.exe"), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script),
            "-InputPath", str(source), "-OutputPath", str(output), "-ReceiptPath", str(receipt),
            "-SourceSha256", source_sha, "-TimeoutSeconds", str(timeout)]
    if include_tables:
        args.append("-IncludeTables")
    # Ne pas transmettre les modules .NET de PowerShell 7 à Windows PowerShell
    # 5.1, utilisé ici pour COM. Un hôte IDE peut fournir son propre PSModulePath.
    environment = os.environ.copy()
    environment["PSModulePath"] = os.pathsep.join((str(ps_home / "Modules"),
        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "WindowsPowerShell" / "Modules")))
    OwnedExcelProcess,existing_excel_pids=_process_helpers()
    previous=existing_excel_pids()
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,encoding='utf-8',env=environment,
                             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    messages=queue.Queue()
    def reader():
        try:
            for line in process.stdout:
                message=json.loads(line.lstrip('\ufeff'))
                messages.put(message if isinstance(message,dict) else {'event':'error','error':'Message natif invalide.'})
        except (ValueError,OSError) as exc:messages.put({'event':'error','error':str(exc)})
        finally:messages.put({'event':'closed'})
    def drain():
        for _ in process.stderr:pass
    threading.Thread(target=reader,daemon=True).start()
    threading.Thread(target=drain,daemon=True).start()
    started=time.monotonic();owned=None;pid=None;complete=False
    try:
        while True:
            remaining=timeout-(time.monotonic()-started)
            if remaining<=0:raise ValueError('Le recalcul a dépassé son délai maximal ; copie non adoptée.')
            try:message=messages.get(timeout=remaining)
            except queue.Empty as exc:raise ValueError('Le recalcul a dépassé son délai maximal ; copie non adoptée.') from exc
            if time.monotonic()-started>=timeout:raise ValueError('Le recalcul a dépassé son délai maximal ; copie non adoptée.')
            event=message.get('event')
            if event=='owned_process':
                candidate=message.get('pid')
                if (owned is not None or not isinstance(candidate,int) or isinstance(candidate,bool)
                        or candidate<=0 or candidate in previous):
                    raise ValueError('Instance Excel préexistante ou non identifiable : aucune modification autorisée.')
                owned=OwnedExcelProcess(candidate);pid=candidate
                process.stdin.write('{"operation":"ownership_confirmed"}\n');process.stdin.flush()
            elif event=='saved' and owned is not None:break
            elif event=='progress' and owned is not None:continue
            else:raise ValueError(message.get('error','Réponse native inattendue : '+str(event)))
        process.stdin.close()
        try:process.wait(timeout=max(.01,timeout-(time.monotonic()-started)))
        except subprocess.TimeoutExpired as exc:raise ValueError('La fermeture native a dépassé le délai.') from exc
        if process.returncode or not output.is_file() or not receipt.is_file():
            raise ValueError("Excel n'a pas terminé la sauvegarde et la réouverture.")
        result=json.loads(receipt.read_text(encoding='utf-8-sig'))
        output_sha=digest(output)
        validate_receipt(result,source_sha,output_sha,include_tables,pid)
        after=workbook_proof(output)
        if after!=before:raise ValueError('Le recalcul a modifié des entrées, formules ou éléments mécaniques du classeur.')
        if digest(source)!=source_sha or digest(output)!=output_sha:
            raise ValueError('Un fichier a changé pendant la vérification de la sauvegarde.')
        result.update(inputs_unchanged=True,constant_input_signature_before=before['constant_input_signature'],
                      constant_input_signature_after=after['constant_input_signature'],
                      mechanical_signature_before=before['mechanical_signature'],mechanical_signature_after=after['mechanical_signature'],
                      workbook_proof=after,adopted=False,timeout_seconds=timeout,elapsed_seconds=time.monotonic()-started)
        atomic_json(receipt,result)
        complete=True
        return result
    except BaseException as exc:
        atomic_json(receipt.with_name(receipt.stem+'.echec.json'),{'status':'NON_ADOPTE','error':str(exc),
                    'source_sha256':source_sha,'source_preserved':digest(source)==source_sha,'adopted':False,
                    'owned_excel_process_identified':owned is not None,'owned_excel_pid':pid,
                    'output_exists':output.exists()})
        raise
    finally:
        try:
            if not complete and owned:owned.terminate()
            if process.poll() is None:process.kill()
            process.wait(timeout=10)
        finally:
            if owned:owned.close()
