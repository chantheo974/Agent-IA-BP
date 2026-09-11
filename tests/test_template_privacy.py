"""Garde-fous de distribution et de neutralisation de la référence locale.

Les tests du classeur sont ignorés quand les artefacts locaux sont absents. Aucun
test n'expose les valeurs privées qu'il recherche ou ne reconstruit la référence.
"""

import hashlib
import json
from pathlib import Path
import re
import unittest
import zipfile
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "generic-v1"
TEMPLATE = MODEL / "TCA_BP_Trame_generique.xlsm"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
PRIVATE_FRAGMENTS = frozenset({
    "10b05c446ea776cdcae1ab10f5dcdbad5eeb9250a8b6f62752e6d4e755850fab",
    "197316ef3e74b4f9c280bf7eee7184eaace168365e12f1face6a31a08e2f23f9",
    "13c24edf86a2446c258e7d2ec06d3ed95dc059c619d6be334b2f5674b2b650cc",
    "d066f8c757b4cba13d3c8a21a2fb369d927df06c52b93624e872075da6de37d4",
    "37f6cfd2f17342f54c13ebe070b4b31abcd77927824bcf672dbdb48790a53ef6",
    "10e7cb810d59691ee0357576994c977731198ef9d6567407fd545f9624f5ac06",
})


def private_fragment_found(text):
    tokens = re.findall(r"\w+\.?", text.casefold()) + re.findall(r"\w+", text.casefold())
    return any(hashlib.sha256(token.encode()).hexdigest() in PRIVATE_FRAGMENTS
               for token in tokens + [" ".join(tokens[i:i+2]) for i in range(len(tokens)-1)])


class PublicCodePrivacyTests(unittest.TestCase):
    def test_published_code_and_docs_exclude_private_name_fragments(self):
        hits = []
        for folder in ("tca_bp", "docs", "agents", "tools"):
            for path in (ROOT / folder).rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".md", ".json"} or "__pycache__" in path.parts:
                    continue
                if private_fragment_found(path.read_text(encoding="utf-8")):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [], "Fragments de rédaction privée présents ; chemins seuls : " + repr(hits))


@unittest.skipUnless(TEMPLATE.is_file(), "Trame locale non distribuée avec le code")
class LocalTemplatePrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.z = zipfile.ZipFile(TEMPLATE)
        cls.parts = cls.z.namelist()
        cls.workbook = ET.fromstring(cls.z.read("xl/workbook.xml"))
        rels = {r.get("Id"): r.get("Target").lstrip("/") for r in ET.fromstring(cls.z.read("xl/_rels/workbook.xml.rels"))}
        cls.sheet_parts = {}
        for sheet in cls.workbook.find("m:sheets", NS):
            part = rels[sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
            cls.sheet_parts[sheet.get("name")] = part if part.startswith("xl/") else "xl/" + part
        cls.cells = {}

    @classmethod
    def tearDownClass(cls):
        cls.z.close()

    @classmethod
    def cell(cls, sheet, address):
        if sheet not in cls.cells:
            root = ET.fromstring(cls.z.read(cls.sheet_parts[sheet]))
            cls.cells[sheet] = {c.get("r"): c for c in root.findall(".//m:c", NS)}
        return cls.cells[sheet].get(address)

    def test_workbook_does_not_retain_personal_cloud_path_or_revision_identity(self):
        forbidden = {"absPath", "revisionPtr", "revisionLog", "userName"}
        hits = []
        for node in self.workbook.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag in forbidden:
                hits.append(tag)
            if any(re.search(r"(?i)d\.docs\.live\.net|onedrive\.live\.com|[a-z]:[\\/]users[\\/]", value) for value in node.attrib.values()):
                hits.append("personal_path_attribute")
        self.assertEqual(hits, [], "Métadonnées privées à retirer ; catégories seules : " + repr(hits))

    def test_catalog_labels_and_visible_opening_base_are_sector_neutral(self):
        fields = json.loads((MODEL / "catalogue_champs.json").read_text(encoding="utf-8"))
        # L'alias API historique reste stable ; seuls les libellés sont génériques.
        field = next(f for f in fields if f["id"] == "installed_interceptors")
        display = " ".join([field["label"], *field.get("notes", [])])
        self.assertNotRegex(display.casefold(), r"intercepteur|missile|drone")
        self.assertNotRegex("".join(self.cell("Control", "B33").itertext()).casefold(), r"intercepteur|missile|drone")

    def test_comments_unused_strings_media_and_external_relationships_are_removed(self):
        forbidden_parts = [name for name in self.parts if "comment" in name.lower() or name.startswith(("xl/media/", "xl/externalLinks/", "xl/embeddings/"))]
        self.assertEqual(forbidden_parts, [])
        sst = ET.fromstring(self.z.read("xl/sharedStrings.xml"))
        self.assertEqual(len(sst), 0)
        external = []
        for name in self.parts:
            if name.endswith(".rels"):
                if any(node.get("TargetMode") == "External" for node in ET.fromstring(self.z.read(name))):
                    external.append(name)
        self.assertEqual(external, [])
        core = ET.fromstring(self.z.read("docProps/core.xml"))
        self.assertFalse(any(node.tag.endswith("}lastModifiedBy") for node in core))
        self.assertFalse(private_fragment_found(" ".join(core.itertext())))

    def test_formula_and_chart_caches_do_not_reuse_source_results(self):
        cached_parts = []
        shared_string_references = []
        cached = re.compile(rb'<f\b[^<>]*(?:/>|>[^<]*</f>)\s*<(?:v|is)\b')
        for part in self.sheet_parts.values():
            raw = self.z.read(part)
            if cached.search(raw):
                cached_parts.append(part)
            if re.search(rb'\bt="s"', raw):
                shared_string_references.append(part)
        self.assertEqual(cached_parts, [], "Caches financiers encore présents : " + repr(cached_parts))
        self.assertEqual(shared_string_references, [])
        for part in self.parts:
            if part.startswith("xl/charts/") and part.endswith(".xml"):
                self.assertIsNone(re.search(rb'<(?:\w+:)?(?:numCache|strCache)\b', self.z.read(part)), part)

    def test_original_market_funding_and_grant_assumptions_are_empty(self):
        required_empty = [("Valorisation", "D112"), ("DATA Financement", "D18"), ("DATA Financement", "F18"),
                          ("Financement Dette", "C3"), ("SUBVENTION_INVEST", "C3")]
        for sheet, address in required_empty:
            with self.subTest(sheet=sheet, cell=address):
                cell = self.cell(sheet, address)
                self.assertIsNotNone(cell)
                self.assertIsNone(cell.find("m:f", NS))
                self.assertIsNone(cell.find("m:v", NS))
                self.assertFalse("".join(cell.itertext()).strip())

    def test_all_xml_parts_have_no_known_private_documentation(self):
        from tca_bp.privacy import audit_workbook_documentation
        report = audit_workbook_documentation(TEMPLATE)
        self.assertEqual(report['status'], 'PASS', report['hits'])

    def test_market_sources_do_not_claim_a_historical_verification(self):
        text = ''.join(self.cell('Valorisation', 'E111').itertext())
        self.assertNotRegex(text, r'\d{2}/\d{2}/\d{4}|\d{2}:\d{2}\s*UTC')
        self.assertIn('dossier', text.casefold())


if __name__ == "__main__":
    unittest.main()
