# FAC-IO Mini V1 — PROJECT STATUS / AI HANDOFF
Last reviewed: 2026-11-08. Branch: main.
**Status: ENGINEERING DRAFT / NOT PRODUCTION READY.** This file is the primary continuity checkpoint for any new AI agent.

## 2026-11-08 fabrication draft refresh — CAD pass, release still blocked
- Matched C9 to manufacturer-specified KEMET `C1206C102KGRACTU` (1 nF, 2 kV, X7R, 1206), preserving the existing routed 1206 footprint. Set exact candidate values for F1 `1812L050/30PR`, FB1 `BLM18AG121SN1D`, and Y1 `ABM8-25.000MHZ-10-D1G-T` in schematic/PCB/BOM. Updated `hardware/FAC-IO-Mini-V1.kicad_sch` and `.kicad_pcb`; the temporary 1812 C9 reroute was discarded because it did not pass DRC.
- Latest local KiCad 10.0.8 `sch erc --severity-all --exit-code-violations`: exit 0, 0 violations. `pcb drc --severity-all --exit-code-violations --schematic-parity`: exit 0, 0 violations, 0 unconnected, 0 parity issues. Reports: `validation-reports/schematic-erc.txt`, `validation-reports/pcb-drc.txt`. `git diff --check`: exit 0.
- Regenerated `manufacturing/DRAFT-2026-11-08/` from the same current schematic/board: 11 Gerber layers, plated/non-plated drills, BOM, front SMD position CSV, and `DRAFT-FAC-IO-Mini-V1-Gerber-Drill.zip`. ZIP integrity passed. Gerbonara independently parsed 4 copper layers plus mask/silk/paste/outline, 212 plated and 8 non-plated drill objects; reported outline bounds ~110.1 x 75.1 mm. The antenna notch and silk labels are on the current board. `manufacturing/release_check.py` exits 1 as intended; no `release/APPROVED.txt` or production package exists.
- Added `DRAFT-schematic.pdf` and `DRAFT-assembly-front.pdf` to the draft package. Rendered both PDFs with Poppler; the assembly drawing uses references without values to reduce clutter. These are review aids, not approved assembly instructions.
- **Open before manufacture:** exact MPNs for remaining passives/ESD/power parts and availability, controlled impedance and return-path review against the actual 4-layer stackup, Ethernet/USB layout and power integrity review, THT assembly confirmation, external barrier OPEN-input electrical data, independent schematic/PCB review, and prototype bench tests (power, Ethernet, output pulse, reset/brownout/crash/link-loss OFF). Draft outputs must not be submitted as a production release.

