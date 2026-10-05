# Task Sizing, Scheduled Triggers, and Background-Subagent Semantics

Moved from the former tasks skill. Note for owners: which skill owns hosted and scheduled triggers (this one, or the agent-hosting and trigger references) is an open audit question (B03); the content is kept here unchanged until that is decided.

## Task Sizing Heuristic

Source: OpenAI (2025), [*How OpenAI uses Codex*](https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf), p. 11 — internal-usage report.

- **Calibration point:** a well-scoped Codex task is one that *"would take you or a teammate about an hour to complete or a few hundred lines of code to implement."* Treat it as a starting calibration, not a ceiling: size a task to what one reviewer can verify in one sitting, and recalibrate from your own merge rate.
- **Pattern — sizing gate:** before queueing a task, ask "could a teammate do this in roughly an hour given the same prompt?" If no, break it down. If yes, dispatch.
- **Anti-pattern — multi-day asks framed as one task.** "Migrate the auth subsystem to OAuth 2.1" is not a task; it is a project. Decompose into sized tasks each gated by an Ask-Mode plan before dispatch (see [`../../ai-coding-agents/references/openai-internal-practice-codex.md`](../../ai-coding-agents/references/openai-internal-practice-codex.md)).
- **Forecast hook:** "as models improve, expect the size of the tasks it can take on to increase" (OpenAI). Re-baseline this heuristic every two minor model releases; do not treat the hour/few-hundred-LOC figure as a permanent ceiling.
- **Task queue as backlog:** the corollary to the sizing rule — small tasks dispatched freely become a working backlog rather than a planning burden. No obligation to produce a full PR per task; tangential and partial work is legitimate queue content.

## Scheduled Triggers

Hosted scheduling layers (for example Claude Code Routines) let an agent run without a local session. Distinguish three trigger classes; pick the narrowest one that fits:

| Trigger class | Runtime | Persistence | Use when |
|---------------|---------|-------------|----------|
| **Routines** (Anthropic cloud) | Cloud-hosted Claude Code workers | Schedule, API call, or GitHub event fires the job with the laptop closed | You need cadence-driven or webhook-driven work (PR babysitting, nightly repo sweeps, scheduled reports) |
| **`/loop`** (session-bound) | Current local session | Dies with the session; runs while the session is open | You want a repeating task during an active working session (poll deploy, retry until green) |
| **Desktop scheduled tasks** | Local machine | Tied to this machine staying awake | Machine-local automation where cloud access is not acceptable |

Routines are task-shaped: a Routine creates tasks in the host runtime under a scheduler-owned task family. Apply the same typing, claiming, blocker, and cancellation rules as other task types — schedule triggers do not earn special cases.

Caveats (check the routines docs for current status and caps before treating this as a stable contract):
- Run caps exist per plan, and one-off (non-scheduled) fires may be counted separately from scheduled runs — model them as separate counters and look up the current caps rather than hard-coding them. Design for throttling, drop-on-cap, and idempotent handlers regardless of plan.
- Each Routine invocation is a fresh session — depends on `AGENTS.md` / `CLAUDE.md` for context, not transcript memory.
- Treat Routine-spawned tasks as remote-task lifecycle, not local-agent lifecycle, for cancellation and ownership purposes.
- GitHub-event runs are capped per routine per hour; events beyond the cap are **dropped, not queued**.

Source: Matt Abrams, *Claude Code Routines* tutorial (2026-04-20); https://code.claude.com/docs/en/routines.

## Background-Subagent Task Semantics

Claude Code's subagent-task model is a concrete reference implementation of the abstract rules above ("Differentiate abort from kill," "background eligibility"), not a Claude-Code-only detail. Check the runtime's sub-agents docs for current defaults and switch names before depending on them.

- **Task-tracking tools may be absent.** Whether the host exposes task-list or todo tools can depend on the active model and mode. Check availability for the model in use before designing a workflow around them.
- **Assume spawns may default to background.** The lead keeps working and is notified on completion or when input is needed, so background-task surfaces must be a first-class, always-visible part of the UI, not a rare drawer.
- **A permission wait is a pending-input sub-state.** A background task that hits an unapproved tool call must route the prompt to the owning session, labeled with the task's name, while the task stays alive. It must not be swallowed and reported as generic progress.
- **Host-wide background policy beats per-task requests.** A host-wide switch that forces spawns into the background (or into fork mode) is a policy on background eligibility, not a per-task property. A runtime that lets an individual task request silently override host-wide policy has a policy-enforcement bug, not a feature.

Known trap to add to your own review checklist: a runtime that treats "background subagent needs a permission" as a silent, unrecoverable failure (auto-deny plus a stalled read-only loop) instead of routing it to the owning session as a first-class pending state. Shipped runtimes have had this exact bug.
