# Component selection gate — FAC-IO Mini V1

Status: **integrated design candidates; not released for fabrication**. Exact purchasing MPNs and supplier acceptance remain open.

## MCU
Current schematic/BOM MPN: **ESP32-C3-WROOM-02-N4** (4 MB flash, PCB antenna); -02U-N4 is an alternate footprint/RF choice, not currently populated. Espressif's [module datasheet](https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html) lists -02-N4 with chip revision v0.4; the [ESP-IDF Secure Boot V2 guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/security/secure-boot-v2.html) requires ESP32-C3 v0.3/ECO3 onward. Firmware's configured minimum revision 3 is compatible with this specified module variant. Verify the chip marking and lot traceability on received production modules before provisioning; distributor stock/lot and module procurement are still unverified. The datasheet identifies 15 GPIO, 160 MHz single-core CPU, USB Serial/JTAG and strapping GPIO2/8/9.

Datasheet: https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html
Chip: https://documentation.espressif.com/esp32-c3_datasheet_en.html

The local footprint and board instance enforce copper and placement keepout on all four copper layers over the antenna region. The board Edge.Cuts has an existing 30×14 mm antenna cutout (x=113..143 mm, y=98..112 mm); the 28×11 mm antenna keepout (x=114..142 mm, y=100.9..111.9 mm) lies fully outside the base-board outline. The cutout and copper keepout therefore already place the onboard antenna beyond the PCB edge. Confirm at least 15 mm enclosure clearance; run RF range/throughput tests if Wi-Fi/BLE is enabled. See Espressif's current [ESP32-C3 PCB layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html).

**Important caveat**: SPI GPIO4–7 also have JTAG alternate functions. GPIO18/19 are USB D-/D+; GPIO21 is used for USB VBUS sense, and GPIO20 is currently unused. Verify debug requirements, reset levels and module pin availability before freezing firmware.

## Ethernet

**Current carrier design:** WIZnet `WIZ850io` plug-in module contains the W5500, PHY, transformer/magnetics, and RJ45. The carrier schematic connects ESP32-C3 SPI, reset, interrupt, 3.3 V and ground using two 1x6 host sockets. This replaces the earlier discrete W5500 + CETUS magjack candidate; its MDI circuit and old matching rules do not describe the current hardware.

Carrier sockets are the Samtec `SSQ-106-03-G-S` candidate on 2.54 mm pitch. Local footprints use the Samtec recommended 1.02 mm plated hole and standard 1×6 socket body/Fab/courtyard geometry; the two rows use the module's published 20.32 mm spacing. A single 23×25 mm WIZ850io outline is shown on `Dwgs.User` only and is not a fabricated copper/silk layer. CAD measurements do not prove mating tolerance, insertion height, orientation, module retention, enclosure clearance or assembly process. Confirm with physical parts before release. WIZnet's current pin table is checked against the schematic netlist: J1 pins 1/2=GND, 3=MOSI, 4=SCLK, 5=SCNn, 6=INTn; J2 pins 1=GND, 2/3=3V3, 4=NC, 5=RSTn, 6=MISO. The module is tracked as off-board `EXT1` on J6/J7, not U6 (the on-board LTC6993 timer).

WIZ850io requires a 3.3 V supply; WIZnet publishes about 141 mA typical at 100 Mbps transmit. Calculate regulator margin using worst-case ESP32/module load, then validate rail drop and thermal behavior on the first article. Confirm module reset timing and SPI initialization against current WIZnet documentation.

