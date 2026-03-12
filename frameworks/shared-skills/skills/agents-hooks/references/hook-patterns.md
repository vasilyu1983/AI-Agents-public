# Hook Patterns

Common patterns for Claude Code hooks.

Assumptions (Jan 2026):
- Hook input arrives as JSON via stdin (parse with `jq`).
- The only reliable hook env var is `CLAUDE_PROJECT_DIR` (plus plugin/session vars like `CLAUDE_CODE_REMOTE` when applicable).

---

## CI/CD Integration

### Headless Mode for Automation

```bash
# Pre-commit hook
claude -p "Review staged changes for issues" --output-format stream-json

# GitHub Actions
claude -p "Analyze PR #$PR_NUMBER for security issues" \
  --allowedTools "Read,Grep,Glob" \
  --output-format json
```

### Pre-Commit Hook Script

```bash
#!/bin/bash
# .git/hooks/pre-commit
set -euo pipefail

# Get staged files
STAGED=$(git diff --cached --name-only --diff-filter=ACM)

if [[ -z "$STAGED" ]]; then
  exit 0
fi

# Run Claude analysis
claude -p "Check these files for issues: $STAGED" \
  --allowedTools "Read,Grep" \
  --max-turns 3

exit $?
```

---

## Multi-Hook Composition

### Chain: Format → Lint → Test

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": ".claude/hooks/01-format.sh" },
        { "type": "command", "command": ".claude/hooks/02-lint.sh" },
        { "type": "command", "command": ".claude/hooks/03-typecheck.sh" }
      ]
    }
  ]
}
```

All matching hooks run in parallel. If you need strict ordering, run one wrapper hook that sequences sub-steps:

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
printf '%s' "$INPUT" | "$CLAUDE_PROJECT_DIR/.claude/hooks/01-format.sh"
printf '%s' "$INPUT" | "$CLAUDE_PROJECT_DIR/.claude/hooks/02-lint.sh"
printf '%s' "$INPUT" | "$CLAUDE_PROJECT_DIR/.claude/hooks/03-typecheck.sh"
```

### Context Window Optimization

**Problem**: Every PostToolUse formatting change triggers a system reminder to Claude. Aggressive formatting wastes context tokens that could be doing useful work.

**Solution**: Format on commit, not on every edit.

```json
{
  "PostToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": ".claude/hooks/format-on-commit.sh"
        }
      ]
    }
  ]
}
```

```bash
#!/bin/bash
# format-on-commit.sh - Only format when committing
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only run formatter on git commit
if [[ "$COMMAND" =~ ^git\ commit ]]; then
  # Format all staged files
  STAGED=$(git diff --cached --name-only --diff-filter=ACM)
  for file in $STAGED; do
    case "${file##*.}" in
      ts|tsx|js|jsx|json) npx prettier --write "$file" 2>/dev/null ;;
      py) ruff format "$file" 2>/dev/null ;;
    esac
  done
fi

exit 0
```

**Alternative**: Use a pre-commit git hook instead of PostToolUse.

### Parallel Execution Pattern

```bash
#!/bin/bash
# Run checks in parallel, collect results
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

pids=()
results=()

# Start parallel jobs
prettier --check "$FILE_PATH" &
pids+=($!)

eslint "$FILE_PATH" &
pids+=($!)

# Wait and collect
for pid in "${pids[@]}"; do
  wait "$pid" && results+=(0) || results+=($?)
done

# Fail if any failed
for r in "${results[@]}"; do
  [[ "$r" -ne 0 ]] && exit 1
done

exit 0
```

---

## Notification Patterns

### Slack Notification on Stop

```bash
#!/bin/bash
# stop-notify-slack.sh
set -euo pipefail

WEBHOOK_URL="${SLACK_WEBHOOK:-}"
[[ -z "$WEBHOOK_URL" ]] && exit 0

MESSAGE="Claude completed session in $(basename "$CLAUDE_PROJECT_DIR")"

curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$MESSAGE\"}" \
  >/dev/null

exit 0
```

### Desktop Notification (macOS)

