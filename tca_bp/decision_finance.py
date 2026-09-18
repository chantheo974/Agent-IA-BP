"""Pure decision calculations; no workbook access or implicit application.

Ratios are fractions (0.10 means 10%). Shares may be fractional: this is a
fully diluted economic simulation, not a legal issuance/rounding instruction.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import Callable


def _decimal(value, name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name}: nombre fini requis")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name}: nombre décimal invalide") from None
    if not result.is_finite():
        raise ValueError(f"{name}: nombre fini requis")
    return result


def _text(value: Decimal) -> str:
    return format(value, "f")


def calculate_cap_table(shareholders: list[dict], rounds: list[dict], *,
                        initial_pool_shares=0) -> dict:
    """Simulate ordinary equity rounds with a target post-round FD option pool.

``before`` (default): pool top-up enters the pre-money share denominator;
``after``: top-up follows investment and dilutes investors as well. Existing
pool shares are never cancelled to meet a smaller target. An omitted target
means no top-up. Pool shares are reserved unallocated shares, not a person.
All monetary inputs use the same caller-chosen currency. No preferences,
convertibles, vesting, taxes, fees, or securities-law rules are inferred.
"""
    if not isinstance(shareholders, list) or not shareholders or len(shareholders) > 500:
        raise ValueError("1 à 500 actionnaires requis")
    if not isinstance(rounds, list) or len(rounds) > 100:
        raise ValueError("100 tours au maximum")
    with localcontext() as ctx:
        ctx.prec = 50
        owners: dict[str, Decimal] = {}
        for item in shareholders:
            name = str(item.get("name", "")).strip()
            shares = _decimal(item.get("shares"), "shares")
            if not name or len(name) > 200 or name in owners or shares < 0:
                raise ValueError("Noms uniques non vides et parts positives ou nulles requis")
            owners[name] = shares
        pool = _decimal(initial_pool_shares, "initial_pool_shares")
        if pool < 0 or sum(owners.values()) <= 0:
            raise ValueError("Capital détenu strictement positif et pool positif ou nul requis")

        def table():
            total = sum(owners.values()) + pool
            holders = [{"name": name, "shares": _text(shares),
                        "ownership": _text(shares / total), "percent": _text(100 * shares / total)}
                       for name, shares in owners.items()]
            return {"shareholders": holders, "holders": holders,
                    "pool_shares": _text(pool), "pool_ownership": _text(pool / total),
                    "fully_diluted_shares": _text(total)}

        initial = table()
        results = []
        for item in rounds:
            name = str(item.get("name", "")).strip()
            if not name or len(name) > 200 or name in owners:
                raise ValueError("Chaque tour doit porter un nom distinct des détenteurs et tours précédents")
            pre = _decimal(item.get("pre_money"), "pre_money")
            amount = _decimal(item.get("investment"), "investment")
            timing = item.get("pool_timing", "before")
            p = None if item.get("pool_percent") is None else _decimal(item["pool_percent"], "pool_percent")
            if pre <= 0 or amount < 0 or timing not in {"before", "after"}:
                raise ValueError("Pré-money > 0, investissement >= 0 et pool_timing before/after requis")
            if p is not None and not Decimal(0) <= p < Decimal(1):
                raise ValueError("pool_percent est une fraction comprise entre 0 inclus et 1 exclu")
            before = table()
            old_pool = pool
            ratio = amount / pre
            if timing == "before" and p is not None:
                denominator = 1 - p * (1 + ratio)
                if denominator <= 0:
                    raise ValueError("Pool pré-tour impossible pour ce rapport investissement/pré-money")
                required = p * (1 + ratio) * sum(owners.values()) / denominator
                pool = max(pool, required)
            price = pre / (sum(owners.values()) + pool)
            new_shares = amount / price
            owners[name] = new_shares
            if timing == "after" and p is not None:
                required = p * sum(owners.values()) / (1 - p)
                pool = max(pool, required)
            after = table()
            warnings = []
            if p is not None and Decimal(after["pool_ownership"]) > p + Decimal("1e-40"):
                warnings.append("POOL_EXISTANT_SUPERIEUR_A_LA_CIBLE_AUCUNE_ANNULATION")
            results.append({"name": name, "pre_money": _text(pre), "investment": _text(amount),
                "post_money": _text(pre + amount), "pool_timing": timing,
                "pool_target": None if p is None else _text(p), "price_per_share": _text(price),
                "issued_investor_shares": _text(new_shares), "pool_top_up": _text(pool - old_pool),
                "before": before, "after": after, "warnings": warnings})
        final = table()
        return {"schema_version": "tca-capital/1", "status": "SIMULATION", "initial": initial,
                "rounds": results, "final": final, "holders": final["holders"], "conventions": {
                    "pool_target": "fraction du capital pleinement dilué après le tour",
                    "default_pool_timing": "before", "fractional_shares": True,
                    "currency": "identique pour tous les montants fournis",
                    "excluded": ["préférences", "convertibles", "vesting", "frais", "fiscalité", "arrondi juridique"]}}


def solve_single_lever(evaluator: Callable, target, lower, upper, *,
                       tolerance="0.01", lever_tolerance="0.000001",
                       max_evaluations: int = 40, integer_lever: bool = False) -> dict:
    """Bounded bracket/bisection on one lever, never applies the chosen input.

