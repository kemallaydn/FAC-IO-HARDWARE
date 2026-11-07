#!/usr/bin/env python3
"""FAC-IO preliminary GPIO map static checker. NOT a schematic/ERC substitute."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Signal:
    name: str
    gpio: int
    direction: str

# GPIO assignments are PROVISIONAL; validate against exact ESP32-C3 module.
SIGNALS = (
    Signal("ETH_SCK", 4, "out"),
    Signal("ETH_MOSI", 5, "out"),
    Signal("ETH_MISO", 6, "in"),
    Signal("ETH_CS_N", 7, "out"),
    Signal("ETH_INT_N", 10, "in"),
    Signal("ETH_RST_N", 3, "out"),
    Signal("RELAY1_GATE", 0, "out"),
    Signal("RELAY2_GATE", 1, "out"),
    Signal("USB_DM", 18, "usb"),
    Signal("USB_DP", 19, "usb"),
    Signal("STATUS_LED", 20, "out"),
)

STRAPPING = {2, 8, 9}
FLASH_RESERVED = set(range(12, 18))
USB = {18, 19}
RELAY = {"RELAY1_GATE", "RELAY2_GATE"}
EXPECTED_USB = {"USB_DM": 18, "USB_DP": 19}

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
        if s.name in RELAY and s.gpio in STRAPPING | FLASH_RESERVED | USB:
            errors.append(f"{s.name}: unsafe reserved pin")
    if not RELAY.issubset({s.name for s in signals}):
        errors.append("Both relay outputs are required")
    return errors

if __name__ == "__main__":
    problems = validate()
    if problems:
        for p in problems:
            print("ERROR:", p)
        raise SystemExit(1)
    print(f"PASS: {len(SIGNALS)} candidate signals have no static pin conflicts")
    print("WARNING: hardware reset behavior and module pin availability NOT verified")
