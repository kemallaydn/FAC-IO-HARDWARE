# Component selection gate — FAC-IO Mini V1

Status: **datasheet review; not yet released for fabrication**.

## MCU
Candidate **ESP32-C3-WROOM-02-N4** (4 MB flash, PCB antenna) or **ESP32-C3-WROOM-02U-N4** (external antenna). Prefer -02-N4 for prototype only if enclosure placement respects antenna keepout. Espressif datasheet identifies 15 GPIO, 160 MHz single-core CPU, 4 MB N4 / 8 MB N8 variants, USB Serial/JTAG and strapping GPIO2/8/9.

Datasheet: https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html
Chip: https://documentation.espressif.com/esp32-c3_datasheet_en.html

**Important caveat**: provisional SPI GPIO4–7 also have JTAG alternate functions. Verify debug requirements, reset levels and pin multiplexing before freezing layout. GPIO18/19 are USB D-/D+ and GPIO20/21 default UART0. Do not assume all chip pins are available on module.

## Ethernet
W5500 SPI Ethernet controller, with a compatible magnetics-equipped RJ45. WIZnet specifically notes that integrated magnetics with connected center taps can require extra isolation capacitors (C23/C24 in their example); choose an exact RJ45 part number before copying matching network.

**Magjack candidate:** CETUS `J1B1211CCD`. WIZnet lists it for its W5500-EVB and WIZ550io designs. The installed KiCad 10 footprint is `Connector_RJ:RJ45_Cetus_J1B1211CCD_Horizontal`; its twelve signal/LED holes and two 1.6 mm shield holes were compared with CETUS's mechanical drawing. The eight Ethernet holes are 0.9 mm, the four LED holes 1.02 mm, matching the drawing. The local `FAC_IO:J1B1211CCD` symbol follows CETUS's electrical pin drawing. Both physical shield tabs have pad number 13 in the installed footprint, so the symbol exposes one SHIELD pin 13; WIZnet's older reference drawing calls the tabs 13 and 14. This is a CAD convention, not two independent shield nets. Sourcing, board-edge fit and assembly still require confirmation.

The WIZnet `W5500-ref-RJ45WithMag` PDF was visually reviewed against the CETUS drawing. PHY `TXP/TXN` go to magjack `TD+/TD-` (pins 1/3), with separate 49.9 Ω pull-ups to analog 3.3 V; `RXP/RXN` go through separate 6.8 nF series capacitors to `RD+/RD-` (pins 4/6). The magnetics center taps (pins 2/5) have different bias/decoupling networks, so they must not simply be shorted together. The reference places a ferrite bead between digital and analog 3.3 V, 25 MHz crystal with load capacitors, `EXRES1` 12.4 kΩ to ground, `TOCAP`/`1V2O` local capacitors, and a separate chassis-ground net coupled to signal ground through a 1 nF/2 kV capacitor. The magjack's LED pins 9–12 need the reference's supply/current-limit connections. Pins 7 and 8 are unconnected in that reference. Copying this network still requires footprint/stackup/ESD review and a real ERC-tested schematic.

Reference: https://docs.wiznet.io/Product/Chip/Ethernet/W5500/ref-schematic
Layout: https://docs.wiznet.io/Design-Guide/hardware_design_guide

**Do not** use a bare RJ45 without magnetics. Verify ESD, magnetics orientation, RX/TX polarity, 25 MHz crystal, reset timing, termination, decoupling and PCB trace routing.

## Relays
Two independent changeover outputs, each with NO/COM/NC terminals, controlled by independent MOSFET low-side drivers with pulldowns and flyback suppression. The actual barrier OPEN input voltage/current is unavailable; contact compatibility remains a first-article acceptance check.

**Low-level signal candidate:** Omron `G6K-2P-Y DC12`, a non-latching, through-hole DPDT relay. Use only one contact pole per channel; leave the second pole unconnected and explicitly mark its pins no-connect in the integrated schematic. Omron's G6K datasheet lists a 12 V coil at 9.1 mA nominal (1,315 Ω) and reference failure-rate load of 10 µA at 10 mV DC. This is a candidate, not a guarantee at an unknown barrier input. The installed KiCad 10 libraries contain the compatible `Relay:Omron_G6K-2` symbol and `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` footprint; verify availability and assembly before schematic freeze.

Two coils at the 12 V nameplate draw 18.2 mA nominal and dissipate about 0.218 W total; this excludes logic, LEDs, tolerances and startup current. For design calculations only, assume an external 12 V supply with ±10% tolerance (10.8–13.2 V). The manufacturer's 75%-of-rated maximum must-operate threshold is 9 V at 23 °C, leaving 1.8 V at the low supply limit before input-protection drop. The actual site supply range, temperature derating and continuous coil voltage must be measured/reviewed before freezing protection or regulator ratings.

