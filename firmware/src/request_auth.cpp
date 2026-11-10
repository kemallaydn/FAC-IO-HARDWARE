#include "../include/request_auth.h"

#include <cstdio>
#include <cstring>

namespace facio {
namespace {
int hexValue(char character) {
  if (character >= '0' && character <= '9') return character - '0';
  if (character >= 'a' && character <= 'f') return character - 'a' + 10;
  if (character >= 'A' && character <= 'F') return character - 'A' + 10;
  return -1;
}

bool validDeviceId(const char* device_id) {
  if (device_id == nullptr || std::strlen(device_id) != 17) return false;
  for (size_t index = 0; index < 17; ++index) {
    if (index % 3 == 2) {
      if (device_id[index] != ':') return false;
    } else if (hexValue(device_id[index]) < 0) {
      return false;
    }
  }
  return true;
}
}  // namespace

bool buildPulseCanonicalRequest(const char* device_id, RelayChannel channel,
                                uint64_t sequence, char* output,
                                size_t output_capacity, size_t* output_length) {
  if (!validDeviceId(device_id) || sequence == 0 || output == nullptr ||
      output_capacity == 0 || output_length == nullptr) {
    return false;
  }

  const char* path = nullptr;
  switch (channel) {
    case RelayChannel::Open:
      path = "/v1/relays/1/pulse";
      break;
    case RelayChannel::Close:
      path = "/v1/relays/2/pulse";
      break;
    default:
      return false;
  }

  const int length = std::snprintf(
      output, output_capacity, "FACIO/1\nPOST\n%s\n%s\n%llu\n", path,
      device_id, static_cast<unsigned long long>(sequence));
  if (length < 0 || static_cast<size_t>(length) >= output_capacity) {
    return false;
  }
  *output_length = static_cast<size_t>(length);
  return true;
}

bool parseSha256Hex(const char* input, size_t input_length,
                    uint8_t output[kSha256Bytes]) {
  if (input == nullptr || output == nullptr ||
      input_length != kSha256HexChars) {
    return false;
  }

  uint8_t parsed[kSha256Bytes]{};
  for (size_t index = 0; index < kSha256Bytes; ++index) {
    const int high = hexValue(input[index * 2]);
    const int low = hexValue(input[index * 2 + 1]);
    if (high < 0 || low < 0) return false;
    parsed[index] = static_cast<uint8_t>((high << 4) | low);
  }
  std::memcpy(output, parsed, sizeof(parsed));
  return true;
}

bool constantTimeEqual(const uint8_t* left, const uint8_t* right,
                       size_t length) {
  if (left == nullptr || right == nullptr) return false;
  uint8_t difference = 0;
  for (size_t index = 0; index < length; ++index) {
    difference |= static_cast<uint8_t>(left[index] ^ right[index]);
  }
  return difference == 0;
}

}  // namespace facio
