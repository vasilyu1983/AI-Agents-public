#!/usr/bin/env bash
# smoke_test.sh — validates a coding-agent setup before a session starts.
# Checks: (1) agent CLI installed or model API reachable, (2) tool registry
# present, (3) sandbox engaged. Fails closed: an unparseable or disabled
# sandbox setting is a FAIL, not a PASS.
# Exit 0 = all checks passed. Exit 1 = one or more checks failed. Exit 2 = usage.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: smoke_test.sh [--help]

Checks, in order:
  1. Agent CLI installed (claude/codex --version) — an install check, NOT an
     authenticated model probe. With no CLI, an API key triggers a real probe:
       ANTHROPIC_API_KEY + SMOKE_TEST_MODEL  -> 1-token Messages request
       OPENAI_API_KEY                        -> list-models request
     SMOKE_TEST_MODEL must name a model your account can call; the script
     pins no model id.
  2. Tool registry present (.claude/, .codex/, or an SDK dependency).
  3. Sandbox engaged: container marker, AGENT_SANDBOX=1, SANDBOX_EXEC_PROFILE,
     or a Claude Code settings file whose parsed JSON has
     sandbox.enabled == true (settings.local.json overrides settings.json).
     A present-but-false or unparseable setting FAILS.

Environment:
  AGENT_PROJECT_ROOT   project root to inspect (default: current directory)
  SMOKE_TEST_MODEL     model id for the Anthropic API probe
USAGE
}

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  "") ;;
  *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
esac

PASS=0
FAIL=0
RESULTS=()

check() {
  local label="$1"
  local result="$2"   # "ok" | "fail"
  local detail="$3"
  if [[ "$result" == "ok" ]]; then
    RESULTS+=("  [PASS] $label")
    ((++PASS))
  else
    RESULTS+=("  [FAIL] $label — $detail")
    ((++FAIL))
  fi
}

# ── 1. Agent CLI installed / model API reachable ─────────────────────────────
# `claude --version` / `codex --version` prove only that the binary runs; they
# do not prove authentication or model access, so the check is labelled
# "CLI installed". Without a CLI, an API key triggers a real authenticated probe.
MODEL_LABEL="Agent CLI installed or model API reachable"
MODEL_OK="fail"
MODEL_DETAIL="no supported CLI or API key found"

if command -v claude &>/dev/null; then
  MODEL_LABEL="Agent CLI installed (not an auth probe)"
  if claude --version &>/dev/null; then
    MODEL_OK="ok"
    MODEL_DETAIL="claude CLI runs ($(claude --version 2>&1 | head -1))"
  else
    MODEL_DETAIL="claude CLI found but --version failed"
  fi
elif command -v codex &>/dev/null; then
  MODEL_LABEL="Agent CLI installed (not an auth probe)"
  if codex --version &>/dev/null; then
    MODEL_OK="ok"
    MODEL_DETAIL="codex CLI runs ($(codex --version 2>&1 | head -1))"
  else
    MODEL_DETAIL="codex CLI found but --version failed"
  fi
elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  MODEL_LABEL="Model API reachable (authenticated)"
  if [[ -z "${SMOKE_TEST_MODEL:-}" ]]; then
    MODEL_DETAIL="ANTHROPIC_API_KEY set but SMOKE_TEST_MODEL is empty; set it to a model id your account can call"
  else
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST "https://api.anthropic.com/v1/messages" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d "{\"model\":\"${SMOKE_TEST_MODEL}\",\"max_tokens\":1,\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}" \
      2>/dev/null || echo "000")
    if [[ "$STATUS" == "200" ]]; then
      MODEL_OK="ok"; MODEL_DETAIL="Anthropic API reachable with $SMOKE_TEST_MODEL (HTTP 200)"
    else
      MODEL_DETAIL="Anthropic API returned HTTP $STATUS for $SMOKE_TEST_MODEL"
    fi
  fi
elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
  MODEL_LABEL="Model API reachable (authenticated)"
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "https://api.openai.com/v1/models" \
    -H "Authorization: Bearer $OPENAI_API_KEY" 2>/dev/null || echo "000")
  if [[ "$STATUS" == "200" ]]; then
    MODEL_OK="ok"; MODEL_DETAIL="OpenAI API reachable (HTTP 200)"
  else
    MODEL_DETAIL="OpenAI API returned HTTP $STATUS"
  fi
fi
check "$MODEL_LABEL" "$MODEL_OK" "$MODEL_DETAIL"

# ── 2. Tool registry loaded ───────────────────────────────────────────────────
# For Claude Code: a `.claude/` directory with at least settings.json or agents/.
# For Codex: a `.codex/` directory with config.toml.
# For Agent SDK: pyproject.toml / package.json containing anthropic or openai dep.
REGISTRY_OK="fail"
REGISTRY_DETAIL="no tool-registry indicator found (.claude/, .codex/, pyproject.toml, package.json)"
SEARCH_ROOT="${AGENT_PROJECT_ROOT:-$(pwd)}"

