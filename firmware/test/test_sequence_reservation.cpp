#include "../include/sequence_reservation.h"

#include <cassert>
#include <cstdint>
#include <limits>

using facio::Command;
using facio::Decision;
using facio::SequenceReservation;

namespace {
struct FakeStore {
  bool succeeds = true;
  uint32_t writes = 0;
  uint64_t value = 0;
};

bool persistReservation(void* context, uint64_t reserved_through) {
  auto* store = static_cast<FakeStore*>(context);
  ++store->writes;
  if (!store->succeeds) return false;
  store->value = reserved_through;
  return true;
}
}  // namespace

int main() {
  SequenceReservation window;
  FakeStore store;

  assert(window.accept({true, 1}, false, persistReservation, &store) ==
         Decision::Accepted);
  assert(store.writes == 1);
  assert(store.value == 256);
  assert(window.lastAcceptedSequence() == 1);
  assert(window.reservedThroughSequence() == 256);

  assert(window.accept({true, 2}, false, persistReservation, &store) ==
         Decision::Accepted);
  assert(store.writes == 1);  // No persistent write within the reserved block.
  assert(window.accept({true, 2}, false, persistReservation, &store) ==
         Decision::Replay);
  assert(window.accept({true, 3}, true, persistReservation, &store) ==
         Decision::Busy);
  assert(window.accept({false, 3}, false, persistReservation, &store) ==
         Decision::Unauthorized);
  assert(window.lastAcceptedSequence() == 2);

  // Restart skips the entire previously reserved block, including command
  // numbers accepted shortly before power loss.
  SequenceReservation restored;
  restored.restore(store.value);
  assert(restored.lastAcceptedSequence() == 256);
  assert(restored.accept({true, 2}, false, persistReservation, &store) ==
         Decision::Replay);
  assert(restored.accept({true, 257}, false, persistReservation, &store) ==
         Decision::Accepted);
  assert(store.writes == 2);
  assert(store.value == 512);

  SequenceReservation storage_failure;
  FakeStore failing_store;
  failing_store.succeeds = false;
  assert(storage_failure.accept({true, 1}, false, persistReservation,
                                &failing_store) ==
         Decision::PersistenceFailure);
  assert(storage_failure.lastAcceptedSequence() == 0);
  assert(storage_failure.reservedThroughSequence() == 0);

  SequenceReservation no_store;
  assert(no_store.accept({true, 1}, false, nullptr, nullptr) ==
         Decision::PersistenceFailure);
  assert(no_store.lastAcceptedSequence() == 0);

  SequenceReservation exhausted;
  const auto near_max = std::numeric_limits<uint64_t>::max() - 100;
  assert(exhausted.accept({true, near_max}, false, persistReservation, &store) ==
         Decision::SequenceExhausted);
  assert(exhausted.lastAcceptedSequence() == 0);
  return 0;
}
