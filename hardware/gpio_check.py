#!/usr/bin/env python3
"""FAC-IO preliminary GPIO map static checker. NOT a schematic/ERC substitute."""
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass(frozen=True)
class Signal:
    name: str
    gpio: int
    direction: str

# Candidate pin map mirrored from gpio-map-v0.md and the KiCad schematic.
# Relay commands are hardware-one-shot triggers, not direct coil gate signals.
SIGNALS = (
    Signal("ETH_SCK", 4, "out"),
    Signal("ETH_MOSI", 5, "out"),
    Signal("ETH_MISO", 6, "in"),
    Signal("ETH_CS_N", 7, "out"),
    Signal("ETH_INT_N", 10, "in"),
    Signal("ETH_RESET_N", 3, "out"),
    Signal("TRIG1", 0, "out"),
    Signal("TRIG2", 1, "out"),
    Signal("USB_DM", 18, "usb"),
    Signal("USB_DP", 19, "usb"),
    Signal("USB_VBUS_SENSE", 21, "in"),
)

STRAPPING = {2, 8, 9}
FLASH_RESERVED = set(range(12, 18))
USB = {18, 19}
RELAY = {"TRIG1", "TRIG2"}
EXPECTED_USB = {"USB_DM": 18, "USB_DP": 19}
EXPECTED_OTHER = {"USB_VBUS_SENSE": 21, "ETH_RESET_N": 3}
EXPECTED_RELAY_TRIGGERS = {
    "kRelayOpenTriggerPin": 0,
    "kRelayCloseTriggerPin": 1,
}

def validate(signals=SIGNALS):
    errors = []
    seen = {}
    for s in signals:
        if s.gpio in seen:
            errors.append(f"GPIO{s.gpio} used by both {seen[s.gpio]} and {s.name}")
        seen[s.gpio] = s.name
        if s.gpio < 0 or s.gpio > 21:
            errors.append(f"{s.name}: GPIO{s.gpio} outside ESP32-C3 GPIO range")
        if s.gpio in FLASH_RESERVED:
            errors.append(f"{s.name}: GPIO{s.gpio} reserved for flash")
        if s.gpio in STRAPPING:
            errors.append(f"{s.name}: GPIO{s.gpio} is a strapping pin")
        if s.gpio in USB and s.name not in EXPECTED_USB:
            errors.append(f"{s.name}: GPIO{s.gpio} reserved for native USB")
        if s.name in EXPECTED_USB and s.gpio != EXPECTED_USB[s.name]:
            errors.append(f"{s.name}: expected GPIO{EXPECTED_USB[s.name]}")
        if s.name in EXPECTED_OTHER and s.gpio != EXPECTED_OTHER[s.name]:
            errors.append(f"{s.name}: expected GPIO{EXPECTED_OTHER[s.name]}")
        if s.name in RELAY and s.gpio in STRAPPING | FLASH_RESERVED | USB:
            errors.append(f"{s.name}: unsafe reserved pin")
    if not RELAY.issubset({s.name for s in signals}):
        errors.append("Both relay outputs are required")
    return errors

def validate_firmware_startup(source=None):
    if source is None:
        source = (Path(__file__).resolve().parents[1] / "firmware/src/main.cpp").read_text(encoding="utf-8")

    errors = []
    for name, gpio in EXPECTED_RELAY_TRIGGERS.items():
        declaration = rf"constexpr\s+uint8_t\s+{name}\s*=\s*{gpio}\s*;"
        if not re.search(declaration, source):
            errors.append(f"Firmware {name} must map to GPIO{gpio}")

    function_match = re.search(
        r"void\s+initializeRelayTriggersInactive\s*\(\)\s*\{([^}]*)\}",
        source,
        re.DOTALL,
    )
    if not function_match:
        return errors + ["Firmware must initialize relay triggers inactive"]

    body = function_match.group(1)
    for name in EXPECTED_RELAY_TRIGGERS:
        preload = body.find(f"digitalWrite({name}, LOW)")
        enable = body.find(f"pinMode({name}, OUTPUT)")
        if preload < 0 or enable < 0 or preload > enable:
            errors.append(f"Firmware {name} must preload LOW before enabling its output")
        if f"digitalWrite({name}, HIGH)" in body:
            errors.append(f"Firmware startup must not assert {name}")

    setup_start = source.find("void setup()")
    loop_start = source.find("void loop()", setup_start)
    if setup_start < 0 or loop_start < 0:
        errors.append("Firmware setup/loop functions are required")
        return errors
    setup = source[setup_start:loop_start]
    init_call = setup.find("initializeRelayTriggersInactive();")
    network_start = min(
        (index for token in ("SPI.begin(", "Ethernet.init(", "Ethernet.begin(")
         if (index := setup.find(token)) >= 0),
        default=-1,
    )
    if init_call < 0 or network_start < 0 or init_call > network_start:
        errors.append("Relay triggers must be initialized before Ethernet/SPI setup")
    return errors

def validate_firmware_build_config(config=None):
    if config is None:
        config = (Path(__file__).resolve().parents[1] / "firmware/platformio.ini").read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*-D\s+ARDUINO_USB_MODE=1\s*$", config):
        return ["PlatformIO must select ESP32-C3 hardware USB Serial/JTAG mode"]
    if not re.search(r"(?m)^\s*-D\s+ARDUINO_USB_CDC_ON_BOOT=1\s*$", config):
        return ["PlatformIO must enable native USB CDC on boot for the board's USB-only debug interface"]
    return []

if __name__ == "__main__":
    problems = validate() + validate_firmware_startup() + validate_firmware_build_config()
    if problems:
        for p in problems:
            print("ERROR:", p)
        raise SystemExit(1)
    print(f"PASS: {len(SIGNALS)} candidate signals have no static pin conflicts")
    print("PASS: relay trigger GPIOs are initialized low before Ethernet/SPI setup")
    print("PASS: PlatformIO selects hardware USB Serial/JTAG and enables CDC on boot")
    print("WARNING: hardware reset behavior and module pin availability NOT verified")
    print("INFO: GPIO20 is intentionally unused; reset and relay startup levels still need bench verification")
