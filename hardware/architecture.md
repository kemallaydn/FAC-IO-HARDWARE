# FAC-IO Mini V1: current electrical architecture

**Status: integrated DRAFT-1.2 CAD; not released for manufacturing.** Latest KiCad 10.0.8 ERC and PCB DRC with zone refill and schematic parity pass with zero reported violations and zero unconnected pads. Footprint-filter checks are enabled, and the PCB DRC report contains no ignored checks. Electrical behavior, mechanical fit, sourcing, independent CAM review and a physical first article remain unverified.

## Power

- Nominal 12 V DC enters through a two-position terminal, resettable fuse, reverse-polarity protection, and transient suppressor.
- Protected input feeds the 3.3 V buck and the two 12 V relay coils.
- ESP32-C3-WROOM-02-N4 and WIZ850io use the 3.3 V logic rail. WIZ850io current demand and rail margin still need worst-case thermal/load verification.
- USB-C provides programming/debug; USB-only and 12 V + USB power cases need bench verification for backfeed and reset behavior.

## Ethernet

- ESP32-C3 connects to the WIZ850io using SPI, reset, interrupt, 3.3 V, and ground through two 1x6 host sockets.
- WIZ850io contains the W5500, Ethernet PHY, transformer/magnetics, and RJ45. The carrier therefore has no bare W5500 MDI pair or RJ45 layout.
- Carrier sockets use the Samtec SSQ-106-03-G-S candidate and local 1x6 footprints with socket body/Fab/silkscreen/courtyard geometry. A single 23×25 mm external WIZ850io envelope is drawn on Dwgs.User and is not included in manufacturing Gerbers. Mating compatibility, solder process, module retention, module height and enclosure clearance still require a physical sample review.
- The current four-layer draft includes a connected GND copper zone on In2.Cu, with clearances around routed nets and the ESP32 antenna cutout. KiCad refilled DRC reports 0 violations; selected board stackup, return-path/EMC behavior and fabrication CAM still require independent verification.

## Barrier outputs

- K1 and K2 are separate Omron G6K-2P-Y DC12 signal relays. Each uses one pole for its own COM/NO/NC terminal; unused poles are unconnected.
- MOSFET low-side coil drivers, gate pulldowns, and flyback diodes are represented in the schematic.
- Two LTC6993-1 single-shot timers are specified in the schematic as independent pulse-width limiters (nominal 503 ms); the routed PCB now contains both timer channels, their shared DIVCODE network and the required local bypass capacitors. Their startup/trigger behavior and actual contact pulse must be verified with a scope and continuity meter on a first article.
- Connect only the isolated dry contacts across the physically labelled barrier command pair. Never connect FAC-IO power, ground, motor, mains or traffic-light terminals to those contacts.
- Hikvision's 42-Series brochure calls the third-party inputs **Rising Control ±** and **Falling Control ±**, and warns that CLOSE/Falling supports pulsed signals only; a continuous closing signal can lock the barrier. The DS-TMG42X user manual instructs connecting the opening and closing command pairs to the corresponding Access ANPR camera command outputs, but publishes no electrical voltage/current limits, minimum contact load or acceptable pulse-width window. The nominal 503 ms hardware one-shot is therefore only a design value until worst-case pulse and exact controller compatibility are measured on a first article. The Omron signal relay remains an unverified compatibility candidate. ([Hikvision 42-Series brochure](https://www.hikvision.com/content/dam/hikvision/en/brochures-download/product-brochures/Leaflet--Barrier-Gate-42-Series.pdf))

## Release blockers

1. Freeze exact manufacturer ordering codes for every passive, fuse, protection device, connector and assembly item; reconcile the procurement BOM.
2. Confirm WIZ850io, Samtec socket and ESP32 module physical fit/orientation with actual samples and the selected enclosure.
3. Obtain Robotistan's accepted four-layer stackup, finish, drill/slot rules, THT assembly capability and procurement agreement; confirm the Gerber job matches that quote.
4. Independently review power, relay isolation/fail-safe paths, protection, antenna clearance, test points and manufacturing package.
5. Assemble a first article and execute `docs/validation.md`; no lab or barrier-system tests are claimed as complete.
