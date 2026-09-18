"""Résolution WACC locale, sans macro, dans une instance Excel dédiée.

Cette couche produit une copie et un reçu ; seul le service peut les adopter
après vérification du modèle, des entrées et des sources du dossier.
"""
from __future__ import annotations
import ctypes
import csv
import hashlib
from ctypes import wintypes
import json
import math
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

from .native_excel import available
from .storage import atomic_json, canonical, digest
from .wacc_solver import solve


def existing_excel_pids():
    executable = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/tasklist.exe"
    result = subprocess.run([str(executable), "/FI", "IMAGENAME eq EXCEL.EXE", "/FO", "CSV", "/NH"],
                            capture_output=True, timeout=10, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), check=True)
    return {int(row[1]) for row in csv.reader(result.stdout.decode("utf-8", errors="replace").splitlines())
            if len(row) >= 2 and row[0].casefold() == "excel.exe" and row[1].isdigit()}


def native_mapping(profile, kind):
    """Resolve audited logical owners; never infer a replacement for deletion."""
    if profile is None:
        return None
    from .web_model_profile import map_location, map_range, verify_profile, cell_parts
    verify_profile(profile)
    if kind == 'wacc':
        sheet = 'Valorisation'
        addresses = ['D7','D8','D9','D40','D107','D108','D124','D135','D136','D137','D138','D141','D142','D143','D155','D156']
        areas = []
    elif kind == 'sensitivity':
        sheet = 'Sensi Analyses'
        addresses = ['C8','C14','C18','D24','E24','F24','G24','C39','D39','C49']
        addresses += [f'F{row}' for row in range(8,17)] + [f'C{row}' for row in range(25,34)]
        addresses += [f'B{row}' for row in range(40,46)] + ['D49','E49','F49','C50','C51','C52']
        areas = ['D25:G33','C40:D45','D50:F52']
        for area in areas:
            first,last=map(cell_parts,area.split(':'))
            from .vendor.input_engine import colname
            addresses += [colname(col)+str(row) for row in range(first[1],last[1]+1) for col in range(first[0],last[0]+1)]
    else:
        raise ValueError('Protocole natif inconnu.')
    locations={cell:map_location(profile,sheet,cell) for cell in dict.fromkeys(addresses)}
    if any(location is None for location in locations.values()):
        raise ValueError('Un propriétaire du calcul natif a été supprimé. Corriger le profil avant le calcul.')
    sheets={location['sheet'] for location in locations.values()}
    if len(sheets)!=1:
        raise ValueError('Les propriétaires du calcul natif doivent rester sur la même feuille.')
    result={'schema':'tca-native-mapping/1','kind':kind,'profile_sha256':profile['profile_sha256'],
            'sheet':next(iter(sheets)),'cells':{cell:location['cell'] for cell,location in locations.items()},'ranges':{}}
    for area in areas:
        physical=map_range(profile,sheet,area)
        if physical is None:
            raise ValueError('Une table native possède une référence supprimée.')
        first,last=map(cell_parts,area.split(':'))
        a,b=map(cell_parts,physical['range'].split(':'))
        if (last[0]-first[0],last[1]-first[1])!=(b[0]-a[0],b[1]-a[1]):
            raise ValueError('Une insertion ou suppression interne a changé la forme d’une table native. Requalifier sa définition avant cette recette.')
        result['ranges'][area]=physical['range']
    if kind=='wacc':
        result['written_outputs']=[result['cells'][cell] for cell in ('D136','D141','D142','D143','D156')]
    else:
        result['auxiliary']={}
        for name,refs in (('Control',['C59']),('Sensi TCA',['C15']),('Valorisation',['D136','D141','D142','D143','D156'])):
            for cell in refs:
                location=map_location(profile,name,cell)
                if location is None:
                    raise ValueError('Une dépendance native a été supprimée : '+name+'!'+cell)
                result['auxiliary'][name+'!'+cell]=location
    result['mapping_sha256']=hashlib.sha256(canonical(result).encode()).hexdigest()
    return result


