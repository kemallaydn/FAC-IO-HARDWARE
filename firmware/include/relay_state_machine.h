#pragma once
#include <cstdint>

namespace facio {

// Hardware-independent, fail-closed timing state machine.
// Does not touch GPIOs, authenticate requests or provide replay protection.
// The caller must ensure hardware defaults OFF during reset and power loss.
class RelayStateMachine {
 public:
  static constexpr uint32_t kMinPulseMs = 100;
  static constexpr uint32_t kMaxPulseMs = 1000;

  bool start(uint32_t now_ms, uint32_t duration_ms) {
    if (active_ || duration_ms < kMinPulseMs || duration_ms > kMaxPulseMs)
      return false;
    started_at_ms_ = now_ms;
    duration_ms_ = duration_ms;
    active_ = true;
    return true;
  }

  void tick(uint32_t now_ms) {
    // Unsigned subtraction handles wraparound of the 32-bit millisecond clock.
    if (active_ && static_cast<uint32_t>(now_ms - started_at_ms_) >= duration_ms_)
      stop();
  }

  void stop() {
    active_ = false;
    duration_ms_ = 0;
  }

  bool active() const { return active_; }

 private:
  uint32_t started_at_ms_ = 0;
  uint32_t duration_ms_ = 0;
  bool active_ = false;
};

}  // namespace facio