```bash
#!/bin/bash
# stop-notify-desktop.sh
set -euo pipefail

osascript -e "display notification \"Task completed\" with title \"Claude Code\""

exit 0
```

### Log to File

```bash
#!/bin/bash
# post-tool-log.sh
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(echo "$INPUT" | jq -r '.tool_name // empty')"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/audit.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "[$TIMESTAMP] Tool: $TOOL_NAME, File: $FILE_PATH" >> "$LOG_FILE"

exit 0
```

---

## Error Recovery Patterns

### Retry on Transient Failure

```bash
#!/bin/bash
set -euo pipefail

MAX_RETRIES=3
RETRY_DELAY=1

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"

for i in $(seq 1 $MAX_RETRIES); do
  if npm run lint -- "$FILE_PATH"; then
    exit 0
  fi

  [[ $i -lt $MAX_RETRIES ]] && sleep $RETRY_DELAY
done

echo "Failed after $MAX_RETRIES retries"
exit 1
```

### Fallback Command

```bash
#!/bin/bash
set -euo pipefail

# Common case: PostToolUse with matcher Edit|Write
INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

# Try prettier, fall back to eslint --fix
if command -v prettier &>/dev/null; then
  prettier --write "$FILE_PATH"
elif command -v eslint &>/dev/null; then
  eslint --fix "$FILE_PATH"
else
  echo "No formatter available"
fi

exit 0
```

---

## Conditional Execution

### By File Type

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

case "${FILE_PATH##*.}" in
  ts|tsx|js|jsx) npx prettier --write "$FILE_PATH" ;;
  py)            ruff format "$FILE_PATH" ;;
  go)            gofmt -w "$FILE_PATH" ;;
  rs)            rustfmt "$FILE_PATH" ;;
  *)             echo "Skipping: $FILE_PATH" ;;
esac

exit 0
```

### By Directory

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

case "$FILE_PATH" in
  src/*)      npm run lint -- "$FILE_PATH" ;;
  tests/*)    npm run test -- "$FILE_PATH" ;;
  docs/*)     npx markdownlint "$FILE_PATH" ;;
esac

exit 0
```

### Skip Certain Files

```bash
#!/bin/bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

SKIP_PATTERNS="node_modules|dist|.min.|vendor"

if echo "$FILE_PATH" | grep -qE "$SKIP_PATTERNS"; then
  exit 0
fi

prettier --write "$FILE_PATH"

exit 0
```

---

## Environment Setup

### Session Start: Verify Prerequisites

```bash
#!/bin/bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

# Check Node.js version
if command -v node &>/dev/null; then
  NODE_VERSION=$(node -v | cut -d. -f1 | tr -d 'v')
  [[ $NODE_VERSION -lt 18 ]] && echo "WARNING: Node.js 18+ recommended"
fi

# Check dependencies
[[ -f "package.json" && ! -d "node_modules" ]] && echo "NOTE: Run npm install"
[[ -f "requirements.txt" && ! -d ".venv" ]] && echo "NOTE: Create virtualenv"

# Check git state
if git rev-parse --git-dir &>/dev/null; then
  BRANCH=$(git branch --show-current)
  echo "Branch: $BRANCH"

  if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
    echo "WARNING: Working on protected branch"
  fi
fi

exit 0
```

---

## Cost Tracking

### Token Usage Logger

```bash
#!/bin/bash
# stop-token-log.sh
set -euo pipefail

INPUT="$(cat)"
SESSION_ID="$(echo "$INPUT" | jq -r '.session_id // empty')"

LOG_FILE="$CLAUDE_PROJECT_DIR/.claude/token-usage.csv"
TIMESTAMP=$(date -u +"%Y-%m-%d")

# Create header if new file
[[ ! -f "$LOG_FILE" ]] && echo "date,session_id,project" > "$LOG_FILE"

echo "$TIMESTAMP,$SESSION_ID,$(basename "$CLAUDE_PROJECT_DIR")" >> "$LOG_FILE"

exit 0
```

---

## Navigation

- [SKILL.md](../SKILL.md) - Main reference
- [hook-security.md](hook-security.md) - Security guide
