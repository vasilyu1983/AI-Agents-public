#!/usr/bin/env bash
set -euo pipefail

# Template: SessionStart runtime preflight hook
# Usage: configure in hooks settings as command hook for SessionStart

MIN_NODE_MAJOR=22
MIN_NODE_MINOR=22

fail() {
  echo "$1" >&2
  exit 2
}

if ! command -v node >/dev/null 2>&1; then
  fail "Runtime preflight failed: node not found. Install Node >= 22.22.0"
fi

NODE_VERSION_RAW="$(node -v | sed 's/^v//')"
NODE_MAJOR="${NODE_VERSION_RAW%%.*}"
NODE_MINOR="$(echo "$NODE_VERSION_RAW" | cut -d. -f2)"

if [[ "$NODE_MAJOR" -lt "$MIN_NODE_MAJOR" ]] || { [[ "$NODE_MAJOR" -eq "$MIN_NODE_MAJOR" ]] && [[ "$NODE_MINOR" -lt "$MIN_NODE_MINOR" ]]; }; then
  fail "Runtime preflight failed: node v${NODE_VERSION_RAW} detected, requires >= v${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0. Run: nvm install 22.22.0 && nvm use 22.22.0"
fi

# Add additional tool checks below if needed
# command -v jq >/dev/null 2>&1 || fail "jq is required"

echo "Runtime preflight ok: node v${NODE_VERSION_RAW}"
exit 0
