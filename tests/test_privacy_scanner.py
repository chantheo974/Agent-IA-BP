import hashlib
import io
import unittest
from unittest.mock import patch
import zipfile

from tca_bp.privacy import private_fragment_found, audit_workbook_documentation, PRIVATE_TOKEN_HASHES
from tca_bp.model_build import _clean_text


def fingerprint(value):
    return hashlib.sha256(value.encode()).hexdigest()


class PrivacyScannerTests(unittest.TestCase):
    def test_punctuation_case_and_unicode_do_not_hide_a_known_private_word(self):
        hashes = {fingerprint('personnefictive')}
        for text in ('personnefictive', 'PERSONNEFICTIVE.', '(PersonneFictive),',
                     'Personne\u200bfictive', 'ＰＥＲＳＯＮＮＥＦＩＣＴＩＶＥ.'):
            with self.subTest(text=text):
                self.assertTrue(private_fragment_found(text, hashes))
        self.assertFalse(private_fragment_found('personnefictive_suffixe', hashes))

    def test_punctuated_initial_is_still_detected(self):
        self.assertTrue(private_fragment_found('Note de P. Fictive', {fingerprint('p. fictive')}))
        self.assertTrue(private_fragment_found('Note de personne fictive.', {fingerprint('personne fictive')}))

    def test_cleaner_replaces_the_whole_private_narrative(self):
        with patch('tca_bp.model_build.REDACTED_TOKEN_HASHES', {fingerprint('personnefictive')}):
            self.assertEqual(_clean_text('Ancienne validation par PERSONNEFICTIVE.', {}),
                             'À documenter et valider pour le dossier courant.')

    def test_scanner_covers_hidden_cells_formula_strings_shapes_and_attributes_without_echoing_text(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('xl/worksheets/sheet1.xml', '<worksheet><row hidden="1"><c><is><t>PERSONNEFICTIVE.</t></is></c></row><f>IF(A1,"PersonneFictive",0)</f></worksheet>')
            archive.writestr('xl/drawings/drawing1.xml', '<shape descr="personnefictive"/>')
            archive.writestr('docProps/custom.xml', '<property>personnefictive</property>')
        with patch('tca_bp.privacy.PRIVATE_TOKEN_HASHES', {fingerprint('personnefictive')}):
            report = audit_workbook_documentation(stream)
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(report['xml_parts_checked'], 3)
        self.assertEqual(len(report['hits']), 4)
        self.assertNotIn('personnefictive', str(report).casefold())

    def test_production_fingerprints_are_complete_sha256_values(self):
        self.assertEqual(len(PRIVATE_TOKEN_HASHES), 6)
        self.assertTrue(all(len(value) == 64 for value in PRIVATE_TOKEN_HASHES))
