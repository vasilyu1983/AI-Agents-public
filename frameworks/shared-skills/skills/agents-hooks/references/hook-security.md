# Hook Security Guide

Security best practices for Claude Code hooks. Hooks run with full user permissions—no sandboxing.

Assumptions (Jan 2026):
- Hook input arrives as JSON via stdin (parse with `jq`).
- Don’t assume `CLAUDE_TOOL_NAME`, `CLAUDE_TOOL_INPUT`, `CLAUDE_FILE_PATHS`, or `CLAUDE_SESSION_ID` exist as environment variables; derive from stdin instead.

---

## Critical Rules

```text
HOOK SECURITY CHECKLIST

[x] Validate all inputs with regex
[x] Quote all variables: "$VAR" not $VAR
[x] Use absolute paths
[x] No eval with untrusted input
[x] Set -euo pipefail at top
[x] Keep hooks fast (<1 second)
[x] Log actions for audit
[x] Test manually before deploying
```

---

## Command Injection Prevention

### Dangerous Pattern

```bash
# NEVER do this - command injection risk
eval "$(cat)"
bash -c "$USER_PROVIDED_COMMAND"
$(echo "$UNTRUSTED_DATA")
```

### Safe Pattern

```bash
#!/bin/bash
set -euo pipefail

# Validate input is safe before use (example: file path from an Edit/Write hook)
INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

# Only allow alphanumeric, dash, underscore, dot, slash
if [[ -z "$FILE_PATH" || ! "$FILE_PATH" =~ ^[a-zA-Z0-9_./-]+$ ]]; then
  echo "ERROR: Invalid characters in input" >&2
  exit 2
fi

# Now safe to use
cat "$FILE_PATH"
```

### Allowlist Approach

```bash
#!/bin/bash
set -euo pipefail

COMMAND="$1"

# Only allow specific commands
case "$COMMAND" in
  lint)   npm run lint ;;
  test)   npm test ;;
  build)  npm run build ;;
  *)
    echo "ERROR: Unknown command: $COMMAND" >&2
    exit 2
    ;;
esac
```

---

## Path Traversal Defense

### Dangerous Pattern

```bash
# Attacker could pass: "../../../etc/passwd"
cat "$CLAUDE_PROJECT_DIR/$USER_FILE"
```

### Safe Pattern

```bash
#!/bin/bash
set -euo pipefail

FILE="$1"

# Block path traversal
if [[ "$FILE" == *".."* ]]; then
  echo "ERROR: Path traversal detected" >&2
  exit 2
fi

# Resolve to absolute and verify within project
RESOLVED=$(realpath -m "$CLAUDE_PROJECT_DIR/$FILE")
if [[ "$RESOLVED" != "$CLAUDE_PROJECT_DIR"/* ]]; then
  echo "ERROR: Path outside project" >&2
  exit 2
fi

# Now safe
cat "$RESOLVED"
```

### Canonical Path Check

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

