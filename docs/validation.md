# Verification and Manufacturing Gate

## Current gate (2026-11-10, current-source DRAFT review bundle)

- [x] KiCad 10.0.8 schematic netlist exports successfully. D2 uses unidirectional Diodes Incorporated SMCJ15A-13-F; pin 1/K=`12V_PROT`, pin 2/A=`GND`.
- [x] Schematic ERC: exit 0, 0 errors, 0 warnings (`validation-reports/schematic-erc.txt`).
- [x] PCB DRC with zone refill and schematic parity: exit 0, 0 violations, 0 unconnected pads, 0 footprint errors/parity issues and no ignored DRC checks (`validation-reports/pcb-drc.txt`). Project-specific connector symbols now identify the exact CUI and WIZ850io footprints; footprint-filter mismatch checking is warning-enabled.
- [x] KiCad JSON DRC evidence (`validation-reports/pcb-drc-parity.json`) records empty violation, unconnected, schematic-parity and ignored-check arrays.
- [x] Added 1×6 Samtec socket courtyard/Fab/silkscreen geometry and one non-fabrication 23×25 mm external WIZ850io module outline. Physical socket mating, module height and enclosure fit remain open.
- [x] Widened all seven `/12V_IN` and `/12V_FUSED` input-path segments to 0.45 mm; project custom DRC rule enforces that minimum. DRC remains clean with zone refill and schematic parity.
- [x] DRAFT-1.2 Gerber/Excellon, BOM, positions, schematic PDF, assembly drawing, 3D render and ZIP regenerated from current CAD with zone refill. ZIP CRC passes; Gerbonara 1.6.3 independently parses all 11 Gerber layers and both Excellon files. Edge.Cuts is 110.10×77.10 mm; PTH has 181 drill features (177 round hits + 4 slots) and NPTH has 6 round hits. Gerbonara warns about `G90` after `%`; the current KiCad output uses it as the absolute-coordinate body command, as in JLCPCB's published Excellon fragment. A structural check confirms tool tables, decimal metric coordinates, G85 slots and all coordinates inside Edge.Cuts. KiCad exports remain unchanged. Robotistan/fabricator CAM acceptance must still confirm drill interpretation, tool sizes, slots and origin. This refresh incorporates current refilled copper-zone geometry.
- [x] Draft Robotistan BOM and Pick & Place reconcile at 56/56 unique designators; all 56 manufacturer MPN fields are populated. Exact catalog identifiers are mapped to 51 placements across 29 MPNs; 5 rows remain without a confirmed supplier code.
- [x] Corrected 51 stale `Status` notes in the DRAFT-1.2 Robotistan BOM from the authoritative `hardware/bom-draft.csv`; synchronized exact supplier codes across source, Robotistan and assembly BOMs. Regenerated the previously stale 10-row schematic BOM from current CAD; verified 56/56 refs and value/footprint/MPN plus 56/56 Pick & Place refs. Current stock, MOQ, Robotistan import and assembly acceptance remain unverified; this is not a complete PCBA BOM.
- [x] Replaced C3/C8/C30 TDK 0603 bypass capacitors from the manufacturer-NRND 25 V MPN with active-production 50 V C1608X7R1H104K080AA (LCSC C72453); footprint/net geometry unchanged. KiCad netlist, ERC, DRC and parity re-run and pass. TDK warns the alternate is not guaranteed interchangeable; reviewer confirmation remains open.
- [x] Gerbonara 1.6.3 parsed 11 Gerbers and 2 Excellon files: four copper layers, 110.10×77.10 mm board, 177 plated round hits + 4 slots, 6 NPTH. The `G90` post-header warning is documented and structurally cross-checked; CAM acceptance is open.
- [x] `python3 hardware/gpio_check.py`: exit 0, 11 candidate assignments without static GPIO conflicts; also checks GPIO0/GPIO1 low-latch setup before SPI/Ethernet startup and ESP32-C3 hardware USB Serial/JTAG + CDC-on-boot configuration. Five `hardware/test_gpio_check.py` regression tests pass, including wrong-pin, missing-init and disabled-USB negative controls. Reset waveforms, module availability and relay startup remain unverified on hardware.
- [x] Firmware now includes WIZ850io reset/SPI setup, W5500 detection, DHCP request/renew/retry and serial link/IP diagnostics; it has no network command endpoint or relay actuation.
- [x] PlatformIO ESP32-C3 development target build: `pio run -e fac_io_c3` exit 0; firmware image 373,694 bytes and RAM use 15,692 bytes. This used PlatformIO Core 6.2.0 with a temporary local low-disk installer wrapper and verified Arduino-ESP32 3.3.12 / C3 libs 3.3.12. The wrapper is not part of the repo. It is not a signed Secure Boot or production flash-encryption image; command service stays fail-closed. No upload or hardware result is implied.
- [x] Isolated ESP-IDF 5.5.5 / Arduino ESP32-C3 Secure Boot V2 test build: exit 0. Bootloader (28,672 B), application (397,312 B) and partition table (8,192 B) signatures verify with `espsecure v5.4.0`; temporary RSA-3072 signing key deleted after the check. SDKConfig confirms C3 revision minimum 3, 4 MB flash, Secure Boot V2 and flash-encryption Release mode. ESP-IDF warned that no flash-encryption key was set; this is signing/build evidence only, not proof of an encrypted production release. Full evidence and artifact hashes: `validation-reports/firmware-secure-build-test.txt`. No image was flashed and no eFuse was touched.
- [x] Staged `manufacturing/REVIEW-2026-11-10-DRAFT/` from fresh current-source KiCad exports and current ERC/DRC reports. All 11 Gerbers and both decimal-format drill files match DRAFT-1.2 after normalizing only creation timestamps; Gerbonara 1.6.3 parses all 13 files, reports 110.10×77.10 mm Edge.Cuts, 177 round PTH + 4 slots, and 6 NPTH. G90 placement has a structural cross-check in the package. ZIP has 14 members and CRC passes. Review package has a DRAFT/NOT-APPROVED marker; it is not for ordering.
- [x] `manufacturing/release_check.py` accepts `--root` for a separate review package. The current review bundle's bare-PCB profile returns only `Missing: release/APPROVED.txt`; the repository default still reports its five missing release files. The approval record was not created.
- [ ] WIZ850io hardware bring-up; production signing-key custody and per-device flash-encryption provisioning; exact-module/revision build review; update/recovery procedure. Physical USB, Ethernet, reset/brownout, relay pulse and fail-safe behavior remain unverified. Never flash or distribute the security-test artifacts.
- [x] Internal visual scan of Gerbonara SVG renders for F.Cu, B.Cu, In1.Cu, In2.Cu, F.Silkscreen and Edge.Cuts found no obvious missing outline or broken layer geometry. This is a sanity check, not independent CAM approval.
- [x] Explain the Gerbonara G90 warning with a structural check and published Excellon body-command example.
- [ ] Obtain independent visual layer review and project-specific CAM/stackup/drill-slot acceptance from the fabricator.
- [ ] Confirm supplier codes/stock, assembly/THT capability, module/enclosure fit, independent electrical review, and first-article power/thermal/reset/brownout/relay/Ethernet measurements.

