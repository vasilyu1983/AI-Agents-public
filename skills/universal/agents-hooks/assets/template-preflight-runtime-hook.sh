#!/usr/bin/env bash
set -euo pipefail

# Template: SessionStart runtime preflight hook
# Usage: configure in hooks settings as command hook for SessionStart
#
# SessionStart cannot block. A non-zero exit only shows stderr to the user as a
# hook-error notice; Claude never sees it. To make Claude aware of a failed
# preflight, print hookSpecificOutput.additionalContext and exit 0.
# Set the minimum version from the project's engines / .tool-versions file.

MIN_NODE_MAJOR=22
MIN_NODE_MINOR=22

warn() {
  local msg="$1"
  if command -v jq >/dev/null 2>&1; then
    jq -cn --arg msg "$msg" '{
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: $msg
      }
    }'
  else
    # Without jq, plain-text stdout still reaches Claude: for SessionStart the
    # runtime adds plain-text stdout to the model's context. stderr does not.
    echo "$msg (jq not found; install jq for structured hook output)"
  fi
  echo "$msg" >&2
  exit 0
}

if ! command -v node >/dev/null 2>&1; then
  warn "Runtime preflight failed: node not found. Install Node >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0"
fi

NODE_VERSION_RAW="$(node -v | sed 's/^v//')"
NODE_MAJOR="${NODE_VERSION_RAW%%.*}"
NODE_MINOR="$(echo "$NODE_VERSION_RAW" | cut -d. -f2)"

if [[ "$NODE_MAJOR" -lt "$MIN_NODE_MAJOR" ]] || { [[ "$NODE_MAJOR" -eq "$MIN_NODE_MAJOR" ]] && [[ "$NODE_MINOR" -lt "$MIN_NODE_MINOR" ]]; }; then
  warn "Runtime preflight failed: node v${NODE_VERSION_RAW} detected, requires >= v${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0. Run: nvm install ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0 && nvm use ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0"
fi

# Add additional tool checks below if needed
# command -v jq >/dev/null 2>&1 || warn "jq is required"

echo "Runtime preflight ok: node v${NODE_VERSION_RAW}"
exit 0
