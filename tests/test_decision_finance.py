import unittest
from decimal import Decimal as D
from tca_bp.decision_finance import calculate_cap_table, solve_single_lever


class CapitalTests(unittest.TestCase):
    def test_no_pool_independent_economic_oracle(self):
        result = calculate_cap_table([{"name": "Fondateur", "shares": 1000}],
                                     [{"name": "A", "pre_money": 4000000, "investment": 1000000}])
        self.assertEqual(D(result["holders"][0]["percent"]), 80)
        self.assertEqual(D(result["holders"][1]["shares"]), 250)
        self.assertEqual(D(result["rounds"][0]["price_per_share"]), 4000)

    def test_pre_pool_targets_post_round_and_spares_investor(self):
        result = calculate_cap_table([{"name": "F", "shares": 1000}],
                                     [{"name": "A", "pre_money": 4, "investment": 1, "pool_percent": ".1"}])
        holders = result["final"]["holders"]
        self.assertAlmostEqual(D(holders[0]["ownership"]), D(".7"), places=40)
        self.assertAlmostEqual(D(holders[1]["ownership"]), D(".2"), places=40)
        self.assertAlmostEqual(D(result["final"]["pool_ownership"]), D(".1"), places=40)

    def test_after_pool_dilutes_investor(self):
        result = calculate_cap_table([{"name": "F", "shares": 1000}],
            [{"name": "A", "pre_money": 4, "investment": 1, "pool_percent": ".1", "pool_timing": "after"}])
        self.assertAlmostEqual(D(result["holders"][0]["ownership"]), D(".72"), places=40)
        self.assertAlmostEqual(D(result["holders"][1]["ownership"]), D(".18"), places=40)

    def test_multiple_rounds_and_existing_pool_no_cancellation(self):
        result = calculate_cap_table([{"name": "F", "shares": 900}],
            [{"name": "A", "pre_money": 9, "investment": 1},
             {"name": "B", "pre_money": 10, "investment": 10, "pool_percent": 0}], initial_pool_shares=100)
        self.assertEqual(D(result["final"]["pool_shares"]), 100)
        self.assertEqual(D(result["holders"][2]["ownership"]), D(".5"))
        self.assertIn("POOL_EXISTANT", result["rounds"][1]["warnings"][0])
        self.assertAlmostEqual(sum(D(h["ownership"]) for h in result["holders"]) + D(result["final"]["pool_ownership"]), D(1), places=27)

    def test_invalid_ratios_numbers_and_names(self):
        for patch in ({"pool_percent": 10}, {"pool_percent": ".9"}, {"pre_money": 0},
                      {"investment": -1}, {"investment": "NaN"}, {"pool_timing": "unknown"}, {"name": "F"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                calculate_cap_table([{"name": "F", "shares": 100}],
                    [{"name": "A", "pre_money": 4, "investment": 1, **patch}])


class GoalTests(unittest.TestCase):
    def test_linear_oracle_and_exact_budget(self):
        seen = []
        def evaluate(x):
            seen.append(x)
            return {"value": 3*x + 5, "source_sha256": "fixture"}
        result = solve_single_lever(evaluate, 20, 0, 10, tolerance=".000001")
        self.assertEqual(result["status"], "CONVERGED")
        self.assertEqual(D(result["candidate"]["lever"]), 5)
        self.assertEqual(result["evaluations"], len(seen))
        self.assertFalse(result["applied"])
        self.assertEqual(result["candidate"]["proof"]["source_sha256"], "fixture")

    def test_decreasing_function_and_float(self):
        result = solve_single_lever(lambda x: float(100 - x * x), 75, 0, 10)
        self.assertEqual(result["status"], "CONVERGED")
        self.assertEqual(D(result["candidate"]["lever"]), 5)

    def test_unreachable_budget_and_nonmonotonic(self):
        result = solve_single_lever(lambda x: x, 99, 0, 10)
        self.assertEqual(result["status"], "UNBRACKETED")
        self.assertEqual(result["evaluations"], 2)
        result = solve_single_lever(lambda x: x*x, 2, 0, 2, max_evaluations=3, tolerance="1e-12")
        self.assertEqual(result["status"], "BUDGET_EXHAUSTED")
        self.assertEqual(result["evaluations"], 3)
        result = solve_single_lever(lambda x: 100 if x == 5 else x, 3, 0, 10)
        self.assertEqual(result["status"], "NON_MONOTONIC")

    def test_nonfinite_evaluator_and_bad_limits_refused(self):
        with self.assertRaises(ValueError):
            solve_single_lever(lambda x: float("nan"), 1, 0, 2)
        with self.assertRaises(ValueError):
            solve_single_lever(lambda x: x, 1, 0, 2, max_evaluations=201)

    def test_integer_lever_never_evaluates_fractional_staff_or_units(self):
        seen=[]
        def evaluate(x):
            self.assertEqual(x,x.to_integral_value())
            seen.append(x)
            return 200*x-1000
        result=solve_single_lever(evaluate,-400,0,5,integer_lever=True)
        self.assertEqual(result['status'],'CONVERGED')
        self.assertEqual(D(result['candidate']['lever']),3)
        self.assertEqual(len(seen),len(set(seen)))
        self.assertFalse(result['applied'])
        result=solve_single_lever(lambda x:-2*x,-5,-4,5,integer_lever=True)
        self.assertEqual(result['status'],'DISCRETE_TARGET_UNREACHABLE')
        self.assertEqual(abs(D(result['candidate']['residual'])),1)
        self.assertTrue(all(D(p['lever'])==D(p['lever']).to_integral_value() for p in result['history']))
        with self.assertRaisesRegex(ValueError,'bornes entières'):
            solve_single_lever(lambda x:self.fail('Pas de calcul avec bornes fractionnaires'),4,1.5,7,integer_lever=True)


if __name__ == "__main__":
    unittest.main()
