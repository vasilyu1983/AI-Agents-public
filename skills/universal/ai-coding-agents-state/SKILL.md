---
name: ai-coding-agents-state
description: "Designs session and task state for coding-agent runtimes: resume, checkpoints, compaction, cancellation, background and scheduled runs. Use when persisting agent work."
compatibility: Portable core. Works on Claude Code and Codex.
version: "2.0"
last_validated: 2026-09-29
---

# AI Coding Agents State

Use this skill to design or review the durable state of a coding-agent runtime: sessions (IDs, transcripts, resume, checkpoints, compaction) and tasks (types, lifecycle, claiming, cancellation, background work, triggers). Both are host-owned runtime state, so they share one store, one identity model, and one recovery story.

This skill is about runtime state, not product backlog planning. For persistent repo instructions and always-loaded memory files, use [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md).

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What belongs in a session model? | [references/session-lifecycle-and-resume.md](references/session-lifecycle-and-resume.md) | Session IDs, picker flows, stale-cache reset, resume semantics, store schema and retention |
| How do transcripts recover across worktrees and summaries? | [references/transcript-restoration-and-cross-worktree-recovery.md](references/transcript-restoration-and-cross-worktree-recovery.md) | Restoration boundaries, search, cross-project safeguards, replay rules |
| Which resume path applies (session ID / picker / ACP re-attach / recipe re-seed)? | [references/resume-path-decision-tree.md](references/resume-path-decision-tree.md) | Decision tree, path comparison, prompt-cache economics in subagent spawning |
| Continue, rewind, clear, compact or subagent at this turn? | [references/context-lifecycle-and-branching.md](references/context-lifecycle-and-branching.md) | Context rot zone, rewind over correction, compact-vs-clear, subagent mental test |
| How do forked subagents change cache, isolation, resume and cost? | [references/context-forking.md](references/context-forking.md) | Named-vs-forked startup, cache-prefix economics, isolation behavior |
| Checkpoints, rewind vs git vs branch, background-session resume, compaction contract | [references/session-background-checkpointing-and-compaction.md](references/session-background-checkpointing-and-compaction.md) | Mode rules, coverage blind spots, comparison table, re-injection contract |
| How does Codex split Session / Task / Turn state? | [references/openai-codex-session-task-turn-protocol.md](references/openai-codex-session-task-turn-protocol.md) | SQ/EQ protocol, response bookmarks, one-active-task invariant, interruption |
| How does Codex persist, resume, fork and cloud-resume sessions? | [references/openai-codex-session-persistence.md](references/openai-codex-session-persistence.md) | Rebuildable index over the rollout log, `resume` / `fork` / `cloud` semantics |
| What task types should the runtime support? | [references/task-types-and-lifecycle.md](references/task-types-and-lifecycle.md) | Task families, statuses, background eligibility, host ownership |
| How do task lists and teammate routing work? | [references/task-list-coordination-and-teammate-routing.md](references/task-list-coordination-and-teammate-routing.md) | File-watched lists, claiming, blockers, teammate routing, response loops |
| How do Codex cloud tasks and agent graphs behave? | [references/openai-codex-cloud-tasks-and-agent-graph.md](references/openai-codex-cloud-tasks-and-agent-graph.md) | Task CLI lifecycle, best-of-N, partial apply states, persisted topology |
| Where is the runtime surface for loops and cyclic/workflow graphs? | [references/loop-and-graph-runtime-surfaces.md](references/loop-and-graph-runtime-surfaces.md) | Surface matrix, queue-vs-cyclic-graph data model, portable loop contract |
| How do Anthropic-hosted routines (schedule / API / GitHub) behave? | [references/claude-code-routines.md](references/claude-code-routines.md) | Trigger types, `/fire`, fresh-session model, cap-drop behaviour |
| How do I trigger agents from webhooks, queues or schedules at scale? | [references/webhook-and-queue-triggers.md](references/webhook-and-queue-triggers.md) | SQS / Streams / Kafka / EventBridge, idempotency, dedup, DLQ, rate-limit slots |
| How do I make triggered runs durable across crashes? | [references/durable-trigger-integration.md](references/durable-trigger-integration.md) | Temporal / Inngest / Restate / Step Functions, agent-as-activity, sagas, replay |
| Task sizing, scheduled-trigger table, background-subagent semantics | [references/task-sizing-triggers-and-background-semantics.md](references/task-sizing-triggers-and-background-semantics.md) | Sizing gate, routines vs `/loop` vs desktop tasks, pending-input sub-state |
| Goal-mode loops (act, score, check goal) | [references/goal-mode-loops.md](references/goal-mode-loops.md) | Failure modes, bottlenecks, filesystem state for long runs |
| Goose session re-attach, recipe seeds, typed recipe blueprints, sub-recipes | [references/goose-session-and-task-patterns.md](references/goose-session-and-task-patterns.md) | ACP re-attach, capability-narrowed subagents, sub-recipe lifecycle |
| Where do I host the trigger and agent (Vercel, Fly, CF, Render)? | [`../software-paas-hosting/references/agent-hosting-matrix.md`](../software-paas-hosting/references/agent-hosting-matrix.md) | Per-shape PaaS stacks and reference architectures |
| Validate a recipe blueprint YAML statically | [`scripts/recipe_scanner.py`](scripts/recipe_scanner.py) | Fail-closed validator: required fields, parameter types, extension risk gates, placeholders |

