"""Regression checks and opt-in native oracles for unavailable valuation inputs.

Run the bounded real-Excel recipe explicitly, with a new scratch directory:
    py -3.14 -m tests.test_model_guards --native --output PATH
These synthetic fixtures are not an economic qualification of the full model.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import unittest
import zipfile
from copy import copy

from tca_bp.model_engine import ModelEngine
from tca_bp.model_build import VALUATION_GUARDS, dump
from tca_bp.vendor import input_engine as core

ROOT=Path(__file__).resolve().parents[1]
CANDIDATE=ROOT/'models/generic-v1-guards'
SAVED_BASELINE=ROOT/'models/generic-v1-pre-guards'
BASELINE=SAVED_BASELINE if (SAVED_BASELINE/'TCA_BP_Trame_generique.xlsm').is_file() else ROOT/'models/generic-v1'
BASELINE_SHA256='15815c1062653d72cd7686334a3d080aeb88b9eb8f6f6fa75b6c7195409ed663'
TARGETS=[('Valorisation','B55'),('Valorisation','D59'),('Contrôles','C121'),('Contrôles','N121')]


def fixture_updates(name):
    """Independent financial values: 250k / (1m + 250k) = 20%."""
    if name=='empty':return []
    premoney=900000 if name=='divergent' else 1000000
    values=[('Valorisation','D107','Manuel'),('Valorisation','D108',0.12),('Valorisation','D57',premoney)]
    if name!='partial':
        values.extend([('DATA Financement','B14','TOUR FICTIF DE TEST'),
                       ('DATA Financement','C14','SERIE A'),('DATA Financement','D14',250000),
                       ('DATA Financement','E14','2026-06-01'),('DATA Financement','F14',1000000)])
    return [{'sheet':s,'cell':c,'value':v,'reason':'Fixture synthétique : contrôle indépendant des gardes de valorisation',
             'evidence':'TEST_GUARDS_'+name.upper()} for s,c,v in values]


def verify_oracle(name, actual):
    """Check independent outcomes, including absence of false control success."""
    def value(s,c):return actual[s+'!'+c]
    for address in TARGETS:
        v=value(*address)
        if isinstance(v,str) and v.startswith(('#VALUE!','#DIV/0!','#REF!','#NAME?')):
            raise AssertionError(f'{name}: Excel error on {address}: {v}')
    label=value('Valorisation','B55');ratio=value('Valorisation','D59')
    delta=value('Contrôles','C121');status=value('Contrôles','N121')
    if name in ('empty','partial'):
        if ratio!='Non renseigné' or delta!='Non renseigné' or 'Non contrôlé' not in status or 'OK' in status:
            raise AssertionError(f'{name}: missing information was represented as a result: {actual}')
    elif name=='complete':
        if not isinstance(ratio,(int,float)) or abs(ratio-0.2)>1e-12 or delta!=0 or status!='✓ OK':
            raise AssertionError(f'{name}: expected 20% and reconciled pre-money: {actual}')
    elif name=='divergent':
        if delta!=-100000 or 'divergent' not in status or 'OK' in status:
            raise AssertionError(f'{name}: expected -100k discrepancy and warning: {actual}')
    elif name=='zero_denominator':
        if ratio!='Non déterminé':raise AssertionError(f'{name}: denominator zero must not yield a ratio: {actual}')
    if name=='empty':
        if 'non renseigné' not in label:raise AssertionError('Missing rate must remain visible.')
    elif '12 %' not in label:raise AssertionError('Explicit 12% rate must remain visible.')


def prepare_native_validation(output: Path):
    """Prepare reproducible inputs without reserving an Excel process."""
    folder=Path(output).resolve()
    engine=ModelEngine(ROOT,model_dir=CANDIDATE);receipt=engine.ensure_built()
    baseline_hash=core.sha((BASELINE/'TCA_BP_Trame_generique.xlsm').read_bytes())
    if baseline_hash!=BASELINE_SHA256:raise ValueError('La comparaison exige la copie exacte de la référence pré-gardes, jamais le candidat.')
    candidate_hash=core.sha(engine.template_path.read_bytes())
    folder.mkdir(parents=True,exist_ok=True)
    prepared={'schema':'tca-bp-guards-preparation/v1','model_id':engine.model_id,
              'candidate_sha256':candidate_hash,'baseline_sha256':baseline_hash,'baseline_path':str(BASELINE),'status':'PREPARING','cases':[]}
    if (folder/'preparation.json').exists():
        prepared=json.loads((folder/'preparation.json').read_text(encoding='utf-8'))
        if prepared.get('status') not in ('PREPARING','FAILED') or prepared['candidate_sha256']!=candidate_hash or prepared['baseline_sha256']!=baseline_hash:
            raise ValueError('Cette préparation ne peut pas être reprise.')
        prepared.pop('error',None);prepared['status']='PREPARING'
        for item in prepared['cases']:
            if core.sha(Path(item['source']).read_bytes())!=item['source_sha256']:raise ValueError('Une copie préparée a changé.')
    wb=engine._open(engine.template_path)
    try:template_input_signature=wb.input_signature(engine.schema)
    finally:wb.close()
    for name in ('empty','partial','complete','divergent','zero_denominator'):
        if any(item['case']==name for item in prepared['cases']):continue
        if name=='zero_denominator':
            # The public writer correctly refuses nonpositive pre-money. This
            # explicit fault-injection copy tests the Excel guard if a workbook
            # is manually edited outside the application, not a permitted input.
            complete=Path(next(item['source'] for item in prepared['cases'] if item['case']=='complete'))
            try:
                engine.prepare(complete,[{'sheet':'Valorisation','cell':'D57','value':-250000,
                    'reason':'Borne artificielle hors domaine, attendue refusée','evidence':'TEST_DOMAIN','replace_existing':True}])
            except ValueError as exc:
                if 'borne exclusive' not in str(exc):raise
            else:raise AssertionError('The writer must refuse nonpositive pre-money.')
            wb=engine._open(complete);source=folder/'zero_denominator_defensive_input.xlsm'
            try:
                part=wb.sheets['Valorisation']['part']
                raw=core.CELL_RX.sub(lambda m:core.xml_cell(m[0],-250000,'number') if m[1]==b'D57' else m[0],wb.z.read(part))
                with zipfile.ZipFile(source,'x') as output:
                    for info in wb.z.infolist():output.writestr(copy(info),raw if info.filename==part else wb.z.read(info.filename))
            finally:wb.close()
            check=engine._open(source)
            try:input_signature=check.input_signature(engine.schema)
            finally:check.close()
            prepared['cases'].append({'case':name,'source':str(source),'source_sha256':core.sha(source.read_bytes()),
                                     'input_signature':input_signature,'fixture_policy':'OUT_OF_DOMAIN_DEFENSIVE_COPY_ONLY','public_writer_refused_input':True})
            dump(folder/'preparation.json',prepared);print('PREPARED '+name,flush=True);continue
        updates=fixture_updates(name)
        source=engine.template_path
        if updates:
            plan=engine.prepare(source,updates)
            source=folder/(name+'_input.xlsm')
            receipt=engine.apply(engine.template_path,plan,source)
            input_signature=receipt['output_input_signature']
        else:input_signature=template_input_signature
        prepared['cases'].append({'case':name,'source':str(source),'source_sha256':core.sha(source.read_bytes()),'input_signature':input_signature})
        dump(folder/'preparation.json',prepared)
        print('PREPARED '+name,flush=True)
    prepared['status']='PREPARED';dump(folder/'preparation.json',prepared)
    return prepared


def run_native_validation(output: Path):
    """Recalculate exclusively prepared copies via the shared isolated runner."""
    from tca_bp.native_excel import recalculate
    folder=Path(output).resolve()
    prepared=json.loads((folder/'preparation.json').read_text(encoding='utf-8')) if folder.exists() else prepare_native_validation(folder)
    if prepared.get('status')!='PREPARED' or (folder/'validation.json').exists():raise ValueError('Préparation incomplète ou recette déjà commencée.')
    engine=ModelEngine(ROOT,model_dir=CANDIDATE);engine.ensure_built()
    candidate_hash=core.sha(engine.template_path.read_bytes());baseline_hash=core.sha((BASELINE/'TCA_BP_Trame_generique.xlsm').read_bytes())
    if baseline_hash!=BASELINE_SHA256:raise ValueError('Empreinte de la référence pré-gardes incorrecte.')
    if candidate_hash!=prepared['candidate_sha256'] or baseline_hash!=prepared['baseline_sha256']:raise ValueError('Une référence a changé après préparation.')
    result={'schema':'tca-bp-guards-validation/v1','model_id':engine.model_id,
            'candidate_sha256':candidate_hash,'baseline_sha256':baseline_hash,'baseline_path':str(BASELINE),'status':'RUNNING',
            'schema_sha256':engine.ensure_built()['schema_sha256'],'model_signature':engine.schema['signature']['overall'],
            'economic_validation':'NOT_PERFORMED','macros_executed':False,'cases':[]}
    dump(folder/'validation.json',result)
    for item in prepared['cases']:
        name=item['case'];source=Path(item['source']).resolve();input_signature=item['input_signature']
        if source!=engine.template_path.resolve() and not source.is_relative_to(folder):raise ValueError('Source hors recette.')
        if core.sha(source.read_bytes())!=item['source_sha256']:raise ValueError('Une copie préparée a changé.')
        target=folder/(name+'_excel.xlsm')
        native=recalculate(source,target,folder/(name+'_native.json'))
        checked=engine._open(target)
        try:
            if checked.input_signature(engine.schema)!=input_signature:raise AssertionError('Native calculation changed an input.')
            actual={s+'!'+a:checked.value(s,a) for s,a in TARGETS}
            verify_oracle(name,actual)
            error_counts={}
            for sheet in checked.sheets:
                for addr,node in checked.sheet(sheet)[1].items():
                    if node.get('t')=='e':
                        error=checked.value(sheet,addr)
                        if error:error_counts[error]=error_counts.get(error,0)+1
                checked._sheet_cache.pop(sheet,None)
            result['cases'].append({'case':name,'status':'PASS','actual':actual,
                                    'fixture_policy':item.get('fixture_policy','VALID_PUBLIC_WRITER_INPUTS'),
                                    'public_writer_refused_input':item.get('public_writer_refused_input',False),
                                    'model_and_cell_protections_preserved':True,'inputs_preserved':True,
                                    'source_sha256':native['source_sha256'],'output_sha256':native['output_sha256'],
                                    'calculation_state':native['calculation_state'],'remaining_errors':error_counts})
        finally:checked.close()
        dump(folder/'validation.json',result)
        print(json.dumps(result['cases'][-1],ensure_ascii=True),flush=True)
    if core.sha(engine.template_path.read_bytes())!=candidate_hash or core.sha((BASELINE/'TCA_BP_Trame_generique.xlsm').read_bytes())!=baseline_hash:
        raise AssertionError('A reference template changed during validation.')
    result.update(status='PASS',source_templates_unchanged=True,scope='Only four guarded outputs, not the full financial model')
    dump(folder/'validation.json',result)
    return result


class GuardOracles(unittest.TestCase):
    def test_oracle_rejects_missing_data_presented_as_zero_or_ok(self):
        false={'Valorisation!B55':'taux non renseigné','Valorisation!D59':0,
               'Contrôles!C121':0,'Contrôles!N121':'✓ OK'}
        with self.assertRaises(AssertionError):verify_oracle('empty',false)

    def test_oracle_checks_dilution_and_pre_money_reconciliation(self):
        valid={'Valorisation!B55':'Pre-money DCF (taux = 12 %)','Valorisation!D59':0.2,
               'Contrôles!C121':0,'Contrôles!N121':'✓ OK'}
        verify_oracle('complete',valid)
        with self.assertRaises(AssertionError):verify_oracle('complete',{**valid,'Valorisation!D59':0.25})


@unittest.skipUnless((CANDIDATE/'build_receipt.json').is_file(),'Build the separate guards candidate first')
class GuardCandidate(unittest.TestCase):
    def test_guard_candidate_and_available_prior_reference(self):
        old=core.Workbook(BASELINE/'TCA_BP_Trame_generique.xlsm');new=core.Workbook(CANDIDATE/'TCA_BP_Trame_generique.xlsm')
        observed={}
        try:
            self.assertEqual(old.hash,BASELINE_SHA256,'Conserver la copie exacte dans models/generic-v1-pre-guards avant promotion.')
            self.assertNotEqual(old.hash,new.hash,'Le candidat ne peut pas servir de référence historique.')
            for key,formula in VALUATION_GUARDS.items():self.assertEqual(new.formula(*key),formula)
            self.assertEqual(list(old.sheets),list(new.sheets))
            for sheet in old.sheets:
                self.assertEqual(set(old.sheet(sheet)[1]),set(new.sheet(sheet)[1]))
                for addr in old.sheet(sheet)[1]:
                    a,b=old.formula(sheet,addr),new.formula(sheet,addr)
                    if a!=b:observed[sheet,addr]=b
                    if a is None and b is None:self.assertEqual(old.value(sheet,addr),new.value(sheet,addr),(sheet,addr))
                old._sheet_cache.pop(sheet,None);new._sheet_cache.pop(sheet,None)
            self.assertEqual(observed,VALUATION_GUARDS)
            self.assertEqual(old.z.read('xl/vbaProject.bin'),new.z.read('xl/vbaProject.bin'))
        finally:old.close();new.close()


if __name__=='__main__':
    if '--native' in sys.argv or '--prepare-only' in sys.argv:
        parser=argparse.ArgumentParser(description=__doc__)
        mode=parser.add_mutually_exclusive_group(required=True)
        mode.add_argument('--native',action='store_true')
        mode.add_argument('--prepare-only',action='store_true')
        parser.add_argument('--output',type=Path,required=True)
        options=parser.parse_args()
        try:
            if options.prepare_only:prepare_native_validation(options.output)
            else:run_native_validation(options.output)
        except Exception as exc:
            report=options.output/('preparation.json' if options.prepare_only else 'validation.json')
            if report.is_file():
                failed=json.loads(report.read_text(encoding='utf-8'))
                if failed.get('status') in ('RUNNING','PREPARING'):
                    failed.update(status='FAILED',error=str(exc));dump(report,failed)
            raise
    else:unittest.main()
