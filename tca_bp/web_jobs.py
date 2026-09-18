"""Persistent work queue and replayable events for the local workspace."""
from __future__ import annotations

import hashlib
import json
import threading
from .storage import canonical, check_id, now, uid


class JobQueue:
    RETAINED_EVENTS = 2000

    def __init__(self, store, handler, recovery=None):
        self.store, self.handler = store, handler
        self.recovery = recovery
        self.stop = threading.Event()
        self.wake = threading.Event()
        self.threads = []
        with store.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS web_jobs(
                  id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id),
                  kind TEXT NOT NULL, lane TEXT NOT NULL, request_id TEXT NOT NULL,
                  request_hash TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL,
                  progress TEXT, result TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  UNIQUE(case_id,request_id));
                CREATE TABLE IF NOT EXISTS web_events(
                  id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL REFERENCES cases(id),
                  event TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL);
              CREATE INDEX IF NOT EXISTS web_events_case ON web_events(case_id,id);
              CREATE TABLE IF NOT EXISTS web_event_cursors(
                case_id TEXT PRIMARY KEY REFERENCES cases(id), pruned_through INTEGER NOT NULL);
            """)

    def start(self):
        if self.threads:
            return
        # An interrupted action is never silently run twice. Its committed
        # draft receipt, if any, remains available for an explicit retry.
        with self.store.connection() as db:
            interrupted = db.execute("SELECT * FROM web_jobs WHERE status='RUNNING'").fetchall()
            db.execute("UPDATE web_jobs SET status='INTERRUPTED',error=?,updated_at=? WHERE status='RUNNING'",
                       ("Serveur interrompu. Examiner le brouillon et les versions avant de relancer.", now()))
            if self.recovery:
                self.recovery(db, interrupted)
        for lane in ('excel', 'chat'):
            thread = threading.Thread(target=self._worker, args=(lane,), daemon=True, name='tca-'+lane)
            thread.start()
            self.threads.append(thread)

    def close(self):
        self.stop.set()
        self.wake.set()
        for thread in self.threads:
            thread.join(timeout=2)

    def emit(self, case_id, event='refresh', data=None, db=None):
        if db is None:
            with self.store.connection() as conn:
                return self.emit(case_id, event, data, conn)
        cursor = db.execute("INSERT INTO web_events(case_id,event,data,created_at) VALUES(?,?,?,?)",
                            (case_id, event, canonical(data or {}), now()))
        # Ce flux sert au rattrapage court d'un navigateur ; l'historique auditable
        # reste dans history et web_jobs. Sans purge la table ne décroît jamais.
        # Les identifiants restent croissants : un curseur ancien reçoit toujours
        # les événements suivants, jamais un identifiant déjà consommé.
        boundary = db.execute("SELECT id FROM web_events WHERE case_id=? ORDER BY id DESC LIMIT 1 OFFSET ?",
                              (case_id, self.RETAINED_EVENTS)).fetchone()
        if boundary:
            db.execute("INSERT INTO web_event_cursors VALUES(?,?) ON CONFLICT(case_id) DO UPDATE"
                       " SET pruned_through=MAX(pruned_through,excluded.pruned_through)", (case_id,boundary['id']))
            db.execute("DELETE FROM web_events WHERE case_id=? AND id<=?", (case_id,boundary['id']))
        return cursor.lastrowid

    def replay_status(self, case_id, after=0):
        """A pruned cursor cannot reconstruct state: ask the UI for a full read."""
        with self.store.connection() as db:
            row = db.execute('SELECT pruned_through FROM web_event_cursors WHERE case_id=?',(case_id,)).fetchone()
            latest = db.execute('SELECT MAX(id) FROM web_events WHERE case_id=?',(case_id,)).fetchone()[0] or 0
        return {'resync_required': bool(row and after < row['pruned_through']) or after > latest,
                'latest_event_id':latest, 'pruned_through':row['pruned_through'] if row else 0}

    def lookup(self, case_id, request_id):
        with self.store.connection() as db:
            row = db.execute('SELECT * FROM web_jobs WHERE case_id=? AND request_id=?',
                             (case_id,check_id(request_id))).fetchone()
        return self.public(row) if row else None

    def events(self, case_id, after=0):
        with self.store.connection() as db:
            rows = db.execute("SELECT * FROM web_events WHERE case_id=? AND id>? ORDER BY id LIMIT 200", (case_id, after)).fetchall()
        return [{**dict(row), 'data': json.loads(row['data'])} for row in rows]

    @staticmethod
    def public(row):
        result = dict(row)
        for key in ('payload', 'request_hash', 'lane'):
            result.pop(key, None)
        for key in ('progress', 'result'):
            result[key] = json.loads(result[key]) if result.get(key) else None
        return result

    def list(self, case_id):
        with self.store.connection() as db:
            return [self.public(row) for row in db.execute("SELECT * FROM web_jobs WHERE case_id=? ORDER BY created_at DESC LIMIT 100", (case_id,))]

    def submit(self, case_id, kind, payload=None, request_id=None):
        request_id = check_id(request_id or uid('req_'))
        payload = payload or {}
        fingerprint = hashlib.sha256(canonical([kind, payload]).encode()).hexdigest()
        with self.store.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute("SELECT * FROM web_jobs WHERE case_id=? AND request_id=?", (case_id, request_id)).fetchone()
            if old:
                if old['request_hash'] != fingerprint:
                    raise ValueError('Cette demande existe avec un contenu différent.')
                return {'job': self.public(old), 'replayed': True}
            timestamp, job_id = now(), uid('job_')
            stored_payload = dict(payload)
            if kind == 'restore' and not stored_payload.get('operation_id'):
                current = db.execute('SELECT revision,sha256 FROM cases WHERE id=?', (case_id,)).fetchone()
                if current is None:
                    raise ValueError('Dossier inconnu.')
                stored_payload.update(operation_id=job_id, expected_revision=current['revision'], source_sha256=current['sha256'])
            db.execute("INSERT INTO web_jobs VALUES(?,?,?,?,?,?,?,'QUEUED',NULL,NULL,NULL,?,?)",
                       (job_id, case_id, kind, 'chat' if kind == 'chat' else 'excel', request_id,
                        fingerprint, canonical(stored_payload), timestamp, timestamp))
            row = db.execute('SELECT * FROM web_jobs WHERE id=?', (job_id,)).fetchone()
            self.emit(case_id, 'job', self.public(row), db)
        self.wake.set()
        return {'job': self.public(row)}

    def _worker(self, lane):
        while not self.stop.is_set():
            with self.store.connection() as db:
                db.execute('BEGIN IMMEDIATE')
                job = db.execute("SELECT * FROM web_jobs WHERE lane=? AND status='QUEUED' ORDER BY created_at LIMIT 1", (lane,)).fetchone()
                if job:
                    db.execute("UPDATE web_jobs SET status='RUNNING',updated_at=? WHERE id=?", (now(), job['id']))
            if not job:
                self.wake.wait(0.5)
                self.wake.clear()
                continue
            def progress(data):
                with self.store.connection() as db:
                    db.execute('UPDATE web_jobs SET progress=?,updated_at=? WHERE id=?', (canonical(data), now(), job['id']))
                    self.emit(job['case_id'], 'job', {'id': job['id'], 'status': 'RUNNING', 'progress': data}, db)
            try:
                progress({'message': 'Traitement en cours', 'kind': job['kind']})
                result = self.handler(dict(job), json.loads(job['payload']), progress)
                with self.store.connection() as db:
                    status='INTERRUPTED' if isinstance(result,dict) and result.get('status')=='INTERRUPTED' else 'SUCCEEDED'
                    db.execute("UPDATE web_jobs SET status=?,result=?,updated_at=? WHERE id=?", (status,canonical(result), now(), job['id']))
            except Exception as exc:
                # Provider failures are sanitised by the adapter. Never persist
                # request headers, raw HTTP errors, or arbitrary repr objects.
                from .web_settings import ProviderError
                error = str(exc) if isinstance(exc, (ValueError, FileNotFoundError, ProviderError)) else 'Le traitement a échoué. Le brouillon et les versions restent conservés.'
                with self.store.connection() as db:
                    db.execute("UPDATE web_jobs SET status='FAILED',error=?,updated_at=? WHERE id=?", (error[:1500], now(), job['id']))
            with self.store.connection() as db:
                current = db.execute('SELECT * FROM web_jobs WHERE id=?', (job['id'],)).fetchone()
                self.emit(job['case_id'], 'job', self.public(current), db)
                self.emit(job['case_id'], 'refresh', {}, db)
