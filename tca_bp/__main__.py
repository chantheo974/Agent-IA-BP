"""Point d'entrée de TCA BP : interface, commandes et serveur d'outils local."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


def _timeout_seconds(maximum):
    def parse(raw):
        try:
            value = int(raw)
        except ValueError as error:
            raise argparse.ArgumentTypeError("Le délai doit être un entier en secondes.") from error
        if not 1 <= value <= maximum:
            raise argparse.ArgumentTypeError(f"Le délai doit être compris entre 1 et {maximum} secondes.")
        return value
    return parse


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tca-bp", description="TCA BP — dossiers, agents de feuille et saisies Excel contrôlées")
    p.add_argument("--project-root", type=Path)
    p.add_argument("--data-dir", type=Path, help="Espace de dossiers indépendant (par défaut stockage local Windows)")
    subs = p.add_subparsers(dest="command", required=True)
    subs.add_parser("gui", help="Ouvrir l'application Windows")
    subs.add_parser("doctor", help="Vérifier Python, Excel et la disponibilité du modèle")
    subs.add_parser("build", help="Développement TCA : construire la trame depuis la référence locale")
    subs.add_parser("list", help="Lister les dossiers")
    a = subs.add_parser("create", help="Créer un dossier client isolé")
    a.add_argument("--client", required=True); a.add_argument("--name", required=True); a.add_argument("--id")
    for name in ("show", "report", "recover", "open"):
        a = subs.add_parser(name); a.add_argument("case")
    a = subs.add_parser("source", help="Ajouter une pièce ou une réponse au dossier")
    a.add_argument("case"); a.add_argument("--file", type=Path); a.add_argument("--text"); a.add_argument("--title", default="Réponse utilisateur")
    a = subs.add_parser("source-text"); a.add_argument("case"); a.add_argument("source_id")
    a = subs.add_parser("agents", help="Lister les 33 responsabilités de feuille")
    a.add_argument("--case", help="Version exacte du dossier, sinon modèle courant")
    a = subs.add_parser("explain"); a.add_argument("sheet")
    a.add_argument("--case", help="Version exacte du dossier, sinon modèle courant")
    a = subs.add_parser("bind-model", help="Rattacher un ancien dossier à sa version d'origine prouvée par v0000 ; aucune migration")
    a.add_argument("case"); a.add_argument("--model-dir", type=Path, required=True, help="Répertoire de l'ancienne version complète")
    a = subs.add_parser("qualifications", help="Évaluer les prérequis documentaires et la disponibilité des résultats")
    a.add_argument("case")
    a = subs.add_parser("declare-qualification", help="Enregistrer une déclaration de module avec source et justification")
    a.add_argument("case"); a.add_argument("file", type=Path, help="Déclaration JSON sourcée ; aucun changement de cellule")
    a = subs.add_parser("ask", help="Router une demande et enregistrer les questions ouvertes")
    a.add_argument("case"); a.add_argument("text")
    a = subs.add_parser("fields"); a.add_argument("case"); a.add_argument("sheet")
    a = subs.add_parser("inspect"); a.add_argument("case"); a.add_argument("sheet"); a.add_argument("--cells", help="A1,B2")
    a = subs.add_parser("prepare", help="Préparer un lot JSON sur la version courante")
    a.add_argument("case"); a.add_argument("file", type=Path); a.add_argument("--request-id")
    a = subs.add_parser("prepare-agent-proposals", help="Réconcilier des propositions d'agents ; suspendre le lot en cas de conflit")
    a.add_argument("case"); a.add_argument("file", type=Path); a.add_argument("--request-id", required=True)
    a = subs.add_parser("record", help="Préparer une ligne de registre depuis les champs métier")
    a.add_argument("case"); a.add_argument("sheet"); a.add_argument("file", type=Path); a.add_argument("--source", required=True); a.add_argument("--request-id")
    a = subs.add_parser("apply", help="Appliquer un plan validé dans une nouvelle version")
    a.add_argument("case"); a.add_argument("plan_id")
    a = subs.add_parser("recalculate", help="Recalculer une nouvelle copie dans Excel, macros désactivées")
    a.add_argument("case"); a.add_argument("--tables", action="store_true")
    for command, maximum, help_text in (("solve-wacc", 600, "Résoudre explicitement le WACC et enregistrer une nouvelle version vérifiée"), ("verify-sensitivity", 3600, "Comparer explicitement les tables natives à des scénarios scalaires isolés")):
        a = subs.add_parser(command, help=help_text)
        a.add_argument("case"); a.add_argument("--timeout", type=_timeout_seconds(maximum), default=maximum, help=f"Délai maximal en secondes, de 1 à {maximum}")
    a = subs.add_parser("answer"); a.add_argument("case"); a.add_argument("question_id"); a.add_argument("answer")
    subs.add_parser("mcp", help="Serveur d'outils local stdio pour un assistant compatible MCP")
    subs.add_parser("smoke-gui", help="Contrôle automatique de l'interface")
    a = subs.add_parser("maintenance-propose", help="Décrire une évolution de formules sans modifier le modèle")
    a.add_argument("file", type=Path, help="Liste JSON des formules à modifier")
    a.add_argument("--version", required=True); a.add_argument("--reason", required=True)
    a.add_argument("--out", type=Path, help="Nouveau fichier JSON de proposition, sans écrasement")
    a.add_argument("--model-dir", type=Path, help="Version de départ explicite, sinon trame générique")
    a = subs.add_parser("maintenance-build", help="Construire une version expérimentale depuis une proposition")
    a.add_argument("file", type=Path); a.add_argument("--model-dir", type=Path)
    a = subs.add_parser("maintenance-validate", help="Tester une version expérimentale dans Excel sur des scénarios fictifs")
    a.add_argument("model_dir", type=Path); a.add_argument("file", type=Path, help="Liste JSON des scénarios et attentes indépendantes")
    a = subs.add_parser("maintenance-approve", help="Tracer la décision explicite du responsable après une preuve native PASS")
    a.add_argument("model_dir", type=Path); a.add_argument("validation", type=Path)
    a.add_argument("--approved-by", required=True, help="Nom du responsable ayant validé cette version")
    return p


def _require_development(module: str) -> None:
    if importlib.util.find_spec(__package__ + "." + module) is None:
        raise ValueError("Cette commande est réservée au dépôt de développement TCA ; elle n’est pas incluse dans le pack client.")


def _maintenance_command(args):
    """Aucun stockage client ni activation automatique dans ce parcours."""
    _require_development("maintenance")
    from .maintenance import Maintenance
    from .model_engine import ModelEngine
    root = (args.project_root or Path(__file__).resolve().parent.parent).resolve()
    base = args.model_dir if args.command in ("maintenance-propose", "maintenance-build") else None
    maintenance = Maintenance(ModelEngine(root, model_dir=base))
    if args.command == "maintenance-propose":
        changes = json.loads(args.file.read_text(encoding="utf-8-sig"))
        if isinstance(changes, dict):
            changes = changes.get("changes")
        result = maintenance.propose(changes, args.version, args.reason)
        if args.out:
            # Créer exclusivement ; une ancienne proposition reste vérifiable.
            with args.out.open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
                handle.write("\n")
        return result
    if args.command == "maintenance-build":
        return maintenance.build(json.loads(args.file.read_text(encoding="utf-8-sig")))
    if args.command == "maintenance-validate":
        scenarios = json.loads(args.file.read_text(encoding="utf-8-sig"))
        if isinstance(scenarios, dict):
            scenarios = scenarios.get("scenarios")
        return maintenance.validate(args.model_dir, scenarios)
    return maintenance.approve(args.model_dir, args.validation, args.approved_by)


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    if args.command == "doctor":
        from .native_excel import available
        root = (args.project_root or Path(__file__).resolve().parent.parent).resolve()
        try:
            import tkinter
            tkinter_version = tkinter.TkVersion
        except ImportError:
            tkinter_version = None
        development = importlib.util.find_spec(__package__ + ".model_build") is not None
        result = {"python": sys.version.split()[0], "python_compatible": sys.version_info >= (3, 14),
                  "tkinter": tkinter_version, "excel_available": available(), "project_root": str(root),
                  "distribution": "DEVELOPPEMENT" if development else "CLIENT",
                  "generic_template_present": (root / "models/generic-v1/TCA_BP_Trame_generique.xlsm").is_file(),
                  "generic_manifest_present": (root / "models/generic-v1/modele.json").is_file(),
                  "reference_files_required_for_use": False,
                  "notice": "Le diagnostic n'ouvre pas Excel et ne traite aucun dossier."}
        if development:
            archives = [p for p in (root / "exemple/03_Agent_de_saisie").glob("*.zip") if p.is_file()]
            workbooks = [p for p in (root / "exemple/01_Previsionnels").glob("*Pilotage_protege.xlsm") if p.is_file()]
            result.update(reference_archive_present=len(archives) == 1,
                          reference_workbook_present=len(workbooks) == 1,
                          reference_presence_only=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["python_compatible"] and tkinter_version is not None else 2
    try:
        if args.command.startswith("maintenance-"):
            result = _maintenance_command(args)
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str, allow_nan=False))
            return 1 if result.get("status") == "FAIL" else 0
        if args.command == "build":
            _require_development("model_build")
        from .service import Application
        app = Application(args.project_root, args.data_dir)
        command = args.command
        if command == "gui":
            from .gui import main as gui_main
            gui_main(app); return 0
        if command == "smoke-gui":
            from .gui import smoke_test
            result = smoke_test()
        elif command == "mcp":
            from .mcp_server import serve
            serve(app); return 0
        elif command == "build": result = app.initialize()
        elif command == "list": result = app.list_cases()
        elif command == "create": result = app.create_case(args.client, args.name, case_id=args.id)
        elif command == "show": result = app.get_case(args.case)
        elif command == "source": result = app.add_source(args.case, args.file, args.text, args.title)
        elif command == "source-text": result = app.source_text(args.case, args.source_id)
        elif command == "agents": result = app.agents(case_id=args.case)
        elif command == "explain": result = app.sheet_info(args.sheet, case_id=args.case)
        elif command == "bind-model": result = app.bind_legacy_case(args.case, args.model_dir)
        elif command == "qualifications": result = app.qualifications(args.case)
        elif command == "declare-qualification": result = app.declare_qualification(args.case, json.loads(args.file.read_text(encoding="utf-8-sig")))
        elif command == "ask": result = app.route(args.case, args.text)
        elif command == "fields": result = app.fields(args.case, args.sheet)
        elif command == "inspect": result = app.inspect(args.case, args.sheet, args.cells.split(",") if args.cells else None)
        elif command == "prepare":
            updates = json.loads(args.file.read_text(encoding="utf-8-sig"))
            if isinstance(updates, dict):
                updates = updates.get("updates", updates.get("changes"))
            result = app.prepare_changes(args.case, updates, args.request_id)
        elif command == "prepare-agent-proposals":
            proposals = json.loads(args.file.read_text(encoding="utf-8-sig"))
            result = app.prepare_agent_proposals(args.case, proposals, args.request_id)
        elif command == "record":
            values = json.loads(args.file.read_text(encoding="utf-8-sig"))
            result = app.prepare_record(args.case, args.sheet, values, args.source, args.request_id)
        elif command == "apply": result = app.apply_plan(args.case, args.plan_id)
        elif command == "recalculate": result = app.recalculate(args.case, args.tables)
        elif command == "solve-wacc": result = app.solve_wacc(args.case, timeout=args.timeout)
        elif command == "verify-sensitivity": result = app.verify_sensitivity(args.case, timeout=args.timeout)
        elif command == "report": result = {"path": app.export_report(args.case)}
        elif command == "open": result = {"path": app.open_workbook(args.case)}
        elif command == "recover": result = app.recovery_status(args.case)
        elif command == "answer": result = app.answer_question(args.case, args.question_id, args.answer)
        else: raise ValueError("Commande inconnue.")
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"status": "REFUSE", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