def validate_saved_receipt(saved, result, growth, mapping=None):
    finite = lambda x: isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)
    required_numbers = ('candidate', 'calculated', 'residual', 'equity', 'evaluations')
    if any(not finite(saved.get(key)) for key in required_numbers):
        raise ValueError("Sortie numérique WACC invalide dans le reçu.")
    if (saved.get('method') != 'LOCAL_SCALAR_SOLVER' or saved.get('algorithm') != result['algorithm']
            or saved.get('mode') != 'Itération' or saved.get('validity') != 'OK'
            or saved.get('macros_enabled') is not False or saved.get('wacc_macro') != 'NON_EXECUTEE'
            or saved.get('save_reopen_verified') is not True or saved.get('source_preserved') is not True
            or saved.get('global_uniqueness_proven') is not False
            or saved.get('written_outputs') != (mapping['written_outputs'] if mapping else ['D136', 'D141', 'D142', 'D143', 'D156'])
            or saved.get('iteration_enabled') is not False or saved.get('calculation_state') != 0
            or isinstance(saved.get('calculation_state'), bool) or saved['equity'] <= 0
            or saved['candidate'] <= growth + 1e-6 or saved['calculated'] <= growth + 1e-6
            or abs(saved['residual']) > 1e-10
            or abs(saved['calculated'] - saved['candidate'] - saved['residual']) > 1e-12
            or saved['evaluations'] != result['evaluations']
            or any(abs(saved[k] - result[k]) > (0.01 if k == 'equity' else 1e-12)
                   for k in ('candidate', 'calculated', 'residual', 'equity'))):
        raise ValueError("Le reçu WACC est incompatible avec la résolution vérifiée.")
    if mapping and (saved.get('profile_sha256')!=mapping['profile_sha256'] or saved.get('native_mapping_sha256')!=mapping['mapping_sha256']):
        raise ValueError('Le reçu WACC appartient à un autre profil métier ou à une autre cartographie.')