Passing ERC/DRC/parity proves CAD consistency against configured rules. It does not prove electrical safety, part procurement, physical fit, signal integrity, assembly yield, supplier acceptance or production readiness. DRAFT-1.2 remains under `manufacturing/DRAFT-2026-11-09-DRAFT-1.2/` as historical output. The newer current-source review bundle is `manufacturing/REVIEW-2026-11-10-DRAFT/`; it is explicitly not approved for manufacture.

`manufacturing/release_check.py --profile pcb` checks a bare-board release: approval, passing CAD reports and the Gerber/drill ZIP. The default `--profile pcba` adds BOM, Pick & Place, exact source-BOM parity, manufacturer MPNs and catalog-code checks. The production BOM's quantity, value, footprint, MPN, C Code and population fields must match `hardware/bom-draft.csv`; every PCBA C Code must be a non-empty `C` catalog identifier. Both profiles require an approval record with a matching profile and clean CAD evidence. Approval also records SHA-256 hashes for the CAD sources, reports, Gerber, and (for PCBA) BOM and Pick & Place, so changing a reviewed file invalidates that approval. For the review bundle, run `python3 manufacturing/release_check.py --profile pcb --root manufacturing/REVIEW-2026-11-10-DRAFT`; `--print-approval-hashes` accepts the same `--root` option and prints values for the reviewer to record after approval. It does not approve or release anything. A passing script remains a file/package gate; it cannot establish supplier acceptance or physical/independent review by itself.

## Electrical and mechanical review before production

