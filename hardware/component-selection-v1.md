# Component selection gate — FAC-IO Mini V1

Status: **datasheet review; not yet released for fabrication**.

## MCU
Candidate **ESP32-C3-WROOM-02-N4** (4 MB flash, PCB antenna) or **ESP32-C3-WROOM-02U-N4** (external antenna). Prefer -02-N4 for prototype only if enclosure placement respects antenna keepout. Espressif datasheet identifies 15 GPIO, 160 MHz single-core CPU, 4 MB N4 / 8 MB N8 variants, USB Serial/JTAG and strapping GPIO2/8/9.

Datasheet: https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html
Chip: https://documentation.espressif.com/esp32-c3_datasheet_en.html

**Important caveat**: provisional SPI GPIO4–7 also have JTAG alternate functions. Verify debug requirements, reset levels and pin multiplexing before freezing layout. GPIO18/19 are USB D-/D+ and GPIO20/21 default UART0. Do not assume all chip pins are available on module.

## Ethernet
W5500 SPI Ethernet controller, with a compatible magnetics-equipped RJ45. WIZnet specifically notes that integrated magnetics with connected center taps can require extra isolation capacitors (C23/C24 in their example); choose an exact RJ45 part number before copying matching network.

Reference: https://docs.wiznet.io/Product/Chip/Ethernet/W5500/ref-schematic
Layout: https://docs.wiznet.io/Design-Guide/hardware_design_guide

**Do not** use a bare RJ45 without magnetics. Verify ESD, magnetics orientation, RX/TX polarity, 25 MHz crystal, reset timing, termination, decoupling and PCB trace routing.

## Relays
Two SPDT **12 V coil** relays, each with NO/COM/NC terminals, controlled by independent MOSFET low-side drivers with pulldowns and flyback suppression. **Exact manufacturer part number not selected**: choose based on dry-contact switching at the barrier controller's actual control input. Avoid claiming high-current AC rating is necessary or that a contact is suitable for very low-current dry switching without datasheet verification.

## Power
Nominal 12 V input, reverse-polarity protection, surge suppression, input overcurrent protection, 3.3 V switching regulator and local bypass. Exact protection/regulator MPNs and input voltage range remain open. Two relay coils may be energized simultaneously; budget accordingly.

## USB
USB-C receptacle for ESP32-C3 native USB Serial/JTAG; requires correct USB 2.0 wiring, CC pull-downs, ESD and protection against backfeeding supply. Verify behavior with only USB attached versus external 12 V present.

## Schematic freeze criteria
- Exact manufacturer part numbers + verified footprints for MCU, W5500, RJ45, relays, terminals, buck, USB-C and protections.
- Power budget and voltage/current/thermal calculations.
- Final GPIO pin map including bootstraps, USB and JTAG.
- Startup-safe relay drive verified independently of firmware.
- Review against vendor reference designs and first-article test requirements.
