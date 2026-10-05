---
name: dev-workflow-planning
description: "Writes implementation plans before coding: phases, plan files, specs, definition of done. Use when planning a multi-step feature or breaking a large refactor into phases."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.6"
last_validated: 2026-07-11
---

# Dev Workflow Planning

Use this skill to turn vague or risky engineering work into a bounded execution plan with scope, sequencing, checkpoints, verification, and handoff. It owns planning depth, execution shape, and multi-agent guardrails, not system design, PRD authoring, or branch-policy decisions.

## Quick Reference

| Task | Use |
|------|-----|
| Plan structures and artifacts | [references/planning-templates.md](references/planning-templates.md), [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md), [assets/template-milestone-checkpoint.md](assets/template-milestone-checkpoint.md), [../product-management/assets/ops/template-dor-dod.md](../product-management/assets/ops/template-dor-dod.md) |
| Platform-specific workflow mapping | [references/platform-workflows.md](references/platform-workflows.md), [../ai-agents/references/agent-delivery-methods.md](../ai-agents/references/agent-delivery-methods.md) |
| Multi-session planning state | [references/long-horizon-journaling.md](references/long-horizon-journaling.md) |
| Guardrails for parallelism, sessions, and recovery | [references/operational-checklists.md](references/operational-checklists.md), [references/session-patterns.md](references/session-patterns.md), [references/session-scope-budgeting.md](references/session-scope-budgeting.md), [../ai-agents/references/context-rotation-and-state.md](../ai-agents/references/context-rotation-and-state.md) |
| Spec-driven tooling landscape (GitHub Spec Kit, Kiro, BMAD) | [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md) |
| Test-context planning | [../qa-agent-testing/references/coding-agent-regression-testing.md](../qa-agent-testing/references/coding-agent-regression-testing.md) |
| Quantify uncertain delivery cost | [references/uncertain-work-cost.md](references/uncertain-work-cost.md) |
| Mixed changes, no red test possible, process depth by risk | [references/change-classes.md](references/change-classes.md) |
| Source map | [data/sources.json](data/sources.json) |

## When to Use

- Break a feature, migration, refactor, or risky bug fix into verified steps.
- Decide whether work should run sequentially or in bounded parallel waves.
- Turn a requirement or RFC into a plan contract with success criteria and rollback thinking.
- Keep long-running agent work inside durable artifacts and scope limits.

## Route Elsewhere

- System design, service boundaries, or ADRs: use [software-architecture-design](../software-architecture-design/SKILL.md).
- PRD or RFC authoring before planning: use [docs-ai-prd](../docs-ai-prd/SKILL.md).
- Repo maturity, context layers, or instruction rollout: use [dev-context-engineering](../dev-context-engineering/SKILL.md).
- Branching and PR workflow policy: use [dev-git-workflow](../dev-git-workflow/SKILL.md).
- Test-strategy ownership or debugging an active failure: use [qa-testing-strategy](../qa-testing-strategy/SKILL.md) or [qa-debugging](../qa-debugging/SKILL.md).

## Defaults

- Clarify the outcome and success criteria before decomposing work.
- Use the smallest durable planning artifact that fits the task.
- Match planning depth to actual risk and scope.
- Prefer sequential execution when interfaces are moving or files overlap.
- Give each parallel worker a self-contained brief and explicit file ownership; record whether it starts fresh or forks parent history.
- Include targeted test context for affected code instead of generic "write tests first" instructions.

## Workflow

