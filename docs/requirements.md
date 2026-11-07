# FAC-IO Mini V1 — Hardware Requirements (draft)

## Functional
1. Two independent changeover relay outputs, each exposing NO, COM, NC on labelled screw terminals.
2. Ethernet interface using ESP32-C3 + W5500 over SPI; RJ45 with correct integrated magnetics or external magnetics.
3. External 12 V DC supply with reverse-polarity, overcurrent and transient protection; regulated logic rail.
4. Programming/recovery access without opening a sealed production enclosure if possible.
5. Firmware shall support DHCP, static IP, authenticated discovery, authenticated command channel, pulse output, status reporting, and signed updates where supported.
6. Each relay shall be inactive by default with MCU reset/boot pins floating, firmware crash, loss of supply or watchdog reset.
7. Clear silk labels for power polarity, network, relay terminals and board revision.
8. No PoE, RS232 or RS485 in V1.

## Electrical design decisions to finalize BEFORE schematic freeze
- Relay contact rating **for barrier controller low-voltage dry-contact input**, not an assumed mains/motor load; exact relay MPN and contact material to be verified.
- Relay coil voltage and maximum simultaneous current draw, including inrush and regulator margin.
- DC input allowable range (nominal 12 V; tolerance TBD), supply polarity and terminal type.
- MCU exact module variant, available GPIO and boot-strapping pin conflicts with W5500 SPI, 2 relay drivers, indicators and USB.
- USB-C implementation: USB data pins, CC resistors, ESD, connector orientation and power-domain/backfeed isolation.
- W5500 clock, reset, SPI timing, power decoupling, magnetics, RJ45 shield and ESD layout per reference design.
- Relay drivers (transistor/MOSFET, gate/base bias, flyback), reset-safe default OFF, contact isolation/clearance.
- Enclosure and DIN-rail mounting envelope; connector accessibility.
- Optional input feedback? **Not in current scope**; add only after explicit requirements.

## Non-goals
- Driving barrier motors or mains loads directly.
- Emulating Nöron discovery or proprietary configuration utilities.
- PoE power.
- Guaranteeing safety of an untested first-spin PCB.

## Security
A relay-opening endpoint must not be accessible unauthenticated on a shared network. Device pairing, per-device credentials, replay prevention, key provisioning and recovery should be designed before field deployment. Secure boot / flash encryption depend on exact chip and production provisioning and must be validated before enabling irreversible eFuses.
