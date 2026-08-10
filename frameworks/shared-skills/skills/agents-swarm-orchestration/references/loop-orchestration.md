# Loop Orchestration

## Table of Contents

- [Bounded Iteration Is Not Retry](#bounded-iteration-is-not-retry)
- [When A Loop Beats A Wave](#when-a-loop-beats-a-wave)
- [The Four Loop Shapes](#the-four-loop-shapes)
- [Termination Is The Design](#termination-is-the-design)
- [Loop-Until-Dry](#loop-until-dry)
- [Budget-Bounded Loops](#budget-bounded-loops)
- [Convergence Detection](#convergence-detection)
- [Dedup Target Rule](#dedup-target-rule)
- [Runtime Surfaces For Loops](#runtime-surfaces-for-loops)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

Where [operational-guardrails.md](operational-guardrails.md) covers stop conditions for a **wave** of workers, this reference covers **iteration**: orchestration that repeats a step until a convergence condition is met rather than executing a fixed dependency graph once. Where [../../ai-agents/references/autonomous-loop-patterns.md](../../ai-agents/references/autonomous-loop-patterns.md) covers Shape C deployment (a long-running process invoking an agent against a PRD, framework-neutral), this file covers loops **inside a Claude Code or Codex orchestration run**.

## Bounded Iteration Is Not Retry

The SKILL's [§Escalation Over Retry](../SKILL.md#escalation-over-retry) rule — *retry the same approach at most once* — remains correct and is not relaxed here. It governs **failure handling**: a worker that failed should not be re-run hoping for a different outcome, because recurring failure is structural.

Bounded iteration is a different regime. The step is not failing. It is **succeeding partially**, and each pass consumes work that the previous pass surfaced.

| | Retry | Bounded iteration |
|---|---|---|
| Trigger | Worker failed | Worker succeeded, output incomplete |
| Each pass | Same input, same approach | New input derived from prior output |
| Expected passes | 1 (then escalate) | Until convergence or budget |
| Success signal | Task completes | Marginal yield → 0 |
| Failure mode | Masking a structural bug | Never terminating |

Stating the distinction explicitly matters because a lead that has internalized "do not loop" will serialize work that should iterate — running one finder pass over a codebase and reporting the first N bugs as if they were all of them.

**Rule:** if a second pass would consume *different* input than the first, it is iteration, not retry.

## When A Loop Beats A Wave

Use a loop only when the work has **unknown extent**. A wave is correct when you can enumerate the task list before dispatch; a loop is correct when enumerating the list *is* the work.

Use a loop when:

- The item count is unknown and discovery is part of the job (bug hunts, dead-code sweeps, undocumented-endpoint audits).
- Each pass reveals the next pass's input (dependency chasing, transitive migration, citation following).
- Quality is gated by a check that can fail more than once for legitimate, *different* reasons (evaluator-optimizer content).

Do **not** use a loop when:

- The task list is enumerable up front — dispatch a wave; it is cheaper and bounded by construction.
- The termination criterion cannot be written as an observable predicate. "Until it's good" is not a criterion.
- Each iteration is irreversible (money movement, external posts, destructive migrations). Irreversibility plus iteration is the highest-blast-radius combination in this skill.
- One strong model on full context would out-perform the loop at equal budget — see the Data Processing Inequality caveat in [../SKILL.md](../SKILL.md#known-traps).

## The Four Loop Shapes

| Shape | Termination | Typical use | Cost profile |
|---|---|---|---|
| **Loop-until-dry** | K consecutive passes yield nothing new | Unknown-size discovery: bugs, edge cases, dead code | Unbounded without K and a hard cap |
| **Evaluator-optimizer** | Evaluator gate passes, or retry cap hit | Quality hard to verify deterministically | 2 agents/pass; cap at 2–3 |
| **Budget-bounded sweep** | Token or wall-clock budget exhausted | "Be as thorough as the budget allows" audits | Predictable by construction |
| **Fixed-count refinement** | N passes completed | Known-depth polish where N is justified | Fully predictable; weakest guarantee |

Name the shape when proposing a design. An unnamed loop is one whose termination nobody has checked.

## Termination Is The Design

A loop's specification **is** its termination criterion. Write it before writing the loop body, as an observable predicate over state the orchestrator can read:

```text
TERMINATION: <predicate>            # e.g. "2 consecutive rounds add 0 new findings"
HARD CAP:    <count or budget>      # always present, even when the predicate looks safe
ON CAP HIT:  <halt | escalate>      # never "continue anyway"
PROGRESS:    <what must change>     # what makes pass N+1 different from pass N
```

The `HARD CAP` is non-negotiable and independent of the predicate. A convergence predicate can be wrong — a finder that hallucinates a new finding each round never goes dry. The cap is what makes that failure bounded instead of unbounded.

`ON CAP HIT` must be `halt` or `escalate`. A loop that logs a warning and continues has no cap.

## Loop-Until-Dry

The default shape for unknown-size discovery. Simple counters (`while count < N`) systematically miss the tail: they stop at a number chosen before anyone knew the real extent.

```text
seen = {}                      # keys of everything ever surfaced
confirmed = []
dry = 0

while dry < K and rounds < HARD_CAP:
    found  = <dispatch finder wave>
    fresh  = [f for f in found if key(f) not in seen]

    if not fresh:
        dry += 1
        continue

    dry = 0
    seen.update(key(f) for f in fresh)      # BEFORE verification
    confirmed += [f for f in fresh if <verify f>]
```

`K = 2` is the usual default: one empty round is weak evidence (finder variance), two is reasonable. Raise K for high-stakes sweeps, never lower it to 1.

Dispatch each round as a normal wave under existing rules — worker caps, budgets, ownership, structured reports all still apply. The loop wraps wave dispatch; it does not replace it.

## Budget-Bounded Loops

When thoroughness should scale with an explicit budget rather than a discovered condition, gate on remaining budget:

```text
while budget_total and budget_remaining() > PER_PASS_RESERVE:
    <dispatch pass>
```

Two invariants:

- **Guard on the budget existing.** With no budget set, `remaining()` is effectively infinite and the loop runs to the agent cap. This is the most common way a budget-bounded loop becomes an unbounded one.
- **Reserve headroom.** Stop while enough budget remains to synthesize. A loop that spends its last token discovering has nothing left to report with.

Budget-conservation still holds: child budgets are strict subsets of the parent's *remaining* budget, and a breach halts rather than warns (see [../SKILL.md](../SKILL.md#operating-principles)).

## Convergence Detection

Distinguish three states a loop can be in. Only the first is a reason to stop early.

| State | Signal | Action |
|---|---|---|
| **Converged** | K consecutive rounds add nothing new | Stop — the intended exit |
| **Stagnant** | Rounds produce output, but it duplicates prior rounds under a different label | Stop and flag — dedup key is too narrow |
| **Diverging** | Each round adds items with no overlap and no decreasing trend | Stop and escalate — likely hallucinating, or scope is wrong |

Stagnation is the one to instrument. It looks like progress in the logs (non-empty rounds) while yielding nothing. Detect it by tracking the *fresh* rate, not the found rate: if `len(fresh) / len(found)` trends to zero while `len(found)` stays flat, the loop is stagnant regardless of what the round counter says.

## Dedup Target Rule

**Deduplicate against everything ever seen, never against what survived verification.**

This is the single most common loop bug. If `seen` is populated only from confirmed findings, every item the verifier rejected reappears next round, gets re-verified, gets rejected again — and the loop never goes dry. It burns full budget producing the same rejected output repeatedly.

Add to `seen` at the moment an item is *surfaced*, before it is judged. A rejected finding is still a finding you have already spent tokens on.

Dedup is plain orchestrator-side code, not an agent call. Deciding whether two strings are the same key is a deterministic transform — routing it through a model produces a flaky comparison at token cost, and the answer drifts round to round. (Coding Behavior Rule 5.)

## Runtime Surfaces For Loops

| Surface | Runtime | Loop control lives in | Notes |
|---|---|---|---|
| Workflow script | Claude Code | JavaScript `while` / `for` in the script | Deterministic; strongest option — see [scripted-workflows.md](scripted-workflows.md) |
| Lead-thread iteration | Both | Model's turn-by-turn judgment | Weakest termination guarantee; the model must choose to stop |
| Hook-enforced caps | Both | Runtime, outside the agent | Agent cannot opt out — see [../../agents-hooks/references/budget-and-loop-hooks.md](../../agents-hooks/references/budget-and-loop-hooks.md) |
| External driver | Both | Shell / Python / Temporal wrapper | Survives session death; see [../../ai-agents/references/autonomous-loop-patterns.md](../../ai-agents/references/autonomous-loop-patterns.md) |

Prefer the highest surface that fits: script-held loops beat model-held loops because the termination predicate is code rather than an intention. Pair any model-held loop with hook-enforced caps — instructions decay as context grows; hook code does not.

Codex CLI has no code-mode loop primitive; loops there are lead-thread iteration or an external driver. See [../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md](../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md) for the full runtime comparison.

## Anti-Patterns

| Mistake | Fix |
|---|---|
| Loop with no hard cap because the predicate "obviously" terminates | Every loop gets a cap independent of its predicate |
| Dedup against confirmed results | Dedup against everything surfaced, pre-verification |
| `while count < N` for unknown-extent discovery | Loop-until-dry with K consecutive empty rounds |
| Model decides when to stop, with no enforced ceiling | Add hook-enforced iteration and budget caps |
| Budget loop with no guard on budget being set | `while budget_total and remaining() > reserve` |
| Silent truncation at a top-N cap | Log what was dropped; unreported caps read as full coverage |
| Treating a failing step as a loop | Failure escalates after one retry; only partial success iterates |
| Calling a model to compare dedup keys | Deterministic transform — use code |
| Iterating irreversible operations | Never; approval-gate each one instead |
| No progress definition — pass N+1 same input as pass N | Declare `PROGRESS` before writing the loop |

## Validation Checklist

- [ ] Loop shape is named (dry / evaluator-optimizer / budget-bounded / fixed-count).
- [ ] Termination predicate is written as an observable condition over readable state.
- [ ] Hard cap exists and is independent of the predicate.
- [ ] `ON CAP HIT` is halt or escalate — never continue.
- [ ] `PROGRESS` is defined: what makes each pass differ from the last.
- [ ] Dedup targets everything surfaced, not everything confirmed.
- [ ] Stagnation detection tracks fresh-rate, not found-rate.
- [ ] Per-pass worker budgets set; run-level cumulative cap set.
- [ ] Loop control sits in script or hooks where the runtime allows, not model judgment alone.
- [ ] Any coverage cap that truncates results is logged, not silent.
- [ ] Loop is confirmed as iteration (different input per pass), not disguised retry.

## Cross-References

- Scripted deterministic control flow: [scripted-workflows.md](scripted-workflows.md)
- Wave dispatch, ownership, worker budgets: [../SKILL.md](../SKILL.md#dispatch-workflow)
- Stop conditions and verification gates: [operational-guardrails.md](operational-guardrails.md)
- Cumulative cost circuit-breakers: [cost-discipline.md](cost-discipline.md)
- Hook-enforced iteration and budget caps: [../../agents-hooks/references/budget-and-loop-hooks.md](../../agents-hooks/references/budget-and-loop-hooks.md)
- Shape C autonomous loops (PRD-driven, framework-neutral): [../../ai-agents/references/autonomous-loop-patterns.md](../../ai-agents/references/autonomous-loop-patterns.md)
- Evaluator-optimizer pattern detail: [../../agents-subagents/references/harness-patterns.md](../../agents-subagents/references/harness-patterns.md)
- Runtime loop-surface comparison: [../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md](../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md)