## When To Use

- Design resume and continue flows, session IDs, transcript restoration, checkpoint rewind, or compaction for a coding-agent CLI
- Restore transcripts, summaries or worktree-bound state safely, including cross-worktree recovery
- Add typed tasks, task lists, background execution, claiming, blocking, and teammate coordination
- Model cancellation, foreground/background transitions, and remote or workflow tasks
- Wire scheduled, webhook or queue triggers into the task model
- Implement runtime surfaces for Loop Engineering or Graph Engineering

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Persistent repo instructions and shared memory files | [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md) |
| Remote execution, bridge sessions, TUI and dialogs | [`../ai-coding-agents-surfaces/SKILL.md`](../ai-coding-agents-surfaces/SKILL.md) |
| Tool-call permission gating, approval modes, subagent policy inheritance | [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) |
| Multi-agent planning and ownership contracts | [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md) |
| Loop shapes, termination predicates, convergence detection (owner; [references/goal-mode-loops.md](references/goal-mode-loops.md) is pending a move there) | [`../agents-swarm-orchestration/references/loop-orchestration.md`](../agents-swarm-orchestration/references/loop-orchestration.md) |
| Script-held deterministic control flow (Claude Code Workflows) | [`../agents-swarm-orchestration/references/scripted-workflows.md`](../agents-swarm-orchestration/references/scripted-workflows.md) |

## Shared Contract

- **One host-owned store.** Session and task state (identity, status, ownership, timestamps, background flag) live in runtime state, not in UI widgets and not in project memory.
- **Identity is a stable ID.** Session IDs and task-list IDs are host-owned and sanitized before they become a filesystem or sync key. Titles and aliases are convenience lookups.
- **Restore what is safe to trust; rebuild the rest.** Persist transcripts, summaries, checkpoints and task state; recompute caches, discovery indexes and grants.
- **One writer per ID.** A session or task claim is a lease plus a fencing token, not a flag.

## Session Workflow

1. **Define session identity first.** A stable ID, with title or search aliases as secondary keys.
2. **Split restoreable from recomputable state.** Clear discovery caches (file, skill, tool registry, config) before rebuilding live state on resume.
3. **Support exact and interactive recovery.** Resume by UUID, exact title match, and picker/search fallback. Pickers exclude the current session and sidechain-only artifacts.
4. **Treat worktree and project boundaries explicitly.** Same-repo worktree moves are a relocation case, not a missing session; cross-project resume is explicit and reviewable, never silent.
5. **Order lookups deliberately.** An index miss is not a missing session: fall back to direct log or transcript lookup before declaring it unrecoverable.
6. **Restore summaries and collapsed state, not just raw logs.** Background tasks, checkpoints and remote-control state must come back too.
7. **Attest the restored envelope.** Record which transcript/checkpoint loaded, what was rebuilt, what was discarded, and the effective model, tools, permissions, workspace and context-start mode. Resume fidelity and prompt-cache reuse are separate claims; verify both from runtime evidence.
8. **Test failure paths.** Missing session, multiple title matches, stale worktree path, interrupted resume, index miss with log fallback, cross-project recovery.

