import unittest
from xml.etree import ElementTree as ET
from tca_bp.model_qualification_guards import guard_formula, remove_inherited_protection_credentials


class QualificationGuardTests(unittest.TestCase):
    def test_reference_drift_cannot_be_repaired_silently(self):
        for sheet, cell, original in [
            ('ATELIER_CIR_IS', 'C67', 'TRUE'),
            ('ATELIER_CIR_IS', 'D86', '0'),
            ('ATELIER_CIR_IS', 'M68', '"texte différent"'),
            ('Valorisation', 'D138', '"OK"'),
        ]:
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                guard_formula(sheet, cell, original)

    def test_unrelated_formula_is_preserved(self):
        formula = 'SUM(D20:D25)'
        self.assertEqual(guard_formula('Valorisation', 'D26', formula), formula)
        self.assertEqual(guard_formula('Other', 'C67', formula), formula)

    def test_credentials_removed_without_changing_protection_flags_or_other_text(self):
        raw = (b'<worksheet><sheetProtection password="fictional" algorithmName="SHA-512" '
               b'hashValue="fictionalhash" saltValue="fictionalsalt" spinCount="100000" '
               b'sheet="1" objects="1" scenarios="1" autoFilter="0"/>'
               b'<c r="A1"><is><t>password="ordinary text"</t></is></c></worksheet>')
        updated = remove_inherited_protection_credentials(raw)
        root = ET.fromstring(updated)
        self.assertEqual(root.find('sheetProtection').attrib,
                         {'sheet': '1', 'objects': '1', 'scenarios': '1', 'autoFilter': '0'})
        self.assertIn(b'password="ordinary text"', updated)
        for secret in (b'fictionalhash', b'fictionalsalt', b'password="fictional"'):
            self.assertNotIn(secret, updated)

    def test_workbook_credentials_removed_without_unlocking_structure(self):
        raw = b'<workbookProtection workbookPassword="test" revisionsPassword="test" lockStructure="1"/>'
        self.assertEqual(ET.fromstring(remove_inherited_protection_credentials(raw)).attrib, {'lockStructure': '1'})

    def test_range_credentials_acl_and_file_reservation_are_removed(self):
        raw=(b'<workbook xmlns:x="urn:fixture"><x:fileSharing readOnlyRecommended="1" '
             b'userName="Fictitious Person" reservationPassword="ABCD" algorithmName="SHA-512" '
             b'hashValue="fakehash" saltValue="fakesalt" spinCount="100000"/>'
             b'<protectedRanges><protectedRange name="Editable" sqref="A1:B8" '
             b'password="ABCD" securityDescriptor="fictional-acl" algorithmName="SHA-512" '
             b'hashValue="fakehash" saltValue="fakesalt" spinCount="100000"/></protectedRanges>'
             b'<definedName name="userName">"ordinary text"</definedName></workbook>')
        changed=remove_inherited_protection_credentials(raw);root=ET.fromstring(changed)
        self.assertEqual(root.find('{urn:fixture}fileSharing').attrib,{'readOnlyRecommended':'1'})
        self.assertEqual(root.find('protectedRanges/protectedRange').attrib,{'name':'Editable','sqref':'A1:B8'})
        self.assertEqual(root.find('definedName').attrib,{'name':'userName'})
        self.assertNotIn(b'Fictitious Person',changed)
        self.assertNotIn(b'fictional-acl',changed)

    def test_single_quoted_prefixed_credentials_are_removed_without_ranges_loss(self):
        raw=b"<x:protectedRange xmlns:x='urn:fixture' name='Range' sqref='C3:C9' password = 'ABCD' x:hashValue='hashed'/>"
        changed=remove_inherited_protection_credentials(raw)
        self.assertEqual(ET.fromstring(changed).attrib,{'name':'Range','sqref':'C3:C9'})


if __name__ == '__main__':
    unittest.main()
