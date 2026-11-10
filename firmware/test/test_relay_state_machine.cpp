#include "../include/relay_state_machine.h"

#include <cassert>
#include <cstdint>
#include <limits>

using facio::RelayStateMachine;

int main() {
  RelayStateMachine channel;
  assert(!channel.busy());
  assert(channel.start(100));
  assert(channel.busy());
  assert(!channel.start(200));
  channel.tick(699);
  assert(channel.busy());
  channel.tick(700);
  assert(!channel.busy());

  assert(channel.start(800));
  channel.shutdown();
  assert(!channel.busy());

  constexpr uint32_t near_wrap = std::numeric_limits<uint32_t>::max() - 300;
  assert(channel.start(near_wrap));
  channel.tick(298);
  assert(channel.busy());
  channel.tick(299);
  assert(!channel.busy());
  return 0;
}
