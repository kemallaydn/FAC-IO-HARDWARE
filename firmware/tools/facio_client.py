#!/usr/bin/env python3
"""Small authenticated client for the FAC-IO candidate pulse API."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import hmac
import http.client
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import tempfile
from typing import NamedTuple

SEQUENCE_BLOCK_SIZE = 256
MAX_SEQUENCE = (1 << 64) - 1
DEVICE_ID_PATTERN = re.compile(r"^[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}$")


class PulseResult(NamedTuple):
    status: int
    body: str
    sequence: int


def normalize_device_id(device_id: str) -> str:
    if not DEVICE_ID_PATTERN.fullmatch(device_id):
        raise ValueError("device ID must be a six-byte MAC address")
    return device_id.upper()


def canonical_request(device_id: str, relay: str, sequence: int) -> bytes:
    device_id = normalize_device_id(device_id)
    if relay not in ("open", "close"):
        raise ValueError("relay must be 'open' or 'close'")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or not 1 <= sequence <= MAX_SEQUENCE:
        raise ValueError("sequence must be a positive uint64")
    channel = 1 if relay == "open" else 2
    path = f"/v1/relays/{channel}/pulse"
    return f"FACIO/1\nPOST\n{path}\n{device_id}\n{sequence}\n".encode("ascii")


def build_pulse_headers(device_id: str, relay: str, sequence: int,
                        key: bytes) -> dict[str, str]:
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError("device key must contain exactly 32 bytes")
    normalized_id = normalize_device_id(device_id)
    canonical = canonical_request(normalized_id, relay, sequence)
    signature = hmac.new(key, canonical, hashlib.sha256).hexdigest()
    return {
        "Connection": "close",
        "Content-Length": "0",
        "X-FACIO-Device": normalized_id,
        "X-FACIO-Sequence": str(sequence),
        "X-FACIO-Auth": signature,
    }


def _check_private_regular_file(path: Path, label: str) -> os.stat_result:
    try:
        details = path.lstat()
    except FileNotFoundError:
        raise
    if not stat.S_ISREG(details.st_mode):
        raise ValueError(f"{label} must be a regular file, not a symlink/device")
    if details.st_mode & 0o077:
        raise PermissionError(f"{label} permissions must be 0600 or stricter: {path}")
    if hasattr(os, "getuid") and details.st_uid != os.getuid():
        raise PermissionError(f"{label} must be owned by the current user: {path}")
    return details


def load_key(path: Path) -> bytes:
    _check_private_regular_file(path, "key file")
    key = path.read_bytes()
    if len(key) != 32:
        raise ValueError("key file must contain exactly 32 raw bytes")
    return key


def create_key_file(path: Path) -> str:
    key = secrets.token_bytes(32)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(key)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return "KEY:" + key.hex()


class SequenceStore:
    """Local monotonic sequence state, reserved before the network request."""

    def __init__(self, path: Path, device_id: str) -> None:
        self.path = path
        self.device_id = normalize_device_id(device_id)
        self.lock_path = path.with_name(path.name + ".lock")
        self._lock_file = None
        self.next_sequence = 1
        self.reserved_through = 0

    def __enter__(self) -> "SequenceStore":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        no_follow = getattr(os, "O_NOFOLLOW", 0)
        lock_fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT | no_follow, 0o600)
        os.fchmod(lock_fd, 0o600)
        self._lock_file = os.fdopen(lock_fd, "r+")
        fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX)
        try:
            self._read_state()
        except BaseException:
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None
            raise
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._lock_file is not None:
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None

    def _read_state(self) -> None:
        if not self.path.exists():
            self.next_sequence = 1
            self.reserved_through = 0
            return
        _check_private_regular_file(self.path, "sequence state")
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                raise ValueError("sequence state root must be an object")
            if state.get("version") != 1 or state.get("device_id") != self.device_id:
                raise ValueError("sequence state belongs to a different device or version")
            next_sequence = state.get("next_sequence")
            reserved_through = state.get("reserved_through")
            if (not isinstance(next_sequence, int) or isinstance(next_sequence, bool) or
                    not 1 <= next_sequence <= MAX_SEQUENCE):
                raise ValueError("sequence state next_sequence is invalid")
            if (not isinstance(reserved_through, int) or isinstance(reserved_through, bool) or
                    not 0 <= reserved_through <= MAX_SEQUENCE or
                    (reserved_through == 0 and next_sequence != 1) or
                    (reserved_through > 0 and next_sequence > reserved_through + 1)):
                raise ValueError("sequence state reserved_through is invalid")
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot read sequence state {self.path}: {error}") from error
        self.next_sequence = next_sequence
        self.reserved_through = reserved_through

    def _persist(self) -> None:
        payload = json.dumps({
            "version": 1,
            "device_id": self.device_id,
            "next_sequence": self.next_sequence,
            "reserved_through": self.reserved_through,
        }, sort_keys=True, separators=(",", ":")) + "\n"
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, self.path)
            directory_fd = os.open(self.path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
            raise

    def allocate(self) -> int:
        sequence = self.next_sequence
        if sequence > MAX_SEQUENCE - (SEQUENCE_BLOCK_SIZE - 1):
            raise OverflowError("sequence reservation exhausted")
        if sequence > self.reserved_through:
            self.reserved_through = sequence + SEQUENCE_BLOCK_SIZE - 1
        self.next_sequence = sequence + 1
        self._persist()
        return sequence

    def skip_reserved_block(self) -> None:
        if self.reserved_through == MAX_SEQUENCE:
            raise OverflowError("sequence reservation exhausted")
        self.next_sequence = self.reserved_through + 1
        self._persist()


def send_pulse(host: str, port: int, device_id: str, relay: str, key: bytes,
               sequence: int, timeout: float = 3.0) -> PulseResult:
    normalized_id = normalize_device_id(device_id)
    channel = 1 if relay == "open" else 2 if relay == "close" else 0
    if channel == 0:
        raise ValueError("relay must be 'open' or 'close'")
    path = f"/v1/relays/{channel}/pulse"
    headers = build_pulse_headers(normalized_id, relay, sequence, key)
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        connection.request("POST", path, body=b"", headers=headers)
        response = connection.getresponse()
        body = response.read(256).decode("utf-8", errors="replace").strip()
        return PulseResult(response.status, body, sequence)
    finally:
        connection.close()


def pulse_with_sequence_recovery(host: str, port: int, device_id: str,
                                 relay: str, key: bytes, store: SequenceStore,
                                 timeout: float) -> PulseResult:
    # Only an explicit server replay response is safe to recover automatically:
    # no trigger was accepted for that stale sequence. Never retry timeouts.
    for attempt in range(4):
        sequence = store.allocate()
        result = send_pulse(host, port, device_id, relay, key, sequence, timeout)
        if result.status != 409 or result.body != "replay" or attempt == 3:
            return result
        store.skip_reserved_block()
    raise RuntimeError("unreachable sequence recovery state")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    keygen = commands.add_parser("keygen", help="create a random per-device key file")
    keygen.add_argument("--key-file", type=Path, required=True)
    pulse = commands.add_parser("pulse", help="send one authenticated barrier pulse")
    pulse.add_argument("--host", required=True)
    pulse.add_argument("--port", type=int, default=80)
    pulse.add_argument("--device-id", required=True)
    pulse.add_argument("--relay", choices=("open", "close"), required=True)
    pulse.add_argument("--key-file", type=Path, required=True)
    pulse.add_argument("--state-file", type=Path)
    pulse.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args(argv)

    try:
        if args.command == "keygen":
            pairing_line = create_key_file(args.key_file)
            print(f"key_file={args.key_file}")
            print("pairing_line=" + pairing_line)
            print("Copy pairing_line to the USB serial console only after the physical BOOT press.")
            return 0

        key = load_key(args.key_file)
        device_id = normalize_device_id(args.device_id)
        state_file = args.state_file or args.key_file.with_name(
            args.key_file.name + "." + device_id.replace(":", "") + ".sequence.json"
        )
        with SequenceStore(state_file, device_id) as store:
            result = pulse_with_sequence_recovery(
                args.host, args.port, device_id, args.relay, key, store, args.timeout
            )
        print(f"http_status={result.status} sequence={result.sequence} response={result.body}")
        return 0 if result.status == 202 and result.body == "triggered" else 1
    except (OSError, ValueError, PermissionError, OverflowError,
            http.client.HTTPException, TimeoutError) as error:
        print(f"error={error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
