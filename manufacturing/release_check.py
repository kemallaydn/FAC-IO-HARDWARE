#!/usr/bin/env python3
"""Prevent accidental shipment of incomplete FAC-IO production files."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANUFACTURING = ROOT / "manufacturing"
REQUIRED = [
    "release/APPROVED.txt",
    "release/erc-report.txt",
    "release/drc-report.txt",
    "gerber/FAC-IO-Mini-V1.zip",
    "bom/FAC-IO-Mini-V1.csv",
    "position/FAC-IO-Mini-V1.csv",
]
def check_release(root=MANUFACTURING):
    missing = [p for p in REQUIRED if not (root / p).is_file()]
    if missing:
        return False, [f"Missing: {p}" for p in missing]
    approval = (root / "release/APPROVED.txt").read_text(encoding="utf-8")
    required_fields = ("REVISION=", "REVIEWER=", "DATE=", "PCB_DRC=PASS", "SCHEMATIC_ERC=PASS")
    absent = [x for x in required_fields if x not in approval]
    if absent:
        return False, [f"Missing approval field: {x}" for x in absent]
    return True, ["Release package present; human review of contents still required."]

if __name__ == "__main__":
    ok, messages = check_release()
    for m in messages:
        print(("INFO: " if ok else "BLOCKED: ") + m)
    sys.exit(0 if ok else 1)
