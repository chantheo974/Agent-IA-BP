import math
import unittest
from tca_bp.wacc_solver import solve, MAX_EVALUATIONS


def observation(candidate, calculated, equity=1000000, fingerprint="immutable-fixture", validity="OK"):
    return dict(calculated=calculated, equity=equity, fingerprint=fingerprint, validity=validity)


class WaccSolverTests(unittest.TestCase):
    def test_unlevered_business_matches_independent_cost_of_equity(self):
        # Événement fictif : rf3%, bêta1.2, ERP5%, prime3%, dette0.
        expected = 0.03 + 1.2 * 0.05 + 0.03
        result = solve(lambda w: observation(w, expected), growth=0.02)
        self.assertTrue(result["converged"])
        self.assertAlmostEqual(result["candidate"], expected, places=9)
        self.assertLessEqual(result["evaluations"], MAX_EVALUATIONS)
        self.assertFalse(result["global_uniqueness_proven"])

    def test_multiple_crossings_refused(self):
        result = solve(lambda w: observation(w, w + (w - 0.2) * (w - 0.8)), growth=0)
        self.assertEqual(result["status"], "PLUSIEURS_SOLUTIONS_DETECTEES")

    def test_no_bracket_does_not_calibrate(self):
        result = solve(lambda w: observation(w, w + 0.1), growth=0)
        self.assertEqual(result["status"], "AUCUN_ENCADREMENT")
        self.assertNotIn("candidate", result)

    def test_invalid_equity_errors_and_missing_qualifications_never_succeed(self):
        for equity in (0, -1, math.nan, None, True):
            with self.subTest(equity=equity):
                self.assertFalse(solve(lambda w: observation(w, 0.12, equity), growth=0.02)["converged"])
        for calculated in ("#N/A", None, math.inf, False):
            with self.subTest(calculated=calculated):
                self.assertFalse(solve(lambda w: observation(w, calculated), growth=0.02)["converged"])
        self.assertFalse(solve(lambda w: observation(w, 0.12, validity="A_COMPLETER"), growth=0.02)["converged"])

    def test_changed_source_and_time_budget_fail_closed(self):
        calls = []
        def changed(w):
            calls.append(w)
            return observation(w, 0.12, fingerprint="first" if len(calls) == 1 else "changed")
        self.assertEqual(solve(changed, growth=0.02)["status"], "ENTREES_MODIFIEES")
        ticks = iter([0, 0, 999])
        result = solve(lambda w: observation(w, 0.12), growth=0.02, timeout=1, clock=lambda: next(ticks))
        self.assertEqual(result["status"], "BUDGET_EPUISE")

    def test_invalid_observations_cannot_bridge_a_discontinuity(self):
        result = solve(lambda w: observation(w, w + (-0.1 if w < 0.2 else 0.1),
                                             validity="INVALID" if 0.19 < w < 0.3 else "OK"), growth=0)
        self.assertEqual(result["status"], "AUCUN_ENCADREMENT")

    def test_input_bounds_and_missing_fingerprint(self):
        for growth in (None, -1, 5, math.nan, True):
            with self.subTest(growth=growth), self.assertRaises(ValueError):
                solve(lambda _: {}, growth=growth)
        with self.assertRaisesRegex(ValueError, "Empreinte"):
            solve(lambda w: observation(w, 0.12, fingerprint=""), growth=0.02)

    def test_single_root_on_exact_boundary_is_not_counted_twice(self):
        for growth in (0, 0.1, 0.3, -0.5):
            target = growth + 2e-6
            with self.subTest(growth=growth):
                result = solve(lambda w: observation(w, target), growth=growth)
                self.assertEqual(result["status"], "CONVERGENCE_LOCALE")
                self.assertEqual(result["candidate"], target)
                self.assertTrue(all(result["domain"][0] <= item["candidate"] <= result["domain"][1]
                                    for item in result["observations"]))
                # Une observation au balayage et une confirmation finale.
                roots = [item for item in result["observations"] if item["valid"] and abs(item["residual"]) <= 1e-10]
                self.assertEqual(len(roots), 2)

    def test_seed_near_mesh_point_is_not_a_second_root(self):
        # Choisir g pour que le dixième point du maillage soit25 %, à l'arrondi
        # flottant près. L'amorce supplémentaire ne crée pas une seconde racine.
        lower = math.expm1((math.log1p(0.25) - 10 / 80 * math.log(6)) / (1 - 10 / 80))
        result = solve(lambda w: observation(w, 0.25), growth=lower - 2e-6)
        self.assertEqual(result["status"], "CONVERGENCE_LOCALE")
        self.assertAlmostEqual(result["candidate"], 0.25, places=12)

    def test_last_evaluation_cannot_succeed_after_deadline(self):
        baseline = solve(lambda w: observation(w, 0.12), growth=0.02)
        last_call = baseline["evaluations"]
        elapsed, calls = [0], [0]

        def slow_final(w):
            calls[0] += 1
            if calls[0] == last_call:
                elapsed[0] = 2
            return observation(w, 0.12)

        result = solve(slow_final, growth=0.02, timeout=1, clock=lambda: elapsed[0])
        self.assertEqual(result["status"], "BUDGET_EPUISE")
        self.assertFalse(result["converged"])
        self.assertEqual(result["evaluations"], last_call)
        self.assertNotIn("candidate", result)


if __name__ == "__main__":
    unittest.main()
