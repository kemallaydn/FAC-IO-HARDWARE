# ESP32-C3 GPIO allocation — candidate v0.1

**PROVISIONAL: Not electrically verified. Do not route or fabricate using this table without reviewing the exact ESP32-C3 module datasheet and reset/boot behavior.**

Assumed module: ESP32-C3-WROOM-02 family (exact flash size and antenna variant TBD). W5500 uses the ESP32-C3 GPIO matrix for SPI. This proposal deliberately reserves USB GPIO18/19 and boot strapping GPIO2/8/9.

| Net | Candidate GPIO | Notes |
|---|---:|---|
| W5500_SPI_SCK | 4 | SPI clock |
| W5500_SPI_MOSI | 5 | SPI TX |
| W5500_SPI_MISO | 6 | SPI RX |
| W5500_SPI_CS_N | 7 | Active-low chip select, default pull-up |
| W5500_INT_N | 10 | Input, active-low interrupt |
| W5500_RESET_N | 3 | Output, reset network chip |
| RELAY1_GATE | 0 | External strong gate pulldown; relay OFF in reset |
| RELAY2_GATE | 1 | External strong gate pulldown; relay OFF in reset |
| USB_D- | 18 | Native USB Serial/JTAG, verify module pinout |
| USB_D+ | 19 | Native USB Serial/JTAG, verify module pinout |
| STATUS_LED | 20 | Optional, check UART0 alternate function / boot logs |
| SPARE | 21 | Reserved, check UART0 alternate function |
| BOOT_STRAP | 2, 8, 9 | Reserved for strapping and recovery; do not drive relays |
| FLASH_RESERVED | 12–17 | Used internally by flash/module; do not assign |

## Review gates
1. Verify **every** GPIO is exposed on the selected module footprint and that its boot/reset state is safe.
2. Confirm relay gate pins GPIO0/1 do not emit unintended pulses during reset, bootloader, USB enumeration or crash. Scope both signals with relays disconnected.
3. Check W5500 SPI frequency and whether GPIO4–7 routing is feasible with antenna keepout.
4. Validate USB-JTAG recovery and GPIO9 BOOT procedure.
5. Confirm external W5500 reset defaults asserted during MCU startup, and CS remains deselected.
6. Review watchdog/brownout handling: relay hardware must default OFF independently of firmware.
7. Any GPIO change must update schematic, firmware pin map and test plan together.

This allocation is a **candidate**, not an approved pinout.