References: [WIZ850io documentation](https://docs.wiznet.io/Product/ioModule/WIZ850io), [Samtec SSQ socket family and recommended footprint](https://suddendocs.samtec.com/prints/ssq-1xx-xx-xx-x-xx-xxx-xx-xx.pdf).

## Relays
Two independent changeover dry-contact outputs, each with NO/COM/NC terminals, controlled by independent MOSFET low-side drivers with pulldowns and flyback suppression. For Hikvision DS-TMG420, channel 1 is intended for OPEN/Rising and channel 2 for CLOSE/Falling. The board only closes isolated relay contacts; it does not supply voltage or ground to the barrier. Check the installed controller revision and terminal labels before connection. See the Hikvision interface evidence under Barrier command contact.

**Low-level signal candidate:** Omron `G6K-2P-Y DC12`, a non-latching, through-hole DPDT relay. Use only one contact pole per channel; leave the second pole unconnected and explicitly mark its pins no-connect in the integrated schematic. Omron's G6K datasheet lists a 12 V coil at 9.1 mA nominal (1,315 Ω) and reference failure-rate load of 10 µA at 10 mV DC. This is appropriate as a low-level candidate for a controller command contact; final minimum-load compatibility remains unverified because Hikvision does not publish the input load. The installed KiCad 10 libraries contain the compatible `Relay:Omron_G6K-2` symbol and `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` footprint; verify availability and assembly before schematic freeze.

Two coils at the 12 V nameplate draw 18.2 mA nominal and dissipate about 0.218 W total; this excludes logic, LEDs, tolerances and startup current. For design calculations only, assume an external 12 V supply with ±10% tolerance (10.8–13.2 V). The manufacturer's 75%-of-rated maximum must-operate threshold is 9 V at 23 °C, leaving 1.8 V at the low supply limit before input-protection drop. The actual site supply range, temperature derating and continuous coil voltage must be measured/reviewed before freezing protection or regulator ratings.

The manufacturer's bottom-view drawing was compared with the installed footprint: physical pin 1 maps to `A1` (coil +), pin 8 to `A2` (coil -); physical pins 2/3/4 map to `12` (NC), `11` (COM), `14` (NO), and pins 7/6/5 to `22` (NC), `21` (COM), `24` (NO). The symbol's standardized contact numbering matches the footprint, but its *default* footprint is the non-Y `G6K-2P`; explicitly set `Relay_THT:Relay_DPDT_Omron_G6K-2P-Y` on each schematic instance. The relay remains a candidate until supply, assembly and actual barrier-input checks are complete.

Manufacturer datasheet: https://components.omron.com/us-en/datasheet_pdf/K106-E1.pdf

The earlier SONGLE `SRD-12VDC-SL-C` in `relay-driver-design-v0.2.md` is not approved for an unknown low-current dry input; do not assume its high-current contact rating proves low-level switching reliability.

## Power
Nominal 12 V input, reverse-polarity protection, surge suppression, input overcurrent protection, 3.3 V switching regulator and local bypass. Exact protection/regulator MPNs and input voltage range remain open. Two relay coils may be energized simultaneously; budget accordingly.

**D2 TVS polarity:** D2 is Diodes Incorporated `SMCJ15A-13-F`, a unidirectional 15 V, 1.5 kW SMC TVS. The KiCad schematic uses `Device:D_Zener`; netlist pin 1/K is `12V_PROT` and pin 2/A is `GND`; PCB pad nets agree. Its catalog code is LCSC C135138. First-article diode orientation and rail-clamp measurement remain required.

**Buck candidate:** Diodes Incorporated `AP63203WU-7`, fixed 3.3 V, 2 A, 3.8–32 V input, TSOT-26. The current datasheet recommends 3.9 µH, 10 µF input, two 22 µF output and 100 nF BST-to-SW for 3.3 V, with a general inductor selection range of 2.2–10 µH. It states that a ceramic input capacitor greater than 10 µF is sufficient for most applications. The manufacturer AP63203-EVB guide uses a generic 10 µF, X5R/X7R, 1206, 35 V input capacitor; this is a reference design choice, not a named approved MPN for FAC-IO. CAD uses Coilcraft `XAL5050-472MEC` (4.7 µH), which is inside the recommended range; Coilcraft rates it 6.6 A Isat and 6.1 A Irms at 20°C rise. At the provisional 12 V input, its calculated ripple is about 0.46 A at the IC's 1.1 MHz switching frequency. The actual input range and full-load thermal/current test remain open. C1 is TDK `C3225X7R1H226M250AC` (22 µF, 50 V, X7R, 1210) and C2 is TDK `CGA5L1X7R1H106K160AC` (10 µF, 50 V, X7R, 1206), in parallel on `12V_PROT` for 32 µF nominal. TDK product data confirms nominal capacitance, voltage, X7R class and tolerance; its characteristic-curve data is marked reference-only and does not establish a guaranteed minimum combined capacitance at the board DC-bias/temperature corners. The PCB places C2 beside AP63203 VIN and connects the bulk C1 bank nearby. This is a draft candidate, not a release approval: calculate worst-case effective capacitance at the agreed input range and temperature/tolerance, confirm transient clamp/headroom with SMCJ15A-13-F, and measure ripple/startup on a first article. TDK lists the 22 µF MPN as production but current supplier stock/lead time is not closed. C4/C5 now use Murata `GRM21BZ71A226ME15L` (22 µF, 10 V, X7R, 0805) to reduce DC-bias derating versus the previous 6.3 V parts; their effective capacitance over the final voltage/temperature/tolerance range still must be checked. KiCad 10 provides `Regulator_Switching:AP63203WU`; the exact power-layout review is not complete.

Manufacturer datasheet: https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf

### Preliminary 3.3 V / input budget (screening only; not release approval)

Assume a 12 V source with ±10% tolerance only for screening; the actual supply range and environment are not specified. Espressif recommends a 3.3 V supply capable of at least 500 mA for ESP32-C3. The WIZnet WIZ850io publishes 141 mA typical and 137–141 mA at 100 Mb/s transmit, but not a maximum current in that table. Use 0.641 A as a provisional allocation subtotal (0.500 A ESP supply capability + 0.141 A WIZ850io typical), before timers, indicator LEDs and any other rail loads; this is a sizing allocation, not measured consumption or a guaranteed worst-case load.

At 0.641 A, the rail output is 2.115 W. Using 85% buck efficiency as an illustrative sensitivity point gives 2.49 W input. At 10.8 V that is 0.231 A before the series reverse-protection diode drop; adding two relay coils at their 12 V nominal current (2 × 9.1 mA) yields about 0.249 A before the other loads. The former 1812L050/30 PTC is rated 0.29 A at 85°C in Littelfuse's temperature table, leaving roughly 41 mA against that simplified estimate. The current DRAFT-1.2 candidate is Littelfuse 1812L075/33DR (0.75 A hold, 1.5 A trip, 33 V maximum); the same table lists 0.36 A at 85°C, an illustrative 111 mA margin over 0.249 A. Littelfuse explicitly marks the temperature rerating table as reference-only, and this estimate omits board self-heating, diode drop effects, indicators/timers and measured worst-case module/ESP loads. Thus F1 was upgraded as a better-margin candidate, but hot continuous operation, fault/wiring protection and the PTC selection remain unsigned until actual input/ambient/load limits, manufacturer confirmation and first-article measurements are available.

For U1, 85% efficiency at 0.641 A output corresponds to about 0.38 W converter loss. Applying Diodes' reference TSOT26 θJA of 89°C/W gives a first-order 34°C junction rise, or about 119°C at 85°C ambient. The datasheet θJA test is on a single-layer 2 oz FR-4 board with minimum pad layout; actual four-layer board behavior differs. The efficiency is typical-curve data, not a guaranteed minimum, and 125°C is an absolute maximum, not a design target. Thermal margin is therefore open; verify by board-level analysis and first-article temperature measurement. The AP63203 is rated for 2 A output, but that headline rating alone does not close thermal capability.

Sources: [Espressif ESP32-C3 hardware design guideline](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32c3/index.html), [WIZnet WIZ850io electrical characteristics](https://docs.wiznet.io/Product/ioModule/WIZ850io), [Littelfuse 1812L datasheet and ordering options](https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf), [Diodes AP63203 datasheet](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf), [AP63203 evaluation-board efficiency plot](https://www.diodes.com/assets/Evaluation-Boards/AP63203-EVB-User-Guide.pdf).

## Pulse safety
**Hardware one-shot in the current synchronized schematic and PCB:** two Analog Devices `LTC6993IS6-1#TRMPBF` single-channel, rising-edge-triggered, non-retriggerable timers (U5/U6). Each `TRIG` has a 100 kΩ pulldown; each `SET` uses 768 kΩ (Yageo `RC0603FR-07768KL`). Shared `DIVCODE=5` is set by 1 MΩ (`RC0603FR-071ML`) and 523 kΩ (`RC0603FR-07523KL`). The datasheet equation gives nominal pulse width `NDIV × RSET / 50 kΩ × 1 µs` = 503.316 ms for NDIV=32768. The timer's ±2.3% accuracy and resistor tolerance imply a nominal component-only interval of roughly 487–520 ms; verify the full environmental and production tolerance by calculation and scope. C28/C29 are reassigned as local 100 nF supply bypass capacitors. The timer stage is present on the routed PCB, and startup/reset/brownout/pulse behavior remains unverified.

Divider check against the ADI datasheet: the selected 523 kΩ lower / 1 MΩ upper divider gives nominal `VDIV/V+ = 0.3434`, near the DIVCODE-5 target 0.34375; with independent ±1% resistor extremes it remains about 0.3399–0.3479, inside the specified ±1.5% window. Its nominal driving impedance is about 344.5 kΩ, below the datasheet's 500 kΩ maximum. This calculation supports the intended NDIV/POL code but does not replace measurement.

ADI describes the LTC6993-1 as rising-edge triggered and non-retriggerable. Its datasheet states that power-on reset holds OUT low during its typical 0.5–8 ms startup interval, ignores TRIG during startup, and leaves OUT low after startup when POL=0; the selected shared DIVCODE=5 programs POL=0. This is component-datasheet evidence for the intended power-up-off state, not board/first-article proof. Its output is intended to control the respective low-side relay driver; this does not independently force OFF after a MOSFET short, and the current architecture does not prove Ethernet-loss behavior. Scope reset, brownout, held trigger, repeat trigger, timer supply collapse and relay-contact pulse before release.

Datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6993-6993-1-6993-2-6993-3-6993-4.pdf

## Barrier command contact

The target family is Hikvision DS-TMG420. Hikvision's official 42-Series brochure identifies third-party commands as **Rising Control ±** and **Falling Control ±** and says CLOSE/Falling accepts pulsed signals only; a continuous closing signal can lock the barrier. The FAC-IO isolated relay contacts are intended to close only these command pairs. The DS-TMG42X user manual instructs connecting the opening and closing command pairs to the corresponding Access ANPR camera command outputs. It does not publish electrical voltage/current limits, minimum contact load or an acceptable pulse-width window; the manual diagram must not be treated as proof of the installed board's terminal numbering. Verify the exact controller revision, labels and command behavior before connection; never connect to mains, motor, or traffic-light wiring. References: [Hikvision 42-Series brochure](https://www.hikvision.com/content/dam/hikvision/en/brochures-download/product-brochures/Leaflet--Barrier-Gate-42-Series.pdf), [official DS-TMG42X manual listing](https://pro-av.hikvision.com/mena-en/support/how-to/how-to-guide/), [manual text mirror, section 2.4.3](https://device.report/m/7e84c484c62482a55af2c104611088248428c59cc9df12cf88766adf59e0c725), [Hikvision DS-TMG420 product specification](https://assets.hikvision.com/prd/normal/all/doc/m000069561/DS-TMG420_Datasheet_20260529.pdf).

## Resistors
The current 0603 placements use YAGEO RC-series 1% parts in the draft BOM and schematic `MPN` fields: 10 kΩ `RC0603FR-0710KL`, 5.1 kΩ `RC0603FR-075K1L`, 22 Ω `RC0603FR-0722RL`, 68 kΩ `RC0603FR-0768KL`, 100 kΩ `RC0603FR-07100KL`, 768 kΩ `RC0603FR-07768KL`, 1 kΩ `RC0603FR-071KL`, 1 MΩ `RC0603FR-071ML`, and 523 kΩ `RC0603FR-07523KL`. The manufacturer series data confirms the stated resistance, 0603 footprint and 0.1 W class.

LCSC part identifiers were mapped against exact manufacturer MPN and 0603 value/tolerance specifications for 21 resistor placements; 523 kΩ uses the exact YAGEO entry in the JLCPCB component catalog. These are purchasing identifiers, not a stock promise or proof of Robotistan import/assembly acceptance.

| References | Manufacturer MPN | Supplier code | Source |
|---|---|---|---|
| R1, R2, R10–R12 | RC0603FR-0710KL | C98220 | [LCSC](https://www.lcsc.com/product-detail/C98220.html) |
| R3, R4 | RC0603FR-075K1L | C105580 | [LCSC](https://www.lcsc.com/product-detail/C105580.html) |
| R5, R6 | RC0603FR-0722RL | C107701 | [LCSC](https://www.lcsc.com/product-detail/C107701.html) |
| R7 | RC0603FR-0768KL | C114633 | [LCSC](https://www.lcsc.com/product-detail/C114633.html) |
| R8, R20, R21, R26, R28 | RC0603FR-07100KL | C14675 | [LCSC](https://www.lcsc.com/product-detail/C14675.html) |
| R23, R24 | RC0603FR-07768KL | C482916 | [LCSC](https://www.lcsc.com/product-detail/C482916.html) |
| R25, R27 | RC0603FR-071KL | C22548 | [LCSC](https://www.lcsc.com/product-detail/C22548.html) |
| R29 | RC0603FR-071ML | C105578 | [LCSC](https://www.lcsc.com/product-detail/C105578.html) |
| R30 | RC0603FR-07523KL | C185324 | [JLCPCB catalog](https://jlcpcb.com/partdetail/YAGEO-RC0603FR07523KL/C185324) |

Live stock, Robotistan purchase import, lead time, minimum order quantity and assembly acceptance still need confirmation before PCBA.

## Additional exact supplier-code mappings

The following LCSC records match the exact manufacturer MPNs and nominal component values/packages in the current draft BOM. Codes are catalog cross-references only; confirm Robotistan import, stock, MOQ, land pattern and assembly acceptance before purchasing. The previous C3/C8/C30 MPN C1608X7R1E104K080AA is marked NRND by TDK; the current selected C1608X7R1H104K080AA is TDK Production, 100 nF ±10%, 50 V X7R, 0603, LCSC C72453. TDK lists it as a recommended alternate but says interchangeability is not guaranteed, so independent design review remains required; it is used here as a decoupling capacitor with unchanged nets and 0603 land pattern.

| References | Manufacturer MPN | Supplier code | Source |
|---|---|---|---|
| C4, C5 | GRM21BZ71A226ME15L | C907991 | [LCSC](https://www.lcsc.com/product-detail/C907991.html) |
| C6 | GRM21BR71C105KA01L | C77079 | [LCSC](https://www.lcsc.com/product-detail/C77079.html) |
| C7 | GRM21BZ71E106KE15L | C237493 | [LCSC](https://www.lcsc.com/product-detail/C237493.html) |
| C9 | C1206C102KGRACTU | C479755 | [LCSC](https://www.lcsc.com/product-detail/C479755.html) |
| C28, C29 | C2012X7R2A104K125AA | C2167715 | [LCSC](https://www.lcsc.com/product-detail/C2167715.html) |
| C3, C8, C30 | C1608X7R1H104K080AA | C72453 | [LCSC](https://www.lcsc.com/product-detail/C72453.html) |
| D1 | B340A-13-F | C85098 | [LCSC](https://www.lcsc.com/product-detail/C85098.html) |
| D3, D4 | 1N4007G-T | C516593 | [LCSC](https://www.lcsc.com/product-detail/C516593.html) |
| Q1, Q2 | AO3400A | C20917 | [LCSC](https://www.lcsc.com/product-detail/C20917.html) |
| U1 | AP63203WU-7 | C780769 | [LCSC](https://www.lcsc.com/product-detail/C780769.html) |
| U3 | USBLC6-2SC6 | C7519 | [LCSC](https://www.lcsc.com/product-detail/C7519.html) |
| U5, U6 | LTC6993IS6-1#TRMPBF | C581045 | [LCSC](https://www.lcsc.com/product-detail/C581045.html) |
| F1 | 1812L075/33DR | C151170 | [LCSC](https://lcsc.com/product-detail/Resettable-Fuses_Littelfuse-1812L075-33DR_C151170.html) |
| K1, K2 | G6K-2P-Y DC12 | C132367 | [LCSC](https://lcsc.com/product-detail/Signal-Relays_Omron-Electronics-G6K-2P-Y-DC12_C132367.html) |
| U2 | ESP32-C3-WROOM-02-N4 | C2934560 | [LCSC](https://www.lcsc.com/product-detail/C2934560.html) |
| D2 | SMCJ15A-13-F | C135138 | [LCSC](https://lcsc.com/product-detail/TVS_Diodes-Incorporated-SMCJ15A-13-F_C135138.html) |
| J2 | TYPE-C-31-M-12 | C165948 | [LCSC](https://www.lcsc.com/product-detail/USB-Type-C_TYPE-C-31-M-12-Female-16P-SMD_C165948.html) |
| J6, J7 | SSQ-106-03-G-S | C3323798 | [LCSC](https://www.lcsc.com/product-detail/C3323798.html) |
| J1 | TB007-508-02BE | C3816270 | [LCSC](https://www.lcsc.com/product-detail/C3816270.html) |
| J4, J5 | TB007-508-03BE | C3820511 | [LCSC](https://www.lcsc.com/product-detail/C3820511.html) |

In total, 51 of 56 placement rows have exact catalog identifiers across 29 MPNs. Five placements remain uncoded: C1, C2, L1, SW1 and SW2. CUI terminal block and TDK 0603 capacitor identifiers are exact LCSC MPN matches; Robotistan purchase/import, current stock and assembly acceptance remain unverified.

## Terminals
**Terminal candidates:** Same Sky/CUI `TB007-508-03BE` for each 3-position COM/NO/NC output and `TB007-508-02BE` for 12 V input. Both are horizontal, through-hole, 5.08 mm pitch; KiCad 10 includes corresponding `TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-03_1x03_P5.08mm_Horizontal` and `_02_1x02_` footprints. Verify the BE suffix drawing against the KiCad footprints, drill sizes, assembly method and wire-access clearance before placement.

## Verified manufacturer MPNs in current draft BOM

The current 56/56 populated references carry exact manufacturer MPN fields in the schematic, PCB, CAD BOM and Robotistan draft. Primary manufacturer references: [TDK 22 µF/50 V 1210, C1](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1H226M250AC), [TDK 10 µF/50 V 1206, C2](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA5L1X7R1H106K160AC), [Murata 1 µF/16 V 0805](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM21BR71C105KA01L%22%5D&partnumbers=%5B%22GRM21BR71C105KA01%22%5D), [Samsung 100 nF/25 V 0805](https://product.samsungsem.com/mlcc/CL21B104KACNNN.do), [TDK 100 nF/50 V 0603, C3/C8/C30](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1H104K080AA), [KEMET C1206C102KGRACTU](https://search.kemet.com/download/specsheet/C1206C102KGRACTU), [Diodes B340A-13-F](https://www.diodes.com/datasheet/download/B340A.pdf), [Diodes SMCJ15A series](https://www.diodes.com/datasheet/download/SMCJ64A.pdf), [Littelfuse 1812L](https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf), [Diodes 1N4007G](https://www.diodes.com/datasheet/download/1N4007G.pdf), [Same Sky TB007-508](https://www.sameskydevices.com/product/resource/tb007-508.pdf), [HRO TYPE-C-31-M-12](https://en.krhro.com/Product-Details/726.html), [Samtec SSQ series](https://www.samtec.com/products/ssq-106-03-t-s), [Omron G6K](https://components.omron.com/us-en/datasheet_pdf/K106-E1.pdf), [Coilcraft XAL5050](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5050-472/), [AOS AO3400A](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a), [Diodes AP63203](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf), [Espressif ESP32-C3-WROOM-02](https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.html), and [ST USBLC6-2SC6](https://www.st.com/en/protections-and-emi-filters/usblc6-2.html).

These confirm manufacturer identity and nominal package/value. They do not confirm component availability at Robotistan, solder/assembly acceptance, PCB land-pattern tolerances or board-level power margin. C1/C2 now provide 22 µF + 10 µF nominal on 12V_PROT, using TDK 1210/1206, 50 V parts. Their effective capacitance at the real input/transient/temperature corners still requires worst-case calculation; confirm TDK supply/assembly availability and measure ripple and rail behavior on a first article.

## Reset and boot switches

SW1/SW2 use E-Switch `TL3342F100QG`, the 100 gf configuration in the same TL3342 family/land pattern. E-Switch documents 1 million cycles for 100 gf parts and lists this code as a current configuration; the obsolete `TL3342F160QG` option was not used. Authorized-distributor listings indicate long lead time and large MOQ, so actual sourcing must be confirmed before order. References: [E-Switch TL3342 product page](https://www.e-switch.com/product/tl3342-series-low-profile-smt-tactile-switch/?part-number=TL3342F100QG), [E-Switch product change notices](https://www.e-switch.com/wp-content/uploads/2022/06/E-Switch_PCN_Listings.pdf).

## USB
USB-C receptacle for ESP32-C3 native USB Serial/JTAG; requires correct USB 2.0 wiring, CC pull-downs, ESD and protection against backfeeding supply. Verify behavior with only USB attached versus external 12 V present.

## Schematic freeze criteria
- Exact manufacturer part numbers + verified footprints for MCU, WIZ850io host sockets, relays, terminals, buck, USB-C and protections.
- Power budget and voltage/current/thermal calculations.
- Final GPIO pin map including bootstraps, USB and JTAG.
- Startup-safe relay drive verified independently of firmware.
- Review against vendor reference designs and first-article test requirements.
