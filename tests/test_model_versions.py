"""Coexistence réelle sur petits paquets OOXML, sans Excel ni classeur client."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tca_bp.model_engine import ModelEngine
from tca_bp.model_registry import model_pin
from tca_bp.service import Application
from tca_bp.storage import canonical, digest
from tca_bp.vendor import input_engine as core


def fixture(root: Path, *, multiple=2, maximum=100, model_id="fixture/shared") -> ModelEngine:
    root.mkdir(parents=True)
    template = root / "TCA_BP_Trame_generique.xlsm"
    names = ["Inputs", "Control", "Assumptions"]
    with zipfile.ZipFile(template, "w") as archive:
        sheets = ''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i, name in enumerate(names, 1))
        archive.writestr("xl/workbook.xml", f'<workbook xmlns="{core.NS}" xmlns:r="{core.REL}"><sheets>{sheets}</sheets><calcPr calcMode="autoNoTable"/></workbook>')
        relationships = ''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1, 4))
        archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + relationships + '</Relationships>')
        bodies = [f'<row r="1"><c r="A1"/><c r="B1"><f>A1*{multiple}</f></c></row>', '<row r="59"><c r="C59"><v>3</v></c></row>', '']
        for i, body in enumerate(bodies, 1):
            archive.writestr(f"xl/worksheets/sheet{i}.xml", f'<worksheet xmlns="{core.NS}"><sheetData>{body}</sheetData></worksheet>')
        archive.writestr("xl/styles.xml", f'<styleSheet xmlns="{core.NS}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>')
        archive.writestr("xl/vbaProject.bin", b"NONEXECUTABLE_FIXTURE")
    schema = {"model_id": model_id, "template_sha256": digest(template), "cells": {"Inputs": {"A1": {"kind": "number", "max": maximum}}},
              "fields": [{"id": "amount", "sheet": "Inputs", "label": f"Montant limité à {maximum}", "kind": "number", "cells": ["A1"]}], "registers": {}}
    wb = core.Workbook(template)
    try:
        schema["cells"]["Inputs"]["A1"]["fill"] = wb.fill("Inputs", "A1")
        schema["signature"] = wb.semantic_signature(schema)
    finally:
        wb.close()
    (root / "modele.json").write_text(canonical(schema), encoding="utf-8")
    (root / "build_receipt.json").write_text(canonical({"model_id": model_id, "template_sha256": digest(template), "schema_sha256": digest(root / "modele.json")}), encoding="utf-8")
    return ModelEngine(root.parent, root)


class ModelVersionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tca-model-versions-")
        self.root = Path(self.tmp.name)
        self.old_engine = fixture(self.root / "old", multiple=2)
        self.new_engine = fixture(self.root / "new", multiple=3, maximum=10)
        self.data = self.root / "data"
        self.old = Application(self.root, self.data, engine=self.old_engine)
        self.a = self.old.create_case("Client fictif", "Ancien dossier", case_id="old_case")
        self.source = self.old.add_source("old_case", text="Valeur fictive documentée pour vérifier les versions.")

    def tearDown(self):
        self.tmp.cleanup()

    def update(self, value=50, *, source=None):
        return {"field_id": "amount", "value": value, "reason": "Paramètre de recette fictive", "evidence": source or self.source["id"], "status": "CONFIRME"}

    def new_app(self):
        return Application(self.root, self.data, engine=self.new_engine)

    def unpin(self):
        with self.old.store.connection() as db:
            db.execute("UPDATE cases SET model_ref=NULL,template_sha256=NULL,schema_sha256=NULL WHERE id='old_case'")
            event = db.execute("SELECT id,details FROM history WHERE case_id='old_case' AND kind='CREATION'").fetchone()
            old = json.loads(event["details"])
            for key in ("model_ref", "template_sha256", "schema_sha256"):
                old.pop(key, None)
            db.execute("UPDATE history SET details=? WHERE id=?", (canonical(old), event["id"]))

    def test_old_and_new_dossiers_keep_distinct_formulas_limits_and_receipts_after_restart(self):
        plan = self.old.prepare_changes("old_case", [self.update()], "before_upgrade")
        fresh = self.new_app()
        b = fresh.create_case("Autre client fictif", "Nouveau dossier", case_id="new_case")
        self.assertEqual(self.a["model_id"], b["model_id"])
        self.assertNotEqual(self.a["model_ref"], b["model_ref"])
        self.assertNotEqual(self.a["template_sha256"], b["template_sha256"])
        # Les sources de développement ne sont plus nécessaires aux dossiers.
        shutil.rmtree(self.root / "old")
        restarted = self.new_app()
        result = restarted.apply_plan("old_case", plan["id"])
        self.assertEqual(model_pin(result), model_pin(self.a))
        self.assertEqual(restarted.inspect("old_case", "Inputs", ["A1", "B1"])["cells"]["B1"]["current"]["formula"], "A1*2")
        self.assertEqual(restarted.inspect("new_case", "Inputs", ["B1"])["cells"]["B1"]["current"]["formula"], "A1*3")
        source = restarted.add_source("new_case", text="Montant fictif pour nouvelle version.")
        with self.assertRaisesRegex(ValueError, "maximum"):
            restarted.prepare_changes("new_case", [self.update(source=source["id"])])
        self.assertEqual(restarted.apply_plan("old_case", plan["id"])["status"], "DEJA_APPLIQUE")
        self.assertEqual(restarted.get_case("old_case")["revision"], 1)
        self.assertIn("100", restarted.fields("old_case", "Inputs")[0]["label"])
        self.assertEqual(len(list((self.data / "modeles").iterdir())), 2)

    def test_same_template_different_schema_is_a_distinct_pinned_version(self):
        schema_dir = self.root / "schema_only"
        shutil.copytree(self.root / "old", schema_dir)
        schema = json.loads((schema_dir / "modele.json").read_text(encoding="utf-8"))
        schema["cells"]["Inputs"]["A1"]["max"] = 10
        (schema_dir / "modele.json").write_text(canonical(schema), encoding="utf-8")
        receipt = json.loads((schema_dir / "build_receipt.json").read_text(encoding="utf-8"))
        receipt["schema_sha256"] = digest(schema_dir / "modele.json")
        (schema_dir / "build_receipt.json").write_text(canonical(receipt), encoding="utf-8")
        app = Application(self.root, self.data, engine=ModelEngine(self.root, schema_dir))
        b = app.create_case("Client fictif", "Schéma différent")
        self.assertEqual(self.a["template_sha256"], b["template_sha256"])
        self.assertNotEqual(self.a["schema_sha256"], b["schema_sha256"])
        self.assertNotEqual(self.a["model_ref"], b["model_ref"])
        self.assertTrue(app.prepare_changes("old_case", [self.update()])["engine_plan"]["valid"])

    def test_multiple_cases_share_one_archive_and_no_per_case_model_copy(self):
        second = self.old.create_case("Client fictif", "Second dossier")
        self.assertEqual(model_pin(self.a), model_pin(second))
        self.assertEqual(len(list((self.data / "modeles").iterdir())), 1)
        self.assertEqual(list(Path(second["folder"]).rglob("modele.json")), [])

    def test_windows_transient_archive_rename_retries_same_copy_and_closes_files(self):
        rename = Path.rename
        attempts = []
        def transient(source, target):
            attempts.append((source, target))
            if len(attempts) <= 3:
                error = PermissionError("Transient fixture lock")
                error.winerror = (5, 32, 33)[len(attempts) - 1]
                raise error
            return rename(source, target)
        app = self.new_app()
        with patch("tca_bp.model_registry.os.name", "nt"), patch.object(Path, "rename", transient), patch("tca_bp.model_registry.time.sleep") as sleep:
            case = app.create_case("Client fictif", "Publication après verrou transitoire")
        self.assertEqual(len(attempts), 4)
        self.assertEqual(len(set(attempts)), 1)
        self.assertEqual(sleep.call_count, 3)
        self.assertEqual(case["model_status"], "VERSION_EXACTE_DISPONIBLE")
        self.assertFalse(list((self.data / "modeles").glob(".sealing-*")))

    def test_archive_rename_retries_are_bounded_and_do_not_hide_other_errors(self):
        for code, expected in ((5, 8), (87, 1)):
            error = OSError("Fixture rename refusal")
            error.winerror = code
            app = self.new_app()
            with self.subTest(code=code), patch("tca_bp.model_registry.os.name", "nt"), patch.object(Path, "rename", side_effect=error) as rename, patch("tca_bp.model_registry.time.sleep"):
                with self.assertRaisesRegex(OSError, "Fixture rename refusal"):
                    app.initialize()
                self.assertEqual(rename.call_count, expected)
            self.assertFalse(list((self.data / "modeles").glob(".sealing-*")))
        self.assertEqual(len(self.old.list_cases()), 1)

    def test_rename_collision_never_adopts_different_existing_archive(self):
        def collision(source, destination):
            destination.mkdir()
            (destination / "seal.json").write_text('{}')
            error = PermissionError("Fixture collision")
            error.winerror = 5
            raise error
        with patch.object(Path, "rename", collision), patch("tca_bp.model_registry.time.sleep") as sleep:
            with self.assertRaisesRegex(ValueError, "identité"):
                self.new_app().initialize()
        sleep.assert_not_called()
        self.assertEqual(len(self.old.list_cases()), 1)

    def test_existing_case_does_not_require_an_available_current_default(self):
        shutil.rmtree(self.root / "old")
        absent = ModelEngine(self.root, self.root / "unavailable-default")
        reopened = Application(self.root, self.data, engine=absent)
        self.assertEqual(reopened.get_case("old_case")["model_status"], "VERSION_EXACTE_DISPONIBLE")
        self.assertTrue(reopened.prepare_changes("old_case", [self.update()])["engine_plan"]["valid"])
        self.assertFalse(reopened._initialized)

    def test_recovery_receipt_must_carry_the_exact_case_model(self):
        plan = self.old.prepare_changes("old_case", [self.update()])
        result = self.old.apply_plan("old_case", plan["id"])
        transaction = Path(self.a["folder"]) / "transactions" / plan["id"] / "transaction.json"
        transaction.write_text(canonical({"status": "EN_COURS"}), encoding="utf-8")
        self.assertEqual(self.old.recovery_status("old_case")["transactions_to_inspect"][0]["recovery_status"], "COMMIT_CONFIRME_MIROIR_INCOMPLET")
        result["schema_sha256"] = "0" * 64
        with self.old.store.connection() as db:
            db.execute("UPDATE plans SET result=? WHERE id=?", (canonical(result), plan["id"]))
        self.assertEqual(self.old.recovery_status("old_case")["transactions_to_inspect"][0]["recovery_status"], "COPIE_COMMISEE_A_INSPECTER")
        with self.assertRaisesRegex(ValueError, "version exacte"):
            self.old.apply_plan("old_case", plan["id"])

    def test_changed_default_template_or_schema_is_refused_for_new_cases_only(self):
        self.old_engine.template_path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "trame générique a changé"):
            self.old.create_case("Client fictif", "Refusé", case_id="refused")
        self.assertFalse(self.old.store.case_dir("refused").exists())
        self.assertTrue(self.old.prepare_changes("old_case", [self.update()])["engine_plan"]["valid"])
        new = self.new_app()
        new.initialize()
        (self.root / "new" / "modele.json").write_text('{}')
        with self.assertRaisesRegex(ValueError, "manifeste.*changé"):
            new.create_case("Client fictif", "Refusé")

    def test_archived_template_and_schema_tampering_is_detected_after_engine_was_loaded(self):
        self.old.engine_for_case("old_case")
        folder = self.data / "modeles" / self.a["model_ref"]
        for name in ("TCA_BP_Trame_generique.xlsm", "modele.json", "build_receipt.json"):
            with self.subTest(name=name):
                path = folder / name
                before = path.read_bytes()
                path.write_bytes(before + b" ")
                self.assertEqual(self.old.get_case("old_case")["model_status"], "VERSION_INDISPONIBLE_OU_MODIFIEE")
                with self.assertRaisesRegex(ValueError, "archivé a été modifié"):
                    self.old.fields("old_case", "Inputs")
                path.write_bytes(before)

    def test_forged_archive_seal_cannot_adopt_modified_component(self):
        folder = self.data / "modeles" / self.a["model_ref"]
        path = folder / "modele.json"
        path.write_bytes(path.read_bytes() + b" ")
        seal_path = folder / "seal.json"
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
        seal["files"]["modele.json"] = digest(path)
        seal_path.write_text(canonical(seal), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "identité"):
            self.old.engine_for_case("old_case")

    def test_unsealed_optional_graph_or_mutated_in_memory_schema_is_refused(self):
        folder = self.data / "modeles" / self.a["model_ref"]
        graph = folder / "graphe_dependances.json"
        graph.write_text('{}')
        with self.assertRaisesRegex(ValueError, "non scellé"):
            self.old.engine_for_case("old_case")
        graph.unlink()
        engine = self.old.engine_for_case("old_case")
        engine.schema["cells"]["Inputs"]["A1"]["max"] = 999
        with self.assertRaisesRegex(ValueError, "mémoire"):
            self.old.prepare_changes("old_case", [self.update(500)])

    def test_missing_archive_never_falls_back_to_current_or_rebuilds(self):
        folder = self.data / "modeles" / self.a["model_ref"]
        shutil.rmtree(folder)
        fresh = self.new_app()
        self.assertEqual(fresh.get_case("old_case")["model_status"], "VERSION_INDISPONIBLE_OU_MODIFIEE")
        with patch("tca_bp.model_engine.build_model", side_effect=AssertionError("No rebuild")):
            with self.assertRaisesRegex(ValueError, "Version exacte.*absente"):
                fresh.fields("old_case", "Inputs")
        self.assertFalse(folder.exists())

    def test_migration_by_changing_all_case_pins_is_refused_against_creation_journal(self):
        app = self.new_app()
        b = app.create_case("Client fictif", "Nouveau dossier")
        with app.store.connection() as db:
            db.execute("UPDATE cases SET model_ref=?,template_sha256=?,schema_sha256=? WHERE id='old_case'", (b["model_ref"], b["template_sha256"], b["schema_sha256"]))
        with self.assertRaisesRegex(ValueError, "Migration implicite"):
            app.fields("old_case", "Inputs")

    def test_plan_identity_cannot_be_changed_to_new_version_even_with_same_model_id(self):
        plan = self.old.prepare_changes("old_case", [self.update()])
        app = self.new_app()
        b = app.create_case("Client fictif", "Nouveau dossier")
        with app.store.connection() as db:
            stored = db.execute("SELECT payload FROM plans WHERE id=?", (plan["id"],)).fetchone()
            payload = json.loads(stored["payload"])
            payload.update(model_pin(b))
            db.execute("UPDATE plans SET payload=? WHERE id=?", (canonical(payload), plan["id"]))
        with self.assertRaisesRegex(ValueError, "version exacte"):
            app.apply_plan("old_case", plan["id"])
        self.assertEqual(app.get_case("old_case")["revision"], 0)

    def test_unpinned_legacy_case_stays_readable_but_requires_explicit_exact_proof(self):
        before = digest(Path(self.a["workbook_path"]))
        self.unpin()
        app = self.new_app()
        state = app.get_case("old_case")
        self.assertEqual(state["model_status"], "VERSION_NON_EPINGLEE")
        self.assertIsNone(state["model_ref"])
        with self.assertRaisesRegex(ValueError, "Rattachement explicite"):
            app.prepare_changes("old_case", [self.update()])
        with self.assertRaisesRegex(ValueError, "v0000"):
            app.bind_legacy_case("old_case", self.root / "new")
        bound = app.bind_legacy_case("old_case", self.root / "old")
        self.assertEqual(model_pin(bound), model_pin(self.a))
        self.assertEqual(digest(Path(bound["workbook_path"])), before)
        self.assertEqual(bound["revision"], 0)
        self.assertTrue(app.prepare_changes("old_case", [self.update()])["engine_plan"]["valid"])
        with self.assertRaisesRegex(ValueError, "déjà épinglé"):
            app.bind_legacy_case("old_case", self.root / "new")

    def test_legacy_cannot_be_bound_without_initial_or_with_old_unpinned_plan(self):
        plan = self.old.prepare_changes("old_case", [self.update()])
        with self.old.store.connection() as db:
            payload = json.loads(db.execute("SELECT payload FROM plans WHERE id=?", (plan["id"],)).fetchone()["payload"])
            for key in ("model_ref", "template_sha256", "schema_sha256"):
                payload.pop(key)
            db.execute("UPDATE plans SET payload=? WHERE id=?", (canonical(payload), plan["id"]))
        self.unpin()
        initial = Path(self.a["workbook_path"])
        raw = initial.read_bytes()
        initial.unlink()
        with self.assertRaisesRegex(ValueError, "v0000"):
            self.old.bind_legacy_case("old_case", self.root / "old")
        initial.write_bytes(raw)
        self.old.bind_legacy_case("old_case", self.root / "old")
        with self.assertRaisesRegex(ValueError, "version exacte"):
            self.old.apply_plan("old_case", plan["id"])


if __name__ == "__main__":
    unittest.main()
