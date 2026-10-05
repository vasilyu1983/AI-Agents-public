#!/usr/bin/env bash
# test_memory_scripts.sh — regression tests for the four memory validators.
#
# Each case encodes a fail-closed contract: bad, empty, or missing input must
# exit non-zero, and a well-formed repo must pass. Run from anywhere:
#
#   bash skills/universal/agents-memory/scripts/test_memory_scripts.sh
#
# Uses ${TMPDIR:-/tmp} for fixtures so it works inside sandboxes that block the
# platform default temp directory.

set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
work="$(mktemp -d "${TMPDIR:-/tmp}/memory-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

pass=0
fail=0

expect_exit() {
  # expect_exit <expected-code> <label> <command...>
  local want="$1" label="$2"; shift 2
  local out got
  out="$("$@" 2>&1)"; got=$?
  if [[ "$got" -eq "$want" ]]; then
    pass=$((pass + 1))
    echo "  [PASS] $label (exit $got)"
  else
    fail=$((fail + 1))
    echo "  [FAIL] $label: expected exit $want, got $got"
    printf '%s\n' "$out" | sed 's/^/         /' | head -20
  fi
}

# ---- fixtures ----
good="$work/good"
mkdir -p "$good/src"
cat >"$good/AGENTS.md" <<'EOF'
# Repo Guidelines

- Run `bash scripts/test.sh` before handoff.
- Never commit `.env`.
EOF
mkdir -p "$good/scripts"
printf '#!/usr/bin/env bash\nexit 0\n' >"$good/scripts/test.sh"
chmod +x "$good/scripts/test.sh"

empty_repo="$work/empty"
mkdir -p "$empty_repo"

blank_file="$work/blank"
mkdir -p "$blank_file"
printf '\n\n' >"$blank_file/AGENTS.md"

twin="$work/twin"
mkdir -p "$twin"
cp "$good/AGENTS.md" "$twin/AGENTS.md"

missing="$work/does-not-exist"

echo "lint_claude_memory.sh"
expect_exit 0 "well-formed repo passes" bash "$here/lint_claude_memory.sh" "$good"
expect_exit 1 "repo with no memory files fails closed" bash "$here/lint_claude_memory.sh" "$empty_repo"
expect_exit 1 "missing repo path fails" bash "$here/lint_claude_memory.sh" "$missing"

echo "audit_repo.sh"
expect_exit 0 "well-formed repo passes" bash "$here/audit_repo.sh" "$good"
expect_exit 1 "repo with no memory files fails closed" bash "$here/audit_repo.sh" "$empty_repo"
expect_exit 1 "repo with no memory files fails closed (--json)" bash "$here/audit_repo.sh" "$empty_repo" --json
expect_exit 1 "blank AGENTS.md is a HIGH finding" bash "$here/audit_repo.sh" "$blank_file"
expect_exit 2 "missing repo path is a usage error" bash "$here/audit_repo.sh" "$missing"

echo "audit_portfolio.sh"
expect_exit 0 "portfolio of one clean repo passes" bash "$here/audit_portfolio.sh" "$good"
expect_exit 1 "portfolio containing a missing path fails closed" bash "$here/audit_portfolio.sh" "$good" "$missing"
expect_exit 1 "portfolio containing a memory-less repo fails closed" bash "$here/audit_portfolio.sh" "$good" "$empty_repo"

echo "compare_blocks.sh"
expect_exit 2 "fewer than two repos is a usage error" bash "$here/compare_blocks.sh" "$good"
expect_exit 2 "missing repo path is rejected" bash "$here/compare_blocks.sh" "$good" "$missing"
expect_exit 0 "two real repos compare" bash "$here/compare_blocks.sh" "$good" "$twin"

echo
echo "passed: $pass  failed: $fail"
[[ "$fail" -eq 0 ]]
