"""Interface Windows locale de l'atelier BP, sans dépendance supplémentaire.

Le service demeure propriétaire des règles métier et des écritures. Les fonctions
de ce module ne modifient jamais un classeur. Tkinter reste sur le fil principal.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import queue
import re
import tempfile
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable


NAVY = "#183449"
TEAL = "#087F8C"
INK = "#263B4B"
MUTED = "#617587"
PAPER = "#F3F6F9"
WHITE = "#FFFFFF"
STATUS_LABELS = {
    "HYPOTHESE": "Hypothèse",
    "CONFIRME": "Confirmé",
    "INACTIF": "Inactif",
    "NON_RENSEIGNE": "Non renseigné",
    "A_RECALCULER": "Recalcul requis",
    "VERIFIE_SUR_PERIMETRE": "Vérifié sur le périmètre indiqué",
    "NOT_CALCULATED": "Recalcul requis",
    "RECALC_REQUIRED": "Recalcul requis",
    "RECALCUL_REQUIRED": "Recalcul requis",
    "PENDING": "En attente",
    "READY": "Prêt à appliquer",
    "PRET_A_APPLIQUER": "Prêt à appliquer",
    "A_COMPLETER": "Informations à compléter",
    "RECALCULE": "Recalcul Excel terminé",
    "APPLIQUE": "Proposition appliquée",
    "DEJA_APPLIQUE": "Proposition déjà appliquée",
    "NEEDS_INPUT": "Informations à compléter",
    "REFUSED": "Proposition refusée",
}


def display_value(value: Any) -> str:
    if value is None or value == "":
        return "Non renseigné"
    if isinstance(value, (dt.date, dt.datetime)):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, bool):
        return "Oui" if value else "Non"
    if isinstance(value, float):
        return f"{value:,.4f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",")
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def display_cell(value: Any, kind: str, date1904: bool | None) -> str:
    if kind == "date" and date1904 is not None and isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            base = dt.date(1904, 1, 1) if date1904 else dt.date(1899, 12, 30)
            # Excel 1900 contient un jour fictif : les premières dates restent explicites.
            if not date1904 and value < 61:
                return f"Numéro de date Excel : {value}"
            return display_value(base + dt.timedelta(days=int(value)))
        except (OverflowError, ValueError):
            pass
    return display_value(value)


def describe_native_receipt(receipt: dict) -> str:
    """Présenter uniquement les faits fournis, sans certifier le modèle entier."""
    statuses = {"CONVERGENCE_LOCALE": "Convergence locale du WACC vérifiée", "TABLES_VERIFIEES": "Tables de sensibilité vérifiées", "NON_ADOPTE": "Copie non adoptée", "ECHEC_COMPARAISON_OU_DEGENERESCENCE": "Tables non qualifiées"}
    lines = ["Résultat : " + statuses.get(receipt.get("status"), str(receipt.get("status", "Statut non fourni")))]
    for key, label in (("revision", "Révision du dossier"), ("workbook_path", "Classeur"), ("report_path", "Reçu enregistré"), ("receipt_path", "Reçu enregistré")):
        if receipt.get(key) is not None:
            lines.append(label + " : " + str(receipt[key]))
    candidate = receipt.get("candidate")
    if isinstance(candidate, (float, int)) and not isinstance(candidate, bool) and math.isfinite(candidate):
        lines.append("WACC retenu : " + f"{candidate * 100:.6f}".rstrip("0").rstrip(".").replace(".", ",") + " %")
    residual = receipt.get("residual")
    if isinstance(residual, (float, int)) and not isinstance(residual, bool) and math.isfinite(residual):
        lines.append("Écart de convergence : " + f"{residual:.3e}")
    if receipt.get("evaluations") is not None:
        lines.append("Évaluations du taux : " + str(receipt["evaluations"]))
    comparisons = receipt.get("comparisons")
    if isinstance(comparisons, list) and comparisons:
        passed = sum(isinstance(item, dict) and item.get("passed") is True for item in comparisons)
        lines.append(f"Comparaisons concordantes : {passed} sur {len(comparisons)}")
    for key, label in (("source_preserved", "Source conservée"), ("inputs_unchanged", "Entrées métier conservées"), ("save_reopen_verified", "Sauvegarde et réouverture vérifiées"), ("macros_enabled", "Macros activées")):
        if isinstance(receipt.get(key), bool):
            lines.append(label + " : " + display_value(receipt[key]))
    if receipt.get("restoration") == "ISOLATION_PAR_COPIES_BASE_JAMAIS_CHOQUEE":
        lines.append("Scénarios exécutés sur des copies isolées ; les chocs ne sont pas appliqués à la base.")
    if receipt.get("global_uniqueness_proven") is False:
        lines.append("La convergence est locale ; l'unicité globale du taux n'est pas démontrée.")
    if receipt.get("financial_model_globally_validated") is False:
        lines.append("Ce contrôle des tables ne valide pas globalement les hypothèses financières.")
    if receipt.get("notice"):
        lines.append(str(receipt["notice"]))
    return "\n\n".join(lines)


def field_type(field: dict) -> str:
    constraints = field.get("constraints") or {}
    if not isinstance(constraints, dict):
        constraints = {}
    return str(field.get("value_type") or field.get("type") or constraints.get("type") or field.get("kind") or "text").lower()


def parse_value(raw: str, field: dict) -> Any:
    """Conversion de présentation ; la validation finale appartient au moteur."""
    raw = raw.strip()
    if not raw:
        raise ValueError("Renseignez une valeur, ou cochez « Effacer l'entrée ».")
    choices = field.get("choices") or []
    if choices:
        for choice in choices:
            if isinstance(choice, dict):
                if raw in {str(choice.get("label", "")), str(choice.get("value", ""))}:
                    return choice.get("value", choice.get("label"))
            elif raw == str(choice):
                return choice
        raise ValueError("Choisissez une valeur dans la liste proposée pour ce champ.")
    kind = field_type(field)
    if kind in {"date", "datetime", "excel_date"}:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(raw, fmt).date().isoformat()
            except ValueError:
                pass
        raise ValueError("La date doit être au format JJ/MM/AAAA, par exemple 01/07/2027.")
    if kind in {"number", "numeric", "float", "decimal", "currency", "money", "integer", "int", "percentage", "percent", "rate"}:
        percent = raw.endswith("%")
        number = raw.replace("\u00a0", "").replace("\u202f", "").replace(" ", "").replace("€", "").replace("%", "").replace(",", ".")
        try:
            value = float(number)
        except ValueError as exc:
            raise ValueError("Renseignez un nombre, par exemple 125 000 ou 4 %.") from exc
        if value != value or value in {float("inf"), float("-inf")}:
            raise ValueError("Le nombre doit être fini.")
        if percent:
            value /= 100
        if kind in {"integer", "int"}:
            if not value.is_integer():
                raise ValueError("Ce champ attend un nombre entier.")
            return int(value)
        return value
    if kind in {"bool", "boolean"}:
        if raw.lower() in {"oui", "true", "1"}:
            return True
        if raw.lower() in {"non", "false", "0"}:
            return False
        raise ValueError("Ce champ attend Oui ou Non.")
    return raw


def expand_cells(cells: list[str] | str | None) -> list[str]:
    """Accepte cellules explicites et petits rectangles du catalogue."""
    if isinstance(cells, str):
        cells = [cells]
    result: list[str] = []

    def column_number(name: str) -> int:
        number = 0
        for char in name:
            number = number * 26 + ord(char) - 64
        return number

    def column_name(number: int) -> str:
        name = ""
        while number:
            number, remainder = divmod(number - 1, 26)
            name = chr(65 + remainder) + name
        return name

    for item in cells or []:
        item = str(item).replace("$", "")
        if "!" in item:
            item = item.rsplit("!", 1)[1]
        match = re.fullmatch(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?", item.upper())
        if not match:
            continue
        c1, r1, c2, r2 = match.groups()
        ca, cb = column_number(c1), column_number(c2 or c1)
        ra, rb = int(r1), int(r2 or r1)
        if cb < ca or rb < ra or (cb - ca + 1) * (rb - ra + 1) > 10000:
            continue
        result.extend(f"{column_name(c)}{r}" for r in range(ra, rb + 1) for c in range(ca, cb + 1))
    return list(dict.fromkeys(result))


def snapshot_cells(snapshot: Any) -> dict[str, dict]:
    """Normalise les formes usuelles d'une inspection sans inférer des valeurs."""
    if isinstance(snapshot, list):
        return {str(row.get("cell") or row.get("address")): row for row in snapshot if isinstance(row, dict) and (row.get("cell") or row.get("address"))}
    if not isinstance(snapshot, dict):
        return {}
    def unpack(rows: dict) -> dict:
        return {str(k): {**v, **(v.get("current") or {})} if isinstance(v, dict) else {"value": v} for k, v in rows.items()}

    for key in ("cells", "values", "entries"):
        if key in snapshot:
            rows = snapshot[key]
            if isinstance(rows, list):
                return snapshot_cells(rows)
            if isinstance(rows, dict):
                return unpack(rows)
    if isinstance(snapshot.get("inputs"), dict):
        result = {}
        for rows in snapshot["inputs"].values():
            if isinstance(rows, dict):
                result.update(unpack(rows))
        return result
    return {str(k): v if isinstance(v, dict) else {"value": v} for k, v in snapshot.items() if re.fullmatch(r"[A-Z]+\d+", str(k))}


def question_text(question: Any) -> str:
    if isinstance(question, dict):
        return str(question.get("question") or question.get("message") or question.get("label") or question.get("text") or question)
    return str(question)


def plan_is_ready(plan: dict) -> bool:
    status = str(plan.get("status", "")).upper()
    if status in {"REFUSED", "INVALID", "NEEDS_INPUT", "BLOCKED", "FAILED", "ERROR"} or plan.get("questions"):
        return False
    return bool(plan.get("id") and plan.get("changes")) and status in {
        "READY", "PREPARED", "VALIDATED", "OK", "PRÊT", "PRET", "PROPOSITION_VALIDEE", "PRET_A_APPLIQUER"
    }


