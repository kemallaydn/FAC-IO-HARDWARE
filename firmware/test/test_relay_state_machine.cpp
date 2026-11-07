#include "../include/relay_state_machine.h"
#include <cassert>
#include <cstdint>
#include <limits>

using facio::RelayStateMachine;

int main() {
  RelayStateMachine relay;
  assert(!relay.active());
  assert(!relay.start(100, 0));
  assert(!relay.start(100, 99));
  assert(!relay.start(100, 1001));
  assert(!relay.active());

  assert(relay.start(100, 500));
  assert(relay.active());
  assert(!relay.start(200, 500));  // Never extend an active pulse.
  relay.tick(599);
  assert(relay.active());
  relay.tick(600);
  assert(!relay.active());
  assert(relay.start(700, 100));
  relay.stop();  // Simulates explicit fault/reset shutdown in caller.
  assert(!relay.active());

  // 32-bit millis() rollover must not make pulses stick ON.
  constexpr uint32_t near_wrap = std::numeric_limits<uint32_t>::max() - 50;
  assert(relay.start(near_wrap, 100));
  relay.tick(48);
  assert(relay.active());
  relay.tick(49);
  assert(!relay.active());
  return 0;
}
