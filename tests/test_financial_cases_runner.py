import math
import unittest

from tools.financial_cases_common import common_updates, merge_updates
from tools.validate_financial_cases import oracle_results


class FinancialRunnerTests(unittest.TestCase):
    def test_explicit_boolean_or_error_oracle_cannot_be_replaced_by_numeric_zero(self):
        cases = [{'id': 'boolean', 'sheet': 'Fiscal', 'cell': 'A1', 'expected': False, 'expected_kind': 'boolean'},
                 {'id': 'missing', 'sheet': 'Fiscal', 'cell': 'A2', 'expected': '#N/A', 'expected_kind': 'excel_error'}]
        self.assertTrue(all(not item['passed'] for item in oracle_results(lambda *_: 0, cases)))
        values = {'A1': False, 'A2': '#N/A'}
        self.assertTrue(all(item['passed'] for item in oracle_results(lambda _, cell: values[cell], cases)))

    def test_no_error_empty_boolean_or_nonfinite_can_be_financial_zero(self):
        oracle = [{"id": "cash", "sheet": "Flux", "cell": "C1", "expected": 0}]
        for value in (None, False, True, "0", "#N/A", math.nan, math.inf):
            with self.subTest(value=value):
                result = oracle_results(lambda *_: value, oracle)
                self.assertFalse(result[0]["passed"])
        self.assertTrue(oracle_results(lambda *_: 0, oracle)[0]["passed"])

    def test_all_failures_recorded_without_changing_expected_values(self):
        expected = [{"id": "one", "sheet": "Flux", "cell": "A1", "expected": 100},
                    {"id": "two", "sheet": "Flux", "cell": "A2", "expected": 200}]
        result = oracle_results(lambda *_: -1, expected)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(not r["passed"] for r in result))
        self.assertEqual([r["expected"] for r in result], [100, 200])

    def test_empty_and_duplicate_oracles_cannot_produce_success(self):
        with self.assertRaises(ValueError):
            oracle_results(lambda *_: 0, [])
        item = {"id": "same", "sheet": "Flux", "cell": "A1", "expected": 0}
        with self.assertRaises(ValueError):
            oracle_results(lambda *_: 0, [item, item])

    def test_event_can_override_frame_but_fixture_duplicates_fail(self):
        event = {"sheet": "Assumptions", "cell": "D126", "value": 1000}
        result = merge_updates(common_updates(), [event])
        self.assertEqual([item["value"] for item in result if (item["sheet"], item["cell"]) ==
                          ("Assumptions", "D126")], [1000])
        with self.assertRaises(ValueError):
            merge_updates([event, event])


if __name__ == "__main__":
    unittest.main()