def preview_changes(plan: dict, date1904: bool | None = None) -> list[dict]:
    """L'avant provient de l'instantané contrôlé par le moteur, jamais d'une supposition."""
    expected = {(c.get("sheet"), c.get("cell")): c.get("expected")
                for c in (plan.get("engine_plan") or {}).get("changes", [])}
    kinds = {(c.get("sheet"), c.get("cell")): c.get("kind")
             for c in (plan.get("engine_plan") or {}).get("changes", [])}
    rows = []
    for change in plan.get("changes") or plan.get("updates") or []:
        row = dict(change)
        before = expected.get((change.get("sheet"), change.get("cell")), change.get("expected"))
        if isinstance(before, dict):
            row["before_display"] = ("Défaut calculé : " + str(before["formula"])) if before.get("formula") else display_cell(before.get("value"), kinds.get((change.get("sheet"), change.get("cell")), ""), date1904)
        elif any(key in change for key in ("old_value", "before", "expected_value")):
            row["before_display"] = display_value(change.get("old_value", change.get("before", change.get("expected_value"))))
        else:
            row["before_display"] = "Non fourni par le moteur"
        rows.append(row)
    return rows


def describe_sheet(info: dict) -> str:
    parts = []
    for key, title in (("role", "Rôle de la feuille"), ("dependencies", "Feuilles utilisées"),
                       ("questions", "Informations à réunir"), ("checks", "Points de contrôle"), ("controls", "Contrôles complémentaires"),
                       ("input_policy", "Règles de saisie"), ("notice", "À connaître"),
                       ("limitations", "Périmètre de l'explication")):
        value = info.get(key)
        if value:
            if key == "input_policy":
                value = {"CATALOGUE_UNIQUEMENT": "Seuls les champs autorisés du catalogue peuvent être renseignés.",
                         "LECTURE": "Cette feuille s'explique à partir des données de ses feuilles sources."}.get(str(value), value)
            if isinstance(value, list):
                body = "\n".join("• " + question_text(item) for item in value)
            else:
                body = display_value(value)
            parts.append(title + "\n" + body)
    return "\n\n".join(parts) or "La fiche de cette feuille ne fournit pas encore de description."


