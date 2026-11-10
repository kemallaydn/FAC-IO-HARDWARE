#include "../include/request_auth.h"

#include <mbedtls/md.h>

namespace facio {

bool verifyPulseHmacSha256(const uint8_t* key, size_t key_length,
                           const char* device_id, RelayChannel channel,
                           uint64_t sequence, const char* signature_hex,
                           size_t signature_length) {
  if (key == nullptr || key_length != kAuthKeyBytes || signature_hex == nullptr ||
      signature_length != kSha256HexChars) {
    return false;
  }

  char canonical[96]{};
  size_t canonical_length = 0;
  uint8_t supplied[kSha256Bytes]{};
  uint8_t expected[kSha256Bytes]{};
  if (!buildPulseCanonicalRequest(device_id, channel, sequence, canonical,
                                  sizeof(canonical), &canonical_length) ||
      !parseSha256Hex(signature_hex, signature_length, supplied)) {
    return false;
  }

  const mbedtls_md_info_t* sha256 =
      mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
  if (sha256 == nullptr ||
      mbedtls_md_hmac(sha256, key, key_length,
                      reinterpret_cast<const unsigned char*>(canonical),
                      canonical_length, expected) != 0) {
    return false;
  }
  return constantTimeEqual(supplied, expected, sizeof(expected));
}

}  // namespace facio
