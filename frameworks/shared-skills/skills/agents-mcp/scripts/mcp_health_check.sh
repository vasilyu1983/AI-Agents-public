#!/usr/bin/env bash
# mcp_health_check.sh — Ping stdio and HTTP MCP servers and report status.
#
# Usage:
#   bash mcp_health_check.sh                    # check all configured servers
#   bash mcp_health_check.sh --server postgres  # check one server by name
#   bash mcp_health_check.sh --verbose          # include raw response snippets
#
# Requires: claude CLI on PATH (for mcp list / mcp get), curl, python3
# Exit codes: 0 = all healthy, 1 = one or more failures

set -euo pipefail

VERBOSE=0
TARGET_SERVER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose|-v) VERBOSE=1; shift ;;
    --server)     TARGET_SERVER="${2:-}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; RESET='\033[0m'
ok()   { printf "${GREEN}[OK]${RESET}    %s\n" "$*"; }
fail() { printf "${RED}[FAIL]${RESET}  %s\n" "$*"; }
warn() { printf "${YELLOW}[WARN]${RESET}  %s\n" "$*"; }
info() { printf "        %s\n" "$*"; }

# ── Require claude CLI ────────────────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  fail "claude CLI not found on PATH. Install it before running this script."
  exit 1
fi

# ── Collect server list ───────────────────────────────────────────────────────
# `claude mcp list` output format: "<name>  <transport>  <endpoint/command>"
# We parse it loosely — adapt to your actual CLI version if the format differs.
mcp_list_output=$(claude mcp list 2>&1) || {
  fail "claude mcp list failed: $mcp_list_output"
  exit 1
}

if [[ -z "$mcp_list_output" || "$mcp_list_output" == *"No MCP"* ]]; then
  warn "No MCP servers configured. Add one with: claude mcp add <name> -- <command>"
  exit 0
fi

# ── Parse server entries ──────────────────────────────────────────────────────
declare -a NAMES=()
declare -A TRANSPORTS=()
declare -A ENDPOINTS=()

while IFS= read -r line; do
  [[ -z "$line" || "$line" == NAME* ]] && continue   # skip header/blank
  # Extract name (first word), rest is transport + endpoint
  name=$(printf '%s' "$line" | awk '{print $1}')
  transport=$(printf '%s' "$line" | awk '{print $2}' | tr '[:upper:]' '[:lower:]')
  endpoint=$(printf '%s' "$line" | awk '{$1=""; $2=""; print $0}' | sed 's/^ *//')
  NAMES+=("$name")
  TRANSPORTS["$name"]="${transport:-unknown}"
  ENDPOINTS["$name"]="${endpoint:-}"
done <<< "$mcp_list_output"

# ── Health-check functions ────────────────────────────────────────────────────

check_stdio_server() {
  local name="$1"
  local command="${ENDPOINTS[$name]:-}"

  # Resolve actual command from `claude mcp get`
  if [[ -z "$command" ]]; then
    command=$(claude mcp get "$name" 2>/dev/null | grep -i 'command\|cmd' | head -1 | awk -F'[:=]' '{print $2}' | xargs) || true
  fi

  if [[ -z "$command" ]]; then
    warn "$name (stdio): could not resolve launch command — skipping process check"
    return
  fi

  # A stdio server is healthy if its binary exists and responds to --help or
  # a fast probe. We just check the binary is executable as a minimal check.
  bin=$(printf '%s' "$command" | awk '{print $1}')
  if command -v "$bin" &>/dev/null || [[ -x "$bin" ]]; then
    ok "$name (stdio): binary found at $(command -v "$bin" 2>/dev/null || echo "$bin")"
    [[ "$VERBOSE" -eq 1 ]] && info "launch command: $command"
  else
    fail "$name (stdio): binary not found or not executable — '$bin'"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_http_server() {
  local name="$1"
  local url="${ENDPOINTS[$name]:-}"

  if [[ -z "$url" ]]; then
    url=$(claude mcp get "$name" 2>/dev/null | grep -i 'url\|endpoint' | head -1 | awk -F'[:=] ' '{print $2}' | xargs) || true
  fi

  if [[ -z "$url" ]]; then
    warn "$name (http): could not resolve URL — skipping"
    return
  fi

  # Probe the server with a short timeout
  http_status=$(curl -s -o /tmp/mcp_probe_$$.json -w "%{http_code}" \
    --max-time 5 \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    "$url" 2>/dev/null) || http_status="000"

  if [[ "$http_status" =~ ^(200|400|401|403|405)$ ]]; then
    # 400/401/403/405 still means the server is running — auth or method issue
    ok "$name (http): reachable — HTTP $http_status at $url"
    [[ "$VERBOSE" -eq 1 ]] && info "response snippet: $(head -c 200 /tmp/mcp_probe_$$.json 2>/dev/null || true)"
  elif [[ "$http_status" == "000" ]]; then
    fail "$name (http): connection refused or timeout — $url"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    warn "$name (http): unexpected HTTP $http_status at $url"
    [[ "$VERBOSE" -eq 1 ]] && info "response snippet: $(head -c 200 /tmp/mcp_probe_$$.json 2>/dev/null || true)"
  fi

  rm -f "/tmp/mcp_probe_$$.json"
}

check_sse_server() {
  local name="$1"
  local url="${ENDPOINTS[$name]:-}"

  if [[ -z "$url" ]]; then
    warn "$name (sse): could not resolve URL — skipping"
    return
  fi

  http_status=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 5 \
    -H "Accept: text/event-stream" \
    "$url" 2>/dev/null) || http_status="000"

  if [[ "$http_status" =~ ^(200|400|401|403)$ ]]; then
    ok "$name (sse): reachable — HTTP $http_status at $url"
  elif [[ "$http_status" == "000" ]]; then
    fail "$name (sse): connection refused or timeout — $url"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    warn "$name (sse): HTTP $http_status at $url"
  fi
}

# ── Main loop ─────────────────────────────────────────────────────────────────
FAIL_COUNT=0
CHECKED=0

printf '\nMCP Health Check — %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n\n' "$(printf '=%.0s' {1..50})"

for name in "${NAMES[@]}"; do
  [[ -n "$TARGET_SERVER" && "$name" != "$TARGET_SERVER" ]] && continue
  CHECKED=$((CHECKED + 1))
  transport="${TRANSPORTS[$name]:-unknown}"

  case "$transport" in
    stdio)            check_stdio_server "$name" ;;
    http|streamable)  check_http_server "$name" ;;
    sse)              check_sse_server "$name" ;;
    *)
      # Fall back to URL probe if transport is unclear
      endpoint="${ENDPOINTS[$name]:-}"
      if [[ "$endpoint" =~ ^https?:// ]]; then
        check_http_server "$name"
      else
        check_stdio_server "$name"
      fi
      ;;
  esac
done

printf '\n%s\n' "$(printf '=%.0s' {1..50})"
printf 'Checked %d server(s). Failures: %d\n\n' "$CHECKED" "$FAIL_COUNT"

[[ "$FAIL_COUNT" -gt 0 ]] && exit 1 || exit 0