1. Confirm the goal, in-scope boundary, success criteria, and missing inputs.
2. Classify the change as fix, change, refactor or add, and take its first move ([Change Classes](#change-classes-and-first-moves)). Then choose the planning depth by the cost of being wrong: trivial, lightweight, full plan contract, or spec-driven.
3. Order the first step to retire the riskiest assumption, and name the observation that invalidates the plan (for example, call sites exceed the estimate, or a test outside scope fails). When it appears, stop and re-plan instead of continuing.
4. Lock the plan contract: goal, scope, dependencies, execution order, verification, and rollback.
5. Choose execution shape: sequential or dependency-based waves.
6. Run bounded batches with verification between waves and checkpoint state in durable artifacts.
7. End with a handoff that states what is done, what is not, what was checked, and the next bounded action.

## Core Decisions

### Planning Depth

| Complexity | Depth | Artifact | Trigger |
|---|---|---|---|
| Single-file, obvious outcome | trivial | none or one-liner | direct execution |
| Multi-step, clear scope | low | goal + steps + verification | 2-5 files, no shared interfaces |
| Multi-file, overlapping interfaces | medium | full plan contract with file ownership | 3+ files, schema or API changes |
| Multi-agent, long-horizon, or spec-required | high | spec → design → tasks → implementation | production-touching, unknown dependencies |

### Change Classes and First Moves

Classify by what happens to observable behavior. One class per step; split a mixed request.

| Class | Behavior | First move | Test-first rule |
|---|---|---|---|
| fix | Current behavior is wrong against an agreed spec | Write a test that reproduces the bug | The new test fails on current code for the reported reason, then passes; it stays as a regression test |
| change | Behavior is correct today, but the intended behavior changes | Find the tests that assert the old behavior and edit them to state the new one | The edited tests fail before the code changes; the plan names every edited assertion |
| refactor | Must not change at all | Get the existing suite green; if coverage is thin, add characterization tests that pin current behavior | No assertion edits and no new behavior tests; the same suite passes before and after |
| add | New behavior; existing behavior unchanged | Write the acceptance criteria and the interface, and check for reusable code | New failing tests per criterion before implementation; existing tests pass unedited |

The class sets the first move; risk sets the depth around it. Spend process only where its result could change the plan, and treat irreversible harm as a gate ([decision step and per-class scaling](references/change-classes.md#depth-of-process-the-cost-of-being-wrong), from [foundations-decision-theory](../foundations-decision-theory/SKILL.md)).

### Plan Readiness Gates

For a medium or high plan, pass these before implementation starts:

1. **Ambiguity gate.** If the deliverable, the success criteria or the technical approach has more than one reasonable reading, stop and ask. Do not plan on a guess.
2. **Pattern grounding.** For naming, error handling, logging, data access and tests, cite one existing example in the affected area as `path:line`. If none exists, say so; do not invent a convention.
3. **Cold-reader test.** Someone with no prior knowledge of the codebase could execute every step from the plan alone, with no further searching or questions. If not, add the missing paths, imports and commands.
4. **Deviation log.** During implementation, record each departure from the plan as what changed and why, and carry the log into the handoff.

### When to Spec vs Prototype

| Choose spec-driven | Choose prototype-first |
|---|---|
| Spec required before agent execution (Kiro, Spec Kit workflow) | Throwaway scaffold, demo, or unknown-unknowns spike |
| Multi-agent handoffs with acceptance criteria | Single-session, one dev, no handoffs |
| Requirements must survive context resets | Goal will change within the same session |
| AI agent downstream will re-parse the contract | Human drives all decisions interactively |

Choose depth by where the uncertainty can be resolved. If a bounded spike or read-only exploration will answer it faster than a full plan, run that first and keep the plan provisional.

### Fork Classification and Playbook Fidelity

- Classify each "which approach?" fork before acting: observable (prototype both cheaply and compare) or a preference call (ask the human). Do not ask about an observable fork; do not prototype a preference call.
- When a workflow or playbook is chosen, copy its steps into the todo list verbatim; mark any step you don't take `skip: <reason>` rather than dropping it.
- Hill-climbing optimization loops (one change per measurement, a frozen sensitive harness, a named target and minimum attempts, a decision log) are owned by [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md), not this skill.

### Estimation in the AI-Coding Era

AI coding agents shift the bottleneck from typing speed to decision quality, review bandwidth, and verification cost. Estimating in story points or hours calibrated to human typing speed will misprice the work:

- Re-anchor the estimate to review and verification burden, not generation time. A 200-line AI-generated diff across three files with a stable interface can take minutes to produce and hours to review safely — the review time is the real constrained resource, not the generation time.
- Spec-writing and clarification time now dominates for ambiguous work. An underspecified prompt costs more in rework cycles than the original round of AI-assisted execution saved; budget explicit time for the interview/clarification phase (see [Pre-loop setup phase](#pre-loop-setup-phase-both-variants)) instead of folding it into "implementation."
- Do not let apparent AI generation speed compress the estimate for irreversible or high-blast-radius work (schema migrations, auth, billing, public APIs). Generation is fast; the safe-rollout and verification path is not, and estimating on generation speed alone under-scopes the plan.
- A plausible-looking AI-generated diff is not evidence of correctness. Budget the same verification rigor for AI-generated code as for human-written code of the same risk class — a clean diff creates false confidence, not a discount on review time.
- Treat pre-AI-agent historical velocity or throughput baselines as unreliable comparators for estimation. Recalibrate against the team's own current throughput on AI-assisted work rather than carrying forward last year's per-story averages.

When uncertain review, rework, or work-item volume can change a budget decision, use [the uncertainty recipe](references/uncertain-work-cost.md). Keep schedule logic in the dependency plan; cost simulation does not discover the critical path.

### Plan Mode (Claude Code)

- Use `/plan` for an ambiguous or risky change when reviewing a plan before edits would help. The [Claude Code commands](https://code.claude.com/docs/en/commands) and [permissions](https://code.claude.com/docs/en/permissions) docs are the lookup for current entry points and command gating.

### Execution Model

- sequential by default when risk or overlap is high
- wave-based parallelism only when tasks are truly independent
- explicit `depends_on`, shared-interface definitions, and one validation pass between waves
- stop parallelism once interface churn or file overlap appears
- for schema or API migrations, plan expand → migrate readers and writers → contract as separate milestones, each independently deployable and reversible; never plan a step that changes the producer and all consumers atomically

For plans with parallel work, model dependencies explicitly rather than relying on list order. Each work item names prerequisites, produced artifact or state, owner, verification evidence, and the downstream items it unlocks. Mark an item `ready` only when its prerequisites are observed, `blocked` when a named dependency is unresolved, and `done` only when its evidence exists.

Identify the current critical path and the integration points where parallel branches converge. Recompute it when scope or evidence changes; adding workers to non-critical tasks does not shorten the plan. A milestone is complete only when its integration check passes, even if every contributing task reports done in isolation.

### Next Eligible Milestone

When a PRD or plan carries a [delivery-milestones table](../docs-ai-prd/references/delivery-milestones.md), pick the next work from the table, not from memory:

1. Check that the table is a DAG: every depends-on id exists and no cycle exists. A topological order exists only when there is no directed cycle; if one exists, name it and re-cut the milestones instead of picking an order (`foundations-graph-theory`, Quick Reference).
2. Eligible means `pending` with every dependency `done`, where `done` means its acceptance check passed.
3. On a tie, take the milestone with the most pending milestones downstream of it, directly or transitively. This tie-break is a planning heuristic, not a graph theorem. If still tied, take the one that retires the riskiest assumption (Workflow step 3).
4. Set it `in-progress` before starting. With parallel workers, claim it as [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md) describes. Set it `done` only with the passing check's evidence.

### Foundations for invalid sequences or constrained choices

- Use [planning/search](../foundations-ai-planning-search/SKILL.md) when list order
  hides state-dependent preconditions, irreversible effects, or alternative
  sequences that can invalidate execution. Return initial-state evidence,
  action preconditions/effects, a replayed valid sequence or the first failed
  precondition, and a replanning trigger. An unknown precondition is unresolved;
  a valid abstract sequence does not establish implementation success. Skip
  this model for a routine checklist or a dependency DAG whose prerequisites
  are already explicit and directly checked.
- Use [mathematical optimization](../foundations-mathematical-optimization/SKILL.md)
  when indivisible work selections compete for quantified capacity, budget, or
  other hard constraints and a greedy ranking may miss feasible combinations.
  Return variables/domains, objective and coefficient provenance, constraints,
  a feasible selection, and method/bound/gap status. Preserve indivisibility;
  a continuous relaxation is a bound, not an executable allocation. Skip for
  ordinary qualitative prioritization or when inputs cannot support a model;
  document the unresolved tradeoff instead. This skill still owns execution,
  ownership, verification, and checkpoints.

### Context and Session Discipline

- give each worker a self-contained brief and record whether it starts fresh or forks parent history; "worker" alone does not guarantee a fresh or full window (same rule as [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md))
- persist plan, progress, and decisions in files or stable task artifacts
- keep one bounded outcome per session where possible
- if repeated retries or re-reads appear, rescope instead of brute-forcing

### Scope-Creep Detection

Scope creep is easier to catch early than to unwind late. Check for these signals at every checkpoint:

- The task now touches files or systems not named in the original plan contract, and no one decided that on purpose.
- New acceptance criteria appear mid-implementation that were not in the original success criteria ("while we're in here, let's also...").
- A "quick fix" step balloons into a refactor because the agent (or a human) noticed adjacent bad code.
- The verification plan keeps growing to cover things the original scope never promised.
- Estimated remaining work keeps resetting to "almost done" across multiple checkpoints without net progress.

Response: do not silently absorb the addition into the current session. Name it explicitly, then either (a) re-scope the plan contract and tell the human what changed and why, or (b) split it into a follow-up milestone and keep the current session's original success criteria intact. Absorbing scope without renegotiating the contract is how a bounded task becomes an unbounded one.

### Output Format for Plan Documents

Keep acceptance criteria parseable in a version-controlled plan. For document format choices, use [docs-ai-prd](../docs-ai-prd/SKILL.md).

### Test Context and Verification

- include `source -> tests` context for the affected area
- use the best available approximation if a full dependency graph is unavailable
- require exact verification commands or review evidence in the handoff
- before implementing a bug fix or new behavior, apply its class's test-first rule ([Change Classes](#change-classes-and-first-moves)): record the failure or gap on the current code, then show it passes after the change
- for a behavior-preserving refactor or safety change, name the single fact that makes it safe and prove it by running the real code path, not by reading the diff; run relevant existing checks before and after as regression baselines, and add a focused check or review for any risk those checks don't cover
- if spec or contract validation is unavailable, say so instead of claiming it passed

## Multi-session Planning State

For work that will cross a session boundary, choose the smallest existing durable artifact that preserves the goal, decisions, verified progress, and next bounded action. [Multi-session planning state](references/long-horizon-journaling.md) gives two optional layouts for exploratory and bounded implementation work. Use [ai-coding-agents-state](../ai-coding-agents-state/SKILL.md) for autonomous loop termination and [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md) for multi-wave dispatch.

## Known Traps

- Writing a plan that decomposes work but never states the decision boundary, success criteria, or explicit stop condition.
- Running parallel workers on overlapping files or unstable interfaces because the task list looked independent on paper.
- Treating "needs tests" as a sufficient verification plan when the task actually needs concrete commands, datasets, or manual review checkpoints.
- Persisting too little state, which forces later sessions to reconstruct intent and status from chat instead of durable artifacts.
- Keeping the original scope after repeated retries and confusion instead of shrinking the outcome to something still verifiable.

- Treating a known bug, regression, or framework/compiler/runtime footgun as current fact without checking it against a primary web source; version-specific crash or workaround guidance decays fast.
- Asserting a platform-specific workflow claim, planning surface, or product limit as current behavior without verifying it against primary documentation for Claude Code, Codex, GitHub, or the relevant workflow tooling.

## Common Anti-Patterns

- Producing full-spec planning overhead for low-risk work that should have been executed directly.
- Splitting work into many tiny tasks without ownership, dependency, or rollback logic.
- Handing workers the whole conversation history instead of a bounded task packet and explicit acceptance criteria.
- Claiming a wave is complete before the planned validation gate actually runs.
- Treating the final handoff as narrative summary instead of a precise statement of what changed, what was checked, and what remains.

## Navigation

> Load a foundation only for a named decision gap. Check its apply/skip conditions; when it does not fit, continue the applied workflow or route to an owner only if that owner is needed.

- Planning and platform references: [references/planning-templates.md](references/planning-templates.md), [references/platform-workflows.md](references/platform-workflows.md), [../ai-agents/references/agent-delivery-methods.md](../ai-agents/references/agent-delivery-methods.md)
- Parallelism and recovery: [references/operational-checklists.md](references/operational-checklists.md), [references/session-patterns.md](references/session-patterns.md), [references/session-scope-budgeting.md](references/session-scope-budgeting.md), [references/flow-metrics.md](references/flow-metrics.md), [../ai-agents/references/context-rotation-and-state.md](../ai-agents/references/context-rotation-and-state.md)
- Supporting workflow references: [../product-management/references/agile-ceremony-patterns.md](../product-management/references/agile-ceremony-patterns.md), [../product-management/references/remote-async-workflows.md](../product-management/references/remote-async-workflows.md), [../product-management/references/technical-debt-management.md](../product-management/references/technical-debt-management.md), [../qa-agent-testing/references/coding-agent-regression-testing.md](../qa-agent-testing/references/coding-agent-regression-testing.md), [data/sources.json](data/sources.json)
- Spec-driven tooling and workflow: [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md)
- Foundations: [../foundations-theory-of-constraints/SKILL.md](../foundations-theory-of-constraints/SKILL.md) — bottleneck identification, WIP limits, and T/CU throughput accounting underlying flow-metrics.md and the product-management technical-debt-management.md
- Templates: [../product-management/assets/ops/template-dor-dod.md](../product-management/assets/ops/template-dor-dod.md), [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md), [assets/template-milestone-checkpoint.md](assets/template-milestone-checkpoint.md), [assets/example-medium-plan-contract.md](assets/example-medium-plan-contract.md) (worked medium-size plan-contract example)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
