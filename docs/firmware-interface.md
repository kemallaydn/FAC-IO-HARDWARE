# Firmware ↔ Hardware contract v0.1

## Pin map
Use `hardware/gpio-map-v0.md` as the current static mapping: it is checked against the KiCad netlist, but has not been verified on an assembled board. Target compilation and first-article tests are still required before operational use.

## Startup
1. Hardware relay drivers held OFF by external pulldowns before MCU boots.
2. Firmware initializes relay GPIOs to inactive before enabling any network services.
3. Initialize W5500 with CS deasserted; reset and identify W5500; establish Ethernet link.
4. DHCP by default; use persisted static IP only after integrity check.
5. Advertise identity only after device pairing state and network configuration are valid.
6. Never automatically pulse relays on reconnect or boot.

## Relay control
- Accept pulse only after authenticated authorization.
- Require an authenticated, strictly increasing per-device command sequence. Pulse duration is fixed by the board's hardware one-shot (about 503 ms nominal); callers cannot request a longer or shorter pulse. Verify its worst-case maximum by calculation and first-article measurement.
- Serialize OPEN and CLOSE commands: reject either command while the shared 600 ms re-arm guard is busy. Do not allow simultaneous opposing barrier commands.
- Use a hardware timer / watchdog-safe state machine; never rely on an indefinitely blocking network task.
- On reset/update, initialize trigger GPIOs low and never replay an accepted request. An LTC6993 one-shot already started may finish its bounded pulse; an MCU reset does not necessarily abort the timer.
- Loss of coil supply de-energizes the relay and opens its NO contact; verify this and the NC/COM state on the first article.

## Security/provisioning
- ESP32-C3 supports secure boot and flash encryption; exact configuration and key provisioning must be specified and tested.
- Keep irreversible security fuses **disabled during initial prototype bring-up**.
- Secure firmware update design and device identity provisioning required before field use.
- Network discovery must not allow unauthenticated relay operations.

## Testable acceptance criteria
- No relay movement during 100 cold boots and 100 software resets.
- No relay movement during firmware flashing and USB reconnection.
- Pulse duration measured at actual NO/COM contacts.
- Coil-supply loss mid-pulse opens NO contacts.
- MCU reset or Ethernet loss after a trigger does not extend the fixed hardware pulse; measure the residual pulse and confirm no retrigger.
- Unauthenticated, duplicate/stale, malformed and busy commands never pulse.
- W5500 link flaps and DHCP renewals never pulse.
