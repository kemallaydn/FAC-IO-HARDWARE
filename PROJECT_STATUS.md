# FAC-IO Mini V1 — PROJECT STATUS / AI HANDOFF
Last reviewed: 2026-11-07. Branch: main.
**Status: ENGINEERING DRAFT / NOT PRODUCTION READY.** This file is the primary continuity checkpoint for any new AI agent.

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
2. **Flyback diode polarity:** latest PCB net assignment maps D1/D2 pad 1 to coil low and pad 2 to protected 12 V. Confirm actual DO-41 footprint pin numbering/cathode marking and diode symbol orientation before routing. Prior version was reversed.
3. **Partial gate traces:** check geometric clearance, pad attachment and potential shorts; manually generated PCB text has not been validated by KiCad.
4. **Contact terminal footprint** `FAC_DRAFT:Terminal_3_P5.08_UNVERIFIED` is provisional and not tied to a chosen manufacturer component.
5. **No relay footprints**: contact terminals currently have no actual electrical path to relay contacts.
6. **W5500** requires correct oscillator, PHY magnetics, center-tap, reset, power decoupling, ESD and matched RJ45.
7. **ESP32-C3** GPIO0/1 relay drive candidate, GPIO4–7 SPI/JTAG overlap, USB GPIO18/19, boot straps GPIO2/8/9. Validate actual module pinout and reset behavior.
8. **Power domains:** 12 V input, relay coils, buck 3.3 V, USB VBUS backfeed prevention and transient protection unresolved.
9. **Manufacturing:** PCB is explicitly NOT approved; no valid production Gerbers.

## Recent repo commits
- `9809b967`: changed flyback diode PCB net assignments (needs real footprint/symbol check).
- `ef8fb960`: PCB DRC CI fails on nonzero DRC result and uploads report.
- `e06d94ab`: schematic CI fails on parse/netlist errors and prints KiCad version.
- `dabe7067`: PCB CI installation timeout and CLI existence checks.
These commits are evidence of file changes, NOT evidence of passing CI.

## Local Mac environment / next AI agent
User installed **KiCad 10.0.8** successfully using `brew install --cask kicad` on Apple Silicon macOS. Homebrew linked `kicad-cli` to `/opt/homebrew/bin/kicad-cli`. New AI working locally may use the actual filesystem, terminal and KiCad CLI; this ChatGPT GitHub connector alone cannot execute commands on user's Mac. First confirm CLI version and repo checkout; don't assume this agent can access local machine unless local execution tools exist.

Run:
```bash
kicad-cli version
git clone https://github.com/kemallaydn/FAC-IO-HARDWARE.git  # only if not already cloned
cd FAC-IO-HARDWARE
mkdir -p validation-reports
kicad-cli pcb drc --severity-all -o validation-reports/pcb-drc.txt hardware/FAC-IO-Mini-V1.kicad_pcb
kicad-cli sch erc --severity-all -o validation-reports/schematic-erc.txt hardware/FAC-IO-Mini-V1.kicad_sch
```
Expect errors and/or syntax incompatibilities. Capture stdout, stderr, exit code and reports. Do not suppress failures. KiCad 10 may migrate older KiCad format; preserve backups, commit controlled changes.

## Priority execution sequence
P0: Establish repeatable local CLI and CI; capture REAL initial ERC/DRC reports, identify syntax errors and component pin/footprint mismatches. Fix bad CAD structure, avoid arbitrary trace additions.
P1: Choose exact purchasable MPNs and vendor reference circuits; document relay minimum dry-contact load, pinout, enclosure, connector pitches, power input range and thermal/current budget.
P2: Create ONE integrated KiCad project/schematic with ESP32-C3, W5500, magnetics RJ45, oscillator, 12V protections, buck, USB-C, 2 relay drivers and real relays/terminals. ERC zero errors, reviewed warnings.
P3: Update PCB from schematic, place verified footprints, enforce antenna keepout, isolate contact nets, route power/Ethernet/USB and all signals, proper return paths. DRC zero unwaived errors.
P4: Export fabrication and assembly outputs from SAME approved commit: Gerber, drill, BOM, position files, schematic PDF, assembly drawings; inspect in independent viewer; confirm Robotistan PCBA capabilities for THT parts.
P5: Order 2 prototypes; current-limited bench bring-up, power checks, USB flash, Ethernet tests, relay continuity, pulse/failsafe testing, then controlled barrier integration.

## Definition of done
A successful CI check alone does NOT mean ready to manufacture. Only mark ready after exact MPNs and pin mapping, ERC/DRC, independent design review, Gerber inspection, assembly confirmation and prototype test plan are documented. Keep `PROJECT_STATUS.md` updated after every meaningful work session with completed work, evidence (commit/command/report), blockers and next exact action. Never claim tests passed without logs.
