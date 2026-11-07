import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hardware"))
from gpio_check import Signal, SIGNALS, validate

class GpioMapTests(unittest.TestCase):
    def test_current_map(self):
        self.assertEqual(validate(), [])
    def test_duplicate(self):
        bad = SIGNALS + (Signal("EXTRA", 0, "out"),)
        self.assertTrue(any("both" in e for e in validate(bad)))
    def test_strapping_pin(self):
        bad = tuple(Signal(s.name, 9 if s.name == "RELAY1_GATE" else s.gpio, s.direction) for s in SIGNALS)
        self.assertTrue(any("strapping" in e for e in validate(bad)))
    def test_usb_conflict(self):
        bad = SIGNALS + (Signal("SPI_ALT", 18, "out"),)
        self.assertTrue(any("reserved for native USB" in e for e in validate(bad)))
    def test_flash_pin(self):
        bad = SIGNALS + (Signal("BAD", 12, "out"),)
        self.assertTrue(any("reserved for flash" in e for e in validate(bad)))

if __name__ == "__main__":
    unittest.main()
