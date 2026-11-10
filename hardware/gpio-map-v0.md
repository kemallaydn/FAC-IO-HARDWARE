# ESP32-C3 GPIO map — current schematic assignment

**As-designed in `hardware/FAC-IO-Mini-V1.kicad_sch`; not firmware-frozen or bench-verified.** The WIZ850io uses the W5500 SPI host interface. Relay coils are not driven directly from ESP32 pins: the MCU triggers a dual monostable pulse-limiter, then independent MOSFET coil drivers.

| Net / function | GPIO | Module symbol pin | Notes |
|---|---:|---:|---|
| ETH_SCK | 4 | 3 | WIZ850io J6.4 |
| ETH_MOSI | 5 | 4 | WIZ850io J6.3 |
| ETH_MISO | 6 | 5 | WIZ850io J7.6 |
| ETH_CS_N | 7 | 6 | 10 kΩ pull-up to 3V3; WIZ850io J6.5 |
| ETH_INT_N | 10 | 10 | 10 kΩ pull-up to 3V3; WIZ850io J6.6 |
| ETH_RESET_N | 3 | 15 | 10 kΩ pull-up to 3V3; WIZ850io J7.5 |
| TRIG1 | 0 | 18 | One-shot input for relay channel 1; 100 kΩ pulldown |
| TRIG2 | 1 | 17 | One-shot input for relay channel 2; 100 kΩ pulldown |
| Unused | — | 11 | GPIO20 / IO20 is not connected in current schematic; timer arm net removed |
| USB_DM | 18 | 13 | USB-C D- path through series resistor/ESD |
| USB_DP | 19 | 14 | USB-C D+ path through series resistor/ESD |
| USB_VBUS_SENSE | 21 | 12 | USB VBUS sense through resistor divider |
| BOOT_N | 9 | 8 | BOOT switch; ESP32-C3 strapping function |
| ESP_EN | — | 2 | Reset enable network and switch |
| GPIO2 / GPIO8 | — | 16 / 7 | Not connected in current schematic |

Netlist checked with KiCad 10.0.8. ESP32-C3 GPIO4-7 also have JTAG alternate functions; debug/JTAG use must be handled in firmware. GPIO20/21 alternate UART functions are also available on the module; GPIO20 is currently unused and GPIO21 is USB VBUS sense. U5/U6 one-shot reset/startup behavior and trigger levels require scope verification on the first article; do not infer relay-off safety from the static netlist alone.
