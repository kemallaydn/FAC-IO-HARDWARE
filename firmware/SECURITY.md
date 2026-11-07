# Security implementation status

**No remote relay control is implemented or enabled.**

The standalone `pulse_policy.h` is only a *partial* pure decision helper.
It does not implement authentication, replay protection, time synchronization,
network transport, hardware interlocks or relay actuation. The `Duplicate`
enum value is reserved; no duplicate detection exists yet.

Before any production control endpoint:
1. Establish device identity, secure pairing, key rotation and revocation.
2. Implement authenticated transport with replay resistance and monotonic nonce/ID store.
3. Make authorization + deduplication + execution an atomic state transition.
4. Define clock expiry semantics across reboot and offline operation.
5. Verify GPIO output safety with a real PCB and oscilloscope.
6. Validate with fault injection and first-article tests.

The host unit tests exercise policy boundaries only. They do **not**
constitute hardware, network or production security validation.
