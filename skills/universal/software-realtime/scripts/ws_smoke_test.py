#!/usr/bin/env python3
"""Compatibility entry point for the canonical ``check_ws_smoke.py`` tool.

This preserves the old positional URL and millisecond timeout. The second
connection check verifies that a fresh connection works; it cannot prove that
an application client automatically reconnects after a server-side close.
"""

from __future__ import annotations

import argparse

from check_ws_smoke import main as run_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="WebSocket message and second-connection smoke test")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=500, help="Timeout in milliseconds")
    parser.add_argument("--ping-msg", default="ping")
    parser.add_argument("--pong-pattern")
    args = parser.parse_args()
    options = ["--url", args.url, "--timeout", str(args.timeout / 1000), "--send", args.ping_msg, "--reconnect"]
    if args.pong_pattern is not None:
        options.extend(["--expect", args.pong_pattern])
    return run_smoke(options)


if __name__ == "__main__":
    raise SystemExit(main())
