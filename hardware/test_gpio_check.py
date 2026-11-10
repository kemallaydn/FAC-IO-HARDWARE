"""Regression tests for firmware-to-schematic GPIO startup checks."""
from pathlib import Path
import unittest

import gpio_check


FIRMWARE_SOURCE = (
    Path(__file__).resolve().parents[1] / "firmware/src/main.cpp"
).read_text(encoding="utf-8")


class FirmwareGpioStartupTests(unittest.TestCase):
    def test_current_firmware_map_and_order_pass(self):
        self.assertEqual([], gpio_check.validate_firmware_startup(FIRMWARE_SOURCE))

    def test_wrong_trigger_gpio_is_rejected(self):
        changed = FIRMWARE_SOURCE.replace(
            "constexpr uint8_t kRelayOpenTriggerPin = 0;",
            "constexpr uint8_t kRelayOpenTriggerPin = 2;",
        )

        errors = gpio_check.validate_firmware_startup(changed)

        self.assertIn("Firmware kRelayOpenTriggerPin must map to GPIO0", errors)

    def test_missing_early_initialization_is_rejected(self):
        changed = FIRMWARE_SOURCE.replace(
            "  initializeRelayTriggersInactive();\n",
            "",
        )

        errors = gpio_check.validate_firmware_startup(changed)

        self.assertIn(
            "Relay triggers must be initialized before Ethernet/SPI setup",
            errors,
        )

    def test_native_usb_cdc_must_be_enabled(self):
        config = (Path(__file__).resolve().parents[1] / "firmware/platformio.ini").read_text(encoding="utf-8")
        self.assertEqual([], gpio_check.validate_firmware_build_config(config))
        disabled = config.replace("-D ARDUINO_USB_CDC_ON_BOOT=1", "-D ARDUINO_USB_CDC_ON_BOOT=0")
        self.assertTrue(gpio_check.validate_firmware_build_config(disabled))

    def test_c3_hardware_usb_mode_must_be_enabled(self):
        config = (Path(__file__).resolve().parents[1] / "firmware/platformio.ini").read_text(encoding="utf-8")
        disabled = config.replace("-D ARDUINO_USB_MODE=1", "-D ARDUINO_USB_MODE=0")
        self.assertIn("hardware USB Serial/JTAG", " ".join(gpio_check.validate_firmware_build_config(disabled)))


if __name__ == "__main__":
    unittest.main()
