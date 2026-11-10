#pragma once

#include "command_policy.h"

#include <cstdint>
#include <limits>

namespace facio {

// Persists a reservation ceiling before allowing commands in that sequence
// block. After a reboot, restoring that ceiling as the accepted floor skips
// every sequence that might have been accepted before power was lost, while
// amortizing nonvolatile writes across a block of commands.
class SequenceReservation {
 public:
  static constexpr uint64_t kReservationSize = 256;
  using Persist = bool (*)(void* context, uint64_t reserved_through);

  void restore(uint64_t reserved_through) {
    reserved_through_ = reserved_through;
    last_accepted_sequence_ = reserved_through;
  }

  Decision accept(const Command& command, bool any_relay_busy, Persist persist,
                  void* context) {
    const Decision policy_decision =
        policy_.evaluate(command, last_accepted_sequence_, any_relay_busy);
    if (policy_decision != Decision::Accepted) return policy_decision;

    if (command.sequence > reserved_through_) {
      constexpr uint64_t kReservationTail = kReservationSize - 1;
      if (command.sequence >
          std::numeric_limits<uint64_t>::max() - kReservationTail) {
        return Decision::SequenceExhausted;
      }

      const uint64_t new_reserved_through = command.sequence + kReservationTail;
      if (persist == nullptr || !persist(context, new_reserved_through)) {
        return Decision::PersistenceFailure;
      }
      reserved_through_ = new_reserved_through;
    }

    last_accepted_sequence_ = command.sequence;
    return Decision::Accepted;
  }

  uint64_t lastAcceptedSequence() const { return last_accepted_sequence_; }
  uint64_t reservedThroughSequence() const { return reserved_through_; }

 private:
  CommandPolicy policy_;
  uint64_t reserved_through_ = 0;
  uint64_t last_accepted_sequence_ = 0;
};

}  // namespace facio
