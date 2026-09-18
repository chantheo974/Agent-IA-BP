"""Archives locales de modèles, adressées par leur contenu et vérifiées à la lecture.

Une archive est partagée par les dossiers épinglés à la même version. Elle n'est
jamais reconstruite ni remplacée implicitement à partir du modèle courant.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time

from .storage import canonical, digest
from .model_components import component_exists, component_path, read_component, MAX_COMPONENT_BYTES

TEMPLATE = "TCA_BP_Trame_generique.xlsm"
REQUIRED = frozenset({TEMPLATE, "modele.json", "build_receipt.json"})
OPTIONAL = frozenset({"catalogue_champs.json", "classification_cellules.json",
                      "graphe_dependances.json", "migrations.json", "web_profile.json"})
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
        self._compression = {}

    def describe(self, engine) -> dict:
        """Relire les sources, même si le moteur a déjà mémorisé son manifeste."""
        from .model_engine import ModelEngine
        receipt = engine.ensure_built()
        template_sha = digest(engine.template_path)
        if receipt.get("template_sha256") and receipt["template_sha256"] != template_sha:
            raise ValueError("La trame générique a changé depuis son chargement. Version refusée.")
        if isinstance(engine, ModelEngine):
            source = engine.model_dir
            names = REQUIRED | {name for name in OPTIONAL if component_exists(source / name)}
            files = {name: _sha(read_component(_plain(source / name, source))) for name in sorted(names)}
            actual = json.loads((source / "build_receipt.json").read_text(encoding="utf-8"))
            schema = json.loads(read_component(source / "modele.json"))
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
        if kind == 'MODELE':
            # An already archived legacy engine keeps its exact original pin.
            existing = source / 'seal.json'
            if existing.is_file():
                previous = json.loads(existing.read_text(encoding='utf-8'))
                if previous.get('schema') == 'tca-bp-model-archive/1':
                    return {**seal, "model_ref": _sha(canonical(seal).encode())}
            storage = {}
            for name, sha in files.items():
                physical = component_path(source / name)
                if physical.name != name:
                    stored = json.loads(existing.read_text(encoding='utf-8'))['storage'][name]
                    storage[name] = stored
                elif name.endswith('.json') and physical.stat().st_size >= 1024 * 1024:
                    key = (sha, physical.stat().st_size)
                    if key not in self._compression:
                        class Fingerprint:
                            def __init__(self): self.hash=hashlib.sha256()
                            def write(self, chunk): self.hash.update(chunk); return len(chunk)
                            def flush(self): pass
                        sink=Fingerprint()
                        with physical.open('rb') as src, gzip.GzipFile(filename='',mode='wb',fileobj=sink,mtime=0,compresslevel=6) as dst:
                            shutil.copyfileobj(src,dst)
                        self._compression[key] = sink.hash.hexdigest()
                    storage[name] = {'path':name+'.gz','codec':'gzip','size':key[1], 'stored_sha256':self._compression[key]}
                else:
                    storage[name] = {'path':name,'codec':'identity','size':physical.stat().st_size,'stored_sha256':sha}
            seal.update(schema='tca-bp-model-archive/2',storage=storage)
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
                        src = _plain(component_path(engine.model_dir / name), engine.model_dir)
                        item = seal.get('storage',{}).get(name,{'path':name,'codec':'identity'})
                        if item['codec']=='gzip' and src.name==name:
                            with src.open('rb') as source, (scratch/item['path']).open('wb') as packed, gzip.GzipFile(filename='',mode='wb',fileobj=packed,mtime=0,compresslevel=6) as dest:
                                shutil.copyfileobj(source,dest)
                        else:
                            shutil.copyfile(src, scratch/item['path'])
                else:
                    shutil.copyfile(engine.template_path, scratch / TEMPLATE)
                    raw = canonical({"model_id": engine.model_id, "schema": engine.schema, "fields": engine.catalog()}).encode()
                    (scratch / "adapter_schema.json").write_bytes(raw)
                (scratch / "seal.json").write_text(canonical(seal), encoding="utf-8")
                if seal != self.describe(engine) or any(_sha(read_component(scratch / name)) != sha for name, sha in seal["files"].items()):
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
            version=seal.get('schema')
            if version not in ('tca-bp-model-archive/1','tca-bp-model-archive/2'):
                raise ValueError('Format d’archive de modèle inconnu.')
            storage=seal.get('storage',{}) if version.endswith('/2') else {
                name:{'path':name,'codec':'identity','stored_sha256':sha} for name,sha in seal['files'].items()}
            if set(storage)!=set(seal['files']):
                raise ValueError('Index de stockage incomplet.')
            physical_names=set()
            for name,item in storage.items():
                codec=item.get('codec')
                expected=name+'.gz' if codec=='gzip' else name
                if codec not in ('gzip','identity') or item.get('path')!=expected or (codec=='gzip' and not name.endswith('.json')):
                    raise ValueError('Composant archivé invalide.')
                physical_names.add(expected)
                path=_plain(directory/expected,self.root)
                # Every public verification reads every byte. File metadata is
                # never evidence of integrity, including restored timestamps.
                if digest(path)!=item.get('stored_sha256'):
                    raise ValueError('Le modèle archivé a été modifié. Restaurer cette version exacte.')
                if codec=='identity' and item['stored_sha256']!=seal['files'][name]:
                    raise ValueError('Empreinte logique du composant incohérente.')
                if version.endswith('/2') and (type(item.get('size')) is not int or not 0<=item['size']<=MAX_COMPONENT_BYTES):
                    raise ValueError('Taille de composant hors limite.')
            if {path.name for path in directory.iterdir()} != physical_names | {'seal.json'}:
                raise ValueError("Un composant non scellé a été ajouté à l'archive du modèle.")
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
            schema = json.loads(read_component(self.root / ref / 'modele.json'))
            if schema.get('runtime_profile') == 'web-profile/1':
                from .web_model import ProfileEngine
                engine_type = ProfileEngine
            else:
                engine_type = ModelEngine
            self._engines[ref] = engine_type(self.project_root, self.root / ref)
            self._loaded_schema_hashes[ref] = _sha(canonical(self._engines[ref].schema).encode())
        engine = self._engines[ref]
        engine.ensure_built()
        if seal["kind"] == "MODELE" and _sha(canonical(engine.schema).encode()) != self._loaded_schema_hashes[ref]:
            raise ValueError("Le manifeste chargé en mémoire a été modifié. Fermer ce moteur et reprendre sa version exacte.")
        return engine
