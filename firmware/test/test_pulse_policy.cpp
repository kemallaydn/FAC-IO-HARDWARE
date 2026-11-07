#include "../include/pulse_policy.h"
#include <cassert>
using namespace facio;

int main() {
  PulsePolicy p;
  const Request valid{true, 500, 42, 2000};
  assert(p.evaluate(valid, 1000, false) == Decision::Accepted);
  assert(p.evaluate({false, 500, 42, 2000}, 1000, false) == Decision::Unauthorized);
  assert(p.evaluate({true, 99, 42, 2000}, 1000, false) == Decision::InvalidDuration);
  assert(p.evaluate({true, 1001, 42, 2000}, 1000, false) == Decision::InvalidDuration);
  assert(p.evaluate(valid, 1000, true) == Decision::Busy);
  assert(p.evaluate(valid, 2000, false) == Decision::Expired);
  return 0;
}