- [ ] Confirm ESP32-C3-WROOM-02-N4 pinout, strapping and reset behavior. Current Edge.Cuts has an antenna cutout spanning x=113..143 mm to y=112 mm; the 28×11 mm four-layer antenna keepout at x=114..142 mm, y=100.9..111.9 mm is outside the base-board outline. KiCad enforces copper and placement keepout. Confirm the 15 mm enclosure clearance; run RF range/throughput validation if Wi-Fi/BLE will be enabled.
- [ ] Confirm WIZ850io pinout, supply margin, host-header mating and module retention.
- [ ] Confirm Omron G6K-2P-Y pin mapping, coil supply, contact behavior and minimum load compatibility with the actual barrier input.
- [ ] Verify 12 V input range, protection, buck power/thermal margin and simultaneous coil load. Preliminary screening estimates ~0.25 A input under stated assumptions against 0.29 A PTC hold at 85°C; the estimate excludes several loads and is not a release calculation.
- [ ] Review USB recovery, ESD and USB/external-supply backfeed behavior.
- [ ] Confirm enclosure, terminal pitch, mounting and field wiring access.
- [ ] Independently inspect isolation of dry-contact terminals from all powered nets.
- [ ] Verify the monostable pulse limiter startup/clear/trigger behavior and scope outputs under reset/brownout/crash scenarios.

## CAD and manufacturing acceptance

- [x] Integrated schematic and explicit nets exist; current netlist exports.
- [x] ERC and schematic/PCB parity pass with no reported violations.
- [ ] Check impedance/return path and final stackup with the selected fabricator; WIZ850io removes the carrier-board Ethernet MDI routing.
- [x] Draft Gerber, Excellon, BOM, positions and drawings were generated from current source files.
- [ ] Inspect each Gerber/drill layer independently; verify polarity, outline, slots and drills.
- [ ] Supplier confirms THT relays, sockets, terminals and module procurement/mounting process.
- [ ] Generate production-named exports only after all review gates are passed.

## First-article test (current-limited bench supply)

1. Inspect polarity, shorts, solder bridges and part variants.
2. Power at the approved input range; record inrush, steady load, 3.3 V ripple and temperatures.
3. Verify USB flash/recovery, reset, brownout and no power-domain backfeed.
4. Verify WIZ850io SPI identity, Ethernet link, DHCP, reconnect and long-run stability.
5. Test each relay separately with a meter, not connected to a barrier; verify COM/NO/NC and pulse width.
6. Verify power/coil loss de-energizes the relay; boot and reset do not create a fresh closure. If MCU reset or network loss occurs after a timer trigger, measure the remaining bounded pulse and confirm it does not retrigger or extend.
7. Perform appropriate ESD/surge/environment tests.
8. Only then connect to the documented low-voltage barrier command input under supervision.

No first-article tests have been run. Hikvision's 42-Series brochure identifies **Rising Control ±** and **Falling Control ±** as third-party command interfaces and warns that a continuous closing signal can lock the barrier; use only a pulse. The DS-TMG42X user manual instructs connecting the barrier's opening and closing command pairs to the corresponding Access ANPR camera command outputs. It does not publish electrical voltage/current limits, minimum contact load or an accepted pulse-width window. Neither document establishes J4/J5 terminal numbers. Before connection, inspect the exact controller revision and labels, confirm the barrier's command behavior, and measure the hardware-limited CLOSE pulse on the assembled board. ([Hikvision 42-Series brochure](https://www.hikvision.com/content/dam/hikvision/en/brochures-download/product-brochures/Leaflet--Barrier-Gate-42-Series.pdf), [official DS-TMG42X manual listing](https://pro-av.hikvision.com/mena-en/support/how-to/how-to-guide/), [manual text mirror, section 2.4.3](https://device.report/m/7e84c484c62482a55af2c104611088248428c59cc9df12cf88766adf59e0c725))

## Supplier intake (checked 2026-11-09)

Robotistan's current [PCB service page](https://www.robotistan.com/pcb-servisi) lists 1/2/4-layer production, a five-board standard minimum and Gerber-only intake for bare PCB fabrication. PCB assembly additionally requires BOM and Pick & Place; C codes are used to match parts when Robotistan is asked to source them. The `pcb` and `pcba` release profiles reflect those different file requirements. This is service capability information, not acceptance of this specific board. Obtain project-specific CAM/DFM and sourcing approval before order.
