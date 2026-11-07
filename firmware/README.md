# Firmware prototype (ESP32-C3)

A minimal, buildable PlatformIO/Arduino project for ESP32-C3 development boards.

- Entry point: `src/main.cpp`.
- Build: `cd firmware && pio run`.
- Upload to a compatible **development board only**: `pio run -t upload`.
- Monitor: `pio device monitor`.

**Current behavior:** Serial heartbeat only. No W5500 initialization, relay GPIO drive, network discovery or remote control. This is deliberate: custom PCB pin map and fail-safe relay driver circuit are not yet validated.

The PlatformIO target `esp32-c3-devkitm-1` is a development target and **does not imply** that this is the final production module/board configuration. Test and verify the firmware/toolchain locally before claiming build success.

Before relay support is added, require physical circuit verification and a boot-safe design. Never enable unauthenticated relay endpoints.
