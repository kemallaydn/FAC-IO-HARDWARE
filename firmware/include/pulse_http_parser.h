#pragma once

#include "request_auth.h"

#include <cstddef>
#include <cstdint>

namespace facio {

enum class HttpParseStatus {
  Incomplete,
  Ok,
  BadRequest,
  NotFound,
  MethodNotAllowed,
};

struct PulseHttpRequest {
  RelayChannel channel = RelayChannel::Open;
  uint64_t sequence = 0;
  char device_id[18]{};
  char signature_hex[kSha256HexChars + 1]{};
};

constexpr size_t kMaxPulseHttpRequestBytes = 512;

HttpParseStatus parsePulseHttpRequest(const char* data, size_t length,
                                      PulseHttpRequest* request);

}  // namespace facio
