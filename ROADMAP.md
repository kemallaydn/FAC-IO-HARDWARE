# FAC-IO Mini V1 — Roadmap

Status is evidence-based. Passing CAD checks alone is not a production release.

| Phase | Current state | Evidence / exit criteria still needed |
|---|---|---|
| M0 Audit | Complete for current checkout | KiCad 10.0.8 CLI reports saved; current ERC/DRC/parity results in `PROJECT_STATUS.md`. |
| M1 Electrical freeze | Incomplete | Confirm actual 12 V source/environment; close hot PTC and buck thermal/current margin; verify procurement availability, pin/footprints and independent safety review. Screening budget is recorded in `hardware/component-selection-v1.md`, but its assumptions are not a design sign-off. |
| M2 Integrated schematic | CAD complete; electrical approval open | Integrated schematic/netlist and ERC pass; component suitability/startup behavior still need engineering review. |
| M3 Routed PCB | DRAFT-1.2 CAD rule gate passes; physical/layout review open | DRC/parity pass with footprint-filter checks enabled and no ignored PCB DRC checks; protected-input width rule and static GPIO map pass. Confirm carrier stackup, power/return paths, module/enclosure fit and independent review. |
| M4 Manufacturing | Current-source DRAFT review bundle staged | `manufacturing/REVIEW-2026-11-10-DRAFT/` includes fresh Gerbers/Excellon and current ERC/DRC evidence. Its release gate is blocked only on independent approval; fabricator CAM/stackup, slot acceptance and Robotistan acceptance are still open. The Gerbonara G90 warning is explained by the conventional Excellon body command and structurally cross-checked. PCBA sourcing/BOM and assembly require separate checks. |
| M5 Bring-up | Not started | Assemble prototype and record current-limited 12 V, 3.3 V, USB, Ethernet, relay, pulse-width and fault tests. |
| M6 Firmware/integration | Development target builds; not production-ready | `firmware/src/main.cpp` wires bounded HTTP parsing, mbedTLS HMAC-SHA256, physical USB key provisioning/rotation, persistent 256-sequence reservations and fixed OPEN/CLOSE GPIO pulses with a shared 600 ms guard. `firmware/tools/facio_client.py` signs/sends commands and keeps private local sequence state; host tests pass. The ESP32-C3 PlatformIO development build passes. The command server fails closed unless link/DHCP, Secure Boot, flash encryption, NVS and a per-device key are available. Signed production-security build, target/board test, crash fail-off and LPR integration remain open. |

## Engineering scope

V1: ESP32-C3-WROOM-02-N4 + plug-in WIZnet WIZ850io; 12 V protected input and 3.3 V buck; USB-C debug; two isolated SPDT signal relays with NO/COM/NC terminals. WIZ850io contains W5500, PHY, transformer/magnetics and RJ45. No PoE, RS485, or direct motor/mains switching.

## Immediate next actions

1. Confirm the field 12 V supply tolerance and maximum enclosure ambient; close the PTC, buck loss/temperature and effective input-capacitance calculations against those conditions.
2. Freeze orderable sources/stock and assembly process for the 56 board references and external WIZ850io; verify terminal and socket footprints against physical samples.
3. Obtain independent electrical/CAM review and Robotistan stackup, drill/slot, THT/SMT and sourcing acceptance for `manufacturing/REVIEW-2026-11-10-DRAFT/`.
4. Build a first article and complete the validation matrix. Until these gates pass, the board is not production-ready.
