# FAC-IO network contract v0 (proposed; not implemented)

This is a **new protocol**, not the Nöron protocol. Hardware is independent of application framing.

## Provisioning
- DHCP on first boot; optional static IP in device settings.
- Device identity must be stable and unique; never rely on IP address as identity.
- Discovery can use mDNS (e.g. _fac-io._tcp.local) or authenticated UDP discovery; multicast may be blocked across VLANs. For cross-subnet deployments use configured IP or server-side registration.
- Pairing must establish per-device credentials before any relay activation is allowed.
- Factory reset must require physical presence and have documented security consequences.

## API candidate (requires security design)
Authenticated TLS-capable local gateway or protected network endpoint:
- GET /v1/status: deviceId, firmware, link, relay states, uptime.
- POST /v1/relays/1/pulse: durationMs, requestId.
- POST /v1/relays/2/pulse: durationMs, requestId.
- POST /v1/network/config: DHCP/static IP settings; authorization required.

Response must distinguish accepted, executed and rejected commands. Deduplicate requestId to avoid repeat pulses after retries. Apply maximum pulse duration, rate limits, safety interlocks and logging.

**Important:** HTTPS/TLS memory and throughput on ESP32-C3 + W5500 need benchmarking. Do not expose unauthenticated plaintext control endpoints. If constrained, use a mutually authenticated local gateway and segmented VLAN.

## Failure behavior
- Startup: all relay outputs inactive.
- Network loss: relays inactive; do not queue stale pulses.
- Restart during pulse: relay goes inactive.
- Invalid auth, duplicate, expired or oversized request: no pulse.
- Firmware upgrade: relay outputs remain inactive.
