#!/usr/bin/env python3
"""Prevent accidental shipment of incomplete FAC-IO production files."""
from pathlib import Path
import csv
import hashlib
import json
import re
import sys
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
MANUFACTURING = ROOT / "manufacturing"
SOURCE_BOM = ROOT / "hardware/bom-draft.csv"
CAD_SOURCE_PATHS = (
    "hardware/FAC-IO-Mini-V1.kicad_sch",
    "hardware/FAC-IO-Mini-V1.kicad_pcb",
    "hardware/FAC-IO-Mini-V1.kicad_pro",
    "hardware/FAC-IO-Mini-V1.kicad_dru",
    "hardware/fac_io.kicad_sym",
    "hardware/sym-lib-table",
    "hardware/fp-lib-table",
    "hardware/fac_io.pretty/ESP32-C3-WROOM-02_0p3mmThermal.kicad_mod",
    "hardware/fac_io.pretty/WIZ850io_Host_J1_Socket_1x06.kicad_mod",
    "hardware/fac_io.pretty/WIZ850io_Host_J2_Socket_1x06.kicad_mod",
    "hardware/bom-draft.csv",
)
APPROVAL_HASH_PATHS = {
    "ERC_REPORT_SHA256": "release/erc-report.txt",
    "DRC_REPORT_SHA256": "release/drc-report.txt",
    "DRC_PARITY_SHA256": "release/drc-parity.json",
    "GERBER_SHA256": "gerber/FAC-IO-Mini-V1.zip",
    "BOM_SHA256": "bom/FAC-IO-Mini-V1.csv",
    "POSITION_SHA256": "position/FAC-IO-Mini-V1.csv",
}
BOM_FIELDS = (
    "Reference",
    "Quantity",
    "Value",
    "Footprint",
    "Manufacturer MPN",
    "RobotistanPro/LCSC C Code",
    "Populate",
)
PCB_REQUIRED = [
    "release/APPROVED.txt",
    "release/erc-report.txt",
    "release/drc-report.txt",
    "release/drc-parity.json",
    "gerber/FAC-IO-Mini-V1.zip",
]
PCBA_REQUIRED = PCB_REQUIRED + [
    "bom/FAC-IO-Mini-V1.csv",
    "position/FAC-IO-Mini-V1.csv",
]


def expected_approval_hashes(root, profile):
    source_digest = hashlib.sha256()
    for relative_path in CAD_SOURCE_PATHS:
        source_path = ROOT / relative_path
        source_digest.update(relative_path.encode("utf-8"))
        source_digest.update(b"\0")
        source_digest.update(source_path.read_bytes())
        source_digest.update(b"\0")

    keys = (
        "ERC_REPORT_SHA256",
        "DRC_REPORT_SHA256",
        "DRC_PARITY_SHA256",
        "GERBER_SHA256",
    )
    if profile == "pcba":
        keys += ("BOM_SHA256", "POSITION_SHA256")

    hashes = {"CAD_SOURCE_SHA256": source_digest.hexdigest()}
    for key in keys:
        artifact_path = root / APPROVAL_HASH_PATHS[key]
        hashes[key] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    return hashes


