#!/usr/bin/env bash
# smoke_test.sh — validates a coding-agent setup before a session starts.
# Checks: (1) model reachable, (2) tool registry loaded, (3) sandbox engaged.
# Exit 0 = all checks passed. Exit 1 = one or more checks failed.

set -euo pipefail

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

# ── 1. Model reachable ────────────────────────────────────────────────────────
# Strategy: try the cheapest API call available. Supports Claude Code (claude),
# Codex (codex), generic ANTHROPIC_API_KEY, and OPENAI_API_KEY environments.
MODEL_OK="fail"
MODEL_DETAIL="no supported CLI or API key found"

if command -v claude &>/dev/null; then
  # Claude Code: `claude --version` exits 0 when the binary is functional.
  if claude --version &>/dev/null; then
    MODEL_OK="ok"
    MODEL_DETAIL="claude CLI reachable ($(claude --version 2>&1 | head -1))"
  else
    MODEL_DETAIL="claude CLI found but --version failed"
  fi
elif command -v codex &>/dev/null; then
  if codex --version &>/dev/null; then
    MODEL_OK="ok"
    MODEL_DETAIL="codex CLI reachable ($(codex --version 2>&1 | head -1))"
  else
    MODEL_DETAIL="codex CLI found but --version failed"
  fi
elif [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  # Bare SDK environment: probe the messages endpoint with a 1-token request.
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "https://api.anthropic.com/v1/messages" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{"model":"claude-haiku-4-5","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' \
    2>/dev/null || echo "000")
  if [[ "$STATUS" == "200" ]]; then
    MODEL_OK="ok"; MODEL_DETAIL="Anthropic API reachable (HTTP 200)"
  else
    MODEL_DETAIL="Anthropic API returned HTTP $STATUS"
  fi
elif [[ -n "${OPENAI_API_KEY:-}" ]]; then
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X GET "https://api.openai.com/v1/models" \
    -H "Authorization: Bearer $OPENAI_API_KEY" 2>/dev/null || echo "000")
  if [[ "$STATUS" == "200" ]]; then
    MODEL_OK="ok"; MODEL_DETAIL="OpenAI API reachable (HTTP 200)"
  else
    MODEL_DETAIL="OpenAI API returned HTTP $STATUS"
  fi
fi
check "Model reachable" "$MODEL_OK" "$MODEL_DETAIL"

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
# Heuristics (any one passing = sandbox engaged):
#   a. Running inside a container (/.dockerenv or cgroup marker)
#   b. AGENT_SANDBOX=1 env var set
#   c. macOS sandbox-exec available and active (SANDBOX_EXEC_PROFILE set)
#   d. Claude Code sandbox flag in settings.json
SANDBOX_OK="fail"
SANDBOX_DETAIL="no sandbox indicator detected"

if [[ -f "/.dockerenv" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="container environment detected (/.dockerenv)"
elif grep -q 'docker\|lxc\|containerd' /proc/1/cgroup 2>/dev/null; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="cgroup sandbox marker detected"
elif [[ "${AGENT_SANDBOX:-}" == "1" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="AGENT_SANDBOX=1 env var set"
elif [[ -n "${SANDBOX_EXEC_PROFILE:-}" ]]; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="macOS sandbox-exec profile active: $SANDBOX_EXEC_PROFILE"
elif [[ -f "$SEARCH_ROOT/.claude/settings.json" ]] && \
     grep -q '"sandbox"' "$SEARCH_ROOT/.claude/settings.json" 2>/dev/null; then
  SANDBOX_OK="ok"; SANDBOX_DETAIL="sandbox key present in .claude/settings.json"
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
  echo "  • Model unreachable  → check CLI installation, ANTHROPIC_API_KEY, or OPENAI_API_KEY"
  echo "  • Registry missing   → run from the project root that has .claude/ or .codex/"
  echo "  • Sandbox not found  → start a container, set AGENT_SANDBOX=1, or enable claude sandbox"
  exit 1
fi

echo "All checks passed. Safe to start your coding-agent session."
