# Firmware ↔ Hardware contract v0.1

## Pin map
Use `hardware/gpio-map-v0.md` as a **provisional** mapping only. Do not flash a board using it until the actual PCB netlist is verified.

## Startup
1. Hardware relay drivers held OFF by external pulldowns before MCU boots.
2. Firmware initializes relay GPIOs to inactive before enabling any network services.
3. Initialize W5500 with CS deasserted; reset and identify W5500; establish Ethernet link.
4. DHCP by default; use persisted static IP only after integrity check.
5. Advertise identity only after device pairing state and network configuration are valid.
6. Never automatically pulse relays on reconnect or boot.

## Relay control
- Accept pulse only after authenticated authorization.
- Require idempotency key and bounded pulse duration (suggested initial 100–1000 ms; final range requires barrier input spec).
- Prevent simultaneous or overlapping pulse requests until explicit policy defined.
- Use a hardware timer / watchdog-safe state machine; never rely on an indefinitely blocking network task.
- On restart, loss of supply, watchdog reset or update: relay driver OFF.

## Security/provisioning
- ESP32-C3 supports secure boot and flash encryption; exact configuration and key provisioning must be specified and tested.
- Keep irreversible security fuses **disabled during initial prototype bring-up**.
- Secure firmware update design and device identity provisioning required before field use.
- Network discovery must not allow unauthenticated relay operations.

## Testable acceptance criteria
- No relay movement during 100 cold boots and 100 software resets.
- No relay movement during firmware flashing and USB reconnection.
- Pulse duration measured at actual NO/COM contacts.
- Power loss mid-pulse opens contacts.
- Unauthenticated, duplicate, expired, malformed and oversized commands never pulse.
- W5500 link flaps and DHCP renewals never pulse.
