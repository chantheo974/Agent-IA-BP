"""Resumable simulations of an exact business draft on an isolated scenario.

The persistent Excel lane runs the existing preview, apply and recalculate
services. Every checkpoint is recoverable from their authoritative receipts;
publishing the parent is deliberately a separate human-approved transaction.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .cockpit_workspace import CockpitWorkspace, _can_propose
from .decision_model import create_scenario, read_annual_metrics, read_series
from .model_registry import model_pin
from .storage import canonical


KIND = 'cockpit_simulation'
JOB_KIND = 'decision_' + KIND


def _sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _operations(draft):
    return [{key: value for key, value in operation.items() if not key.startswith('_')}
            for operation in draft.get('operations', [])]


def _same_base(row, snapshot):
    return (row['revision'] == snapshot['base_revision'] and row['sha256'] == snapshot['base_sha256']
            and model_pin(row) == snapshot['model'])


class CockpitSimulations:
    def __init__(self, decision):
        self.d = decision
        self.app, self.work, self.store = decision.app, decision.work, decision.store
        self.cockpit = CockpitWorkspace(decision)

    def _capture(self, case_id):
        with self.d.lock:
            row, engine, profile, records, fields = self.cockpit._context(case_id)
            draft = self.work.draft(case_id)
            if not draft.get('id') or not draft.get('operations'):
                raise ValueError('Préparer des hypothèses au brouillon avant de simuler.')
            if draft.get('status') == 'PREPARING' or draft.get('conflicts'):
                raise ValueError('Attendre la fin de l’aperçu et résoudre les conflits avant de simuler.')
            if draft['revision'] != row['revision'] or draft['source_sha256'] != row['sha256']:
                raise ValueError('Le brouillon ne correspond plus à la référence courante.')
            self.cockpit._ordinary_draft(case_id)
            operations = _operations(draft)
            known = {(f['sheet'], cell): f for f in fields for cell in f.get('cells', [])}
            for op in operations:
                field = known.get((op.get('sheet'), op.get('cell')))
                if not field or not _can_propose(field):
                    raise ValueError('Le brouillon contient une entrée hors du catalogue métier autorisé.')
            def verify(wb, current):
                self.cockpit._assert_snapshot(row, current)
                if any(wb.formula(op['sheet'], op['cell']) is not None for op in operations):
                    raise ValueError('Les formules et défauts calculés relèvent du parcours de maintenance.')
            self.work._read(case_id, verify)
            sources = []
            for source_id in sorted({op.get('evidence_id', '') for op in operations}):
                source = self.d.source(case_id, source_id)
                sources.append({key: source[key] for key in ('id', 'title', 'sha256')})
            self.cockpit._assert_snapshot(row)
            latest = self.work.draft(case_id)
            if latest.get('id') != draft['id'] or _operations(latest) != operations or latest.get('conflicts'):
                raise ValueError('Le brouillon a changé pendant sa lecture. Examiner les nouvelles hypothèses.')
            snapshot = {'case_id': case_id, 'base_revision': row['revision'], 'base_sha256': row['sha256'],
                        'model': model_pin(row), 'draft_id': draft['id'], 'operations': operations,
                        'operations_sha256': _sha(operations), 'sources': sources}
            snapshot['draft_fingerprint'] = _sha(snapshot)
            affected = {op['sheet'] for op in operations}
            sheets = self.cockpit._sheets(engine, profile, records, fields)
            return snapshot, draft, [{'id': s['id'], 'name': s['name'], 'label': s['label']}
                                     for s in sheets if s['name'] in affected]

    def impacts(self, case_id):
        row = self.app._row(case_id)
        draft = self.work.draft(case_id)
        snapshot, affected, reasons = {}, [], []
        try:
            snapshot, draft, affected = self._capture(case_id)
        except ValueError as error:
            reasons.append(str(error))
        return {'case_id': case_id, 'revision': row['revision'], 'draft_id': draft.get('id'),
                'draft_fingerprint': snapshot.get('draft_fingerprint'), 'status': draft['status'],
                'operations': snapshot.get('operations', _operations(draft)), 'changes': draft.get('changes', []),
                'sources': snapshot.get('sources', []), 'affected_sheets': affected,
                'diagnostics': draft.get('diagnostics', []), 'conflicts': draft.get('conflicts', []),
                'can_simulate': not reasons, 'blocking_reasons': reasons,
                'notice': 'Entrées modifiées et contrôles disponibles. Les effets financiers exigent le calcul de la copie de scénario.'}

    def submit(self, case_id, body):
        self.cockpit._command(body, {'draft_id', 'draft_fingerprint', 'name'})
        if not isinstance(body.get('name'), str) or not 1 <= len(body['name'].strip()) <= 160:
            raise ValueError('Nom de simulation requis (160 caractères maximum).')
        request_body = {key: value for key, value in body.items() if key != 'request_id'}
        with self.d.lock:
            with self.store.connection() as db:
                old = db.execute('SELECT * FROM web_jobs WHERE case_id=? AND request_id=?',
                                 (case_id, body['request_id'])).fetchone()
            if old:
                if old['kind'] != JOB_KIND or json.loads(old['payload']).get('request_body') != request_body:
                    raise ValueError('Cette demande existe avec un contenu différent.')
                return {'job': self.work.jobs.public(old), 'replayed': True}
            self.d.check_revision(case_id, body['expected_revision'])
            snapshot, _, _ = self._capture(case_id)
            if body.get('draft_id') != snapshot['draft_id'] or body.get('draft_fingerprint') != snapshot['draft_fingerprint']:
                raise ValueError('Les hypothèses ont changé. Examiner les nouveaux impacts avant de simuler.')
            self.d.require_space(case_id, 1)
            simulation_id = 'simulation_' + _sha([case_id, body['request_id']])[:24]
            # A saved QUEUED object is harmless if queue submission is interrupted.
            # Its deterministic ID and request body let that same intention resume.
            previous = next((s for s in self.d.objects(case_id, KIND) if s['id'] == simulation_id), None)
            if previous and previous.get('request_body') != request_body:
                raise ValueError('Cette intention conserve déjà une autre simulation.')
            if not previous:
                self.d.save(case_id, KIND, {'name': body['name'].strip(), 'snapshot': snapshot,
                                           'request_body': request_body, 'saved': False, 'stage': 'QUEUED'},
                            status='QUEUED', object_id=simulation_id)
            return self.work.jobs.submit(case_id, JOB_KIND,
                                         {'simulation_id': simulation_id, 'request_body': request_body}, body['request_id'])

    def _save(self, case_id, item, *, db=None, **changes):
        payload = {key: value for key, value in item.items()
                   if key not in ('id', 'case_id', 'kind', 'status', 'revision', 'created_at', 'updated_at')}
        status = changes.pop('status', item['status'])
        return self.d.save(case_id, KIND, {**payload, **changes}, status=status, object_id=item['id'], db=db)

    def _job(self, case_id, simulation_id):
        with self.store.connection() as db:
            rows = db.execute('SELECT * FROM web_jobs WHERE case_id=? AND kind=? ORDER BY rowid DESC',
                              (case_id, JOB_KIND)).fetchall()
        return next((self.work.jobs.public(row) for row in rows
                     if json.loads(row['payload']).get('simulation_id') == simulation_id), None)

    def public(self, case_id, item):
        snapshot = item['snapshot']
        current = self.app._row(case_id)
        public = {key: item[key] for key in ('id', 'case_id', 'name', 'status', 'stage', 'saved', 'created_at', 'updated_at')}
        public.update({key: snapshot[key] for key in ('base_revision', 'base_sha256', 'draft_id', 'draft_fingerprint')})
        public.update(scenario_case_id=item.get('scenario_case_id'), stale=not _same_base(current, snapshot),
                      error=item.get('error'), job=self._job(case_id, item['id']))
        result = item.get('observations')
        if result and item['status'] == 'READY':
            child = self.app._row(item['scenario_case_id'])
            if child['revision'] == result['revision'] and child['sha256'] == result['sha256'] and model_pin(child) == snapshot['model']:
                try:
                    self.app._workbook(child)
                except ValueError:
                    public.update(status='NEEDS_REVIEW', error='La copie de scénario ou son modèle a changé ; ses résultats sont masqués.')
                else:
                    public.update(result)
            else:
                public.update(status='NEEDS_REVIEW', error='La copie de scénario a changé depuis son calcul ; ses anciens résultats sont masqués.')
        elif public['job'] and public['job']['status'] in ('FAILED', 'INTERRUPTED'):
            public.update(status=public['job']['status'], error=public['job'].get('error') or item.get('error'))
        return public

    def list(self, case_id):
        return {'simulations': [self.public(case_id, item) for item in self.d.objects(case_id, KIND)]}

    def get(self, case_id, simulation_id):
        return self.public(case_id, self.d.get(case_id, simulation_id, KIND))

    def keep(self, case_id, simulation_id, body):
        self.cockpit._command(body, {'name'})
        def action():
            self.d.check_revision(case_id, body['expected_revision'])
            item = self.d.get(case_id, simulation_id, KIND)
            if self.public(case_id, item)['status'] != 'READY':
                raise ValueError('Seule une simulation calculée et intacte peut être conservée.')
            name = body.get('name', item['name'])
            if not isinstance(name, str) or not 1 <= len(name.strip()) <= 160:
                raise ValueError('Nom de scénario requis (160 caractères maximum).')
            scenario = self.d.get(case_id, item['scenario_record_id'], 'scenario')
            scenario_payload = {key: value for key, value in scenario.items()
                                if key not in ('id', 'case_id', 'kind', 'status', 'revision', 'created_at', 'updated_at')}
            with self.store.connection() as db:
                # One existing copy becomes available to the shared comparison
                # and documentary services; keep never creates another workbook.
                self.d.save(case_id, 'scenario', {**scenario_payload, 'purpose': 'user', 'name': name.strip()},
                            object_id=scenario['id'], status=scenario['status'], db=db)
                item = self._save(case_id, item, saved=True, name=name.strip(), db=db)
            return self.public(case_id, item)
        return self.d.request(case_id, 'cockpit/simulations/' + simulation_id + '/keep', body, action)

    def propose_adoption(self, case_id, simulation_id, body):
        self.cockpit._command(body, set())
        def action():
            item = self.d.get(case_id, simulation_id, KIND)
            snapshot = item['snapshot']
            self.d.check_revision(case_id, body['expected_revision'])
            if not _same_base(self.app._row(case_id), snapshot):
                raise ValueError('La référence a changé depuis la simulation. Préparer une nouvelle simulation.')
            if self.public(case_id, item)['status'] != 'READY':
                raise ValueError('Le scénario doit être calculé et inchangé avant de proposer son adoption.')
            for source in snapshot['sources']:
                if self.d.source(case_id, source['id'])['sha256'] != source['sha256']:
                    raise ValueError('Une source a changé depuis la simulation.')
            draft = self.work.draft(case_id)
            if draft.get('operations') or draft.get('conflicts'):
                if (draft.get('conflicts') or draft.get('status') == 'PREPARING'
                        or draft['revision'] != snapshot['base_revision'] or draft['source_sha256'] != snapshot['base_sha256']
                        or _sha(_operations(draft)) != snapshot['operations_sha256']):
                    raise ValueError('Le brouillon parent est différent. Conserver ou abandonner ce lot avant de préparer l’adoption.')
            else:
                draft = self.d.propose(case_id, deepcopy(snapshot['operations']), snapshot['base_revision'])
            with self.store.connection() as db:
                self.store.history(db, case_id, 'SIMULATION_ADOPTION_PROPOSEE',
                                   {'simulation_id': simulation_id, 'scenario_case_id': item['scenario_case_id'],
                                    'draft_id': draft['id'], 'base_revision': snapshot['base_revision'],
                                    'draft_fingerprint': snapshot['draft_fingerprint'],
                                    'reason': 'Hypothèses de la simulation proposées ; aperçu et approbation parent requis.'})
            return draft
        return self.d.request(case_id, 'cockpit/simulations/' + simulation_id + '/adoption', body, action)

    def _scenario_copy(self, case_id, item):
        candidates = [s for s in self.d.objects(case_id, 'scenario')
                      if s.get('purpose') in (KIND, 'user') and s.get('hypotheses') == [{'cockpit_simulation_id': item['id']}]]
        if len(candidates) > 1:
            raise ValueError('Plusieurs copies correspondent à cette simulation. Examiner leur filiation.')
        if candidates:
            return candidates[0]
        snapshot = item['snapshot']
        if not _same_base(self.app._row(case_id), snapshot):
            raise ValueError('La référence a changé avant la création de la copie de scénario.')
        return create_scenario(self.d, case_id, {'name': item['name'], 'expected_revision': snapshot['base_revision'],
                                               'purpose': KIND, 'hypotheses': [{'cockpit_simulation_id': item['id']}]})

    def _recalculation_receipt(self, child_id, apply_receipt):
        row = self.app._row(child_id)
        self.app._workbook(row)
        with self.store.connection() as db:
            events = db.execute("SELECT details FROM history WHERE case_id=? AND kind='RECALCUL_EXCEL' ORDER BY rowid DESC", (child_id,)).fetchall()
        for event in events:
            receipt = json.loads(event['details'])
            if (receipt.get('source_sha256') == apply_receipt['output_sha256']
                    and receipt.get('revision') == apply_receipt['revision'] + 1
                    and receipt.get('revision') == row['revision']
                    and receipt.get('output_sha256') == row['sha256'] and receipt.get('adopted')
                    and model_pin(receipt) == model_pin(row)):
                return receipt
        if row['revision'] != apply_receipt['revision'] or row['sha256'] != apply_receipt['output_sha256']:
            raise ValueError('La copie a changé sans reçu de recalcul correspondant. Examiner le scénario avant toute reprise.')
        return None

    def _observations(self, child_id):
        case = self.app.get_case(child_id)
        if not case.get('outputs_current'):
            raise ValueError('Le recalcul ne fournit pas encore de résultats courants ; examiner les diagnostics du scénario.')
        return {'revision': case['revision'], 'sha256': case['sha256'],
                'calculation_status': case['calculation_status'], 'metrics': self.d.metrics(child_id),
                'annual_metrics': read_annual_metrics(self.d, child_id), 'series': read_series(self.d, child_id)}

    def run(self, job, payload, progress):
        case_id = job['case_id']
        item = self.d.get(case_id, payload['simulation_id'], KIND)
        snapshot = item['snapshot']
        if item['status'] == 'READY':
            result = self.public(case_id, item)
            if result['status'] != 'READY':
                raise ValueError(result['error'])
            return result
        item = self._save(case_id, item, status='RUNNING', error=None, observations=None)
        try:
            progress({'message': 'Création ou reprise de la copie isolée.'})
            copy = self._scenario_copy(case_id, item)
            child_id = copy['scenario_case_id']
            if copy['base_revision'] != snapshot['base_revision'] or copy['base_sha256'] != snapshot['base_sha256']:
                raise ValueError('La copie ne correspond pas à la référence capturée.')
            source_map = copy['origin']['sources']
            operations = deepcopy(snapshot['operations'])
            source_hashes = {source['id']: source['sha256'] for source in snapshot['sources']}
            for op in operations:
                source_id = op['evidence_id']
                child_source = source_map.get(source_id)
                if not child_source or self.d.source(child_id, child_source)['sha256'] != source_hashes[source_id]:
                    raise ValueError('Les preuves copiées ne correspondent pas aux sources de la simulation.')
                op['evidence_id'] = child_source
            child = self.app._row(child_id)
            if model_pin(child) != snapshot['model']:
                raise ValueError('Le modèle de la copie diffère du modèle simulé.')
            item = self._save(case_id, item, scenario_case_id=child_id, scenario_record_id=copy['id'], stage='COPY_READY')
            if not item.get('child_draft_id'):
                if child['revision'] != 0 or child['sha256'] != snapshot['base_sha256']:
                    raise ValueError('La copie a été modifiée avant la préparation du lot simulé.')
                draft = self.work.draft(child_id)
                if draft.get('operations') and (_operations(draft) != operations or draft.get('conflicts')):
                    raise ValueError('Le brouillon de la copie a été modifié indépendamment de cette simulation.')
                if not draft.get('operations'):
                    draft = self.d.propose(child_id, operations, 0)
                item = self._save(case_id, item, child_draft_id=draft['id'], stage='DRAFT_READY')
            if not item.get('child_approval_token'):
                draft = self.work.draft(child_id)
                if draft.get('id') != item['child_draft_id'] or _operations(draft) != operations or draft.get('conflicts'):
                    raise ValueError('Le lot de la copie ne correspond plus aux hypothèses capturées.')
                if draft.get('status') != 'READY':
                    progress({'message': 'Aperçu et contrôles dans la copie de scénario.'})
                    draft = self.work.preview(child_id, item['child_draft_id'], progress)
                if draft.get('status') != 'READY' or not draft.get('approval_token'):
                    raise ValueError('Les contrôles bloquent le brouillon de la copie. Examiner les diagnostics avant de reprendre.')
                item = self._save(case_id, item, child_approval_token=draft['approval_token'], stage='PREVIEW_READY')
            # apply is already idempotent on this exact draft and reviewed token.
            receipt = self.work.apply(child_id, item['child_draft_id'], item['child_approval_token'])
            item = self._save(case_id, item, child_apply_receipt=receipt, stage='APPLIED_IN_COPY')
            calculation = self._recalculation_receipt(child_id, receipt)
            if calculation is None:
                item = self._save(case_id, item, stage='CALCULATING')
                progress({'message': 'Recalcul Excel de la copie. La référence reste inchangée.'})
                self.app.recalculate(child_id)
                calculation = self._recalculation_receipt(child_id, receipt)
                if calculation is None:
                    raise ValueError('Le reçu du recalcul ne correspond pas à la copie simulée.')
            item = self._save(case_id, item, calculation_receipt=calculation, stage='READING_RESULTS')
            observations = self._observations(child_id)
            item = self._save(case_id, item, status='READY', stage='READY', observations=observations, error=None)
            return self.public(case_id, item)
        except Exception as error:
            message = str(error) if isinstance(error, (ValueError, FileNotFoundError)) else 'Simulation interrompue. Les étapes et preuves sont conservées ; reprendre cette tâche après examen.'
            self._save(case_id, item, status='FAILED', error=message, observations=None)
            raise