class OwnedExcelProcess:
    """Garder un handle sur le processus dédié empêche toute confusion de PID."""
    def __init__(self, pid):
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
        kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel, self.handle = kernel, kernel.OpenProcess(0x1000 | 0x0001, False, pid)
        if not self.handle:
            raise ValueError("Impossible de superviser le processus Excel dédié.")
        buffer, length = ctypes.create_unicode_buffer(32768), wintypes.DWORD(32768)
        if (not kernel.QueryFullProcessImageNameW(self.handle, 0, buffer, ctypes.byref(length))
                or Path(buffer.value).name.casefold() != "excel.exe"):
            self.close()
            raise ValueError("Le processus fourni n'est pas l'instance Excel attendue.")

    def terminate(self):
        if self.handle:
            self.kernel.TerminateProcess(self.handle, 2)

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def solve_native(source: Path, output: Path, receipt: Path, *, timeout=300, profile=None):
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 1 <= timeout <= 600:
        raise ValueError("Le délai WACC doit être compris entre 1 et 600 secondes.")
    if not available():
        raise ValueError("Excel est requis pour la résolution locale WACC.")
    source, output, receipt = Path(source).resolve(), Path(output).resolve(), Path(receipt).resolve()
    progress_path=receipt.with_name(receipt.stem+'.progress.json')
    if source == output or output.exists() or receipt.exists() or progress_path.exists():
        raise ValueError("La résolution exige une nouvelle copie et un nouveau reçu.")
    source_sha = digest(source)
    mapping=native_mapping(profile,'wacc')
    windows = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    ps_home = windows / "System32/WindowsPowerShell/v1.0"
    environment = os.environ.copy()
    environment["PSModulePath"] = os.pathsep.join((str(ps_home / "Modules"),
        str(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "WindowsPowerShell/Modules")))
    args = [str(ps_home / "powershell.exe"), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
            str(Path(__file__).with_name("wacc_worker.ps1")), "-InputPath", str(source), "-OutputPath", str(output), "-ReceiptPath", str(receipt)]
    if mapping:
        mapping_path=receipt.with_suffix('.mapping.json')
        if mapping_path.exists():
            raise ValueError('Le reçu de cartographie native doit être neuf.')
        atomic_json(mapping_path,mapping)
        args += ['-MappingPath',str(mapping_path),'-MappingSha256',digest(mapping_path)]
    previous_pids = existing_excel_pids()
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", env=environment,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    messages = queue.Queue()
    errors = []
    def read_lines():
        try:
            for line in process.stdout:
                messages.put(json.loads(line.lstrip('\ufeff')))
        except (ValueError, OSError) as error:
            messages.put({"event": "error", "error": str(error)})
        finally:
            messages.put({"event": "closed"})
    def read_errors():
        for line in process.stderr:
            errors.append(line)
            if len(errors) > 20:
                del errors[0]
    threading.Thread(target=read_lines, daemon=True).start()
    threading.Thread(target=read_errors, daemon=True).start()
    deadline = time.monotonic() + timeout
    started = time.monotonic()
    observations=[]
    progress={'schema':'tca-wacc-progress/1','source_sha256':source_sha,'adopted':False}
    def record_progress(phase,**details):
        progress.update(phase=phase,elapsed_seconds=time.monotonic()-started,observations=observations,**details)
        atomic_json(progress_path,progress)
    owned = None
    complete = False

    def receive(event):
        nonlocal owned
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("Résolution WACC interrompue à son délai maximal.")
            try:
                message = messages.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty as error:
                raise TimeoutError("Résolution WACC interrompue à son délai maximal.") from error
            if message.get("event") == "owned_process":
                if owned is not None:
                    raise ValueError("Seconde instance Excel inattendue.")
                if not isinstance(message.get('pid'), int) or isinstance(message['pid'], bool) or message['pid'] <= 0 or message['pid'] in previous_pids:
                    raise ValueError("Instance Excel déjà présente avant l'opération : aucune modification autorisée.")
                owned = OwnedExcelProcess(message["pid"])
                send({'operation': 'ownership_confirmed'})
                continue
            if message.get("event") == "error":
                raise ValueError(message.get("error", "Erreur du calcul WACC."))
            if message.get("event") != event:
                raise ValueError("Réponse inattendue du calcul WACC : " + str(message.get("event")))
            return message

    def send(value):
        process.stdin.write(json.dumps(value, allow_nan=False, ensure_ascii=False) + "\n")
        process.stdin.flush()

    try:
        record_progress('WAITING_FOR_NATIVE_READINESS')
        ready = receive("ready")
        if owned is None or ready["iteration_enabled"]:
            raise ValueError("Instance Excel dédiée ou mode de calcul non vérifié.")
        def evaluate(candidate):
            record_progress('EVALUATING',pending_candidate=candidate)
            observed_at=time.monotonic()
            send({"operation": "evaluate", "candidate": candidate})
            item=receive("evaluation")
            observations.append({'candidate':candidate,'elapsed_seconds':time.monotonic()-observed_at,
                'validity':item.get('validity'),'calculated':item.get('calculated'),'equity':item.get('equity')})
            record_progress('OBSERVED',pending_candidate=None)
            return item
        result = solve(evaluate, ready["growth"], timeout=max(0.01, deadline - time.monotonic()))
        if not result["converged"]:
            send({"operation": "abort"})
            receive("aborted")
            atomic_json(receipt.with_name(receipt.stem + ".echec.json"), {**result, "source_sha256": source_sha,
                        "source_preserved": digest(source) == source_sha, "adopted": False, "macros_enabled": False})
            raise ValueError("Résolution WACC sans succès : " + result["status"])
        record_progress('VERIFYING_SAVE_AND_REOPEN')
        send({"operation": "save", "evaluations": result["evaluations"]})
        receive("saved")
        process.stdin.close()
        process.wait(timeout=max(0.01, deadline - time.monotonic()))
        if process.returncode != 0 or not output.is_file() or not receipt.is_file():
            raise ValueError("La sauvegarde WACC n'est pas terminée.")
        saved = json.loads(receipt.read_text(encoding="utf-8-sig"))
        validate_saved_receipt(saved, result, ready['growth'], mapping)
        if (saved.get("status") != "CONVERGENCE_LOCALE" or saved.get("save_reopen_verified") is not True
                or saved.get("source_sha256") != source_sha or digest(source) != source_sha
                or saved.get("output_sha256") != digest(output) or saved.get("iteration_enabled")
                or saved.get("fingerprint") != result["fingerprint"]):
            raise ValueError("Le reçu WACC ne correspond pas aux fichiers et à la résolution.")
        saved["solver_proof"] = result
        saved["adopted"] = False
        atomic_json(receipt, saved)
        record_progress('COMPLETE')
        complete = True
        return saved
    except BaseException as error:
        record_progress('ERROR',error=type(error).__name__+': '+str(error))
        raise
    finally:
        from .native_cleanup import finish_native_process
        finish_native_process(process, owned, complete)
