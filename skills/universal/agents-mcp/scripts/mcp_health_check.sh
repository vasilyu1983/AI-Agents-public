#!/usr/bin/env bash
# Check Claude Code's MCP connection status; this does not execute a read tool.
# Usage: bash mcp_health_check.sh [--server NAME] [--verbose]
# Requires: claude CLI and python3. Exit 0 only when every selected server connects.
set -euo pipefail

exec python3 - "$@" <<'PY'
import argparse
import re
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description="Check MCP connection status, then run a separate read-tool probe.")
parser.add_argument("--server", help="Check one server, including servers omitted by mcp list")
parser.add_argument("--verbose", "-v", action="store_true", help="Explain the evidence boundary without printing config or responses")
args = parser.parse_args()

def fail(message):
    print(f"[FAIL] {message}", file=sys.stderr)
    sys.exit(1)

if args.server is not None and not args.server.strip():
    fail("--server requires a non-empty name")
if not shutil.which("claude"):
    fail("claude CLI not found on PATH")

command = ["claude", "mcp", "get", args.server] if args.server else ["claude", "mcp", "list"]
try:
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
except (OSError, subprocess.TimeoutExpired):
    fail("Claude MCP status command failed or timed out")
if result.returncode:
    # CLI errors/config can contain credentials; do not echo raw output.
    fail("Claude MCP status command returned a nonzero exit code")

# CLI text is version-dependent. Accept known shapes and reject all other output.
output = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", result.stdout)
entries = []
if args.server:
    statuses = re.findall(r"^Status:\s*(.+?)\s*$", output, re.MULTILINE)
    if len(statuses) != 1:
        fail("Missing or ambiguous server status; inspect claude mcp get manually")
    entries.append((args.server, statuses[0]))
else:
    for line in output.splitlines():
        line = line.strip()
        if not line or line == "Checking MCP server health...":
            continue
        match = re.fullmatch(r"(\S+):\s+.+ - (.+)", line)
        if not match:
            fail("Empty inventory or unrecognized list output; inspect claude mcp list manually")
        entries.append(match.groups())
if not entries:
    fail("No server connection was checked")
if len({name for name, _ in entries}) != len(entries):
    fail("Duplicate server names; inspect configuration before relying on the result")

failed = 0
for name, status in entries:
    if status in ("✓ Connected", "✔ Connected"):
        print(f"[OK] {name}: connected (read tool not checked)")
    else:
        print(f"[FAIL] {name}: no verified connection")
        failed += 1
if args.verbose:
    print("Only CLI connection status was checked. Run one authorized low-cost read tool before admission.")
print(f"Checked {len(entries)} server(s). Failures: {failed}")
sys.exit(1 if failed else 0)
PY
