from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import facio_client


class FacioClientTests(unittest.TestCase):
    def test_hmac_matches_documented_cross_language_vector(self):
        key = bytes(range(32))
        headers = facio_client.build_pulse_headers(
            "02:11:22:33:44:55", "open", 42, key
        )
        self.assertEqual(
            "da87663161f843060887c86a07ae473afcfb5408a30cf37ad86dfcdf8d3bc4cf",
            headers["X-FACIO-Auth"],
        )
        self.assertEqual("02:11:22:33:44:55", headers["X-FACIO-Device"])
        self.assertEqual("42", headers["X-FACIO-Sequence"])

    def test_invalid_device_relay_sequence_and_key_are_rejected(self):
        key = bytes(range(32))
        for device_id, relay, sequence, candidate_key in (
            ("not-a-mac", "open", 1, key),
            ("02:11:22:33:44:55", "stop", 1, key),
            ("02:11:22:33:44:55", "open", 0, key),
            ("02:11:22:33:44:55", "open", 1, b"short"),
        ):
            with self.subTest(device_id=device_id, relay=relay, sequence=sequence):
                with self.assertRaises(ValueError):
                    facio_client.build_pulse_headers(
                        device_id, relay, sequence, candidate_key
                    )

    def test_sequence_is_persisted_before_use_and_survives_process_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "device.sequence.json"
            with facio_client.SequenceStore(path, "02:11:22:33:44:55") as store:
                self.assertEqual(1, store.allocate())
                self.assertEqual(2, store.next_sequence)
                self.assertEqual(256, store.reserved_through)
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            with facio_client.SequenceStore(path, "02:11:22:33:44:55") as store:
                self.assertEqual(2, store.allocate())
                store.skip_reserved_block()
                self.assertEqual(257, store.allocate())
                self.assertEqual(512, store.reserved_through)

    def test_explicit_replay_response_skips_reserved_block_once(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "device.sequence.json"
            with facio_client.SequenceStore(path, "02:11:22:33:44:55") as store:
                with patch.object(
                    facio_client,
                    "send_pulse",
                    side_effect=(
                        facio_client.PulseResult(409, "replay", 1),
                        facio_client.PulseResult(202, "triggered", 257),
                    ),
                ) as send:
                    result = facio_client.pulse_with_sequence_recovery(
                        "192.0.2.1", 80, "02:11:22:33:44:55", "open",
                        bytes(range(32)), store, 1.0,
                    )
            self.assertEqual(facio_client.PulseResult(202, "triggered", 257), result)
            self.assertEqual([1, 257], [call.args[5] for call in send.call_args_list])

    def test_network_timeout_is_not_retried_and_sequence_stays_consumed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "device.sequence.json"
            with facio_client.SequenceStore(path, "02:11:22:33:44:55") as store:
                with patch.object(facio_client, "send_pulse", side_effect=TimeoutError) as send:
                    with self.assertRaises(TimeoutError):
                        facio_client.pulse_with_sequence_recovery(
                            "192.0.2.1", 80, "02:11:22:33:44:55", "open",
                            bytes(range(32)), store, 1.0,
                        )
                    self.assertEqual(1, send.call_count)
                self.assertEqual(2, store.next_sequence)

    def test_keygen_creates_private_random_key_and_usb_pairing_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unit.key"
            pairing_line = facio_client.create_key_file(path)
            key = path.read_bytes()
            self.assertEqual(32, len(key))
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual("KEY:" + key.hex(), pairing_line)
            with self.assertRaises(FileExistsError):
                facio_client.create_key_file(path)

    def test_http_client_sends_signed_fixed_route_to_local_mock(self):
        key = bytes(range(32))
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["path"] = self.path
                received["length"] = self.headers.get("Content-Length")
                received["device"] = self.headers.get("X-FACIO-Device")
                received["sequence"] = self.headers.get("X-FACIO-Sequence")
                received["signature"] = self.headers.get("X-FACIO-Auth")
                self.send_response(202)
                self.send_header("Content-Length", "9")
                self.end_headers()
                self.wfile.write(b"triggered\n")

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = facio_client.send_pulse(
                "127.0.0.1", server.server_port, "02:11:22:33:44:55",
                "close", key, 43, timeout=1.0,
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=1.0)

        self.assertEqual(facio_client.PulseResult(202, "triggered", 43), result)
        self.assertEqual("/v1/relays/2/pulse", received["path"])
        self.assertEqual("0", received["length"])
        self.assertEqual("02:11:22:33:44:55", received["device"])
        self.assertEqual("43", received["sequence"])
        self.assertEqual(
            facio_client.build_pulse_headers(
                "02:11:22:33:44:55", "close", 43, key
            )["X-FACIO-Auth"],
            received["signature"],
        )


if __name__ == "__main__":
    unittest.main()
