# FAC-IO Lite V2 — WT32 pin/net map (draft)

Status: **candidate mapping, not footprint-, schematic- or firmware-frozen**.

The pin names follow the Wireless-Tag WT32-ETH01 manufacturer datasheet. The datasheet numbers the 20-pin main interface and 6-pin debug interface independently. The KiCad symbol now uses one **candidate physical pad numbering** across 26 pads, based on the interface order and a community KiCad pattern; this resolves the previous mistaken assumption that main pins were physical pads 1–20. The manufacturer does not publish a dimensioned land pattern. Confirm the numbering, row spacing, drill size, module revision and Ethernet-jack outline against the exact purchased sample before PCB fabrication.

| Candidate physical pad | Signal | Interface |
|---:|---|---|
| 1–3 | EN, GND, 3V3 | Debug |
| 4–14 | EN, IO32/CFG, IO33/485_EN, IO5/RXD, IO17/TXD, GND, 3V3, GND, 5V, LINK, GND | Main |
| 15–23 | IO2, IO4, IO35, IO12, IO14, IO15, IO36, IO39, GND | Main |
| 24–26 | IO0, IO3/RXD0, IO1/TXD0 | Debug |

Pad numbering/sequence reference: [community KiCad symbol and footprint](https://github.com/egnor/wt32-eth01); it is not a manufacturer mechanical drawing. Product revisions have been reported, so use it only as a candidate until checked against the sample. Manufacturer reference: [WT32-ETH01 datasheet](https://www.mouser.com/datasheet/2/744/WT32_ETH01_datasheet_V1_1__en-2487862.pdf).

| Candidate pad | Module signal | Board net | Intended use |
|---|---|---|
| 5 | CFG / IO32 | OPEN_TRIGGER | OPEN channel trigger |
| 6 | 485_EN / IO33 | CLOSE_TRIGGER | CLOSE channel trigger |
| 1, 4 | EN | WT32_EN | Reset/program enable |
| 26 | TXD / IO1 | UART_TX | Firmware programming TX |
| 25 | RXD / IO3 | UART_RX | Firmware programming RX |
| 24 | IO0 | BOOT_N | Bootloader selection |
| 3, 10 | 3V3 | 3V3 | Module supply; choose only this rail or 5V |
| 2, 9, 11, 14, 23 | GND | GND | Common low-voltage ground |

All Ethernet PHY GPIOs remain reserved inside the WT32 module. IO2, IO12, IO15 have boot-strapping concerns; IO35/36/39 are input-only; they are left unused. OPEN/CLOSE GPIO assignment is a firmware interface candidate and must match the user firmware before schematic freeze.

**Supply choice for the current schematic draft:** 3.3 V from the carrier's buck regulator, rated for at least 500 mA source capability per manufacturer. This avoids adding a second 5 V rail and uses the current V1 AP63203 3.3 V regulator family, pending power/thermal validation. The schematic's WT32 pad numbering has been corrected to the candidate 26-pad sequence, and the netlist now shows OPEN/CLOSE on pads 5/6, programming on 24–26 and both EN pads on reset. This is a pin-map correction, not physical footprint verification.
