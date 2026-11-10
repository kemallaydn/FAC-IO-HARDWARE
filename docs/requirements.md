# FAC-IO Mini V1 — Hardware Requirements (draft)

## Functional
1. Two independent changeover relay outputs, each exposing NO, COM, NC on labelled screw terminals.
2. Ethernet interface using ESP32-C3 + W5500 over SPI. Current CAD uses WIZ850io, which integrates the W5500, PHY, magnetics and RJ45.
3. External 12 V DC supply with reverse-polarity, overcurrent and transient protection; regulated logic rail.
4. Programming/recovery access without opening a sealed production enclosure if possible.
5. Firmware shall support DHCP, static IP, authenticated discovery, authenticated command channel, status reporting, and signed updates where supported. Each relay command triggers the fixed hardware one-shot (about 503 ms nominal with current values); firmware must not accept a caller-selected duration. Verify worst-case maximum pulse on the first article.
6. Each relay shall be inactive by default with MCU reset/boot pins floating, firmware crash, loss of supply or watchdog reset.
   OPEN and CLOSE commands shall be serialized; the controller must reject the opposite command during the shared hardware-pulse re-arm interval.
7. Clear silk labels for power polarity, network, relay terminals and board revision.
8. No PoE, RS232 or RS485 in V1.

## Electrical design decisions to finalize BEFORE schematic freeze
- Relay contacts close only the barrier controller's isolated command pairs. Hikvision 42-Series documentation names these **Rising Control ±** and **Falling Control ±**; it does not establish fixed terminal numbers or minimum contact-load specifications. Hikvision warns that CLOSE/Falling accepts pulsed signals only and a continuous signal can lock the barrier. Verify labels on the exact installed controller and measure compatibility before connection; never connect this card to mains, motor or traffic-light outputs. ([Hikvision 42-Series brochure](https://www.hikvision.com/content/dam/hikvision/en/brochures-download/product-brochures/Leaflet--Barrier-Gate-42-Series.pdf))
- Relay coil voltage and maximum simultaneous current draw, including inrush and regulator margin.
- DC input allowable range (nominal 12 V; tolerance TBD), supply polarity and terminal type.
- MCU exact module variant, available GPIO and boot-strapping pin conflicts with W5500 SPI, 2 relay drivers, indicators and USB.
- USB-C implementation: USB data pins, CC resistors, ESD, connector orientation and power-domain/backfeed isolation.
- WIZ850io host pin mapping, module current/rail margin, reset timing, SPI timing and mating connector/mechanical fit.
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
