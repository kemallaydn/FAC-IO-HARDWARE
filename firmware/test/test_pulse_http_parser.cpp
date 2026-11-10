#include "../include/pulse_http_parser.h"

#include <cassert>
#include <cstdio>
#include <cstring>

using facio::HttpParseStatus;
using facio::PulseHttpRequest;

namespace {
constexpr char kGoodRequest[] =
    "POST /v1/relays/1/pulse HTTP/1.1\r\n"
    "Host: facio\r\n"
    "X-FACIO-Device: 02:11:22:33:44:55\r\n"
    "X-FACIO-Sequence: 42\r\n"
    "X-FACIO-Auth: da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf\r\n"
    "Content-Length: 0\r\n"
    "\r\n";

HttpParseStatus parse(const char* request, PulseHttpRequest* parsed) {
  return facio::parsePulseHttpRequest(request, std::strlen(request), parsed);
}
}  // namespace

int main() {
  PulseHttpRequest parsed;
  assert(parse(kGoodRequest, &parsed) == HttpParseStatus::Ok);
  assert(parsed.channel == facio::RelayChannel::Open);
  assert(parsed.sequence == 42);
  assert(std::strcmp(parsed.device_id, "02:11:22:33:44:55") == 0);
  assert(std::strcmp(
             parsed.signature_hex,
             "da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf") ==
         0);

  char request[sizeof(kGoodRequest) + 1]{};
  std::memcpy(request, kGoodRequest, sizeof(kGoodRequest));
  char* path = std::strstr(request, "/v1/relays/1/pulse");
  assert(path != nullptr);
  path[11] = '2';
  assert(parse(request, &parsed) == HttpParseStatus::Ok);
  assert(parsed.channel == facio::RelayChannel::Close);

  assert(facio::parsePulseHttpRequest(kGoodRequest, 12, &parsed) ==
         HttpParseStatus::Incomplete);
  assert(facio::parsePulseHttpRequest(kGoodRequest, std::strlen(kGoodRequest),
                                      nullptr) == HttpParseStatus::BadRequest);

  const char* get_request =
      "GET /v1/relays/1/pulse HTTP/1.1\r\nHost: facio\r\n\r\n";
  assert(parse(get_request, &parsed) == HttpParseStatus::MethodNotAllowed);
  const char* missing_auth =
      "POST /v1/relays/1/pulse HTTP/1.1\r\n"
      "X-FACIO-Device: 02:11:22:33:44:55\r\n"
      "X-FACIO-Sequence: 42\r\n\r\n";
  assert(parse(missing_auth, &parsed) == HttpParseStatus::BadRequest);
  const char* unknown_path =
      "POST /v1/unknown HTTP/1.1\r\nHost: facio\r\n\r\n";
  assert(parse(unknown_path, &parsed) == HttpParseStatus::NotFound);

  char malformed[sizeof(kGoodRequest) + 96]{};
  std::snprintf(malformed, sizeof(malformed),
                "POST /v1/relays/1/pulse HTTP/1.1\r\n"
                "X-FACIO-Device: 02:11:22:33:44:55\r\n"
                "X-FACIO-Sequence: 42\r\n"
                "X-FACIO-Sequence: 43\r\n"
                "X-FACIO-Auth: %064d\r\n\r\n",
                0);
  assert(parse(malformed, &parsed) == HttpParseStatus::BadRequest);

  const char* body_request =
      "POST /v1/relays/1/pulse HTTP/1.1\r\n"
      "X-FACIO-Device: 02:11:22:33:44:55\r\n"
      "X-FACIO-Sequence: 42\r\n"
      "X-FACIO-Auth: da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf\r\n"
      "Content-Length: 0\r\n\r\nX";
  assert(parse(body_request, &parsed) == HttpParseStatus::BadRequest);

  const char* transfer_request =
      "POST /v1/relays/1/pulse HTTP/1.1\r\n"
      "X-FACIO-Device: 02:11:22:33:44:55\r\n"
      "X-FACIO-Sequence: 42\r\n"
      "X-FACIO-Auth: da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf\r\n"
      "Transfer-Encoding: chunked\r\n\r\n";
  assert(parse(transfer_request, &parsed) == HttpParseStatus::BadRequest);

  const char* overflow_request =
      "POST /v1/relays/1/pulse HTTP/1.1\r\n"
      "X-FACIO-Device: 02:11:22:33:44:55\r\n"
      "X-FACIO-Sequence: 18446744073709551616\r\n"
      "X-FACIO-Auth: da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf\r\n\r\n";
  assert(parse(overflow_request, &parsed) == HttpParseStatus::BadRequest);
  return 0;
}
