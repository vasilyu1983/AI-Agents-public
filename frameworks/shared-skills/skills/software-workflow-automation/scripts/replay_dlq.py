#!/usr/bin/env python3
"""
replay_dlq.py — Generic dead-letter queue (DLQ) message replay scaffold.

Reads a JSON file containing an array of DLQ message objects and prints the
replay command for each message. Supports dry-run (default) and --execute mode.

The script is intentionally generic: adapt TARGET_COMMAND and the payload
extraction logic for your specific queue/runtime (SQS, Temporal, Trigger.dev,
n8n, RabbitMQ, etc.).

Usage:
    python3 replay_dlq.py dlq-messages.json
    python3 replay_dlq.py dlq-messages.json --execute
    python3 replay_dlq.py dlq-messages.json --limit 5 --filter '{"status": "failed"}'

Input JSON format (array of objects):
    [
      {
        "id": "msg-001",
        "queue": "order-processing",
        "payload": { "orderId": "ORD-123", "amount": 99.99 },
        "error": "PaymentGatewayTimeout",
        "attempts": 3,
        "created_at": "2026-04-20T10:00:00Z"
      },
      ...
    ]

Exit codes:
    0 — all messages processed (dry-run: all commands printed)
    1 — one or more replays failed in --execute mode
    2 — usage error (missing file, invalid JSON)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# CONFIGURE: Replace this with the actual replay command for your runtime.
# The {payload} placeholder is replaced with the JSON-encoded message payload.
# Examples:
#   Temporal:     ["temporal", "workflow", "start", "--type", "ProcessOrder", "--input", "{payload}"]
#   AWS SQS:      ["aws", "sqs", "send-message", "--queue-url", "https://...", "--message-body", "{payload}"]
#   Trigger.dev:  ["trigger", "run", "process-order", "--payload", "{payload}"]
#   curl/HTTP:    ["curl", "-s", "-X", "POST", "https://api.example.com/jobs", "-d", "{payload}"]
# ---------------------------------------------------------------------------
TARGET_COMMAND_TEMPLATE: list[str] = [
    "echo",  # Replace with your actual command
    "REPLAY:",
    "{payload}",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay DLQ messages from a JSON file."
    )
    parser.add_argument("input_file", help="Path to JSON file containing DLQ messages")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute replay commands (default: dry-run, print only)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of messages to process",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help='JSON object of key:value pairs to filter messages (e.g. \'{"queue": "orders"}\')',
    )
    parser.add_argument(
        "--payload-key",
        default="payload",
        help='Key in each message object to use as replay payload (default: "payload")',
    )
    return parser.parse_args()


def load_messages(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, list):
        print("ERROR: Input JSON must be an array of message objects.", file=sys.stderr)
        sys.exit(2)
    return data


def matches_filter(message: dict, filter_obj: dict) -> bool:
    for key, value in filter_obj.items():
        if message.get(key) != value:
            return False
    return True


def build_command(message: dict, payload_key: str) -> list[str]:
    payload = message.get(payload_key, message)
    payload_str = json.dumps(payload)
    return [
        arg.replace("{payload}", payload_str) if isinstance(arg, str) else arg
        for arg in TARGET_COMMAND_TEMPLATE
    ]


def replay_message(cmd: list[str], execute: bool) -> tuple[bool, str]:
    cmd_str = " ".join(cmd)
    if not execute:
        return True, f"[DRY-RUN] {cmd_str}"

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, f"[OK] {cmd_str}\n       stdout: {result.stdout.strip()}"
        else:
            return False, f"[ERROR] {cmd_str}\n        stderr: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, f"[TIMEOUT] {cmd_str}"
    except FileNotFoundError:
        return False, f"[NOT FOUND] Command not found: {cmd[0]}"


def main() -> None:
    args = parse_args()
    messages = load_messages(args.input_file)

    # Parse filter
    filter_obj: dict[str, Any] = {}
    if args.filter:
        try:
            filter_obj = json.loads(args.filter)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid --filter JSON: {exc}", file=sys.stderr)
            sys.exit(2)

    # Apply filter
    if filter_obj:
        messages = [m for m in messages if matches_filter(m, filter_obj)]

    # Apply limit
    if args.limit is not None:
        messages = messages[: args.limit]

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"DLQ Replay ({mode})")
    print(f"Messages to replay: {len(messages)}")
    print(f"Command template:   {' '.join(TARGET_COMMAND_TEMPLATE)}")
    print("")

    if not messages:
        print("No messages to replay after filtering.")
        sys.exit(0)

    results: list[tuple[bool, str]] = []
    for i, message in enumerate(messages, start=1):
        msg_id = message.get("id", f"index-{i}")
        queue = message.get("queue", "unknown")
        error = message.get("error", "")
        attempts = message.get("attempts", "?")

        print(f"[{i}/{len(messages)}] id={msg_id} queue={queue} attempts={attempts} error={error!r}")

        cmd = build_command(message, args.payload_key)
        passed, output = replay_message(cmd, args.execute)
        results.append((passed, output))
        print(f"  {output}")
        print("")

    passed_count = sum(1 for p, _ in results if p)
    failed_count = len(results) - passed_count

    print(f"Summary: {passed_count} passed, {failed_count} failed")

    if failed_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
