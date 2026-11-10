#include "../include/pulse_http_parser.h"

#include <cstring>
#include <limits>

namespace facio {
namespace {
bool equalsIgnoreCase(const char* data, size_t length, const char* expected) {
  const size_t expected_length = std::strlen(expected);
  if (length != expected_length) return false;
  for (size_t index = 0; index < length; ++index) {
    char left = data[index];
    char right = expected[index];
    if (left >= 'A' && left <= 'Z') left = static_cast<char>(left + ('a' - 'A'));
    if (right >= 'A' && right <= 'Z') right = static_cast<char>(right + ('a' - 'A'));
    if (left != right) return false;
  }
  return true;
}

bool parseSequence(const char* data, size_t length, uint64_t* sequence) {
  if (data == nullptr || sequence == nullptr || length == 0 ||
      (length > 1 && data[0] == '0')) {
    return false;
  }

  uint64_t value = 0;
  for (size_t index = 0; index < length; ++index) {
    if (data[index] < '0' || data[index] > '9') return false;
    const uint8_t digit = static_cast<uint8_t>(data[index] - '0');
    if (value > (std::numeric_limits<uint64_t>::max() - digit) / 10) {
      return false;
    }
    value = value * 10 + digit;
  }
  if (value == 0) return false;
  *sequence = value;
  return true;
}

bool validDeviceId(const char* data, size_t length) {
  if (data == nullptr || length != 17) return false;
  for (size_t index = 0; index < length; ++index) {
    const char value = data[index];
    if (index % 3 == 2) {
      if (value != ':') return false;
    } else if (!((value >= '0' && value <= '9') ||
                 (value >= 'a' && value <= 'f') ||
                 (value >= 'A' && value <= 'F'))) {
      return false;
    }
  }
  return true;
}
}  // namespace

HttpParseStatus parsePulseHttpRequest(const char* data, size_t length,
                                      PulseHttpRequest* request) {
  if (data == nullptr || request == nullptr || length == 0 ||
      length > kMaxPulseHttpRequestBytes) {
    return HttpParseStatus::BadRequest;
  }

  size_t header_end = length;
  for (size_t index = 0; index + 3 < length; ++index) {
    if (data[index] == '\r' && data[index + 1] == '\n' &&
        data[index + 2] == '\r' && data[index + 3] == '\n') {
      header_end = index;
      break;
    }
  }
  if (header_end == length) return HttpParseStatus::Incomplete;
  if (header_end + 4 != length) return HttpParseStatus::BadRequest;

  for (size_t index = 0; index < length; ++index) {
    if (data[index] == '\0') return HttpParseStatus::BadRequest;
  }

  const size_t request_line_end = [&]() {
    for (size_t index = 0; index + 1 < header_end; ++index) {
      if (data[index] == '\r' && data[index + 1] == '\n') return index;
    }
    return header_end;
  }();
  if (request_line_end == header_end) return HttpParseStatus::BadRequest;

  const char* first_space = static_cast<const char*>(
      std::memchr(data, ' ', request_line_end));
  if (first_space == nullptr) return HttpParseStatus::BadRequest;
  const size_t method_length = static_cast<size_t>(first_space - data);
  const char* path = first_space + 1;
  const size_t remaining = request_line_end - (method_length + 1);
  const char* second_space = static_cast<const char*>(
      std::memchr(path, ' ', remaining));
  if (second_space == nullptr || second_space == path) {
    return HttpParseStatus::BadRequest;
  }
  const size_t path_length = static_cast<size_t>(second_space - path);
  const char* version = second_space + 1;
  const size_t version_length = request_line_end -
                                static_cast<size_t>(version - data);
  if (method_length != 4 || std::memcmp(data, "POST", 4) != 0) {
    return HttpParseStatus::MethodNotAllowed;
  }
  if (version_length != 8 || std::memcmp(version, "HTTP/1.1", 8) != 0) {
    return HttpParseStatus::BadRequest;
  }

  RelayChannel channel;
  if (path_length == std::strlen("/v1/relays/1/pulse") &&
      std::memcmp(path, "/v1/relays/1/pulse", path_length) == 0) {
    channel = RelayChannel::Open;
  } else if (path_length == std::strlen("/v1/relays/2/pulse") &&
             std::memcmp(path, "/v1/relays/2/pulse", path_length) == 0) {
    channel = RelayChannel::Close;
  } else {
    return HttpParseStatus::NotFound;
  }

  bool has_device = false;
  bool has_sequence = false;
  bool has_signature = false;
  bool has_content_length = false;
  uint64_t sequence = 0;
  char device_id[18]{};
  char signature_hex[kSha256HexChars + 1]{};

  size_t cursor = request_line_end + 2;
  size_t header_count = 0;
  while (cursor < header_end) {
    if (++header_count > 16) return HttpParseStatus::BadRequest;
    size_t line_end = cursor;
    while (line_end <= header_end &&
           !(data[line_end] == '\r' && data[line_end + 1] == '\n')) {
      ++line_end;
    }
    if (line_end > header_end || line_end == cursor) {
      return HttpParseStatus::BadRequest;
    }

    const char* line = data + cursor;
    const size_t line_length = line_end - cursor;
    const char* colon = static_cast<const char*>(
        std::memchr(line, ':', line_length));
    if (colon == nullptr || colon == line) return HttpParseStatus::BadRequest;
    const size_t name_length = static_cast<size_t>(colon - line);
    const char* value = colon + 1;
    size_t value_length = line_length - name_length - 1;
    while (value_length > 0 && (*value == ' ' || *value == '\t')) {
      ++value;
      --value_length;
    }
    while (value_length > 0 &&
           (value[value_length - 1] == ' ' || value[value_length - 1] == '\t')) {
      --value_length;
    }

    if (equalsIgnoreCase(line, name_length, "X-FACIO-Device")) {
      if (has_device || !validDeviceId(value, value_length)) {
        return HttpParseStatus::BadRequest;
      }
      std::memcpy(device_id, value, value_length);
      has_device = true;
    } else if (equalsIgnoreCase(line, name_length, "X-FACIO-Sequence")) {
      if (has_sequence || !parseSequence(value, value_length, &sequence)) {
        return HttpParseStatus::BadRequest;
      }
      has_sequence = true;
    } else if (equalsIgnoreCase(line, name_length, "X-FACIO-Auth")) {
      uint8_t parsed[kSha256Bytes]{};
      if (has_signature ||
          !parseSha256Hex(value, value_length, parsed)) {
        return HttpParseStatus::BadRequest;
      }
      std::memcpy(signature_hex, value, value_length);
      has_signature = true;
    } else if (equalsIgnoreCase(line, name_length, "Content-Length")) {
      if (has_content_length || value_length != 1 || value[0] != '0') {
        return HttpParseStatus::BadRequest;
      }
      has_content_length = true;
    } else if (equalsIgnoreCase(line, name_length, "Transfer-Encoding")) {
      return HttpParseStatus::BadRequest;
    }

    cursor = line_end + 2;
  }

  if (!has_device || !has_sequence || !has_signature) {
    return HttpParseStatus::BadRequest;
  }
  request->channel = channel;
  request->sequence = sequence;
  std::memcpy(request->device_id, device_id, sizeof(device_id));
  std::memcpy(request->signature_hex, signature_hex, sizeof(signature_hex));
  return HttpParseStatus::Ok;
}

}  // namespace facio
