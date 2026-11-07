# Relay driver electrical design, revision 0.2 (prototype candidate)

**Status: engineering candidate, NOT validated, NOT approved for PCB manufacturing.**

## Exact candidate components

| Ref | MPN candidate | Purpose | Design note |
| --- | --- | --- | --- |
| K1, K2 | SONGLE SRD-12VDC-SL-C | 12 V SPDT relay, nominal 0.36 W coil | Verify exact manufacturer drawing, pin pitch, coil/contact variant and authentic sourcing before footprint lock. |
| Q1, Q2 | Alpha & Omega AO3400A | Logic-level N-MOSFET, SOT-23 | Verify 3.3 V gate drive and package pin numbering from manufacturer datasheet. |
| D1, D2 | onsemi 1N4007G | Flyback diode, DO-41 | Cathode to protected +12 V, anode to switched coil low node. |
| R1, R3 | 1 kΩ, 0603, 1%, >=0.1 W | Series GPIO-to-gate | Peak GPIO gate charge current bounded by ~3.3 mA (ignoring pin resistance). |
| R2, R4 | 100 kΩ, 0603, 1%, >=0.1 W | Gate-to-source pulldown | GPIO reset/high-Z tends toward OFF; cannot replace boot-state verification. |
| J_OUT1, J_OUT2 | 3-position terminal block, pitch TBD | Isolated dry contacts | Pins COM/NO/NC, no connection to controller 12 V or GND. |

## One-channel circuit topology (repeat for channel 2)

```text
ESP32_GPIO -- 1k --+---- G   AO3400A
                   |
                 100k
                   |
GND ---------------+---- S
                         D ----- COIL_LOW ------+------ relay coil ------ +12V_PROTECTED
                                                |
                                        diode ANODE
                                        diode CATHODE ------------------ +12V_PROTECTED

RELAY_CONTACTS (electrically isolated from the coil):
barrier input terminal A <-- COM
barrier input terminal B <-- NO   [NC unused unless explicitly required]
```

## Electrical calculations and constraints

- Candidate coil nominal current: 0.36 W / 12 V = **30 mA** per relay.
- Both coils ON: ~60 mA total nominal, **not** including MCU, Ethernet, indicator LEDs, transient or regulator losses.
- Coil resistance implied by nominal rating: 12² / 0.36 = **400 Ω** (nominal only; datasheet governs).
- Gate pulldown DC current with 3.3 V HIGH: 3.3 V / (101 kΩ) ≈ **32.7 µA**.
- 1 kΩ gate resistor is for transient gate charge control; **not** a steady-state 3.3 mA GPIO load.
- Do not rely on relay contacts to switch mains, barrier motor or any unknown inductive load. The intended interface is an isolated, low-energy barrier control input only.
- Relay energization must be inhibited until MCU initialization, watchdog and application authorization are complete. GPIO reset states and boot glitches require oscilloscope validation.
- Contact rating and dielectric separation require the *exact* relay datasheet and board creepage/clearance design. Dry contact does not automatically imply safe isolation.

## Blocking checks before release

1. Verify **manufacturer datasheets** for AO3400A, SRD-12VDC-SL-C, 1N4007G and the terminal block.
2. Confirm the MOSFET gate-source voltage, Rds(on) at available Vgs, package pinout and relay coil worst-case voltage/current.
3. Validate diode footprint, cathode band orientation and coil suppression effect on relay release time.
4. Choose actual relay footprint only after matching mechanical drawing and hole dimensions; **no guessed footprint**.
5. Confirm NO/COM/NC pin mapping by continuity measurement on assembled first articles.
6. Test cold boot, brownout, watchdog reset, Ethernet loss, power cycling and stuck-high GPIO fault behavior.
7. KiCad ERC and PCB DRC must pass; neither has been run on this candidate.
8. A software pulse timeout cannot protect against MOSFET short or welded contacts; assess barrier controller fail-safe separately.

## Schematic mapping

Current draft `hardware/relay-driver-v0.kicad_sch` has K1/K2 **coil symbols only**. It does not yet represent the SPDT contact sets or J_OUT terminals. Do not export manufacturing data from that draft.
