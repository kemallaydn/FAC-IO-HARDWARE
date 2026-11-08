# FAC-IO Mini V1: Electrical architecture (pre-schematic)

**Status: design specification only. Block-level/experimental KiCad drafts exist, but there is no integrated electrical schematic, complete routed PCB or approved Gerber. See `PROJECT_STATUS.md` for actual KiCad check results.**

## Power tree
12V_IN -> resettable fuse / protection -> reverse polarity protection -> TVS -> protected 12V rail.
Protected 12V -> relay coils (if 12V coil MPN chosen).
Protected 12V -> 3.3V switching regulator -> ESP32-C3 + W5500 + Ethernet PHY support.
Include regulator headroom for ESP32 radio startup even if Wi-Fi is disabled. Power from USB must not backfeed 12V or relay supply. The USB power/data scheme must be chosen and checked against the actual module design.

## Ethernet
ESP32-C3 SPI <-> W5500 <-> matched Ethernet magnetics <-> RJ45.
Use WIZnet reference hardware design, not a generic unmagnetized RJ45. Verify W5500 reference voltage, oscillator/crystal, reset, decoupling, SPI signal integrity, center taps, chassis/shield and ESD from datasheets.

## Relay output, repeated twice
MCU GPIO -> gate resistor -> low-side MOSFET -> relay coil -> protected 12V.
Flyback diode across coil. MOSFET gate pulldown ensures OFF while MCU is in reset or unprogrammed.
Contacts brought to isolated NO/COM/NC terminal block. No shared contact supply. Keep coil traces separate from contact terminals. Contact ratings must match the intended barrier controller input and environmental conditions. **No mains or motor loads.**

## Programming and recovery
ESP32-C3 USB Serial/JTAG capability may be used after checking exact module pins, USB-C D+/D- routing, CC resistors, ESD and BOOT/reset requirements. Keep accessible recovery pads. Security fuses must remain unset during first-article bring-up.

## Indicative logical signals (NOT pin assignments)
W5500: SPI_SCK, SPI_MOSI, SPI_MISO, SPI_CS, ETH_INT, ETH_RESET.
Relays: RELAY1_EN, RELAY2_EN.
Status: LED_PWR, LED_NET (may derive from W5500 LINK), optional LED_R1, LED_R2 (may derive from relay drive).
USB: USB_DP, USB_DM.
Programming: EN, BOOT strap, GND, 3V3.
**GPIO allocation is a blocking design task**: check ESP32-C3 strapping, USB pins, SPI peripherals and startup behavior before assigning GPIOs. Never connect relay gates to strapping pins without proving reset-safe levels.

## Mechanical
Two independent 3-way screw terminals, 2-way power terminal, RJ45, USB-C, four mounting holes. Reserve keepout around module antenna even if Wi-Fi disabled. Design to fit a selected DIN-rail enclosure.

## Open blockers
1. Exact relay MPN, footprint, coil current and contact ratings.
2. Exact ESP32-C3 module MPN, GPIO allocation and antenna keepout.
3. Exact W5500 reference design and RJ45 magnetics part/footprint.
4. Regulator, fuse, reverse polarity, TVS and USB power arrangement.
5. Enclosure dimensions and terminal block placement.
6. ESD, EMC, isolation/creepage and production-test fixture requirements.

No manufacturing release until these are resolved and independent schematic/PCB review is complete.
