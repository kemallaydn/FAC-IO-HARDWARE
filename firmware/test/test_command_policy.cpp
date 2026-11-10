#include "../include/command_policy.h"

#include <cassert>
#include <cstdint>

using facio::Command;
using facio::CommandPolicy;
using facio::Decision;

int main() {
  const CommandPolicy policy;
  assert(policy.evaluate({true, 42}, 41, false) == Decision::Accepted);
  assert(policy.evaluate({false, 42}, 41, false) == Decision::Unauthorized);
  assert(policy.evaluate({true, 0}, 0, false) == Decision::Replay);
  assert(policy.evaluate({true, 42}, 42, false) == Decision::Replay);
  assert(policy.evaluate({true, 42}, 43, false) == Decision::Replay);
  assert(policy.evaluate({true, UINT64_MAX}, 42, true) == Decision::Busy);
  return 0;
}