The manufacturer's bottom-view drawing was compared with the installed footprint: physical pin 1 maps to `A1` (coil +), pin 8 to `A2` (coil -); physical pins 2/3/4 map to `12` (NC), `11` (COM), `14` (NO), and pins 7/6/5 to `22` (NC), `21` (COM), `24` (NO). The symbol's standardized contact numbering matches the footprint, but its *default* footprint is the non-Y `G6K-2P`; explicitly set `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` on each schematic instance. The relay remains a candidate until supply, assembly and actual barrier-input checks are complete.

Manufacturer datasheet: https://components.omron.com/us-en/datasheet_pdf/K106-E1.pdf

The earlier SONGLE `SRD-12VDC-SL-C` in `relay-driver-design-v0.2.md` is not approved for an unknown low-current dry input; do not assume its high-current contact rating proves low-level switching reliability.

## Power
Nominal 12 V input, reverse-polarity protection, surge suppression, input overcurrent protection, 3.3 V switching regulator and local bypass. Exact protection/regulator MPNs and input voltage range remain open. Two relay coils may be energized simultaneously; budget accordingly.

**Buck candidate:** Diodes Incorporated `AP63203WU-7`, fixed 3.3 V, 2 A, 3.8–32 V input, TSOT-26. The manufacturer datasheet (not a product-page typo saying 3 V) confirms 3.3 V and shows a 4.7 µH inductor, 10 µF input, two 22 µF output and 100 nF BST-to-SW capacitor in its application circuit. Choose an inductor with verified saturation current and final capacitor MPNs after a load/thermal calculation. KiCad 10 provides `Regulator_Switching:AP63203WU`; the exact regulator footprint and power layout must be verified.

Manufacturer datasheet: https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf

## Pulse safety
**Hardware timeout candidate:** TI `SN74LV221ADR`, a 3.3 V-compatible dual non-retriggerable monostable in SOIC-16. One timer per relay can bound a pulse even if firmware leaves its trigger asserted. The manufacturer specifies external `Rext`/`Cext`, active-low clear, glitch-free power-up outputs, and a pulse-duration equation of approximately `Rext × Cext` for `Cext ≥ 1 nF`. A project-local symbol with datasheet pin numbers was added to `fac_io.kicad_sym` and exported successfully by KiCad. Timing component tolerance, reset sequencing, link-loss behavior and actual contact pulse width still require circuit design and bench validation; this is not an implemented safety circuit.

The manufacturer's function table supports a reset-safe trigger scheme to **evaluate**: hold each `A` low; hold each `B` low with a physical resistor while MCU pins are high impedance; assert a short positive pulse on `B` only after application authorization; hold `CLR_N` low until the 3.3 V rail and controller are ready. A `B` rising edge with `A` low triggers one finite `Q` pulse. `CLR_N` low forces `Q` low and can terminate a pulse. This still needs a reviewed startup circuit: releasing `CLR_N` with `A` low and `B` high can itself trigger an output. Hardware pulse limiting does not prove immediate OFF on Ethernet loss or a MOSFET short. TI also warns that a large timing capacitor can discharge through input protection during rapid power-down; select the actual R/C and any clamp only after calculating tolerances and worst-case supply fall time.

Manufacturer datasheet: https://www.ti.com/lit/ds/symlink/sn74lv221a.pdf

## Terminals
**Terminal candidates:** Same Sky/CUI `TB007-508-03BE` for each 3-position COM/NO/NC output and `TB007-508-02BE` for 12 V input. Both are horizontal, through-hole, 5.08 mm pitch; KiCad 10 includes corresponding `TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-03_1x03_P5.08mm_Horizontal` and `_02_1x02_` footprints. Verify the BE suffix drawing against the KiCad footprints, drill sizes, assembly method and wire-access clearance before placement.

## USB
USB-C receptacle for ESP32-C3 native USB Serial/JTAG; requires correct USB 2.0 wiring, CC pull-downs, ESD and protection against backfeeding supply. Verify behavior with only USB attached versus external 12 V present.

## Schematic freeze criteria
- Exact manufacturer part numbers + verified footprints for MCU, W5500, RJ45, relays, terminals, buck, USB-C and protections.
- Power budget and voltage/current/thermal calculations.
- Final GPIO pin map including bootstraps, USB and JTAG.
- Startup-safe relay drive verified independently of firmware.
- Review against vendor reference designs and first-article test requirements.
