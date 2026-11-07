# FAC-IO Mini V1 — Ethernet Barrier Relay Controller

Status: **Hardware requirements / architecture draft. NOT production-ready.**

FAC-IO is an Ethernet-connected, programmable dry-contact relay controller for integration with our own license-plate recognition/access-control software. It is **not** a barrier motor driver.

## V1 scope
- ESP32-C3 module (exact ordering code TBD after GPIO and USB review)
- W5500 SPI 10/100 Ethernet + magnetics-equipped RJ45
- 2 independent, normally-open / common / normally-closed dry-contact relay outputs
- 12 V DC input, regulated 3.3 V logic supply
- USB programming/debug interface, BOOT/RESET recovery access
- Power, link and relay indicators; four mounting holes
- DHCP with configurable static IP; authenticated device discovery and relay control in our own firmware
- Relays default **OFF** during power-up, brownout, watchdog reset, firmware update and Ethernet loss
- Optional future PoE; **not included** in V1
- RS232, RS485 and legacy Nöron protocol **not required** in V1

## System flow
LPR service -> authenticated LAN command -> FAC-IO -> timed dry-contact closure -> barrier controller OPEN input.

The dry-contact output must be wired only to the barrier controller's documented command input, **never directly to the motor or mains**. Pulse duration is firmware-configurable and must have a hardware/software maximum.

## Repository layout
- `docs/requirements.md`: engineering requirements and open decisions
- `docs/validation.md`: verification and acceptance plan
- `hardware/`: future KiCad schematic, board and libraries
- `manufacturing/`: future Gerber, Excellon, BOM and position files
- `firmware/`: firmware project (not yet implemented)

## Manufacturing release rule
Do not order PCB/PCBA until actual KiCad schematic and routed board exist, ERC/DRC pass with documented exceptions, all exact MPNs/footprints are verified against datasheets, and a human engineer reviews power, isolation, relay safety, Ethernet signal integrity and assembly. **There are currently no valid production Gerbers in this repository.**
