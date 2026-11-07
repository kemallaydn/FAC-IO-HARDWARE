#pragma once
#include <cstdint>
#include <cstddef>
#include <array>
#include "relay_state_machine.h"
#include "pulse_policy.h"

namespace facio {
// Logic-only controller; does not authenticate credentials or drive GPIO.
// Replay cache is VOLATILE and bounded: NOT production replay protection.
class RelayController {
 public:
  static constexpr size_t kHistorySize = 16;
  Decision request(unsigned relay_index, const Request& req, uint64_t now_ms,
                   uint32_t now_tick_ms) {
    if (relay_index >= relays_.size()) return Decision::InvalidDuration;
    if (!req.authenticated) return Decision::Unauthorized;
    if (req.request_id == 0) return Decision::Duplicate;
    for (const auto id : history_)
      if (id == req.request_id) return Decision::Duplicate;
    const auto decision = policy_.evaluate(req, now_ms, relays_[relay_index].active());
    if (decision != Decision::Accepted) return decision;
    if (!relays_[relay_index].start(now_tick_ms, req.duration_ms))
      return Decision::Busy;
    history_[next_history_] = req.request_id;
    next_history_ = (next_history_ + 1) % kHistorySize;
    return Decision::Accepted;
  }
  void tick(uint32_t now_tick_ms) {
    for (auto& relay : relays_) relay.tick(now_tick_ms);
  }
  void shutdown() {
    for (auto& relay : relays_) relay.stop();
  }
  bool active(unsigned relay_index) const {
    return relay_index < relays_.size() && relays_[relay_index].active();
  }
 private:
  PulsePolicy policy_;
  std::array<RelayStateMachine, 2> relays_{};
  std::array<uint64_t, kHistorySize> history_{};
  size_t next_history_ = 0;
};
}  // namespace facio
