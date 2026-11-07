#include <Arduino.h>

// FAC-IO prototype firmware: SAFE DEFAULTS ONLY.
// The provisional PCB pin mapping is NOT approved. Do not connect real
// barrier equipment or relay driver hardware until schematic and pin review.
// This diagnostic does not energize any relay, nor accept network commands.

namespace {
constexpr uint32_t kHeartbeatMs = 5000;
uint32_t lastHeartbeatMs = 0;
}

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("FAC-IO Mini V1 / firmware bring-up / NO RELAY CONTROL");
}

void loop() {
  const uint32_t now = millis();
  if (now - lastHeartbeatMs >= kHeartbeatMs) {
    lastHeartbeatMs = now;
    Serial.printf("uptime_ms=%lu mode=diagnostic relays=disabled\n",
                  static_cast<unsigned long>(now));
  }
  delay(10);
}
