"""Conditionner l'application et son modèle déjà construit, sans données client.

Bibliothèque standard uniquement. Aucune reconstruction, exécution Excel, macro
ou installation de dépendance n'est effectuée pendant le conditionnement.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile
import io
import sys

# Résolution locale déterministe, également depuis un autre répertoire courant.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tca_bp.privacy import audit_workbook_documentation, private_fragment_found


MODEL_PREFIX = "models/generic-v1/"
TEMPLATE = "TCA_BP_Trame_generique.xlsm"
MODEL_FILES = frozenset({TEMPLATE, "modele.json", "catalogue_champs.json", "classification_cellules.json",
                         "graphe_dependances.json", "migrations.json", "build_receipt.json"})
ROOT_FILES = frozenset({"README.md", "pyproject.toml", "Installer_TCA_BP.ps1", "Lancer_TCA_BP.cmd", "run_mcp.py"})
CLIENT_README = "docs/README_CLIENT.md"
DOC_FILES = frozenset({"docs/" + name for name in ("ARCHITECTURE.md", "INTERFACE.md",
    "AGENTS_ET_QUESTIONNAIRES.md", "model_contract.md", "ETAT_LIVRAISON.md", "DISTRIBUTION.md",
    "RECETTE_VALIDATION.md", "model_guards.md", "model_wacc.md", "model_sensitivity.md",
    "MODELES_ET_VERSIONS.md", "QUALIFICATIONS.md", "PROPOSITIONS_ET_CONFLITS.md", "CATALOGUE_SEMANTIQUE.md")})
DEVELOPMENT_DOCS = frozenset({"docs/MAINTENANCE.md", "docs/RECETTE_MAINTENANCE.md"})
VENDOR_REQUIRED = frozenset({"tca_bp/vendor/PROVENANCE.md", "tca_bp/vendor/vendor/olefile/PROVENANCE.json",
                            "tca_bp/vendor/vendor/olefile/LICENSE.txt"})
VENDOR_CODE = frozenset({"tca_bp/vendor/" + name for name in ("__init__.py", "input_engine.py",
    "resolve_input_defaults.py", "vba_fingerprint.py", "vendor/olefile/__init__.py", "vendor/olefile/olefile.py")})
CORE_REQUIRED = frozenset({"tca_bp/" + name for name in (
    "__init__.py", "__main__.py", "service.py", "storage.py", "gui.py", "mcp_server.py",
    "model_engine.py", "model_runtime.py", "model_registry.py", "qualifications.py", "agents.py", "knowledge.py", "native_excel.py", "recalculate.ps1", "privacy.py",
    "wacc_solver.py", "wacc_native.py", "wacc_worker.ps1", "sensitivity_native.py", "sensitivity_worker.ps1",
    "calculation_operations.py", "calculation_proofs.py", "field_semantics.py",
    "field_semantics_data.py", "_field_semantics_basis.py", "web_lock.py", "model_components.py", "native_cleanup.py", "initial_model.py")})
CLIENT_CODE = CORE_REQUIRED | VENDOR_CODE | VENDOR_REQUIRED
FORBIDDEN = frozenset({"exemple", ".git", ".venv", "runtime", "clients", "dossiers", "data", "secrets", "__pycache__"})
MANIFEST = "PACKAGE_MANIFEST.json"
NOTICE = "LIRE_AVANT_UTILISATION.md"
PERSONAL_PATH = re.compile(rb'(?i)(?:[a-z]:[\\/]+(?:users|documents and settings)[\\/]+|d\.docs\.live\.net/[0-9a-f]+|onedrive\.live\.com)')
MARKDOWN_LINK = re.compile(r'(?<!!)\[([^]\n]+)\]\((<[^>]+>|[^)\n]+)\)')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def allowed_name(name: str) -> bool:
    path = PurePosixPath(name)
    if not name or name != path.as_posix() or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or "\\" in name or ":" in name:
        return False
    lowered = [part.casefold() for part in path.parts]
    if any(part in FORBIDDEN or part.startswith(".env") or any(word in part for word in ("secret", "credential", "password", "api_key", "apikey")) for part in lowered):
        return False
    if name in ROOT_FILES or name in {MANIFEST, NOTICE, ".vscode/mcp.json"}:
        return True
    if name.startswith(MODEL_PREFIX):
        return name[len(MODEL_PREFIX):] in MODEL_FILES
    if name.startswith("tca_bp/"):
        return name in CLIENT_CODE
    if name.startswith("docs/"):
        return name in DOC_FILES or name == "docs/feuilles/README.md" or bool(re.fullmatch(r"docs/feuilles/agent_\d{2}\.md", name))
    if re.fullmatch(r"agents/agent_\d{2}\.json", name):
        return True
    return False


def _regular_file(root: Path, path: Path) -> bytes:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        raise ValueError("Un lien de fichier ne peut être distribué : " + path.name)
    if not path.resolve().is_relative_to(root):
        raise ValueError("Une source de distribution sort du projet.")
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise ValueError("Un répertoire lié ne peut servir de source de distribution.")
    if not path.is_file():
        raise ValueError("Fichier requis absent : " + path.relative_to(root).as_posix())
    return path.read_bytes()


def _validate_model(files: dict[str, bytes]) -> dict:
    try:
        receipt = json.loads(files[MODEL_PREFIX + "build_receipt.json"])
        schema_raw = files[MODEL_PREFIX + "modele.json"]
        schema = json.loads(schema_raw)
        template_raw = files[MODEL_PREFIX + TEMPLATE]
        if digest(template_raw) != receipt["template_sha256"] or digest(schema_raw) != receipt["schema_sha256"]:
            raise ValueError("La trame ou son manifeste ne correspond plus au reçu de construction.")
        if schema["model_id"] != receipt["model_id"] or schema["model_id"] != "tca-bp-template/1":
            raise ValueError("Ce pack attend le modèle courant reconnu par l'application.")
        if schema.get("template_sha256") and schema["template_sha256"] != digest(template_raw):
            raise ValueError("Le manifeste décrit une autre trame.")
        if receipt.get("counts", {}).get("sheets") != 33:
            raise ValueError("Le modèle distribué doit décrire 33 feuilles.")
        return receipt
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Reçu ou manifeste du modèle incomplet.") from exc


def _local_target(document: str, raw_target: str) -> str | None:
    target = raw_target.strip().strip("<>")
    parsed = urlsplit(target)
    if parsed.scheme in {"http", "https", "mailto"} or target.startswith("#"):
        return None
    if parsed.scheme or target.startswith(("/", "\\")):
        return "__absolute_internal_resource__"
    path = unquote(parsed.path).replace("\\", "/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(document), path))


def _portable_document(raw: bytes, document: str, available: set[str]) -> bytes:
    text = raw.decode("utf-8")

    def substitute(match):
        target = _local_target(document, match[2])
        if target == CLIENT_README:
            return "[" + match[1] + "](" + posixpath.relpath("README.md", posixpath.dirname(document) or ".") + ")"
        if target is None or target in available or any(n.startswith(target.rstrip("/") + "/") for n in available):
            return match[0]
        if target == "PLAN_CONCEPTION_AGENTS_BP_TCA.md":
            return match[1] + " (document interne non distribué)"
        if target in DEVELOPMENT_DOCS or target.startswith(("tools/", "docs/exemples/", "tca_bp/model_build", "tca_bp/model_maintenance", "tca_bp/maintenance")):
            return match[1] + " (réservé au dépôt de développement TCA ; non inclus dans le pack client)"
        if target.startswith(("runtime/", "models/maintenance/", "models/versions/", "models/private/")):
            return match[1] + " (preuve locale conservée dans l'environnement de développement ; non incluse dans le pack)"
        if target.startswith(("exemple/", "tests/", "__absolute_internal_resource__")):
            return match[1] + " (ressource interne non distribuée)"
        raise ValueError("Lien documentaire sans cible dans le pack : " + document)

    text = MARKDOWN_LINK.sub(substitute, text)
    return text.encode("utf-8")


def _client_readme(raw: bytes, source_document=CLIENT_README) -> bytes:
    """Déplacer les liens du guide source docs/ vers le README racine du pack."""
    def relocate(match):
        target = _local_target(source_document, match[2])
        if target is None or target == "__absolute_internal_resource__":
            return match[0]
        parsed = urlsplit(match[2].strip().strip("<>"))
        suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
        return "[" + match[1] + "](<" + target + suffix + ">)"
    return MARKDOWN_LINK.sub(relocate, raw.decode("utf-8")).encode("utf-8")


def _check_content(files: dict[str, bytes]) -> None:
    """Refuse les liens cassés et chemins personnels sans en afficher la valeur."""
    available = set(files)
    for name, raw in files.items():
        if (name.endswith(('.md', '.py')) or name.startswith('agents/')
                or name == MODEL_PREFIX + 'catalogue_champs.json'):
            if private_fragment_found(raw.decode('utf-8-sig')):
                raise ValueError('Un fragment documentaire privé subsiste dans le pack : ' + name)
        if name.endswith(".md"):
            for match in MARKDOWN_LINK.finditer(raw.decode("utf-8")):
                target = _local_target(name, match[2])
                if target is not None and target not in available and not any(n.startswith(target.rstrip("/") + "/") for n in available):
                    raise ValueError("Lien documentaire sans cible dans le pack : " + name)
        if name.endswith(".md") or (name.startswith(MODEL_PREFIX) and name.endswith(".json")):
            if PERSONAL_PATH.search(raw):
                raise ValueError("Un chemin personnel subsiste dans un document distribué : " + name)
    template = files.get(MODEL_PREFIX + TEMPLATE)
    if template is not None:
        audit = audit_workbook_documentation(io.BytesIO(template))
        if audit['status'] != 'PASS':
            raise ValueError('Un fragment documentaire privé subsiste dans le modèle : ' + audit['hits'][0]['part'])
        with zipfile.ZipFile(io.BytesIO(template)) as workbook:
            for part in workbook.namelist():
                if part.endswith((".xml", ".rels", ".vml")) and PERSONAL_PATH.search(workbook.read(part)):
                    raise ValueError("Un chemin personnel subsiste dans le modèle : " + part)


def collect_files(project_root: Path) -> tuple[dict[str, bytes], dict]:
    root = Path(project_root).resolve()
    files = {}
    for name in sorted(ROOT_FILES):
        files[name] = _regular_file(root, root / (CLIENT_README if name == "README.md" else name))
        if name == "README.md":
            files[name] = _client_readme(files[name])
    for folder in ("tca_bp", "docs", "agents"):
        for path in sorted((root / folder).rglob("*")):
            if path.is_dir():
                continue
            name = path.relative_to(root).as_posix()
            if allowed_name(name):
                raw = _regular_file(root, path)
                files[name] = raw
    for name in (".vscode/mcp.json",):
        files[name] = _regular_file(root, root / name)
    for name in MODEL_FILES:
        files[MODEL_PREFIX + name] = _regular_file(root, root / MODEL_PREFIX / name)
    missing = CLIENT_CODE - files.keys()
    if missing:
        raise ValueError("Un composant ou sa provenance manque : " + ", ".join(sorted(missing)))
    expected_agents = {f"agents/agent_{i:02d}.json" for i in range(1, 34)}
    actual_agents = {name for name in files if name.startswith("agents/")}
    if actual_agents != expected_agents:
        raise ValueError("Le pack doit inclure exactement les 33 contrats d'agents.")
    receipt = _validate_model(files)
    # Les chemins de construction du poste ne sont pas des données portables.
    portable_receipt = dict(receipt)
    portable_receipt["template_path"] = MODEL_PREFIX + TEMPLATE
    portable_receipt["schema_path"] = MODEL_PREFIX + "modele.json"
    for key in list(portable_receipt):
        if key.endswith("_path") and key not in {"template_path", "schema_path"}:
            del portable_receipt[key]
    files[MODEL_PREFIX + "build_receipt.json"] = json_bytes(portable_receipt)
    files[NOTICE] = ("# Démarrer le pack TCA BP\n\n"
        "Ce pack contient déjà le modèle générique et ses manifestes. Aucun document du dossier de référence n'est nécessaire à son utilisation.\n\n"
        "1. Extraire tout le ZIP dans un répertoire local.\n"
        "2. Installer Python 3.14 avec Tcl/Tk, puis exécuter Installer_TCA_BP.ps1. Cette étape installe les dépendances Python du projet et peut nécessiter Internet.\n"
        "3. Lancer Lancer_TCA_BP.cmd et créer un dossier. Les données du dossier sont conservées dans le stockage local de l'utilisateur.\n"
        "4. Utiliser Microsoft Excel pour le recalcul natif. Les macros restent désactivées ; la résolution WACC n'est pas lancée par ce bouton.\n\n"
        "Ce pack client exclut le générateur, la maintenance de formules, les scripts de conditionnement et les tests. Les commandes de développement sont refusées explicitement. Restaurer un pack complet si la trame ou ses manifestes manquent ; les documents du dossier de référence ne sont jamais requis à l'utilisation.\n\n"
        "Consulter docs/DISTRIBUTION.md, docs/INTERFACE.md et docs/ETAT_LIVRAISON.md. Le manifeste SHA256 vérifie l'intégrité du pack ; il ne certifie pas les hypothèses financières ni son auteur.\n").encode("utf-8")
    for name, raw in list(files.items()):
        if name.endswith(".md"):
            files[name] = _portable_document(raw, name, set(files))
    _check_content(files)
    return files, portable_receipt


def _output_path(root: Path, output: Path) -> Path:
    output = Path(output).absolute()
    resolved = output.resolve()
    if resolved.suffix.lower() != ".zip":
        raise ValueError("La destination doit être un fichier ZIP.")
    if output.exists() or output.is_symlink():
        raise ValueError("La destination existe déjà ; aucun pack n'est écrasé.")
    forbidden_roots = [root / name for name in ("exemple", ".git", ".venv", "runtime", "clients", "dossiers", "data", "tca_bp", "docs", "agents", "models", "tools", "tests")]
    if any(resolved.is_relative_to(path.resolve()) for path in forbidden_roots):
        raise ValueError("La destination doit être séparée des sources, modèles et dossiers clients ; utiliser dist/.")
    if any(part.casefold() in FORBIDDEN for part in resolved.parts):
        raise ValueError("La destination appartient à un espace exclu de la distribution.")
    return resolved


def verify_package(path: Path) -> dict:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or len(names) != len({name.casefold() for name in names}):
                raise ValueError("Entrées ZIP dupliquées ou ambiguës sous Windows.")
            if any(not allowed_name(name) for name in names):
                raise ValueError("Le ZIP contient un chemin exclu de la distribution.")
            if archive.testzip():
                raise ValueError("Archive ZIP endommagée.")
            manifest = json.loads(archive.read(MANIFEST))
            if manifest.get("schema") != "tca-bp-package/1":
                raise ValueError("Format du manifeste de distribution invalide.")
            if manifest.get("distribution") != "CLIENT":
                raise ValueError("Ce vérificateur attend un pack client séparé du développement.")
            entries = manifest.get("files", [])
            listed = [entry["path"] for entry in entries]
            if len(listed) != len(set(listed)) or set(listed) != set(names) - {MANIFEST}:
                raise ValueError("Le manifeste ne couvre pas exactement le contenu du ZIP.")
            model_files = {}
            content_view = {}
            for entry in entries:
                raw = archive.read(entry["path"])
                if len(raw) != entry["size"] or digest(raw) != entry["sha256"]:
                    raise ValueError("Empreinte invalide : " + entry["path"])
                if entry["path"].startswith(MODEL_PREFIX):
                    model_files[entry["path"]] = raw
                content_view[entry["path"]] = raw
            if not (ROOT_FILES | CLIENT_CODE | {NOTICE, ".vscode/mcp.json"} | {MODEL_PREFIX + n for n in MODEL_FILES}).issubset(names):
                raise ValueError("Composant, licence ou provenance manquant dans le pack.")
            if {n for n in names if n.startswith("agents/")} != {f"agents/agent_{i:02d}.json" for i in range(1,34)}:
                raise ValueError("Les 33 contrats d'agents sont requis.")
            receipt = _validate_model(model_files)
            if manifest["model_id"] != receipt["model_id"] or manifest["template_sha256"] != receipt["template_sha256"]:
                raise ValueError("Le manifeste de distribution décrit un autre modèle.")
            content_view[MANIFEST] = archive.read(MANIFEST)
            _check_content(content_view)
            return {"status": "VERIFIE", "files": len(entries), "model_id": receipt["model_id"],
                    "template_sha256": receipt["template_sha256"], "package_sha256": digest(Path(path).read_bytes()),
                    "distribution": "CLIENT", "development_components_included": False,
                    "reference_files_required": False, "native_calculation_certified": False}
    except (KeyError, TypeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        raise ValueError("Pack incomplet ou manifeste illisible.") from exc


def create_package(project_root: Path, output: Path) -> dict:
    root = Path(project_root).resolve()
    destination = _output_path(root, output)
    files, receipt = collect_files(root)
    manifest = {"schema": "tca-bp-package/1", "distribution": "CLIENT", "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "model_id": receipt["model_id"], "template_sha256": receipt["template_sha256"],
                "reference_source_sha256": receipt.get("source_sha256"), "python_required": ">=3.14",
                "macros_automatically_enabled": False, "native_calculation_certified": False,
                "files": [{"path": name, "size": len(raw), "sha256": digest(raw)} for name, raw in sorted(files.items())]}
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".tca-package-", suffix=".zip", dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, raw in sorted(files.items()):
                archive.writestr(name, raw)
            archive.writestr(MANIFEST, json_bytes(manifest))
        result = verify_package(temporary)
        # Publication entière et exclusive, sans fenêtre d'écrasement concurrent.
        os.link(temporary, destination)
        return {**result, "status": "CREE_ET_VERIFIE", "path": str(destination)}
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Créer ou vérifier un pack local TCA BP, sans documents de référence")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path, help="Nouveau fichier ZIP à créer, par exemple dist/TCA_BP.zip")
    action.add_argument("--verify", type=Path, help="Vérifier un ZIP existant sans l'extraire")
    args = parser.parse_args(argv)
    try:
        result = verify_package(args.verify) if args.verify else create_package(args.project_root, args.output)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "REFUSE", "reason": str(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
