"""Qualifier une correction documentaire sans publier les anciens textes privés."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tca_bp.vendor.input_engine import Workbook
from tca_bp.storage import atomic_json, digest
from tca_bp.privacy import audit_workbook_documentation
from tca_bp.template_documentation import DOCUMENTARY_REPLACEMENTS


def verify(before_dir: Path, after_dir: Path, output: Path, *, qualification_guards=False):
    before_dir, after_dir = Path(before_dir), Path(after_dir)
    old = Workbook(before_dir / "TCA_BP_Trame_generique.xlsm")
    new = Workbook(after_dir / "TCA_BP_Trame_generique.xlsm")
    report = {"schema": "tca-bp-documentary-revision/1", "status": "EN_COURS",
              "before_sha256": old.hash, "after_sha256": new.hash, "checks": {}, "changes": [],
              "qualification_guards": qualification_guards}
    from tca_bp.model_qualification_guards import guard_formula, remove_inherited_protection_credentials
    try:
        schema = json.loads((before_dir / "modele.json").read_text(encoding="utf-8"))
        allowed_extra = {("Revenue", "B291"), ("Valorisation", "E111"), ("Valorisation", "B79"),
                         ("Charges_Externes", "A2"), ("BFR", "E50"), ("BFR", "G51"), ("Valorisation", "B3")}
        all_formula_logic_same, inputs_same, no_unknown_change, no_numeric_change = True, True, True, True
        styles_same, cell_attributes_same, sheet_protection_same = True, True, True
        guard_addresses = {("ATELIER_CIR_IS", f'{col}{row}') for col in 'CDEFGHIJKLM' for row in (67, 68, 86, 90)} | {('Valorisation', 'D138')}
        changed_guards = set()
        for name in old.sheets:
            old_cells, new_cells = old.sheet(name)[1], new.sheet(name)[1]
            protection = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetProtection'
            old_protection = ET.tostring(old.sheet(name)[0].find(protection))
            if qualification_guards:
                old_protection = remove_inherited_protection_credentials(old_protection)
            sheet_protection_same &= old_protection == ET.tostring(new.sheet(name)[0].find(protection))
            for address in old_cells.keys() | new_cells.keys():
                old_node, new_node = old_cells.get(address), new_cells.get(address)
                if old_node is None or new_node is None:
                    cell_attributes_same = False
                    styles_same = False
                else:
                    styles_same &= (ET.tostring(old.xfs[int(old_node.get('s', '0'))]) ==
                                    ET.tostring(new.xfs[int(new_node.get('s', '0'))]))
                    # t peut changer si une chaîne a été reconstruite ; style,
                    # protection, adresse et autres attributs restent contrôlés.
                    cell_attributes_same &= ({k: v for k, v in old_node.attrib.items() if k not in {'s', 't'}} ==
                                              {k: v for k, v in new_node.attrib.items() if k not in {'s', 't'}})
                old_f, new_f = old.formula(name, address), new.formula(name, address)
                old_v, new_v = old.value(name, address), new.value(name, address)
                if (old_f, old_v) == (new_f, new_v):
                    continue
                shape = lambda value: re.sub(r'"(?:[^"]|"")*"', '""', value or '')
                known_guard = qualification_guards and (name, address) in guard_addresses and old_f is not None
                if known_guard:
                    if guard_formula(name, address, old_f) != new_f:
                        raise ValueError('Révision de garde différente du contrat : ' + name + '!' + address)
                    changed_guards.add((name, address))
                if not known_guard and shape(old_f) != shape(new_f):
                    all_formula_logic_same = False
                if address in schema["cells"].get(name, {}):
                    inputs_same = False
                if not known_guard and (name, address) not in DOCUMENTARY_REPLACEMENTS and (name, address) not in allowed_extra:
                    no_unknown_change = False
                if any(isinstance(v, (int, float, bool)) for v in (old_v, new_v)):
                    no_numeric_change = False
                report["changes"].append({"sheet": name, "cell": address, "formula_display_changed": old_f != new_f,
                                          "old_text_sha256": hashlib.sha256(str(old_v or old_f).encode()).hexdigest(),
                                          "new_text": new_v if not new_f else "Texte affiché de formule modifié"})
            old._sheet_cache.pop(name, None)
            new._sheet_cache.pop(name, None)
        with zipfile.ZipFile(old.path) as left, zipfile.ZipFile(new.path) as right:
            same_parts = set(left.namelist()) == set(right.namelist())
            # Les cellules changent ; tous les composants hors feuilles restent
            # strictement identiques, dont styles/protections, VBA, liens, dessins.
            other_parts_same = same_parts and all((remove_inherited_protection_credentials(left.read(n)) if qualification_guards and n == 'xl/workbook.xml' else left.read(n)) == right.read(n) for n in left.namelist()
                                                   if not n.startswith("xl/worksheets/sheet") and n != 'xl/styles.xml')
            # Les builds antérieurs numérotaient les styles ajoutés dans l'ordre
            # d'un set Python. Seule une permutation des cellXfs est acceptée,
            # et chaque cellule doit conserver son style effectif ci-dessus.
            old_styles, new_styles = ET.fromstring(left.read('xl/styles.xml')), ET.fromstring(right.read('xl/styles.xml'))
            cell_xfs = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}cellXfs'
            ox, nx = old_styles.find(cell_xfs), new_styles.find(cell_xfs)
            styles_permutation_only = (ox.attrib == nx.attrib and sorted(map(ET.tostring, ox)) == sorted(map(ET.tostring, nx)))
            old_styles.remove(ox)
            new_styles.remove(nx)
            styles_permutation_only &= ET.tostring(old_styles) == ET.tostring(new_styles)
        report["checks"].update(formula_logic_unchanged_outside_declared_guards=all_formula_logic_same, inputs_unchanged=inputs_same,
                                 changes_in_reviewed_locations=no_unknown_change, no_numeric_change=no_numeric_change,
                                 other_package_parts_unchanged=other_parts_same, effective_cell_styles_unchanged=styles_same,
                                 cell_attributes_unchanged=cell_attributes_same, sheet_protection_unchanged=sheet_protection_same,
                                 styles_only_permuted=styles_permutation_only)
        if qualification_guards:
            report['checks']['exactly_declared_guard_changes'] = changed_guards == guard_addresses
            report['expected_guard_changes'] = len(guard_addresses)
            report['guard_changes'] = [sheet + '!' + cell for sheet, cell in sorted(changed_guards)]
        report["privacy_audit"] = audit_workbook_documentation(new.path)
        report["checks"]["privacy_scan_pass"] = report["privacy_audit"]["status"] == "PASS"
        report["status"] = "SUCCES" if all(report["checks"].values()) else "ECHEC"
    finally:
        old.close()
        new.close()
    atomic_json(output, report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--qualification-guards", action='store_true')
    args = parser.parse_args()
    result = verify(args.before, args.after, args.report, qualification_guards=args.qualification_guards)
    print(json.dumps({"status": result["status"], "checks": result["checks"], "changes": len(result["changes"])}))
    raise SystemExit(0 if result["status"] == "SUCCES" else 2)
