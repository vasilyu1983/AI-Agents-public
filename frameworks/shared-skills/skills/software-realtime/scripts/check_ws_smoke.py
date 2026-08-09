#!/usr/bin/env python3
"""
WebSocket smoke-test.

Uses the `websockets` library when available; falls back to a raw TCP
socket-level HTTP Upgrade handshake when it is not installed.

Usage:
    python3 check_ws_smoke.py --url ws://localhost:8080/ws
    python3 check_ws_smoke.py --url wss://example.com/ws --timeout 10
    python3 check_ws_smoke.py --help
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
import socket
import ssl
import sys
import time
import urllib.parse
from typing import Optional


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "WebSocket connection smoke-test.\n\n"
            "Attempts to open a WebSocket connection to the given URL and "
            "reports success or failure. Uses the 'websockets' library when "
            "present; falls back to a raw socket-level HTTP Upgrade handshake "
            "when it is not installed (no external dependencies required for "
            "the basic check)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        required=True,
        help="WebSocket URL to test (ws:// or wss://). Example: ws://localhost:8080/ws",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Connection and handshake timeout in seconds (default: 5).",
    )
    parser.add_argument(
        "--send",
        default=None,
        metavar="MESSAGE",
        help=(
            "Optional text message to send after connecting. "
            "Only used when the 'websockets' library is available."
        ),
    )
    parser.add_argument(
        "--expect",
        default=None,
        metavar="SUBSTRING",
        help=(
            "Optional substring expected in the first message received from the server. "
            "Only used when the 'websockets' library is available and --send is given."
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Raw handshake fallback (no external deps)
# ---------------------------------------------------------------------------

def _ws_key() -> str:
    return base64.b64encode(os.urandom(16)).decode()


def _expected_accept(key: str) -> str:
    magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    digest = hashlib.sha1((key + magic).encode()).digest()
    return base64.b64encode(digest).decode()


def smoke_raw(url: str, timeout: float) -> tuple[bool, str]:
    """
    Perform a raw HTTP Upgrade handshake without the websockets library.
    Returns (success, message).
    """
    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    host = parsed.hostname or ""
    port = parsed.port
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    if scheme == "ws":
        default_port = 80
        use_tls = False
    elif scheme == "wss":
        default_port = 443
        use_tls = True
    else:
        return False, f"Unsupported scheme: {scheme!r}. Use ws:// or wss://."

    port = port or default_port
    key = _ws_key()
    expected_accept = _expected_accept(key)

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )

    try:
        raw_sock = socket.create_connection((host, port), timeout=timeout)
    except OSError as exc:
        return False, f"TCP connection failed: {exc}"

    try:
        if use_tls:
            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(raw_sock, server_hostname=host)
        else:
            sock = raw_sock

        sock.sendall(request.encode())

        # Read response headers
        response = b""
        start = time.monotonic()
        while b"\r\n\r\n" not in response:
            if time.monotonic() - start > timeout:
                return False, "Timed out waiting for server handshake response."
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk

        header_text = response.split(b"\r\n\r\n", 1)[0].decode(errors="replace")
        first_line = header_text.splitlines()[0] if header_text else ""

        if "101" not in first_line:
            return False, f"Server did not return 101 Switching Protocols. Got: {first_line!r}"

        # Verify Sec-WebSocket-Accept
        for line in header_text.splitlines():
            if line.lower().startswith("sec-websocket-accept:"):
                server_accept = line.split(":", 1)[1].strip()
                if server_accept != expected_accept:
                    return False, (
                        f"Sec-WebSocket-Accept mismatch. "
                        f"Expected {expected_accept!r}, got {server_accept!r}."
                    )
                break

        return True, f"Handshake successful (101 Switching Protocols). Host: {host}:{port}"

    except ssl.SSLError as exc:
        return False, f"TLS error: {exc}"
    except OSError as exc:
        return False, f"Socket error: {exc}"
    finally:
        try:
            sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# websockets library path (async)
# ---------------------------------------------------------------------------

def smoke_websockets_lib(url: str, timeout: float, send: Optional[str], expect: Optional[str]) -> tuple[bool, str]:
    """
    Use the 'websockets' library for a richer smoke-test.
    """
    import asyncio

    async def _run() -> tuple[bool, str]:
        import websockets  # type: ignore

        try:
            async with websockets.connect(url, open_timeout=timeout, close_timeout=timeout) as ws:
                if send:
                    await ws.send(send)
                    try:
                        reply = await asyncio.wait_for(ws.recv(), timeout=timeout)
                        if expect and expect not in str(reply):
                            return False, (
                                f"Connected and sent message but expected substring "
                                f"{expect!r} not found in reply: {str(reply)[:200]!r}"
                            )
                        return True, f"Connected, sent, and received reply ({len(str(reply))} chars)."
                    except asyncio.TimeoutError:
                        return False, "Connected and sent message, but no reply received within timeout."
                return True, "Connected successfully (no send/receive requested)."
        except Exception as exc:
            return False, f"websockets error: {exc}"

    return asyncio.run(_run())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    url: str = args.url
    timeout: float = args.timeout

    print(f"Target : {url}")
    print(f"Timeout: {timeout}s")

    # Try websockets library first
    try:
        import websockets  # noqa: F401
        lib_available = True
    except ImportError:
        lib_available = False

    if lib_available:
        print("Backend: websockets library")
        success, message = smoke_websockets_lib(url, timeout, args.send, args.expect)
    else:
        print("Backend: raw socket handshake (install 'websockets' for full support)")
        success, message = smoke_raw(url, timeout)

    status = "PASS" if success else "FAIL"
    print(f"Result : {status} — {message}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
