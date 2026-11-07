#include "../include/relay_controller.h"
#include <cassert>
using namespace facio;
int main() {
  RelayController c;
  Request valid{true, 500, 123, 2000};
  assert(c.request(0, valid, 1000, 100) == Decision::Accepted);
  assert(c.active(0) && !c.active(1));
  assert(c.request(0, valid, 1000, 101) == Decision::Duplicate);
  assert(c.request(1, {false,500,124,2000}, 1000, 101) == Decision::Unauthorized);
  assert(c.request(1, {true,99,124,2000}, 1000, 101) == Decision::InvalidDuration);
  assert(c.request(0, {true,500,124,2000}, 1000, 101) == Decision::Busy);
  assert(c.request(1, {true,500,125,2000}, 2000, 101) == Decision::Expired);
  assert(c.request(1, {true,500,125,2000}, 1000, 101) == Decision::Accepted);
  c.tick(599); assert(c.active(0) && c.active(1));
  c.tick(600); assert(!c.active(0) && c.active(1));
  c.shutdown(); assert(!c.active(1));
  assert(c.request(1, {true,500,0,2000}, 1000, 900) == Decision::Duplicate);
  return 0;
}
