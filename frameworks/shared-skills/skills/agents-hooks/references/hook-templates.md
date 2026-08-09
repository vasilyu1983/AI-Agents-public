# Hook and Notification Templates

Ready-to-use templates for current Claude command hooks and Codex notification callbacks.

Assumptions:

- Claude command hooks receive JSON via stdin.
- Claude hooks run with full user permissions; validate all input.
- Codex `notify` is a narrower external-program callback, not a full Claude-style lifecycle hook system.

---
## Table of Contents

- [Claude: PreToolUse Validation](#claude-pretooluse-validation)
- [Claude: PostToolUse Fast Formatter](#claude-posttooluse-fast-formatter)
- [Claude: PostToolUse Smoke Check Script](#claude-posttooluse-smoke-check-script)
- [Claude: Strip Sensitive Files From `git add`](#claude-strip-sensitive-files-from-git-add)
- [Claude: Runtime Preflight](#claude-runtime-preflight)
- [Claude: PreCompact Checkpoint + SessionStart Restore](#claude-precompact-checkpoint--sessionstart-restore)
- [Claude: PostToolBatch Test Gate](#claude-posttoolbatch-test-gate)
- [Claude: ConfigChange Audit + Policy Guard](#claude-configchange-audit--policy-guard)
- [Claude: SubagentStart Context + SubagentStop Validation](#claude-subagentstart-context--subagentstop-validation)
- [Claude: WorktreeCreate Setup + WorktreeRemove Teardown](#claude-worktreecreate-setup--worktreeremove-teardown)
- [Codex: `notify` Callback Script](#codex-notify-callback-script)
- [Codex: `hooks.json` Lifecycle Hooks](#codex-hooksjson-lifecycle-hooks)
- [Wiring: register the backfilled hooks](#wiring-register-the-backfilled-hooks)
- [Notes](#notes)
- [Navigation](#navigation)


## Claude: PreToolUse Validation

Guard the Bash tool against destructive commands and possible credential exposure.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[[ "$TOOL_NAME" != "Bash" ]] && exit 0

if printf '%s' "$CMD" | grep -qE '(^|[[:space:]])rm[[:space:]]+-rf[[:space:]]+/($|[[:space:]])'; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked destructive rm -rf / command."
    }
  }'
  exit 0
fi

if printf '%s' "$CMD" | grep -qE 'git[[:space:]]+push.*--force.*(main|master)'; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Force-push to main/master is blocked by policy."
    }
  }'
  exit 0
fi

if printf '%s' "$CMD" | grep -qiE '(password|secret|api[_-]?key|token)[[:space:]]*='; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "Possible secret detected in command.",
      additionalContext: "Review the command carefully before approving."
    }
  }'
  exit 0
fi

exit 0
```

The `rm -rf` check above only matches root deletion (`rm -rf /`) — it is deliberately narrow and needs no allowlist. A broader guard that also blocks `rm -rf` against arbitrary paths (or `DROP TABLE`, `git reset --hard`, `docker system prune`, etc.) is a common extension of this template, and that broader guard needs a safe-exceptions allowlist or it becomes unusable: it either blocks routine cleanup of build/cache directories (so people disable the hook entirely, which guards nothing) or gets scoped so loosely it stops catching real mistakes.

If you extend the `rm -rf` check to arbitrary paths, add an allowlist short-circuit before the deny, using the same `CMD` variable already extracted above:

```bash
# Starting allowlist for a broadened rm -rf guard — extend per project.
# These are build/cache artifacts that are always safe to nuke and regenerate;
# a different repo might reasonably add .venv, target/, or vendor/.
SAFE_RM_PATHS='node_modules|\.next|dist|__pycache__|\.cache|build|\.turbo|coverage'

if printf '%s' "$CMD" | grep -qE '(^|[[:space:]])rm[[:space:]]+-rf[[:space:]]'; then
  if ! printf '%s' "$CMD" | grep -qE "${SAFE_RM_PATHS}"; then
    jq -cn '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Blocked destructive rm -rf command outside the safe-exceptions allowlist."
      }
    }'
    exit 0
  fi
fi
```

This list is project-specific, not exhaustive — treat it as a starting point to extend, not a fixed spec. (Source: `garrytan/gstack@94993f74012782fd94416dd44b8314f6363a13a4`, `careful/SKILL.md`, MIT, 2026-08-09.)

---

## Claude: PostToolUse Fast Formatter

Keep synchronous post-edit hooks cheap. Format only the touched file and tolerate missing formatters.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"

[[ ! "$TOOL_NAME" =~ ^(Edit|Write)$ ]] && exit 0
[[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]] && exit 0

case "$FILE_PATH" in
  *.js|*.jsx|*.ts|*.tsx|*.json|*.md)
    command -v prettier >/dev/null 2>&1 && prettier --write "$FILE_PATH" >/dev/null 2>&1 || true
    ;;
  *.py)
    command -v ruff >/dev/null 2>&1 && ruff format "$FILE_PATH" >/dev/null 2>&1 || true
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && gofmt -w "$FILE_PATH" >/dev/null 2>&1 || true
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && rustfmt "$FILE_PATH" >/dev/null 2>&1 || true
    ;;
esac

exit 0
```

---

## Claude: PostToolUse Smoke Check Script

Use the script below with a background `PostToolUse` or `TaskCompleted` hook. Do not make expensive checks synchronous unless you need a hard gate.

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR"

if [[ -f package.json ]]; then
  npm run lint -- --max-warnings=0 >/tmp/claude-hook-smoke.log 2>&1 || true
elif [[ -f pyproject.toml ]]; then
  pytest -q >/tmp/claude-hook-smoke.log 2>&1 || true
fi

exit 0
```

---

## Claude: Strip Sensitive Files From `git add`

Rewrite staging commands to exclude `.env`-style files rather than silently discarding unrelated writes.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[[ "$TOOL_NAME" != "Bash" ]] && exit 0
[[ ! "$CMD" =~ ^git[[:space:]]+add ]] && exit 0

SAFE_CMD="$(printf '%s' "$CMD" | sed -E 's/[[:space:]]+\.env[^[:space:]]*//g')"

if [[ "$SAFE_CMD" != "$CMD" ]]; then
  jq -cn --arg cmd "$SAFE_CMD" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow",
      permissionDecisionReason: "Removed .env-style files from git add command.",
      updatedInput: { command: $cmd }
    }
  }'
  exit 0
fi

exit 0
```

---

## Claude: Runtime Preflight

Use this for `SessionStart` or `Setup` to fail fast on missing prerequisites.

```bash
#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "$1" >&2
  exit 2
}

command -v node >/dev/null 2>&1 || fail "Runtime preflight failed: node not found. Install Node >= 22.22.0"
command -v jq >/dev/null 2>&1 || fail "Runtime preflight failed: jq not found. Install jq before using hooks."

NODE_VERSION_RAW="$(node -v | sed 's/^v//')"
NODE_MAJOR="${NODE_VERSION_RAW%%.*}"
NODE_MINOR="$(printf '%s' "$NODE_VERSION_RAW" | cut -d. -f2)"

if [[ "$NODE_MAJOR" -lt 22 ]] || { [[ "$NODE_MAJOR" -eq 22 ]] && [[ "$NODE_MINOR" -lt 22 ]]; }; then
  fail "Runtime preflight failed: node v${NODE_VERSION_RAW} detected, requires >= ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0. Run: nvm install ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0 && nvm use ${MIN_NODE_MAJOR}.${MIN_NODE_MINOR}.0"
fi

echo "Runtime preflight ok: node v${NODE_VERSION_RAW}, jq installed"
exit 0
```

---

## Claude: PreCompact Checkpoint + SessionStart Restore

Survive context compaction. `PreCompact` stdout is **not** injected back to the model, so reinjection is a pair: `PreCompact` checkpoints minimal state to disk; `SessionStart` reads it back via `additionalContext` (which *is* injected).

`PreCompact` writer:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
STATE_DIR="$ROOT/.claude/state"
mkdir -p "$STATE_DIR"

BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
{
  echo "branch: $BRANCH"
  echo "checkpoint_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  # Append the few facts the next turn must keep: active task id, blocker, next step.
} > "$STATE_DIR/precompact-checkpoint.txt"

exit 0
```

`SessionStart` restore:

```bash
#!/usr/bin/env bash
set -euo pipefail

CHECKPOINT="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/state/precompact-checkpoint.txt"
[[ -f "$CHECKPOINT" ]] || exit 0

CONTEXT="$(cat "$CHECKPOINT")"
jq -cn --arg ctx "$CONTEXT" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("Restored pre-compaction checkpoint:\n" + $ctx)
  }
}'
exit 0
```

Keep the checkpoint to a handful of lines — it is state, not documentation.

---

## Claude: PostToolBatch Test Gate

After a parallel tool burst, stop the agentic loop before the next model call if a test/build command in the batch shows failure. `PostToolBatch` receives all results in `tool_calls[]` and blocks with `decision: "block"`.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"

FAILED="$(printf '%s' "$INPUT" | jq -r '
  [ .tool_calls[]?
    | select(.tool_name == "Bash")
    | select((.tool_input.command // "")
        | test("(npm|pnpm|yarn) (test|run build)|pytest|go test|cargo test"))
    | select((.tool_output // "")
        | test("(FAIL|failed|Error:|panic:|Traceback)"))
  ] | length')"

if [[ "${FAILED:-0}" -gt 0 ]]; then
  jq -cn '{
    decision: "block",
    reason: "A test or build command in the parallel batch reported failure. Fix it before continuing."
  }'
  exit 0
fi
exit 0
```

`tool_output` matching is heuristic. For a hard gate, have the command emit a sentinel (e.g. `echo HOOK_TESTS_OK`) and match that instead of failure strings.

---

## Claude: ConfigChange Audit + Policy Guard

Audit every config mutation and optionally block agent-initiated edits to sensitive scopes. `ConfigChange` carries `config_source` and `config_path`; it can block all sources except `policy_settings`.

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
SRC="$(printf '%s' "$INPUT" | jq -r '.config_source // empty')"
CFG_PATH="$(printf '%s' "$INPUT" | jq -r '.config_path // empty')"

AUDIT="${CLAUDE_PROJECT_DIR:-/tmp}/.claude/config-audit.log"
mkdir -p "$(dirname "$AUDIT")"
printf '%s\tsource=%s\tpath=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${SRC:-?}" "${CFG_PATH:-?}" >> "$AUDIT"

# Require human review for hook/permission policy edits made mid-session.
if [[ "$SRC" == "local_settings" ]]; then
  jq -cn '{
    decision: "block",
    reason: "Local settings change requires human review (logged to .claude/config-audit.log)."
  }'
  exit 0
fi
exit 0
```

`policy_settings` cannot be blocked by a user hook — only audited.

---

## Claude: SubagentStart Context + SubagentStop Validation

Inject guardrails into every spawned subagent, then gate its handoff. `SubagentStart` injects `additionalContext` / `systemMessage` into the subagent (not the parent); `SubagentStop` blocks the subagent from finishing with `decision: "block"`.

`SubagentStart` context injection:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
AGENT_TYPE="$(printf '%s' "$INPUT" | jq -r '.agent_type // "unknown"')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

jq -cn --arg at "$AGENT_TYPE" --arg br "$BRANCH" '{
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: ("Working branch: " + $br + ". Stay within assigned files; do not edit shared config or commit."),
    systemMessage: ("Spawned as " + $at + " — return findings only.")
  }
}'
exit 0
```

`SubagentStop` validation:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TRANSCRIPT="$(printf '%s' "$INPUT" | jq -r '.transcript_path // empty')"

if [[ -n "$TRANSCRIPT" && -f "$TRANSCRIPT" ]]; then
  TAIL="$(tail -c 4000 "$TRANSCRIPT" 2>/dev/null || true)"
  if ! printf '%s' "$TAIL" | grep -qiE 'summary|result|findings|conclusion'; then
    jq -cn '{
      decision: "block",
      reason: "No summary/result detected — produce a concise findings summary before finishing."
    }'
    exit 0
  fi
fi
exit 0
```

Transcript inspection is heuristic; prefer a structured sentinel if the subagent contract allows it.

---

## Claude: WorktreeCreate Setup + WorktreeRemove Teardown

Per-worktree setup and symmetric teardown. **Registering `WorktreeCreate` means your hook owns creation** — it must run `git worktree add` and print the resulting path to stdout, or creation fails. Omit this hook entirely to keep Claude's default git behavior; add it only when you need custom placement or per-worktree setup.

`WorktreeCreate`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
ISO_ID="$(printf '%s' "$INPUT" | jq -r '.isolation_id // empty')"

ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
WT_BASE="$ROOT/.worktrees"
mkdir -p "$WT_BASE"
WT_PATH="$WT_BASE/${ISO_ID:-wt-$(date +%s)}"
BRANCH="agent/${ISO_ID:-tmp}"

git -C "$ROOT" worktree add -b "$BRANCH" "$WT_PATH" >/dev/null 2>&1 \
  || git -C "$ROOT" worktree add "$WT_PATH" >/dev/null 2>&1

# Per-worktree setup
mkdir -p "$WT_PATH/.cache"
[[ -f "$ROOT/.env.example" ]] && cp "$ROOT/.env.example" "$WT_PATH/.env" 2>/dev/null || true

# REQUIRED: print the worktree path so Claude uses it.
printf '%s\n' "$WT_PATH"
exit 0
```

`WorktreeRemove` (cannot block; failures logged in debug only):

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
WT_PATH="$(printf '%s' "$INPUT" | jq -r '.worktree_path // empty')"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
[[ -z "$WT_PATH" ]] && exit 0

# Symmetric teardown of anything WorktreeCreate made.
rm -rf "${WT_PATH:?}/.cache" 2>/dev/null || true
git -C "$ROOT" worktree remove --force "$WT_PATH" >/dev/null 2>&1 || true
exit 0
```

The `${WT_PATH:?}` guard aborts the `rm` if the path is somehow empty — never `rm -rf` an unset variable.

---

## Codex: `notify` Callback Script

Use the official `notify.program` config to run a local script when Codex emits supported notification events.

Configuration:

```toml
[notify]
program = ["python3", "/absolute/path/to/codex_notify.py"]
```

Script:

```python
#!/usr/bin/env python3
import json
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        return 1

    payload = json.loads(sys.argv[1])
    title = "Codex"
    message = payload.get("title") or payload.get("event", "Notification")
    message = str(message).replace('"', "'")

    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"',
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Keep the callback idempotent and event-driven. Do not assume Claude-style permission or tool lifecycle data is available.

---

## Codex: `hooks.json` Lifecycle Hooks

Codex has a lifecycle hooks system distinct from `notify`. Config lives in `~/.codex/hooks.json` or an inline `[hooks]` table in `~/.codex/config.toml` (repo-local `.codex/` paths and plugin-bundled `hooks/hooks.json` also load and merge). Events: `SessionStart`, `SubagentStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop`. Only `type: "command"` handlers execute — `async`, `prompt`, and `agent` are parsed but ignored.

**Verify-first.** Official docs don't apply a GA/experimental label, but they do confirm partial implementation: only `type: "command"` handlers execute today (`prompt`/`agent` are parsed but skipped), and `async` is parsed but not yet functional. Windows is supported via a `commandWindows` override (an earlier "no Windows" caveat is stale as of mid-2026). Despite that, there are documented firing-reliability bugs still open as of mid-2026 ([codex#21639](https://github.com/openai/codex/issues/21639) — hooks stop firing after a Codex Desktop update; [codex#17532](https://github.com/openai/codex/issues/17532) — repo-local `.codex/config.toml` hooks don't fire in interactive sessions). Confirm the hook actually fires on your runtime before relying on it, and prefer `notify` for anything that must be dependable.

Registration (`~/.codex/hooks.json`) — same three-level shape as Claude (event → matcher group → handlers):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.codex/hooks/pre_tool_use_guard.sh",
            "statusMessage": "Checking Bash command",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "bash ~/.codex/hooks/stop_gate.sh" }
        ]
      }
    ]
  }
}
```

`PreToolUse` deny guard (`~/.codex/hooks/pre_tool_use_guard.sh`) — the stdin payload matches Claude's (`tool_name`, `tool_input.command`):

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[[ "$TOOL_NAME" != "Bash" ]] && exit 0

if printf '%s' "$CMD" | grep -qE '(^|[[:space:]])rm[[:space:]]+-rf[[:space:]]+/($|[[:space:]])'; then
  jq -cn '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked destructive rm -rf / command."
    }
  }'
  exit 0
fi
exit 0
```

