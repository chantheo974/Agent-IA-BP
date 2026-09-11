"""État persistant, écritures atomiques et exclusion mutuelle par dossier."""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import threading
import time
import uuid


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def uid(prefix: str = "") -> str:
    return prefix + uuid.uuid4().hex


def digest(path: Path) -> str:
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", value):
        raise ValueError("Identifiant de dossier ou de demande invalide.")
    return value


def confined(root: Path, relative: str | Path) -> Path:
    root = root.resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Le chemin sort de l'espace du dossier.")
    return candidate


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
            stream.flush()
            os.fsync(stream.fileno())
        # Un antivirus ou OneDrive peut tenir brièvement l'ancienne version
        # sous Windows. Réessayer le même remplacement atomique, sans effacer
        # la destination ni perdre sa version précédente.
        for attempt in range(8):
            try:
                os.replace(name, path)
                break
            except PermissionError as error:
                if os.name != "nt" or getattr(error, "winerror", None) not in (5, 32, 33) or attempt == 7:
                    raise
                time.sleep(0.025 * 2 ** min(attempt, 4))
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "tca_bp.sqlite3"
        self._lock = threading.RLock()
        with self.connection() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS clients(
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, normalized TEXT NOT NULL UNIQUE);
                CREATE TABLE IF NOT EXISTS cases(
                    id TEXT PRIMARY KEY, client_id TEXT NOT NULL REFERENCES clients(id),
                    name TEXT NOT NULL, model_id TEXT NOT NULL, revision INTEGER NOT NULL,
                    workbook TEXT NOT NULL, sha256 TEXT NOT NULL, calculation_status TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, field_states TEXT NOT NULL DEFAULT '{}');
                CREATE TABLE IF NOT EXISTS sources(
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), title TEXT NOT NULL,
                    path TEXT, text TEXT NOT NULL, sha256 TEXT NOT NULL, kind TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS plans(
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), request_id TEXT NOT NULL,
                    request_hash TEXT NOT NULL, source_sha256 TEXT NOT NULL, status TEXT NOT NULL,
                    payload TEXT NOT NULL, result TEXT, created_at TEXT NOT NULL,
                    UNIQUE(case_id, request_id));
                CREATE TABLE IF NOT EXISTS history(
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), kind TEXT NOT NULL,
                    details TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS questions(
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), topic TEXT NOT NULL,
                    question TEXT NOT NULL, status TEXT NOT NULL, answer TEXT, created_at TEXT NOT NULL,
                    UNIQUE(case_id, topic, question));
                CREATE TABLE IF NOT EXISTS records(
                    case_id TEXT NOT NULL REFERENCES cases(id), record_key TEXT NOT NULL,
                    plan_id TEXT NOT NULL REFERENCES plans(id), PRIMARY KEY(case_id,record_key));
            """)
            # Les dossiers historiques restent non épinglés : aucun modèle
            # courant n'est déduit de leur seul identifiant fonctionnel.
            columns = {row[1] for row in db.execute("PRAGMA table_info(cases)")}
            for column in ("model_ref", "template_sha256", "schema_sha256"):
                if column not in columns:
                    db.execute(f"ALTER TABLE cases ADD COLUMN {column} TEXT")

    @contextlib.contextmanager
    def connection(self):
        db = sqlite3.connect(self.database, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=30000")
        try:
            with db:
                yield db
        finally:
            db.close()

    def case_dir(self, case_id: str) -> Path:
        return confined(self.root / "dossiers", check_id(case_id))

    @contextlib.contextmanager
    def case_lock(self, case_id: str):
        """Refuse une seconde transaction, y compris depuis un autre processus.

        Un verrou laissé par un arrêt brutal n'est jamais supprimé sur une simple
        supposition d'ancienneté. La commande recover présente le verrou et les
        artefacts ; elle ne suppose pas qu'un PID enregistré est encore actif.
        """
        folder = self.case_dir(case_id)
        if not folder.is_dir():
            raise ValueError("Dossier inconnu.")
        path = folder / ".transaction.lock"
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise ValueError("Ce dossier a une transaction en cours. Attendre sa fin ou utiliser le diagnostic de reprise.")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(canonical({"pid": os.getpid(), "started_at": now()}))
            yield
        finally:
            path.unlink(missing_ok=True)

    def history(self, db, case_id: str, kind: str, details) -> None:
        db.execute("INSERT INTO history VALUES(?,?,?,?,?)", (uid("evt_"), case_id, kind, canonical(details), now()))