## 2026-11-08 routed PCB — M3 CAD gate passed; manufacturing blocked
- Current integrated files: `hardware/FAC-IO-Mini-V1.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, `fac_io.kicad_sym`, `fac_io.pretty/ESP32-C3-WROOM-02_0p3mmThermal.kicad_mod`, `sym-lib-table`, `fp-lib-table`. Replaced the USB receptacle with manufacturer-listed HRO `TYPE-C-31-M-12` and matching installed footprint, eliminating the GCT locating-hole clearance error. Board has 4 layers, GND plane on In1.Cu, GND pour on B.Cu, 82 schematic components and 4 board-only M3 holes. Routed all nets at >=0.2 mm; contact copper has a project DRC rule requiring >=0.5 mm separation. Manually corrected relay contact routes and a GND via after routing.
- Local KiCad 10.0.8: `kicad-cli sch erc --severity-all --exit-code-violations`: exit 0, 0 violations. `kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity`: exit 0, 0 DRC violations, 0 unconnected items, 0 footprint parity errors. Reports in `validation-reports/`. The source board matches the schematic.
- Measured direct routed paths on the current board: W5500 TXP/TXN to RJ45 19.59/19.11 mm; W5500 RXP/RXN to coupling capacitors 15.14/16.02 mm; coupling capacitors to RJ45 17.17/15.27 mm. This is geometry only; 100 Ω differential impedance, return continuity, full pair coupling and USB 90 Ω impedance have not been verified against a fabricator stackup. ESP32 antenna is still within the board outline, contrary to Espressif's preferred over-edge placement, and requires layout correction or a qualified antenna solution. W5500 analog decoupling, power-loop placement, EMI/ESD, exact passive MPNs and hardware fail-safe testing remain open. No Gerber generated or release approved.
- Next: finish signal-integrity/antenna/power layout, silk polarity and terminal labels, freeze BOM MPNs and stackup, inspect fabrication files and assembly capability, then prototype and bench-test. Do not order this CAD-pass draft as production hardware.

## 2026-11-08 integrated schematic — M2 CAD gate, electrical review open
- Replaced `hardware/FAC-IO-Mini-V1.kicad_sch` functional blocks with one 87-instance, 61-net schematic: 12 V input/protection, AP63203 3.3 V buck, ESP32-C3-WROOM-02-N4, W5500 plus CETUS magjack/matching network, self-powered USB-C, dual SN74LV221A pulse timer, AO3400A coil drivers, two Omron G6K relays and isolated output terminals. Added `hardware/FAC-IO-Mini-V1.kicad_pro`, `hardware/fp-lib-table`; expanded `hardware/sym-lib-table` and `hardware/fac_io.kicad_sym`. No previous user work was discarded; the earlier block draft was replaced only after the generated schematic parsed and passed ERC in `/tmp`.
- Ran local `kicad-cli sch erc --severity-all --exit-code-violations -o validation-reports/schematic-erc.txt hardware/FAC-IO-Mini-V1.kicad_sch`: **exit 0, 0 errors, 0 warnings**. Ran `kicad-cli sch export netlist -o validation-reports/schematic-integrated.net ...`: **exit 0**. Audited the exported net relationships for relay contacts, coil flyback, power isolation, USB VBUS sensing and timer-to-gate drive. This is a CAD/ERC pass, not a full electrical, layout, timing or hardware safety validation.
- **Next:** review exact passive/ESD/fuse/crystal/timing MPNs and power tolerances; regenerate the PCB from this schematic, place and route all 87 physical components, then run schematic parity + DRC. Existing PCB is still the incompatible partial draft. No Gerber or release approval.

## 2026-11-08 PCB synchronization — M3 routing in progress
- Regenerated `hardware/FAC-IO-Mini-V1.kicad_pcb` from the current KiCad XML netlist: 82 physical schematic components, 4 board-only M3 holes, 4 copper layers, 110 × 75 mm outline. Matched every pad to the schematic net and component UUID; placed verified library footprints without intercomponent copper/courtyard overlap. Selected `USB4105-GF-A` in place of the earlier USB4085 because the latter's installed pad geometry violates the default 0.2 mm copper clearance; updated the schematic and board together.
- Added project-local `hardware/fac_io.pretty/ESP32-C3-WROOM-02_0p3mmThermal.kicad_mod`, derived from KiCad 10's module footprint by changing only the twelve GND thermal-via drills from 0.2 to 0.3 mm; this removes the default minimum-drill DRC errors. `hardware/fp-lib-table` includes the local library.
- Real local `kicad-cli sch erc --severity-all --exit-code-violations`: **exit 0, 0 errors, 0 warnings**. Real `kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity`: **exit 5, 4 USB4105 locating-hole clearance violations, 208 unconnected items, 0 schematic-parity errors**. Reports: `validation-reports/schematic-erc.txt`, `validation-reports/pcb-drc.txt`. Placement, copper routing, USB hole exception/fabricator capability, exact BOM, power/timing calculations and hardware validation remain open. No Gerber generated.
- **Next:** resolve the USB connector hole geometry with supplier capability or another verified footprint, route all signals/power/return paths, then repeat DRC and visual inspection.

## 2026-11-08 manufacturing path and Ethernet part review — M1 in progress
- Reconfirmed the existing working tree changes from the 2026-11-07 audit; no previous edits were discarded. Local `kicad-cli version` remains 10.0.8.
- Checked Robotistan's current PCB service page. `manufacturing/README.md` now records the required fabrication Gerber ZIP/RAR and drill layers, plus BOM and Pick & Place for assembly. The page lists five boards as the standard minimum PCB order; the earlier goal of two assembled prototypes is a bring-up quantity, not a confirmed order quantity. THT component assembly and sourcing still require supplier confirmation. No upload or order was made.
- Added CETUS `J1B1211CCD` as a WIZnet-used integrated-magnetics RJ45 candidate in `hardware/component-selection-v1.md`. The local KiCad 10 footprint exists, but a matching symbol was not found. Pin mapping, center taps, shield/LED network, ESD, footprint-to-datasheet geometry and availability remain open. No schematic or PCB placement was changed for this candidate.
- WIZnet's W5500 reference drawing numbers the candidate RJ45's two chassis pins 13 and 14, while the installed KiCad footprint labels both physical shield pads 13. This discrepancy triggered the manufacturer drawing review below; project CAD uses a single shared SHIELD net for both physical tabs.
- Reviewed CETUS's own connector schematic and mechanical images: PCB pins 1–8 are Ethernet/magnetics, 9–12 are LEDs, and two physical shield tabs share the same chassis. Added project-local `hardware/fac_io.kicad_sym` with one logical SHIELD pin 13 for the installed footprint's two pad-13 tabs, plus `hardware/sym-lib-table`. `kicad-cli sym export svg --symbol J1B1211CCD` succeeded (exit 0) and the rendered symbol was visually checked. This validates CAD parsing and pin labels, **not** the full W5500 circuit, sourcing or schematic/PCB parity. WIZnet's store and LCSC listed the candidate in stock during this review; reconfirm before ordering.
- Compared Omron's G6K-2P-Y bottom-view pin drawing with KiCad's `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` and compatible `Relay:Omron_G6K-2` symbol. `A1/A2` map to physical coil pins 1/8; standardized contact pads `12/11/14` map to physical 2/3/4, and `22/21/24` to 7/6/5. Updated `hardware/component-selection-v1.md` with this mapping. No relay has yet been placed in the integrated schematic.
- Added a second project-local symbol, `SN74LV221ADR`, from TI's pin table; `kicad-cli sym export svg --symbol SN74LV221ADR` succeeded (exit 0) and the SVG was visually checked. This non-retriggerable dual monostable is a **candidate** to bound both relay pulses; no timeout circuit or firmware handshake exists yet. Updated `hardware/component-selection-v1.md` with the datasheet timing basis and open safety checks.
- Added source-backed candidates for the 3.3 V buck (`AP63203WU-7`; Diodes datasheet confirms 3.3 V/2 A) and 5.08 mm CUI input/output terminals to `hardware/component-selection-v1.md`. These are not a frozen BOM; exact input protection, inductor/capacitor MPNs, footprint geometry, supply range and assembly remain open.
- Visually inspected WIZnet's full `W5500-ref-RJ45WithMag` reference PDF against CETUS's electrical/mechanical drawings and the installed KiCad footprint. Recorded the TX/RX, center-tap, analog-rail, crystal, LED and chassis-ground requirements in `hardware/component-selection-v1.md`. The footprint's 0.9 mm signal, 1.02 mm LED and 1.6 mm shield drills match the manufacturer's hole drawing. This is a reference/footprint review, not a W5500 schematic ERC pass or signal-integrity verification.
- Reviewed TI's `SN74LV221ADR` function and power-down tables. Recorded a candidate reset-safe trigger sequence and the timing-capacitor discharge risk in `hardware/component-selection-v1.md`; it has not been implemented in CAD or bench-tested. Corrected stale status sentences in `hardware/architecture.md` and `docs/validation.md` so they distinguish real draft checks from a passed design gate.
- Re-ran local KiCad 10.0.8 `sch erc --severity-all --exit-code-violations` and `pcb drc --severity-all --exit-code-violations --schematic-parity` against the unchanged main drafts after the reference review. Both returned **exit 5**. Current reports in `validation-reports/` remain **53 ERC violations** and **15 DRC violations, 6 unconnected items, 18 schematic-parity issues**. No production Gerber was generated.
- Ran `python3 manufacturing/release_check.py`: **exit 1**, correctly blocking release because approval, passing ERC/DRC reports, Gerber ZIP, BOM and position files are absent. Marked `hardware/relay-driver-design-v0.2.md` as historical so its superseded SONGLE candidate and GPIO-only timeout cannot be mistaken for the approved relay circuit. `git diff --check` passed.
- Documented the Omron symbol's default-footprint trap (non-Y footprint must be overridden to the chosen `G6K-2P-Y`), the two-coil 18.2 mA nameplate budget, and a provisional 10.8–13.2 V external-supply assumption in `hardware/component-selection-v1.md`. These calculations are not a verified field power budget; temperature and protection-drop checks remain. Final `kicad-cli version` was 10.0.8 and `git diff --check` passed.
- **Next action:** finish exact part selection and electrical design, then replace the block-only schematic with the integrated circuit. Do not export production Gerbers from the disconnected draft PCB.

## 2026-11-07 local KiCad 10.0.8 audit — M0 in progress
- Initial working tree was clean on `main`; `kicad-cli version` returned `10.0.8`.
- Initial real ERC failed to load the main schematic (exit 3); initial DRC failed to load the PCB at line 149 (`fp_text` font thickness in the wrong S-expression, exit 3). No reports were produced by those initial attempts.
- Removed unsupported UUID fields from the 33 embedded library pins in `hardware/FAC-IO-Mini-V1.kicad_sch`. Corrected the two terminal `fp_text` expressions in `hardware/FAC-IO-Mini-V1.kicad_pcb`. Both drafts now parse. A draft schematic netlist was exported to `validation-reports/schematic-draft.net` (export exit 0); it is a functional-block netlist, not a buildable circuit.
- Corrected D1/D2 PCB net assignments: pad 1 is the banded cathode side of KiCad's `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` footprint and is now on `12V_PROTECTED`; pad 2 is coil low. The onsemi 1N400x datasheet identifies the band as cathode. The PCB's manually copied DO-41 pad/drill sizes still differ from the installed library footprint and require part/footprint verification before layout.
- Executed `kicad-cli sch erc --severity-all --exit-code-violations -o validation-reports/schematic-erc.txt hardware/FAC-IO-Mini-V1.kicad_sch`: **exit 5, 53 violations** (3 undriven power pins, off-grid endpoints, isolated labels, missing custom symbol-library table). No ERC pass.
- Executed `kicad-cli pcb drc --severity-all --exit-code-violations --schematic-parity -o validation-reports/pcb-drc.txt hardware/FAC-IO-Mini-V1.kicad_pcb`: **exit 5, 15 DRC violations, 6 unconnected items, 18 schematic/PCB parity errors**. The 15 include 14 footprint-library configuration warnings and one silkscreen overlap; parity includes four missing schematic footprints and 14 extra PCB footprints. No DRC pass. KiCad without `--exit-code-violations` returns 0 even when violations exist; CI must use the flag or inspect the report.
- Verified AO3400A manufacturer datasheet's SOT-23 G/S/D arrangement against the PCB's Q1/Q2 pad 1/2/3 net intent. This is a pin-function check only; the manually copied footprint geometry and supply/transient design remain unvalidated.
- The separate experimental `relay-driver-v0.kicad_sch` initially did not parse. Removed nine unsupported embedded-pin UUIDs and corrected its custom MOSFET symbol to AO3400A/KiCad `Q_NMOS_GSD` pin numbers G=1, S=2, D=3. It now exports a netlist (exit 0), but ERC still reports 44 violations (exit 5, `validation-reports/relay-driver-erc.txt`); it is not integrated or electrically approved. `relay-contacts-v0.kicad_sch` produced 21 ERC violations (exit 5, `validation-reports/relay-contacts-erc.txt`).
- Updated `.github/workflows/kicad-pcb.yml` to use `--exit-code-violations`; previously a DRC report with violations could still return exit 0. Updated `.github/workflows/kicad-schematic.yml` to fail the job on ERC violations instead of printing a warning and allowing a green check. These workflow edits were checked locally for diff whitespace only; no GitHub Actions run has been observed.
- The barrier OPEN input's voltage/current and minimum contact load are unavailable. Added Omron `G6K-2P-Y DC12` as a low-level signal-relay candidate in `hardware/component-selection-v1.md`: manufacturer datasheet lists DPDT, 12 V/9.1 mA coil and 10 µA at 10 mV DC reference failure-rate load; installed KiCad has matching symbol/footprint names. Use one changeover pole per output. This is not a frozen BOM or validated barrier compatibility; the SONGLE candidate remains unapproved for unknown low-current loading.
- **Next action:** replace the functional-block schematic with one integrated, electrically complete schematic using exact sourced MPNs and manufacturer reference circuits. Prioritize relay/terminal minimum-load compatibility, input and USB power domains, ESP32-C3 boot-safe GPIOs, W5500 magnetics/RJ45 pairing, and watchdog/link-loss relay inhibit. Then regenerate the PCB from that schematic; do not complete the disconnected manual routing draft.

## Mission
Design and manufacture two assembled prototype PCBs for an Ethernet-connected, ESP32-C3 + W5500, two-channel dry-contact barrier controller. Integration: LPR/access software -> authenticated LAN command -> timed relay pulse (nominal 500 ms, configurable and bounded) -> barrier controller's low-voltage OPEN input. Never connect relay outputs directly to motor or mains.

## Source of truth
- `README.md`, `docs/requirements.md`, `docs/validation.md`: scope, acceptance and safety gates.
- `hardware/architecture.md`: power/Ethernet/relay architecture.
- `hardware/component-selection-v1.md`, `hardware/gpio-map-v0.md`, `hardware/design-review-v0.md`: candidate components, GPIOs, risks.
- `hardware/netlist-design-v0.csv`: textual connectivity proposal, NOT an exported CAD netlist.
- `hardware/FAC-IO-Mini-V1.kicad_sch`: block-level schematic draft, NOT a complete electrical schematic.
- `hardware/FAC-IO-Mini-V1.kicad_pcb`: partial manually edited PCB draft, NOT routed or schematic-synchronized.
- `hardware/relay-driver-v0.kicad_sch`, `hardware/relay-contacts-v0.kicad_sch`: separate experimental drafts, NOT integrated.
- `.github/workflows/kicad-pcb.yml`, `kicad-schematic.yml`: GitHub Actions KiCad checks; actual passing run NOT independently confirmed.
- `firmware/`: prototype/diagnostic scaffolding; do not assume production firmware.

## Verified progress vs unverified
DONE (repository content): 100x70 mm tentative PCB outline, four M3 mounting holes, R1-R4 resistor footprint drafts, Q1/Q2 MOSFET footprint drafts, D1/D2 diode footprint drafts, J_OUT1/J_OUT2 three-pin terminal footprint drafts; some provisional copper routes. Preliminary requirements, electrical architecture, GPIO allocation, test plan and CI workflow committed.
NOT DONE: actual integrated MCU, Ethernet, 3.3 V regulator, 12 V input protection, USB-C, relays, schematic-to-PCB sync, full routing, ERC/DRC PASS, verified MPNs, verified terminal footprint, Gerber/BOM/PnP manufacturing package, assembled prototype, hardware validation.
IMPORTANT: a GitHub commit is NOT a passed ERC/DRC. Previous assistant updates repeatedly claimed progress without verifying KiCad output. Do not repeat this.

## Critical risks requiring immediate review
1. **MOSFET SOT-23 pin mapping:** draft PCB Q1/Q2 uses pad 1=gate, pad 2=GND/source, pad 3=drain. Verify against chosen AO3400A datasheet and KiCad symbol; do not trust this mapping.
2. **Flyback diode polarity:** corrected draft PCB assignment maps D1/D2 pad 1 (banded cathode) to protected 12 V and pad 2 (anode) to coil low. No actual relay coil or protected rail is present; verify again after schematic-to-PCB synchronization.
3. **Partial gate traces:** check geometric clearance, pad attachment and potential shorts; manually generated PCB text has not been validated by KiCad.
4. **Contact terminal footprint** `FAC_DRAFT:Terminal_3_P5.08_UNVERIFIED` is provisional and not tied to a chosen manufacturer component.
5. **No relay footprints**: contact terminals currently have no actual electrical path to relay contacts.
6. **W5500** requires correct oscillator, PHY magnetics, center-tap, reset, power decoupling, ESD and matched RJ45.
7. **ESP32-C3** GPIO0/1 relay drive candidate, GPIO4–7 SPI/JTAG overlap, USB GPIO18/19, boot straps GPIO2/8/9. Validate actual module pinout and reset behavior.
8. **Power domains:** 12 V input, relay coils, buck 3.3 V, USB VBUS backfeed prevention and transient protection unresolved.
9. **Manufacturing:** PCB is explicitly NOT approved; no valid production Gerbers.
10. **Fail-safe behavior:** gate pulldowns only establish OFF when MCU pins are high-impedance. A crashed MCU can hold GPIO high; link loss does not inherently de-energize a relay. An independently reviewed watchdog/enable mechanism and timed pulse limit are required before claiming OFF on crash or network failure.

## Recent repo commits
- `9809b967`: changed flyback diode PCB net assignments (needs real footprint/symbol check).
- `ef8fb960`: PCB DRC CI fails on nonzero DRC result and uploads report.
- `e06d94ab`: schematic CI fails on parse/netlist errors and prints KiCad version.
- `dabe7067`: PCB CI installation timeout and CLI existence checks.
These commits are evidence of file changes, NOT evidence of passing CI.

## Local Mac environment / next AI agent
User installed **KiCad 10.0.8** using `brew install --cask kicad` on Apple Silicon macOS. Local shell access was confirmed in the audit above. A later agent must still verify its own execution environment and re-run checks after design changes.

Run:
```bash
kicad-cli version
git clone https://github.com/kemallaydn/FAC-IO-HARDWARE.git  # only if not already cloned
cd FAC-IO-HARDWARE
mkdir -p validation-reports
kicad-cli pcb drc --severity-all -o validation-reports/pcb-drc.txt hardware/FAC-IO-Mini-V1.kicad_pcb
kicad-cli sch erc --severity-all -o validation-reports/schematic-erc.txt hardware/FAC-IO-Mini-V1.kicad_sch
```
Use `--exit-code-violations` to make violations fail the command; add `--schematic-parity` for local PCB comparison. Capture stdout, stderr, exit code and reports. Do not suppress failures. KiCad 10 may migrate older KiCad format; preserve backups and make controlled changes.

## Priority execution sequence
P0: Establish repeatable local CLI and CI; capture REAL initial ERC/DRC reports, identify syntax errors and component pin/footprint mismatches. Fix bad CAD structure, avoid arbitrary trace additions.
P1: Choose exact purchasable MPNs and vendor reference circuits; document relay minimum dry-contact load, pinout, enclosure, connector pitches, power input range and thermal/current budget.
P2: Create ONE integrated KiCad project/schematic with ESP32-C3, W5500, magnetics RJ45, oscillator, 12V protections, buck, USB-C, 2 relay drivers and real relays/terminals. ERC zero errors, reviewed warnings.
P3: Update PCB from schematic, place verified footprints, enforce antenna keepout, isolate contact nets, route power/Ethernet/USB and all signals, proper return paths. DRC zero unwaived errors.
P4: Export fabrication and assembly outputs from SAME approved commit: Gerber, drill, BOM, position files, schematic PDF, assembly drawings; inspect in independent viewer; confirm Robotistan PCBA capabilities for THT parts.
P5: Order 2 prototypes; current-limited bench bring-up, power checks, USB flash, Ethernet tests, relay continuity, pulse/failsafe testing, then controlled barrier integration.

## Definition of done
A successful CI check alone does NOT mean ready to manufacture. Only mark ready after exact MPNs and pin mapping, ERC/DRC, independent design review, Gerber inspection, assembly confirmation and prototype test plan are documented. Keep `PROJECT_STATUS.md` updated after every meaningful work session with completed work, evidence (commit/command/report), blockers and next exact action. Never claim tests passed without logs.
