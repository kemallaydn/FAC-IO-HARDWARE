#include "../include/relay_controller_v2.h"
#include <cassert>
#include <cstdint>
#include <limits>
using namespace facio;
int main(){
 RelayControllerV2 c;
 assert(c.request(0,{true,500,1,2000},1000,100)==Decision::Accepted);
 assert(c.active(0));
 assert(c.request(1,{true,500,1,2000},1000,101)==Decision::Duplicate);
 assert(c.request(0,{true,500,2,2000},1000,101)==Decision::Busy);
 assert(c.request(1,{false,500,2,2000},1000,101)==Decision::Unauthorized);
 assert(c.request(1,{true,99,2,2000},1000,101)==Decision::InvalidDuration);
 assert(c.request(1,{true,500,2,1000},1000,101)==Decision::Expired);
 assert(c.request(2,{true,500,2,2000},1000,101)==Decision::InvalidRelay);
 assert(c.request(1,{true,500,2,2000},1000,101)==Decision::Accepted);
 c.tick(599);assert(c.active(0)&&c.active(1));
 c.tick(600);assert(!c.active(0)&&c.active(1));
 c.shutdown();assert(!c.active(1));
 const uint32_t wrap=std::numeric_limits<uint32_t>::max()-50;
 assert(c.request(0,{true,100,3,2000},1000,wrap)==Decision::Accepted);
 c.tick(48);assert(c.active(0));c.tick(49);assert(!c.active(0));
}
