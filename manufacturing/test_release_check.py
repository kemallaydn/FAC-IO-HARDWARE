"""Regression tests for the FAC-IO production package gate."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import release_check


ROOT = Path(__file__).resolve().parents[1]
POSITION_SOURCE = (
    ROOT
    / "manufacturing/DRAFT-2026-11-09-DRAFT-1.2/position/robotistan-pick-and-place-draft.csv"
)
GERBER_MEMBERS = {
    f"FAC-IO-Mini-V1-{layer}.gbr"
    for layer in (
        "F_Cu",
        "B_Cu",
        "In1_Cu",
        "In2_Cu",
        "F_Mask",
        "B_Mask",
        "F_Paste",
        "B_Paste",
        "F_Silkscreen",
        "B_Silkscreen",
        "Edge_Cuts",
    )
} | {"FAC-IO-Mini-V1-PTH.drl", "FAC-IO-Mini-V1-NPTH.drl"}


class ReleaseCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="fac-io-release-check-")
        self.project_root = Path(self.temp_dir.name)
        self.package = self.project_root / "manufacturing"
        for folder in ("release", "gerber", "bom", "position"):
            (self.package / folder).mkdir(parents=True, exist_ok=True)

        for index, relative_path in enumerate(release_check.CAD_SOURCE_PATHS):
            source_path = self.project_root / relative_path
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(f"fixture-cad-{index}\n", encoding="utf-8")
        (self.package / "release/erc-report.txt").write_text(
            "ERC messages: 0 Errors 0 Warnings\n", encoding="utf-8"
        )
        (self.package / "release/drc-report.txt").write_text(
            "Found 0 DRC violations\n"
            "Found 0 unconnected pads\n"
            "Found 0 Footprint errors\n",
            encoding="utf-8",
        )
        (self.package / "release/drc-parity.json").write_text(
            json.dumps(
                {
                    "kicad_version": "10.0.8",
                    "violations": [],
                    "unconnected_items": [],
                    "schematic_parity": [],
                    "ignored_checks": [],
                }
            ),
            encoding="utf-8",
        )
        with ZipFile(self.package / "gerber/FAC-IO-Mini-V1.zip", "w") as gerbers:
            for name in sorted(GERBER_MEMBERS):
                gerbers.writestr(name, "fixture")

        source_rows = self._read_csv(ROOT / "hardware/bom-draft.csv")
        for index, row in enumerate(source_rows, start=1):
            if not row["RobotistanPro/LCSC C Code"].strip():
                # Synthetic identifiers only make this fixture self-contained.
                row["RobotistanPro/LCSC C Code"] = f"C{9000000 + index}"
        self._write_csv(self.project_root / "hardware/bom-draft.csv", source_rows)
        self._write_csv(self.package / "bom/FAC-IO-Mini-V1.csv", source_rows)
        shutil.copy(
            POSITION_SOURCE,
            self.package / "position/FAC-IO-Mini-V1.csv",
        )
        self._write_approval()

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def _read_csv(path):
        with path.open(newline="", encoding="utf-8-sig") as stream:
            return list(csv.DictReader(stream))

    @staticmethod
    def _write_csv(path, rows):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _check(self, profile="pcba"):
        with (
            patch.object(release_check, "ROOT", self.project_root),
            patch.object(release_check, "SOURCE_BOM", self.project_root / "hardware/bom-draft.csv"),
        ):
            return release_check.check_release(self.package, profile=profile)

    def _write_approval(self, profile="pcba"):
        source_digest = hashlib.sha256()
        for relative_path in release_check.CAD_SOURCE_PATHS:
            source_digest.update(relative_path.encode("utf-8"))
            source_digest.update(b"\0")
            source_digest.update((self.project_root / relative_path).read_bytes())
            source_digest.update(b"\0")
        fields = {
            "PROFILE": profile.upper(),
            "REVISION": "V1.0",
            "REVIEWER": "fixture",
            "DATE": "2026-11-09",
            "PCB_DRC": "PASS",
            "SCHEMATIC_ERC": "PASS",
            "CAD_SOURCE_SHA256": source_digest.hexdigest(),
        }
        keys = [
            "ERC_REPORT_SHA256",
            "DRC_REPORT_SHA256",
            "DRC_PARITY_SHA256",
            "GERBER_SHA256",
        ]
        if profile == "pcba":
            keys.extend(("BOM_SHA256", "POSITION_SHA256"))
        for key in keys:
            path = self.package / release_check.APPROVAL_HASH_PATHS[key]
            fields[key] = hashlib.sha256(path.read_bytes()).hexdigest()
        content = "".join(f"{key}={value}\n" for key, value in fields.items())
        (self.package / "release/APPROVED.txt").write_text(content, encoding="utf-8")

    def test_complete_consistent_package_passes_structural_gate(self):
        ok, messages = self._check()
        self.assertTrue(ok, messages)

    def test_bom_field_drift_from_source_is_rejected(self):
        rows = self._read_csv(self.package / "bom/FAC-IO-Mini-V1.csv")
        rows[0]["Value"] = "INTENTIONALLY-MISMATCHED"
        self._write_csv(self.package / "bom/FAC-IO-Mini-V1.csv", rows)

        ok, messages = self._check()

        self.assertFalse(ok)
        self.assertIn("Production BOM C1 Value differs from source BOM", messages)

    def test_blank_or_non_catalog_supplier_code_is_rejected(self):
        rows = self._read_csv(self.package / "bom/FAC-IO-Mini-V1.csv")
        rows[0]["RobotistanPro/LCSC C Code"] = "TBD"
        self._write_csv(self.package / "bom/FAC-IO-Mini-V1.csv", rows)

        ok, messages = self._check()

        self.assertFalse(ok)
        self.assertIn(
            "Production BOM has blank or invalid RobotistanPro/LCSC C Code fields",
            messages,
        )

    def test_pcb_only_profile_does_not_require_bom_or_pick_and_place(self):
        self._write_approval(profile="pcb")
        shutil.rmtree(self.package / "bom")
        shutil.rmtree(self.package / "position")

        ok, messages = self._check(profile="pcb")

        self.assertTrue(ok, messages)
        self.assertIn("PCB package checks pass", messages[0])

    def test_cli_accepts_an_explicit_review_package_root(self):
        (self.package / "release/APPROVED.txt").unlink()
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "manufacturing/release_check.py"),
                "--profile",
                "pcb",
                "--root",
                str(self.package),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout.strip(),
            "BLOCKED: Missing: release/APPROVED.txt",
        )

    def test_changed_cad_source_invalidates_approval(self):
        source = self.project_root / "hardware/FAC-IO-Mini-V1.kicad_pcb"
        source.write_text(source.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

        ok, messages = self._check()

        self.assertFalse(ok)
        self.assertIn("Approval field CAD_SOURCE_SHA256 does not match the current release file", messages)

    def test_changed_report_invalidates_approval(self):
        report = self.package / "release/drc-report.txt"
        report.write_text(report.read_text(encoding="utf-8") + "stale\n", encoding="utf-8")

        ok, messages = self._check()

        self.assertFalse(ok)
        self.assertIn("Approval field DRC_REPORT_SHA256 does not match the current release file", messages)

    def test_approval_profile_must_match_requested_release_profile(self):
        ok, messages = self._check(profile="pcb")

        self.assertFalse(ok)
        self.assertIn("Approval PROFILE must be PCB", messages)


if __name__ == "__main__":
    unittest.main()
