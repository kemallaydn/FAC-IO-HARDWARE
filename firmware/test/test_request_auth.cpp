#include "../include/request_auth.h"

#include <array>
#include <cassert>
#include <cstring>

using facio::RelayChannel;

int main() {
  constexpr const char* device_id = "02:11:22:33:44:55";
  char canonical[96]{};
  size_t canonical_length = 0;
  assert(facio::buildPulseCanonicalRequest(
      device_id, RelayChannel::Open, 42, canonical, sizeof(canonical),
      &canonical_length));
  constexpr const char* expected =
      "FACIO/1\nPOST\n/v1/relays/1/pulse\n02:11:22:33:44:55\n42\n";
  assert(canonical_length == std::strlen(expected));
  assert(std::memcmp(canonical, expected, canonical_length) == 0);

  assert(facio::buildPulseCanonicalRequest(
      device_id, RelayChannel::Close, 43, canonical, sizeof(canonical),
      &canonical_length));
  assert(std::strstr(canonical, "/v1/relays/2/pulse") != nullptr);

  assert(!facio::buildPulseCanonicalRequest(
      "02:11:22:33:44:GG", RelayChannel::Open, 1, canonical, sizeof(canonical),
      &canonical_length));
  assert(!facio::buildPulseCanonicalRequest(
      device_id, RelayChannel::Open, 0, canonical, sizeof(canonical),
      &canonical_length));
  assert(!facio::buildPulseCanonicalRequest(
      device_id, static_cast<RelayChannel>(3), 1, canonical, sizeof(canonical),
      &canonical_length));
  assert(!facio::buildPulseCanonicalRequest(
      device_id, RelayChannel::Open, 42, canonical, 8, &canonical_length));

  constexpr const char* digest_hex =
      "000102030405060708090a0b0c0d0e0f"
      "101112131415161718191a1b1c1d1e1f";
  std::array<uint8_t, facio::kSha256Bytes> digest{};
  assert(facio::parseSha256Hex(digest_hex, std::strlen(digest_hex), digest.data()));
  for (size_t i = 0; i < digest.size(); ++i) {
    assert(digest[i] == static_cast<uint8_t>(i));
  }
  assert(facio::parseSha256Hex(
      "000102030405060708090A0B0C0D0E0F"
      "101112131415161718191A1B1C1D1E1F",
      facio::kSha256HexChars, digest.data()));
  assert(!facio::parseSha256Hex("0x", 2, digest.data()));
  assert(!facio::parseSha256Hex("gg00000000000000000000000000000000000000000000000000000000000000",
                                facio::kSha256HexChars, digest.data()));

  auto equal = digest;
  assert(facio::constantTimeEqual(digest.data(), equal.data(), digest.size()));
  equal[31] ^= 1;
  assert(!facio::constantTimeEqual(digest.data(), equal.data(), digest.size()));
  assert(!facio::constantTimeEqual(nullptr, digest.data(), digest.size()));

  std::array<uint8_t, facio::kAuthKeyBytes> key{};
  for (size_t i = 0; i < key.size(); ++i) key[i] = static_cast<uint8_t>(i);
  constexpr const char* signature =
      "da87663161f843060887c86a07ae473a"
      "fcfb5408a30cf37ad86dfcdf8d3bc4cf";
  assert(facio::verifyPulseHmacSha256(
      key.data(), key.size(), device_id, RelayChannel::Open, 42, signature,
      facio::kSha256HexChars));
  assert(!facio::verifyPulseHmacSha256(
      key.data(), key.size(), device_id, RelayChannel::Close, 42, signature,
      facio::kSha256HexChars));
  assert(!facio::verifyPulseHmacSha256(
      key.data(), key.size() - 1, device_id, RelayChannel::Open, 42, signature,
      facio::kSha256HexChars));
  return 0;
}
