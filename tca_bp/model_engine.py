"""Public, generic model API. All workbook writes are exclusive new copies."""
from __future__ import annotations
import copy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from .model_runtime import MODEL_ID, invalidate_caches, invalidate_chart
from .vendor import input_engine as core


def build_model(*args, **kwargs):
    """Chargement différé du générateur, uniquement dans le dépôt TCA."""
    try:
        from .model_build import build_model as build
    except ModuleNotFoundError as exc:
        if exc.name != __package__ + '.model_build':
            raise
        raise ValueError('Modèle préconstruit absent : restaurer le pack client complet. La reconstruction est réservée au dépôt de développement TCA.') from exc
    return build(*args, **kwargs)


class ModelEngine:
    def __init__(self, project_root: Path, model_dir: Path|None=None):
        self.project_root=Path(project_root).resolve()
        self._explicit_model_dir=model_dir is not None
        self.model_dir=Path(model_dir).resolve() if model_dir is not None else self.project_root/'models'/'generic-v1'
        self._schema=None
        self._receipt=None
        self._protection_signature=None

    @property
    def model_id(self):
        self.ensure_built()
        return self._schema['model_id']

    @property
    def template_path(self):return self.model_dir/'TCA_BP_Trame_generique.xlsm'

    @property
    def schema(self):
        self.ensure_built()
        return self._schema

    def ensure_built(self):
        if self._schema is not None:return copy.deepcopy(self._receipt)
        path=self.model_dir/'build_receipt.json'
        if not path.exists():
            if self._explicit_model_dir:raise ValueError('Version de modèle absente : aucune reconstruction implicite d’une variante.')
            build_model(self.project_root,self.model_dir)
        try:
            receipt=json.loads(path.read_text(encoding='utf-8'))
            raw=(self.model_dir/'modele.json').read_bytes()
            if core.sha(raw)!=receipt['schema_sha256']:raise ValueError('Le manifeste généré a changé. Reconstruire une version contrôlée du modèle.')
            if core.sha(self.template_path.read_bytes())!=receipt['template_sha256']:raise ValueError('La trame générique a changé. La référence de modèle doit rester immuable.')
            schema=json.loads(raw)
            if schema['model_id']!=receipt['model_id'] or (not self._explicit_model_dir and schema['model_id']!=MODEL_ID):raise ValueError('Identifiant de modèle incohérent avec son reçu.')
        except (OSError,KeyError,json.JSONDecodeError) as exc:
            raise ValueError('Modèle incomplet : reconstruire les artefacts du modèle.') from exc
        self._schema=schema;self._receipt=receipt
        return copy.deepcopy(receipt)

    def catalog(self):
        from .field_semantics import enrich_catalog
        self.ensure_built()
        # Catalogue complémentaire : le schéma scellé n'est jamais enrichi en place.
        reference = core.Workbook(self.template_path)
        try:
            if reference.hash != self._receipt['template_sha256']:
                raise ValueError('La référence du catalogue sémantique a changé.')
            return enrich_catalog(self.schema, workbook=reference)
        finally:
            reference.close()

    def reseal_variant(self, workbook: Path, output_dir: Path, model_id: str, expected_changes: list[dict]):
        """Déléguer le scellement au composant de développement non distribué."""
        try:
            from .model_maintenance import reseal_variant
        except ModuleNotFoundError as exc:
            if exc.name != __package__ + '.model_maintenance':
                raise
            raise ValueError('La maintenance est réservée au dépôt de développement TCA ; elle n’est pas incluse dans le pack client.') from exc
        return reseal_variant(self, workbook, output_dir, model_id, expected_changes)

    def _open(self,path):
        wb=None
        try:
            wb=core.Workbook(Path(path));core.verify_model(wb,self.schema)
            actual=self._cell_protection_signature(wb)
            if self._protection_signature is None:
                if wb.hash==self._receipt['template_sha256']:
                    self._protection_signature=actual
                else:
                    reference=core.Workbook(self.template_path)
                    try:
                        if reference.hash!=self._receipt['template_sha256']:raise ValueError('La référence de protection a changé.')
                        self._protection_signature=self._cell_protection_signature(reference)
                    finally:reference.close()
            if actual!=self._protection_signature:raise ValueError('Protections de cellules modifiées : la saisie requiert une trame conforme.')
            return wb
        except (OSError,KeyError,TypeError,ValueError,zipfile.BadZipFile) as exc:
            if wb:wb.close()
            raise ValueError(str(exc)) from exc

    def _cell_protection_signature(self,wb):
        """Compare effective cell locks, not unstable Excel style indices."""
        protections=[]
        for xf in wb.xfs:
            p=xf.find('m:protection',core.N)
            protections.append((p is None or p.get('locked','1') not in ('0','false'),
                                p is not None and p.get('hidden','0') in ('1','true')))
        result={}
        for sheet in wb.sheets:
            digest=hashlib.sha256()
            required=set(self.schema['cells'].get(sheet,{}))|set(self.schema.get('native_outputs',{}).get(sheet,[]))|set(self.schema.get('native_table_outputs',{}).get(sheet,[]))
            for addr,c in sorted(wb.sheet(sheet)[1].items()):
                if addr not in required and c.find('m:f',core.N) is None and core.blank(wb.value(sheet,addr)):continue
                digest.update(core.packed([addr,*protections[int(c.get('s','0'))]]))
            result[sheet]=digest.hexdigest()
            wb._sheet_cache.pop(sheet,None)
        return result

    def _completeness(self,wb):
        missing=[];modules={};active=[]
        def require(sheet,cell,reason):
            if core.blank(wb.value(sheet,cell)) and wb.formula(sheet,cell) is None:
                missing.append({'sheet':sheet,'cell':cell,'reason':reason,'state':'NON_RENSEIGNE'})
        years=wb.value('Control','C59')
        if not isinstance(years,(int,float)) or isinstance(years,bool) or int(years)!=years or not 1<=years<=10:
            missing.append({'sheet':'Control','cell':'C59','reason':'Entier requis de 1 à 10','state':'NON_RENSEIGNE'});years=0
        years=int(years)
        for row in range(15,28):
            flag=wb.value('Assumptions','C'+str(row))
            if flag==1:
                active.append(row)
                for c in ('D','E','F','U','V','W','X','Y'):
                    require('Assumptions',c+str(row),'Paramètre requis de l’offre active')
                vols=['K','L','M','N','O','AK','AL','AM','AN','AO'][:years]
                for c in vols:require('Assumptions',c+str(row),'Objectif explicite, zéro autorisé, pour l’offre active')
                require('DATA COGS','D'+str(row),'Méthode de coût de l’offre active')
                for c in ('D','E'):
                    require('ATELIER_CIR_IS',c+str(row+128),'Régime et taux de TVA à qualifier pour l’offre active')
            modules[f'offer.{row-14:02d}']='ACTIF' if flag==1 else 'INACTIF' if flag==0 else 'NON_RENSEIGNE'
        occupied={}
        for sheet,reg in self.schema['registers'].items():
            rows=[]
            for row in range(reg['start_row'],reg['end_row']+1):
                # An untouched known default formula cannot activate a record.
                if any(not core.blank(wb.value(sheet,c+str(row))) and wb.formula(sheet,c+str(row)) is None for c in reg['identity_columns']):
                    rows.append(row)
                    for c in reg.get('required',[]):require(sheet,c+str(row),'Registre activé : information requise')
            occupied[sheet]=rows;modules[sheet]='ACTIF' if rows else 'INACTIF'
        has_activity=bool(active or any(occupied.values()))
        if has_activity:
            require('Assumptions','D126',"Solde d’ouverture sourcé, zéro explicite possible")
            require('Assumptions','D4','Inflation générale à renseigner explicitement')
            require('Assumptions','D79','Traitement IS applicable à documenter')
            for c in 'CDEFGHIJKLM'[:years]:
                require('ATELIER_CIR_IS',c+'66','Conditions du régime fiscal à qualifier')
        return {'state':'EMPTY' if not has_activity else 'NEEDS_INPUT' if missing else 'INPUTS_COMPLETE_ON_DECLARED_SCOPE',
                'modules':modules,'active_offers':len(active),'missing':missing,'missing_count':len(missing),
                'business_qualification_required':True,'financial_results_available':False}

    def context(self,workbook: Path):
        wb=self._open(workbook)
        try:
            result=core.context(wb,self.schema)
            result['schema']='tca-bp-context/v1'
            result['input_signature']=wb.input_signature(self.schema)
            result['cell_protection_signature']=copy.deepcopy(self._protection_signature)
            result['date1904']=wb.date1904
            from .qualifications import SCOPES, error_perimeter
            errors=[];counts={};total=0
            error_scopes=dict.fromkeys(SCOPES,0);inactive_errors=0
            years=wb.value('Control','C59')
            years=int(years) if isinstance(years,(int,float)) and not isinstance(years,bool) and int(years)==years else 0
            for sheet in wb.sheets:
                for addr,node in wb.sheet(sheet)[1].items():
                    if node.get('t')=='e':
                        value=wb.value(sheet,addr)
                        # An empty error-typed formula has no calculated error.
                        if value is not None:
                            total+=1;counts[value]=counts.get(value,0)+1
                            scope,active=error_perimeter(sheet,addr,years)
                            if active:error_scopes[scope]+=1
                            else:inactive_errors+=1
                            if len(errors)<100:errors.append({'sheet':sheet,'cell':addr,'error':value})
                wb._sheet_cache.pop(sheet,None)
            result['formula_errors']={'count':total,'by_error':counts,'cells':errors,'truncated':total>len(errors),'status':'CACHED_VALUES_ONLY',
                                      'active_by_scope':error_scopes,'inactive_horizon_count':inactive_errors,'attribution_complete':True}
            result['completeness']=self._completeness(wb)
            result['modules']=result['completeness']['modules']
            result['status']=result['completeness']['state']
            result['financial_results_available']=False
            result['calculation_status']='NATIVE_VERIFICATION_REQUIRED'
            result['fiscal_policy']='Règles annuelles héritées : qualification du régime, des dates et des sources requise avant utilisation des résultats.'
            return result
        finally:wb.close()

    def qualification_snapshot(self, workbook: Path) -> dict:
        """Valeurs propriétaires reconnues, sans interpréter les caches fiscaux."""
        from .qualifications import collect_snapshot
        wb = self._open(workbook)
        try:
            snapshot = collect_snapshot(wb, self.schema)
            from .field_semantics import summary
            catalogue = self.catalog()
            snapshot['field_semantics'] = summary(catalogue)
            for field in catalogue:
                semantic = field.get('semantics', {})
                for address in field.get('cells', []):
                    key = field['sheet'] + '!' + address
                    if key in snapshot['cells']:
                        snapshot['cells'][key]['semantic_status'] = semantic.get('status')
                        snapshot['cells'][key]['semantic_issues'] = semantic.get('blocking_reasons', [])
            return snapshot
        finally:
            wb.close()

    def inspect(self,workbook: Path,sheet: str,cells: list[str]|None=None):
        wb=self._open(workbook)
        try:
            if sheet not in wb.sheets:raise ValueError('Feuille inconnue : '+str(sheet))
            addresses=cells if cells is not None else list(self.schema['cells'].get(sheet,{}))
            if not isinstance(addresses,list) or len(addresses)>15000:raise ValueError('Liste de cellules limitée à 15 000 éléments.')
            result={}
            for addr in addresses:
                core.coord(addr)
                spec=copy.deepcopy(self.schema['cells'].get(sheet,{}).get(addr,{}))
                result[addr]={**spec,'writable':bool(spec),'current':wb.snapshot(sheet,addr),
                              'calculation_status':'CACHED_VALUE_NOT_CERTIFIED' if wb.formula(sheet,addr) is not None else 'INPUT_VALUE'}
            return {'schema':'tca-bp-inspection/v1','model_id':self.model_id,'source_name':wb.path.name,
                    'source_sha256':wb.hash,'inputs':{sheet:result},'cells':result,'sheet':sheet,
                    'input_signature':wb.input_signature(self.schema),'date1904':wb.date1904}
        finally:wb.close()

    def prepare(self,workbook: Path,updates: list[dict]):
        wb=self._open(workbook)
        try:
            if not isinstance(updates,list) or not 1<=len(updates)<=2000:raise ValueError('Prévoir de 1 à 2 000 écritures par lot.')
            from .field_semantics import validate_updates, contract_digest
            if all(isinstance(update,dict) for update in updates):
                validate_updates(self.catalog(), updates)
            changes=[]
            for update in updates:
                if not isinstance(update,dict):raise ValueError('Chaque mise à jour doit être un objet.')
                allowed={'sheet','cell','value','reason','evidence','evidence_id','expected','replace_existing','override_default'}
                if set(update)-allowed:raise ValueError('Clés non autorisées dans une mise à jour : '+', '.join(sorted(set(update)-allowed)))
                if not {'sheet','cell','value','reason'}<=set(update):raise ValueError('Feuille, cellule, valeur et justification sont requises.')
                evidence=update.get('evidence',update.get('evidence_id'))
                if not evidence:raise ValueError('Chaque saisie doit citer une réponse ou une pièce du dossier.')
                if isinstance(update['value'],str) and update['value'].lstrip().startswith('='):raise ValueError('Une formule libre ne peut pas être introduite par la saisie.')
                snap=wb.snapshot(update['sheet'],update['cell'])
                if 'expected' in update and core.packed(update['expected'])!=core.packed(snap):raise ValueError('La cellule a changé depuis la préparation.')
                change={k:v for k,v in update.items() if k not in ('expected','evidence_id')}
                change['expected']=snap;change['evidence']=evidence
                changes.append(change)
            request={'schema':'isp-pilotage-plan/v1','model_id':self.model_id,'source_sha256':wb.hash,'changes':changes}
            normalized=core.prepare_plan(wb,self.schema,request)
            # Calendar validation uses the prospective batch, never a cached date.
            values={(c['sheet'],c['cell']):c['value'] for c in normalized}
            if ('Control','C10') in values:
                date=dt.date.fromisoformat(values['Control','C10'])
                if date.month!=1 or date.day!=1:raise ValueError('La date de début doit être le 1er janvier.')
            return {'schema':'tca-bp-plan/v1','model_id':self.model_id,'source_sha256':wb.hash,
                    'source_name':wb.path.name,'source_input_signature':wb.input_signature(self.schema),
                    'changes':normalized,'updates':copy.deepcopy(normalized),'valid':True,
                    'semantics_sha256':contract_digest(),
                    'calculation_status':'RECALCULATION_REQUIRED_AFTER_APPLY',
                    'prepared_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
        except (KeyError,TypeError,OverflowError) as exc:raise ValueError('Saisie invalide : '+str(exc)) from exc
        finally:wb.close()

    def apply(self,workbook: Path,plan: dict,output: Path):
        wb=self._open(workbook);out=Path(output).resolve();tmp=None;jtmp=None;published=[]
        try:
            if out==wb.path.resolve() or out==self.template_path.resolve():raise ValueError('La source et la trame ne peuvent pas être écrasées.')
            if out.suffix.lower()!='.xlsm':raise ValueError('La sortie doit conserver le format XLSM.')
            journal=out.with_suffix('.journal.json')
            if out.exists() or journal.exists():raise ValueError('La sortie ou son journal existe déjà.')
            if not out.parent.is_dir():raise ValueError('Le dossier de sortie doit déjà exister.')
            if plan.get('schema')!='tca-bp-plan/v1':raise ValueError('Format de plan invalide.')
            from .field_semantics import contract_digest, validate_updates
            if plan.get('semantics_sha256') is not None and plan['semantics_sha256'] != contract_digest():
                raise ValueError('Le catalogue sémantique a changé depuis la préparation ; préparer un nouveau plan explicite.')
            # Un plan historique sans ce champ n'est pas promu implicitement :
            # chaque saisie doit encore avoir une définition établie dans la carte actuelle.
            validate_updates(self.catalog(), plan.get('changes', []))
            if plan.get('source_input_signature')!=wb.input_signature(self.schema):raise ValueError('Plan périmé : les saisies ont changé.')
            nativeplan={'schema':'isp-pilotage-plan/v1','model_id':plan.get('model_id'),'source_sha256':plan.get('source_sha256'),
                        'changes':[{k:v for k,v in c.items() if k!='kind'} for c in plan.get('changes',[])]}
            changes=core.prepare_plan(wb,self.schema,nativeplan)
            replacements={};materialized={}
            for sheet in {c['sheet'] for c in changes}:
                raw,group=core.patch_sheet(wb,sheet,[c for c in changes if c['sheet']==sheet]);replacements[wb.sheets[sheet]['part']]=raw
                if group:materialized[sheet]=group
            # All downstream cached results are invalidated, including untouched
            # sheets, chart caches and What-If table constant output cells.
            for sheet,meta in wb.sheets.items():
                raw=replacements.get(meta['part'],wb.z.read(meta['part']))
                native=set(self.schema.get('native_table_outputs',{}).get(sheet,[]))|set(self.schema.get('native_outputs',{}).get(sheet,[]))
                if native:
                    def clear(m):
                        addr=m[1].decode()
                        if addr in native and not re.search(rb'<f(?:\s|>)',m[0]):
                            return core.xml_cell(m[0],'NON_EXECUTE' if sheet=='Valorisation' and addr=='D141' else None,'text')
                        return m[0]
                    raw=core.CELL_RX.sub(clear,raw)
                raw=invalidate_caches(raw)
                if raw!=wb.z.read(meta['part']):replacements[meta['part']]=raw
            for name in wb.z.namelist():
                if name.startswith('xl/charts/') and name.endswith('.xml'):
                    raw=invalidate_chart(wb.z.read(name))
                    if raw!=wb.z.read(name):replacements[name]=raw
            replacements['xl/workbook.xml']=core.mark_for_native_calculation(wb.z.read('xl/workbook.xml'))
            chain,removed=core.patch_calculation_chain(wb,changes)
            if chain is not None and chain!=wb.z.read('xl/calcChain.xml'):replacements['xl/calcChain.xml']=chain
            fd,name=tempfile.mkstemp(prefix='.tca-model-',suffix='.xlsm',dir=out.parent);os.close(fd);tmp=Path(name)
            with zipfile.ZipFile(tmp,'w') as zout:
                for info in wb.z.infolist():zout.writestr(copy.copy(info),replacements.get(info.filename,wb.z.read(info.filename)))
            after=core.Workbook(tmp)
            try:
                signature=core.verify_model(after,self.schema)
                planned={(c['sheet'],c['cell']):c for c in changes}
                for sheet,cs in self.schema['cells'].items():
                    for addr in cs:
                        if (sheet,addr) in planned:
                            c=planned[sheet,addr];expected=core.excel_serial(c['value'],after.date1904) if c['kind']=='date' and c['value'] is not None else c['value']
                            if after.value(sheet,addr)!=expected or after.formula(sheet,addr) is not None:raise ValueError('La valeur écrite ne correspond pas au plan.')
                        else:
                            bf=wb.formula(sheet,addr);af=after.formula(sheet,addr)
                            if bf!=af or (bf is None and wb.value(sheet,addr)!=after.value(sheet,addr)):raise ValueError('Une saisie hors plan a changé.')
                output_hash=after.hash;input_sig=after.input_signature(self.schema)
            finally:after.close()
            if core.sha(wb.path.read_bytes())!=wb.hash:raise ValueError('La source a changé pendant la transaction.')
            receipt={'schema':'tca-bp-receipt/v1','model_id':self.model_id,'source_sha256':wb.hash,'source_name':wb.path.name,
                     'output_sha256':output_hash,'output_name':out.name,'output_path':str(out),'output_input_signature':input_sig,
                     'source_unchanged':True,'changes':changes,'model_signature':signature['overall'],
                     'native_calculation':'PENDING_EXCEL','calculation_status':'RECALCULATION_REQUIRED',
                     'financial_results_available':False,'formula_and_chart_caches_invalidated':True,
                     'equivalent_shared_formula_serialization':materialized,'calculation_chain_defaults_removed':removed,
                     'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                     'checks':{'protected_formula_count':signature['protected_formula_count'],'inputs_outside_plan_preserved':True,'macros_executed':False}}
            fd,name=tempfile.mkstemp(prefix='.tca-receipt-',suffix='.json',dir=out.parent);os.close(fd);jtmp=Path(name)
            jtmp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            os.link(tmp,out);published.append(out)
            os.link(jtmp,journal);published.append(journal)
            receipt['journal_path']=str(journal)
            return receipt
        except (KeyError,TypeError,OverflowError,zipfile.BadZipFile) as exc:
            for p in reversed(published):p.unlink(missing_ok=True)
            raise ValueError('Transaction refusée : '+str(exc)) from exc
        except Exception:
            for p in reversed(published):p.unlink(missing_ok=True)
            raise
        finally:
            wb.close()
            if tmp:tmp.unlink(missing_ok=True)
            if jtmp:jtmp.unlink(missing_ok=True)