`Stop` gate (`~/.codex/hooks/stop_gate.sh`) — `decision: "block"` does not reject; it makes Codex continue, using `reason` as the next prompt:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"

# Illustrative gate. For a real one use a cached/async test result, not a full
# suite on every Stop — a synchronous suite here violates the fast-hook rule.
if [[ -f "$ROOT/.codex/state/tests-red" ]]; then
  jq -cn '{decision:"block", reason:"Tests are marked failing — fix them before ending the turn."}'
  exit 0
fi
exit 0
```

Notes:

- Shared stdin fields: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `model`, `permission_mode`. Turn-scoped events add `turn_id`; `PreToolUse` adds `tool_name`, `tool_use_id`, `tool_input`.
- Exit-code equivalents: for `PreToolUse`, exit `2` + stderr ≡ deny; for `Stop`/`SubagentStop`, exit `2` + stderr ≡ `decision: block`.
- Codex has **no** `PostToolBatch`, `WorktreeCreate/Remove`, `ConfigChange`, `MessageDisplay`, `TeammateIdle`, or `Elicitation` events — do not port those Claude templates over.
- `timeout` defaults to 600s; set a tighter value for synchronous guards. Toggle the whole system with `[features] hooks = false` in `config.toml`.

---

## Wiring: register the backfilled hooks

Drop the scripts in `~/.claude/hooks/` (or `.claude/hooks/`), `chmod +x` them, then register in `settings.json`. Events without a matcher (`PostToolBatch`, `PreCompact`, `SessionStart`, `WorktreeCreate`/`WorktreeRemove`) use `"matcher": ""`.

```json
{
  "hooks": {
    "PreCompact":     [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/precompact-checkpoint.sh" }] }],
    "SessionStart":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/sessionstart-restore.sh" }] }],
    "PostToolBatch":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/posttoolbatch-gate.sh" }] }],
    "ConfigChange":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/configchange-audit.sh" }] }],
    "SubagentStart":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/subagent-context.sh" }] }],
    "SubagentStop":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/subagent-validate.sh" }] }],
    "WorktreeCreate": [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/worktree-create.sh" }] }],
    "WorktreeRemove": [{ "matcher": "", "hooks": [{ "type": "command", "command": "bash ~/.claude/hooks/worktree-remove.sh" }] }]
  }
}
```

Dry-run each before trusting it, using the input fields the event actually sends:

```bash
echo '{"tool_calls":[{"tool_name":"Bash","tool_input":{"command":"pytest"},"tool_output":"FAILED"}]}' \
  | bash ~/.claude/hooks/posttoolbatch-gate.sh   # expect a {"decision":"block"} JSON line
echo '{"config_source":"local_settings","config_path":"/x/.claude/settings.json"}' \
  | bash ~/.claude/hooks/configchange-audit.sh    # expect a block + an audit-log line
```

## Notes

- For Claude HTTP, prompt, or agent hooks, keep the wiring in `settings.local.json` and let the hook type do the heavy lifting. Those are config-native patterns, not shell-script templates.
- Prefer `ConfigChange`, `PreCompact`, `WorktreeCreate`, and `WorktreeRemove` for repo lifecycle concerns instead of overloading `Stop`.
- Run ShellCheck on non-trivial bash hooks before rollout.

---

## Navigation

- [SKILL.md](../SKILL.md) - Main reference
- [hook-patterns.md](hook-patterns.md) - Async, HTTP, compaction, and worktree patterns
- [hook-security.md](hook-security.md) - Shell hardening and event-safety guidance
