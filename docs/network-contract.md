# FAC-IO network contract v0 (candidate; runtime/release incomplete)

This is a **new protocol**, not the Nöron protocol. Hardware is independent of application framing.

## Provisioning
- DHCP on first boot; optional static IP in device settings.
- Device identity must be stable and unique; never rely on IP address as identity.
- Discovery can use mDNS (e.g. _fac-io._tcp.local) or authenticated UDP discovery; multicast may be blocked across VLANs. For cross-subnet deployments use configured IP or server-side registration.
- Pairing must establish per-device credentials before any relay activation is allowed.
- Factory reset must require physical presence and have documented security consequences.

## Runtime endpoint scope
The firmware source currently implements only the two authenticated pulse routes below. The PlatformIO ESP32-C3 development target compiles, but it has no signed Secure Boot/production-flash-encryption configuration and therefore fails closed; there is no production endpoint until that build and device provisioning are completed. `firmware/tools/facio_client.py` provides a host HMAC signer/HTTP client and private local sequence state, but it has not been integrated with the LPR service or exercised on physical ESP32 hardware.

Deferred API ideas, not served by this firmware:
- GET /v1/status: deviceId, firmware, link, uptime.
- POST /v1/network/config: DHCP/static IP settings; authorization required.

Implemented candidate routes:
- POST /v1/relays/1/pulse: strictly increasing uint64 `sequence`.
- POST /v1/relays/2/pulse: strictly increasing uint64 `sequence`.

For the two pulse routes, device-side request authentication is HMAC-SHA256 with a 32-byte per-device secret. Include `X-FACIO-Device` (the device MAC shown by serial commissioning), `X-FACIO-Sequence` (strictly increasing unsigned decimal), and `X-FACIO-Auth` (64 hexadecimal characters). The signature input is the UTF-8 byte sequence `FACIO/1\nPOST\n{path}\n{device-id}\n{sequence}\n`, with LF separators and a final LF; there is no request body. The bounded HTTP handler and verifier are implemented in firmware source. A test vector uses key bytes `00` through `1f`, OPEN path, device ID `02:11:22:33:44:55`, sequence `42`, and expected signature `da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf`.

The handler returns HTTP 202 `triggered` after asserting the one-shot input; it has no barrier-position/contact feedback and cannot claim that the gate moved. Each pulse is fixed by the on-board LTC6993-1 one-shot (about 503 ms nominal), so the caller cannot choose or extend its duration. OPEN/CLOSE requests share a 600 ms re-arm guard. The sequence reservation is persisted before triggering. The guard limits authenticated pulse frequency; per-client throttling and durable command audit logging remain unimplemented.

The host-tested `firmware/include/sequence_reservation.h` uses 256-command reservation windows: before accepting a sequence beyond the persisted ceiling, it persists `sequence + 255`. On reboot, firmware restores the ceiling as the accepted floor; clients must resume above it, deliberately skipping unused values that may have been reserved before power loss. The request handler persists before it pulses a trigger. NVS power-failure behavior remains untested on the target.

The server also requires the active Ethernet link, DHCP, Secure Boot, flash encryption and a provisioned key. After the application boots normally, a physical BOOT-button press opens a 60-second USB commissioning window accepting `KEY:<64 hex chars>`; holding BOOT through reset instead enters the ROM downloader. Commissioning is disabled until the security fuses/configuration are active. The current PlatformIO development build does not configure/sign that production image, so the API is not enabled by the current build.

**Important:** HTTPS/TLS memory and throughput on ESP32-C3 + W5500 need benchmarking. Do not expose unauthenticated plaintext control endpoints. If constrained, use a mutually authenticated local gateway and segmented VLAN.

## Failure behavior
- Startup: all relay outputs inactive.
- Network loss: accept no new command and queue none; a one-shot pulse already started runs to its hardware timeout.
- MCU reset during pulse: firmware issues no new trigger; an already-running one-shot may complete its bounded pulse. Measure this behavior on the first article.
- Loss of relay-coil power: NO contact opens as the relay de-energizes; verify contact behavior on the first article.
- Invalid auth, duplicate/stale sequence or busy relay: no pulse.
- Firmware upgrade: relay outputs remain inactive.
