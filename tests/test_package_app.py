"""Recette de conditionnement sur une fixture intégralement fictive."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools.package_app import (CLIENT_CODE, CLIENT_README, CORE_REQUIRED, DOC_FILES, MANIFEST, MODEL_FILES, MODEL_PREFIX,
    ROOT_FILES, TEMPLATE, VENDOR_REQUIRED, allowed_name, create_package, digest, json_bytes, verify_package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tca-package-fixture-")
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        for name in ROOT_FILES | CLIENT_CODE | {CLIENT_README, ".vscode/mcp.json", "tools/package_app.py"}:
            self.write(name, b"{}" if name.endswith(".json") else b"# Fixture de conditionnement\n")
        for number in range(1, 34):
            self.write(f"agents/agent_{number:02d}.json", json_bytes({"id": f"AGENT_{number:02d}", "sheet": f"Feuille {number:02d}"}))
        self.write("docs/INTERFACE.md", b"# Guide fictif\n")
        self.write("docs/ETAT_LIVRAISON.md", b"[Plan](../PLAN_CONCEPTION_AGENTS_BP_TCA.md)\n")
        self.write("docs/DISTRIBUTION.md", b"# Distribution fictive\n")
        for name in MODEL_FILES - {TEMPLATE, "modele.json", "build_receipt.json"}:
            self.write(MODEL_PREFIX + name, b"{}")
        model = self.root / MODEL_PREFIX / TEMPLATE
        model.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(model, "w") as archive:
            # Paquet OOXML lisible par le catalogue réel, intégralement fictif.
            ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
            rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            sheets = ''.join(f'<sheet name="Feuille {i:02d}" sheetId="{i}" r:id="rId{i}"/>' for i in range(1, 34))
            archive.writestr("xl/workbook.xml", f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>{sheets}</sheets></workbook>')
            relationships = ''.join(f'<Relationship Id="rId{i}" Target="worksheets/sheet{i}.xml" Type="worksheet"/>' for i in range(1, 34))
            archive.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + relationships + '</Relationships>')
            for i in range(1, 34):
                archive.writestr(f"xl/worksheets/sheet{i}.xml", f'<worksheet xmlns="{ns}"><sheetData/></worksheet>')
            archive.writestr("xl/styles.xml", f'<styleSheet xmlns="{ns}"><fills count="1"><fill><patternFill patternType="none"/></fill></fills><cellXfs count="1"><xf fillId="0"/></cellXfs></styleSheet>')
            archive.writestr("xl/vbaProject.bin", b"NONEXECUTABLE_FIXTURE")
        template_hash = digest(model.read_bytes())
        schema = json_bytes({"model_id": "tca-bp-template/1", "template_sha256": template_hash, "fields": []})
        self.write(MODEL_PREFIX + "modele.json", schema)
        self.write(MODEL_PREFIX + "build_receipt.json", json_bytes({
            "model_id": "tca-bp-template/1", "template_sha256": template_hash,
            "schema_sha256": digest(schema), "source_sha256": "f" * 64, "counts": {"sheets": 33},
            "template_path": "C:/Users/PRIVATE_BUILD_FOLDER/model.xlsm", "schema_path": "C:/Users/PRIVATE_BUILD_FOLDER/schema.json"}))
        self.output = self.base / "dist" / "pack.zip"

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def rewrite(self, source, transform):
        output = self.base / "tampered.zip"
        with zipfile.ZipFile(source) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        transform(parts)
        with zipfile.ZipFile(output, "w") as archive:
            for name, raw in parts.items():
                archive.writestr(name, raw)
        return output

    def test_pack_contains_model_33_contracts_licenses_and_only_allowed_files(self):
        for name in ("exemple/original.xlsm", ".git/config", ".venv/credentials.txt", "runtime/client.json",
                     "clients/one/source.txt", ".env", "tca_bp/secret.py", "tca_bp/api_key.json", "tca_bp/passwords.txt", "docs/credentials.md", "docs/client_notes.md"):
            self.write(name, b"NE_DOIT_PAS_ETRE_DISTRIBUE")
        result = create_package(self.root, self.output)
        self.assertEqual(result["status"], "CREE_ET_VERIFIE")
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(len([name for name in archive.namelist() if name.startswith("agents/")]), 33)
            self.assertTrue(VENDOR_REQUIRED.issubset(archive.namelist()))
            self.assertIn(MODEL_PREFIX + TEMPLATE, archive.namelist())
            self.assertFalse(any(b"NE_DOIT_PAS_ETRE_DISTRIBUE" in archive.read(name) for name in archive.namelist()))
            self.assertNotIn(b"PRIVATE_BUILD_FOLDER", archive.read(MODEL_PREFIX + "build_receipt.json"))
            self.assertNotIn(b"../PLAN_CONCEPTION", archive.read("docs/ETAT_LIVRAISON.md"))
        self.assertFalse(result["reference_files_required"])
        self.assertFalse(result["native_calculation_certified"])
        self.assertEqual(result["distribution"], "CLIENT")
        self.assertFalse(result["development_components_included"])

    def test_development_modules_tools_tests_and_examples_are_not_distributed(self):
        internal = ("tca_bp/model_build.py", "tca_bp/maintenance.py", "tca_bp/model_maintenance.py", "tca_bp/maintenance_impact.py",
                    "tca_bp/new_internal_module.py", "tools/package_app.py", "tools/build_model.py",
                    "tests/test_service.py", "docs/MAINTENANCE.md", "docs/RECETTE_MAINTENANCE.md",
                    "docs/exemples/maintenance-calendrier-changements.json", "docs/feuilles/internal_notes.md")
        for name in internal:
            self.write(name, b"IMPLEMENTATION_INTERNE_ABSENTE_DU_PACK")
            self.assertFalse(allowed_name(name), name)
        self.write("README.md", b"README_DEPOT_DEVELOPPEMENT")
        self.write(CLIENT_README, b"# Guide du pack client\n")
        create_package(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertFalse(set(internal).intersection(archive.namelist()))
            self.assertEqual(archive.read("README.md"), b"# Guide du pack client\n")
            self.assertFalse(any(name.startswith(("tools/", "tests/")) for name in archive.namelist()))
            self.assertEqual(json.loads(archive.read(MANIFEST))["distribution"], "CLIENT")

    def test_manifest_cannot_authorize_a_development_module(self):
        create_package(self.root, self.output)
        def add(parts):
            name = "tca_bp/maintenance.py"
            parts[name] = b"# Module de developpement\n"
            manifest = json.loads(parts[MANIFEST])
            manifest["files"].append({"path": name, "size": len(parts[name]), "sha256": digest(parts[name])})
            parts[MANIFEST] = json_bytes(manifest)
        with self.assertRaisesRegex(ValueError, "chemin exclu"):
            verify_package(self.rewrite(self.output, add))

    def test_client_readme_links_follow_its_packaged_location(self):
        self.write(CLIENT_README, b"[Interface](INTERFACE.md#utiliser)\n")
        self.write("docs/DISTRIBUTION.md", b"[Guide client](README_CLIENT.md)\n")
        create_package(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertIn(b"](<docs/INTERFACE.md#utiliser>)", archive.read("README.md"))
            self.assertEqual(archive.read("docs/DISTRIBUTION.md"), b"[Guide client](../README.md)\n")

    def test_actual_client_modules_import_and_run_from_extraction_in_isolated_python(self):
        project = Path(__file__).resolve().parents[1]
        for name in CLIENT_CODE:
            self.write(name, (project / name).read_bytes())
        for name in DOC_FILES | {CLIENT_README}:
            if (project / name).is_file():
                self.write(name, (project / name).read_bytes())
        for path in (project / "docs" / "feuilles").glob("*.md"):
            self.write(path.relative_to(project).as_posix(), path.read_bytes())
        self.write(MODEL_PREFIX + "graphe_dependances.json", json_bytes({"model_id": "tca-bp-template/1", "sheets": {}, "cells": []}))
        create_package(self.root, self.output)
        extracted = self.base / "client-extracted"
        with zipfile.ZipFile(self.output) as archive:
            archive.extractall(extracted)
        script = r'''
import contextlib, importlib, importlib.util, io, json, sys
from pathlib import Path
root, data = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root))
for module in ('tca_bp.model_engine', 'tca_bp.service', 'tca_bp.agents', 'tca_bp.gui', 'tca_bp.mcp_server', 'tca_bp.__main__', 'tca_bp.wacc_solver', 'tca_bp.wacc_native', 'tca_bp.sensitivity_native', 'tca_bp.calculation_operations', 'tca_bp.calculation_proofs', 'tca_bp.field_semantics', 'tca_bp.field_semantics_data', 'tca_bp._field_semantics_basis'):
    loaded = importlib.import_module(module)
    assert Path(loaded.__file__).resolve().is_relative_to(root), module
for module in ('tca_bp.model_build', 'tca_bp.maintenance', 'tca_bp.model_maintenance', 'tca_bp.maintenance_impact'):
    assert importlib.util.find_spec(module) is None, module
    assert module not in sys.modules, module
from tca_bp.model_engine import ModelEngine
from tca_bp.service import Application
from tca_bp.__main__ import main
engine = ModelEngine(root)
assert engine.ensure_built()['model_id'] == 'tca-bp-template/1'
app = Application(root, data)
assert app.initialize()['status'] == 'PRET'
assert len(app.agents()) == 33
case = app.create_case('Client fictif du test', 'Dossier fictif', case_id='fixture_client')
assert case['revision'] == 0 and len(app.list_cases()) == 1
assert len(case['model_ref']) == 64 and len(case['schema_sha256']) == 64
assert app.engine_for_case(case['id']).model_dir.parent == data / 'modeles'
for worker in ('wacc_worker.ps1', 'sensitivity_worker.ps1'):
    assert (root / 'tca_bp' / worker).is_file()
from tca_bp.mcp_server import dispatch
class NativeRoutingWitness:
    def solve_wacc(self, case_id, timeout=600):
        return {'operation':'wacc','case_id':case_id,'timeout':timeout}
    def verify_sensitivity(self, case_id, timeout=3600):
        return {'operation':'tables','case_id':case_id,'timeout':timeout}
witness = NativeRoutingWitness()
assert dispatch(witness, 'bp_solve_wacc', {'case_id':'fixture'})['timeout'] == 600
assert dispatch(witness, 'bp_verify_sensitivity', {'case_id':'fixture'})['timeout'] == 3600
for command in (['build'], ['maintenance-propose', 'absent.json', '--version', 'test/2', '--reason', 'Essai']):
    output, error = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
        code = main(['--project-root', str(root), '--data-dir', str(data)] + command)
    result = json.loads(error.getvalue())
    assert code == 2 and result['status'] == 'REFUSE', result
    assert 'pack client' in result['reason'], result
for action in (lambda: ModelEngine(root / 'missing-model').ensure_built(),
               lambda: engine.reseal_variant(root / 'absent.xlsm', root / 'unused', 'fixture/2', [])):
    try:
        action()
    except ValueError as error:
        assert 'pack client' in str(error), str(error)
    else:
        raise AssertionError('Une operation de developpement a ete acceptee')
for name, module in list(sys.modules.items()):
    if name == 'tca_bp' or name.startswith('tca_bp.'):
        if getattr(module, '__file__', None):
            assert Path(module.__file__).resolve().is_relative_to(root), name
assert not (root / 'unused').exists()
assert not (root / 'exemple').exists()
assert not (root / 'tools').exists()
assert not (root / 'tests').exists()
assert sys.flags.isolated and sys.flags.no_site
print(json.dumps({'status':'PASS','agents':33,'case_created':True,'isolated':bool(sys.flags.isolated)}))
'''
        # -I conserve les hooks du site système, dont ceux d'un pip install -e.
        # -S exclut ces chemins indirects pour cette sonde du coeur autonome.
        # Les imports PDF optionnels et l'installation sont hors de sa portée.
        run = subprocess.run([sys.executable, "-I", "-S", "-X", "utf8", "-c", script, str(extracted), str(self.base / "isolated-data")],
                             cwd=self.base, capture_output=True, text=True, encoding="utf-8", timeout=45)
        self.assertEqual(run.returncode, 0, run.stderr[-2500:])
        self.assertEqual(json.loads(run.stdout)["status"], "PASS")

    def test_extracted_model_initializes_without_reference_or_rebuild(self):
        from tca_bp.model_engine import ModelEngine
        create_package(self.root, self.output)
        extracted = self.base / "extracted"
        with zipfile.ZipFile(self.output) as archive:
            archive.extractall(extracted)
        self.assertFalse((extracted / "exemple").exists())
        with patch("tca_bp.model_engine.build_model", side_effect=AssertionError("Reconstruction interdite")):
            receipt = ModelEngine(extracted).ensure_built()
        self.assertEqual(receipt["model_id"], "tca-bp-template/1")

    def test_model_hash_mismatch_refuses_before_output_creation(self):
        self.write(MODEL_PREFIX + TEMPLATE, b"MODELE_MODIFIE")
        with self.assertRaisesRegex(ValueError, "ne correspond"):
            create_package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_destinations_inside_sources_are_refused_and_existing_pack_preserved(self):
        for folder in ("exemple", "models", "tca_bp", "docs", "clients", "runtime"):
            with self.subTest(folder=folder), self.assertRaises(ValueError):
                create_package(self.root, self.root / folder / "pack.zip")
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"EXISTANT")
        with self.assertRaisesRegex(ValueError, "existe"):
            create_package(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), b"EXISTANT")

    def test_missing_contract_or_license_is_refused(self):
        license_file = self.root / "tca_bp/vendor/vendor/olefile/LICENSE.txt"
        license_file.unlink()
        with self.assertRaisesRegex(ValueError, "provenance"):
            create_package(self.root, self.output)
        self.write("tca_bp/vendor/vendor/olefile/LICENSE.txt", b"LICENCE FICTIVE")
        (self.root / "agents/agent_33.json").unlink()
        with self.assertRaisesRegex(ValueError, "33 contrats"):
            create_package(self.root, self.output)

    def test_tampering_or_unlisted_file_is_detected(self):
        create_package(self.root, self.output)
        modified = self.rewrite(self.output, lambda parts: parts.__setitem__("docs/INTERFACE.md", b"MODIFIE"))
        with self.assertRaisesRegex(ValueError, "Empreinte"):
            verify_package(modified)
        extra = self.rewrite(self.output, lambda parts: parts.__setitem__("docs/ARCHITECTURE.md", b"NON_LISTE"))
        with self.assertRaisesRegex(ValueError, "exactement"):
            verify_package(extra)

    def test_forbidden_archive_paths_are_refused_before_extraction(self):
        create_package(self.root, self.output)
        for name in ("../escape.txt", "exemple/original.xlsm", "C:/escape.txt"):
            changed = self.rewrite(self.output, lambda parts, n=name: parts.__setitem__(n, b"EXCLU"))
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "chemin exclu"):
                verify_package(changed)

    def test_manifest_cannot_hide_missing_runtime_component(self):
        create_package(self.root, self.output)
        def remove(parts):
            del parts["tca_bp/service.py"]
            manifest = json.loads(parts[MANIFEST])
            manifest["files"] = [entry for entry in manifest["files"] if entry["path"] != "tca_bp/service.py"]
            parts[MANIFEST] = json_bytes(manifest)
        changed = self.rewrite(self.output, remove)
        with self.assertRaisesRegex(ValueError, "Composant"):
            verify_package(changed)

    def test_private_proof_links_become_clear_mentions_without_changing_source_doc(self):
        original = ("# Recette fictive\n\n[Rapport natif](../runtime/run/native.json)\n"
                    "[Variante](../models/versions/test/validation.json)\n"
                    "[Guide](INTERFACE.md)\n[Documentation](https://example.org/spec)\n").encode()
        self.write("docs/RECETTE_VALIDATION.md", original)
        create_package(self.root, self.output)
        self.assertEqual((self.root / "docs/RECETTE_VALIDATION.md").read_bytes(), original)
        with zipfile.ZipFile(self.output) as archive:
            result = archive.read("docs/RECETTE_VALIDATION.md").decode()
        self.assertIn("Rapport natif (preuve locale", result)
        self.assertIn("non incluse dans le pack", result)
        self.assertNotIn("](../runtime", result)
        self.assertIn("[Guide](INTERFACE.md)", result)
        self.assertIn("[Documentation](https://example.org/spec)", result)

    def test_development_document_links_become_explicit_mentions(self):
        self.write("docs/INTERFACE.md", b"[Maintenance](MAINTENANCE.md)\n[Outil](../tools/package_app.py)\n")
        create_package(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            text = archive.read("docs/INTERFACE.md").decode()
        self.assertIn("non inclus dans le pack client", text)
        self.assertNotIn("](MAINTENANCE.md)", text)

    def test_missing_public_document_target_is_not_silently_removed(self):
        self.write("docs/INTERFACE.md", b"[Guide](PUBLIC_GUIDE_MISSING.md)")
        with self.assertRaisesRegex(ValueError, "Lien documentaire"):
            create_package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_personal_document_path_is_refused_without_exposing_its_value(self):
        self.write("docs/INTERFACE.md", b"Source C:/Users/PRIVATE_PERSON/documents/record.json")
        with self.assertRaisesRegex(ValueError, "chemin personnel") as context:
            create_package(self.root, self.output)
        self.assertNotIn("PRIVATE_PERSON", str(context.exception))
        self.assertFalse(self.output.exists())

    def test_verified_model_with_private_path_is_still_refused(self):
        model = self.root / MODEL_PREFIX / TEMPLATE
        with zipfile.ZipFile(model, "w") as archive:
            archive.writestr("xl/workbook.xml", '<workbook path="C:/Users/PRIVATE_PERSON/source"/>')
        schema_path = self.root / MODEL_PREFIX / "modele.json"
        schema = json.loads(schema_path.read_bytes())
        schema["template_sha256"] = digest(model.read_bytes())
        schema_path.write_bytes(json_bytes(schema))
        receipt_path = self.root / MODEL_PREFIX / "build_receipt.json"
        receipt = json.loads(receipt_path.read_bytes())
        receipt.update(template_sha256=schema["template_sha256"], schema_sha256=digest(schema_path.read_bytes()))
        receipt_path.write_bytes(json_bytes(receipt))
        with self.assertRaisesRegex(ValueError, "chemin personnel") as context:
            create_package(self.root, self.output)
        self.assertNotIn("PRIVATE_PERSON", str(context.exception))

    def test_pack_rejects_private_name_with_final_dot(self):
        self.write('docs/INTERFACE.md', b'Validation par PERSONNEFICTIVE.')
        with patch('tca_bp.privacy.PRIVATE_TOKEN_HASHES', {digest(b'personnefictive')}):
            with self.assertRaisesRegex(ValueError, 'fragment documentaire') as context:
                create_package(self.root, self.output)
        self.assertNotIn('PERSONNEFICTIVE', str(context.exception))

    def test_verify_rejects_private_xml_even_when_all_hashes_are_recomputed(self):
        import io
        create_package(self.root, self.output)
        def tamper(parts):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as workbook:
                workbook.writestr('xl/workbook.xml', '<workbook><hidden>PERSONNEFICTIVE.</hidden></workbook>')
            parts[MODEL_PREFIX + TEMPLATE] = stream.getvalue()
            template_hash = digest(stream.getvalue())
            schema = json.loads(parts[MODEL_PREFIX + 'modele.json'])
            schema['template_sha256'] = template_hash
            parts[MODEL_PREFIX + 'modele.json'] = json_bytes(schema)
            receipt = json.loads(parts[MODEL_PREFIX + 'build_receipt.json'])
            receipt.update(template_sha256=template_hash, schema_sha256=digest(parts[MODEL_PREFIX + 'modele.json']))
            parts[MODEL_PREFIX + 'build_receipt.json'] = json_bytes(receipt)
            manifest = json.loads(parts[MANIFEST])
            manifest['template_sha256'] = template_hash
            for entry in manifest['files']:
                entry.update(size=len(parts[entry['path']]), sha256=digest(parts[entry['path']]))
            parts[MANIFEST] = json_bytes(manifest)
        changed = self.rewrite(self.output, tamper)
        with patch('tca_bp.privacy.PRIVATE_TOKEN_HASHES', {digest(b'personnefictive')}):
            with self.assertRaisesRegex(ValueError, 'fragment documentaire'):
                verify_package(changed)

    def test_verify_checks_python_documentation_even_when_its_hash_is_updated(self):
        create_package(self.root, self.output)
        def tamper(parts):
            name = "tca_bp/agents.py"
            parts[name] += b"\n# PERSONNEFICTIVE.\n"
            manifest = json.loads(parts[MANIFEST])
            for entry in manifest["files"]:
                if entry["path"] == name:
                    entry.update(size=len(parts[name]), sha256=digest(parts[name]))
            parts[MANIFEST] = json_bytes(manifest)
        changed = self.rewrite(self.output, tamper)
        with patch('tca_bp.privacy.PRIVATE_TOKEN_HASHES', {digest(b'personnefictive')}):
            with self.assertRaisesRegex(ValueError, 'fragment documentaire'):
                verify_package(changed)

    def test_zip_verification_rejects_personal_metadata_even_with_updated_manifest(self):
        create_package(self.root, self.output)
        def tamper(parts):
            name = "docs/INTERFACE.md"
            parts[name] = b"Dossier C:/Users/PRIVATE_PERSON/notes"
            manifest = json.loads(parts[MANIFEST])
            for entry in manifest["files"]:
                if entry["path"] == name:
                    entry.update(size=len(parts[name]), sha256=digest(parts[name]))
            parts[MANIFEST] = json_bytes(manifest)
        changed = self.rewrite(self.output, tamper)
        with self.assertRaisesRegex(ValueError, "chemin personnel"):
            verify_package(changed)


if __name__ == "__main__":
    unittest.main()
