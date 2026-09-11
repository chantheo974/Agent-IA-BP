import unittest
from tca_bp.vendor import input_engine as core


class InactiveOfferTests(unittest.TestCase):
    def test_disabling_an_offer_does_not_invent_billing_percentages(self):
        class Workbook:
            def value(self, sheet, cell):
                return 3 if (sheet, cell) == ("Control", "C59") else None
        schema = {"cells": {"Assumptions": {"C15": {}}}, "business_rules": [
            {"type": "sum_100", "sheet": "Assumptions", "rows": [15], "cols": ["V", "X", "Z"]}]}
        change = {"sheet": "Assumptions", "cell": "C15", "value": 0, "kind": "number"}
        core.business_checks(Workbook(), schema, [change])
        for active in (1, None):
            with self.subTest(active=active), self.assertRaisesRegex(ValueError, "pourcentages"):
                core.business_checks(Workbook(), schema, [{**change, "value": active}])


if __name__ == "__main__":
    unittest.main()
