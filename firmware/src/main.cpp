#include <Arduino.h>
#include <Ethernet.h>
#include <Preferences.h>
#include <SPI.h>
#include <cstdio>
#include <cstring>
#include <esp_flash_encrypt.h>
#include <esp_secure_boot.h>
#include <esp_mac.h>

#include "../include/pulse_http_parser.h"
#include "../include/relay_state_machine.h"
#include "../include/request_auth.h"
#include "../include/sequence_reservation.h"

namespace {
constexpr uint8_t kSpiClockPin = 4;
constexpr uint8_t kSpiMisoPin = 6;
constexpr uint8_t kSpiMosiPin = 5;
constexpr uint8_t kEthernetCsPin = 7;
constexpr uint8_t kEthernetResetPin = 3;
constexpr uint8_t kRelayOpenTriggerPin = 0;
constexpr uint8_t kRelayCloseTriggerPin = 1;
constexpr uint8_t kBootButtonPin = 9;
constexpr uint32_t kHeartbeatIntervalMs = 5000;
constexpr uint32_t kDhcpRetryIntervalMs = 30000;
constexpr uint32_t kRequestTimeoutMs = 1000;
constexpr uint32_t kTriggerPulseMs = 10;
constexpr uint32_t kPairingWindowMs = 60000;

uint8_t ethernetMac[6]{};
uint8_t authKey[facio::kAuthKeyBytes]{};
uint32_t lastHeartbeatMs = 0;
uint32_t lastDhcpAttemptMs = 0;
uint32_t pairingStartedMs = 0;
uint32_t requestStartedMs = 0;
uint32_t triggerStartedMs = 0;
bool dhcpConfigured = false;
bool ethernetReady = false;
bool sequenceStorageReady = false;
bool secureRuntime = false;
bool authKeyReady = false;
bool commandServerReady = false;
bool requestActive = false;
bool triggerActive = false;
Preferences devicePreferences;
facio::SequenceReservation commandSequences;
facio::RelayStateMachine relayState;
EthernetServer commandServer(80);
EthernetClient activeClient;
char requestBuffer[facio::kMaxPulseHttpRequestBytes + 1]{};
size_t requestLength = 0;
char pairingBuffer[72]{};
size_t pairingLength = 0;
bool pairingEnabled = false;
bool pairingWindowOpen = false;

bool persistSequence(void*, uint64_t reservedThrough) {
  return devicePreferences.putULong64("seq_hi", reservedThrough) ==
         sizeof(uint64_t);
}

void initializeRelayTriggersInactive() {
  digitalWrite(kRelayOpenTriggerPin, LOW);
  digitalWrite(kRelayCloseTriggerPin, LOW);
  pinMode(kRelayOpenTriggerPin, OUTPUT);
  pinMode(kRelayCloseTriggerPin, OUTPUT);
  digitalWrite(kRelayOpenTriggerPin, LOW);
  digitalWrite(kRelayCloseTriggerPin, LOW);
}

bool initializePersistentState() {
  if (!devicePreferences.begin("facio", false)) return false;

  uint64_t reservedThrough = 0;
  if (devicePreferences.isKey("seq_hi")) {
    if (devicePreferences.getType("seq_hi") != PT_U64) return false;
    reservedThrough = devicePreferences.getULong64("seq_hi", 0);
  }
  commandSequences.restore(reservedThrough);

  const size_t keyLength = devicePreferences.getBytesLength("auth_key");
  if (keyLength == sizeof(authKey) &&
      devicePreferences.getBytes("auth_key", authKey, sizeof(authKey)) ==
          sizeof(authKey)) {
    authKeyReady = true;
  }
  return true;
}

bool loadLocalMac() {
  uint8_t baseMac[6]{};
  if (esp_read_mac(baseMac, ESP_MAC_WIFI_STA) != ESP_OK) return false;
  std::memcpy(ethernetMac, baseMac, sizeof(ethernetMac));
  ethernetMac[0] = static_cast<uint8_t>((ethernetMac[0] | 0x02U) & 0xFEU);
  return true;
}

void printMac() {
  Serial.printf("mac=%02X:%02X:%02X:%02X:%02X:%02X\n", ethernetMac[0],
                ethernetMac[1], ethernetMac[2], ethernetMac[3],
                ethernetMac[4], ethernetMac[5]);
}

void formatMac(char output[18]) {
  std::snprintf(output, 18, "%02X:%02X:%02X:%02X:%02X:%02X", ethernetMac[0],
                ethernetMac[1], ethernetMac[2], ethernetMac[3],
                ethernetMac[4], ethernetMac[5]);
}

bool deviceIdMatches(const char* requestId) {
  char localId[18]{};
  formatMac(localId);
  for (size_t index = 0; index < sizeof(localId); ++index) {
    char left = localId[index];
    char right = requestId[index];
    if (left >= 'a' && left <= 'f') left = static_cast<char>(left - 'a' + 'A');
    if (right >= 'a' && right <= 'f') right = static_cast<char>(right - 'a' + 'A');
    if (left != right) return false;
  }
  return true;
}

void writeResponse(EthernetClient& client, int status, const char* reason,
                   const char* body) {
  client.print("HTTP/1.1 ");
  client.print(status);
  client.print(' ');
  client.print(reason);
  client.print("\r\nContent-Type: text/plain\r\nConnection: close\r\nCache-Control: no-store\r\nContent-Length: ");
  client.print(std::strlen(body));
  client.print("\r\n\r\n");
  client.print(body);
}

void closeActiveClient() {
  activeClient.stop();
  requestActive = false;
  requestLength = 0;
  requestStartedMs = 0;
}

void processRequest() {
  facio::PulseHttpRequest request;
  const facio::HttpParseStatus status =
      facio::parsePulseHttpRequest(requestBuffer, requestLength, &request);
  if (status != facio::HttpParseStatus::Ok) {
    if (status == facio::HttpParseStatus::MethodNotAllowed) {
      writeResponse(activeClient, 405, "Method Not Allowed", "method_not_allowed\n");
    } else if (status == facio::HttpParseStatus::NotFound) {
      writeResponse(activeClient, 404, "Not Found", "not_found\n");
    } else {
      writeResponse(activeClient, 400, "Bad Request", "bad_request\n");
    }
    return;
  }

  if (!deviceIdMatches(request.device_id) ||
      !facio::verifyPulseHmacSha256(authKey, sizeof(authKey), request.device_id,
                                    request.channel, request.sequence,
                                    request.signature_hex,
                                    std::strlen(request.signature_hex))) {
    writeResponse(activeClient, 401, "Unauthorized", "unauthorized\n");
    return;
  }

  const facio::Command command{true, request.sequence};
  const facio::Decision decision = commandSequences.accept(
      command, relayState.busy(), persistSequence, nullptr);
  if (decision != facio::Decision::Accepted) {
    if (decision == facio::Decision::Busy) {
      writeResponse(activeClient, 409, "Conflict", "busy\n");
    } else if (decision == facio::Decision::PersistenceFailure) {
      writeResponse(activeClient, 503, "Service Unavailable", "storage_failure\n");
    } else if (decision == facio::Decision::SequenceExhausted) {
      writeResponse(activeClient, 409, "Conflict", "sequence_exhausted\n");
    } else {
      writeResponse(activeClient, 409, "Conflict", "replay\n");
    }
    return;
  }

  const uint32_t now = millis();
  if (!relayState.start(now)) {
    writeResponse(activeClient, 409, "Conflict", "busy\n");
    return;
  }
  const uint8_t triggerPin = request.channel == facio::RelayChannel::Open
                                 ? kRelayOpenTriggerPin
                                 : kRelayCloseTriggerPin;
  digitalWrite(triggerPin, HIGH);
  triggerStartedMs = now;
  triggerActive = true;
  writeResponse(activeClient, 202, "Accepted", "triggered\n");
}

void serviceCommandServer(uint32_t now) {
  if (!commandServerReady || !dhcpConfigured || Ethernet.linkStatus() != LinkON) {
    if (requestActive) closeActiveClient();
    return;
  }

  if (!requestActive) {
    EthernetClient candidate = commandServer.accept();
    if (!candidate) return;
    activeClient = candidate;
    requestActive = true;
    requestLength = 0;
    requestStartedMs = now;
  }

  while (activeClient.available() > 0) {
    const int incoming = activeClient.read();
    if (incoming < 0) break;
    if (requestLength >= facio::kMaxPulseHttpRequestBytes) {
      writeResponse(activeClient, 413, "Content Too Large", "request_too_large\n");
      closeActiveClient();
      return;
    }
    requestBuffer[requestLength++] = static_cast<char>(incoming);
    requestBuffer[requestLength] = '\0';
    if (requestLength >= 4 &&
        std::strstr(requestBuffer, "\r\n\r\n") != nullptr) {
      processRequest();
      closeActiveClient();
      return;
    }
  }

  if (!activeClient.connected() || now - requestStartedMs >= kRequestTimeoutMs) {
    if (requestLength > 0 && requestLength < facio::kMaxPulseHttpRequestBytes) {
      // The parser distinguishes an incomplete request from malformed data.
      facio::PulseHttpRequest ignored;
      if (facio::parsePulseHttpRequest(requestBuffer, requestLength, &ignored) ==
          facio::HttpParseStatus::Incomplete) {
        writeResponse(activeClient, 400, "Bad Request", "incomplete_request\n");
      }
    }
    closeActiveClient();
  }
}

void servicePairing(uint32_t now) {
  if (!pairingEnabled) {
    return;
  }
  if (!pairingWindowOpen) {
    if (digitalRead(kBootButtonPin) != LOW) return;
    pairingStartedMs = now;
    pairingWindowOpen = true;
    Serial.println("pairing=physical_window_open; send KEY:<64 hex chars> within 60s");
  }
  if (now - pairingStartedMs >= kPairingWindowMs) {
    pairingEnabled = false;
    pairingWindowOpen = false;
    std::memset(pairingBuffer, 0, sizeof(pairingBuffer));
    pairingLength = 0;
    Serial.println("pairing=window_closed");
    return;
  }
  while (Serial.available() > 0) {
    const int incoming = Serial.read();
    if (incoming < 0) return;
    if (incoming == '\r') continue;
    if (incoming == '\n') {
      pairingBuffer[pairingLength] = '\0';
      uint8_t newKey[facio::kAuthKeyBytes]{};
      if (pairingLength == 68 && std::memcmp(pairingBuffer, "KEY:", 4) == 0 &&
          facio::parseSha256Hex(pairingBuffer + 4, 64, newKey)) {
        const size_t stored = devicePreferences.putBytes("auth_key", newKey,
                                                         sizeof(newKey));
        uint8_t check[facio::kAuthKeyBytes]{};
        if (stored == sizeof(newKey) &&
            devicePreferences.getBytes("auth_key", check, sizeof(check)) ==
                sizeof(check) && facio::constantTimeEqual(newKey, check, sizeof(check))) {
          std::memcpy(authKey, check, sizeof(authKey));
          authKeyReady = true;
          commandServerReady = false;
          Serial.println("pairing=complete; reboot_required=1");
        } else {
          Serial.println("pairing=storage_failure");
        }
        std::memset(newKey, 0, sizeof(newKey));
      } else {
        Serial.println("pairing=invalid_key_format");
      }
      std::memset(pairingBuffer, 0, sizeof(pairingBuffer));
      pairingLength = 0;
      pairingEnabled = false;
      return;
    }
    if (pairingLength >= sizeof(pairingBuffer) - 1) {
      std::memset(pairingBuffer, 0, sizeof(pairingBuffer));
      pairingLength = 0;
      pairingEnabled = false;
      Serial.println("pairing=input_too_long");
      return;
    }
    pairingBuffer[pairingLength++] = static_cast<char>(incoming);
  }
}

void attemptDhcp(uint32_t now) {
  lastDhcpAttemptMs = now;
  Serial.println("dhcp=starting");
  dhcpConfigured = Ethernet.begin(ethernetMac) == 1;
  Serial.printf("dhcp=%s\n", dhcpConfigured ? "configured" : "failed");
}

void printNetworkStatus(uint32_t now) {
  const EthernetLinkStatus link = Ethernet.linkStatus();
  const char* linkText = "unknown";
  if (link == LinkON) linkText = "up";
  else if (link == LinkOFF) linkText = "down";
  const bool commandsOnline = commandServerReady && dhcpConfigured &&
                              link == LinkON;
  const IPAddress ip = Ethernet.localIP();
  Serial.printf("uptime_ms=%lu link=%s dhcp=%s ip=%u.%u.%u.%u secure=%s key=%s commands=%s relay_guard=%s trigger=%s\n",
                static_cast<unsigned long>(now), linkText,
                dhcpConfigured ? "configured" : "unavailable", ip[0], ip[1],
                ip[2], ip[3], secureRuntime ? "yes" : "no",
                authKeyReady ? "provisioned" : "missing",
                commandsOnline ? "online" : "gated",
                relayState.busy() ? "busy" : "ready",
                triggerActive ? "asserted" : "inactive");
}
}  // namespace

