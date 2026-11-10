# FAC-IO Mini V1 — Ethernet Barrier Relay Controller

Status: **Integrated engineering draft. NOT production-ready.** KiCad 10.0.8 ERC/DRC and schematic parity currently pass; sourcing, mechanical, supplier, independent review, and first-article gates remain open.

FAC-IO is an Ethernet-connected, programmable dry-contact relay controller for integration with our own license-plate recognition/access-control software. It is **not** a barrier motor driver.

## V1 scope
- ESP32-C3-WROOM-02-N4 in current DRAFT BOM (GPIO/USB and antenna placement still require physical review)
- WIZnet WIZ850io (W5500 + PHY + magnetics + RJ45) as a plug-in module on two host sockets
- 2 independent, normally-open / common / normally-closed dry-contact relay outputs
- 12 V DC input, regulated 3.3 V logic supply
- USB programming/debug interface, BOOT/RESET recovery access
- Power, link and relay indicators; four mounting holes
- Firmware source contains DHCP and an HMAC-authenticated fixed-pulse command path; a host signer/client exists, but LPR integration, Secure Boot/flash-encryption production build and target verification are incomplete, so command service remains fail-closed in the current build
- Two independent hardware one-shots nominally limit OPEN/CLOSE relay pulses to about 503 ms; tolerance and fail-safe behavior still require first-article validation
- Optional future PoE; **not included** in V1
- RS232, RS485 and legacy Nöron protocol **not required** in V1

## System flow
LPR service -> authenticated LAN command -> FAC-IO -> timed dry-contact closure -> barrier controller OPEN or CLOSE input.

The dry-contact output must be wired only to the barrier controller's documented command input, **never directly to the motor or mains**. Each channel uses a fixed hardware one-shot (about 503 ms nominal from the current timer/resistor values); firmware cannot extend or configure the relay pulse. The full pulse tolerance and first-article maximum still require verification.

Hikvision's 42-Series brochure identifies the third-party command interfaces as **Rising Control ±** and **Falling Control ±**; it does not substantiate controller terminal numbers such as J4/J5. Wire each isolated relay COM/NO pair only across the matching, physically labelled command pair. Hikvision states that closing accepts pulsed signals only and a continuous closing signal can lock the barrier. The independent hardware one-shot bounds both outputs, but the nominal 503 ms pulse and its maximum tolerance must be verified on the exact controller revision before connection. Do not connect FAC-IO power or ground to these pairs. Never connect to mains, motor or traffic-light terminals. ([Hikvision 42-Series brochure](https://www.hikvision.com/content/dam/hikvision/en/brochures-download/product-brochures/Leaflet--Barrier-Gate-42-Series.pdf))

## Repository layout
- `docs/requirements.md`: engineering requirements and open decisions
- `docs/validation.md`: verification and acceptance plan
- `hardware/`: integrated KiCad schematic, PCB and local footprints
- `manufacturing/`: draft Gerber, Excellon, BOM, positions and validation artifacts
- `firmware/`: ESP32-C3/W5500 candidate firmware, protocol/security implementation and host tests; development target build passes, while production-secure build and first-article validation remain open

## Manufacturing release rule
The current-source bare-board review bundle is `manufacturing/REVIEW-2026-11-10-DRAFT/`; it contains fresh Gerber/Excellon outputs, current ERC/DRC reports, a preview and hashes. It includes `release/NOT-APPROVED.txt` and is not approved for fabrication. The package gate with `--root` currently reports only the missing independent approval file. CAM/stackup and drill/slot acceptance, Robotistan pricing/acceptance, module/header fit, independent electrical review and first-article tests remain open. `manufacturing/release_check.py` is the release gate.