validate_path() {
  local file="$1"
  local base="$CLAUDE_PROJECT_DIR"

  # Get canonical paths
  local canonical_base=$(cd "$base" && pwd -P)
  local canonical_file=$(cd "$(dirname "$file")" 2>/dev/null && pwd -P)/$(basename "$file")

  # Must be under project root
  if [[ "$canonical_file" != "$canonical_base"/* ]]; then
    return 1
  fi

  return 0
}

if ! validate_path "$FILE_PATH"; then
  echo "ERROR: Invalid path: $FILE_PATH" >&2
  exit 2
fi
```

---

## Variable Quoting

### Dangerous Pattern

```bash
# Word splitting and glob expansion risk
rm $FILE
cat $FILE_PATH
```

### Safe Pattern

```bash
#!/bin/bash
set -euo pipefail

# Always quote variables
rm "$FILE"

# For paths derived from stdin JSON, avoid word splitting:
INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -n "$FILE_PATH" ]] && cat "$FILE_PATH"
```

---

## Credential Protection

### Never Log Secrets

```bash
#!/bin/bash
set -euo pipefail

# WRONG: May expose secrets
echo "Input: $(cat)"
echo "Env: $(env)"

# RIGHT: Sanitize before logging
INPUT="$(cat)"
CMD="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"
SAFE_CMD="$(echo "$CMD" | sed 's/password=[^ ]*/password=REDACTED/g')"
echo "Command: $SAFE_CMD"
```

### Skip Sensitive Files

```bash
#!/bin/bash
set -euo pipefail

SENSITIVE_PATTERNS="\.env|\.env\.|credentials|secrets|\.pem|\.key|id_rsa"

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

if echo "$FILE_PATH" | grep -qE "$SENSITIVE_PATTERNS"; then
  echo "SKIP: Sensitive file $FILE_PATH" >&2
  exit 0
fi

process_file "$FILE_PATH"
```

### Block Credential Commits

```bash
#!/bin/bash
# pre-tool-validate.sh for Bash tool
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
CMD="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"

if [[ "$TOOL_NAME" == "Bash" ]]; then
  # Block git add of sensitive files
  if echo "$CMD" | grep -qE 'git\s+add.*\.(env|pem|key)'; then
    echo "BLOCKED: Cannot stage sensitive files" >&2
    exit 2
  fi
fi

exit 0
```

---

## Audit Logging

### Comprehensive Audit Log

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // empty')"

LOG_DIR="$CLAUDE_PROJECT_DIR/.claude/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/audit-$(date +%Y-%m-%d).log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
USER=$(whoami)

# Structured log entry
cat >> "$LOG_FILE" << EOF
{"timestamp":"$TIMESTAMP","user":"$USER","tool":"$TOOL_NAME","session":"$SESSION_ID"}
EOF
```

### Tamper-Evident Logging

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/audit.jsonl"

# Append-only with hash chain
PREV_HASH=""
[[ -f "$LOG_FILE" ]] && PREV_HASH=$(tail -1 "$LOG_FILE" | sha256sum | cut -d' ' -f1)

ENTRY="{\"ts\":\"$(date -u +%s)\",\"tool\":\"$TOOL_NAME\",\"prev\":\"$PREV_HASH\"}"
echo "$ENTRY" >> "$LOG_FILE"
```

---

## Resource Limits

### Timeout Protection

```bash
#!/bin/bash
set -euo pipefail

# Kill hook if takes too long
INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

timeout 5s npm run lint -- "$FILE_PATH" || {
  echo "ERROR: Lint timed out" >&2
  exit 1
}
```

### Memory Limit

```bash
#!/bin/bash
set -euo pipefail

# Limit memory usage (Linux)
ulimit -v 500000  # 500MB virtual memory

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

node expensive-analysis.js "$FILE_PATH"
```

### Output Truncation

```bash
#!/bin/bash
set -euo pipefail

# Prevent massive output
npm test 2>&1 | head -100

# Or use tail for recent output
npm run build 2>&1 | tail -50
```

---

## Testing Hooks Safely

### Manual Testing

```bash
export CLAUDE_PROJECT_DIR="$(pwd)"

# Run hook with stdin JSON
echo '{"hook_event_name":"PostToolUse","session_id":"test-session","tool_name":"Edit","tool_input":{"file_path":"'"$(pwd)"'/src/test.ts"}}' \
  | bash .claude/hooks/post-tool-format.sh

# Check exit code
echo "Exit code: $?"
```

### Dry Run Mode

```bash
#!/bin/bash
set -euo pipefail

DRY_RUN="${DRY_RUN:-false}"

if [[ "$DRY_RUN" == "true" ]]; then
  INPUT="$(cat)"
  FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
  echo "DRY RUN: Would format $FILE_PATH"
  exit 0
fi

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
prettier --write "$FILE_PATH"
```

### Sandboxed Testing

```bash
# Test in temporary directory
TEMP_DIR=$(mktemp -d)
cp -r . "$TEMP_DIR"
cd "$TEMP_DIR"

CLAUDE_PROJECT_DIR="$TEMP_DIR" bash .claude/hooks/dangerous-hook.sh

# Cleanup
rm -rf "$TEMP_DIR"
```

---

## Common Vulnerabilities

| Vulnerability | Example | Fix |
|--------------|---------|-----|
| Command injection | `eval "$INPUT"` | Use allowlist |
| Path traversal | `cat "../$FILE"` | Validate paths |
| Word splitting | `rm $FILES` | Quote: `"$FILES"` |
| Glob expansion | `cat *.txt` | Quote or disable |
| Secret exposure | `echo "$API_KEY"` | Redact logs |
| Symlink attacks | `cat "$LINK"` | Use `realpath -P` |
| Race conditions | Check-then-use | Atomic operations |

---

## Security Review Checklist

Before deploying a hook:

```text
[ ] No eval, bash -c, or $() with untrusted input
[ ] All variables quoted
[ ] Path traversal blocked
[ ] Sensitive files skipped
[ ] Output sanitized (no secrets logged)
[ ] Timeout protection added
[ ] Tested in isolation
[ ] Exit codes correct (0=ok, 1=error, 2=block)
[ ] ShellCheck passes with no errors
[ ] Script under 50 lines (or refactored)
```

---

## Tooling Requirements

### ShellCheck (Mandatory)

All hook scripts must pass ShellCheck before deployment.

```bash
# Install
brew install shellcheck        # macOS
apt install shellcheck         # Debian/Ubuntu
pacman -S shellcheck           # Arch

# Run on all hooks
shellcheck .claude/hooks/*.sh

# CI integration (GitHub Actions)
- name: Lint hooks
  run: shellcheck .claude/hooks/*.sh --severity=warning
```

### Common ShellCheck Fixes

| Code | Issue | Fix |
|------|-------|-----|
| SC2086 | Unquoted variable | `"$VAR"` not `$VAR` |
| SC2046 | Unquoted command substitution | `"$(cmd)"` not `$(cmd)` |
| SC2006 | Legacy backticks | `$(cmd)` not `` `cmd` `` |
| SC2164 | cd without || exit | `cd dir || exit 1` |

### Inline Suppressions

```bash
# Suppress specific warning (use sparingly)
# shellcheck disable=SC2086
echo $KNOWN_SAFE_VAR
```

---

## Script Size Guidelines

Google's Shell Style Guide recommends keeping scripts under 50 lines.

### Why 50 Lines?

- Easier to audit for security issues
- Faster execution (less parsing)
- More maintainable
- Forces modular design

### When Scripts Grow

If a hook exceeds 50 lines:

1. **Split into multiple hooks** — Chain in settings.json
2. **Use a real language** — Python, Node.js, Go
3. **Create a CLI tool** — Compile and distribute

### Example: Refactoring Large Hook

**Before** (80 lines):
```bash
#!/bin/bash
# All-in-one formatting, linting, testing hook
# ... 80 lines of bash ...
```

**After** (3 hooks, 20 lines each):
```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": ".claude/hooks/01-format.sh" },
        { "type": "command", "command": ".claude/hooks/02-lint.sh" },
        { "type": "command", "command": ".claude/hooks/03-test.sh" }
      ]
    }
  ]
}
```

---

## Navigation

- [SKILL.md](../SKILL.md) - Main reference
- [hook-patterns.md](hook-patterns.md) - Common patterns