### Session Rules

- **An in-flight tool call at crash time has an unknown outcome.** Surface a call with no recorded result to the model and the user on resume. Never auto-replay a non-idempotent call (push, deploy, migration, external API). Rewinding past a side-effecting call leaves a note that the effect happened.
- **One writer per session ID.** Take a lease (owner process, host, heartbeat) before appending. A second attach becomes a read-only viewer or forks a new ID; take over a stale lease only after its heartbeat expires.
- **The session store carries its own schema version.** Migrate forward only, back up first, and never let an older client write to a newer store. A documented retention policy bounds transcript, log and job-worktree growth. See [Store Schema And Retention](references/session-lifecycle-and-resume.md#store-schema-and-retention).
- **Re-derive grants on resume, branch and fork.** Intersect persisted session-scoped approvals with the current managed and project policy instead of restoring them; a grant saved before a policy was tightened must not survive.
- **One resume path does not fit local, remote and cross-worktree recovery** without explicit environment validation.
- Transcript, checkpoint and log storage formats are internal and version-fragile: build against export or scripting interfaces. Storage-layer names in the Codex references come from source, not public docs; check current source before relying on them.

### Checkpoints, Rewind and Compaction

- Checkpoints track only file changes made through the agent's own edit tools, not files touched by shell commands. Say so in any rewind UI; silently implying full coverage is the most common trust-breaking bug in this feature class.
- Restore modes discard state; summarize modes are non-destructive. `/clear` starts a new resumable session and leaves the old one rewindable.
- Rewind (same session, in place), session branch (new independent session ID) and git (durable, cross-tool) are different mechanisms. Documenting them as one feature loses the original thread. Comparison table: [references/session-background-checkpointing-and-compaction.md](references/session-background-checkpointing-and-compaction.md).
- Compaction is a state transition with a written contract: name what is re-injected (each item separately bounded), name what is lost, and record a boundary marker in the transcript so rewind and debugging can see where detail ends. Look up the runtime's current re-injection set and limits before depending on it.

## Task Workflow

1. **Model task types explicitly.** Local shell, local agent, remote agent, teammate, workflow and monitor-style tasks are not one untyped blob. Task type and state are runtime data, typed separately from UI rendering.
2. **Keep task state in the host store.** Status, ownership, backgrounding and timestamps are runtime state.
3. **Define background eligibility.** Only running or pending tasks that are actually backgrounded appear in background surfaces.
4. **Use claiming for shared lists.** External or teammate lists need explicit claim and release.
5. **Respect blockers and owners.** Pending tasks with unresolved blockers or owners are not available for pickup, and UI sort order never decides runnable order.
6. **Differentiate abort from kill.** Interrupting the current turn is not terminating the task object.
7. **Stabilize task-list identity.** Resolve from explicit context first; use monotonic high-water-mark rules so resets and branch changes do not reuse old IDs and reconnect stale work.
8. **Serialize shared mutations.** Lock or back off when several workers can touch one list.
9. **Separate budget axes.** Store task budget, context/input tokens, output/reasoning tokens when available, tool calls, wall time and external spend independently. Declare which limits the runtime enforces and map each exhausted limit to a terminal or escalated state.
10. **Test concurrency edges.** Double claim, failed submission after claim, blocked ordering, background/foreground transitions, remote cancellation.

### Task Host Rules

- A claim is a lease plus a fencing token: record owner, lease deadline and a monotonically increasing token; the worker renews by heartbeat and presents the token on every progress, complete or release write, and the store rejects stale tokens. Lease expiry is the only stale-owner recovery path. See [`../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md`](../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md).
- Cancellation is two-phase: a cancel request moves the task to `cancelling`; after the worker acknowledges or a hard-kill deadline expires, kill the whole process group and cascade to child tasks. The task is terminal only after children are reaped.
- Write the result (or artifact reference) and the `completed` status in one atomic write, or write the result first and flip the status idempotently. A retry after a claim checks for an existing result before re-executing side-effecting work.
- Lead and teammate navigation stay separate from generic task-list execution.
- Check whether the host exposes task-tracking tools for the active model before designing on them; availability differs by host, model and mode.
- A background task that hits an unapproved tool call surfaces a pending-input state to the owning session, labeled with the task's name, while the task stays alive. Never auto-deny into a stalled read-only loop. Host-wide background policy beats per-task requests. See [references/task-sizing-triggers-and-background-semantics.md](references/task-sizing-triggers-and-background-semantics.md).
- A scheduled or triggered run is a task: apply the same typing, claiming, blocker and cancellation rules; a Routine-spawned task follows remote-task lifecycle, and each fire starts a fresh session that relies on repo instructions, not transcript memory.
- Size a task to what one reviewer can verify in one sitting; decompose multi-day asks before dispatch.

## Build Order

1. Stable session identity, storage keys, and typed task families with lifecycle states.
2. One host-owned store separating durable state from recomputable caches, with timestamps and ownership.
3. Exact-ID resume before title or picker recovery; cache clear and live-state rebuild on resume.
4. Background eligibility, foreground transitions, and claim/release for shared lists.
5. Worktree-aware recovery, task-list identity non-reuse, blocker resolution, serialized mutations.
6. Transcript compaction with a contract, summary restore, fallback lookup.
7. Teammate and remote-task routing with explicit cancellation; then triggers.

## Core Invariants

- Session and task state are runtime data, not UI decoration and not project memory.
- Identity is a stable ID; task-list IDs are not reused casually after reset or crash.
- Claiming shared work is explicit and collision-resistant; abort and kill are different actions with different guarantees.
- Background visibility reflects real background execution, not intent.
- Compaction must not destroy decision boundaries that later rewind or debugging still needs.

## Failure Modes

- Title collision resumes the wrong session; replayed persisted caches restore stale tools, settings or summaries.
- Requiring the enriched index to exist, so an index miss reads as a lost session.
- Background daemon and foreground resume interleave appends and corrupt the transcript.
- Multiple workers claim the same task; submission fails after claim without releasing ownership.
- Blocked tasks scheduled as runnable; badge counts with no real background-task model.
- Cancellation stops the turn but leaves the task object running; a task marked terminal before its children are reaped leaves orphan shells mutating the workspace.
- A crash between writing the result and writing `completed` yields "done with no output" or a re-run of finished side-effecting work.
- A renamed spawn primitive (for example `Task` to `Agent`) treated as two task families instead of one primitive under an old name.

## Minimal Viable Version

- Stable session IDs, exact resume by ID, persisted transcripts and light metadata, cache clear on resume, one picker fallback, direct-log fallback.
- One typed task model with statuses and ownership in one host store, one real-state background filter, one atomic-enough claim and release path, one host-owned task-list ID strategy, and an abort-versus-kill distinction.

## What Strong Implementations Add

- Worktree adoption, progressive transcript loading, summary and usage-state restore, and an audit trail of why a resume succeeded, failed or switched paths.
- File-watched or externally synchronized task lists, teammate routing, debounced watchers, lockfile discipline, and explicit blocker, retry and escalation transitions.
- Typed recipe blueprints with static validation, capability-narrowed subagents, and sub-recipe composition with cascading cancellation.

## Navigation

- References: the Quick Reference table lists every file in `references/`.
- Scripts: [`scripts/recipe_scanner.py`](scripts/recipe_scanner.py) with tests in [`scripts/test_recipe_scanner.py`](scripts/test_recipe_scanner.py) (`python3 -m unittest test_recipe_scanner` from `scripts/`).
- Data: [`data/sources.json`](data/sources.json) holds primary documentation and source references.
- Related: [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md), [`../ai-coding-agents-surfaces/SKILL.md`](../ai-coding-agents-surfaces/SKILL.md), [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md), [`../ai-agents/references/autonomous-loop-patterns.md`](../ai-agents/references/autonomous-loop-patterns.md) (when a trigger drives an autonomous loop, not a single run), [`../agents-hooks/references/budget-and-loop-hooks.md`](../agents-hooks/references/budget-and-loop-hooks.md) (budget, iteration-cap, stagnation and kill-switch enforcement for triggered runs).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
