import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "manufacturing"))
from release_check import REQUIRED, check_release

class ReleaseCheckTest(unittest.TestCase):
    def test_empty_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            ok, errors = check_release(Path(d))
            self.assertFalse(ok)
            self.assertEqual(len(errors), len(REQUIRED))

    def test_incomplete_approval_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in REQUIRED:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("placeholder", encoding="utf-8")
            ok, errors = check_release(root)
            self.assertFalse(ok)
            self.assertTrue(any("approval field" in e for e in errors))

    def test_complete_manifest_only_passes_presence_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in REQUIRED:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("placeholder", encoding="utf-8")
            (root / "release/APPROVED.txt").write_text(
                "REVISION=1\nREVIEWER=person\nDATE=2026-11-07\nPCB_DRC=PASS\nSCHEMATIC_ERC=PASS\n",
                encoding="utf-8")
            ok, _ = check_release(root)
            self.assertTrue(ok)  # Presence check ONLY, not Gerber validation.

if __name__ == "__main__":
    unittest.main()
