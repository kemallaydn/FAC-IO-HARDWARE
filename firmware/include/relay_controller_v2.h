#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
namespace facio {
enum class Decision { Accepted, Unauthorized, InvalidDuration, Busy, Duplicate, Expired, InvalidRelay };
struct Request { bool authenticated; uint32_t duration_ms; uint64_t request_id; uint64_t expires_at_ms; };
class RelayControllerV2 {
 public:
  static constexpr uint32_t kMinPulseMs=100, kMaxPulseMs=1000;
  static constexpr size_t kHistorySize=16;
  Decision request(unsigned index, const Request& r, uint64_t now, uint32_t tick) {
    if(index>=2) return Decision::InvalidRelay;
    if(!r.authenticated) return Decision::Unauthorized;
    if(r.duration_ms<kMinPulseMs || r.duration_ms>kMaxPulseMs) return Decision::InvalidDuration;
    if(r.expires_at_ms<=now) return Decision::Expired;
    if(r.request_id==0) return Decision::Duplicate;
    for(uint64_t id:history_) if(id==r.request_id) return Decision::Duplicate;
    if(relays_[index].active) return Decision::Busy;
    relays_[index]={true,tick,r.duration_ms};
    history_[next_]=r.request_id;
    next_=(next_+1)%kHistorySize;
    return Decision::Accepted;
  }
  void tick(uint32_t now) {
    for(auto& r:relays_) if(r.active && uint32_t(now-r.started)>=r.duration) r.active=false;
  }
  void shutdown() { for(auto& r:relays_) r.active=false; }
  bool active(unsigned i) const { return i<2 && relays_[i].active; }
 private:
  struct Relay {bool active=false; uint32_t started=0; uint32_t duration=0;};
  std::array<Relay,2> relays_{};
  std::array<uint64_t,kHistorySize> history_{};
  size_t next_=0;
};
}
