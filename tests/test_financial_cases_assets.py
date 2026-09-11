"""Oracles indépendants et échec fermé des recettes actifs/aides ; aucun COM."""
import copy
import math
from pathlib import Path
import unittest

from tools.financial_cases_assets import assert_oracles, cases, lease_payment, rejection_cases


class AssetsOracleTests(unittest.TestCase):
    def test_contract_has_unique_cells_finite_oracles_and_business_events(self):
        fixtures = cases()
        self.assertEqual(len(fixtures), 7)
        self.assertEqual(len({case["id"] for case in fixtures}), len(fixtures))
        for case in fixtures:
            self.assertGreaterEqual(len(case["events"]), 3)
            coordinates = [(v["sheet"], v["cell"]) for v in case["updates"]]
            self.assertEqual(len(coordinates), len(set(coordinates)), case["id"])
            ids = [oracle["id"] for oracle in case["oracles"]]
            self.assertEqual(len(ids), len(set(ids)), case["id"])
            self.assertGreater(len(ids), 5)
            for oracle in case["oracles"]:
                self.assertTrue(math.isfinite(oracle["expected"]))
                self.assertTrue(oracle["reason"])

    def test_missing_errors_boolean_nonfinite_are_never_zero(self):
        oracle = {"id": "zero", "sheet": "Fictif", "cell": "A1", "expected": 0, "tolerance": 0.01}
        for value in (None, "", "0", False, True, "#VALUE!", "#N/A", float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                assert_oracles(lambda _s, _a: value, [oracle])
        self.assertTrue(assert_oracles(lambda _s, _a: 0, [oracle])[0]["passed"])
        with self.assertRaises(ValueError):
            assert_oracles(lambda _s, _a: 0, [])
        for key, invalid in (("tolerance", -1), ("expected", float("nan")), ("expected", True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                assert_oracles(lambda _s, _a: 0, [{**oracle, key: invalid}])

    def test_incorrect_double_rate_and_missing_last_rent_fail(self):
        by_id = {case["id"]: case for case in cases()}
        grant = next(v for v in by_id["assets_grants_awarded_vs_base"]["oracles"] if v["cell"] == "N3")
        with self.assertRaises(AssertionError):
            assert_oracles(lambda _s, _a: 120000 * 0.4, [grant])
        lease = next(v for v in by_id["assets_lease_one_month_horizon"]["oracles"] if v["cell"] == "R81")
        with self.assertRaises(AssertionError):
            assert_oracles(lambda _s, _a: 0, [lease])

    def test_lease_interest_oracle_retires_balance_and_conserves_cash(self):
        payment = lease_payment(12000, 0.12, 12)
        self.assertAlmostEqual(payment, 1066.18546414010, places=8)
        balance, interest = 12000, 0
        for _ in range(12):
            accrued = balance * 0.01
            interest += accrued
            balance += accrued - payment
        self.assertAlmostEqual(balance, 0, places=7)
        self.assertAlmostEqual(12 * payment, 12000 + interest, places=7)
        self.assertAlmostEqual(lease_payment(12000, 0, 2), 6000, places=8)
        self.assertAlmostEqual(lease_payment(900, 0, 1), 900, places=8)
        for args in ((0, 0, 1), (1, -0.1, 1), (1, 0, 1.2), (1, 0, True), (math.inf, 0, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                lease_payment(*args)

    def test_rejections_do_not_mutate_successful_fixtures(self):
        before = cases()
        refusals = rejection_cases()
        self.assertEqual(len(refusals), 8)
        self.assertEqual(before, cases())
        for refusal in refusals:
            self.assertEqual(refusal["expected_exception"], "ValueError")
            mutation = refusal["mutation"]
            self.assertIn(mutation, refusal["updates"])
        changed = copy.deepcopy(before)
        changed[0]["updates"][0]["value"] = "Modification locale au test"
        self.assertNotEqual(changed, cases())


class AssetsPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tca_bp.model_engine import ModelEngine
        root = Path(__file__).resolve().parent.parent
        if not (root / "models/generic-v1/modele.json").is_file():
            raise unittest.SkipTest("Modèle local absent : aucune génération à partir de sources client.")
        cls.engine = ModelEngine(root)
        cls.template = cls.engine.template_path
        # Préparation seulement : ces valeurs ne prétendent pas constituer une
        # qualification fiscale ni une base de résultat financier recalculé.
        cls.frame = [{"sheet": "Control", "cell": "C10", "value": "2026-01-01"},
                     {"sheet": "Control", "cell": "C59", "value": 3}]

    def _prepare(self, fixture):
        updates = [{**value, "reason": "Événement fictif indépendant de recette actifs/aides",
                    "evidence": "SOURCE_FICTIVE_TEST_ASSETS", "override_default": True,
                    "replace_existing": True} for value in self.frame + fixture["updates"]]
        return self.engine.prepare(self.template, updates)

    def test_each_valid_case_is_authorized_by_real_model_engine(self):
        for case in cases():
            with self.subTest(case=case["id"]):
                self.assertTrue(self._prepare(case)["valid"])

    def test_invalid_cases_are_refused_without_writing_source(self):
        from tca_bp.storage import digest
        before = digest(self.template)
        for case in rejection_cases():
            with self.subTest(case=case["id"]):
                with self.assertRaises(ValueError) as failure:
                    self._prepare(case)
                self.assertTrue(any(fragment in str(failure.exception)
                                    for fragment in case["expected_error_any"]), str(failure.exception))
        self.assertEqual(digest(self.template), before)


if __name__ == "__main__":
    unittest.main()
