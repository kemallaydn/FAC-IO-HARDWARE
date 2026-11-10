# Security implementation status

The candidate firmware now contains a bounded HTTP pulse handler, per-device
HMAC-SHA256 authentication, a durable anti-replay sequence reservation, and
fixed GPIO trigger pulses with a shared OPEN/CLOSE re-arm guard. These controls
are fail-closed: the command server starts only after link/DHCP, Secure Boot,
flash encryption, persistent state, and a provisioned 32-byte key are present.
The custom API accepts only the two fixed pulse routes and no request body or
caller-selected pulse duration.

Initial key provisioning and rotation require the application to boot normally,
then a physical BOOT-button press opens a 60-second USB CDC window for
`KEY:<64 hex chars>`. Holding BOOT through reset would enter the ROM downloader,
so it must be pressed after startup. The key is saved to NVS and read back before acceptance.
This is gated on Secure Boot and flash encryption. The isolated PlatformIO
security-test profile now builds and signs Secure Boot V2 images, and its
bootloader, application and partition signatures have been verified using a
temporary test key. No flash-encryption key was supplied and no encrypted
production image or device provisioning has been verified. The profile uses
Release-mode flash-encryption configuration; never flash or distribute its
artifacts. First boot can irreversibly provision security eFuses. Do not burn
eFuses on a development unit.

The host tests do not exercise ESP32 Preferences, the W5500 socket stack, USB
commissioning, GPIO pulse timing, reset/brownout behavior, or the physical
relay contacts. The software re-arm guard is not feedback. GPIO pull-downs do
not independently prove crash fail-off if an MCU output is stuck high.

## Required before field use

1. Establish production signing-key custody, per-device flash-encryption key
   provisioning, signed/encrypted release packaging and a tested recovery/update
   process without provisioning a development unit.
2. Build and test the exact target image; test NVS write failures, corruption,
   reboot and power loss during sequence reservation and key storage.
3. Measure reset/brownout GPIO states, trigger width, one-shot output and relay
   isolation on a first article using an oscilloscope and continuity checks.
4. Add and test an independent hardware watchdog/enable path for crash and
   brownout fail-off.
5. Implement and test the request signer/client and commissioning/rekey
   workflow; provision a unique random 32-byte key per device.
6. Review rate limiting, local-network threat assumptions, update/recovery and
   production provisioning before field deployment.
