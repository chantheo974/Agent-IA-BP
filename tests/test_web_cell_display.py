"""Number-format witnesses on small real OOXML packages, without Excel."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from xml.sax.saxutils import quoteattr
import zipfile

from tca_bp.vendor import input_engine as core
from tca_bp.web_cells import cell_display


class WebCellDisplayTests(unittest.TestCase):
    def render(self, value, *, format_id=0, custom=None, date1904=False):
        with tempfile.TemporaryDirectory(prefix="tca-display-") as directory:
            path = Path(directory) / "formats.xlsm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("xl/workbook.xml", f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><workbookPr date1904="{int(date1904)}"/><sheets><sheet name="Test" sheetId="1" r:id="rId1"/></sheets></workbook>')
                archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="worksheet"/></Relationships>')
                number_format = '' if custom is None else f'<numFmts count="1"><numFmt numFmtId="{format_id}" formatCode={quoteattr(custom)}/></numFmts>'
                archive.writestr("xl/styles.xml", f'<styleSheet xmlns="{core.NS}">{number_format}<fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0" numFmtId="{format_id}"/></cellXfs></styleSheet>')
                if value is None:
                    cell = '<c r="A1"/>'
                elif isinstance(value, bool):
                    cell = f'<c r="A1" t="b"><v>{int(value)}</v></c>'
                else:
                    cell = f'<c r="A1"><v>{value}</v></c>'
                archive.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{core.NS}"><sheetData><row r="1">{cell}</row></sheetData></worksheet>')
                archive.writestr("xl/vbaProject.bin", b"NONEXECUTABLE_DISPLAY_FIXTURE")
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            wb = core.Workbook(path)
            try:
                raw = wb.value("Test", "A1")
                result = cell_display(wb, "Test", "A1")
                self.assertEqual(wb.value("Test", "A1"), raw)
            finally:
                wb.close()
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            return result

    def test_grouping_requires_a_separator_in_the_number_format(self):
        for fmt, expected in [(1, "1234"), (2, "1234,25"), (3, "1\u202f234"), (4, "1\u202f234,25")]:
            with self.subTest(format=fmt):
                self.assertEqual(self.render(1234.25, format_id=fmt)["display"], expected)

    def test_percentage_currency_and_negative_parentheses_keep_their_units(self):
        self.assertEqual(self.render(12.345, format_id=10)["display"], "1234,50 %")
        self.assertEqual(self.render(-1234.5, format_id=39)["display"], "(1\u202f234,50)")
        self.assertEqual(self.render(1234.5, format_id=164, custom='0.00 "€"')["display"], "1234,50 €")
        self.assertEqual(self.render(1234.5, format_id=165, custom='#,##0.00 "€"')["display"], "1\u202f234,50 €")

    def test_builtin_minutes_seconds_wrap_hours(self):
        result = self.render((25 * 3600 + 2 * 60 + 3) / 86400, format_id=45)
        self.assertEqual(result, {"display": "02:03", "format": "mm:ss"})

    def test_elapsed_hours_remain_above_24_in_both_date_systems(self):
        for date1904 in (False, True):
            self.assertEqual(self.render((49 * 3600 + 2 * 60 + 3) / 86400, format_id=46, date1904=date1904)["display"], "49:02:03")
        self.assertEqual(self.render(3599.6 / 86400, format_id=46)["display"], "1:00:00")

    def test_builtin_compact_minutes_seconds_preserves_tenths(self):
        self.assertEqual(self.render(123.4 / 86400, format_id=47), {"display": "0203,4", "format": "mmss.0"})
        self.assertEqual(self.render(59.96 / 86400, format_id=47)["display"], "0100,0")

    def test_scientific_notation_exponent_sign_precision_and_rounding(self):
        for value, expected in [(12200000, "1,22E+07"), (0.0000122, "1,22E-05"), (-12200000, "-1,22E+07"), (9.999, "1,00E+01"), (0, "0,00E+00")]:
            with self.subTest(value=value):
                self.assertEqual(self.render(value, format_id=11)["display"], expected)

    def test_engineering_notation_uses_exponents_in_multiples_of_three(self):
        for value, expected in [(12200000, "12,2E+6"), (0.0122, "12,2E-3"), (0.000000122, "122,0E-9"), (-122000, "-122,0E+3"), (999.96, "1,0E+3"), (0, "0,0E+0")]:
            with self.subTest(value=value):
                self.assertEqual(self.render(value, format_id=48)["display"], expected)

    def test_custom_overrides_builtin_format_and_unsupported_time_stays_raw(self):
        self.assertEqual(self.render(1234.5, format_id=48, custom="0.00")["display"], "1234,50")
        self.assertEqual(self.render(-0.5, format_id=46)["display"], "-0.5")

    def test_blank_boolean_and_general_are_not_coerced(self):
        self.assertEqual(self.render(None, format_id=46)["display"], "")
        self.assertEqual(self.render(True, format_id=11)["display"], "VRAI")
        self.assertEqual(self.render(1234.56789)["display"], "1234.56789")


if __name__ == "__main__":
    unittest.main()
