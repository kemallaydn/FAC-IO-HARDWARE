# FAC-IO Lite V3 — active low-cost production architecture

Status: **V3 schematic and a routed two-layer PCB exist. Current ERC and error-level DRC/parity checks pass, but Ethernet pair routing, layout review, sourcing and assembly acceptance remain open. NOT production-ready.**

## Objective

Have Robotistan deliver one assembled Ethernet I/O card: connect low-voltage supply, Ethernet, and the barrier controller's labelled OPEN/CLOSE command pairs. The two outputs are isolated dry-contact relays. They never drive the barrier motor or mains.

## Selected architecture

- ESP32-C3-WROOM-02-N4 and W5500 directly on the same PCB. Preserve the existing firmware target and SPI interface.
- Populate the W5500 directly and use its matching WIZnet `J1B1211CCD` magnetic RJ45. Remove the plug-in WIZ850io module and its carrier sockets.
- Two independent dry-contact relay channels, OPEN and CLOSE, each with NO/COM/NC output terminals.
- One `CD74HC221M96` dual one-shot with separate RC networks to bound the two relay pulses in hardware. Outputs remain de-energized at reset and loss of power. Measure maximum pulse on the first article.
- Protected 12 V DC input and 3.3 V buck. Verify simultaneous ESP32, W5500 and relay load with power and thermal calculations.
- Remove USB-UART bridge and BOOT/RESET switches; retain accessible UART/BOOT/EN programming pads/header. Omit PoE and status LEDs in this cost-focused revision.
- Target a two-layer standard FR-4 board. This is a target, not a released stackup: routing, antenna keepout, Ethernet return path, contact isolation and fabricator capabilities must be checked against actual CAD.

## Ethernet implementation constraints from WIZnet

- Use WIZnet's W5500 RJ45-with-magnetics reference as the electrical source of truth. Do not mix the reference circuit for a different magjack or center-tap arrangement. The installed KiCad 10 library provides `Interface_Ethernet:W5500`, `Package_QFP:LQFP-48_7x7mm_P0.5mm`, and the board footprint `Connector_RJ:RJ45_Cetus_J1B1211CCD_Horizontal`.
- WIZnet explicitly requires C23/C24 to isolate the RX matching network from 3.3 V when using a magjack with connected center taps; omitting them can prevent proper W5500 operation. The exact selected J1B1211CCD revision and pin drawing must be reconciled against the reference before freezing those nets.
- Route TX/RX pairs short and matched, target 100 Ω differential, avoid vias/layer changes, keep other signal/power routing away, and leave all copper layers clear beneath the RJ45/magnetics. Keep the crystal close to the W5500. These constraints must be checked against the final board, not inferred from ERC.
- An official WIZnet Altium reference board was imported to `/tmp` only to inspect the layout approach. Its KiCad import reports 298 DRC violations, so it is not used as a manufacturing board or claimed as a clean reference implementation.

### MDI routing block found during V3 follow-up (2026-11-11)

- Fresh KiCad 10.0.8 error-only DRC with zone refill and schematic parity exits **0**, with 0 error-level violations, 0 unconnected pads and 0 parity problems. Full-severity reporting still returns **389 warnings**, all silkscreen overlap/clipping/edge-clearance issues; ERC exits 0 with 0 messages and four listed exclusions. Follow-up reports: `validation-reports/lite-v3-final-followup-erc.txt`, `validation-reports/lite-v3-final-followup-drc.txt`, and `.json`.
- The existing source PCB's MDI paths remain 39–59 mm and use 1–4 vias per conductor. They are not releasable under WIZnet's no-via/layer-change guidance. A trackless temporary layout shortened pad-center distances but did not yield a valid routed board.
- A pin-order sweep of all four cardinal orientations for the W5500 and J1B1211 footprint found no straight-through same-layer fanout in the currently fitting connector orientation. Other RJ45 orientations tested at the same candidate location collide with neighboring footprints, board edge, or copper. No pair-net polarity or TX/RX net mapping was changed; the datasheet confirms W5500 lacks Auto-MDIX and does not provide evidence to permit these changes.
- WIZnet's recommended J1B121ZCCD drawing has the same relevant MDI pad ordering/placement as J1B1211CCD; swapping to that variant alone does not fix the routing topology.
- A second temporary placement (U6 180°, J7 0°) let FreeRouting reduce 195 unrouted connections to 2, but KiCad DRC rejected it with 62 track-width errors (0.15 mm where the board minimum is 0.20 mm), 4 unconnected pads, and 1–3 vias per MDI net. Measured MDI paths were TXP 48.89 mm, TXN 39.63 mm, RXP_PHY 22.38 mm, RXN_PHY 29.87 mm, RXP_CABLE 35.96 mm, RXN_CABLE 21.53 mm. This is not a source-board change or production candidate; reports are in `validation-reports/lite-v3-orient-u180-j0-*`.
- U6 0° / J7 0° autorouting left 1 unrouted connection; DRC found 42 track-width errors, 4 unconnected pads, and 1–2 vias on each MDI pair. MDI lengths were TXP/TXN 52.49/34.60 mm, RX_PHY 18.25/20.42 mm, and RX_CABLE 23.83/21.53 mm. U6 90° / J7 0° was worse at 15 unrouted connections. Both placements were rejected and remain temporary; reports are in `validation-reports/lite-v3-orient-u0-j0-*`.
- Next engineering step is a new Ethernet-region placement with a physically verified magjack orientation/footprint and complete MDI route measurement. If a route meeting the WIZnet constraints cannot fit within the 110 x 77 mm 2-layer board, compare the existing WIZ850io-based 4-layer V1 route and PCBA sourcing gates before deciding the manufacturing path. No production files may be exported from the present V3 source.

