---
name: ai-coding-agents-sessions
description: "Designs session lifecycle for coding-agent runtimes. Use when implementing resume, transcript restoration, checkpoint rewind, cross-worktree recovery, or session-state persistence."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Sessions

Use this skill to design or review the session lifecycle for a coding-agent runtime: session IDs, transcript persistence, resume pickers, stale-cache clearing, cross-worktree recovery, and what state must be restored versus recomputed.

This skill owns runtime session lifecycle. For persistent repo instructions and always-loaded memory, use [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md).

## ASCII Flow

```text
new or resumed invocation
  |
  v
session identity
  project + worktree + session_id + title + runtime mode
  |
  v
state restoration
  transcript + summaries + tool state + task state + provider cache metadata
  |
  v
branch decision
  continue | rewind | compact | clear | fork subagent | exact resume | claude agents (background resume)
  |
  v
active turn
  append events, persist checkpoints, keep recovery path auditable
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What belongs in a coding-agent session model? | [`references/session-lifecycle-and-resume.md`](references/session-lifecycle-and-resume.md) | Session IDs, picker flows, stale-cache reset, and resume semantics |
| How should transcripts recover across worktrees and summaries? | [`references/transcript-restoration-and-cross-worktree-recovery.md`](references/transcript-restoration-and-cross-worktree-recovery.md) | Restoration boundaries, search, cross-project safeguards, and replay rules |
| How do users decide between continue / rewind / clear / compact / subagent at each turn? | [`references/context-lifecycle-and-branching.md`](references/context-lifecycle-and-branching.md) | 1M-context branching model, context rot zone, rewind > correction, compact-vs-clear, bad-compact causes, subagent mental test |
| How do forked subagents change session lifecycle (cache, isolation, resume, cost)? | [`references/context-forking.md`](references/context-forking.md) | Blank-vs-forked startup, `CLAUDE_CODE_FORK_SUBAGENT=1` and `/fork` surfaces, cache-prefix economics, fork-as-exception rule |
| Which resume path should I use (session ID / picker / ACP re-attach / recipe re-seed)? | [`references/resume-path-decision-tree.md`](references/resume-path-decision-tree.md) | Decision tree, path comparison table, prompt-cache economics in subagent spawning |
| How does OpenAI Codex split Session / Task / Turn protocol state? | [`references/openai-codex-session-task-turn-protocol.md`](references/openai-codex-session-task-turn-protocol.md) | SQ/EQ protocol, response bookmarks, one-active-task invariant, and interruption rules |
| How does Codex persist, resume, fork, and cloud-resume sessions? | [`references/openai-codex-session-persistence.md`](references/openai-codex-session-persistence.md) | SQLite-backed session index, `codex resume` UUID lookup, `codex fork` branch semantics, `codex cloud` task-apply |

## When To Use

- Design resume and continue flows for a coding-agent CLI
- Decide how session IDs, titles, or logs map to recovery behavior
- Restore transcripts, summaries, or worktree-bound state safely
- Build interactive resume pickers or exact-match resume commands
- Separate project memory from session memory and transcript state

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Persistent repo instructions and shared memory files | [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md) |
| Remote execution or bridge sessions | [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md) |
| Background task lifecycle | [`../ai-coding-agents-tasks/SKILL.md`](../ai-coding-agents-tasks/SKILL.md) |

## Default Workflow

1. **Define session identity first.** Use a stable session ID and keep title or search aliases as secondary lookup keys.
2. **Split restoreable from recomputable state.** Persist transcripts, summaries, and user-visible session identity; recompute caches and discovery indexes after resume.
3. **Clear stale discovery caches before restore.** Resume should not inherit old file, skill, or config caches.
4. **Support both exact and interactive recovery.** Resume should work by UUID, exact title match, and picker/search fallback.
5. **Treat worktree and project boundaries explicitly.** Same-repo worktrees can often resume directly or adopt the worktree; different projects should route through an explicit user command.
6. **Use fallback lookup order deliberately.** Enriched session indexes may fail; direct log or transcript lookup should exist as a second path before the runtime declares a session missing.
7. **Restore summary state, not just raw logs.** Transcript collapse, synthesized summaries, and lightweight cost or usage state should survive resume even if the visible REPL list is truncated.
8. **Test failure paths.** Verify missing sessions, multiple title matches, stale worktree paths, interrupted resume, index miss with direct-log fallback, and cross-project recovery.

## Host Rules

- Session lifecycle is runtime state, not project memory.
- Resume should restore only state that is safe to trust from storage.
- Search aliases and custom titles are convenience layers on top of session IDs.
- Cross-project resume must be explicit and reviewable.
- Same-repo worktree adoption and cross-project resume should follow different code paths.
- Resume should clear stale discovery caches before rebuilding live runtime state.
- If enriched indexes miss a session, the runtime should have a direct-log or transcript fallback before failing hard.
- Picker flows should exclude the current session and sidechain-only artifacts.

## Build Order

1. Define stable session identity and storage keys.
2. Separate durable session state from recomputable caches.
3. Implement exact-ID resume before title or picker-based recovery.
4. Add cache clearing and live-state rebuild on resume.
5. Add worktree-aware recovery rules.
6. Add transcript compaction, summary restore, and fallback lookup paths.

## Core Invariants

- Session identity must not depend on mutable titles.
- Resume must only trust persisted state that is safe to restore.
- Discovery caches are disposable and should be rebuilt.
- Same-repo worktree recovery and cross-project recovery are different problems.
- Missing enriched indexes must not be the only reason a session becomes unrecoverable.

## Failure Modes

- Resuming the wrong session because title lookup overrode session identity.
- Restoring stale discovery or config caches into a new runtime.
- Treating a moved worktree as a missing session instead of a relocation case.
- Losing summaries or collapsed transcript state even though raw logs exist.
- Declaring a session missing without checking direct log or transcript fallbacks.

## Minimal Viable Version

- Stable session IDs and exact resume by ID.
- Persisted transcripts and lightweight session metadata.
- Cache clear on resume.
- One picker or search fallback for humans.
- Direct-log or transcript fallback when secondary indexes fail.

## What Strong Implementations Add

- Worktree adoption and same-repo relocation handling.
- Progressive transcript loading for large sessions.
- Summary and usage-state restore alongside raw logs.
- Picker exclusions for current session and sidechain artifacts.
- Clear auditability around why a resume succeeded, failed, or switched paths.

## Background Agent Sessions

Claude Code supports background agents: daemon-supervised processes that run independently of the active terminal, persisting between invocations and resumable through the agent-view UI.

### How Background Sessions Work

| Aspect | Detail |
|--------|--------|
| Launch | `claude --bg "<task>"` from the shell, or `/bg <task>` / `/background <task>` from within a session (carries over in-flight shell commands, subagents, and workflows) |
| Isolation | Each background session moves into its own git worktree under project-relative `.claude/worktrees/` before editing, unless it's already in a worktree, isn't a git repo, or `worktree.bgIsolation` is set to `"none"` |
| Session state | Written to `~/.claude/jobs/<id>/state.json`; each job also gets a scratch dir at `~/.claude/jobs/<id>/tmp/` and a `CLAUDE_JOB_DIR` env var pointing at it |
| Roster | All active background sessions tracked in `~/.claude/daemon/roster.json`, used to reconnect after a supervisor restart |
| Daemon | A persistent on-demand supervisor process runs background sessions and restarts stopped ones (idle timeout ~1 hour) with conversation state intact |
| Resume/manage | `claude agents` opens the agent-view roster (no `/agents` slash command exists); `claude attach <id>`, `claude stop <id>`, `claude respawn <id>`, `claude rm <id>` operate on a specific job from the shell |
| CI usage | `claude agents --json` (add `--all` for completed sessions, `--cwd <path>` to scope) returns the roster as JSON with `id`, `state`, `status`, `waitingFor` fields; CI can poll this before collecting output |

### Storage Paths

```text
~/.claude/jobs/<id>/state.json       — per-job session state (transcript, tool state, task state)
~/.claude/jobs/<id>/tmp/             — per-job scratch directory (no permission prompts)
~/.claude/daemon/roster.json         — daemon-maintained roster of all known background jobs
~/.claude/daemon.log                 — supervisor process log
<project>/.claude/worktrees/         — isolated worktrees for background sessions (project-relative, not under the user's home config dir)
```

### Resume Path Decision

When a user returns to a background agent after leaving the terminal:

1. Run `claude agents` to open the roster (or `claude agents --cwd <path>` to scope to a directory) → select the row → attach with `Enter`/`→`, or peek with `Space` without attaching.
2. Direct attach without the roster UI: `claude attach <id>` (or `claude attach <name>` if the session was renamed).
3. If agent view is disabled (`disableAgentView: true` in settings, or `CLAUDE_CODE_DISABLE_AGENT_VIEW=1`): fall back to `claude --resume <id>` using the job ID from `roster.json`.
4. From CI: `claude agents --json | jq '.[] | select(.id == "<id>") | .status'` to poll job completion before collecting output.
5. If a session shows as failed after a machine shutdown, `claude attach <id>` restarts it in place; if the transcript was misread as empty on restart, Claude Code renames it with an `.orphaned-` suffix rather than discarding it (v2.1.196+).

### Lifecycle Settings

| Setting | Effect |
|---------|--------|
| `disableAgentView: true` (or `CLAUDE_CODE_DISABLE_AGENT_VIEW=1`) | Turns off `claude agents`, `--bg`, `/background`, and the on-demand supervisor entirely — not just the panel |
| `cleanupPeriodDays: <n>` | Governs local session/transcript retention generally (default 30 days, minimum 1); also bounds how long completed background jobs and their worktrees stick around |
| `awaySummaryEnabled: true` (default) | Shows a one-line recap of what happened while you were away (5+ minutes) when you return to a session; set to `false` (or `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=0`) to suppress it |

### Design Implications

- Background session state must be written durably enough to survive supervisor restart (`state.json` is flushed on every checkpoint, and in-flight shell commands/subagents/scheduled tasks are handed off across a stop-restart cycle as of v2.1.196 — `CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF=1` opts out).
- Worktree isolation means background agents cannot accidentally dirty the main working tree; merging results back is an explicit user action — though as of v2.1.198, sessions that create a worktree may auto-commit, push, and open a draft PR without asking, which implementations should treat as a policy decision, not a hidden default to copy blindly.
- `roster.json` is the authoritative list of background sessions; session pickers should read from it when building the resume list, but it is a rebuildable cache over supervisor-managed process state, not the sole source of truth for a crashed daemon.
- `disableAgentView` is a managed enterprise setting exposed both as a `settings.json` key and an env var — enterprise deployments may hide the whole feature, not just the UI; implementations must not assume it is always present.
- `awaySummaryEnabled` is independent of agent-view visibility; a summary can be generated even for a foreground session resumed after being away.

### Integration With the Resume Decision Tree

The `references/resume-path-decision-tree.md` decision tree should route to `claude agents` as a named path when:

- The session was started with `--bg` or `/bg`
- The session ID is present in roster.json
- The terminal was closed and agent-view is the preferred UX

This path sits between "exact session ID resume" (lower UX friction) and "picker search" (broader coverage) in the tree.

## Checkpointing and Rewind

Claude Code creates a new checkpoint on every user prompt, capturing the code state before that prompt's edits begin. Checkpoints track **only file changes made through Claude's own file-editing tools** — they do not capture files touched by bash commands (`rm`, `mv`, `cp`, etc.) or by any process outside the current session. That is a load-bearing limitation, not an edge case: any runtime cloning this pattern must decide explicitly whether to widen tracked-change scope beyond editor-tool calls, and must not imply broader coverage than it has.

### Entry Points

| Method | Behavior |
|--------|----------|
| `Esc Esc` (double-tap, empty prompt) | Open the rewind menu. If the prompt has text, double-Esc clears the input instead (recoverable via `Up`) |
| `/rewind` | Open the rewind menu via slash command |
| Select a checkpoint | Restore conversation, code, both — or summarize around that point |

### Restore Modes

- **Restore code and conversation**: full rollback to the selected point
- **Restore conversation**: rewind chat history, keep current code
- **Restore code**: revert file changes, keep the conversation
- **Summarize from here**: keeps messages before the selected point intact; the selected message and everything after collapses into a summary — use to discard a side discussion while keeping earlier context in full detail
- **Summarize up to here**: keeps messages after the selected point intact; everything before collapses into a summary and you remain at the end of the conversation — use to compress early setup while keeping recent work in full detail

Both summarize modes preserve the original messages in the session transcript (Claude can still reference them if needed) and accept optional steering instructions, the same way `/compact` does — but scoped to one side of a chosen point instead of the whole conversation.

### Rewind Past a Cleared Conversation

If `/clear` ran earlier in the same process, the rewind menu shows an extra top entry, `/resume <session-id> (previous session)`, to jump back to the pre-clear conversation (requires a recent-enough Claude Code version; on older versions use `/resume` and pick it from the picker instead). Design implication: `/clear` does not destroy the prior session's checkpoints — it starts a new one and the old session remains independently resumable/rewindable.

### Design Implications for Session Storage

- Checkpoints are runtime state, not project memory — they live in the session layer alongside transcripts
- Checkpoints persist across session resume, so a user can close the terminal and still rewind later
- Checkpoint storage should be cheap per operation (copy-on-write or incremental diff) to avoid blocking the agent loop
- The rewind menu should clearly distinguish restore modes (conversation vs code vs both) from the two non-destructive summarize modes, since only the restore modes actually discard state
- Document the bash-command blind spot explicitly in any user-facing rewind UI — silently implying full coverage is the most common trust-breaking bug in this feature class

### Rewind vs Git vs Session Branching

Checkpointing is not a replacement for git, and it is not the same primitive as branching a session. Three distinct mechanisms solve three distinct problems — conflating them is a common design mistake:

| Mechanism | Scope | What survives | Use when |
|---|---|---|---|
| Rewind / checkpoint (`/rewind`, `Esc Esc`) | Same session, same conversation | Files reverted via copy-on-write/diff; conversation truncated or summarized in place | Undo the agent's own recent edits or steer the current thread without starting over |
| Session branch (`/branch`, or `claude --continue`/`--resume <id> --fork-session`) | New, independent session — a full copy of the conversation so far | Original session is untouched and stays resumable; the new session diverges from that point forward | Try a different top-level approach while preserving the path you were on; A/B test prompting or implementation strategy from the same loaded context |
| Git commit | Durable, cross-session, cross-tool | Whatever you committed, forever | Permanent history and collaboration |

Rewind and `/branch`/`--fork-session` are easy to confuse because both "go back to an earlier point," but rewind mutates the current session in place while branching spins up a second, independent session ID that shows up grouped under the root session in the picker. Permissions approved with "allow for this session" do **not** carry over to a branched session. Users should still commit to git regularly — rewind and branching are for fast in-session experimentation, not long-term version control.

### Integration With Compaction

Checkpoints interact with compaction: "Summarize from here" and "Summarize up to here" let the user choose a point to compact around, keeping the side that matters intact while compressing the rest. This is a more targeted alternative to auto-compaction at the context limit, which always summarizes the entire history.

## Known Traps

- Using human-readable titles or recent-path heuristics as the real session identity and colliding restores across worktrees or projects.
- Persisting caches and derived state that should be recomputed, then replaying stale tool registries, settings, or summaries after resume.
- Treating transcript restoration as enough while background tasks, checkpoints, and remote-control state are still missing.
- Assuming one resume path works across local, remote, and cross-worktree recovery without explicit environment validation.
- Letting compaction destroy decision boundaries that later rewind or debugging workflows still depend on.
- Conflating in-place rewind/summarize with session branching. Rewind mutates the current session; `/branch` or `--fork-session` mints a second, independent session ID. Documenting them as one feature causes users to lose the original thread when they only meant to peek at an alternative.
- Assuming checkpoint/rewind covers every file mutation. It only tracks changes made through the agent's own file-editing tools — bash-driven renames, deletes, and copies are invisible to it and cannot be undone through rewind.

## Common Anti-Patterns

- Using titles as primary session identity.
- Persisting caches that should be recomputed.
- Treating repo memory and runtime session state as the same layer.
- Assuming one resume code path works equally well across worktrees and projects.
- Requiring enriched indexes to exist before any session can be restored.

## Cross-Platform Patterns (Goose)

Goose adds two session patterns not covered by the Claude Code-derived core: **cross-process session re-attach over ACP**, and **recipe-as-session-seed** for deterministic resume.

### Cross-process session re-attach (ACP)

Goose runs as an ACP stdio server. When an editor (Zed, JetBrains, etc.) disconnects and reconnects, the session ID is passed back on the new stdin pipe and the agent re-attaches in-place. This is different from in-process resume (already covered by rewind/checkpoint) and different from same-machine file-watch continuation — the process may have restarted, but the session object persists.

- **Pattern:** session identity must survive the parent process it was spawned by. Persist session state server-side; require the re-attaching client to prove it holds the session ID.
- **Anti-pattern:** binding session lifetime to the stdin FD or parent PID. That collapses editor restarts, agent upgrades, and sleep/resume into session loss.
- **Recipe:** on ACP connect, the agent looks up the session ID in its session store; if found and auth proof matches, resume from persisted transcript + checkpoint. If not, create new. Log whether a resume hit or missed so operators can distinguish session loss from client-side amnesia.

### Recipe-as-session-seed

A resumed session is usually rehydrated from the transcript. Goose's recipe model offers an alternative: a session can be re-seeded from the *recipe* that spawned it plus its parameters — a typed, versioned, much smaller artifact than a raw transcript. This is stronger than transcript replay because inputs are structured and the recipe version pins extension set and instructions.

- **Pattern:** for recipe-spawned sessions, persist `(recipe ref, recipe version, parameter values, output checkpoints)` alongside the transcript. Resume can choose: replay transcript (high fidelity, large) or re-spawn from recipe + parameters + last checkpoint (deterministic, small).
- **Anti-pattern:** storing only the transcript for recipe-spawned sessions. On cross-version resume, the transcript may reference tools or extensions no longer in the envelope.
- **Recipe:** add a `seed_ref: Option<RecipeSeed>` field to session metadata. When present, resume UI should offer "replay transcript" and "re-run recipe from last checkpoint" as named modes.

## Navigation

### References

- [`references/session-lifecycle-and-resume.md`](references/session-lifecycle-and-resume.md) — Session identity, picker flows, cache clearing, and resume entrypoints
- [`references/transcript-restoration-and-cross-worktree-recovery.md`](references/transcript-restoration-and-cross-worktree-recovery.md) — Transcript recovery, summary persistence, and cross-worktree safeguards
- [`references/context-lifecycle-and-branching.md`](references/context-lifecycle-and-branching.md) — Per-turn branching (continue/rewind/clear/compact/subagent), 1M-context rot zone, steered compaction, and subagents as context-management primitive
- [`references/context-forking.md`](references/context-forking.md) — Blank-vs-forked subagent startup, `CLAUDE_CODE_FORK_SUBAGENT=1` and `/fork` surfaces, cache-prefix economics, isolation guarantees, and fork-as-exception rule
- [`references/resume-path-decision-tree.md`](references/resume-path-decision-tree.md) — When to use session ID vs picker vs ACP re-attach vs recipe re-seed
- [`references/openai-codex-session-task-turn-protocol.md`](references/openai-codex-session-task-turn-protocol.md) — OpenAI Codex Session / Task / Turn protocol, queue contract, response bookmarks, and interruption rules
- [`references/openai-codex-session-persistence.md`](references/openai-codex-session-persistence.md) — SQLite session index, `codex resume` / `fork` / `cloud` subcommand semantics, storage path layering

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for session lifecycle guidance

### Related Skills

- [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md)
- [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md)
- [`../ai-coding-agents-tasks/SKILL.md`](../ai-coding-agents-tasks/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Session/resume/checkpoint mechanics were re-verified against `code.claude.com/docs/en/{sessions,checkpointing,sub-agents,agent-view}` and `learn.chatgpt.com/docs/developer-commands` on 2026-07-11. Several details in this file are gated behind a specific Claude Code version (noted inline, e.g. "v2.1.117+", "v2.1.196+"); re-check the changelog before asserting exact behavior on an unknown build.
- Resume, checkpoint, and log storage formats drift release to release — Anthropic's own docs state the transcript JSONL entry format is internal and can change between versions. Preserve the architecture and behavioral contracts described here; re-verify exact file formats and flag names before shipping code that parses them directly.
- The Codex references in this skill mix two source types: CLI-surface behavior (re-verified against `learn.chatgpt.com/docs/developer-commands`, 2026-07-11) and internal storage architecture (SQLite index, crate/file names) pinned to a specific `openai/codex` source commit from 2026-05-25 that is not restated in public docs — treat the storage-layer claims as commit-pinned engineering detail, not a documented public contract, and re-check against current source before relying on exact file/module names.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
