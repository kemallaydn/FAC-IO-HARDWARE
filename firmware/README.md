# Firmware prototype (ESP32-C3)

A minimal, buildable PlatformIO/Arduino project for ESP32-C3 development boards.

- Entry point: `src/main.cpp`.
- Build: `cd firmware && pio run`.
- Upload to a compatible **development board only**: `pio run -t upload`.
- Monitor: `pio device monitor`.

**Candidate behavior:** Initializes both one-shot trigger GPIOs inactive, initializes WIZ850io/W5500, derives a stable local MAC, requests DHCP and reports state over native USB CDC. When Secure Boot, flash encryption, NVS state and a per-device key are all valid, it serves authenticated fixed-duration OPEN/CLOSE pulse routes. The normal development target and an isolated Secure Boot V2 signed test target compile. The signed test image is not a production release: no flash-encryption key was supplied, no hardware provisioning was run, and the command endpoint has not been verified on a board. The custom PCB, power/reset behavior and relay path are not bench-validated.

The board's two LTC6993-1 circuits target a fixed hardware pulse (about 503 ms nominal with the current component values). Firmware does not accept a caller-selected duration; OPEN/CLOSE commands share a 600 ms lockout. The HTTP parser, HMAC verifier, NVS sequence reservation, physical USB key commissioning and GPIO trigger code are connected in `src/main.cpp`; the development target compiles, but compilation and host tests do not substitute for board validation. Commissioning is opened by pressing BOOT after the application has started; holding BOOT through reset enters the ROM downloader.

The PlatformIO target `esp32-c3-devkitm-1` has been built successfully as a development target; this **does not imply** that it is the final production module/board configuration. It is not a signed Secure Boot / production flash-encryption image, has not been uploaded to hardware, and does not enable the command server.

The isolated `fac_io_c3_security_test` profile uses Arduino as an ESP-IDF component, Secure Boot V2, flash-encryption Release configuration, 4 MB flash and minimum C3 revision 3. A local ESP-IDF 5.5.5 build succeeded; bootloader, application and partition images were signed with an ephemeral RSA-3072 test key and all three signatures verified with `espsecure v5.4.0`. The key was deleted after verification. ESP-IDF warned that no flash-encryption key was set, so this evidence does **not** establish an encrypted production image. **Never flash or distribute this test image.** First boot of an image configured for Release-mode security can irreversibly provision security eFuses. Production-key custody, per-device encryption/provisioning, update/recovery, and exact module silicon revision must be reviewed before field use.

`tools/facio_client.py keygen --key-file <private-file>` creates a random 32-byte key and prints the USB pairing line. `tools/facio_client.py pulse --host <device-ip> --device-id <mac> --relay open|close --key-file <private-file>` signs and sends one command, keeping the local sequence reservation in a private state file. A network timeout is not retried because the command may already have been accepted. The helper has host tests but has not been run against a board.

Do not deploy until signed Secure Boot / flash-encryption production provisioning, hardware bring-up, first-article pulse/fail-safe measurements and fault testing pass. Never enable unauthenticated relay endpoints.
