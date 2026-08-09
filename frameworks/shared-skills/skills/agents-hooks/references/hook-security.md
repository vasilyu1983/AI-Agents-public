# Hook Security Guide

Security rules for Claude command hooks and adjacent notification scripts.

Assumptions:

- Claude command hooks run with full user permissions and receive untrusted JSON via stdin.
- Codex notification callbacks are also local programs and should be treated as untrusted event inputs.
- Event support differs by hook type; unsupported JSON fields are a correctness risk, not just a style issue.

---
## Table of Contents

- [Critical Rules](#critical-rules)
- [1. Treat Event Payloads As Untrusted](#1-treat-event-payloads-as-untrusted)
- [2. Canonical Path Validation](#2-canonical-path-validation)
- [3. Command Injection Prevention](#3-command-injection-prevention)
- [4. Variable Quoting](#4-variable-quoting)
- [5. Logging And Notification Hygiene](#5-logging-and-notification-hygiene)
- [6. Event-Specific Output Safety](#6-event-specific-output-safety)
- [7. Avoid Silent Data Discard](#7-avoid-silent-data-discard)
- [8. Sensitive File Policy](#8-sensitive-file-policy)
- [9. Synchronous Performance Budget](#9-synchronous-performance-budget)
- [10. Validation Workflow](#10-validation-workflow)
- [Navigation](#navigation)


## Critical Rules

```text
HOOK SECURITY CHECKLIST

[x] Parse stdin JSON explicitly
[x] Validate every field before use
[x] Prefer canonical path validation over regex alone
[x] Quote every shell variable
[x] Never use eval on hook input
[x] Keep synchronous hooks fast
[x] Redact logs and notifications
[x] Match JSON output to the specific event schema
[x] Run ShellCheck on non-trivial scripts
```

---

## 1. Treat Event Payloads As Untrusted

Do not assume:

- file paths are safe
- shell commands are trustworthy
- event payloads share the same schema across all hook types
- notification text is safe to log or interpolate directly

Parse only the fields you need and validate them before use.

Safe extraction pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -er '.tool_name // empty')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -er '.tool_input.file_path // empty' 2>/dev/null || true)"
```

---

## 2. Canonical Path Validation

Regex can reject obvious garbage, but it does not prove a path stays inside the project root.

Prefer:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"
[[ -z "$FILE_PATH" ]] && exit 0

BASE="$(cd "$CLAUDE_PROJECT_DIR" && pwd -P)"
TARGET="$(python3 - <<'PY' "$BASE" "$FILE_PATH"
import os
import sys
base = sys.argv[1]
path = sys.argv[2]
candidate = path if os.path.isabs(path) else os.path.join(base, path)
print(os.path.realpath(candidate))
PY
)"

case "$TARGET" in
  "$BASE"/*) ;;
  *)
    echo "ERROR: Path outside project root: $FILE_PATH" >&2
    exit 2
    ;;
esac
```

Use lightweight regex filtering only as an extra guard, not the primary one.

---

## 3. Command Injection Prevention

Never do this:

```bash
eval "$(cat)"
bash -c "$USER_PROVIDED_COMMAND"
$(echo "$UNTRUSTED_DATA")
```

Prefer deterministic command families and fixed tooling.

Safe command family pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"

case "$ACTION" in
  lint) npm run lint ;;
  test) npm test ;;
  build) npm run build ;;
  *)
    echo "ERROR: Unsupported action: $ACTION" >&2
    exit 2
    ;;
esac
```

---

## 4. Variable Quoting

Always quote variables and use `printf '%s'` when piping potentially unsafe values.

Unsafe:

```bash
rm $FILE
echo $INPUT | jq .
```

Safer:

```bash
rm "$FILE"
printf '%s' "$INPUT" | jq .
```

---

## 5. Logging And Notification Hygiene

Do not log raw hook payloads or full environments.

Unsafe:

```bash
echo "Input: $(cat)"
env
```

Safer:

```bash
INPUT="$(cat)"
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
SAFE_CMD="$(printf '%s' "$CMD" | sed -E 's/(password|secret|token)=([^ ]+)/\1=REDACTED/gI')"
echo "Command: $SAFE_CMD"
```

Apply the same redaction rules to Codex `notify` callbacks before sending desktop notifications, chat messages, or audit records.

---

## 6. Event-Specific Output Safety

Do not emit Claude hook JSON fields unless the current event supports them.

Examples:

- `PreToolUse`: allow/deny/ask and `updatedInput` are appropriate
- `PermissionRequest`: approval decisions are event-specific
- `PostToolUse`: use only the documented result-update fields for that event
- Codex `notify`: do not emit Claude `hookSpecificOutput` payloads at all

Wrong schema on the wrong event produces confusing failures and false confidence.

---

## 7. Avoid Silent Data Discard

Do not default to patterns that silently redirect edits to `/dev/null` or otherwise discard agent work without review.

Prefer:

- deny with an explicit reason
- ask for confirmation
- rewrite to a safer but still visible command

Silent discard is only acceptable when project policy makes it explicit and the operator can still see what happened.

---

## 8. Sensitive File Policy

Guard common secret-bearing files:

- `.env`
- `.env.*`
- `*.pem`
- `*.key`
- SSH private keys
- credential dumps or exported tokens
- `.aws/`, `.ssh/`, `.npmrc`, `.pypirc`, `config/credentials.json`

Good pattern:

- block accidental staging
- warn on edits when appropriate
- keep audit messages redacted

Do not print the full secret-bearing path plus payload contents in logs.

### Three leak paths (not just direct read)

Hook authors often guard only the obvious path. There are three:

1. **Direct file read.** The agent opens `.env` and the contents enter the conversation. Easiest to block.
2. **Runtime stdout capture.** The agent runs tests or starts the app; a failed HTTP call logs `Authorization: Bearer …`, a DB timeout dumps the connection string. The agent never opened `.env` but secrets still leak through captured command output.
3. **Grep / search hits.** The agent greps for a function name; the search hits a config file containing credentials. Matched lines surface in tool output.

Coverage for paths 2 and 3 must be designed in, not assumed.

### Defense layers, ordered

Layer the controls — do not rely on any single one:

1. **`permissions.deny` glob rules** in `~/.claude/settings.json` (system-level enforcement, applied before the model sees the file).
   - Globs: `Read(**/.env*)`, `Read(**/*.pem)`, `Read(**/*.key)`, `Read(**/secrets/**)`, `Read(**/credentials/**)`, `Read(**/.aws/**)`, `Read(**/.ssh/**)`, `Read(**/.npmrc)`, `Read(**/.pypirc)`. Mirror with `Write(**/.env*)` etc.
   - Owns: design model in [`../../ai-coding-agents-settings-policy/SKILL.md`](../../ai-coding-agents-settings-policy/SKILL.md); operator workflow in the `update-config` skill.
2. **PreToolUse hooks** (this skill) — defense in depth for paths 2 and 3 the deny rules cannot reach: command rewrites that strip `.env` from `git add`, redaction in audit logs, blocking grep/search outputs that contain secret prefixes.
3. **Project memory rules** in `CLAUDE.md` / `AGENTS.md` — advisory only; treat as a hint, never as enforcement.

Rule of thumb: anything load-bearing must be in layer 1 or 2. CLAUDE.md is for guidance the model should follow, not for protecting secrets.

### Runtime leak mitigation: `.env.test` with dummies

Deny rules block direct file reads but cannot prevent your test runner from logging real secrets. Point test frameworks at `.env.test` populated with dummy values (`AKIAIOSFODNN7EXAMPLE`, `sk_test_...`, `sk-test-dummy-...`). When the agent captures stdout from a failing test, only dummies surface.

This is the operational complement to deny rules — both are needed.

### Container isolation (nuclear option)

For client work with production credentials, mount `/dev/null` over `.env` so the file is unreadable from inside the container:

```bash
docker run -v /dev/null:/app/.env:ro your-dev-container
```

Reserved for high-stakes credential exposure; overkill for personal projects where deny rules + `.env.test` + gitleaks already give layered protection.

### Pre-commit secret scan

Hook-level redaction protects the conversation but not the repo. Pair with a pre-commit secret scan — see [`../../dev-git-workflow/references/git-hooks-automation.md`](../../dev-git-workflow/references/git-hooks-automation.md) for the gitleaks recipe (preferred over hand-rolled regex pre-commit hooks: gitleaks is maintained, has a curated rule set, and exits non-zero on common token prefixes — `sk-ant-`, `sk_live_`, `ghp_`, `AKIA`, `xox[bpors]-`, `SG.`, JWTs, `BEGIN PRIVATE KEY`).

---

## 9. Synchronous Performance Budget

Slow synchronous hooks are both a UX and security problem:

- operators bypass them
- timeouts hide failures
- teams stop trusting policy

Policy:

- keep synchronous hooks under ~1 second where possible
- move heavy checks to background execution or completion hooks
- keep failures explicit and actionable

---

## 10. Validation Workflow

Before rollout:

1. Run `shellcheck` on every non-trivial bash hook.
2. Test with captured sample payloads.
3. Verify event-specific JSON against the current official docs.
4. Exercise deny/ask paths manually.
5. Confirm logs and notifications redact secrets.

---

## Navigation

- [SKILL.md](../SKILL.md) - Main reference
- [hook-templates.md](hook-templates.md) - Copy-paste templates
- [hook-patterns.md](hook-patterns.md) - Lifecycle and architecture patterns
