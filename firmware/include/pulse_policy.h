#pragma once
#include <cstdint>

namespace facio {

// Pure decision logic; this module never drives a GPIO.
// Caller MUST authenticate the command before invoking this policy.
enum class Decision { Accepted, Unauthorized, InvalidDuration, Busy, Duplicate, Expired };
struct Request {
  bool authenticated;
  uint32_t duration_ms;
  uint64_t request_id;
  uint64_t expires_at_ms;
};
class PulsePolicy {
 public:
  static constexpr uint32_t kMinPulseMs = 100;
  static constexpr uint32_t kMaxPulseMs = 1000;
  Decision evaluate(const Request& req, uint64_t now_ms, bool relay_busy) const {
    if (!req.authenticated) return Decision::Unauthorized;
    if (req.duration_ms < kMinPulseMs || req.duration_ms > kMaxPulseMs)
      return Decision::InvalidDuration;
    if (req.expires_at_ms <= now_ms) return Decision::Expired;
    if (relay_busy) return Decision::Busy;
    // Deliberately no replay cache here. The caller must check and atomically
    // persist request IDs before accepting a command; otherwise FAIL CLOSED.
    return Decision::Accepted;
  }
};

}  // namespace facio
