#!/bin/zsh
set -euo pipefail

XCODEBUILDMCP_CMD=()

resolve_xcodebuildmcp() {
  if (( ${#XCODEBUILDMCP_CMD[@]} > 0 )); then
    return 0
  fi

  if command -v xcodebuildmcp >/dev/null 2>&1; then
    XCODEBUILDMCP_CMD=(xcodebuildmcp)
    return 0
  fi

  if command -v npx >/dev/null 2>&1; then
    XCODEBUILDMCP_CMD=(npx -y xcodebuildmcp@latest)
    return 0
  fi

  echo "xcodebuildmcp was not found and npx is unavailable." >&2
  echo "Install xcodebuildmcp or Node.js, or run ./scripts/bootstrap-xcodebuildmcp.sh after installing npx." >&2
  return 1
}

run_xcodebuildmcp() {
  resolve_xcodebuildmcp
  "${XCODEBUILDMCP_CMD[@]}" "$@"
}

skill_root() {
  cd "$(dirname "$0")/.." && pwd
}

repo_root() {
  if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    printf '%s\n' "$git_root"
    return 0
  fi

  pwd
}

default_config_path() {
  printf '%s/.xcodebuildmcp/config.yaml\n' "$(repo_root)"
}

discover_booted_simulator_id() {
  local output
  output="$(run_xcodebuildmcp simulator list --enabled true --output json)"
  printf '%s\n' "$output" | grep -oE '[A-F0-9-]{36}.*\[Booted\]' | head -n 1 | grep -oE '[A-F0-9-]{36}' || true
}
