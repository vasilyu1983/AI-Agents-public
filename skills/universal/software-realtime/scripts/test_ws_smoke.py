"""Offline regression checks for WebSocket smoke-test false successes."""

from __future__ import annotations

import unittest
from unittest import mock

import check_ws_smoke
import ws_smoke_test


class FakeSocket:
    def __init__(self, response: bytes):
        self.response = response

    def settimeout(self, timeout: float) -> None:
        pass

    def sendall(self, request: bytes) -> None:
        pass

    def recv(self, size: int) -> bytes:
        response, self.response = self.response, b""
        return response

    def close(self) -> None:
        pass


class ValidHandshakeSocket(FakeSocket):
    def __init__(self) -> None:
        super().__init__(b"")

    def sendall(self, request: bytes) -> None:
        key = next(line.split(b":", 1)[1].strip().decode("ascii") for line in request.split(b"\r\n") if line.startswith(b"Sec-WebSocket-Key:"))
        accept = check_ws_smoke._expected_accept(key)
        self.response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\nConnection: keep-alive, Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        ).encode("ascii")


class SmokeTest(unittest.TestCase):
    def test_accepts_complete_handshake(self) -> None:
        fake = ValidHandshakeSocket()
        with mock.patch.object(check_ws_smoke.socket, "create_connection", return_value=fake):
            ok, message = check_ws_smoke.smoke_raw("ws://example.invalid/ws", 1)
        self.assertTrue(ok, message)

    def test_rejects_101_without_accept_header(self) -> None:
        # Old behavior returned success solely because the status line contained 101.
        fake = FakeSocket(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
        with mock.patch.object(check_ws_smoke.socket, "create_connection", return_value=fake):
            ok, message = check_ws_smoke.smoke_raw("ws://example.invalid/ws", 1)
        self.assertFalse(ok, message)
        self.assertIn("Sec-WebSocket-Accept", message)

    def test_rejects_101_without_upgrade_header(self) -> None:
        key = "AAAAAAAAAAAAAAAAAAAAAA=="
        accept = check_ws_smoke._expected_accept(key)
        response = f"HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: {accept}\r\n\r\n".encode()
        fake = FakeSocket(response)
        with mock.patch.object(check_ws_smoke.os, "urandom", return_value=b"\x00" * 16), mock.patch.object(check_ws_smoke.socket, "create_connection", return_value=fake):
            ok, message = check_ws_smoke.smoke_raw("ws://example.invalid/ws", 1)
        self.assertFalse(ok, message)
        self.assertIn("Upgrade", message)

    def test_send_does_not_fall_back_to_handshake(self) -> None:
        with mock.patch.object(check_ws_smoke.importlib.util, "find_spec", return_value=None):
            with self.assertRaises(SystemExit) as caught:
                check_ws_smoke.parse_args(["--url", "ws://example.invalid/ws", "--send", "ping"])
        self.assertEqual(caught.exception.code, 2)

    def test_invalid_timeout_rejected(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            check_ws_smoke.parse_args(["--url", "ws://example.invalid/ws", "--timeout", "nan"])
        self.assertEqual(caught.exception.code, 2)

    def test_legacy_entry_point_forwards_to_canonical(self) -> None:
        with mock.patch.object(ws_smoke_test, "run_smoke", return_value=0) as run, mock.patch("sys.argv", ["ws_smoke_test.py", "ws://example.invalid/ws", "--timeout", "1500", "--pong-pattern", "pong"]):
            self.assertEqual(ws_smoke_test.main(), 0)
        run.assert_called_once_with(["--url", "ws://example.invalid/ws", "--timeout", "1.5", "--send", "ping", "--reconnect", "--expect", "pong"])


if __name__ == "__main__":
    unittest.main()
