# Hook Templates

Ready-to-use shell scripts for common Claude Code hook scenarios.

Assumptions (Jan 2026):
- Hook input arrives as JSON via stdin (parse with `jq`).
- Scripts run with full user permissions; use `set -euo pipefail` and validate input.

---

## Pre-Tool Validation

Guards the Bash tool against dangerous commands. Use with `PreToolUse` + `matcher: "Bash"`.

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name')"
CMD="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"

if [[ "$TOOL_NAME" == "Bash" ]]; then
  # Block rm -rf /
  if echo "$CMD" | grep -qE 'rm\s+-rf\s+/'; then
    echo '{}' | jq -cn '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Dangerous rm command detected"
      }
    }'
    exit 0
  fi

  # Block force push to main
  if echo "$CMD" | grep -qE 'git\s+push.*--force.*(main|master)'; then
    echo '{}' | jq -cn '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Force push to main/master not allowed"
      }
    }'
    exit 0
  fi

  # Soft-warning: possible credential exposure
  if echo "$CMD" | grep -qE '(password|secret|api_key)\s*='; then
    echo '{}' | jq -cn '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: "Possible credential exposure in command",
        additionalContext: "Command may include a secret. Confirm intent and avoid committing secrets."
      }
    }'
    exit 0
  fi
fi

exit 0
```

---

## Post-Tool Formatting

Auto-formats files after Edit/Write. Use with `PostToolUse` + `matcher: "Edit|Write"`.

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name')"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ && -n "$FILE_PATH" && -f "$FILE_PATH" ]]; then
  case "$FILE_PATH" in
    *.js|*.ts|*.jsx|*.tsx|*.json|*.md)
      npx prettier --write "$FILE_PATH" 2>/dev/null || true
      ;;
    *.py)
      ruff format "$FILE_PATH" 2>/dev/null || true
      ;;
    *.go)
      gofmt -w "$FILE_PATH" 2>/dev/null || true
      ;;
    *.rs)
      rustfmt "$FILE_PATH" 2>/dev/null || true
      ;;
  esac
fi

exit 0
```

---

## Post-Tool Security Audit

Checks for hardcoded secrets and debug statements after Edit/Write.

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name')"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

if [[ "$TOOL_NAME" =~ ^(Edit|Write)$ && -n "$FILE_PATH" && -f "$FILE_PATH" ]]; then
  # Check for hardcoded secrets
  if grep -qE '(password|secret|api_key|token)\s*[:=]\s*["\x27][^"\x27]+["\x27]' "$FILE_PATH"; then
    echo "WARNING: Possible hardcoded secret in $FILE_PATH" >&2
  fi

  # Check for console.log in production code
  if [[ "$FILE_PATH" =~ \.(ts|js|tsx|jsx)$ ]] && grep -q 'console.log' "$FILE_PATH"; then
    echo "NOTE: console.log found in $FILE_PATH" >&2
  fi
fi

exit 0
```

---

## Stop Hook (Run Tests)

Runs the project test suite after Claude finishes. Use with `Stop`.

```bash
#!/bin/bash
set -euo pipefail

# Run tests after Claude finishes
cd "$CLAUDE_PROJECT_DIR"

# Detect test framework
if [[ -f "package.json" ]]; then
  if grep -q '"vitest"' package.json; then
    npm run test 2>&1 | head -50
  elif grep -q '"jest"' package.json; then
    npm test 2>&1 | head -50
  fi
elif [[ -f "pytest.ini" ]] || [[ -f "pyproject.toml" ]]; then
  pytest --tb=short 2>&1 | head -50
fi

exit 0
```

---

## Session Start

Checks git state and dependencies at session startup.

```bash
#!/bin/bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

# Check git status
echo "=== Git Status ==="
git status --short

# Check for uncommitted changes
if ! git diff --quiet; then
  echo "WARNING: Uncommitted changes detected"
fi

# Verify dependencies
if [[ -f "package.json" ]]; then
  if [[ ! -d "node_modules" ]]; then
    echo "NOTE: node_modules missing, run npm install"
  fi
fi

exit 0
```

---

## Input Modification: Redirect Sensitive File Edits

Redirects writes to `package-lock.json` to `/dev/null` using `updatedInput`.

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

# Redirect package-lock.json edits to /dev/null
if [[ "$FILE_PATH" == *"package-lock.json" ]]; then
  UPDATED_INPUT="$(echo "$INPUT" | jq -c '.tool_input | .file_path = "/dev/null"')"
  jq -cn --argjson updatedInput "$UPDATED_INPUT" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: "Redirected write to /dev/null",
      updatedInput: $updatedInput
    }
  }'
  exit 0
fi

echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
```

---

## Input Modification: Strip Sensitive Files from Git Add

Removes `.env` files from `git add` commands before execution.

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name')"
CMD="$(echo "$INPUT" | jq -r '.tool_input.command // empty')"

if [[ "$TOOL_NAME" == "Bash" && "$CMD" =~ ^git[[:space:]]+add ]]; then
  # Remove .env files from staging
  SAFE_CMD="$(echo "$CMD" | sed 's/\.env[^ ]*//g')"
  if [[ "$SAFE_CMD" != "$CMD" ]]; then
    echo '{}' | jq -cn --arg cmd "$SAFE_CMD" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "allow",
        permissionDecisionReason: "Removed .env from git add",
        updatedInput: { command: $cmd }
      }
    }'
    exit 0
  fi
fi

echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}'
```

---

## Navigation

- [SKILL.md](../SKILL.md) — Main reference
- [hook-patterns.md](hook-patterns.md) — Advanced patterns (CI/CD, composition, notifications)
- [hook-security.md](hook-security.md) — Security guide
