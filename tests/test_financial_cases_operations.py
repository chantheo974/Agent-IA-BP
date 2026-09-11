"""Recettes commerciales : événements indépendants, refus et aucune COM."""
import copy
import math
import os
from pathlib import Path
import unittest

from tools.financial_cases_common import common_updates, merge_updates
from tools.financial_cases_operations import cases, fifo_schedule, rejection_cases
from tools.validate_financial_cases import oracle_results


class OperationsOracleTests(unittest.TestCase):
    def test_fifo_uses_original_prices_and_conserves_orders(self):
        events = [{"month": 0, "quantity": 150, "price": 100},
                  {"month": 1, "quantity": 150, "price": 200}]
        before = copy.deepcopy(events)
        result = fifo_schedule(events, 100, 4)
        self.assertEqual([month["revenue"] for month in result], [10000, 15000, 20000, 0])
        self.assertEqual([month["backlog_quantity"] for month in result], [50, 100, 0, 0])
        self.assertEqual([month["backlog_value"] for month in result], [5000, 20000, 0, 0])
        self.assertEqual(sum(month["delivered"] for month in result), 300)
        self.assertEqual(sum(month["revenue"] for month in result), 45000)
        self.assertEqual(events, before)
        shipped_value = 0
        for month in result:
            ordered_value = sum(event["quantity"] * event["price"] for event in events if event["month"] <= month["month"])
            shipped_value += month["revenue"]
            self.assertEqual(ordered_value, shipped_value + month["backlog_value"])

    def test_fifo_rejects_nonphysical_input(self):
        for event in ({"month": -1, "quantity": 2, "price": 1},
                      {"month": 0, "quantity": -2, "price": 1},
                      {"month": 0, "quantity": 2, "price": math.nan},
                      {"month": False, "quantity": 2, "price": 1}):
            with self.subTest(event=event), self.assertRaises(ValueError):
                fifo_schedule([event], 100, 2)
        for capacity in (0, -1, False, math.inf):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                fifo_schedule([], capacity, 2)

    def test_fixtures_have_unique_entries_and_explicit_tax_convention(self):
        fixtures = cases()
        self.assertEqual(len(fixtures), 3)
        for case in fixtures:
            self.assertTrue(any("convention" in event.casefold() and "fiscale" in event.casefold() for event in case["events"]))
            positions = [(item["sheet"], item["cell"]) for item in case["updates"]]
            self.assertEqual(len(positions), len(set(positions)))
            ids = [item["id"] for item in case["oracles"]]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertGreater(len(ids), 20)
            self.assertTrue(all(math.isfinite(item["expected"]) for item in case["oracles"]))
            merged = merge_updates(common_updates(), case["updates"])
            current = {(item["sheet"], item["cell"]): item["value"] for item in merged}
            self.assertEqual(current["Assumptions", "C15"], 1)
            self.assertEqual(current["Assumptions", "C16"], 0)
            self.assertEqual(current["Assumptions", "D79"], 0)

    def test_false_pass_on_fifo_fae_and_ttc_is_rejected(self):
        fixtures = {case["id"]: case for case in cases()}
        wrong = [
            ("operations_fifo_two_prices", "Revenue", "Q36", 20000),
            ("operations_deposit_pca_fae", "Bilan", "D13", 0),
            ("operations_inventory_vat_bfr", "Bilan", "D14", 10000),
            ("operations_inventory_vat_bfr", "Bilan", "E18", 3600),
        ]
        for case_id, sheet, cell, incorrect in wrong:
            oracle = next(item for item in fixtures[case_id]["oracles"] if (item["sheet"], item["cell"]) == (sheet, cell))
            with self.subTest(case=case_id, cell=cell):
                self.assertFalse(oracle_results(lambda _s, _a: incorrect, [oracle])[0]["passed"])
                for missing in (None, "", "0", False, "#VALUE!", math.nan):
                    self.assertFalse(oracle_results(lambda _s, _a: missing, [oracle])[0]["passed"])

    def test_refusals_are_independent_copies_and_all_have_specific_reasons(self):
        before = cases()
        refusals = rejection_cases()
        self.assertEqual(len(refusals), 6)
        for case in refusals:
            self.assertEqual(case["expected_exception"], "ValueError")
            self.assertTrue(case["expected_error_any"])
            self.assertTrue(case["mutations"])
        self.assertEqual(cases(), before)


class OperationsPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tca_bp.model_engine import ModelEngine
        root = Path(__file__).resolve().parent.parent
        configured = os.environ.get("TCA_TEST_MODEL_DIR")
        model_dir = Path(configured).resolve() if configured else root / "models/generic-v1-confidentialite2"
        if not (model_dir / "modele.json").is_file():
            model_dir = root / "models/generic-v1"
        if not (model_dir / "modele.json").is_file():
            raise unittest.SkipTest("Modèle local absent ; aucune génération à partir de sources client.")
        cls.engine = ModelEngine(root, model_dir=model_dir)
        cls.template = cls.engine.template_path

    def _prepare(self, fixture):
        updates = [{**item, "reason": "Événements fictifs indépendants de recette commerciale",
                    "evidence": "SOURCE_FICTIVE_OPERATIONS_TEST", "replace_existing": True,
                    "override_default": True}
                   for item in merge_updates(common_updates(), fixture["updates"])]
        return self.engine.prepare(self.template, updates)

    def test_three_cases_are_accepted_by_actual_model_engine(self):
        for fixture in cases():
            with self.subTest(case=fixture["id"]):
                self.assertTrue(self._prepare(fixture)["valid"])

    def test_all_oracle_addresses_have_a_formula_or_material_value(self):
        workbook = self.engine._open(self.template)
        try:
            for fixture in cases():
                for oracle in fixture['oracles']:
                    sheet, cell = oracle['sheet'], oracle['cell']
                    with self.subTest(case=fixture['id'], sheet=sheet, cell=cell):
                        self.assertTrue(workbook.formula(sheet, cell) is not None
                                        or workbook.value(sheet, cell) is not None,
                                        'Oracle dirigé vers une cellule vide de la trame.')
        finally:
            workbook.close()

    def test_six_refusals_have_expected_cause_and_preserve_template(self):
        from tca_bp.storage import digest
        before = digest(self.template)
        for fixture in rejection_cases():
            with self.subTest(case=fixture["id"]):
                with self.assertRaises(ValueError) as refusal:
                    self._prepare(fixture)
                self.assertTrue(any(fragment in str(refusal.exception) for fragment in fixture["expected_error_any"]), str(refusal.exception))
        self.assertEqual(digest(self.template), before)


if __name__ == "__main__":
    unittest.main()
