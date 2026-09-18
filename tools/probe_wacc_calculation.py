"""Four bounded calculation measurements on an identified fictitious case.

Uses an instrumented PRIVATE copy of the production worker and its normal
ownership/abort supervisor. Never saves or adopts a workbook. The scalar solver
is replaced only in this diagnostic process, never in the application.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from unittest.mock import patch
import uuid

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tca_bp import wacc_native
from tca_bp.service import Application
from tca_bp.storage import atomic_json,digest
from tca_bp.web_lock import serialized_excel
from tca_bp.web_model import ProfileEngine


@serialized_excel
def run(prepared_folder,automatic_inputs=False):
    prepared_folder=Path(prepared_folder).resolve()
    if prepared_folder.parent!=ROOT/'runtime' or not prepared_folder.name.startswith('recette_qualifications_service_'):
        raise ValueError('Seul un dossier de recette fictive identifié est admis.')
    prepared=json.loads((prepared_folder/'preparation.json').read_text(encoding='utf-8'))
    if prepared['case_id']!='test_qualifications_wacc':raise ValueError('Identité fictive inattendue.')
    engine=ProfileEngine(ROOT,Path(prepared['model_dir']));engine.ensure_built()
    from tca_bp.web_model_profile import map_location
    diagnostic_addresses=['D7','D8','D15','D16','D17','D20','D21','D22','D23','D24','D25','D26','E26','F26','G26','M26',
                          'D31','D32','F32','G32','M32','D33','F33','G33','M33','D34','D35','D36','D37','D38','D39',
                          'D127','D128','D129','D130','D131','D132','D133','D134','D136']
    if any(map_location(engine.profile,'Valorisation',a)['cell']!=a for a in diagnostic_addresses):
        raise ValueError('Cette sonde détaillée exige les adresses de la trame de recette sans déplacement.')
    app=Application(ROOT,prepared_folder,engine=engine)
    source=app._workbook(app._row(prepared['case_id']));source_sha=digest(source)
    folder=ROOT/'runtime'/('sonde_wacc_calcul_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
    folder.mkdir()
    worker=Path(wacc_native.__file__).with_name('wacc_worker.ps1').read_text(encoding='utf-8-sig')
    before="            $sheet.Range((Mapped 'D136')).Value2 = [double]$candidate"
    instrumented="""            $probeForceBefore=[bool]$book.ForceFullCalculation
            $probeWatch=[Diagnostics.Stopwatch]::StartNew()
            if ($evaluations -ge 2) { $book.ForceFullCalculation=$false }
            $excelInstance.Calculation=$(if ($evaluations -ge 3) {2} else {-4135})
            $sheet.Range((Mapped 'D136')).Value2 = [double]$candidate"""
    marker="Emit @{event='evaluation'; validity="
    telemetry="""Emit @{event='evaluation'; probe_force_before=$probeForceBefore;
                   probe_force_after=[bool]$book.ForceFullCalculation;
                   probe_calculation_mode=[int]$excelInstance.Calculation;
                   probe_elapsed_ms=$probeWatch.Elapsed.TotalMilliseconds; validity="""
    if worker.count(before)!=1 or worker.count(marker)!=1:
        raise ValueError('Le worker a changé : adapter explicitement la sonde.')
    worker=worker.replace(before,instrumented).replace(marker,telemetry)
    auto_wait='            while ($excelInstance.CalculationState -ne 0) { Start-Sleep -Milliseconds 50 }'
    if automatic_inputs:
        worker=worker.replace('if ($evaluations -ge 2) { $book.ForceFullCalculation=$false }','')
        worker=worker.replace('$excelInstance.Calculation=$(if ($evaluations -ge 3) {2} else {-4135})','$excelInstance.Calculation=2')
        worker=worker.replace('            $excelInstance.Calculate()',auto_wait)
    else:
        worker=worker.replace(auto_wait,'            $excelInstance.Calculate()')
    snapshots="            $probeCells=@{}\n            foreach($address in @("+','.join("'"+a+"'" for a in diagnostic_addresses)+")) { $probeCells[$address]=$sheet.Range($address).Value2 }\n            "
    worker=worker.replace("Emit @{event='evaluation'; probe_force_before",snapshots+"Emit @{event='evaluation'; probe_values=$probeCells; probe_force_before")
    (folder/'wacc_worker.ps1').write_bytes(b'\xef\xbb\xbf'+worker.replace('\r\n','\n').replace('\n','\r\n').encode())
    report={'schema':'tca-wacc-calculation-probe/1','status':'EN_COURS','adopted':False,
            'source_sha256':source_sha,'production_worker_sha256':digest(Path(wacc_native.__file__).with_name('wacc_worker.ps1')),
            'probe_worker_sha256':digest(folder/'wacc_worker.ps1'),'automatic_inputs_without_f9':automatic_inputs,'observations':[]}
    def observe(evaluate,growth,**kwargs):
        for candidate in ((.08,.10) if automatic_inputs else (.08,.10,.09,.11)):
            item=evaluate(candidate)
            report['observations'].append({'candidate':candidate,**item})
            atomic_json(folder/'validation.json',report)
            print(json.dumps({k:v for k,v in report['observations'][-1].items() if k!='fingerprint'}),flush=True)
        return {'status':'DIAGNOSTIC_ONLY','converged':False,'evaluations':len(report['observations']),
                'observations':report['observations']}
    print('Sonde native sans sauvegarde : '+str(folder),flush=True)
    try:
        with patch.object(wacc_native,'__file__',str(folder/'probe.py')),patch.object(wacc_native,'solve',observe):
            try:
                wacc_native.solve_native(source,folder/'never_saved.xlsm',folder/'probe.json',timeout=300,profile=engine.profile)
            except ValueError as error:
                if str(error)!='Résolution WACC sans succès : DIAGNOSTIC_ONLY':raise
        report['status']='MESURE_TERMINEE'
    except BaseException as error:
        report.update(status='ECHEC',error=repr(error));raise
    finally:
        report['source_preserved']=digest(source)==source_sha
        report['no_workbook_saved']=not (folder/'never_saved.xlsm').exists()
        atomic_json(folder/'validation.json',report)
        print(report['status']+' — '+str(folder/'validation.json'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared_folder',type=Path)
    parser.add_argument('--automatic-inputs',action='store_true')
    args=parser.parse_args()
    run(args.prepared_folder,args.automatic_inputs)
