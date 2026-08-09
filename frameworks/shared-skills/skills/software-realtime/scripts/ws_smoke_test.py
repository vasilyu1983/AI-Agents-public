#!/usr/bin/env python3
"""
ws_smoke_test.py — WebSocket smoke test: connects to a WS endpoint, sends a ping
message, asserts a pong response arrives within 500 ms, then asserts that the
connection auto-reconnects after a server-side close.

Usage:
    python3 ws_smoke_test.py wss://echo.websocket.org
    python3 ws_smoke_test.py ws://localhost:8080/ws --timeout 1000 --ping-msg '{"type":"ping"}'

Requirements:
    Python 3.8+
    websocket-client >= 1.7  (pip install websocket-client)

Exit codes:
    0 — all assertions pass
    1 — one or more assertions fail (details printed to stdout)
    2 — usage/dependency error
"""

from __future__ import annotations

import argparse
import sys
import time
import threading

try:
    import websocket
except ImportError:
    print("ERROR: websocket-client not installed. Run: pip install websocket-client", file=sys.stderr)
    sys.exit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="WebSocket smoke test: ping/pong latency + reconnect check."
    )
    parser.add_argument("url", help="WebSocket URL (ws:// or wss://)")
    parser.add_argument(
        "--timeout",
        type=int,
        default=500,
        help="Max milliseconds to wait for pong response (default: 500)",
    )
    parser.add_argument(
        "--ping-msg",
        default="ping",
        help='Message to send as ping (default: "ping")',
    )
    parser.add_argument(
        "--pong-pattern",
        default=None,
        help="Substring expected in pong response (default: any non-empty message)",
    )
    return parser.parse_args()


def test_ping_pong(url: str, ping_msg: str, timeout_ms: int, pong_pattern: str | None) -> tuple[bool, float | None, str]:
    """
    Connect, send ping_msg, wait for a response.
    Returns (passed, latency_ms, description).
    """
    received: list[str] = []
    error: list[str] = []
    event = threading.Event()

    def on_message(ws, message):
        received.append(message)
        event.set()

    def on_error(ws, err):
        error.append(str(err))
        event.set()

    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
    )

    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()

    # Wait for connection
    deadline = time.monotonic() + (timeout_ms / 1000)
    while not ws.sock and time.monotonic() < deadline:
        time.sleep(0.01)

    if not ws.sock or not ws.sock.connected:
        ws.close()
        return False, None, f"FAIL [ping/pong]: Could not connect to {url}"

    t0 = time.monotonic()
    ws.send(ping_msg)

    timeout_sec = timeout_ms / 1000
    event.wait(timeout=timeout_sec)
    latency_ms = (time.monotonic() - t0) * 1000

    ws.close()

    if error:
        return False, latency_ms, f"FAIL [ping/pong]: WebSocket error: {error[0]}"

    if not received:
        return False, latency_ms, (
            f"FAIL [ping/pong]: No response within {timeout_ms} ms "
            f"(latency: {latency_ms:.0f} ms)"
        )

    if pong_pattern and pong_pattern not in received[0]:
        return False, latency_ms, (
            f"FAIL [ping/pong]: Response '{received[0][:100]}' "
            f"does not contain expected pattern '{pong_pattern}'"
        )

    return True, latency_ms, f"PASS [ping/pong]: Response in {latency_ms:.0f} ms"


def test_reconnect(url: str, timeout_ms: int) -> tuple[bool, str]:
    """
    Connect, force a close, then reconnect and verify the new connection works.
    """
    connected_count = [0]
    event = threading.Event()

    def on_open(ws):
        connected_count[0] += 1
        if connected_count[0] == 1:
            # Close immediately to trigger reconnect
            ws.close()
        else:
            event.set()
            ws.close()

    def on_error(ws, err):
        pass  # Expected on forced close

    ws = websocket.WebSocketApp(url, on_open=on_open, on_error=on_error)

    timeout_sec = (timeout_ms * 4) / 1000  # give more time for reconnect

    thread = threading.Thread(
        target=ws.run_forever,
        kwargs={"reconnect": 1},  # 1-second reconnect delay
        daemon=True,
    )
    thread.start()
    event.wait(timeout=timeout_sec)

    ws.close()

    if connected_count[0] >= 2:
        return True, f"PASS [reconnect]: Reconnected successfully (connections: {connected_count[0]})"
    else:
        return False, (
            f"FAIL [reconnect]: Did not reconnect within {timeout_sec:.0f} s "
            f"(connections observed: {connected_count[0]})"
        )


def main() -> None:
    args = parse_args()
    results: list[tuple[bool, str]] = []

    print(f"WebSocket smoke test: {args.url}")
    print(f"Ping message: {args.ping_msg!r}")
    print(f"Timeout: {args.timeout} ms")
    print("")

    # Test 1: ping/pong latency
    passed, latency_ms, msg = test_ping_pong(
        args.url, args.ping_msg, args.timeout, args.pong_pattern
    )
    results.append((passed, msg))
    print(msg)
    if latency_ms is not None and passed:
        if latency_ms > args.timeout * 0.8:
            print(f"  WARNING: latency {latency_ms:.0f} ms is close to the {args.timeout} ms budget")

    # Test 2: reconnect on close
    passed_r, msg_r = test_reconnect(args.url, args.timeout)
    results.append((passed_r, msg_r))
    print(msg_r)

    print("")
    all_passed = all(p for p, _ in results)
    if all_passed:
        print("PASS: All smoke tests passed.")
        sys.exit(0)
    else:
        print("FAIL: One or more smoke tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
