# FAC-IO Mini V1 — Roadmap
Status: planned; milestone completion must be backed by reports and commits.

| Phase | Deliverable | Acceptance |
|---|---|---|
| M0 Audit | KiCad 10 local and CI validation baseline | Saved ERC/DRC reports and actionable issue list |
| M1 Electrical freeze | Exact MPNs, datasheets, power budget, GPIO and safety review | Approved component matrix and schematic architecture |
| M2 Integrated schematic | One complete KiCad schematic and libraries | Netlist export, ERC zero errors, reviewed warnings |
| M3 Routed PCB | Real footprints, placements, 100x70 mm envelope re-evaluated, routed copper | DRC zero unwaived errors, schematic-to-PCB match |
| M4 Manufacturing | Gerber, Excellon, BOM, PnP, assembly drawing, revision tag | Independent review and PCBA supplier sign-off |
| M5 Bring-up | 2 assembled prototypes and test logs | 12V/3.3V, USB, Ethernet, 2 independent dry-contact outputs and failsafe tests |
| M6 Firmware/integration | Authenticated LAN commands, 500ms bounded pulses, secure provisioning | End-to-end LPR -> command -> pulse tested; reset/loss-of-link safe |

## Engineering scope
V1: ESP32-C3-WROOM-02-N4 candidate, W5500 SPI 10/100 Ethernet, RJ45 magnetics, 12 V input and protected 3.3 V buck, USB-C debug, two independent SPDT 12 V coil relays, NO/COM/NC terminals, diagnostics and fail-safe firmware.
Out of scope: PoE, RS485, direct motor/mains switching.

## Blocking decisions
Exact relay and terminal MPNs, Ethernet RJ45 magnetics, regulator and protections, ESP32 pin mapping, enclosure, USB power-domain behavior, sourcing/assembly constraints. Do not silently mark them resolved.

## Immediate next step
On the user's local Mac, run `kicad-cli version`, then initial `pcb drc` and `sch erc` with report files. Fix actual parse/netlist/pin-mapping errors first. Update `PROJECT_STATUS.md` with command output and evidence.
