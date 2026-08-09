---
name: dev-workflow-planning
description: "Plans complex development workflows for Claude Code, Codex, and assistants. Use when breaking features, refactors, migrations, or parallel work into verified steps."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Dev Workflow Planning

Use this skill to turn vague or risky engineering work into a bounded execution plan with scope, sequencing, checkpoints, verification, and handoff. It owns planning depth, execution shape, and multi-agent guardrails, not system design, PRD authoring, or branch-policy decisions.

## Quick Reference

| Task | Use |
|------|-----|
| Plan structures and artifacts | [references/planning-templates.md](references/planning-templates.md), [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md), [assets/template-milestone-checkpoint.md](assets/template-milestone-checkpoint.md), [assets/template-dor-dod.md](assets/template-dor-dod.md) |
| Platform-specific workflow mapping | [references/platform-workflows.md](references/platform-workflows.md), [../ai-agents/references/agent-delivery-methods.md](../ai-agents/references/agent-delivery-methods.md) |
| Guardrails for parallelism, sessions, and recovery | [references/operational-checklists.md](references/operational-checklists.md), [references/session-patterns.md](references/session-patterns.md), [references/session-scope-budgeting.md](references/session-scope-budgeting.md), [../ai-agents/references/context-rotation-and-state.md](../ai-agents/references/context-rotation-and-state.md) |
| Spec-driven tooling landscape (GitHub Spec Kit, Kiro, BMAD) | [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md) |
| Test-context planning | [../qa-agent-testing/references/coding-agent-regression-testing.md](../qa-agent-testing/references/coding-agent-regression-testing.md) |
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
- Use fresh-context workers and explicit file ownership when running parallel waves.
- Include targeted test context for affected code instead of generic "write tests first" instructions.

## Workflow

1. Confirm the goal, in-scope boundary, success criteria, and missing inputs.
2. Choose the planning depth: trivial, lightweight, full plan contract, or spec-driven.
3. Lock the plan contract: goal, scope, dependencies, execution order, verification, and rollback.
4. Choose execution shape: sequential or dependency-based waves.
5. Run bounded batches with verification between waves and checkpoint state in durable artifacts.
6. End with a handoff that states what is done, what is not, what was checked, and the next bounded action.

## ASCII Flow

```text
development planning request
  -> confirm goal, scope, success criteria, and missing inputs
  -> choose planning depth: trivial, lightweight, full contract, or spec-driven
  -> define dependencies, ownership, sequence, verification, and rollback
  -> choose execution shape
     +-- sequential -> overlapping files or moving interfaces
     +-- waves -> independent file ownership and stable interfaces
  -> run batches with validation between waves
  -> checkpoint decisions in durable artifacts
  -> hand off done, not done, checked, and next action
```

## Core Decisions

### Planning Depth

| Complexity | Depth | Artifact | Trigger |
|---|---|---|---|
| Single-file, obvious outcome | trivial | none or one-liner | direct execution |
| Multi-step, clear scope | low | goal + steps + verification | 2-5 files, no shared interfaces |
| Multi-file, overlapping interfaces | medium | full plan contract with file ownership | 3+ files, schema or API changes |
| Multi-agent, long-horizon, or spec-required | high | spec → design → tasks → implementation | production-touching, unknown dependencies |

### When to Spec vs Prototype

| Choose spec-driven | Choose prototype-first |
|---|---|
| Spec required before agent execution (Kiro, Spec Kit workflow) | Throwaway scaffold, demo, or unknown-unknowns spike |
| Multi-agent handoffs with acceptance criteria | Single-session, one dev, no handoffs |
| Requirements must survive context resets | Goal will change within the same session |
| AI agent downstream will re-parse the contract | Human drives all decisions interactively |

Over-planning burns time; under-planning creates rework.

**Judgment call:** the deciding question is not "how big is this task" but "is the missing information discoverable by more upfront analysis, or only by executing and observing?" If a spike, prototype, or a single read-only exploration pass would resolve the open question faster than writing a fuller plan contract, do that first and treat the plan as provisional until it returns. Choosing planning depth from task size alone, while ignoring where the actual uncertainty lives, produces plans that are either padded with guesses on the unknowable parts or confidently wrong on the one thing that mattered.

### Estimation in the AI-Coding Era

AI coding agents shift the bottleneck from typing speed to decision quality, review bandwidth, and verification cost. Estimating in story points or hours calibrated to human typing speed will misprice the work:

- Re-anchor the estimate to review and verification burden, not generation time. A 200-line AI-generated diff across three files with a stable interface can take minutes to produce and hours to review safely — the review time is the real constrained resource, not the generation time.
- Spec-writing and clarification time now dominates for ambiguous work. An underspecified prompt costs more in rework cycles than the original round of AI-assisted execution saved; budget explicit time for the interview/clarification phase (see [Pre-loop setup phase](#pre-loop-setup-phase-both-variants)) instead of folding it into "implementation."
- Do not let apparent AI generation speed compress the estimate for irreversible or high-blast-radius work (schema migrations, auth, billing, public APIs). Generation is fast; the safe-rollout and verification path is not, and estimating on generation speed alone under-scopes the plan.
- A plausible-looking AI-generated diff is not evidence of correctness. Budget the same verification rigor for AI-generated code as for human-written code of the same risk class — a clean diff creates false confidence, not a discount on review time.
- Treat pre-AI-agent historical velocity or throughput baselines as unreliable comparators for estimation. Recalibrate against the team's own current throughput on AI-assisted work rather than carrying forward last year's per-story averages.

### Plan Mode (Claude Code)

- Enter with `/plan` (added Jan 2026), `Shift+Tab` twice, or `--permission-mode plan` at startup.
- Plan mode is read-only: Claude reads and reasons but cannot write files or run side-effecting commands.
- `/ultraplan` hands the plan off to a cloud session that runs multiple agents in parallel and returns a structured plan for review — it is a research-preview feature gated to paid plans, not a "slower but deeper" mode. Verify current requirements (subscription tier, CLI version) before recommending it, since research-preview gating changes fast.
- For changes touching 3+ files, schema, or security-sensitive code: always enter plan mode first.
- Plan mode's real saving is avoiding trial-and-error rework tokens (wrong-direction edits, failed builds, redundant re-reads). Expect a meaningful reduction on complex, ambiguous tasks — but do not quote a specific percentage as fact unless you have checked it against a current first-party source; blog-post figures in this space vary widely and are not authoritative.

### Execution Model

- sequential by default when risk or overlap is high
- wave-based parallelism only when tasks are truly independent
- explicit `depends_on`, shared-interface definitions, and one validation pass between waves
- stop parallelism once interface churn or file overlap appears

### Context and Session Discipline

- each worker should get fresh context, not the full conversation history
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

Plans default to markdown, but multi-step plans intended for human review often outgrow markdown's usefulness. Choose deliberately:

- **Markdown** — default for plans an agent will re-ingest, for short plans (≤100 lines), and for plans living in version control where clean diffs matter.
- **HTML** — preferred when the plan is >100 lines, needs visual structure (data flow diagrams, mockups, side-by-side option comparisons, annotated code snippets), or will be shared via link to non-technical stakeholders. Author reports humans rarely read past ~100 lines of markdown; HTML invites reading.

Cost: HTML plan generation is **2–4× slower** than markdown and produces noisy version-control diffs. The tradeoff is worth it for read-once human-facing plans; not worth it for agent-consumed context.

For exploration plans (multi-option, mockup-heavy), HTML's grid layout with per-option tradeoff labels outperforms a linear markdown bullet list. For multi-step implementation plans handed off to an agent, keep the *acceptance criteria* in a parseable table or code block even inside an HTML artifact — the implementation agent needs binary, extractable success conditions.

For interactive plan artifacts (drag-drop prioritization, form-based config), always end with a *"copy as markdown / JSON / prompt"* export button so the human's UI manipulation closes back into pasteable text. See [`../docs-ai-prd/SKILL.md#output-format-html-vs-markdown-for-spec-artifacts`](../docs-ai-prd/SKILL.md) for the full format-selection table.

Source: [Thariq, *Using Claude Code: The Unreasonable Effectiveness of HTML*](https://x.com/trq212/status/2052809885763747935) (Claude Code team, 2026-05-08).

### Test Context and Verification

- include `source -> tests` context for the affected area
- use the best available approximation if a full dependency graph is unavailable
- require exact verification commands or review evidence in the handoff
- if spec or contract validation is unavailable, say so instead of claiming it passed

## Long-Horizon Agent Journaling

For agent runs spanning hours or days (goal-mode loops, scheduled Routines, multi-session refactors), in-memory compaction is not sufficient — the agent loses coherence on the timescale of long-running work. Force state to the filesystem using role-separated markdown files. Two patterns exist, optimized for different domains. Pick by domain, do not blend them.

### Variant selector

| Your work is… | Use this variant | Why |
|---|---|---|
| **Exploratory** — running experiments, searching architectures, trying many options, learning from dead ends | [Hayduk 3-file](#variant-1-hayduk-3-file-exploratory) | Curated `EXPERIMENTS.md` separates re-readable history from append-only scratchpad; agent reasons about past attempts |
| **Bounded product building** — known target, ambiguity must be resolved upfront, then execute coherently | [Watts 4-file](#variant-2-watts-4-file-bounded-product) | `STANDARDS.md` and `PROGRESS.md` keep multi-agent execution aligned across context resets |

The patterns are **not contradictory** — they target different shapes of long-horizon work. If a run is exploratory in early stages and execution-heavy later, you can transition from the Hayduk variant to the Watts variant; do not run both simultaneously.

### Variant 1 — Hayduk 3-file (exploratory)

| File | Role | Lifecycle |
|------|------|-----------|
| `PLAN.md` | High-level plan + intended direction. Seedable with human-provided initial ideas. | Read often; rewritten when direction shifts |
| `EXPERIMENTS.md` | Curated table of attempts: title, what was tried, what happened, why it did or didn't work. The *re-readable* history. | Append-only with periodic curation; entries earn their place |
| `EXPERIMENT_NOTES.md` | Chronological scratchpad: raw thoughts as the agent runs. The *audit trail*. | Append-only, never curated |

Key invariant: `EXPERIMENTS.md` is for re-reading (by both agent and human), `EXPERIMENT_NOTES.md` is for write-only logging. Conflating them is the failure mode.

Source: Chris Hayduk (OpenAI), [*Using Codex Goals Effectively*](https://x.com/ChrisHayduk/status/2053807198870880743) (2026-05-11), reporting on multi-day Codex `/goal` runs for ML architecture search.

### Variant 2 — Watts 4-file (bounded product)

| File | Role | Lifecycle |
|------|------|-----------|
| `GOAL.md` | Top-level objective written after a heavy interview/clarification phase. The thing being built, not the path to it. | Stable; rewritten only when scope genuinely shifts |
| `STANDARDS.md` | Non-negotiable code-quality standards, conventions, and acceptance criteria the agent and its subagents must respect | Mostly stable; updated when standards evolve |
| `IMPLEMENT.md` | Workflow instructions: how to delegate (implementer + reviewer subagents), how to verify work, when to spawn parallel teams, what passes a review | Stable; updated when the orchestration recipe changes |
| `PROGRESS.md` | Continuously updated log of decisions made, work completed, milestones passed | Append-only; new agents read this first to inherit context |

New agents (or new context windows after compaction) read all four files before acting, inheriting both the *what* (GOAL + STANDARDS) and the *how* (IMPLEMENT + PROGRESS). The split prevents orchestrator-vs-subagent drift across long runs.

Source: Jarrod Watts, [*You Need More Than a Ralph Loop*](https://x.com/jarrodwatts/status/2052372045829382430) (2026-05-07), packaged as the [long-running-agent-skill](https://github.com/jarrodwatts/long-running-agent-skill) on GitHub (includes git-worktrees parallelization for subagent teams).

### Pre-loop setup phase (both variants)

Watts's critical addition: invest heavily **before** the loop in an interview phase that surfaces 20–50 clarifying questions. Ambiguity in the prompt compounds across iterations — each loop's output becomes the next loop's input, so one underspecified decision direction-shifts everything downstream.

The interview phase is brainstorming/clarification work, not journaling. Use the `superpowers:brainstorming` skill (invoke via the Skill tool; it is a plugin skill, not a file in this repo) or an equivalent `/interview`-style command to drive question-led discovery before any long-horizon run. The questions force *the human* to make decisions instead of leaving them implicit; the resulting `GOAL.md` or `PLAN.md` is dramatically tighter than what a single-prompt seed produces.

#### Interview mechanic: one question at a time with an attached guess

**Scope note:** this mechanic targets underspecified *ad hoc requests from a human* — the setup phase above, or any planning intake where the goal is still fuzzy. It does not apply to agent-to-agent work inside an already-scoped skill or task packet (fresh-context workers, wave-based delegation, orchestrator-to-subagent handoff) — those contexts already carry a bounded contract and should not re-run an interview loop against another agent. For batched clarification across a multi-member team, see [`../agents-subagents/references/clarification-questions-protocol.md`](../agents-subagents/references/clarification-questions-protocol.md) instead — that protocol collects up to ~3 questions per member and dedupes them into one relay to the human; it is a different mechanic (batched, multi-agent) from the one below (sequential, single-agent-to-human).

When the request is underspecified, do not open with an open-ended clarifying-question list. Instead:

1. State a one-sentence hypothesis about what the human wants, with an honest numeric confidence score (e.g. "My guess: you want X because Y — confidence 40%").
2. Ask exactly **one** question at a time, and attach your own guessed answer to it. The human corrects a guess faster than they compose an answer from scratch.
3. Wait for the human's reaction before asking the next question. Do not queue multiple questions in one turn.
4. Watch for "want vs. should-want" answers — buzzword-driven responses like "scalable" or "modern" describe an aspiration, not a constraint. Probe past them: ask what breaks today without it, or what "scalable" needs to hold up to, concretely.
5. Stop only when the stop condition is checkable, not a vibe: **can you predict the human's reaction to the next three questions you would ask?** If yes, stop asking and restate. If no, keep asking one at a time.
6. Close with a restate — Outcome / User / Why now / Success / Constraint / Out of scope — and require an explicit **"yes"** before proceeding. "Sounds good," a thumbs-up, or silence is not consent. "Whatever you think is best" is explicitly **not** consent either — treat it as a deflected question and ask a narrower, more concrete version of the same question instead of proceeding on it.

This is a sharper alternative to batching every clarifying question into one message: an attached guess gives the human something to react to instead of a blank field to fill in, and the falsifiable stop test (predicting the next three reactions) replaces "I think I've asked enough" with a checkable condition.

Source: Addy Osmani, [`interview-me` skill](https://github.com/addyosmani/agent-skills/blob/7676817c12a1317454ae3898a0c5c1eacf5dd3d5/skills/interview-me/SKILL.md), commit `7676817`, MIT license. Extracted 2026-08-09.

### When to apply (either variant)

- Goal-mode or autonomous loops with no human in the inner cycle
- Any agent run expected to exceed one compaction window
- Multi-agent runs where context resets across orchestrator-vs-subagent boundaries

### When to skip

- Short, single-session tasks — the planning artifacts in `assets/` already cover these
- Tasks with a single deterministic verification step — no history to preserve
- Bare prototype scripts where ambiguity costs little

### Related

- Goal-mode loop semantics that drove these patterns: [`../ai-coding-agents-tasks/SKILL.md#goal-mode-loops-codex-goal-and-analogues-2026-05`](../ai-coding-agents-tasks/SKILL.md)
- Orchestrator + implementer + reviewer triad for multi-agent execution: [`../agents-swarm-orchestration/SKILL.md`](../agents-swarm-orchestration/SKILL.md)
- Pre-loop interview-driven clarification: `superpowers:brainstorming` skill
- Batched multi-agent clarifying questions (different mechanic — sequential single-agent-to-human vs. batched multi-member): [`../agents-subagents/references/clarification-questions-protocol.md`](../agents-subagents/references/clarification-questions-protocol.md)

## Known Traps

- Writing a plan that decomposes work but never states the decision boundary, success criteria, or explicit stop condition.
- Running parallel workers on overlapping files or unstable interfaces because the task list looked independent on paper.
- Treating "needs tests" as a sufficient verification plan when the task actually needs concrete commands, datasets, or manual review checkpoints.
- Persisting too little state, which forces later sessions to reconstruct intent and status from chat instead of durable artifacts.
- Keeping the original scope after repeated retries and confusion instead of shrinking the outcome to something still verifiable.

## Common Anti-Patterns

- Producing full-spec planning overhead for low-risk work that should have been executed directly.
- Splitting work into many tiny tasks without ownership, dependency, or rollback logic.
- Handing workers the whole conversation history instead of a bounded task packet and explicit acceptance criteria.
- Claiming a wave is complete before the planned validation gate actually runs.
- Treating the final handoff as narrative summary instead of a precise statement of what changed, what was checked, and what remains.

## Navigation

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- Planning and platform references: [references/planning-templates.md](references/planning-templates.md), [references/platform-workflows.md](references/platform-workflows.md), [../ai-agents/references/agent-delivery-methods.md](../ai-agents/references/agent-delivery-methods.md)
- Parallelism and recovery: [references/operational-checklists.md](references/operational-checklists.md), [references/session-patterns.md](references/session-patterns.md), [references/session-scope-budgeting.md](references/session-scope-budgeting.md), [references/flow-metrics.md](references/flow-metrics.md), [../ai-agents/references/context-rotation-and-state.md](../ai-agents/references/context-rotation-and-state.md)
- Supporting workflow references: [references/agile-ceremony-patterns.md](references/agile-ceremony-patterns.md), [references/remote-async-workflows.md](references/remote-async-workflows.md), [references/technical-debt-management.md](references/technical-debt-management.md), [../qa-agent-testing/references/coding-agent-regression-testing.md](../qa-agent-testing/references/coding-agent-regression-testing.md), [data/sources.json](data/sources.json)
- Spec-driven tooling and workflow: [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md)
- Foundations: [../foundations-theory-of-constraints/SKILL.md](../foundations-theory-of-constraints/SKILL.md) — bottleneck identification, WIP limits, and T/CU throughput accounting underlying flow-metrics.md and technical-debt-management.md
- Templates: [assets/template-dor-dod.md](assets/template-dor-dod.md), [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md), [assets/template-milestone-checkpoint.md](assets/template-milestone-checkpoint.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify platform-specific workflow claims, current planning surfaces, and product limits before presenting them as current behavior.
- Prefer primary documentation for Claude Code, Codex, GitHub, and related workflow tooling.
- If live verification is unavailable, mark platform-specific guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