## Why this route

Robotistan currently lists WT32-ETH01 as sold out. WT32 would also move away from the existing ESP32-C3 + SPI-W5500 firmware target. Robotistan's ESP32-C3 Mini development board is also shown as sold out; use the production ESP32-C3-WROOM-02-N4 module instead. Current LCSC catalogue pages show sourcing candidates for the ESP32-C3 module (C2934560), W5500 (C32843), WIZnet magnetic RJ45 (C910371), and dual one-shot (C133954). These are live-catalog observations, not a Robotistan purchase quote or guaranteed future stock. Confirm codes and availability in RobotistanPro before ordering.

Putting W5500 and the matched magjack on the PCB removes the WIZ850io module premium and preserves the firmware hardware interface. Ethernet pair/center-tap routing must follow WIZnet's reference circuit and the selected jack's manufacturer drawing; it must not be guessed.

## Release gates

1. Match W5500 PHY and center-tap circuitry to the official WIZnet reference schematic and the exact J1B1211CCD revision drawing.
2. Verify every BOM C code, MPN, package, stock and Robotistan PCBA procurement acceptance. Use substitutes only after electrical and mechanical verification.
3. Create complete KiCad schematic and pass ERC; route the two-layer PCB and pass DRC, schematic parity and CAM checks; export Robotistan BOM and Pick & Place with exact reference/count/footprint matching.
4. Obtain independent electrical/layout review and fabricator/Robotistan CAM and assembly acceptance.
5. First article: 12 V power corners and thermal behavior, reset/brownout, firmware programming, Ethernet/DHCP, power-loss fail-off, both relay channels and maximum pulse. Then test on the actual barrier command input.

Architecture selection is not production approval. No Gerber, BOM or Pick & Place is approved until these gates have evidence.

## Current CAD progress (2026-11-11)

- V3 contains ESP32-C3-WROOM-02-N4 + W5500 + J1B1211CCD, relay/power circuits and two-layer routed PCB. W5500 pin 18 VBG is NC per the official datasheet; the previously drawn 10 nF C100 was removed from schematic and PCB.
- KiCad 10.0.8 ERC: **0 violations**. Zone-refilled DRC plus schematic parity: **0 error-level violations, 0 unconnected pads, 0 parity problems**. Full DRC has 389 silkscreen warnings; footprint-value/reference placement needs cleanup.
- Ethernet routes are not released: current pair segments measure TXP 59.19 mm/3 vias, TXN 49.11 mm/3 vias, RXP_PHY 39.48 mm/4 vias, RXN_PHY 40.41 mm/4 vias, RXP_CABLE 42.33 mm/1 via, RXN_CABLE 36.79 mm/1 via. WIZnet specifies 100 Ω differential impedance, recommends under 25 mm (75 mm worst case), requires equal TX+/− and RX+/− lengths, and prohibits vias/layer changes on MDI traces. The current board violates these layout constraints. A later placement-only candidate at U6 `(191,133,270°)` / J7 `(188,108,0°)` reduced MDI pad-center distances to TXP 21.49 mm, TXN 21.08 mm, RXP 23.38 mm, RXN 23.52 mm; courtyard, copper-short and clearance violations were zero after moving the local passive cluster. This is not a routed-board result: the tracks were removed for the placement test, C32/C33 still require a library-synchronized compact footprint, and the candidate remains in `/tmp`, not on the V3 source board.
- The current netlist contains 71 physical line items; 20 have blank MPN fields. (An earlier count of 25 also included five non-physical `PWR_FLAG` symbols.) Exact MPN/catalog mapping for all BOM rows, stock confirmation and Robotistan PCBA import/acceptance are incomplete. Controlled-impedance stack-up and actual fabricator capability also remain unverified.
- No Gerber, Excellon, assembly BOM or Pick & Place is approved/exported. The board must not be ordered until MDI placement/routing, silkscreen and independent CAM/assembly review pass. Then verify first-article power, boot, Ethernet, reset/power-loss fail-off and relay pulse/contact behavior.

## Sources

- Robotistan WT32-ETH01: https://www.robotistan.com/wt32-eth01-ethernet-modul
- Robotistan ESP32-C3 Mini: https://www.robotistan.com/esp32-c3-mini-wifi-bluetooth-modul
- Robotistan PCB/PCBA service: https://www.robotistan.com/pcb-servisi
- WIZnet W5500 reference circuit: https://docs.wiznet.io/Product/Chip/Ethernet/W5500/ref-schematic
- WIZnet W5500 PCB design guide: https://docs.wiznet.io/Design-Guide/hardware_design_guide
- WIZnet W5500 RJ45/magnetics reference PDF: https://docs.wiznet.io/img/products/w5500/w5500_sch_v110_use_mag_.pdf
- LCSC W5500 C32843: https://www.lcsc.com/product-detail/C32843.html
- LCSC ESP32-C3-WROOM-02-N4 C2934560: https://www.lcsc.com/product-detail/C2934560.html
- LCSC WIZnet J1B1211CCD C910371: https://www.lcsc.com/product-detail/C910371.html
- LCSC TI CD74HC221M96 C133954: https://www.lcsc.com/product-detail/C133954.html
