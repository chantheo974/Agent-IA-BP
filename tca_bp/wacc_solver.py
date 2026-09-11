"""Recherche locale bornée d'un point fixe du WACC.

Ce composant ne fournit aucune hypothèse financière. L'évaluateur doit calculer
le WACC et l'equity du même scénario pour chaque candidat. Il n'active aucune
itération circulaire d'Excel et ne poursuit aucune valeur d'entreprise cible.
Une convergence locale n'est pas une preuve d'unicité globale.
"""
from __future__ import annotations

import math
import time

ALGORITHM_ID = "tca-local-wacc/1"
RESIDUAL_TOLERANCE = 1e-10
MAX_EVALUATIONS = 180


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def solve(evaluate, growth, *, timeout=120, clock=time.monotonic):
    """L'évaluateur retourne validity='OK', calculated, equity et fingerprint.

    L'empreinte des entrées doit rester identique entre toutes les évaluations.
    Des observations invalides coupent l'intervalle ; on ne les franchit jamais
    pour inventer un encadrement. Les exceptions opérationnelles se propagent.
    """
    if not _finite(growth) or not -1 < growth < 5 - 2e-6:
        raise ValueError("Croissance terminale hors domaine de résolution.")
    if not _finite(timeout) or timeout <= 0:
        raise ValueError("Délai positif requis.")
    started = clock()
    lower, upper = max(growth + 2e-6, -1 + 2e-6), 5.0
    evaluations = []
    fingerprint = None

    def result(status, **extra):
        return {"algorithm": ALGORITHM_ID, "status": status, "converged": status == "CONVERGENCE_LOCALE",
                "domain": [lower, upper], "tolerance": RESIDUAL_TOLERANCE,
                "evaluations": len(evaluations), "observations": evaluations,
                "global_uniqueness_proven": False, **extra}

    class Exhausted(Exception):
        pass

    class Changed(Exception):
        pass

    def observe(candidate):
        nonlocal fingerprint
        if clock() - started >= timeout or len(evaluations) >= MAX_EVALUATIONS:
            raise Exhausted()
        item = evaluate(candidate)
        if not isinstance(item, dict):
            raise ValueError("Réponse scalaire structurée requise.")
        current = item.get("fingerprint")
        if not isinstance(current, str) or not current:
            raise ValueError("Empreinte des entrées absente de l'évaluation.")
        if fingerprint is not None and current != fingerprint:
            raise Changed()
        fingerprint = current
        calculated, equity = item.get("calculated"), item.get("equity")
        valid = (item.get("validity") == "OK" and _finite(calculated) and _finite(equity)
                 and equity > 0 and calculated > growth + 1e-6)
        observation = {"candidate": candidate, "valid": valid,
                       "calculated": calculated if _finite(calculated) else None,
                       "equity": equity if _finite(equity) else None,
                       "residual": calculated - candidate if valid else None}
        evaluations.append(observation)
        # L'appel scalaire peut avoir pris tout le délai restant, notamment la
        # dernière évaluation de confirmation. Il compte comme une évaluation,
        # mais son résultat tardif ne peut pas devenir une convergence valide.
        if clock() - started >= timeout:
            raise Exhausted()
        return observation

    def success(observation):
        # Une nouvelle évaluation finale est obligatoire, même si le balayage
        # avait déjà observé un zéro. Une sortie instable ne peut pas réussir.
        final = observe(observation["candidate"])
        if not final["valid"] or abs(final["residual"]) > RESIDUAL_TOLERANCE:
            return result("EVALUATION_FINALE_INCOHERENTE")
        return result("CONVERGENCE_LOCALE", candidate=final["candidate"], calculated=final["calculated"],
                      residual=final["residual"], equity=final["equity"], fingerprint=fingerprint)

    try:
        # Maillage uniforme dans log(1+w), bornes comprises ; l'amorce25%
        # constitue uniquement une évaluation numérique supplémentaire.
        log_lower, log_upper = math.log1p(lower), math.log1p(upper)
        # Injecter chaque borne une seule fois : expm1(log1p(borne)) peut
        # différer d'un ULP et créer artificiellement deux racines observées.
        points = [lower, *[math.expm1(log_lower + i / 80 * (log_upper - log_lower))
                          for i in range(1, 80)], upper]
        if lower < 0.25 < upper and not any(math.isclose(point, 0.25, rel_tol=0, abs_tol=1e-12)
                                           for point in points):
            points.append(0.25)
        points = sorted(set(points))
        roots, brackets, previous = [], [], None
        for candidate in points:
            current = observe(candidate)
            if not current["valid"]:
                previous = None
                continue
            if abs(current["residual"]) <= RESIDUAL_TOLERANCE:
                roots.append(current)
                previous = None
                continue
            if previous is not None and previous["residual"] * current["residual"] < 0:
                brackets.append((previous, current))
            previous = current
        if len(roots) + len(brackets) > 1:
            return result("PLUSIEURS_SOLUTIONS_DETECTEES", root_count=len(roots), bracket_count=len(brackets))
        if roots:
            return success(roots[0])
        if not brackets:
            return result("AUCUN_ENCADREMENT")
        left, right = brackets[0]
        for _ in range(80):
            midpoint = (left["candidate"] + right["candidate"]) / 2
            if midpoint in (left["candidate"], right["candidate"]):
                return result("PRECISION_INSUFFISANTE")
            current = observe(midpoint)
            if not current["valid"]:
                return result("INTERVALLE_INVALIDE")
            if abs(current["residual"]) <= RESIDUAL_TOLERANCE:
                return success(current)
            if left["residual"] * current["residual"] < 0:
                right = current
            else:
                left = current
        return result("BUDGET_EPUISE")
    except Exhausted:
        return result("BUDGET_EPUISE")
    except Changed:
        return result("ENTREES_MODIFIEES")
