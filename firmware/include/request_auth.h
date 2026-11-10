#pragma once

#include <cstddef>
#include <cstdint>

namespace facio {

enum class RelayChannel : uint8_t { Open = 1, Close = 2 };

constexpr size_t kAuthKeyBytes = 32;
constexpr size_t kSha256Bytes = 32;
constexpr size_t kSha256HexChars = kSha256Bytes * 2;

bool buildPulseCanonicalRequest(const char* device_id, RelayChannel channel,
                                uint64_t sequence, char* output,
                                size_t output_capacity, size_t* output_length);
bool parseSha256Hex(const char* input, size_t input_length,
                    uint8_t output[kSha256Bytes]);
bool constantTimeEqual(const uint8_t* left, const uint8_t* right,
                       size_t length);
bool verifyPulseHmacSha256(const uint8_t* key, size_t key_length,
                           const char* device_id, RelayChannel channel,
                           uint64_t sequence, const char* signature_hex,
                           size_t signature_length);

}  // namespace facio