void setup() {
  initializeRelayTriggersInactive();
  pinMode(kBootButtonPin, INPUT_PULLUP);
  Serial.begin(115200);
  delay(100);
  Serial.println("FAC-IO Mini V1 / W5500 / authenticated pulse API");

  secureRuntime = esp_secure_boot_enabled() &&
                  esp_flash_encryption_enabled();
  Serial.printf("secure_runtime=%s\n", secureRuntime ? "enabled" : "disabled");
  sequenceStorageReady = initializePersistentState();
  Serial.printf("persistent_state=%s\n",
                sequenceStorageReady ? "ready" : "failed_closed");
  pairingEnabled = secureRuntime && sequenceStorageReady;

  digitalWrite(kEthernetResetPin, LOW);
  pinMode(kEthernetResetPin, OUTPUT);
  delay(1);
  digitalWrite(kEthernetResetPin, HIGH);
  delay(50);
  SPI.begin(kSpiClockPin, kSpiMisoPin, kSpiMosiPin, kEthernetCsPin);
  Ethernet.init(kEthernetCsPin);
  if (Ethernet.hardwareStatus() == EthernetNoHardware) {
    Serial.println("fatal=w5500_not_detected ethernet=disabled");
    return;
  }
  if (!loadLocalMac()) {
    Serial.println("fatal=unable_to_read_factory_mac ethernet=disabled");
    return;
  }
  ethernetReady = true;
  printMac();
  attemptDhcp(millis());

  commandServerReady = secureRuntime && sequenceStorageReady && authKeyReady;
  if (commandServerReady) {
    commandServer.begin();
    Serial.println("command_server=ready port=80 auth=hmac-sha256 replay=protected");
  } else {
    Serial.println("command_server=disabled reason=security_or_provisioning_gate");
  }
}

void loop() {
  const uint32_t now = millis();
  servicePairing(now);
  relayState.tick(now);
  if (triggerActive && now - triggerStartedMs >= kTriggerPulseMs) {
    digitalWrite(kRelayOpenTriggerPin, LOW);
    digitalWrite(kRelayCloseTriggerPin, LOW);
    triggerActive = false;
  }

  if (ethernetReady) {
    if (dhcpConfigured) {
      const int maintainResult = Ethernet.maintain();
      if (maintainResult == 2 || maintainResult == 4) dhcpConfigured = false;
    } else if (now - lastDhcpAttemptMs >= kDhcpRetryIntervalMs) {
      attemptDhcp(now);
    }
    serviceCommandServer(now);
  }

  if (now - lastHeartbeatMs >= kHeartbeatIntervalMs) {
    lastHeartbeatMs = now;
    printNetworkStatus(now);
  }
  delay(2);
}
