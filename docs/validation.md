# Verification and Manufacturing Gate

## Before layout
- [ ] Confirm exact ESP32-C3 module part number, pinout and strapping constraints.
- [ ] Confirm W5500 reference schematic, magnetics pinout and manufacturer layout guidance.
- [ ] Confirm relay part number, footprint, coil current and dry-contact rating.
- [ ] Verify 12 V input protection and power budget at both relays energized.
- [ ] Review USB programming/recovery and backfeed protections.
- [ ] Confirm chosen enclosure and terminal pitch.

## EDA checks
- [ ] KiCad schematic created with explicit electrical nets.
- [ ] ERC passes; all warnings reviewed and documented.
- [ ] PCB routed with continuous return paths and appropriate Ethernet routing.
- [ ] DRC passes; all warnings reviewed and documented.
- [ ] Gerber, Excellon drill, BOM and pick-and-place exported from **same tagged revision**.
- [ ] Independent Gerber viewer inspection of outline, drill, solder mask, polarity and labels.
- [ ] Assembly house confirms THT relay/RJ45/terminal population and component sourcing.

## First-article hardware test (bench supply, current limited)
1. Visual inspection for polarity, shorts, missing parts and solder bridges.
2. Power-up at nominal 12 V, record inrush and steady current, check 3.3 V rail and ripple.
3. Flash a diagnostic firmware; verify reset, USB recovery and brownout behavior.
4. Verify W5500 SPI communication, link negotiation, DHCP, TCP reconnect and long-run stability.
5. Exercise relay 1 and 2 with a continuity meter, **not connected to a real barrier**.
6. Verify NO/COM/NC mapping and pulse width under normal and abnormal reset conditions.
7. Verify power loss, reboot, watchdog, firmware crash and network disconnect never cause unintended pulses.
8. Test ESD/surge and environmental robustness appropriate to the installation.
9. Only then connect to a documented low-voltage barrier control input under supervision.

## Release artifacts
`hardware/*.kicad_sch`, `hardware/*.kicad_pcb`, `manufacturing/gerber/*.zip`, `manufacturing/bom/*.csv`, `manufacturing/position/*.csv`, revisioned test evidence.

**Status: planning only; none of the above checks have been executed.**
