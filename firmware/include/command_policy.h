#pragma once

#include <cstdint>

namespace facio {

// Pure command checks only. Authentication is supplied by the caller; this
// class does not provide cryptography, persistence, transport or GPIO control.
enum class Decision {
  Accepted,
  Unauthorized,
  Replay,
  Busy,
  PersistenceFailure,
  SequenceExhausted,
};

struct Command {
  bool authenticated;
  uint64_t sequence;
};

class CommandPolicy {
 public:
  Decision evaluate(const Command& command, uint64_t last_accepted_sequence,
                    bool any_relay_busy) const {
    if (!command.authenticated) return Decision::Unauthorized;
    if (command.sequence == 0 ||
        command.sequence <= last_accepted_sequence) {
      return Decision::Replay;
    }
    if (any_relay_busy) return Decision::Busy;
    return Decision::Accepted;
  }
};

}  // namespace facio
