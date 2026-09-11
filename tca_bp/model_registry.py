"""Archives locales de modèles, adressées par leur contenu et vérifiées à la lecture.

Une archive est partagée par les dossiers épinglés à la même version. Elle n'est
jamais reconstruite ni remplacée implicitement à partir du modèle courant.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time

from .storage import canonical, digest

TEMPLATE = "TCA_BP_Trame_generique.xlsm"
REQUIRED = frozenset({TEMPLATE, "modele.json", "build_receipt.json"})
OPTIONAL = frozenset({"catalogue_champs.json", "classification_cellules.json",
                      "graphe_dependances.json", "migrations.json"})
PIN_KEYS = ("model_id", "model_ref", "template_sha256", "schema_sha256")


def model_pin(value: dict) -> dict:
    return {key: value.get(key) for key in PIN_KEYS}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _plain(path: Path, root: Path) -> Path:
    """Refuser aussi les jonctions Windows et les parents liés."""
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Une archive de modèle sort de son répertoire.")
    for part in (path, *path.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError("Un lien ne peut servir de référence de modèle.")
        if part == root:
            break
    return path


class ModelRegistry:
    def __init__(self, root: Path, project_root: Path):
        self.root = Path(root).resolve()
        self.project_root = Path(project_root).resolve()
        self._engines = {}
        self._loaded_schema_hashes = {}

    def describe(self, engine) -> dict:
        """Relire les sources, même si le moteur a déjà mémorisé son manifeste."""
        from .model_engine import ModelEngine
        receipt = engine.ensure_built()
        template_sha = digest(engine.template_path)
        if receipt.get("template_sha256") and receipt["template_sha256"] != template_sha:
            raise ValueError("La trame générique a changé depuis son chargement. Version refusée.")
        if isinstance(engine, ModelEngine):
            source = engine.model_dir
            names = REQUIRED | {name for name in OPTIONAL if (source / name).exists()}
            files = {name: digest(_plain(source / name, source)) for name in sorted(names)}
            actual = json.loads((source / "build_receipt.json").read_text(encoding="utf-8"))
            schema = json.loads((source / "modele.json").read_text(encoding="utf-8"))
            if (actual.get("template_sha256") != template_sha or actual.get("schema_sha256") != files["modele.json"]
                    or receipt.get("schema_sha256") != files["modele.json"]
                    or actual.get("model_id") != engine.model_id or schema.get("model_id") != engine.model_id
                    or schema != engine.schema):
                raise ValueError("Le manifeste ou le reçu du modèle a changé. Version refusée.")
            schema_sha = files["modele.json"]
            kind = "MODELE"
        else:
            # Adaptateurs injectés des tests : aucune conversion en moteur réel.
            raw = canonical({"model_id": engine.model_id, "schema": engine.schema, "fields": engine.catalog()}).encode()
            schema_sha = _sha(raw)
            files = {TEMPLATE: template_sha, "adapter_schema.json": schema_sha}
            kind = "ADAPTATEUR_INJECTE"
        seal = {"schema": "tca-bp-model-archive/1", "kind": kind, "model_id": engine.model_id,
                "template_sha256": template_sha, "schema_sha256": schema_sha, "files": files}
        return {**seal, "model_ref": _sha(canonical(seal).encode())}

    def register(self, engine) -> dict:
        seal = self.describe(engine)
        self.root.mkdir(parents=True, exist_ok=True)
        destination = _plain(self.root / seal["model_ref"], self.root)
        if destination.exists():
            self.verify(model_pin(seal))
        else:
            scratch = Path(tempfile.mkdtemp(prefix=".sealing-", dir=self.root))
            try:
                if seal["kind"] == "MODELE":
                    for name in seal["files"]:
                        shutil.copyfile(_plain(engine.model_dir / name, engine.model_dir), scratch / name)
                else:
                    shutil.copyfile(engine.template_path, scratch / TEMPLATE)
                    raw = canonical({"model_id": engine.model_id, "schema": engine.schema, "fields": engine.catalog()}).encode()
                    (scratch / "adapter_schema.json").write_bytes(raw)
                if seal != self.describe(engine) or any(digest(scratch / name) != sha for name, sha in seal["files"].items()):
                    raise ValueError("La source du modèle a changé pendant son archivage.")
                (scratch / "seal.json").write_text(canonical(seal), encoding="utf-8")
                for attempt in range(8):
                    try:
                        scratch.rename(destination)
                        break
                    except OSError as error:
                        # Une autre instance a pu publier la même référence.
                        # Sa présence n'autorise jamais son remplacement.
                        if destination.exists():
                            self.verify(model_pin(seal))
                            break
                        # Un antivirus ou un synchroniseur Windows peut tenir
                        # brièvement le répertoire qui vient d'être écrit.
                        if os.name != "nt" or getattr(error, "winerror", None) not in (5, 32, 33) or attempt == 7:
                            raise
                        time.sleep(0.025 * 2 ** min(attempt, 4))
            finally:
                if scratch.exists() and scratch.resolve().is_relative_to(self.root):
                    shutil.rmtree(scratch)
        if seal["kind"] == "ADAPTATEUR_INJECTE":
            self._engines[seal["model_ref"]] = engine
        return model_pin(seal)

    def verify(self, pin: dict) -> dict:
        ref = pin.get("model_ref")
        if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{64}", ref):
            raise ValueError("Ce dossier n'est pas épinglé à une version exacte. Rattachement explicite requis, avec la preuve de sa copie initiale v0000.")
        directory = _plain(self.root / ref, self.root)
        try:
            seal = json.loads(_plain(directory / "seal.json", self.root).read_text(encoding="utf-8"))
            unsigned = {key: value for key, value in seal.items() if key != "model_ref"}
            if _sha(canonical(unsigned).encode()) != ref or model_pin(seal) != model_pin(pin):
                raise ValueError("L'identité du modèle archivé ne correspond pas au dossier. Migration implicite refusée.")
            allowed = REQUIRED | OPTIONAL if seal["kind"] == "MODELE" else {TEMPLATE, "adapter_schema.json"}
            required = REQUIRED if seal["kind"] == "MODELE" else allowed
            if not required <= set(seal["files"]) <= allowed:
                raise ValueError("Liste des composants du modèle archivé invalide.")
            if {path.name for path in directory.iterdir()} != set(seal["files"]) | {"seal.json"}:
                raise ValueError("Un composant non scellé a été ajouté à l'archive du modèle.")
            for name, sha in seal["files"].items():
                if digest(_plain(directory / name, self.root)) != sha:
                    raise ValueError("Le modèle archivé a été modifié. Restaurer cette version exacte ; aucune migration automatique n'est effectuée.")
            return seal
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Version exacte du modèle absente ou incomplète. Restaurer son archive ; le modèle courant ne sera pas substitué.") from exc

    def resolve(self, pin: dict, *, injected_engine=None):
        seal = self.verify(pin)
        ref = seal["model_ref"]
        if seal["kind"] == "ADAPTATEUR_INJECTE":
            engine = self._engines.get(ref, injected_engine)
            if engine is None or model_pin(self.describe(engine)) != model_pin(pin):
                raise ValueError("L'adaptateur injecté de cette version exacte est indisponible.")
            self._engines[ref] = engine
        elif ref not in self._engines:
            from .model_engine import ModelEngine
            self._engines[ref] = ModelEngine(self.project_root, self.root / ref)
            self._loaded_schema_hashes[ref] = _sha(canonical(self._engines[ref].schema).encode())
        engine = self._engines[ref]
        engine.ensure_built()
        if seal["kind"] == "MODELE" and _sha(canonical(engine.schema).encode()) != self._loaded_schema_hashes[ref]:
            raise ValueError("Le manifeste chargé en mémoire a été modifié. Fermer ce moteur et reprendre sa version exacte.")
        return engine
