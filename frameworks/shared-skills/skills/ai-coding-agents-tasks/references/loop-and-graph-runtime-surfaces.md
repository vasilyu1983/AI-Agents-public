# Loop and Graph Runtime Surfaces

## Table of Contents

- [Why This Comparison Matters](#why-this-comparison-matters)
- [Surface Matrix](#surface-matrix)
- [Claude Code — Programmable Control Flow](#claude-code--programmable-control-flow)
- [Codex — Declarative Roles, Model-Held Control Flow](#codex--declarative-roles-model-held-control-flow)
- [Task Queue vs Cyclic Graph](#task-queue-vs-cyclic-graph)
- [Choosing A Runtime For Iterative Work](#choosing-a-runtime-for-iterative-work)
- [Portable Loop Contract](#portable-loop-contract)
- [Scheduled And Recurring Work](#scheduled-and-recurring-work)
- [Known Traps](#known-traps)
- [Verification Note](#verification-note)
- [Cross-References](#cross-references)

Where [task-types-and-lifecycle.md](task-types-and-lifecycle.md) models tasks as a **queue** — claim, run, complete — this reference covers what happens when the work is **iterative or cyclic**: loops that repeat until convergence, and graphs whose edges carry state between nodes. Where [openai-codex-cloud-tasks-and-agent-graph.md](openai-codex-cloud-tasks-and-agent-graph.md) covers Codex's persisted parent-child *topology*, this file covers **control flow** across both runtimes.

## Why This Comparison Matters

Claude Code and Codex diverged in mid-2026 on a dimension that determines how iterative work must be built. The difference is not cosmetic and not closable by prompt engineering:

- **Claude Code** can execute orchestration as **code**. Loops, branches, and fan-out live in a script the runtime runs.
- **Codex** orchestrates through **declarative role files plus turn-by-turn model decisions**. There is no code-mode loop primitive.

Design consequence: an iterative workflow that is ten lines of `while` on Claude Code becomes either a model-held loop (weak termination guarantee) or an external driver (extra infrastructure) on Codex. Teams targeting both runtimes must build to the weaker surface or accept per-runtime implementations.

## Surface Matrix

| Capability | Claude Code | Codex CLI |
|---|---|---|
| Code-mode orchestration script | Yes — Dynamic Workflows | No |
| Loop primitive in orchestration | Yes — JS `while`/`for` in script | No — lead-thread iteration only |
| Parallel fan-out | Subagents; `parallel()`/`pipeline()` in scripts | Subagents; `max_threads` (default ~6) |
| Direct worker-to-worker comms | Agent Teams | No — coordinate via parent |
| Recursive spawning | Bounded by depth rules | `max_depth = 1` default |
| Concurrency ceiling | ~16 concurrent, 1000 total per run | `max_threads` configurable |
| Role definition | Agent files / frontmatter | TOML in `.codex/agents/` |
| Persisted parent-child topology | Session and task state | Agent-graph store |
| Batch spawn from data | Script over a list | Experimental `spawn_agents_on_csv` |
| Deterministic replay / resume | Prefix-cached resume by run id | Task-level re-run |

Treat every row as verify-before-relying. Both runtimes moved substantially through 2026.

## Claude Code — Programmable Control Flow

Dynamic Workflows shipped **2026-05-28** alongside Opus 4.8 (CLI v2.1.154+). The orchestrator writes a small JavaScript program that the harness executes; the script spawns subagents, routes outputs between them, and holds the loops and conditionals itself.

Consequences for task-system design:

- **Intermediate results stay out of the lead's context.** A 200-item sweep keeps the lead's window at roughly final-answer size, because per-item reports live in script variables.
- **Termination becomes executable.** A loop predicate in code is a guarantee; a loop predicate in a prompt is an intention that decays as context fills.
- **Runs are resumable by prefix.** The unchanged prefix of agent calls returns cached results; the first edited call onward re-executes. Iterating on orchestration is cheap.
- **Scale is real and must be opted into.** One instruction can spawn dozens of agents, so this surface should never be entered by inference.

Full primitive semantics, barrier-vs-pipeline rules, and determinism constraints: [`../../agents-swarm-orchestration/references/scripted-workflows.md`](../../agents-swarm-orchestration/references/scripted-workflows.md).

## Codex — Declarative Roles, Model-Held Control Flow

Codex CLI Multi-Agent v2 (v0.137, **2026-06-04**) defines agents as TOML role files under `.codex/agents/`, with `/agent` for thread management. Orchestration is declarative in the roles and imperative in the model's turn-by-turn reasoning — there is no script layer that decides what runs next.

Building iterative work on Codex means choosing one of:

1. **Lead-thread iteration** — the model decides each round whether to continue. Weakest termination guarantee; pair with enforced caps.
2. **External driver** — a shell or Python wrapper invoking Codex non-interactively per iteration, holding the loop and the checkpoint. Strongest guarantee; most infrastructure. See [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md).
3. **Durable workflow engine** — Temporal / Inngest / Restate with the agent as an activity, when the loop must survive crashes. See [durable-trigger-integration.md](durable-trigger-integration.md).

Defaults to respect: `max_depth = 1` (no recursion) and `max_threads` (~6). Raising depth is rarely correct — errors compound across levels uncaught.

## Task Queue vs Cyclic Graph

A queue and a cyclic graph are different data models, and conflating them is the most common design error in this area.

| | Task queue | Cyclic graph |
|---|---|---|
| Node revisits | No — a task completes once | Yes — nodes re-enter with new state |
| Edges carry | Nothing (ordering only) | Accumulated state |
| Termination | Queue drains | Predicate over state |
| Failure unit | One task | One pass; state persists |
| Naturally models | Independent work items | Refinement, discovery, feedback |

If work re-enters the same node with different state, a queue will model it as an unrelated new task and lose the accumulated context that made the second visit meaningful. Symptoms: rediscovering the same findings each round, no convergence signal, retry counts that mean nothing.

**Rule:** the moment a task's input depends on a prior *completion of the same task type*, you need graph state — an explicit accumulated-state object — not a second queue entry. Persist that state in files, not memory, so any new lead session resumes by reading it.

## Choosing A Runtime For Iterative Work

| Situation | Choose | Why |
|---|---|---|
| Many items, known stages, high intermediate volume | Claude Code scripted workflow | Deterministic flow; lead context stays small |
| Unknown extent, must converge, single runtime | Claude Code script loop | Executable termination predicate |
| Must survive crash / span hours or days | External driver or durable engine | Survives session death on either runtime |
| Codex-only shop, iterative work | External driver + enforced caps | No code-mode loop available |
| Cross-runtime portability required | Portable loop contract (below) | Build to the weaker surface |
| Judgment-dependent next step | Lead-thread on either runtime | Scripts cannot encode judgment |

## Portable Loop Contract

When the same iterative workflow must run on both runtimes, define the loop as data and keep the driver thin. Every field is required — a loop missing any of them is unbounded on at least one runtime:

```text
goal:            <one-sentence objective>
progress:        <what makes pass N+1 differ from pass N>
termination:     <observable predicate over state>
hard_cap:        <max iterations AND max tokens>       # independent of predicate
on_cap:          halt | escalate                       # never "continue"
state_file:      <path — accumulated state, survives restart>
dedup_key:       <function over surfaced items>
checkpoint:      <path — written every pass>
```

Then implement the driver per runtime: a script loop on Claude Code, an external wrapper on Codex. The contract stays identical, so the workflow's behavior does not depend on which runtime executed it.

Two invariants worth restating because both runtimes make it easy to violate them:

- Deduplicate against **everything surfaced**, not everything confirmed. Dedup against confirmed results makes rejected items resurface every pass, and the loop never terminates.
- Enforce caps in **hooks or driver code**, not prompt instructions. Instructions decay with context; runtime enforcement does not.

## Scheduled And Recurring Work

Recurring work is a loop with time as the trigger. Both runtimes expose scheduling, and it interacts with task-store design: each firing is normally a fresh session, so **nothing carries over except what was written to files**.

Design rules:

- Treat the state file as the only continuity between firings. A scheduled loop that relies on session memory silently restarts from zero.
- Make each firing idempotent — a re-fire after a crash must not double-apply.
- Cap cumulative spend across firings, not just per firing. Per-run caps do not bound a schedule that fires hourly.
- Give recurring runs an explicit stop condition or expiry. A schedule with no end is an unbounded loop with a slow clock.

See [claude-code-routines.md](claude-code-routines.md) for trigger types and fresh-session semantics, and [webhook-and-queue-triggers.md](webhook-and-queue-triggers.md) for event-driven equivalents.

## Known Traps

| Trap | Consequence | Fix |
|---|---|---|
| Assuming Codex has a code-mode loop | Design does not build; late rework | Use external driver on Codex |
| Modeling cyclic refinement as queue entries | Accumulated state lost; no convergence | Explicit graph-state object in a file |
| Model-held loop with no enforced ceiling | Runs until context or budget dies | Hook or driver caps outside the agent |
| Dedup against confirmed results | Rejected items resurface forever | Dedup against all surfaced items |
| Raising Codex `max_depth` above 1 | Errors compound uncaught across levels | Keep at 1; verify at each level |
| Scheduled loop relying on session memory | Silent restart from zero each firing | State file is the only continuity |
| Per-firing cost cap on a recurring schedule | Unbounded cumulative spend | Cap cumulative across firings |
| Reading a cached empty result as "did not run" | Misdiagnosis during resume debugging | Read the run journal for actual returns |
| Porting a Claude Code script to Codex verbatim | No execution surface for it | Re-implement the driver; keep the contract |

## Verification Note

Version- and date-stamped claims here (Dynamic Workflows 2026-05-28 / CLI v2.1.154+; Codex Multi-Agent v2 v0.137 / 2026-06-04; concurrency and depth defaults) reflect the August 2026 check. Both runtimes iterate faster than this file. Re-verify against official release notes before committing an architecture, and mark these as unverified when web access is unavailable.

## Cross-References

- Scripted workflow primitives and constraints: [`../../agents-swarm-orchestration/references/scripted-workflows.md`](../../agents-swarm-orchestration/references/scripted-workflows.md)
- Loop shapes, termination, convergence detection: [`../../agents-swarm-orchestration/references/loop-orchestration.md`](../../agents-swarm-orchestration/references/loop-orchestration.md)
- Codex persisted parent-child topology and apply states: [openai-codex-cloud-tasks-and-agent-graph.md](openai-codex-cloud-tasks-and-agent-graph.md)
- Task families, statuses, background eligibility: [task-types-and-lifecycle.md](task-types-and-lifecycle.md)
- Crash-durable multi-step runs: [durable-trigger-integration.md](durable-trigger-integration.md)
- Hosted routines and fresh-session model: [claude-code-routines.md](claude-code-routines.md)
- Hook-enforced iteration and budget caps: [`../../agents-hooks/references/budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md)
- Shape C autonomous loops (PRD-driven, framework-neutral): [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md)
- Graph-structured agent state and traversal: [`../../ai-agents/references/context-graph-patterns.md`](../../ai-agents/references/context-graph-patterns.md)