if [[ -d "$SEARCH_ROOT/.claude" ]]; then
  TOOL_COUNT=$(find "$SEARCH_ROOT/.claude" -name "*.json" -o -name "*.md" -o -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
  REGISTRY_OK="ok"
  REGISTRY_DETAIL=".claude/ found ($TOOL_COUNT config files)"
elif [[ -d "$SEARCH_ROOT/.codex" ]]; then
  REGISTRY_OK="ok"
  REGISTRY_DETAIL=".codex/ found"
elif [[ -f "$SEARCH_ROOT/pyproject.toml" ]] && grep -qE 'anthropic|openai' "$SEARCH_ROOT/pyproject.toml" 2>/dev/null; then
  REGISTRY_OK="ok"
  REGISTRY_DETAIL="pyproject.toml with SDK dependency found"
elif [[ -f "$SEARCH_ROOT/package.json" ]] && grep -qE 'anthropic|openai' "$SEARCH_ROOT/package.json" 2>/dev/null; then
  REGISTRY_OK="ok"
  REGISTRY_DETAIL="package.json with SDK dependency found"
fi
check "Tool registry loaded" "$REGISTRY_OK" "$REGISTRY_DETAIL"

# ── 3. Sandbox engaged ────────────────────────────────────────────────────────
# Any one of these passes:
#   a. Running inside a container (/.dockerenv or cgroup marker)
#   b. AGENT_SANDBOX=1 env var set (operator attestation)
#   c. macOS sandbox-exec profile active (SANDBOX_EXEC_PROFILE set)
#   d. Claude Code settings whose parsed JSON has sandbox.enabled == true.
#      settings.local.json overrides settings.json. The mere presence of a
#      "sandbox" key is NOT enough: {"sandbox":{"enabled":false}} fails.
SANDBOX_OK="fail"
SANDBOX_DETAIL="no sandbox indicator detected"

# Prints "true", "false", "unset", or "error:<reason>" for the effective
# sandbox.enabled value across the project's Claude Code settings files.
claude_sandbox_state() {
  command -v python3 &>/dev/null || { echo "error:python3 not found; cannot parse settings"; return; }
  python3 - "$1" <<'PY'
import json, os, sys
root = sys.argv[1]
for name in ("settings.local.json", "settings.json"):
    path = os.path.join(root, ".claude", name)
    if not os.path.isfile(path):
        continue
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"error:{name} is not valid JSON ({exc.__class__.__name__})")
        sys.exit(0)
    sandbox = data.get("sandbox") if isinstance(data, dict) else None
    if isinstance(sandbox, dict) and "enabled" in sandbox:
        print("true" if sandbox["enabled"] is True else f"false:{name}")
        sys.exit(0)
print("unset")
PY
}

CLAUDE_SANDBOX="$(claude_sandbox_state "$SEARCH_ROOT")"

if [[ -f "/.dockerenv" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="container environment detected (/.dockerenv)"
elif grep -q 'docker\|lxc\|containerd' /proc/1/cgroup 2>/dev/null; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="cgroup sandbox marker detected"
elif [[ "${AGENT_SANDBOX:-}" == "1" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="AGENT_SANDBOX=1 env var set"
elif [[ -n "${SANDBOX_EXEC_PROFILE:-}" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="macOS sandbox-exec profile active: $SANDBOX_EXEC_PROFILE"
elif [[ "$CLAUDE_SANDBOX" == "true" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="sandbox.enabled is true in .claude settings"
elif [[ "$CLAUDE_SANDBOX" == false:* ]]; then
  SANDBOX_DETAIL="sandbox.enabled is not true in .claude/${CLAUDE_SANDBOX#false:}"
elif [[ "$CLAUDE_SANDBOX" == error:* ]]; then
  SANDBOX_DETAIL="${CLAUDE_SANDBOX#error:}"
fi

# Warn rather than hard-fail when running interactively outside CI
if [[ "$SANDBOX_OK" == "fail" && -t 0 ]]; then
  SANDBOX_DETAIL="$SANDBOX_DETAIL (interactive shell — set AGENT_SANDBOX=1 or run inside a container)"
fi
check "Sandbox engaged" "$SANDBOX_OK" "$SANDBOX_DETAIL"

# ── Report ────────────────────────────────────────────────────────────────────
echo ""
echo "Coding-agent smoke test"
echo "─────────────────────────────────────────────────────"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo "─────────────────────────────────────────────────────"
echo "  Passed: $PASS / $((PASS + FAIL))"
echo ""

if (( FAIL > 0 )); then
  echo "Resolution: fix the [FAIL] items above before starting your coding-agent session."
  echo "  • CLI/API failed     → install the CLI, or set ANTHROPIC_API_KEY + SMOKE_TEST_MODEL, or OPENAI_API_KEY"
  echo "  • Registry missing   → run from the project root that has .claude/ or .codex/"
  echo "  • Sandbox not found  → start a container, set AGENT_SANDBOX=1, or set sandbox.enabled: true in .claude settings"
  exit 1
fi

echo "All checks passed. The CLI check is an install check; confirm model access in the first session."
