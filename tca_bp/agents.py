"""Coordinateur déterministe : questions, orientation et propositions vérifiées.

Aucune méthode de ce module n'écrit un classeur. Le service de dossier décide de
la validation humaine et de la transaction, puis appelle le moteur central.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

from .knowledge import (RECORD_IDENTITIES, STATES, contracts, normalized,
                        graph_dependencies, load_model_graph)

PROPOSAL_CONTEXT_KEYS = ('case_id', 'client_id', 'model_id', 'model_ref',
                         'template_sha256', 'schema_sha256', 'revision', 'source_sha256')


def _searchable(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", normalized(value))
    return " ".join(w for w in words if w not in {"de", "du", "des", "d", "le", "la", "les", "l", "un", "une", "au", "aux"})


def _contains(text: str, term: str) -> bool:
    term = _searchable(term)
    return bool(term and re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text))


def _cell_parts(cell: str) -> tuple[str, int]:
    match = re.fullmatch(r"\$?([A-Za-z]{1,3})\$?([1-9][0-9]*)", cell)
    if not match:
        raise ValueError(f"Adresse de cellule invalide : {cell}")
    return match[1].upper(), int(match[2])


def _col_number(column: str) -> int:
    result = 0
    for char in column:
        result = result * 26 + ord(char) - 64
    return result


def _col_name(number: int) -> str:
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _field_cells(field: dict) -> list[str]:
    if isinstance(field.get("cells"), list):
        return list(field["cells"])
    result = []
    for area in field.get("ranges", []):
        bounds = area.split(":")
        first_col, first_row = _cell_parts(bounds[0])
        last_col, last_row = _cell_parts(bounds[-1])
        for row in range(first_row, last_row + 1):
            for column in range(_col_number(first_col), _col_number(last_col) + 1):
                result.append(_col_name(column) + str(row))
    return result


def _empty(value: Any) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


def _unit(field: dict) -> str:
    return str(field.get('unit') or field.get('semantics',{}).get('unit') or 'NON_ETABLIE : revue du catalogue requise')


class Coordinator:
    """Oriente la demande vers des contrats de responsabilité et un moteur unique."""

    def __init__(self, engine):
        self.engine = engine
        self._agents = contracts()
        self._by_sheet = {agent["sheet"]: agent for agent in self._agents}
        self._graph_cache = None
        self._graph_key = None

    def _dependency_graph(self, extra_nodes=()) -> dict:
        model_dir = getattr(self.engine, 'model_dir', None)
        path = Path(model_dir) / 'graphe_dependances.json' if model_dir else None
        stamp = path.stat() if path and path.is_file() else None
        key = (self.engine.model_id, str(path), stamp.st_mtime_ns if stamp else None,
               stamp.st_size if stamp else None)
        injected = getattr(self.engine, 'dependency_graph', None) is not None
        absent = self._graph_cache is None or any(node not in self._graph_cache['key_nodes'] for node in extra_nodes)
        if injected or key != self._graph_key or absent:
            self._graph_cache = load_model_graph(self.engine, extra_nodes)
            self._graph_key = key
        return self._graph_cache

    def _sheet(self, name: str) -> str:
        for sheet in self._by_sheet:
            if normalized(name) == normalized(sheet):
                return sheet
        raise ValueError(f"Feuille inconnue : {name}")

    def _catalog(self) -> list[dict]:
        catalog = self.engine.catalog()
        return list(catalog.get("fields", [])) if isinstance(catalog, dict) else list(catalog)

    def merge_proposals(self, proposals: list[dict], *, expected_context: dict | None = None) -> dict:
        """Réconcilier un lot explicite ; aucun arbitrage de valeur ou écriture.

        Chaque agent peut suggérer une entrée d'une autre feuille : son identité
        décrit l'auteur, elle n'élargit jamais le catalogue d'écriture. Une pièce
        documentaire ne constitue pas une proposition autorisée.
        """
        if not isinstance(proposals, list) or not 1 <= len(proposals) <= 33:
            raise ValueError('Le lot doit contenir de 1 à 33 propositions structurées.')
        agents = {agent['id'] for agent in self._agents}
        fields = self._catalog()
        by_field = {field['id']: field for field in fields}
        by_cell = {(f['sheet'], cell): f for f in fields for cell in _field_cells(f)}
        known_context = deepcopy(expected_context)
        candidates, questions, refused = {}, [], []
        total = 0

        def question(text, **details):
            value = {'question': text, **details}
            if value not in questions:
                questions.append(value)

        for index, proposal in enumerate(proposals):
            if not isinstance(proposal, dict) or set(proposal) - {'agent_id', 'context', 'updates', 'questions', 'origin'}:
                raise ValueError('Proposition mal formée ou champs inconnus.')
            author = proposal.get('agent_id')
            if not isinstance(author, str) or author not in agents:
                raise ValueError('Identifiant d’agent inconnu dans les 33 contrats.')
            if proposal.get('origin', 'agent_proposal') != 'agent_proposal':
                refused.append({'agent_id': author, 'code': 'DOCUMENT_SANS_AUTORITE',
                                'message': 'La pièce reste une source de données ; reformuler une proposition sur demande utilisateur.'})
                continue
            context = proposal.get('context')
            if not isinstance(context, dict) or set(context) != set(PROPOSAL_CONTEXT_KEYS):
                raise ValueError('Contexte complet du dossier et de la version requis pour chaque proposition.')
            if any(not isinstance(context[key], str) or not context[key] for key in PROPOSAL_CONTEXT_KEYS if key != 'revision') or isinstance(context['revision'], bool) or not isinstance(context['revision'], int) or context['revision'] < 0:
                raise ValueError('Types d’identité, d’empreinte ou de révision invalides.')
            if context.get('model_id') != self.engine.model_id:
                raise ValueError('La proposition vise un autre modèle.')
            if known_context is None:
                known_context = deepcopy(context)
            if context != known_context:
                raise ValueError('Les propositions ne portent pas la même identité, version ou empreinte courante.')
            pending = proposal.get('questions', [])
            if not isinstance(pending, list) or len(pending) > 30:
                raise ValueError('Questions attendues sous forme de liste limitée à 30 éléments par agent.')
            for item in pending:
                text = item if isinstance(item, str) else item.get('question') if isinstance(item, dict) else None
                if not isinstance(text, str) or not 1 <= len(text.strip()) <= 2000:
                    raise ValueError('Question d’agent invalide.')
                question(text.strip(), agent_id=author, code='QUESTION_AGENT')
            updates = proposal.get('updates', [])
            if not isinstance(updates, list):
                raise ValueError('Les changements doivent être une liste.')
            total += len(updates)
            if total > 2000:
                raise ValueError('Un lot d’agents est limité à 2 000 propositions de cellules.')
            for raw in updates:
                allowed = {'sheet', 'cell', 'field_id', 'value', 'reason', 'evidence', 'status', 'override_default', 'replace_existing'}
                if not isinstance(raw, dict) or set(raw) - allowed or 'value' not in raw:
                    raise ValueError('Changement mal formé ; formules et autorisations libres refusées.')
                update = deepcopy(raw)
                field = by_field.get(update.get('field_id'))
                if update.get('field_id') and field is None:
                    raise ValueError('Champ inconnu dans le catalogue du modèle.')
                if field:
                    update.setdefault('sheet', field['sheet'])
                    if 'cell' not in update and len(_field_cells(field)) == 1:
                        update['cell'] = _field_cells(field)[0]
                pair = (update.get('sheet'), update.get('cell'))
                if not all(isinstance(part, str) for part in pair):
                    raise ValueError('Feuille et cellule explicites requises.')
                if pair not in by_cell or field and pair not in {(field['sheet'], c) for c in _field_cells(field)}:
                    refused.append({'agent_id': author, 'code': 'HORS_CATALOGUE', 'field': '!'.join(str(p) for p in pair),
                                    'message': 'Cette proposition ne vise pas une entrée autorisée.'})
                    continue
                value = update['value']
                if not (value is None or isinstance(value, (str, int, float, bool))) or isinstance(value, float) and not math.isfinite(value):
                    raise ValueError('Une valeur scalaire JSON finie est requise.')
                if isinstance(value, str) and value.lstrip().startswith(('=', '+', '@')):
                    raise ValueError('Une pièce ou un agent ne peut introduire une formule libre.')
                status = update.get('status', 'HYPOTHESE')
                if status not in ('CONFIRME', 'HYPOTHESE', 'NON_RENSEIGNE') or (value is None) != (status == 'NON_RENSEIGNE'):
                    raise ValueError('Valeur et qualification incompatibles ; INACTIF ne neutralise pas une cellule.')
                if not isinstance(update.get('evidence'), str) or not update['evidence'].strip():
                    raise ValueError('Chaque proposition doit référencer une source du dossier.')
                if not isinstance(update.get('reason'), str) or not 8 <= len(update['reason'].strip()) <= 4000:
                    raise ValueError('Une justification métier de 8 à 4 000 caractères est requise.')
                for flag in ('override_default', 'replace_existing'):
                    if flag in update and not isinstance(update[flag], bool):
                        raise ValueError('Les choix de remplacement sont des booléens explicites.')
                item = {'sheet': pair[0], 'cell': pair[1], 'value': value, 'status': status,
                        'reason': update['reason'].strip(), 'evidence': update['evidence'],
                        'override_default': update.get('override_default', False),
                        'replace_existing': update.get('replace_existing', False)}
                candidates.setdefault(pair, []).append({'agent_id': author, 'update': item})

        updates, conflicts, contributions = [], [], []
        for pair, variants in sorted(candidates.items()):
            signatures = {}
            for variant in variants:
                item = variant['update']
                value = item['value']
                typed = ('boolean', value) if isinstance(value, bool) else ('number', value) if isinstance(value, (int, float)) else (type(value).__name__, value)
                key = (typed, item['status'], item['override_default'], item['replace_existing'])
                signatures.setdefault(key, []).append(variant)
            provenance = sorted(variants, key=lambda v: (v['agent_id'], v['update']['evidence'], v['update']['reason']))
            detail = {'field': '!'.join(pair), 'field_id': by_cell[pair]['id'], 'proposals': provenance}
            contributions.append(detail)
            if len(signatures) > 1:
                conflicts.append({**detail, 'code': 'PROPOSITIONS_INCOMPATIBLES'})
                question('Quelle valeur, qualification et autorisation de remplacement retenir pour ' + '!'.join(pair) + ' ?',
                         field='!'.join(pair), field_id=by_cell[pair]['id'], code='CONFLIT_A_ARBITRER')
                continue
            merged = deepcopy(provenance[0]['update'])
            reasons = sorted({v['update']['reason'] for v in variants})
            evidence = sorted({v['update']['evidence'] for v in variants})
            merged['evidence'] = evidence[0]
            merged['reason'] = ' ; '.join(reasons) + ' [sources concordantes : ' + ', '.join(evidence) + ']'
            updates.append(merged)
        if refused:
            status = 'REFUSED'
        elif conflicts or questions:
            status = 'NEEDS_REVIEW' if conflicts else 'NEEDS_INPUT'
        elif updates:
            status = 'READY_FOR_PREPARATION'
        else:
            status = 'NEEDS_INPUT'
            question('Renseigner au moins une proposition de saisie sourcée.', code='LOT_VIDE')
        digest = hashlib.sha256(json.dumps({'context': known_context, 'contributions': contributions, 'questions': questions, 'refusals': refused},
                    sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        return {'schema': 'tca-bp-agent-proposals/1', 'status': status, 'context': known_context,
                'proposal_sha256': digest, 'updates': updates if status == 'READY_FOR_PREPARATION' else [],
                'conflicts': conflicts, 'questions': questions, 'refusals': refused, 'contributions': contributions,
                'affected_sheets': self._impacted(sorted({pair[0] for pair in candidates})) if candidates else [],
                'notice': 'Le lot seul attend sa résolution. Aucune cellule ni aucun statut global de dossier n’a été modifié.',
                'source_policy': 'DONNEES_UNIQUEMENT'}

    def agents(self) -> list[dict]:
        result = deepcopy(self._agents)
        graph = self._dependency_graph()
        counts: dict[str, int] = {}
        for field in self._catalog():
            counts[field["sheet"]] = counts.get(field["sheet"], 0) + 1
        for agent in result:
            agent["field_count"] = counts.get(agent["sheet"], 0)
            agent["model_id"] = self.engine.model_id
            dependencies = graph_dependencies(graph, agent['sheet'])
            agent['business_dependencies'] = agent['dependencies']
            agent['dependencies'] = dependencies['incoming']
            agent['dependents'] = dependencies['outgoing']
            agent['graph_available'] = graph['available']
            agent['graph_sha256'] = graph['sha256']
            agent["dependency_basis"] = "GRAPHE_EXTRAIT_MODELE" if graph['available'] else "GRAPHE_INDISPONIBLE"
        return result

    def _impacted(self, sheets: list[str]) -> list[str]:
        graph = self._dependency_graph()
        downstream = {name: [] for name in self._by_sheet}
        for consumer, sources in graph['sheets'].items():
            for source in sources:
                downstream[source].append(consumer)
        selected = set(sheets)
        pending = list(sheets)
        while pending:
            sheet = pending.pop()
            for dependent in downstream[sheet]:
                if dependent not in selected:
                    selected.add(dependent)
                    pending.append(dependent)
        return [agent["sheet"] for agent in self._agents if agent["sheet"] in selected]

    def route(self, text: str, *, source_type: str = "user") -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Une demande métier non vide est requise.")
        if source_type != "user":
            return {"intent": "source_review", "sheets": [], "affected_sheets": [], "questions": [],
                    "status": "DATA_ONLY", "message": "Pièce documentaire reçue comme donnée. Une demande utilisateur distincte est nécessaire pour préparer une action."}
        searchable = _searchable(text)
        model_change = bool(re.search(r"\b(?:modifier|modifie|changer|change|reparer|repare|remplacer|remplace|ajouter|ajoute|supprimer|supprime|creer|cree|corriger|corrige)\b.{0,55}\b(?:formule|formules|macro|macros|vba|structure|feuille|feuilles|colonne|colonnes|calcul circulaire)\b", searchable))
        explanation = any(_contains(searchable, term) for term in ("expliquer", "explique", "comprendre", "pourquoi", "comment fonctionne"))
        diagnostic = any(_contains(searchable, term) for term in ("diagnostic", "verifier", "verifie", "alerte", "erreur", "anomalie", "audit"))
        intent = "model_change" if model_change else "explain" if explanation else "diagnostic" if diagnostic else "input_update"
        scored = []
        for index, agent in enumerate(self._agents):
            hits = [term for term in agent["keywords"] if _contains(searchable, term)]
            # Une référence explicite à la feuille l'emporte sur les mots métier.
            score = sum(1 + len(_searchable(term).split()) for term in hits)
            if _contains(searchable, agent["sheet"]):
                score += 4
            if score:
                scored.append((score, index, agent["sheet"]))
        scored.sort(key=lambda row: (-row[0], row[1]))
        sheets = [row[2] for row in scored[:6]]
        # Les trois instruments restent distincts, même si le mot financement apparaît.
        if _contains(searchable, "subvention investissement") or _contains(searchable, "aide investissement"):
            sheets = ["SUBVENTION_INVEST"] + [s for s in sheets if s not in ("DATA Financement", "SUBVENTION_INVEST")]
        if not sheets:
            return {"intent": intent, "sheets": [], "affected_sheets": [], "questions": ["Souhaitez-vous renseigner une opération, expliquer un résultat ou faire évoluer une règle du modèle ?"],
                    "status": "NEEDS_INPUT", "message": "Le module métier n'est pas encore identifié. Aucune saisie préparée."}
        questions = []
        for sheet in sheets:
            for question in self._by_sheet[sheet]["questions"]:
                if question not in questions:
                    questions.append(question)
        if intent == "model_change":
            questions = ["Quelle règle économique attendue et quel exemple avant/après ?",
                         "Quels résultats indépendants doivent vérifier la nouvelle règle ?"]
            message = "Demande orientée vers le développement versionné : analyse d'impact, modification sur copie et tests. Le parcours de saisie ne modifie aucune formule de calcul."
        elif intent in ("explain", "diagnostic"):
            message = "Les agents concernés retracent les sources. La lecture d'un cache ne démontre pas un résultat recalculé."
        else:
            message = "Préparer les réponses sourcées puis un lot vérifié par le moteur. Les données manquantes restent ouvertes."
        impacted = self._impacted(sheets)
        graph = self._dependency_graph()
        if not graph['available']:
            message += " Graphe extrait indisponible : les conséquences aval restent à déterminer."
        return {"intent": intent, "sheets": sheets, "affected_sheets": impacted,
                "questions": questions[:4], "status": "ROUTED" if graph['available'] else "NEEDS_REVIEW", "message": message,
                "dependency_basis": "GRAPHE_EXTRAIT_MODELE" if graph['available'] else "GRAPHE_INDISPONIBLE",
                "impact_scope": "FERMETURE_AVAL_CONSERVATRICE_PAR_FEUILLE",
                "graph_sha256": graph['sha256'], "dependency_limits": list(graph['limits']),
                "requires_development": intent == "model_change", "can_write": False}

    def questions(self, sheet: str, context: dict | None = None) -> list[dict]:
        sheet = self._sheet(sheet)
        context = context or {}
        answers = context.get("answers", {})
        if isinstance(answers, list):
            answers = {answer.get("field_id"): answer for answer in answers if isinstance(answer, dict)}
        register = self.engine.schema.get("registers", {}).get(sheet, {})
        required_columns = set(register.get("required", []))
        result = []
        for field in self._catalog():
            if field.get("sheet") != sheet:
                continue
            answer = answers.get(field["id"])
            semantic_review = field.get('semantics',{}).get('status') == 'REEXAMEN_REQUIS'
            if not semantic_review and isinstance(answer, dict) and answer.get("status") in ("CONFIRME", "VERIFIE_SUR_PERIMETRE") and not _empty(answer.get("value", answer.get("normalized_value"))):
                continue
            cells = _field_cells(field)
            required = bool(required_columns.intersection(_cell_parts(cell)[0] for cell in cells))
            constraints = field.get("constraints") or {}
            if constraints.get("allow_blank") is False:
                required = True
            label = field.get("label", field["id"])
            status = answer.get("status", "NON_RENSEIGNE") if isinstance(answer, dict) else "NON_RENSEIGNE"
            result.append({"id": "Q_" + field["id"], "field_id": field["id"], "sheet": sheet,
                "label": label, "question": (f"Faire réexaminer par TCA l’unité, l’assiette ou le propriétaire de « {label} » avant toute nouvelle saisie." if semantic_review else f"Quelle valeur documentée retenir pour « {label} » ?"),
                "kind": field.get("kind", "text"), "unit": _unit(field), "choices": deepcopy(field.get("choices")),
                "constraints": deepcopy(constraints), "required": required or semantic_review, "priority": 0 if semantic_review else 1 if required else 2,
                "status": 'SEMANTIQUE_A_REEXAMINER' if semantic_review else status, "source": "CATALOGUE_MODELE", "source_required": True,
                "notes": deepcopy(field.get("notes", [])), "cells": cells,
                "basis": field.get('basis'), "semantics": deepcopy(field.get('semantics'))})
        if not result and not any(f.get("sheet") == sheet for f in self._catalog()):
            for i, question in enumerate(self._by_sheet[sheet]["questions"], 1):
                result.append({"id": f"Q_{self._by_sheet[sheet]['id']}_{i}", "sheet": sheet,
                    "field_id": None, "question": question, "kind": "context", "required": False,
                    "priority": 2, "status": "NON_RENSEIGNE", "source": "CONTRAT_METIER"})
        return sorted(result, key=lambda question: question["priority"])

    def _inspect(self, workbook: Path, sheet: str, cells: list[str]) -> dict:
        if not cells:
            return {}
        inspection = self.engine.inspect(workbook, sheet, cells)
        if "inputs" in inspection:
            return inspection["inputs"].get(sheet, {})
        return inspection.get("cells", inspection)

    def explain(self, sheet: str, cell: str | None = None, *, workbook: str | Path | None = None,
                calculation_evidence: dict | None = None) -> dict:
        sheet = self._sheet(sheet)
        path = Path(workbook or self.engine.template_path)
        result = deepcopy(self._by_sheet[sheet])
        if cell is not None:
            col, row = _cell_parts(cell)
            cell = col + str(row)
        graph = self._dependency_graph([(sheet, cell)] if cell else ())
        dependencies = graph_dependencies(graph, sheet)
        result['business_dependencies'] = result['dependencies']
        result['dependencies'] = dependencies['incoming']
        result['dependents'] = dependencies['outgoing']
        result.update(model_id=self.engine.model_id,
                      dependency_basis="GRAPHE_EXTRAIT_MODELE" if graph['available'] else "GRAPHE_INDISPONIBLE",
                      graph_sha256=graph['sha256'], dependency_limits=list(graph['limits']),
                      calculation_status="NON_VERIFIE", result_claims_allowed=False, workbook=str(path))
        addresses = list(dict.fromkeys([point['cell'] for point in result['key_calculations']] + ([cell] if cell else [])))
        try:
            readings = self._inspect(path, sheet, addresses)
        except (ValueError, KeyError, OSError) as exc:
            readings = {}
            result['inspection_notice'] = str(exc)
        for point in result['key_calculations']:
            observed = readings.get(point['cell'])
            current = observed.get('current', observed) if observed else {}
            point.update(formula=current.get('formula'), reading_status='CELLULE_LUE' if observed else 'LECTURE_INDISPONIBLE',
                         value_status='CACHE_NON_CERTIFIE' if current.get('formula') is not None else 'DONNEE_NON_QUALIFIEE')
            node = graph['key_nodes'].get((sheet, point['cell']), {})
            effective = current.get('formula')
            matches = isinstance(effective, str) and node.get('formula_sha256') == hashlib.sha256(effective.encode('utf-8')).hexdigest()
            point['dependency_status'] = 'FORMULE_CONFORME_AU_GRAPHE' if matches else 'DEPENDANCES_NON_VERIFIEES'
            point['references'] = list(node.get('references', [])) if matches else []
            point['defined_names'] = list(node.get('defined_names', [])) if matches else []
        if cell is not None:
            column, row = _cell_parts(cell)
            cell = column + str(row)
            try:
                inspected = readings.get(cell)
                if inspected:
                    current = inspected.get("current", inspected)
                    result["cell"] = cell
                    result["current"] = deepcopy(current)
                    result["formula"] = current.get("formula")
                    result["field"] = {key: value for key, value in inspected.items() if key != "current"}
                    result["formula_source"] = "LECTURE_CLASSEUR" if current.get("formula") is not None else "AUCUNE_FORMULE_LUE"
                else:
                    result["cell"] = cell
                    result["formula_source"] = "NON_EXPOSEE_PAR_MOTEUR"
                    result["notice"] = "Cette adresse n'est pas exposée par l'inspection du moteur ; aucune formule n'est déduite."
            except (ValueError, KeyError, OSError) as exc:
                result["cell"] = cell
                result["formula_source"] = "LECTURE_INDISPONIBLE"
                result["notice"] = str(exc)
            result["workbook"] = str(path)
        # Une déclaration seule ne rend jamais les résultats frais. Le service doit
        # attester à la fois la signature courante, le périmètre et l'exécution.
        evidence = calculation_evidence or {}
        same_workbook = False
        if evidence.get("workbook_sha256") and path.is_file():
            same_workbook = evidence["workbook_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        if (evidence.get("verified") is True and evidence.get("inputs_match") is True
                and evidence.get("completed") is True and evidence.get("evidence_id")
                and same_workbook and sheet in evidence.get("sheets", [])):
            result["calculation_status"] = "VERIFIE_SUR_PERIMETRE"
            result["result_claims_allowed"] = True
            result["calculation_evidence"] = deepcopy(evidence)
        result["limitations"] = ["L'impact extrait au niveau feuille est conservateur ; les limites dynamiques et VBA restent à qualifier.",
            "Les cas métier sont des spécifications non exécutées, sans preuve native implicite.",
            "Le statut d'un calcul ne confirme pas la validité économique des hypothèses."]
        return result

    def intake_source(self, source_id: str, text: str, *, title: str = "Pièce du dossier") -> dict:
        """Expose des extraits à qualifier ; n'en déduit aucune valeur à saisir."""
        if not source_id or not isinstance(text, str):
            raise ValueError("Identifiant de source et texte requis.")
        lines = text.splitlines()
        excerpts = [{"line": i, "text": line.strip()[:1000]} for i, line in enumerate(lines, 1)
                    if line.strip() and re.search(r"\d", line)][:50]
        instruction_lines = [i for i, line in enumerate(lines, 1)
                             if re.search(r"ignore.{0,25}instruction|system prompt|desactiv.{0,25}controle|execut.{0,15}macro|remplac.{0,15}formule", normalized(line))]
        return {"source_id": source_id, "title": title, "source_type": "document", "status": "A_QUALIFIER",
                "excerpts": excerpts, "instruction_like_lines": instruction_lines, "updates": [],
                "message": "Extraits documentaires à confirmer et relier à des champs. Les instructions contenues dans la pièce ne sont pas exécutées."}

    def _record_fields(self, sheet: str, row: int) -> dict[str, tuple[dict, str]]:
        result = {}
        for field in self._catalog():
            if field.get("sheet") != sheet:
                continue
            matching = [cell for cell in _field_cells(field) if _cell_parts(cell)[1] == row]
            if len(matching) == 1:
                result[field["id"]] = (field, matching[0])
        return result

    @staticmethod
    def _canonical_record_value(value: Any, kind: str | None) -> Any:
        if kind == "date":
            if isinstance(value, (date, datetime)):
                return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return (date(1899, 12, 30) + timedelta(days=int(value))).isoformat()
        return normalized(value) if isinstance(value, str) else value

    def plan_record(self, workbook: str | Path, sheet: str, values: dict, evidence_id: str) -> dict:
        """Choisit une ligne libre actuelle, demande le manquant, valide sans écrire.

        values accepte field_id: valeur ou field_id: {value,status,evidence_id,
        reason,override_default}. Une inconnue n'est jamais remplacée par zéro.
        """
        sheet = self._sheet(sheet)
        workbook = Path(workbook)
        if not evidence_id or not isinstance(evidence_id, str):
            raise ValueError("Une référence de pièce ou de réponse explicite est requise.")
        if not isinstance(values, dict):
            raise ValueError("Les réponses doivent être un objet field_id → valeur.")
        if sheet not in self.engine.schema.get("registers", {}):
            raise ValueError("Cette feuille n'est pas un registre ; utiliser une proposition de champs explicitement adressés.")
        context = self.engine.context(workbook)
        register = context.get("registers", {}).get(sheet, {})
        row = register.get("first_free_row")
        result = {"status": "NEEDS_INPUT", "sheet": sheet, "row": row, "updates": [], "questions": [],
                  "evidence_id": evidence_id, "model_id": self.engine.model_id, "can_write": False,
                  "source_sha256": context.get("source_sha256"), "plan": None}
        if row is None:
            result.update(status="REFUSED", message="Le registre ne contient plus de ligne libre. Une évolution de structure doit passer par le développement.")
            return result
        fields = self._record_fields(sheet, row)
        unknown = sorted(set(values) - set(fields))
        if unknown:
            raise ValueError("Champs inconnus ou hors registre : " + ", ".join(unknown))
        current = self._inspect(workbook, sheet, [address for _, address in fields.values()])
        missing_inspection = [address for _, address in fields.values() if address not in current]
        if missing_inspection:
            result.update(status="REFUSED", message="Inspection incomplète de la ligne libre : " + ", ".join(missing_inspection))
            return result
        metadata = {}
        prepared = {}
        for field_id, answer in values.items():
            payload = answer if isinstance(answer, dict) and "value" in answer else {"value": answer, "status": "HYPOTHESE"}
            status = payload.get("status", "HYPOTHESE")
            if status not in STATES:
                raise ValueError(f"État de réponse inconnu : {status}")
            field, address = fields[field_id]
            metadata[field_id] = {"status": status, "evidence_id": payload.get("evidence_id") or evidence_id}
            if status in ("NON_RENSEIGNE", "INACTIF", "A_RECALCULER", "VERIFIE_SUR_PERIMETRE") or _empty(payload["value"]):
                result["questions"].append({"field_id": field_id, "status": status,
                    "question": f"Préciser « {field.get('label', field_id)} » ; aucune valeur n'est déduite de cet état."})
                continue
            if isinstance(payload["value"], (dict, list)):
                raise ValueError(f"Valeur scalaire attendue pour {field_id}.")
            prepared[address] = (field_id, field, payload)
        required_columns = self.engine.schema["registers"][sheet].get("required", [])
        for column in required_columns:
            address = column + str(row)
            if address in prepared:
                continue
            snapshot = current.get(address, {}).get("current", current.get(address, {}))
            if snapshot.get("formula") is not None or not _empty(snapshot.get("value")):
                continue
            match = next(((field_id, field) for field_id, (field, addr) in fields.items() if addr == address), None)
            if match and not any(question.get("field_id") == match[0] for question in result["questions"]):
                result["questions"].append({"field_id": match[0], "required": True, "status": "NON_RENSEIGNE",
                    "question": f"Quelle valeur documentée pour « {match[1].get('label', match[0])} » ?",
                    "kind": match[1].get("kind"), "unit": _unit(match[1]), "choices": match[1].get("choices")})
        updates = []
        for address, (field_id, field, payload) in prepared.items():
            snapshot = current[address].get("current", current[address])
            update = {"sheet": sheet, "cell": address, "value": payload["value"],
                "reason": payload.get("reason") or f"Réponse documentée pour {field.get('label', field_id)} ; source {metadata[field_id]['evidence_id']}.",
                "evidence": metadata[field_id]["evidence_id"], "status": metadata[field_id]["status"],
                "expected": {"value": snapshot.get("value"), "formula": snapshot.get("formula")}}
            if snapshot.get("formula") is not None:
                if payload.get("override_default") is not True:
                    result["questions"].append({"field_id": field_id, "status": "DEFAULT_OVERRIDE_REQUIRES_REASON",
                        "question": f"Le champ « {field.get('label', field_id)} » possède un défaut calculé. Confirmer son remplacement et sa raison."})
                    continue
                if not isinstance(payload.get("reason"), str) or len(payload["reason"].strip()) < 8:
                    result["questions"].append({"field_id": field_id, "status": "DEFAULT_OVERRIDE_REQUIRES_REASON",
                        "question": "Quelle raison métier justifie de remplacer ce défaut calculé ?"})
                    continue
                update["override_default"] = True
            elif snapshot.get("value") is not None and snapshot.get("value") != payload["value"]:
                update["replace_existing"] = True
            updates.append(update)
        # Le service possède la source, le dossier et la transaction. Il reçoit
        # son format public strict; expected reste réservé à la première validation.
        result["updates"] = [{key: value for key, value in update.items() if key != "expected"} for update in updates]
        result["expected_states"] = {update["cell"]: deepcopy(update["expected"]) for update in updates}
        result["answers"] = metadata
        if result["questions"]:
            result["message"] = "Informations à compléter avant toute saisie de la ligne. Les valeurs déjà fournies restent dans la proposition."
            return result
        if not updates:
            result["message"] = "Aucune valeur documentée à saisir."
            return result
        identity_columns = RECORD_IDENTITIES.get(sheet, [])
        if identity_columns and all(col + str(row) in prepared for col in identity_columns):
            occupied = register.get("occupied_rows", [])
            existing = self._inspect(workbook, sheet, [col + str(r) for r in occupied for col in identity_columns])
            duplicates = []
            for old_row in occupied:
                same = True
                for column in identity_columns:
                    _, field, payload = prepared[column + str(row)]
                    old = existing.get(column + str(old_row), {})
                    if not old:
                        same = False
                        break
                    old_value = old.get("current", old).get("value")
                    if self._canonical_record_value(old_value, field.get("kind")) != self._canonical_record_value(payload["value"], field.get("kind")):
                        same = False
                        break
                if same:
                    duplicates.append(old_row)
            if duplicates:
                result.update(status="NEEDS_REVIEW", duplicate_rows=duplicates,
                    message="Une opération possède déjà les mêmes éléments d'identité. Vérifier la ligne existante avant d'en créer une autre.")
                return result
        try:
            engine_updates = [{key: value for key, value in update.items() if key != "status"} for update in updates]
            result["plan"] = self.engine.prepare(workbook, engine_updates)
            result.update(status="READY", message="Proposition complète vérifiée contre le classeur courant. Le service de dossier peut la présenter pour validation.")
        except (ValueError, KeyError, TypeError, OSError) as exc:
            result.update(status="REFUSED", message=str(exc))
            result["questions"].append({"status": "ENGINE_VALIDATION", "question": str(exc)})
        return result

    def build_record_updates(self, workbook: str | Path, sheet: str, values: dict, evidence_id: str) -> list[dict]:
        result = self.plan_record(workbook, sheet, values, evidence_id)
        if result["status"] != "READY":
            raise ValueError(result.get("message", "Proposition incomplète."))
        return result["updates"]

    def import_record_proposal(self, workbook: str | Path, proposal: dict) -> dict:
        """Valide une proposition JSON de saisie ; aucune formule libre ni action embarquée."""
        allowed = {"schema", "model_id", "intent", "sheet", "values", "evidence_id"}
        if not isinstance(proposal, dict) or set(proposal) - allowed:
            raise ValueError("Structure de proposition inconnue.")
        if proposal.get("schema") != "tca-bp-record-proposal/1" or proposal.get("model_id") != self.engine.model_id:
            raise ValueError("Proposition destinée à un autre schéma ou modèle.")
        if proposal.get("intent") != "input_update":
            raise ValueError("Seule une proposition de saisie est acceptée ; les évolutions sont séparées.")
        return self.plan_record(workbook, proposal.get("sheet", ""), proposal.get("values", {}), proposal.get("evidence_id", ""))
