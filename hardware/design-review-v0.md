# FAC-IO Mini V1 design review — 2026-11-07

## Progress
This is a **textual circuit connectivity specification**, not an exported electrical CAD netlist. It cannot be imported as a complete KiCad design or manufactured.

- [x] Confirm ESP32-C3-WROOM-02 module pin names against Espressif datasheet.
- [x] Confirm USB GPIO18/19 and boot strap GPIO2/8/9.
- [x] Identify W5500 reference schematic and magnetics compatibility concern.
- [x] Define preliminary net-to-net block connections in `netlist-design-v0.csv`.
- [ ] Select exact manufacturer part numbers and matching KiCad symbols/footprints.
- [ ] Build complete schematic, ERC, routed PCB, DRC and manufacturing package.

## High-risk findings
1. **GPIO4–7 double as JTAG**. Current candidate uses them for W5500 SPI. Native USB Serial/JTAG is reserved for flashing/debug, but external JTAG use may conflict.
2. **GPIO10 may glitch low at startup** per Espressif schematic checklist. It is assigned only to W5500 interrupt input in our proposal, not a relay gate.
3. GPIO0/1 relay gate assignments require actual scope verification at power-up, brownout, reset and flashing. Pulldowns are mandatory; software alone is not a safety interlock.
4. W5500 and integrated-magnetics RJ45 need the exact matching circuit. WIZnet warns certain center-tap arrangements require C23/C24 isolation capacitors; blindly substituting RJ45 parts is unsafe.
5. USB-C must not accidentally energize the 12V relay rail or backfeed the regulator. Explicit power-domain strategy is missing.
6. The nominal 12V supply range, relay contact minimum switching current and surge environment must be finalized before selecting protective components.

## Manufacturer references
- Espressif ESP32-C3-WROOM-02 module: https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html
- Espressif ESP32-C3 schematic checklist: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
- WIZnet W5500 reference: https://docs.wiznet.io/Product/Chip/Ethernet/W5500/ref-schematic

## Manufacturing gate
**BLOCKED** until real KiCad schematic, PCB and ERC/DRC exist. Do not order based on this document or earlier test Gerbers.