class BPWindow:
    """Fenêtre de l'atelier. Toutes les fonctions du service passent par _run."""

    def __init__(self, root: tk.Tk, app: Any, *, start: bool = True) -> None:
        self.root, self.app = root, app
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tca-service")
        self.events: queue.Queue = queue.Queue()
        self.busy = False
        self.closed = False
        self.close_when_idle = False
        self.case_id: str | None = None
        self.case: dict = {}
        self.case_rows: dict[str, dict] = {}
        self.agent_rows: list[dict] = []
        self.field_rows: dict[str, dict] = {}
        self.snapshot: dict[str, dict] = {}
        self.date1904: bool | None = None
        self.source_rows: dict[str, dict] = {}
        self.question_rows: dict[str, dict] = {}
        self.target_rows: dict[str, str] = {}
        self.pending: list[dict] = []
        self.plan: dict | None = None
        self.loaded_sheet = ""
        self._buttons: list[tuple[ttk.Button, bool]] = []
        self._poll_id: str | None = None
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._poll_id = root.after(50, self._poll)
        if start:
            self.root.after(10, self.initialize)

    def _build(self) -> None:
        self.root.title("TCA Conseil — Atelier business plan")
        self.root.geometry("1440x920")
        self.root.minsize(1120, 760)
        self.root.configure(background=PAPER)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), foreground=INK)
        style.configure("TFrame", background=PAPER)
        style.configure("Card.TFrame", background=WHITE)
        style.configure("TLabel", background=PAPER)
        style.configure("Card.TLabel", background=WHITE)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 19), foreground=NAVY)
        style.configure("Section.TLabel", font=("Segoe UI Semibold", 11), foreground=NAVY)
        style.configure("TButton", padding=(12, 7), borderwidth=0)
        style.configure("Primary.TButton", background=TEAL, foreground=WHITE, font=("Segoe UI Semibold", 10))
        style.map("Primary.TButton", background=[("active", "#066975"), ("disabled", "#B9CDCF")])
        style.configure("TNotebook", background=PAPER, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(15, 10))
        style.map("TNotebook.Tab", background=[("selected", WHITE)], foreground=[("selected", TEAL)])
        style.configure("Treeview", background=WHITE, fieldbackground=WHITE, rowheight=29, borderwidth=0)
        style.configure("Treeview.Heading", background="#E6EDF3", font=("Segoe UI Semibold", 9), padding=7)
        style.map("Treeview", background=[("selected", "#D8EDEE")], foreground=[("selected", NAVY)])
        style.configure("TLabelframe", background=PAPER, borderwidth=1)
        style.configure("TLabelframe.Label", background=PAPER, font=("Segoe UI Semibold", 10))

        header = tk.Frame(self.root, background=NAVY, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="TCA CONSEIL", background=NAVY, foreground=WHITE, font=("Segoe UI Semibold", 14)).pack(side="left", padx=(24, 18))
        tk.Label(header, text="Atelier business plan", background=NAVY, foreground="#B9CFD9", font=("Segoe UI", 13)).pack(side="left")
        tk.Label(header, text="Vos dossiers restent sur cet ordinateur", background=NAVY, foreground="#B9CFD9", font=("Segoe UI", 9)).pack(side="right", padx=24)
        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=18, pady=(18, 8))
        sidebar = ttk.Frame(body, padding=(0, 0, 14, 0), width=242)
        body.add(sidebar, weight=0)
        ttk.Label(sidebar, text="Dossiers", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self.case_tree = ttk.Treeview(sidebar, show="tree", selectmode="browse", height=16)
        self.case_tree.column("#0", width=230, stretch=True)
        self.case_tree.pack(fill="both", expand=True)
        self.case_tree.bind("<<TreeviewSelect>>", self._case_selected)
        self._button(sidebar, "Nouveau dossier", self.new_case_dialog, primary=True).pack(fill="x", pady=(12, 4))
        self._button(sidebar, "Actualiser la liste", self.refresh_cases).pack(fill="x")
        ttk.Label(sidebar, text="Un dossier, ses sources et ses versions.\nChaque proposition produit une copie.", style="Muted.TLabel", wraplength=225).pack(anchor="w", pady=14)
        main = ttk.Frame(body, padding=(12, 0, 0, 0))
        body.add(main, weight=1)
        self.case_title = tk.StringVar(value="Bienvenue dans votre atelier")
        self.case_subtitle = tk.StringVar(value="Créez un dossier pour commencer, ou choisissez un dossier existant.")
        ttk.Label(main, textvariable=self.case_title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(main, textvariable=self.case_subtitle, style="Muted.TLabel").pack(anchor="w", pady=(5, 13))
        toolbar = ttk.Frame(main)
        toolbar.pack(fill="x", pady=(0, 12))
        self._button(toolbar, "Ouvrir le classeur", self.open_workbook, case=True).pack(side="left", padx=(0, 6))
        self._button(toolbar, "Rapport du dossier", self.export_report, case=True).pack(side="left", padx=(0, 6))
        self._button(toolbar, "Afficher les fichiers", self.open_folder, case=True).pack(side="left")
        self._button(toolbar, "Actualiser", self.refresh_case, case=True).pack(side="right")
        self.tabs = ttk.Notebook(main)
        self.tabs.pack(fill="both", expand=True)
        self.overview = ttk.Frame(self.tabs, padding=18)
        self.entry_tab = ttk.Frame(self.tabs, padding=14)
        self.chat_tab = ttk.Frame(self.tabs, padding=18)
        self.sources_tab = ttk.Frame(self.tabs, padding=18)
        self.qualifications_tab = ttk.Frame(self.tabs, padding=18)
        self.history_tab = ttk.Frame(self.tabs, padding=18)
        for frame, title in ((self.overview, "Vue d'ensemble"), (self.entry_tab, "Saisie guidée"), (self.chat_tab, "Conversation"), (self.sources_tab, "Documents et preuves"), (self.qualifications_tab, "Qualifications"), (self.history_tab, "Historique")):
            self.tabs.add(frame, text=title)
        self._build_overview()
        self._build_entry()
        self._build_chat()
        self._build_sources()
        self._build_qualifications()
        self._build_history()
        self.tabs.bind("<<NotebookTabChanged>>", self._tab_changed)
        footer = ttk.Frame(self.root, padding=(20, 2, 20, 12))
        footer.pack(fill="x")
        self.status = tk.StringVar(value="Ouverture de l'atelier…")
        ttk.Label(footer, textvariable=self.status, style="Muted.TLabel").pack(side="left", fill="x", expand=True)
        self.progress = ttk.Progressbar(footer, mode="indeterminate", length=180)
        self.progress.pack(side="right")
        self._set_busy(False)

    def _button(self, parent: Any, text: str, command: Callable, *, primary: bool = False, case: bool = False) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command, style="Primary.TButton" if primary else "TButton")
        self._buttons.append((button, case))
        return button

    def _text(self, parent: Any, *, height: int = 6, editable: bool = False) -> tk.Text:
        holder = ttk.Frame(parent)
        holder.pack(fill="both", expand=True)
        text = tk.Text(holder, height=height, wrap="word", font=("Segoe UI", 10), background=WHITE, foreground=INK, relief="flat", padx=12, pady=10, insertbackground=TEAL)
        scroll = ttk.Scrollbar(holder, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        if not editable:
            text.configure(state="disabled")
        return text

    @staticmethod
    def _set_text(widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.configure(state="disabled")

    def _tree(self, parent: Any, columns: tuple[tuple[str, str, int], ...], *, height: int = 8) -> ttk.Treeview:
        holder = ttk.Frame(parent)
        holder.pack(fill="both", expand=True)
        tree = ttk.Treeview(holder, columns=[c[0] for c in columns], show="headings", selectmode="browse", height=height)
        for key, label, width in columns:
            tree.heading(key, text=label)
            tree.column(key, width=width, minwidth=60, anchor="w")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree

    def _build_overview(self) -> None:
        cards = ttk.Frame(self.overview)
        cards.pack(fill="x", pady=(0, 18))
        self.card_vars = {}
        for index, (key, label) in enumerate((("revision", "VERSION COURANTE"), ("calculation", "ÉTAT DES CALCULS"), ("sources", "SOURCES DU DOSSIER"))):
            card = ttk.Frame(cards, style="Card.TFrame", padding=18)
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10 if index < 2 else 0))
            cards.columnconfigure(index, weight=1)
            ttk.Label(card, text=label, style="Card.TLabel", foreground=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
            value = tk.StringVar(value="—")
            self.card_vars[key] = value
            ttk.Label(card, textvariable=value, style="Card.TLabel", font=("Segoe UI Semibold", 13), wraplength=290).pack(anchor="w", pady=(8, 0))
        self.overview_text = self._text(self.overview, height=5)
        model = ttk.Frame(self.overview)
        model.pack(fill="x", pady=(10, 0))
        self.model_status = tk.StringVar(value="Modèle du dossier : aucun dossier sélectionné")
        ttk.Label(model, textvariable=self.model_status, style="Muted.TLabel").pack(side="left")
        self.bind_model_button = self._button(model, "Rattacher l'ancien modèle", self.bind_legacy_model, case=True)
        self.bind_model_button.pack(side="right")
        self.model_reference = tk.StringVar(value="")
        ttk.Entry(self.overview, textvariable=self.model_reference, state="readonly").pack(fill="x", pady=(5, 0))
        compute = ttk.Frame(self.overview)
        compute.pack(fill="x", pady=14)
        self._button(compute, "Recalculer dans Excel", self.recalculate, primary=True, case=True).pack(side="left")
        self.include_tables = tk.BooleanVar(value=False)
        ttk.Checkbutton(compute, text="Inclure les tables de sensibilité", variable=self.include_tables).pack(side="left", padx=14)
        advanced = ttk.Frame(self.overview)
        advanced.pack(fill="x", pady=(0, 10))
        self.wacc_button = self._button(advanced, "Résoudre le WACC", self.solve_wacc, case=True)
        self.wacc_button.pack(side="left", padx=(0, 8))
        self.sensitivity_button = self._button(advanced, "Vérifier les sensibilités", self.verify_sensitivity, case=True)
        self.sensitivity_button.pack(side="left")
        ttk.Label(advanced, text="Calculs sur la version enregistrée, avec un reçu distinct.", style="Muted.TLabel").pack(side="left", padx=12)
        ttk.Label(self.overview, text="Questions ouvertes", style="Section.TLabel").pack(anchor="w", pady=(6, 8))
        self.question_tree = self._tree(self.overview, (("sheet", "Sujet", 170), ("question", "Information attendue", 610)), height=6)
        answer = ttk.Frame(self.overview)
        answer.pack(fill="x", pady=(10, 0))
        self.answer_var = tk.StringVar()
        ttk.Entry(answer, textvariable=self.answer_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._button(answer, "Répondre à la question", self.answer_question, case=True).pack(side="right")

    def _build_entry(self) -> None:
        select = ttk.Frame(self.entry_tab)
        select.pack(fill="x")
        ttk.Label(select, text="Agent de feuille", style="Section.TLabel").pack(side="left", padx=(0, 12))
        self.agent_var = tk.StringVar()
        self.agent_combo = ttk.Combobox(select, textvariable=self.agent_var, state="readonly", width=44)
        self.agent_combo.pack(side="left", fill="x", expand=True)
        self.agent_combo.bind("<<ComboboxSelected>>", self.load_sheet)
        self._button(select, "Lire la fiche", self.show_sheet_info).pack(side="left", padx=(8, 0))
        self.sheet_summary = tk.StringVar(value="Choisissez l'une des feuilles pour comprendre son rôle et ses entrées.")
        ttk.Label(self.entry_tab, textvariable=self.sheet_summary, style="Muted.TLabel", wraplength=1050).pack(anchor="w", pady=(8, 10))
        mode = ttk.Frame(self.entry_tab)
        mode.pack(fill="x", pady=(0, 8))
        self.mode_var = tk.StringVar(value="update")
        ttk.Radiobutton(mode, text="Modifier des champs existants", value="update", variable=self.mode_var, command=self._mode_changed).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(mode, text="Ajouter une ligne au registre", value="record", variable=self.mode_var, command=self._mode_changed).pack(side="left")
        ttk.Label(mode, text="Filtrer", style="Muted.TLabel").pack(side="left", padx=(25, 6))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._render_fields())
        ttk.Entry(mode, textvariable=self.filter_var, width=22).pack(side="left", fill="x", expand=True)
        split = ttk.Panedwindow(self.entry_tab, orient="horizontal")
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split)
        right = ttk.Frame(split, padding=(16, 0, 0, 0))
        split.add(left, weight=1)
        split.add(right, weight=1)
        self.fields_tree = self._tree(left, (("label", "Champ", 255), ("kind", "Type", 100), ("scope", "Emplacement", 130)), height=8)
        self.fields_tree.bind("<<TreeviewSelect>>", self._field_selected)
        self.field_name = tk.StringVar(value="Sélectionnez un champ")
        ttk.Label(right, textvariable=self.field_name, style="Section.TLabel", wraplength=470).pack(anchor="w")
        self.field_help = tk.StringVar(value="Les valeurs et contraintes proviennent du catalogue du modèle.")
        ttk.Label(right, textvariable=self.field_help, style="Muted.TLabel", wraplength=470).pack(anchor="w", pady=(5, 8))
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(right, textvariable=self.target_var, state="readonly")
        self.target_combo.pack(fill="x", pady=(0, 5))
        self.target_combo.bind("<<ComboboxSelected>>", self._target_selected)
        self.current_var = tk.StringVar(value="Valeur actuelle : —")
        ttk.Label(right, textvariable=self.current_var, style="Muted.TLabel", wraplength=470).pack(anchor="w", pady=(0, 6))
        self.value_var = tk.StringVar()
        self.value_combo = ttk.Combobox(right, textvariable=self.value_var)
        self.value_combo.pack(fill="x")
        flags = ttk.Frame(right)
        flags.pack(fill="x", pady=(5, 2))
        self.clear_var = tk.BooleanVar(value=False)
        self.replace_var = tk.BooleanVar(value=False)
        self.override_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(flags, text="Effacer l'entrée", variable=self.clear_var).pack(anchor="w")
        ttk.Checkbutton(flags, text="Confirmer le remplacement de la valeur existante", variable=self.replace_var).pack(anchor="w")
        ttk.Checkbutton(flags, text="Remplacer le défaut calculé de ce champ", variable=self.override_var).pack(anchor="w")
        provenance = ttk.Frame(self.entry_tab)
        provenance.pack(fill="x", pady=(10, 4))
        ttk.Label(provenance, text="Preuve / source").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.evidence_var = tk.StringVar()
        self.evidence_combo = ttk.Combobox(provenance, textvariable=self.evidence_var, state="readonly", width=40)
        self.evidence_combo.grid(row=0, column=1, sticky="ew")
        ttk.Label(provenance, text="État").grid(row=0, column=2, padx=(12, 8))
        self.input_status = tk.StringVar(value="Hypothèse")
        self.status_combo = ttk.Combobox(provenance, textvariable=self.input_status, values=("Hypothèse", "Confirmé", "Non renseigné"), state="readonly", width=16)
        self.status_combo.grid(row=0, column=3, sticky="ew")
        self._button(provenance, "Ajouter une preuve", lambda: self.tabs.select(self.sources_tab), case=True).grid(row=0, column=4, padx=(8, 0))
        provenance.columnconfigure(1, weight=1)
        reason = ttk.Frame(self.entry_tab)
        reason.pack(fill="x", pady=(4, 8))
        ttk.Label(reason, text="Justification", width=14).pack(side="left")
        self.reason_var = tk.StringVar()
        ttk.Entry(reason, textvariable=self.reason_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._button(reason, "Ajouter à la proposition", self.add_pending, case=True).pack(side="right")
        self.pending_title = tk.StringVar(value="Proposition en cours · aucun champ")
        ttk.Label(self.entry_tab, textvariable=self.pending_title, style="Section.TLabel").pack(anchor="w", pady=(2, 7))
        self.pending_tree = self._tree(self.entry_tab, (("field", "Champ", 280), ("value", "Valeur proposée", 200), ("status", "État", 130), ("source", "Source", 260)), height=4)
        actions = ttk.Frame(self.entry_tab)
        actions.pack(fill="x", pady=(8, 0))
        self._button(actions, "Retirer le champ sélectionné", self.remove_pending).pack(side="left")
        self._button(actions, "Vider la proposition", self.clear_pending).pack(side="left", padx=8)
        self._button(actions, "Vérifier et prévisualiser", self.prepare, primary=True, case=True).pack(side="right")

    def _build_chat(self) -> None:
        ttk.Label(self.chat_tab, text="Décrivez votre besoin", style="Section.TLabel").pack(anchor="w")
        ttk.Label(self.chat_tab, text="Le coordinateur identifie les feuilles concernées et les informations utiles. Une demande ne modifie pas le classeur.", style="Muted.TLabel", wraplength=1050).pack(anchor="w", pady=(5, 12))
        self.transcript = self._text(self.chat_tab, height=20)
        self._set_text(self.transcript, "Coordinateur\nPar exemple : « Ajouter un recrutement en juillet », « Expliquer le besoin de trésorerie » ou « Préparer un investissement en crédit-bail ».\n")
        bar = ttk.Frame(self.chat_tab)
        bar.pack(fill="x", pady=(12, 0))
        self.message_var = tk.StringVar()
        chat_entry = ttk.Entry(bar, textvariable=self.message_var)
        chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        chat_entry.bind("<Return>", lambda _: self.send_message())
        self._button(bar, "Examiner la demande", self.send_message, primary=True, case=True).pack(side="right")

    def _build_sources(self) -> None:
        top = ttk.Frame(self.sources_tab)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Documents et réponses du dossier", style="Section.TLabel").pack(side="left")
        self._button(top, "Importer des documents", self.import_sources, primary=True, case=True).pack(side="right")
        self.sources_tree = self._tree(self.sources_tab, (("title", "Source", 380), ("kind", "Nature", 180), ("date", "Ajoutée le", 170)), height=7)
        ttk.Label(self.sources_tab, text="Ajouter une réponse ou une hypothèse documentée", style="Section.TLabel").pack(anchor="w", pady=(18, 7))
        self.source_title = tk.StringVar(value="Réponse utilisateur")
        ttk.Entry(self.sources_tab, textvariable=self.source_title).pack(fill="x", pady=(0, 8))
        self.source_text = self._text(self.sources_tab, height=7, editable=True)
        bottom = ttk.Frame(self.sources_tab)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Label(bottom, text="L'ajout d'une source ne confirme pas automatiquement ses hypothèses.", style="Muted.TLabel").pack(side="left")
        self._button(bottom, "Enregistrer cette source", self.add_text_source, case=True).pack(side="right")

    def _build_history(self) -> None:
        ttk.Label(self.history_tab, text="Versions et opérations du dossier", style="Section.TLabel").pack(anchor="w", pady=(0, 12))
        self.history_tree = self._tree(self.history_tab, (("date", "Date", 175), ("action", "Opération", 210), ("version", "Version", 90), ("detail", "Détail", 470)), height=15)
        self.history_tree.bind("<Double-1>", self.show_history_detail)
        ttk.Label(self.history_tab, text="Double-cliquez sur une opération pour consulter son détail.", style="Muted.TLabel").pack(anchor="w", pady=(12, 0))

    def _build_qualifications(self) -> None:
        ttk.Label(self.qualifications_tab, text="Modules et prérequis documentaires", style="Section.TLabel").pack(anchor="w")
        ttk.Label(self.qualifications_tab, text="Déclarez la situation du dossier à partir d'une source. Une déclaration inactive ne neutralise pas des valeurs présentes dans Excel.", style="Muted.TLabel", wraplength=1000).pack(anchor="w", pady=(6, 12))
        self.qualification_modules = {"Chiffre d'affaires": "CA", "Coûts directs": "COGS", "Stocks": "STOCK", "Crédit d'impôt recherche": "CIR", "Règles fiscales": "REGLES_FISCALES", "BFR en valeur terminale": "BFR_TERMINAL", "Contrats": "DATA Contrats", "Effectifs": "Effectifs", "Investissements": "DATA CAPEX", "Levées de fonds": "DATA Financement", "Dette": "Financement Dette", "Subventions d'investissement": "SUBVENTION_INVEST"}
        form = ttk.Frame(self.qualifications_tab)
        form.pack(fill="x")
        self.qual_module, self.qual_state, self.qual_status = tk.StringVar(), tk.StringVar(value="Actif"), tk.StringVar(value="Hypothèse")
        for index, (label, variable, choices, width) in enumerate((("Module", self.qual_module, tuple(self.qualification_modules), 31), ("Situation", self.qual_state, ("Actif", "Inactif"), 15), ("Qualification", self.qual_status, ("Hypothèse", "Confirmé"), 15))):
            ttk.Label(form, text=label).grid(row=0, column=index, sticky="w", padx=(0, 12))
            combo = ttk.Combobox(form, textvariable=variable, values=choices, state="readonly", width=width)
            combo.grid(row=1, column=index, sticky="ew", padx=(0, 12), pady=5)
            if index == 0:
                combo.bind("<<ComboboxSelected>>", self._qualification_module_changed)
        ttk.Label(form, text="Source du dossier").grid(row=0, column=3, sticky="w")
        self.qual_source_combo = ttk.Combobox(form, textvariable=self.evidence_var, state="readonly", width=31)
        self.qual_source_combo.grid(row=1, column=3, sticky="ew", pady=5)
        form.columnconfigure(3, weight=1)
        self.qual_fiscal = ttk.Frame(self.qualifications_tab)
        self.qual_jurisdiction, self.qual_valid_from, self.qual_valid_to = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for index, (label, variable) in enumerate((("Juridiction", self.qual_jurisdiction), ("Applicable à partir du", self.qual_valid_from), ("Applicable jusqu'au", self.qual_valid_to))):
            ttk.Label(self.qual_fiscal, text=label).grid(row=0, column=index, sticky="w", padx=(0, 12))
            ttk.Entry(self.qual_fiscal, textvariable=variable, width=27).grid(row=1, column=index, sticky="ew", padx=(0, 12), pady=5)
        ttk.Label(self.qual_fiscal, text="Dates : JJ/MM/AAAA ou AAAA-MM-JJ", style="Muted.TLabel").grid(row=2, column=0, columnspan=3, sticky="w")
        reason = ttk.Frame(self.qualifications_tab)
        reason.pack(fill="x", pady=(10, 8))
        self.qual_reason = tk.StringVar()
        ttk.Label(reason, text="Justification").pack(side="left", padx=(0, 8))
        ttk.Entry(reason, textvariable=self.qual_reason).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._button(reason, "Enregistrer la déclaration", self.declare_qualification, case=True).pack(side="right")
        actions = ttk.Frame(self.qualifications_tab)
        actions.pack(fill="x", pady=(6, 12))
        self._button(actions, "Évaluer la disponibilité", self.refresh_qualifications, primary=True, case=True).pack(side="left")
        ttk.Label(actions, text="Aucun recalcul Excel n'est lancé par cette évaluation.", style="Muted.TLabel").pack(side="left", padx=12)
        self.qualification_tree = self._tree(self.qualifications_tab, (("scope", "Résultats", 190), ("state", "État", 260), ("scenario", "Scénario de travail", 155), ("available", "Résultats qualifiés", 155)), height=5)
        self.qualification_text = self._text(self.qualifications_tab, height=8)
        self._set_text(self.qualification_text, "Choisissez un dossier puis évaluez ses prérequis. Un calcul récent ne confirme pas ses hypothèses.")

    def _qualification_module_changed(self, _event=None) -> None:
        if self.qualification_modules.get(self.qual_module.get()) == "REGLES_FISCALES":
            self.qual_fiscal.pack(fill="x", pady=5, after=self.qual_source_combo.master)
        else:
            self.qual_fiscal.pack_forget()

    def declare_qualification(self) -> None:
        if not self.case_id or self.busy:
            return
        try:
            module = self.qualification_modules.get(self.qual_module.get())
            if not module:
                raise ValueError("Choisissez le module à documenter.")
            declaration = {"module": module, "state": {"Actif": "ACTIF", "Inactif": "INACTIF"}[self.qual_state.get()], "status": {"Confirmé": "CONFIRME", "Hypothèse": "HYPOTHESE"}[self.qual_status.get()], "evidence": self._selected_evidence(), "reason": self.qual_reason.get().strip()}
            if len(declaration["reason"]) < 8:
                raise ValueError("Expliquez cette déclaration en huit caractères minimum.")
            if module == "REGLES_FISCALES":
                if not self.qual_jurisdiction.get().strip():
                    raise ValueError("Renseignez la juridiction des règles fiscales.")
                declaration.update(jurisdiction=self.qual_jurisdiction.get().strip(), valid_from=parse_value(self.qual_valid_from.get(), {"kind": "date"}), valid_to=parse_value(self.qual_valid_to.get(), {"kind": "date"}))
        except (ValueError, KeyError) as error:
            self._error("Déclarer le module", error)
            return
        case_id = self.case_id
        def task():
            self.app.declare_qualification(case_id, declaration)
            return self._case_data(case_id)
        def done(case):
            self._render_case(case)
            self.refresh_qualifications()
        self._run("Enregistrement de la déclaration sourcée", task, done)

    def refresh_qualifications(self) -> None:
        if self.case_id:
            case_id = self.case_id
            self._run("Évaluation des prérequis du dossier", lambda: self.app.qualifications(case_id), self._render_qualifications)

    def _render_qualifications(self, result: dict) -> None:
        self.qualification_tree.delete(*self.qualification_tree.get_children())
        labels = {"CA": "Chiffre d'affaires", "COGS": "Coûts directs", "CASH": "Trésorerie", "FISCALITE": "Fiscalité", "DCF": "Valorisation DCF"}
        statuses = {"DISPONIBLE_SUR_PREREQUIS_QUALIFIES": "Prérequis qualifiés", "A_RECALCULER": "À recalculer", "HYPOTHESES_A_CONFIRMER": "Hypothèses à confirmer", "INDISPONIBLE": "Informations manquantes"}
        details = []
        scopes = result.get("scopes", {})
        for scope, item in scopes.items():
            self.qualification_tree.insert("", "end", values=(labels.get(scope, scope), statuses.get(item.get("status"), item.get("status", "À vérifier")), "Prêt" if item.get("scenario_ready") else "À compléter", "Disponibles" if item.get("available") else "Non disponibles"))
            points = item.get("blockers", []) + item.get("hypotheses", [])
            if points:
                details.append(labels.get(scope, scope) + "\n" + "\n".join("• " + str(point.get("message", point.get("code", "À compléter"))) + (" · " + str(point["field"]) if point.get("field") else "") for point in points))
        if result.get("notice"):
            details.insert(0, str(result["notice"]))
        if result.get("declarations"):
            details.append("Déclarations conservées\n" + "\n".join("• " + module + " : " + str(item.get("state", "")) + ", " + str(item.get("status", "")) + " — " + str(item.get("reason", "")) for module, item in result["declarations"].items()))
        if not scopes:
            details.append("Aucune évaluation de disponibilité n'a été fournie. Les résultats restent à vérifier.")
        elif not details:
            details.append("Aucun blocage documentaire signalé sur ce périmètre. Les preuves propres au WACC et aux tables de sensibilité restent distinctes.")
        self._set_text(self.qualification_text, "\n\n".join(details))

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        for button, needs_case in self._buttons:
            button.configure(state="disabled" if busy or (needs_case and not self.case_id) else "normal")
        self.case_tree.state(["disabled"] if busy else ["!disabled"])
        self.agent_combo.configure(state="disabled" if busy else "readonly")
        if hasattr(self, "bind_model_button"):
            self.bind_model_button.configure(state="disabled" if busy or not self.case_id or self.case.get("model_ref") else "normal")
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _run(self, action: str, task: Callable, success: Callable | None = None) -> None:
        if self.busy or self.closed:
            return
        self.status.set(action + "…")
        self._set_busy(True)

        def work() -> None:
            try:
                result = task()
                self.events.put((True, action, result, success))
            except Exception as exc:
                self.events.put((False, action, exc, None))

        self.executor.submit(work)

    def _poll(self) -> None:
        if self.closed:
            return
        try:
            while True:
                ok, action, payload, callback = self.events.get_nowait()
                self._set_busy(False)
                if ok:
                    self.status.set(action + " : terminé.")
                    if callback:
                        try:
                            callback(payload)
                        except Exception as exc:
                            self._error("Afficher le résultat", exc)
                else:
                    self._error(action, payload)
        except queue.Empty:
            pass
        if self.close_when_idle and not self.busy:
            self.close()
            return
        self._poll_id = self.root.after(60, self._poll)

    def _error(self, action: str, error: Exception | str) -> None:
        self.status.set(action + " : à vérifier.")
        messagebox.showerror("TCA Conseil", f"{action}\n\n{str(error)[:1800]}", parent=self.root)

    def initialize(self) -> None:
        def task() -> tuple:
            cases = self.app.list_cases()
            try:
                state = self.app.initialize()
                agents = self.app.agents()
            except (ValueError, OSError) as error:
                state, agents = {"notice": str(error)}, []
            return state, agents, cases

        def done(result: tuple) -> None:
            state, agents, cases = result
            self.agent_rows = agents
            self.agent_combo["values"] = [self._agent_display(a, i) for i, a in enumerate(agents)]
            if agents:
                self.agent_combo.current(0)
            self._render_cases(cases)
            self.status.set("Modèle courant indisponible. Les dossiers archivés restent accessibles. " + state["notice"] if state.get("notice") else "Atelier prêt. Choisissez un dossier ou créez le premier.")

        self._run("Préparation de l'atelier", task, done)

    @staticmethod
    def _agent_display(agent: dict, index: int) -> str:
        return f"{index + 1:02d} · {agent.get('sheet') or agent.get('name') or agent.get('label') or agent.get('id')}"

    def _selected_sheet(self) -> str:
        index = self.agent_combo.current()
        if 0 <= index < len(self.agent_rows):
            row = self.agent_rows[index]
            return str(row.get("sheet") or row.get("name") or row.get("label") or "")
        return ""

    def refresh_cases(self) -> None:
        self._run("Lecture des dossiers", self.app.list_cases, self._render_cases)

    def _render_cases(self, cases: list[dict]) -> None:
        self.case_rows = {str(c["id"]): c for c in cases}
        self.case_tree.delete(*self.case_tree.get_children())
        for case in cases:
            self.case_tree.insert("", "end", iid=str(case["id"]), text=f"{case.get('name', 'Dossier')} · {case.get('client_name', '')}")
        if self.case_id in self.case_rows:
            self.case_tree.selection_set(self.case_id)
        self._set_busy(self.busy)

    def _case_selected(self, _event: Any = None) -> None:
        selected = self.case_tree.selection()
        if self.busy or not selected or selected[0] == self.case_id:
            return
        if self.pending:
            if not messagebox.askyesno("Proposition en cours", "La proposition n'a pas été appliquée. L'abandonner et ouvrir l'autre dossier ?", parent=self.root):
                if self.case_id:
                    self.case_tree.selection_set(self.case_id)
                return
        self.clear_pending()
        self.case_id = selected[0]
        self.loaded_sheet = ""
        self.field_rows = {}
        self.snapshot = {}
        self._render_fields()
        self.refresh_case()

    def refresh_case(self) -> None:
        if self.case_id:
            case_id = self.case_id
            self._run("Lecture du dossier", lambda: self._case_data(case_id), self._render_case)

    def _case_data(self, case_id: str) -> dict:
        """À appeler depuis le travail de fond, y compris après une mutation."""
        case = self.app.get_case(case_id)
        if case.get("model_status") in {"VERSION_NON_EPINGLEE", "VERSION_INDISPONIBLE_OU_MODIFIEE"}:
            case["_ui_agents"] = []
        else:
            try:
                case["_ui_agents"] = self.app.agents(case_id=case_id)
            except (ValueError, OSError) as error:
                case["_ui_agents"] = []
                case["_ui_agents_notice"] = str(error)
        return case

    def _render_case(self, case: dict) -> None:
        if self.case.get("id") != case.get("id"):
            for variable in (self.qual_module, self.qual_reason, self.qual_jurisdiction, self.qual_valid_from, self.qual_valid_to):
                variable.set("")
            self.qual_state.set("Actif")
            self.qual_status.set("Hypothèse")
            self._qualification_module_changed()
        if "_ui_agents" in case:
            sheet = self._selected_sheet()
            self.agent_rows = case["_ui_agents"]
            self.agent_combo["values"] = [self._agent_display(agent, i) for i, agent in enumerate(self.agent_rows)]
            if self.agent_rows:
                selected = next((i for i, a in enumerate(self.agent_rows) if a.get("sheet") == sheet), 0)
                self.agent_combo.current(selected)
            else:
                self.agent_combo.set("")
        self.case = case
        self.case_id = str(case.get("id", self.case_id))
        revision = case.get("revision", "—")
        calc = case.get("calculation_status", "A_RECALCULER")
        calc_label = STATUS_LABELS.get(str(calc), display_value(calc))
        self.case_title.set(str(case.get("name", "Dossier")))
        self.case_subtitle.set(f"{case.get('client_name', '')}  ·  Version {revision}  ·  {calc_label}")
        model_labels = {"VERSION_EXACTE_DISPONIBLE": "Archive exacte disponible", "VERSION_NON_EPINGLEE": "Ancien dossier à rattacher", "VERSION_INDISPONIBLE_OU_MODIFIEE": "Archive absente ou modifiée"}
        self.model_status.set("Modèle du dossier : " + model_labels.get(case.get("model_status"), "Version non renseignée"))
        self.model_reference.set(case.get("model_ref") or "Référence exacte non enregistrée")
        self.card_vars["revision"].set(str(revision))
        self.card_vars["calculation"].set(calc_label)
        sources = case.get("sources") or []
        self.card_vars["sources"].set(str(len(sources)))
        self.sources_tree.delete(*self.sources_tree.get_children())
        self.source_rows = {}
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
            label = f"{index + 1:02d} · {source.get('title') or source.get('name') or 'Source'}"
            self.source_rows[label] = source
            self.sources_tree.insert("", "end", values=(source.get("title") or source.get("name") or "Source", source.get("kind") or source.get("type") or ("Document" if source.get("path") else "Réponse"), source.get("created_at") or source.get("added_at") or ""))
        self.evidence_combo["values"] = list(self.source_rows)
        self.qual_source_combo["values"] = list(self.source_rows)
        if self.evidence_var.get() not in self.source_rows:
            self.evidence_var.set(next(reversed(self.source_rows), ""))
        self.question_tree.delete(*self.question_tree.get_children())
        self.question_rows = {}
        for index, q in enumerate(case.get("questions") or []):
            q = q if isinstance(q, dict) else {"question": str(q)}
            if q.get("status") in {"ANSWERED", "RESOLVED", "CLOSED", "REPONDUE", "FERMEE"}:
                continue
            key = str(q.get("id") or index)
            self.question_rows[key] = q
            self.question_tree.insert("", "end", iid=key, values=(q.get("sheet") or q.get("module") or q.get("topic") or "Dossier", question_text(q)))
        self.history_tree.delete(*self.history_tree.get_children())
        self.history_rows = {}
        for index, entry in enumerate(case.get("history") or []):
            if not isinstance(entry, dict):
                entry = {"detail": str(entry)}
            self.history_rows[str(index)] = entry
            details = entry.get("details") if isinstance(entry.get("details"), dict) else {}
            self.history_tree.insert("", "end", iid=str(index), values=(entry.get("created_at") or entry.get("timestamp") or entry.get("date") or "", entry.get("action") or entry.get("type") or entry.get("event") or entry.get("kind") or "Opération", entry.get("revision") or entry.get("version") or details.get("revision") or "", entry.get("summary") or entry.get("message") or entry.get("detail") or details.get("message") or "Double-cliquez pour le détail"))
        summary = [f"État du dossier : {calc_label}.", "Les résultats financiers ne doivent être interprétés qu'après le recalcul requis et la lecture des contrôles.", f"{len(self.question_rows)} question(s) ouverte(s). {len(sources)} source(s) conservée(s) avec ce dossier."]
        if case.get("integrity") == "MODIFIE_OU_ABSENT":
            summary.insert(0, "La version courante a été modifiée hors de l'atelier ou n'est plus disponible. Les nouvelles saisies nécessitent sa vérification.")
        for key in ("model_notice", "_ui_agents_notice", "notice", "summary", "dashboard", "warnings", "checks", "calculation_details", "qualification_status"):
            if case.get(key):
                summary.append(self._describe(case[key]))
        self._set_text(self.overview_text, "\n\n".join(summary))
        self.qualification_tree.delete(*self.qualification_tree.get_children())
        self._set_text(self.qualification_text, "La disponibilité doit être évaluée sur cette version du dossier. Les déclarations restent liées à leurs sources.")
        self._set_busy(False)

    def bind_legacy_model(self) -> None:
        if not self.case_id or self.busy:
            return
        if self.case.get("model_ref"):
            self._error("Rattacher l'ancien modèle", "Ce dossier possède déjà une version exacte. Le rattachement ne permet aucune migration.")
            return
        case_id = self.case_id
        dialog = tk.Toplevel(self.root)
        if self.root.state() == "withdrawn":
            dialog.withdraw()
        dialog.title("Rattacher la version d'origine")
        dialog.geometry("690x295")
        dialog.transient(self.root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=self.case.get("name", "Ancien dossier"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Choisissez le répertoire qui contient la trame et les manifestes de l'ancienne version. Le rattachement exige une copie initiale v0000 identique et un journal cohérent. Il conserve le classeur et sa révision.", wraplength=635).pack(anchor="w", pady=12)
        selected = tk.StringVar()
        ttk.Entry(frame, textvariable=selected, state="readonly").pack(fill="x", pady=6)
        def choose():
            path = filedialog.askdirectory(parent=dialog, title="Répertoire de la version d'origine", mustexist=True)
            if path:
                selected.set(path)
        ttk.Button(frame, text="Choisir l'ancienne version…", command=choose).pack(anchor="w")
        def submit():
            if not selected.get():
                self._error("Rattacher l'ancien modèle", "Choisissez le répertoire de la version d'origine.")
                return
            path = Path(selected.get())
            dialog.destroy()
            def task():
                self.app.bind_legacy_case(case_id, path)
                return self._case_data(case_id)
            def done(case):
                self.clear_pending()
                self.loaded_sheet = ""
                self.field_rows, self.snapshot = {}, {}
                self._render_fields()
                self._render_case(case)
                self.status.set("Version d'origine rattachée sur preuve. Les anciennes propositions doivent être préparées à nouveau.")
            self._run("Vérification et rattachement de la version d'origine", task, done)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=16)
        ttk.Button(buttons, text="Annuler", command=dialog.destroy).pack(side="left")
        self.model_bind_button = ttk.Button(buttons, text="Vérifier et rattacher cette version", command=submit, style="Primary.TButton")
        self.model_bind_button.pack(side="right")
        self.model_bind_dialog, self.model_dir_var = dialog, selected

    def _tab_changed(self, _event: Any = None) -> None:
        if not self.busy and self.case_id and self.tabs.select() == str(self.entry_tab) and self.loaded_sheet != self._selected_sheet():
            self.load_sheet()

    def new_case_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        if self.root.state() == "withdrawn":
            dialog.withdraw()
        dialog.title("Nouveau dossier")
        dialog.geometry("500x285")
        dialog.transient(self.root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Créer un dossier", style="Title.TLabel").pack(anchor="w", pady=(0, 14))
        client_var, name_var = tk.StringVar(), tk.StringVar()
        ttk.Label(frame, text="Nom du client").pack(anchor="w")
        client_entry = ttk.Entry(frame, textvariable=client_var)
        client_entry.pack(fill="x", pady=(4, 10))
        ttk.Label(frame, text="Nom du dossier").pack(anchor="w")
        ttk.Entry(frame, textvariable=name_var).pack(fill="x", pady=(4, 12))

        def submit() -> None:
            client, name = client_var.get().strip(), name_var.get().strip()
            if not client or not name:
                messagebox.showinfo("Nouveau dossier", "Renseignez le client et le nom du dossier.", parent=dialog)
                return
            dialog.destroy()
            self.create_case(client, name)

        ttk.Button(frame, text="Créer le dossier", command=submit, style="Primary.TButton").pack(anchor="e")
        client_entry.focus_set()

    def create_case(self, client: str, name: str) -> None:
        def task() -> tuple:
            case = self.app.create_case(client, name)
            return self._case_data(case["id"]), self.app.list_cases()

        def done(result: tuple) -> None:
            case, cases = result
            self.clear_pending()
            self.case_id = str(case["id"])
            self.loaded_sheet = ""
            self.field_rows = {}
            self._render_fields()
            self._render_cases(cases)
            self._render_case(case)
            self.tabs.select(self.sources_tab)

        self._run("Création du dossier", task, done)

    def load_sheet(self, _event: Any = None) -> None:
        sheet = self._selected_sheet()
        if not sheet:
            return
        if self.pending and sheet != self.loaded_sheet:
            self.status.set("La proposition conserve ses champs ; les ajouts de registre doivent porter sur une seule feuille.")
        if not self.case_id:
            self.show_sheet_info()
            return
        case_id = self.case_id

        def task() -> tuple:
            fields = self.app.fields(case_id, sheet)
            # Le service choisit le périmètre d'inspection autorisé.
            return fields, self.app.inspect(case_id, sheet), self.app.sheet_info(sheet, case_id=case_id)

        def done(result: tuple) -> None:
            fields, snap, info = result
            self.loaded_sheet = sheet
            self.field_rows = {str(f.get("id") or f.get("field_id")): f for f in fields}
            self.snapshot = snapshot_cells(snap)
            self.date1904 = snap.get("date1904") if isinstance(snap, dict) else None
            self.sheet_summary.set(str(info.get("role") or info.get("summary") or info.get("description") or f"{sheet} · {len(fields)} champs décrits dans le catalogue."))
            self._render_fields()

        self._run(f"Lecture de {sheet}", task, done)

    def _render_fields(self) -> None:
        self.fields_tree.delete(*self.fields_tree.get_children())
        search = self.filter_var.get().strip().casefold()
        for field_id, field in self.field_rows.items():
            label = str(field.get("label") or field_id)
            if search and search not in (label + " " + field_id).casefold():
                continue
            cells = expand_cells(field.get("cells") or field.get("cell"))
            scope = "Champ unique" if len(cells) == 1 else f"{len(cells)} emplacements"
            self.fields_tree.insert("", "end", iid=field_id, values=(label, field.get("unit") or field_type(field), scope))
        self.field_name.set("Sélectionnez un champ")
        self.value_var.set("")
        self.target_var.set("")
        self.target_rows = {}
        self.target_combo["values"] = []
        self.current_var.set("")

    def _field_selected(self, _event: Any = None) -> None:
        selected = self.fields_tree.selection()
        if not selected or selected[0] not in self.field_rows:
            return
        field = self.field_rows[selected[0]]
        self.field_name.set(str(field.get("label") or selected[0]))
        constraints = field.get("constraints") or {key: field[key] for key in ("min", "max", "min_exclusive", "max_exclusive", "allow_blank", "integer") if key in field}
        help_parts = [str(field.get("description") or ""), f"Type : {field_type(field)}"]
        if field.get("unit"):
            help_parts.append("Unité : " + str(field["unit"]))
        if constraints:
            help_parts.append("Règles : " + self._describe(constraints))
        self.field_help.set("\n".join(p for p in help_parts if p))
        self.target_rows = {}
        for index, cell in enumerate(expand_cells(field.get("cells") or field.get("cell"))):
            snap = self.snapshot.get(cell, {})
            context = snap.get("label") or snap.get("row_label") or snap.get("period") or f"Emplacement {index + 1}"
            value = snap.get("value")
            label = f"{context} · {display_cell(value, field_type(field), self.date1904)[:75]}  ({cell})"
            self.target_rows[label] = cell
        self.target_combo["values"] = list(self.target_rows)
        self.target_var.set(next(iter(self.target_rows), ""))
        choices = field.get("choices") or []
        self.value_combo["values"] = [str(c.get("label", c.get("value", ""))) if isinstance(c, dict) else str(c) for c in choices]
        self.value_combo.configure(state="readonly" if choices else "normal")
        self.clear_var.set(False)
        self.replace_var.set(False)
        self.override_var.set(False)
        self.value_var.set("")
        self._target_selected()

    def _target_selected(self, _event: Any = None) -> None:
        cell = self.target_rows.get(self.target_var.get())
        current = self.snapshot.get(cell or "", {})
        value = current.get("value")
        formula = current.get("formula")
        if self.mode_var.get() == "record":
            self.current_var.set("Nouvelle ligne : le moteur choisira un emplacement disponible.")
            self.target_combo.configure(state="disabled")
        else:
            self.target_combo.configure(state="readonly")
            state = (self.case.get("field_states") or {}).get(f"{self.loaded_sheet}!{cell}", {})
            status = STATUS_LABELS.get(state.get("status"), "À qualifier")
            source_id = state.get("evidence")
            source_title = next((s.get("title", "Source conservée") for s in self.source_rows.values() if s.get("id") == source_id), "")
            self.current_var.set("Valeur actuelle : " + display_cell(value, str(current.get("kind", "")), self.date1904) + (" · défaut calculé" if formula else "") + "\n" + status + (" · " + source_title if source_title else ""))

    def _mode_changed(self) -> None:
        if self.pending:
            # Une proposition ne mélange jamais ajout de ligne et modification.
            self.mode_var.set(self.pending[0]["_mode"])
            self.status.set("Videz ou appliquez la proposition avant de changer de mode de saisie.")
            return
        self._target_selected()
        self.status_combo.configure(state="readonly")
        if self.mode_var.get() == "record":
            self.status.set("Nouvelle ligne : renseignez ses champs avec une même source, puis vérifiez la proposition.")

    def _selected_evidence(self) -> str:
        source = self.source_rows.get(self.evidence_var.get())
        if not source or not source.get("id"):
            raise ValueError("Ajoutez d'abord un document ou une réponse dans « Documents et preuves », puis sélectionnez cette source.")
        return str(source["id"])

    def add_pending(self) -> None:
        try:
            if not self.case_id:
                raise ValueError("Choisissez un dossier.")
            selected = self.fields_tree.selection()
            if not selected or selected[0] not in self.field_rows:
                raise ValueError("Sélectionnez un champ dans la liste.")
            field_id = selected[0]
            field = self.field_rows[field_id]
            evidence = self._selected_evidence()
            reason = self.reason_var.get().strip()
            if len(reason) < 8:
                raise ValueError("Précisez la justification de cette saisie (au moins huit caractères).")
            value = None if self.clear_var.get() else parse_value(self.value_var.get(), field)
            cell = self.target_rows.get(self.target_var.get())
            mode = self.mode_var.get()
            if mode == "record" and self.clear_var.get():
                raise ValueError("Pour une nouvelle ligne, renseignez les champs utiles et laissez les autres sans proposition.")
            if mode == "update" and not cell:
                raise ValueError("Ce champ ne comporte pas d'emplacement modifiable dans le catalogue.")
            if mode == "record" and self.pending:
                if self.pending[0]["sheet"] != self.loaded_sheet:
                    raise ValueError("Terminez cette ligne avant d'en préparer une autre dans une autre feuille.")
                if self.pending[0]["evidence"] != evidence:
                    raise ValueError("Une nouvelle ligne doit s'appuyer sur une même source. Regroupez les informations dans une réponse documentée.")
            status = next((key for key, label in STATUS_LABELS.items() if label == self.input_status.get()), "HYPOTHESE")
            if self.clear_var.get():
                status = "NON_RENSEIGNE"
            update = {"field_id": field_id, "sheet": self.loaded_sheet, "value": value, "evidence": evidence, "reason": reason, "status": status, "override_default": self.override_var.get(), "replace_existing": self.replace_var.get(), "_label": field.get("label", field_id), "_source_label": self.evidence_var.get(), "_mode": mode}
            if mode == "update":
                update["cell"] = cell
            identity = (update["sheet"], update.get("cell") or field_id)
            self.pending = [p for p in self.pending if (p["sheet"], p.get("cell") or p["field_id"]) != identity]
            self.pending.append(update)
            self.plan = None
            self._render_pending()
            self.status.set("Champ ajouté à la proposition. Le classeur n'a pas encore été modifié.")
        except ValueError as exc:
            self._error("Préparer une saisie", exc)

    def _render_pending(self) -> None:
        self.pending_tree.delete(*self.pending_tree.get_children())
        for index, update in enumerate(self.pending):
            self.pending_tree.insert("", "end", iid=str(index), values=(update["_label"], display_value(update["value"]), STATUS_LABELS.get(update["status"], update["status"]), update["_source_label"]))
        self.pending_title.set(f"Proposition en cours · {len(self.pending)} champ(s)")

    def remove_pending(self) -> None:
        selected = self.pending_tree.selection()
        if selected:
            self.pending.pop(int(selected[0]))
            self.plan = None
            self._render_pending()

    def clear_pending(self) -> None:
        self.pending = []
        self.plan = None
        if hasattr(self, "pending_tree"):
            self._render_pending()

    def prepare(self) -> None:
        if not self.case_id or not self.pending:
            self._error("Vérifier la proposition", "Ajoutez au moins un champ à la proposition.")
            return
        case_id = self.case_id
        updates = [{k: v for k, v in item.items() if not k.startswith("_")} for item in self.pending]
        mode = self.pending[0]["_mode"]
        if mode == "record":
            values = {item["field_id"]: {key: item[key] for key in ("value", "status", "reason", "override_default")} for item in updates}
            task = lambda: self.app.prepare_record(case_id, updates[0]["sheet"], values, updates[0]["evidence"])
        else:
            task = lambda: self.app.prepare_changes(case_id, updates)
        self._run("Vérification de la proposition", task, self.show_plan)

    def show_plan(self, plan: dict) -> None:
        self.plan = plan
        dialog = tk.Toplevel(self.root)
        if self.root.state() == "withdrawn":
            dialog.withdraw()
        dialog.title("Vérifier avant application")
        dialog.geometry("1050x620")
        dialog.minsize(850, 470)
        dialog.transient(self.root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Votre proposition", style="Title.TLabel").pack(anchor="w")
        status = STATUS_LABELS.get(str(plan.get("status")), str(plan.get("status", "À vérifier")))
        ttk.Label(frame, text=status, foreground=TEAL).pack(anchor="w", pady=(5, 12))
        changes = preview_changes(plan, self.date1904)
        tree = self._tree(frame, (("sheet", "Feuille", 165), ("field", "Champ", 250), ("before", "Avant", 225), ("after", "Après", 225)), height=9)
        for change in changes:
            field_label = next((p["_label"] for p in self.pending if p["sheet"] == change.get("sheet") and (p.get("cell") == change.get("cell") or p["field_id"] == change.get("field_id"))), None)
            tree.insert("", "end", values=(change.get("sheet") or "", change.get("label") or field_label or change.get("field_id") or change.get("cell") or "", change["before_display"], display_value(change.get("new_value", change.get("after", change.get("value"))))))
        details = []
        if plan.get("row"):
            details.append(f"Nouvelle ligne disponible sélectionnée : {plan['row']}.")
        if plan.get("questions"):
            details.extend(question_text(q) for q in plan["questions"])
        for key in ("message", "warnings", "errors"):
            if plan.get(key):
                details.append(self._describe(plan[key]))
        if plan_is_ready(plan):
            details.append("L'application créera une nouvelle copie du dossier et conservera la version précédente. Le statut de recalcul sera indiqué après l'opération.")
        else:
            details.append("Complétez les informations demandées puis vérifiez à nouveau la proposition.")
        info = self._text(frame, height=6)
        self._set_text(info, "\n\n".join(details))
        bottom = ttk.Frame(frame)
        bottom.pack(fill="x", pady=(14, 0))
        ttk.Button(bottom, text="Revenir à la saisie", command=dialog.destroy).pack(side="left")
        apply = ttk.Button(bottom, text="Appliquer dans une nouvelle copie", style="Primary.TButton", command=lambda: self.apply_plan(dialog))
        apply.pack(side="right")
        if not plan_is_ready(plan):
            apply.configure(state="disabled")
        self.plan_dialog = dialog
        self.apply_button = apply

    def apply_plan(self, dialog: tk.Toplevel | None = None) -> None:
        if not self.case_id or not self.plan or not plan_is_ready(self.plan):
            return
        case_id, plan_id = self.case_id, self.plan["id"]
        if dialog:
            dialog.destroy()

        def task() -> tuple:
            result = self.app.apply_plan(case_id, plan_id)
            return result, self._case_data(case_id), self.app.list_cases()

        def done(result: tuple) -> None:
            _, case, cases = result
            self.clear_pending()
            self.loaded_sheet = ""
            self.field_rows = {}
            self.snapshot = {}
            self._render_fields()
            self._render_cases(cases)
            self._render_case(case)
            self.tabs.select(self.overview)
            self.status.set("Nouvelle copie enregistrée. Consultez son état de calcul avant d'interpréter les résultats.")

        self._run("Application de la proposition", task, done)

    def add_text_source(self) -> None:
        if not self.case_id:
            return
        text = self.source_text.get("1.0", "end").strip()
        if not text:
            self._error("Ajouter une source", "Renseignez la réponse, son contexte et les informations à conserver.")
            return
        case_id, title = self.case_id, self.source_title.get().strip() or "Réponse utilisateur"

        def task() -> dict:
            self.app.add_source(case_id, text=text, title=title)
            return self._case_data(case_id)

        def done(case: dict) -> None:
            self.source_text.delete("1.0", "end")
            self._render_case(case)
            self.status.set("Source ajoutée au dossier. Elle est disponible dans les propositions de saisie.")

        self._run("Enregistrement de la source", task, done)

    def import_sources(self) -> None:
        if not self.case_id:
            return
        files = filedialog.askopenfilenames(parent=self.root, title="Choisir les documents du dossier", filetypes=(("Documents", "*.pdf *.docx *.xlsx *.xlsm *.pptx *.txt *.md *.csv *.json"), ("Tous les fichiers", "*.*")))
        if not files:
            return
        case_id = self.case_id

        def task() -> dict:
            for filename in files:
                path = Path(filename)
                self.app.add_source(case_id, path=path, title=path.name)
            return self._case_data(case_id)

        self._run("Import des documents", task, self._render_case)

    def send_message(self) -> None:
        if not self.case_id or self.busy:
            return
        text = self.message_var.get().strip()
        if not text:
            return
        case_id = self.case_id
        self.message_var.set("")
        self._append_chat("Vous", text)

        def done(payload: tuple) -> None:
            result, case = payload
            self._render_case(case)
            message = str(result.get("message") or "Demande examinée.")
            sheets = result.get("sheets") or []
            if sheets:
                message += "\n\nFeuilles concernées : " + ", ".join(map(str, sheets))
                for index, agent in enumerate(self.agent_rows):
                    if agent.get("sheet") == sheets[0]:
                        self.agent_combo.current(index)
                        break
            questions = result.get("questions") or []
            if questions:
                message += "\n\nInformations utiles :\n" + "\n".join("• " + question_text(q) for q in questions)
            self._append_chat("Coordinateur", message)
            self.status.set("Demande examinée. Retrouvez les champs de la feuille dans « Saisie guidée ».")

        def task() -> tuple:
            result = self.app.route(case_id, text)
            return result, self._case_data(case_id)

        self._run("Examen de la demande", task, done)

    def _append_chat(self, author: str, text: str) -> None:
        self.transcript.configure(state="normal")
        self.transcript.insert("end", f"\n{author}\n{text}\n")
        self.transcript.see("end")
        self.transcript.configure(state="disabled")

    def answer_question(self) -> None:
        selected = self.question_tree.selection()
        answer = self.answer_var.get().strip()
        if not self.case_id or not selected or not answer:
            self._error("Répondre à la question", "Sélectionnez une question et renseignez votre réponse.")
            return
        question = self.question_rows[selected[0]]
        if not question.get("id"):
            self._error("Répondre à la question", "Cette information n'a pas de question enregistrée. Ajoutez votre réponse dans « Documents et preuves ».")
            return
        case_id = self.case_id

        def task() -> dict:
            self.app.answer_question(case_id, question["id"], answer)
            return self._case_data(case_id)

        def done(case: dict) -> None:
            self.answer_var.set("")
            self._render_case(case)

        self._run("Enregistrement de la réponse", task, done)

    def show_sheet_info(self) -> None:
        sheet, case_id = self._selected_sheet(), self.case_id
        if sheet:
            self._run("Lecture de la fiche de feuille", lambda: self.app.sheet_info(sheet, case_id=case_id), lambda info: self._detail_dialog(sheet, describe_sheet(info)))

    @staticmethod
    def _describe(value: Any, level: int = 0) -> str:
        if isinstance(value, dict):
            return "\n\n".join(str(key).replace("_", " ") + "\n" + BPWindow._describe(item, level + 1) for key, item in value.items() if item is not None and item != [] and item != {})
        if isinstance(value, list):
            return "\n".join("• " + BPWindow._describe(item, level + 1) for item in value)
        return display_value(value)

    def _detail_dialog(self, title: str, text: str) -> None:
        dialog = tk.Toplevel(self.root)
        if self.root.state() == "withdrawn":
            dialog.withdraw()
        dialog.title(title)
        dialog.geometry("900x680")
        dialog.transient(self.root)
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w", pady=(0, 12))
        content = self._text(frame, height=20)
        self._set_text(content, text)
        ttk.Button(frame, text="Fermer", command=dialog.destroy).pack(anchor="e", pady=(12, 0))

    def show_history_detail(self, _event: Any = None) -> None:
        selected = self.history_tree.selection()
        if selected:
            self._detail_dialog("Détail de l'opération", self._describe(self.history_rows[selected[0]]))

    def open_workbook(self) -> None:
        if self.case_id:
            case_id = self.case_id
            self._run("Ouverture du classeur", lambda: self.app.open_workbook(case_id))

    @staticmethod
    def _open_path(path: str | Path) -> None:
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError("Le fichier ou le dossier n'est plus disponible : " + str(path))
        if not hasattr(os, "startfile"):
            raise RuntimeError("L'ouverture native des fichiers est disponible sous Windows.")
        os.startfile(str(path))

    def open_folder(self) -> None:
        if self.case_id:
            path = self.case.get("folder") or self.case.get("directory") or self.case.get("case_path")
            if not path:
                workbook = self.case.get("workbook_path")
                path = str(Path(workbook).parent) if workbook else None
            if not path:
                self._error("Afficher les fichiers", "Le dossier ne fournit pas encore de chemin de classeur.")
                return
            self._run("Ouverture du répertoire", lambda: self._open_path(path))

    def export_report(self) -> None:
        if self.case_id:
            case_id = self.case_id

            def done(path: str) -> None:
                try:
                    self._open_path(path)
                    self.status.set("Rapport créé : " + str(path))
                except Exception as exc:
                    self._error("Ouvrir le rapport enregistré", exc)

            self._run("Création du rapport", lambda: self.app.export_report(case_id), done)

    def recalculate(self) -> None:
        if self.case_id:
            case_id, tables = self.case_id, self.include_tables.get()

            def task() -> tuple:
                result = self.app.recalculate(case_id, include_tables=tables)
                return result, self._case_data(case_id)

            def done(result: tuple) -> None:
                receipt, case = result
                self._render_case(case)
                self._detail_dialog("Résultat du recalcul", self._describe(receipt))

            self._run("Recalcul natif dans Excel", task, done)

    def solve_wacc(self) -> None:
        self._run_native_validation("solve_wacc", "Résolution du WACC", 600)

    def verify_sensitivity(self) -> None:
        self._run_native_validation("verify_sensitivity", "Vérification des sensibilités", 3600)

    def _run_native_validation(self, method: str, title: str, timeout: int) -> None:
        if not self.case_id or self.busy:
            return
        if self.pending:
            self._error(title, "Une proposition de saisie est en cours. Appliquez-la ou videz-la avant de calculer la version enregistrée.")
            return
        case_id = self.case_id
        def task():
            receipt = getattr(self.app, method)(case_id, timeout=timeout)
            return receipt, self._case_data(case_id)
        def done(result):
            receipt, case = result
            self.plan = None
            self.loaded_sheet = ""
            self.field_rows, self.snapshot = {}, {}
            self._render_fields()
            self._render_case(case)
            self._detail_dialog(title, describe_native_receipt(receipt))
        self._run(title + " dans Excel", task, done)

    def close(self) -> None:
        if self.closed:
            return
        if self.busy:
            self.close_when_idle = True
            self.status.set("L'atelier se fermera à la fin de l'opération en cours.")
            return
        self.closed = True
        if self._poll_id:
            self.root.after_cancel(self._poll_id)
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def main(app: Any = None) -> None:
    if app is None:
        from .service import Application
        app = Application()
    root = tk.Tk()
    BPWindow(root, app)
    root.mainloop()


def smoke_test() -> dict:
    """Test Tk réel et caché, avec un service fictif : aucune donnée client lue."""
    from copy import deepcopy

    class SmokeService:
        def __init__(self) -> None:
            self.case = None
            self.applied = 0
            self.prepared = []

        def initialize(self) -> dict:
            return {"status": "READY"}

        def agents(self, case_id=None) -> list[dict]:
            return [{"id": "control", "sheet": "Control", "role": "Calendrier du plan"}]

        def list_cases(self) -> list[dict]:
            return [deepcopy(self.case)] if self.case else []

        def create_case(self, client: str, name: str) -> dict:
            self.case = {"id": "smoke", "client_id": "client-smoke", "client_name": client, "name": name, "revision": 0, "calculation_status": "A_RECALCULER", "sources": [], "history": [], "questions": [], "workbook_path": str(Path(tempfile.gettempdir()) / "tca-gui-smoke-nonexistent.xlsx")}
            return deepcopy(self.case)

        def get_case(self, case_id: str) -> dict:
            assert case_id == "smoke"
            return deepcopy(self.case)

        def add_source(self, case_id: str, *, text: str, title: str) -> dict:
            assert case_id == "smoke" and text
            source = {"id": "preuve-smoke", "title": title, "kind": "text"}
            self.case["sources"].append(source)
            return source

        def fields(self, case_id: str, sheet: str) -> list[dict]:
            return [{"id": "control.horizon", "sheet": "Control", "label": "Nombre d'exercices", "kind": "integer", "cells": ["C59"], "choices": [], "constraints": {"minimum": 1, "maximum": 10}}]

        def inspect(self, case_id: str, sheet: str) -> dict:
            return {"cells": {"C59": {"kind": "integer", "current": {"value": 8, "formula": None}}}}

        def sheet_info(self, sheet: str, case_id=None) -> dict:
            return {"sheet": sheet, "role": "Règle l'horizon du plan.", "questions": ["Combien d'exercices prévoir ?"]}

        def prepare_changes(self, case_id: str, updates: list[dict]) -> dict:
            assert updates[0]["evidence"] == "preuve-smoke"
            self.prepared = updates
            return {"id": "plan-smoke", "status": "PRET_A_APPLIQUER", "changes": updates,
                    "engine_plan": {"changes": [{**updates[0], "expected": {"value": 8, "formula": None}}]}}

        def apply_plan(self, case_id: str, plan_id: str) -> dict:
            assert plan_id == "plan-smoke"
            self.applied += 1
            self.case["revision"] += 1
            self.case["history"].append({"action": "Modification vérifiée", "revision": 1})
            return {"status": "APPLIED"}

        def route(self, case_id: str, text: str) -> dict:
            return {"message": "Le calendrier se règle dans Control.", "sheets": ["Control"], "questions": ["Quel horizon souhaitez-vous ?"]}

    service = SmokeService()
    root = tk.Tk()
    root.withdraw()
    window = BPWindow(root, service, start=False)

    def fail(action: str, error: Any) -> None:
        raise AssertionError(action + ": " + str(error))

    window._error = fail

    def settle() -> None:
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            root.update()
            if not window.busy and window.events.empty():
                root.update()
                return
            time.sleep(0.01)
        raise TimeoutError("Le test de l'interface n'a pas terminé l'opération attendue.")

    try:
        # Lance explicitement l'initialisation afin d'éviter l'attente after(10).
        window.initialize()
        settle()
        assert len(window.agent_rows) == 1
        window.create_case("Client fictif", "Recette interface")
        settle()
        assert window.case_id == "smoke"
        window.source_text.insert("1.0", "Le client souhaite un horizon de six ans.")
        window.add_text_source()
        settle()
        assert window.source_rows
        window.load_sheet()
        settle()
        window.fields_tree.selection_set("control.horizon")
        window._field_selected()
        window.value_var.set("6")
        window.replace_var.set(True)
        window.reason_var.set("Horizon demandé par le client fictif.")
        window.add_pending()
        assert len(window.pending) == 1
        window.prepare()
        settle()
        assert window.apply_button["state"] != "disabled"
        window.apply_button.invoke()
        settle()
        assert service.applied == 1 and window.case["revision"] == 1
        window.message_var.set("Expliquer le calendrier")
        window.send_message()
        settle()
        assert "Le calendrier se règle" in window.transcript.get("1.0", "end")
        assert not window.pending
        return {"status": "OK", "checks": ["ouverture Tk cachée", "création de dossier", "preuve", "lecture de feuille", "proposition typée", "aperçu", "application unique", "actualisation de version", "conversation"], "client_files_touched": False}
    finally:
        window.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atelier BP TCA Conseil")
    parser.add_argument("--smoke", action="store_true", help="Vérifie l'interface avec un dossier fictif, sans fenêtre visible")
    args = parser.parse_args()
    if args.smoke:
        print(json.dumps(smoke_test(), ensure_ascii=False, indent=2))
    else:
        main()
