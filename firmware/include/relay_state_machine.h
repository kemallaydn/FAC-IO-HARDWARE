#pragma once

#include <cstdint>

namespace facio {

// Host-testable software re-arm guard for the board's fixed hardware
// one-shot. It is not a measurement of relay state and never drives GPIO.
class RelayStateMachine {
 public:
  // LTC6993-1 + selected resistors yield about 503 ms nominal and up to about
  // 520 ms in the component-only estimate; add margin before accepting another
  // command. First-article measurement is still required.
  static constexpr uint32_t kRearmGuardMs = 600;

  bool start(uint32_t now_ms) {
    if (busy_) return false;
    started_at_ms_ = now_ms;
    busy_ = true;
    return true;
  }

  void tick(uint32_t now_ms) {
    // Unsigned subtraction handles wraparound of the 32-bit millisecond clock.
    if (busy_ && static_cast<uint32_t>(now_ms - started_at_ms_) >=
                     kRearmGuardMs) {
      busy_ = false;
    }
  }

  void shutdown() { busy_ = false; }
  bool busy() const { return busy_; }

 private:
  uint32_t started_at_ms_ = 0;
  bool busy_ = false;
};

}  // namespace facio
