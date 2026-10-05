#!/usr/bin/env python3
"""Check a WebSocket handshake, with optional message and second-connection checks.

The basic handshake uses the standard library. Message and reconnection checks
require the ``websockets`` package; they never silently fall back to a handshake.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib.util
import math
import os
import re
import socket
import ssl
import sys
import urllib.parse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WebSocket smoke test")
    parser.add_argument("--url", required=True, help="ws:// or wss:// endpoint")
    parser.add_argument("--timeout", type=float, default=5.0, help="Seconds per operation")
    parser.add_argument("--send", help="Text message to send after connecting")
    parser.add_argument("--expect", help="Required substring in the first reply")
    parser.add_argument("--reconnect", action="store_true", help="Open a second connection after closing the first")
    args = parser.parse_args(argv)
    parsed = urllib.parse.urlsplit(args.url)
    try:
        valid_port = parsed.port is None or parsed.port > 0
    except ValueError:
        valid_port = False
    if parsed.scheme not in {"ws", "wss"} or not parsed.hostname or not valid_port or parsed.username or parsed.password or parsed.fragment:
        parser.error("--url must be a ws:// or wss:// URL with a host, without userinfo or fragment")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be a positive finite number")
    if args.expect is not None and args.send is None:
        parser.error("--expect requires --send")
    if (args.send is not None or args.reconnect) and importlib.util.find_spec("websockets") is None:
        parser.error("--send and --reconnect require the websockets package")
    return args


def _expected_accept(key: str) -> str:
    digest = hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def smoke_raw(url: str, timeout: float) -> tuple[bool, str]:
    """Verify a complete HTTP/1.1 WebSocket upgrade without a third-party client."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"ws", "wss"} or not parsed.hostname:
        return False, "Invalid WebSocket URL"
    try:
        port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    except ValueError:
        return False, "Invalid WebSocket port"
    host = parsed.hostname
    authority = f"[{host}]" if ":" in host else host
    if parsed.port is not None:
        authority += f":{port}"
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        f"GET {path} HTTP/1.1\r\nHost: {authority}\r\n"
        "Upgrade: websocket\r\nConnection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
    )
    raw_sock = None
    sock = None
    try:
        raw_sock = socket.create_connection((host, port), timeout=timeout)
        sock = ssl.create_default_context().wrap_socket(raw_sock, server_hostname=host) if parsed.scheme == "wss" else raw_sock
        sock.settimeout(timeout)
        sock.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(1024)
            if not chunk:
                return False, "Incomplete WebSocket handshake response"
            response += chunk
            if len(response) > 16384:
                return False, "WebSocket handshake headers exceed 16 KiB"
        lines = response.split(b"\r\n\r\n", 1)[0].decode("latin-1").split("\r\n")
        if not re.fullmatch(r"HTTP/1\.1 101(?: .*)?", lines[0]):
            return False, f"Expected HTTP/1.1 101; got {lines[0]!r}"
        headers: dict[str, list[str]] = {}
        for line in lines[1:]:
            if ":" not in line:
                return False, "Malformed WebSocket handshake header"
            name, value = line.split(":", 1)
            headers.setdefault(name.lower(), []).append(value.strip())
        if [v.lower() for v in headers.get("upgrade", [])] != ["websocket"]:
            return False, "Missing WebSocket Upgrade header"
        if len(headers.get("connection", [])) != 1 or "upgrade" not in [token.strip().lower() for token in headers["connection"][0].split(",")]:
            return False, "Missing Connection: Upgrade header"
        if headers.get("sec-websocket-accept") != [_expected_accept(key)]:
            return False, "Missing or invalid Sec-WebSocket-Accept header"
        return True, "WebSocket handshake verified"
    except (OSError, ssl.SSLError, UnicodeError) as exc:
        return False, f"WebSocket connection failed: {exc}"
    finally:
        if sock is not None:
            sock.close()
        elif raw_sock is not None:
            raw_sock.close()


def smoke_websockets(url: str, timeout: float, send: str | None, expect: str | None, reconnect: bool) -> tuple[bool, str]:
    import websockets

    async def run() -> tuple[bool, str]:
        try:
            async with websockets.connect(url, open_timeout=timeout, close_timeout=timeout) as ws:
                if send is not None:
                    await asyncio.wait_for(ws.send(send), timeout)
                    reply = await asyncio.wait_for(ws.recv(), timeout)
                    if expect is not None and expect not in str(reply):
                        return False, "Reply did not contain the expected substring"
            if reconnect:
                async with websockets.connect(url, open_timeout=timeout, close_timeout=timeout):
                    pass
            if send is not None and reconnect:
                detail = "Message and second connection verified"
            elif send is not None:
                detail = "Message exchange verified"
            elif reconnect:
                detail = "Second connection verified"
            else:
                detail = "WebSocket connection verified"
            return True, detail
        except Exception as exc:
            return False, f"WebSocket check failed: {exc}"

    return asyncio.run(run())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if importlib.util.find_spec("websockets") is not None:
        ok, message = smoke_websockets(args.url, args.timeout, args.send, args.expect, args.reconnect)
    else:
        ok, message = smoke_raw(args.url, args.timeout)
    print(("PASS" if ok else "FAIL") + ": " + message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
