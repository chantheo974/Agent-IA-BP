"""Maintenance sur un petit paquet OOXML fictif, jamais sur les pièces client.

Le recalcul simulé teste le protocole d'oracles ; il ne prouve pas Excel natif.
Les tests réels de trame et de calcul sont exécutés séparément.
"""
from __future__ import annotations

from copy import deepcopy
import json
import contextlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from xml.etree import ElementTree as ET

from tca_bp.maintenance import Maintenance
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core


def make_fixture(folder):
    folder.mkdir(parents=True)
    ns = core.NS
    workbook = f'<workbook xmlns="{ns}" xmlns:r="{core.REL}"><sheets><sheet name="Inputs" sheetId="1" r:id="rId1"/></sheets><calcPr fullCalcOnLoad="1"/></workbook>'
    worksheet = f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1"><v>2</v></c><c r="B1"><f t="shared" si="0" ref="B1:B2">A1*2</f><v>4</v></c></row><row r="2"><c r="A2"><v>3</v></c><c r="B2"><f t="shared" si="0"/><v>6</v></c></row></sheetData></worksheet>'
    styles = f'<styleSheet xmlns="{ns}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>'
    with zipfile.ZipFile(folder / "template.xlsm", "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="worksheet"/></Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)
        archive.writestr("xl/styles.xml", styles)
        archive.writestr("xl/vbaProject.bin", b"NONEXECUTABLE_TEST_WITNESS")
    (folder / "modele.json").write_text('{}', encoding="utf-8")
    (folder / "build_receipt.json").write_text(canonical({"model_id": "fixture/1"}), encoding="utf-8")


class FixtureEngine:
    def __init__(self, project_root, model_dir=None):
        self.project_root = Path(project_root)
        self.model_dir = Path(model_dir or self.project_root / "base")
        self.model_id = json.loads((self.model_dir / "build_receipt.json").read_text(encoding="utf-8"))["model_id"]
        self.template_path = self.model_dir / "template.xlsm"
        self.schema = json.loads((self.model_dir / "modele.json").read_text(encoding="utf-8"))

    def ensure_built(self):
        return {}

    def catalog(self):
        return deepcopy(self.schema.get('fields', []))

    def _open(self, path):
        return core.Workbook(path)

    def reseal_variant(self, workbook, output_dir, model_id, expected_changes):
        before = self._open(self.template_path)
        after = self._open(workbook)
        try:
            expected = {(c["sheet"], c["cell"]): (c["old_formula"], c["new_formula"]) for c in expected_changes}
            observed = {}
            for addr in before.sheet("Inputs")[1]:
                old, new = before.formula("Inputs", addr), after.formula("Inputs", addr)
                if old != new:
                    observed["Inputs", addr] = (old, new)
                if old is None and before.value("Inputs", addr) != after.value("Inputs", addr):
                    raise ValueError("Constante hors impact modifiée")
            if observed != expected:
                raise ValueError("Formule hors impact modifiée")
            for component in ("xl/styles.xml", "xl/vbaProject.bin"):
                if before.z.read(component) != after.z.read(component):
                    raise ValueError("Composant hors impact modifié")
        finally:
            before.close()
            after.close()
        output_dir.mkdir(parents=True)
        target = output_dir / "template.xlsm"
        shutil.copyfile(workbook, target)
        (output_dir / "modele.json").write_text(canonical({"model_id": model_id}), encoding="utf-8")
        receipt = {"model_id": model_id, "template_path": str(target), "schema_path": str(output_dir / "modele.json"),
                   "template_sha256": digest(target), "schema_sha256": digest(output_dir / "modele.json")}
        (output_dir / "build_receipt.json").write_text(canonical(receipt), encoding="utf-8")
        return receipt

    def context(self, path):
        wb = self._open(path)
        try:
            return {"input_signature": canonical([wb.value("Inputs", "A1"), wb.value("Inputs", "A2")])}
        finally:
            wb.close()

    def inspect(self, path, sheet, cells):
        wb = self._open(path)
        try:
            return {"cells": {cell: {"current": wb.snapshot(sheet, cell)} for cell in cells}}
        finally:
            wb.close()


class FixtureEngineFactory:
    """Constructeur CLI injecté ; l'objet retourné reste un adaptateur de test."""
    def __new__(cls, *args, **kwargs):
        return FixtureEngine(*args, **kwargs)


def native_witness(source, output, receipt, **kwargs):
    """Calcul indépendant attendu du cas fictif, sans interpréter la formule."""
    with zipfile.ZipFile(source) as archive:
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        cells = {node.get("r"): node for node in root.findall(".//m:c", core.N)}
        first = int(cells["A1"].find("m:v", core.N).text)
        second = int(cells["A2"].find("m:v", core.N).text)
        for cell, expected in (("B1", first * 3), ("B2", second * 2)):
            for old in list(cells[cell]):
                if old.tag == "{" + core.NS + "}v":
                    cells[cell].remove(old)
            ET.SubElement(cells[cell], "{" + core.NS + "}v").text = str(expected)
        with zipfile.ZipFile(output, "w") as target:
            for info in archive.infolist():
                target.writestr(deepcopy(info), ET.tostring(root) if info.filename == "xl/worksheets/sheet1.xml" else archive.read(info.filename))
    result = {"status": "RECALCULE", "calculation_state": 0, "source_sha256": digest(source), "output_sha256": digest(output), "macros_enabled": False}
    receipt.write_text(canonical(result), encoding="utf-8")
    return result


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_fixture(self.root / "base")
        self.engine = FixtureEngine(self.root)
        self.maintenance = Maintenance(self.engine, recalculator=native_witness)

    def tearDown(self):
        self.tmp.cleanup()

    def proposal(self):
        return self.maintenance.propose([{"sheet": "Inputs", "cell": "B1", "formula": "A1*3"}], "fixture/2", "Chaque unité représente désormais trois jours de prestation.")

    def scenarios(self, expected=6):
        return [{"name": "Deux unités", "fictional": True, "outputs": [{"sheet": "Inputs", "cell": "B1", "expected": expected}, {"sheet": "Inputs", "cell": "B2", "expected": 6}]}]

    def test_actual_ooxml_change_materializes_shared_anchor_without_other_change(self):
        before = digest(self.engine.template_path)
        version = self.maintenance.build(self.proposal())
        self.assertEqual(version["status"], "EXPERIMENTALE")
        self.assertFalse(version["existing_cases_migrated"])
        self.assertEqual(digest(self.engine.template_path), before)
        wb = core.Workbook(Path(version["model_dir"]) / "template.xlsm")
        try:
            self.assertEqual(wb.formula("Inputs", "B1"), "A1*3")
            self.assertEqual(wb.formula("Inputs", "B2"), "A2*2")
            self.assertEqual(wb.value("Inputs", "A1"), 2)
            self.assertIsNone(wb.value("Inputs", "B1"))
            self.assertIsNone(wb.value("Inputs", "B2"))
        finally:
            wb.close()

    def test_modified_or_stale_proposal_is_refused(self):
        proposal = self.proposal()
        proposal["changes"][0]["new_formula"] = "A1*999"
        with self.assertRaises(ValueError):
            self.maintenance.build(proposal)

    def test_no_implicit_scalar_structure_or_external_formula(self):
        for cell, formula in (("A1", "1+1"), ("B1", "WEBSERVICE(\"https://example.invalid\")"), ("B1", "[Other.xlsx]A1")):
            with self.subTest(cell=cell, formula=formula), self.assertRaises(ValueError):
                self.maintenance.propose([{"sheet": "Inputs", "cell": cell, "formula": formula}], "fixture/2", "Règle explicitement demandée à vérifier.")

    def test_independent_oracle_failure_blocks_publication(self):
        version = self.maintenance.build(self.proposal())
        result = self.maintenance.validate(version["model_dir"], self.scenarios(expected=999))
        self.assertEqual(result["status"], "FAIL")
        with self.assertRaises(ValueError):
            self.maintenance.approve(version["model_dir"], result["report_path"], "Responsable fictif")

    def test_validated_version_can_be_published_once_without_changing_default(self):
        before = digest(self.engine.template_path)
        version = self.maintenance.build(self.proposal())
        result = self.maintenance.validate(version["model_dir"], self.scenarios())
        self.assertEqual(result["status"], "PASS")
        publication = self.maintenance.approve(version["model_dir"], result["report_path"], "Responsable fictif")
        self.assertEqual(publication["status"], "PUBLIEE")
        self.assertFalse(publication["default_model_replaced"])
        self.assertEqual(digest(self.engine.template_path), before)
        with self.assertRaises(ValueError):
            self.maintenance.approve(version["model_dir"], result["report_path"], "Autre responsable")

    def test_mutated_native_evidence_blocks_publication(self):
        version = self.maintenance.build(self.proposal())
        result = self.maintenance.validate(version["model_dir"], self.scenarios())
        proof = Path(version["model_dir"]) / result["scenarios"][0]["native_receipt"]
        proof.write_text("modified", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.maintenance.approve(version["model_dir"], result["report_path"], "Responsable fictif")

    def test_forged_pass_flag_does_not_replace_independent_oracle(self):
        version = self.maintenance.build(self.proposal())
        result = self.maintenance.validate(version["model_dir"], self.scenarios(expected=999))
        result["status"] = "PASS"
        for scenario in result["scenarios"]:
            scenario["status"] = "PASS"
            for assertion in scenario["assertions"]:
                assertion["passed"] = True
        Path(result["report_path"]).write_text(canonical(result), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.maintenance.approve(version["model_dir"], result["report_path"], "Responsable fictif")

    def test_changed_scenarios_block_publication(self):
        version = self.maintenance.build(self.proposal())
        result = self.maintenance.validate(version["model_dir"], self.scenarios())
        Path(result["report_path"]).with_name("scenarios.json").write_text(canonical(self.scenarios(expected=999)), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.maintenance.approve(version["model_dir"], result["report_path"], "Responsable fictif")

    def test_every_changed_formula_requires_an_oracle_and_fictional_data(self):
        version = self.maintenance.build(self.proposal())
        with self.assertRaises(ValueError):
            self.maintenance.validate(version["model_dir"], [{"name": "Unrelated", "fictional": True, "outputs": [{"sheet": "Inputs", "cell": "B2", "expected": 6}]}])
        scenarios = self.scenarios()
        scenarios[0]["fictional"] = False
        with self.assertRaises(ValueError):
            self.maintenance.validate(version["model_dir"], scenarios)

    def test_cli_roundtrip_and_exclusive_proposal_file(self):
        from tca_bp.__main__ import main
        changes = self.root / "changes.json"
        proposal = self.root / "proposal.json"
        scenarios = self.root / "scenarios.json"
        changes.write_text(json.dumps([{"sheet": "Inputs", "cell": "B1", "formula": "A1*3"}]), encoding="utf-8")
        scenarios.write_text(json.dumps(self.scenarios()), encoding="utf-8")
        def run(*args):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = main(["--project-root", str(self.root), *map(str, args)])
            return code, json.loads(output.getvalue())
        with patch("tca_bp.model_engine.ModelEngine", FixtureEngineFactory), patch("tca_bp.native_excel.recalculate", native_witness):
            args = ("maintenance-propose", changes, "--version", "fixture/cli", "--reason", "Chaque unité représente trois jours, cas fictif.", "--out", proposal)
            code, result = run(*args)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "PROPOSITION")
            self.assertEqual(run(*args)[0], 2)
            code, version = run("maintenance-build", proposal)
            self.assertEqual((code, version["status"]), (0, "EXPERIMENTALE"))
            code, validation = run("maintenance-validate", version["model_dir"], scenarios)
            self.assertEqual((code, validation["status"]), (0, "PASS"))
            self.assertFalse((Path(version["model_dir"]) / "publication.json").exists())
            code, publication = run("maintenance-approve", version["model_dir"], validation["report_path"], "--approved-by", "Responsable fictif du test")
            self.assertEqual((code, publication["status"]), (0, "PUBLIEE"))

    def test_cli_reports_failed_oracle_with_nonzero_exit_code(self):
        from tca_bp.__main__ import main
        version = self.maintenance.build(self.proposal())
        scenarios = self.root / "scenarios.json"
        scenarios.write_text(json.dumps(self.scenarios(expected=999)), encoding="utf-8")
        with patch("tca_bp.model_engine.ModelEngine", FixtureEngineFactory), patch("tca_bp.native_excel.recalculate", native_witness), contextlib.redirect_stdout(io.StringIO()):
            code = main(["--project-root", str(self.root), "maintenance-validate", version["model_dir"], str(scenarios)])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