The caller owns isolated Excel evaluations and timeouts. A callable receives
a Decimal and returns a number or ``{value, ...proof metadata}``. Only observed
monotonicity is checked; no proof of global monotonicity or financial validity
is claimed. The final candidate is always one actually evaluated.
"""
    target, lo, hi = (_decimal(v, n) for v, n in [(target, "target"), (lower, "lower"), (upper, "upper")])
    tol, xtol = _decimal(tolerance, "tolerance"), _decimal(lever_tolerance, "lever_tolerance")
    if lo >= hi or tol <= 0 or xtol <= 0:
        raise ValueError("Bornes ordonnées et tolérances strictement positives requises")
    if isinstance(max_evaluations, bool) or not isinstance(max_evaluations, int) or not 2 <= max_evaluations <= 200:
        raise ValueError("Budget de 2 à 200 évaluations requis")
    if type(integer_lever) is not bool:
        raise ValueError('Le caractère entier du levier doit être explicite.')
    if integer_lever and any(x!=x.to_integral_value() for x in (lo,hi)):
        raise ValueError('Ce levier exige des bornes entières.')
    history: list[dict] = []

    def evaluate(x):
        raw = evaluator(x)
        proof = raw if isinstance(raw, dict) else {}
        y = _decimal(proof.get("value") if proof else raw, "évaluation")
        history.append({"lever": _text(x), "value": _text(y), "residual": _text(y - target),
                        "proof": {k: v for k, v in proof.items() if k != "value"}})
        return y

    def result(status):
        best = min(history, key=lambda item: abs(Decimal(item["residual"])))
        return {"schema_version": "tca-goal/1", "status": status,
                "candidate": best, "target": _text(target), "bounds": [_text(lower_d), _text(upper_d)],
                "evaluations": len(history), "max_evaluations": max_evaluations,
                "history": history, "applied": False, "integer_lever":integer_lever, "monotonicity": "OBSERVATIONS_SEULEMENT"}

    lower_d, upper_d = lo, hi
    with localcontext() as ctx:
        ctx.prec = 50
        a, b = evaluate(lo), evaluate(hi)
        if min(abs(a - target), abs(b - target)) <= tol:
            return result("CONVERGED")
        if (a - target) * (b - target) >= 0:
            return result("UNBRACKETED")
        increasing = b > a
        while len(history) < max_evaluations:
            if integer_lever and hi-lo<=1:
                return result('DISCRETE_TARGET_UNREACHABLE')
            middle = (lo + hi) / 2
            if integer_lever:
                from decimal import ROUND_FLOOR
                middle=middle.to_integral_value(rounding=ROUND_FLOOR)
            value = evaluate(middle)
            if value < min(a, b) - tol or value > max(a, b) + tol:
                return result("NON_MONOTONIC")
            if abs(value - target) <= tol:
                return result("CONVERGED")
            if hi - lo <= xtol:
                return result("LEVER_TOLERANCE_REACHED")
            if (value < target) == increasing:
                lo, a = middle, value
            else:
                hi, b = middle, value
        return result("BUDGET_EXHAUSTED")