def check_release(root=MANUFACTURING, profile="pcba"):
    if profile not in ("pcb", "pcba"):
        return False, [f"Unknown release profile: {profile}"]

    required = PCB_REQUIRED if profile == "pcb" else PCBA_REQUIRED
    missing = [p for p in required if not (root / p).is_file()]
    if missing:
        return False, [f"Missing: {p}" for p in missing]

    problems = []
    approval = (root / "release/APPROVED.txt").read_text(encoding="utf-8")
    fields = {}
    for line in approval.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()

    required_fields = (
        "PROFILE",
        "REVISION",
        "REVIEWER",
        "DATE",
        "PCB_DRC",
        "SCHEMATIC_ERC",
        "CAD_SOURCE_SHA256",
    )
    for key in required_fields:
        if not fields.get(key):
            problems.append(f"Missing approval field: {key}")
    if fields.get("PROFILE", "").lower() != profile:
        problems.append(f"Approval PROFILE must be {profile.upper()}")
    if fields.get("PCB_DRC") != "PASS":
        problems.append("Approval must record PCB_DRC=PASS")
    if fields.get("SCHEMATIC_ERC") != "PASS":
        problems.append("Approval must record SCHEMATIC_ERC=PASS")
    revision = fields.get("REVISION", "").upper()
    if "DRAFT" in revision or "PRELIM" in revision:
        problems.append("Approval revision cannot be marked DRAFT/PRELIM")

    try:
        expected_hashes = expected_approval_hashes(root, profile)
        for key, expected in expected_hashes.items():
            approved_hash = fields.get(key, "").lower()
            if not re.fullmatch(r"[0-9a-f]{64}", approved_hash):
                problems.append(f"Approval field {key} must contain a SHA-256 digest")
            elif approved_hash != expected:
                problems.append(f"Approval field {key} does not match the current release file")
    except OSError as exc:
        problems.append(f"Cannot hash CAD or release files: {exc}")

    erc = (root / "release/erc-report.txt").read_text(encoding="utf-8", errors="replace")
    if not re.search(r"ERC messages:\s*0\s+Errors\s+0\s+Warnings", erc, re.IGNORECASE):
        problems.append("ERC report does not prove 0 errors and 0 warnings")

    drc = (root / "release/drc-report.txt").read_text(encoding="utf-8", errors="replace")
    for phrase in ("Found 0 DRC violations", "Found 0 unconnected pads", "Found 0 Footprint errors"):
        if phrase not in drc:
            problems.append(f"DRC report does not prove: {phrase}")

    try:
        drc_parity = json.loads((root / "release/drc-parity.json").read_text(encoding="utf-8"))
        if not isinstance(drc_parity, dict):
            problems.append("KiCad JSON DRC report root must be an object")
        else:
            empty_arrays = {
                "violations": "DRC violations",
                "unconnected_items": "unconnected items",
                "schematic_parity": "schematic parity errors",
                "ignored_checks": "ignored checks",
            }
            for key, label in empty_arrays.items():
                value = drc_parity.get(key)
                if not isinstance(value, list):
                    problems.append(f"KiCad JSON DRC report field '{key}' is missing or invalid")
                elif value:
                    problems.append(f"KiCad JSON DRC report contains {label}")
            if drc_parity.get("kicad_version") != "10.0.8":
                problems.append("KiCad JSON DRC report version is missing or unexpected")
    except (OSError, json.JSONDecodeError) as exc:
        problems.append(f"Cannot read/parse KiCad JSON DRC parity report: {exc}")

    try:
        with ZipFile(root / "gerber/FAC-IO-Mini-V1.zip") as gerbers:
            if gerbers.testzip() is not None:
                problems.append("Gerber ZIP CRC check failed")
            names = {Path(name).name for name in gerbers.namelist()}
            expected = {
                f"FAC-IO-Mini-V1-{layer}.gbr"
                for layer in (
                    "F_Cu", "B_Cu", "In1_Cu", "In2_Cu", "F_Mask", "B_Mask",
                    "F_Paste", "B_Paste", "F_Silkscreen", "B_Silkscreen", "Edge_Cuts",
                )
            } | {"FAC-IO-Mini-V1-PTH.drl", "FAC-IO-Mini-V1-NPTH.drl"}
            absent = sorted(expected - names)
            if absent:
                problems.append(f"Gerber ZIP is missing required layer/drill files: {', '.join(absent)}")
    except BadZipFile:
        problems.append("Gerber package is not a valid ZIP")

    if profile == "pcba":
        try:
            with (root / "bom/FAC-IO-Mini-V1.csv").open(newline="", encoding="utf-8-sig") as stream:
                bom_rows = list(csv.DictReader(stream))
            with SOURCE_BOM.open(newline="", encoding="utf-8-sig") as stream:
                source_bom_rows = list(csv.DictReader(stream))
            with (root / "position/FAC-IO-Mini-V1.csv").open(newline="", encoding="utf-8-sig") as stream:
                position_rows = list(csv.DictReader(stream))

            for filename, rows in (("Production BOM", bom_rows), ("Source BOM", source_bom_rows)):
                if not rows:
                    problems.append(f"{filename} is empty")
                    continue
                missing_fields = sorted(set(BOM_FIELDS) - set(rows[0]))
                if missing_fields:
                    problems.append(f"{filename} is missing required fields: {', '.join(missing_fields)}")

            bom_refs = [row.get("Reference", "").strip() for row in bom_rows]
            source_refs = [row.get("Reference", "").strip() for row in source_bom_rows]
            position_refs = [row.get("Designator", "").strip() for row in position_rows]
            if not bom_rows or any(not ref for ref in bom_refs):
                problems.append("Production BOM is empty or has blank Reference fields")
            if not source_bom_rows or any(not ref for ref in source_refs):
                problems.append("Source BOM is empty or has blank Reference fields")
            if not position_rows or any(not ref for ref in position_refs):
                problems.append("Production position file is empty or has blank Designator fields")
            if len(set(bom_refs)) != len(bom_refs):
                problems.append("Production BOM has duplicate references")
            if len(set(source_refs)) != len(source_refs):
                problems.append("Source BOM has duplicate references")
            if len(set(position_refs)) != len(position_refs):
                problems.append("Production position file has duplicate designators")
            if set(bom_refs) != set(position_refs):
                problems.append("Production BOM and position reference sets do not match")
            if set(bom_refs) != set(source_refs):
                problems.append("Production BOM and source BOM reference sets do not match")

            source_by_ref = {row.get("Reference", "").strip(): row for row in source_bom_rows}
            for row in bom_rows:
                ref = row.get("Reference", "").strip()
                source_row = source_by_ref.get(ref)
                if source_row is None:
                    continue
                for field in BOM_FIELDS[1:]:
                    production_value = row.get(field, "").strip()
                    source_value = source_row.get(field, "").strip()
                    if production_value != source_value:
                        problems.append(f"Production BOM {ref} {field} differs from source BOM")

            if any(not row.get("Manufacturer MPN", "").strip() for row in bom_rows):
                problems.append("Production BOM has blank manufacturer MPN fields")
            if any(not re.fullmatch(r"C[0-9]+", row.get("RobotistanPro/LCSC C Code", "").strip()) for row in bom_rows):
                problems.append("Production BOM has blank or invalid RobotistanPro/LCSC C Code fields")
        except (OSError, csv.Error) as exc:
            problems.append(f"Cannot read/parse BOM or position file: {exc}")

    if problems:
        return False, problems
    return True, [f"{profile.upper()} package checks pass; release approval is recorded but cannot be independently authenticated by this script."]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("pcb", "pcba"), default="pcba")
    parser.add_argument(
        "--root",
        type=Path,
        default=MANUFACTURING,
        help="Manufacturing package root (defaults to manufacturing/)",
    )
    parser.add_argument(
        "--print-approval-hashes",
        action="store_true",
        help="Print SHA-256 values for a reviewer to record after release files are staged",
    )
    args = parser.parse_args()
    package_root = args.root.expanduser().resolve()
    if args.print_approval_hashes:
        try:
            print(json.dumps(expected_approval_hashes(package_root, args.profile), indent=2))
            sys.exit(0)
        except OSError as exc:
            print(f"BLOCKED: Cannot calculate approval hashes: {exc}")
            sys.exit(1)
    ok, messages = check_release(root=package_root, profile=args.profile)
    for m in messages:
        print(("INFO: " if ok else "BLOCKED: ") + m)
    sys.exit(0 if ok else 1)
