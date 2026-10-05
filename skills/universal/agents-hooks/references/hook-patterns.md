# Hook Patterns

Current patterns for Claude Code hooks, with a narrow Codex notification addendum.

Assumptions:

- Claude has a broad lifecycle hook surface and multiple hook modalities.
- Codex documents both `notify` callbacks with notification policy and a separate `hooks.json` lifecycle-hooks system; [`hook-templates.md`](hook-templates.md) §Codex owns the Codex hook facts as lookup steps.

---
## Table of Contents

- [1. Async Verification Instead Of Heavy Stop Hooks](#1-async-verification-instead-of-heavy-stop-hooks)
- [2. HTTP Audit Hook](#2-http-audit-hook)
- [3. Agent-Based Verification Hook](#3-agent-based-verification-hook)
- [4. ConfigChange Audit](#4-configchange-audit)
- [5. PreCompact Reinjection](#5-precompact-reinjection)
- [6. Session Orientation And Persistence](#6-session-orientation-and-persistence)
- [7. Worktree Lifecycle Hooks](#7-worktree-lifecycle-hooks)
- [8. Permission Policy Pattern](#8-permission-policy-pattern)
- [9. Managed Hooks And Skill-Scoped Hooks](#9-managed-hooks-and-skill-scoped-hooks)
- [10. MCP Tool Hook Hygiene](#10-mcp-tool-hook-hygiene)
- [11. Blanket Staging Guard](#11-blanket-staging-guard)
- [12. Codex Notification Pattern](#12-codex-notification-pattern)
- [13. CI / Headless Usage](#13-ci-headless-usage)
- [14. On-Demand Hooks (Skill-Registered)](#14-on-demand-hooks-skill-registered)
- [15. Skill Usage Measurement Hook](#15-skill-usage-measurement-hook)
- [Navigation](#navigation)


## 1. Async Verification Instead Of Heavy Stop Hooks

Heavy synchronous `Stop` hooks create latency and brittle flows. Prefer:

- fast synchronous checks in `PostToolUse`
- background lint/test runs for expensive verification
- completion or notification hooks for reporting

Pattern:

```text
Edit/Write -> fast formatter or smoke check (PostToolUse)
PostToolUseFailure -> log or alert on tool failure separately
PostToolBatch -> gate the next model call after a parallel tool batch
TaskCompleted -> summarize async verification result
Notification -> send external alert if verification failed
```

Use `Stop` as a gate only when you genuinely need to block completion. Prefer `PostToolBatch` over `Stop` when the goal is to check results after a parallel tool burst before allowing Claude to continue.

---

## 2. HTTP Audit Hook

Use an HTTP hook when audit events must leave the local machine immediately.

Good fit:

- security audit trail
- SIEM / webhook ingestion
- org-wide policy enforcement

Avoid this for:

- local formatting
- shell-centric repo maintenance
- high-volume low-value edit noise

Keep payloads minimal and redact secrets before transmission.

---

## 3. Agent-Based Verification Hook

Use an agent hook when the check is semantic rather than syntactic.

Examples:

- stop only if acceptance criteria are satisfied
- review a subagent's output for missing deliverables
- inspect config changes for policy drift

Use command hooks for deterministic checks first. Escalate to agent hooks only when shell logic becomes brittle or unreadable.

---

## 4. ConfigChange Audit

`ConfigChange` is the right place to detect mutations to hook policy, approvals, or other agent-control settings.

What to log:

- which config file changed
- whether hook definitions changed
- whether approval or sandbox policy changed
- whether managed hook policy was enabled or disabled

This is higher value than burying hook-policy changes inside generic git or stop hooks.

---

## 5. PreCompact Reinjection

Use `PreCompact` to preserve only the minimum critical context Claude must keep after compaction.

Good payload:

- current branch / worktree
- active ticket or task id
- unresolved blocker
- next concrete step

Bad payload:

- full diffs
- verbose summaries
- tool logs
- stale reasoning history

Treat `PreCompact` as state checkpointing, not documentation.

---

## 6. Session Orientation And Persistence

Use hooks to support a simple orient -> work -> persist cycle.

Good pattern:

- `SessionStart`: print or load current branch, active task id, durable memory pointers, and the one or two commands the repo expects most often
- `PreCompact`: checkpoint only the minimum current-state summary
- `TaskCompleted` or `SessionEnd`: persist confirmed decisions, durable fixes, and workflow corrections into the right memory surface

Bad pattern:

- dumping raw logs into durable memory
- persisting every transient observation
- using hooks to create hidden background state nobody reviews

Persist compressed facts, not transcripts.

---

## 7. Worktree Lifecycle Hooks

Use `WorktreeCreate` and `WorktreeRemove` when automation is tied to per-worktree state.

Examples:

- create temp cache directories or per-worktree env files
- initialize local tool indexes
- tear down transient directories and pid files

Keep the cleanup symmetric. Anything created on `WorktreeCreate` should have a removal path on `WorktreeRemove`.

---

## 8. Permission Policy Pattern

Use `PreToolUse` and `PermissionRequest` together:

- `PreToolUse` for deterministic deny/ask/rewrite rules
- `PermissionRequest` for approval policy and escalation handling

This reduces approval fatigue without widening the attack surface.

Do not use broad shell allowlists when a narrower prefix or exact command family is enough.

---

## 9. Managed Hooks And Skill-Scoped Hooks

Prefer the narrowest scope that matches the policy:

- repo-wide hooks for baseline security and hygiene
- skill-scoped hooks when policy belongs to a specific workflow
- managed hooks when organization policy must be centralized

This keeps local skill behavior portable while preventing unrelated repos from inheriting broad automation.

---

## 10. MCP Tool Hook Hygiene

If hook logic applies to MCP usage, document it explicitly.

Good examples:

- sanitize MCP tool output before passing it downstream
- audit MCP calls that touch sensitive systems
- attach lightweight policy to a specific MCP tool family

Do not assume MCP tools behave like Bash or Edit events. Keep event logic tool-aware.

---

## 11. Blanket Staging Guard

In agent-heavy repos, blanket staging is often riskier than it looks.

Good fit for a `PreToolUse` policy:

- ask or deny on `git add .`
- ask or deny on `git add -A`
- allow explicit file staging such as `git add path/to/file`

This keeps staging scoped to the files the agent actually intended to modify and reduces accidental inclusion of unrelated local changes.

---

## 12. Codex Notification Pattern

Use Codex `notify` for:

- desktop alerts
- audit logging
- handing `agent-turn-complete` to another local process

Do not use the `notify` callback as documentation cover for:

- command blocking
- permission rewriting
- per-tool lifecycle interception
- stdin JSON schemas copied from Claude hooks

For those behaviors on Codex, use the Codex `hooks.json` lifecycle system (`PreToolUse` deny, `Stop`/`SubagentStop` block) — see [`hook-templates.md` §"Codex: `hooks.json` Lifecycle Hooks"](hook-templates.md#codex-hooksjson-lifecycle-hooks) — but treat it as verify-first (run the lookup steps in that section; firing gaps have been reported) and keep `notify` for anything that must be dependable. Do not assume the `notify` payload itself supports blocking.

---

## 13. CI / Headless Usage

Claude hooks are useful in headless and CI workflows when you want deterministic policy around the agent itself.

Good fits:

- repo bootstrap checks in `Setup`
- config audits in `ConfigChange`
- semantic completion checks via agent hooks

Keep CI hook output concise and machine-consumable where possible.

---

## 14. On-Demand Hooks (Skill-Registered)

Claude Code has a documented mechanism for this, not just a convention: hooks can be declared directly in a skill's or subagent's frontmatter. The two scopes differ (per [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks), "Hooks in skills and agents"):

- **Skill hooks** register when the skill is invoked and keep running for the rest of the session, including turns after the skill's own turn. They do not switch off when the skill "finishes".
- **Subagent hooks** run only while that subagent is running and are removed when it completes; a `Stop` hook there becomes `SubagentStop`.
- `"once": true` removes a handler after its first successful run (a failing, blocking, or timed-out run leaves it in place). It is honored only in skill frontmatter and ignored in settings files and agent frontmatter.

Pattern:

- Declare the hook in the skill/agent's own frontmatter rather than in `settings.json`
- In a skill, set `"once": true` for a run-then-remove handler; omit it only if the hook should keep firing for the rest of the session
- Useful for verification workflows that only apply to specific skill domains

Example scenario:

- A "database migration" skill activates
- It registers a `PostToolUse` hook that runs `pg_dump --schema-only` after any `Bash` call containing `migrate`
- Without `once`, that hook keeps firing after the migration work is done; scope the matcher tightly or set `once`

Constraints:

- On-demand hooks should be lightweight; remember a skill hook is session-scoped, not turn-scoped
- Do not use on-demand hooks for security policy (those belong in static config, not a scope that depends on which skill was invoked)
- Document the hook in the skill's SKILL.md so users understand what automation is added

---

## 15. Skill Usage Measurement Hook

Log which skills are invoked across sessions to spot undertriggering, overtriggering, or abandoned skills. Skills are invoked two ways, and each needs its own event: Claude calls the `Skill` tool (a `PreToolUse` hook with matcher `Skill`), and the user types `/skillname` (a `UserPromptExpansion` hook, which is the only event that sees that path). Matching `Read` of `SKILL.md` undercounts: an invoked skill's body is loaded by the runtime, not read with the `Read` tool. Register the same script on both events:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT="$(cat)"
EVENT="$(printf '%s' "$INPUT" | jq -r '.hook_event_name // empty')"
case "$EVENT" in
  PreToolUse)
    [[ "$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')" != "Skill" ]] && exit 0
    SKILL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_input.skill // empty')"
    ;;
  UserPromptExpansion)
    [[ "$(printf '%s' "$INPUT" | jq -r '.expansion_type // empty')" != "slash_command" ]] && exit 0
    SKILL_NAME="$(printf '%s' "$INPUT" | jq -r '.command_name // empty')"
    ;;
  *) exit 0 ;;
esac
[[ -z "$SKILL_NAME" ]] && exit 0
printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SKILL_NAME" "$EVENT" \
  >> "${CLAUDE_PLUGIN_DATA:-/tmp}/skill-usage.log"
exit 0
```

Analysis queries on the resulting TSV (column 1 is an ISO-8601 UTC timestamp, so string comparison works as a date filter):

```bash
# Most activated skills (last 30 days)
SINCE="$(date -u -v-30d +%Y-%m-%d 2>/dev/null || date -u -d '30 days ago' +%Y-%m-%d)"
awk -F'\t' -v since="$SINCE" '$1 >= since {print $2}' skill-usage.log | sort | uniq -c | sort -rn | head -20

# Skills never activated (compare against skill directory listing)
comm -23 <(ls skills/ | sort) <(awk -F'\t' '{print $2}' skill-usage.log | sort -u)
```

Good fit:

- teams with 20+ skills wanting to prune unused ones
- measuring ROI of new skills
- identifying overtriggering patterns (skill fires on unrelated queries)

---

## Navigation

- [SKILL.md](../SKILL.md) - Main overview
- [hook-templates.md](hook-templates.md) - Copy-paste command hook and Codex notify templates
- [hook-security.md](hook-security.md) - Hardening patterns and anti-patterns
