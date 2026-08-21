# Scripted Workflows — Deterministic Control Flow

## Table of Contents

- [What Changes When The Script Holds The Loop](#what-changes-when-the-script-holds-the-loop)
- [When To Reach For A Script](#when-to-reach-for-a-script)
- [Core Primitives](#core-primitives)
- [Barrier vs Pipeline](#barrier-vs-pipeline)
- [Structured Output Contracts](#structured-output-contracts)
- [Composing Loops With Fan-Out](#composing-loops-with-fan-out)
- [Determinism Constraints](#determinism-constraints)
- [Resume And Caching](#resume-and-caching)
- [Cost And Scale Ceilings](#cost-and-scale-ceilings)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

Where [../SKILL.md](../SKILL.md) covers dispatch where the **lead model decides** each wave turn by turn, this reference covers orchestration where **a script decides** and the model only executes leaf tasks. This is the third execution surface — distinct from both isolated subagents and agent teams.

Runtime-specific: Claude Code **dynamic workflows** — the official name for this surface (shipped 2026-05-28 with Opus 4.8; CLI v2.1.154+). Scripts live as JavaScript files in `.claude/workflows/`, which makes this the repeatable, version-controllable orchestration artifact: subagent and team dispatch are per-run decisions, a workflow script is a committed one. Codex CLI has no equivalent code-mode primitive as of v0.137 — see [../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md](../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md). Verify against current release notes before committing; this surface is young and moving.

## What Changes When The Script Holds The Loop

In standard fan-out the lead is both planner and scheduler: it reads worker reports into its own context, decides what runs next, and pays context cost for every intermediate result. Scripted workflows split those roles.

| | Model-held control flow | Script-held control flow |
|---|---|---|
| Who decides what runs next | Lead model, each turn | Code — loops, conditionals |
| Intermediate results | Enter lead context | Stay in script variables |
| Reproducibility | Varies run to run | Same script + same inputs → same shape |
| Lead context cost | Grows with every worker report | Holds only the final return value |
| Best for | Ambiguous, judgment-heavy routing | Known structure, many items |

The context property is the main prize. A 200-item sweep through a model-held loop puts 200 reports into the lead's window and degrades as it fills. The same sweep in a script keeps the lead's context at roughly the size of the final synthesis, because intermediate results live in JavaScript variables the lead never reads.

**Corollary:** scripts are worth reaching for exactly when intermediate volume is high relative to final-answer volume. For three workers reporting once, the script is overhead.

## When To Reach For A Script

Use a scripted workflow when the control flow is knowable in advance:

- **Fan-out over a discovered work-list** — scout inline first to find the items, then script the pipeline over them. This hybrid is usually right: you do not need to know the shape before the *task*, only before the *orchestration step*.
- **Multi-stage per-item processing** — each item flows find → verify → summarize independently.
- **Loop-until-dry / budget-bounded sweeps** — the termination predicate is code, giving the strongest possible guarantee (see [loop-orchestration.md](loop-orchestration.md)).
- **Scale one context cannot hold** — migrations, audits, portfolio sweeps.

Do **not** use a script when:

- The next step genuinely depends on judgment about the last step's content. That is what the lead model is for.
- The task is a handful of workers reporting once — orchestration cost exceeds execution cost.
- The work is conversational or exploratory, where the human redirects mid-run.

## Core Primitives

Three functions carry nearly all workflow scripts:

| Primitive | Semantics | Returns |
|---|---|---|
| `agent(prompt, opts)` | Spawn one subagent | Final text, or a validated object when `schema` is given |
| `parallel(thunks)` | Run all concurrently, **wait for all** | Array, `null` per failed thunk |
| `pipeline(items, ...stages)` | Each item flows through all stages independently | Array of final-stage results |

Notes that matter in practice:

- `parallel()` never rejects. A thunk that throws resolves to `null` in the array. **Filter before use** — `.filter(Boolean)` — or a downstream stage will read properties off `null`.
- `pipeline()` stages receive `(prevResult, originalItem, index)`. Use `originalItem` in later stages for labelling instead of threading context through stage 1's return value.
- A `pipeline` stage that throws drops that item to `null` and skips its remaining stages. One bad item does not abort the run.

## Barrier vs Pipeline

The most consequential choice in a workflow script, and the most commonly wrong.

`pipeline()` is the default. It has **no barrier between stages** — item A can be in stage 3 while item B is still in stage 1. Wall-clock is the slowest single chain, not the sum of slowest-per-stage.

`parallel()` between stages is a **barrier**: nothing advances until everything in the wave finishes. Reach for it only when stage N genuinely needs cross-item context from all of stage N-1:

- Dedup or merge across the full result set before expensive downstream work.
- Early-exit on the aggregate ("zero findings → skip verification entirely").
- Stage N's prompt refers to the other findings for comparison.

A barrier is **not** justified by needing to flatten, map, or filter — do that inside a pipeline stage. The smell test:

```text
const a = await parallel(...)
const b = transform(a)          // no cross-item dependency
const c = await parallel(b.map(...))
```

That middle transform does not need the barrier. Rewrite as a pipeline with the transform as a stage. If the slowest worker takes 3× the fastest, a needless barrier idles the fast ones for two-thirds of the wave.

## Structured Output Contracts

Pass a JSON Schema via `opts.schema` and the subagent is forced to emit a validated object; the model retries on mismatch at the tool-call layer. This replaces the SKILL's structured-report discipline with an enforced version — the lead is no longer parsing prose to decide whether a report conforms.

Schema-validated returns are what make script-side branching safe. Branching on a free-text return means string-matching model prose, which drifts. Branch on typed fields.

Worker-brief discipline still applies inside each `agent()` prompt: owned files, do-not-touch boundaries, deliverable, verification command, self-rejection clause. The script controls *sequencing*; it does not replace *briefing*.

## Composing Loops With Fan-Out

Loop shapes from [loop-orchestration.md](loop-orchestration.md) become literal code here — the strongest available termination guarantee, because the predicate is executed rather than intended:

```text
const seen = new Set(), confirmed = []
let dry = 0

while (dry < 2 && rounds < HARD_CAP) {
    const found = (await parallel(FINDERS.map(f => () =>
        agent(f.prompt, {phase: 'Find', schema: FINDINGS}))))
        .filter(Boolean).flatMap(r => r.findings)

    const fresh = found.filter(f => !seen.has(key(f)))
    if (!fresh.length) { dry++; continue }

    dry = 0
    fresh.forEach(f => seen.add(key(f)))          // pre-verification

    const judged = await parallel(fresh.map(f => () =>
        agent(`Refute: ${f.desc}`, {phase: 'Verify', schema: VERDICT})
            .then(v => ({f, real: v && !v.refuted}))))

    confirmed.push(...judged.filter(Boolean).filter(v => v.real).map(v => v.f))
}
```

Note the barrier inside each round is correct — dedup needs the whole round's findings at once — while the loop itself carries the termination logic. And `seen` takes `fresh` before verification, per the dedup target rule.

## Determinism Constraints

Scripts run in a restricted JavaScript context. The constraints exist to keep runs replayable:

- **No `Date.now()`, `new Date()` (argless), or `Math.random()`** — these throw. They would break resume. Pass timestamps in as arguments; stamp results after the workflow returns. For randomness, vary the prompt or label by index.
- **Plain JavaScript, not TypeScript.** Type annotations, interfaces, and generics fail to parse. This is an easy and silent-looking authoring error.
- **No filesystem or Node APIs.** Standard built-ins (JSON, Math, Array) are available.
- The script body is async — `await` directly.

## Resume And Caching

A run can be resumed after a pause, kill, or script edit. The longest unchanged prefix of `agent()` calls returns cached results instantly; the first edited or new call and everything after it runs live. Same script plus same args means a full cache hit.

This makes iterating on a workflow cheap: edit the persisted script file, re-invoke with the run id, and only the changed tail re-executes.

**Before diagnosing why a completed workflow returned something empty or odd, read the run journal** — it records each agent's actual return value. Do not assume cached results were non-empty; an empty return that was cached will look identical to a step that never ran.

## Cost And Scale Ceilings

| Limit | Value | Consequence |
|---|---|---|
| Concurrent agents | ~16 (min of 16 and cores-2) | Excess queues; 100 items still complete, ~10–16 at a time |
| Total agents per run | 1000 | Runaway-loop backstop, far above real workflows |
| Items per `parallel`/`pipeline` call | 4096 | Explicit error, not silent truncation |

A script can spawn dozens of agents from one instruction. That is precisely why scripted workflows are an **explicit opt-in surface**, not a default: the cost is real, and the user should be the one choosing that scale. Apply the same run-level cumulative circuit-breaker discipline as any other fan-out ([cost-discipline.md](cost-discipline.md)).

Model tiering still applies per `agent()` call. Default to omitting a model override so leaves inherit the session model; set a cheaper tier explicitly for mechanical stages and a stronger one only for the hardest verify or judge stages.

## Anti-Patterns

| Mistake | Fix |
|---|---|
| Barrier between stages with no cross-item dependency | Use `pipeline()`; move the transform into a stage |
| Using `parallel()` results without `.filter(Boolean)` | Failed thunks resolve to `null`, not exceptions |
| Branching on free-text agent returns | Pass a `schema`; branch on typed fields |
| TypeScript annotations in the script | Plain JavaScript only — annotations fail to parse |
| `Date.now()` / `Math.random()` in the script | They throw; pass values in or stamp after return |
| Scripting a three-worker single-round task | Orchestration cost exceeds execution cost; stay in-thread |
| Scripting genuinely judgment-dependent routing | That is the lead model's job |
| Assuming an empty result means a step did not run | Read the journal; cached empties look identical |
| Silent top-N truncation inside a stage | Log what was dropped |
| Treating a script as exempt from worker briefing | Ownership, verification, self-rejection still go in each prompt |

## Validation Checklist

- [ ] Control flow is genuinely knowable in advance — not judgment-dependent.
- [ ] `pipeline()` is the default; every `parallel()` barrier has a named cross-item justification.
- [ ] Every `parallel()` result is `.filter(Boolean)`-ed before use.
- [ ] Agent calls that feed branching carry a `schema`.
- [ ] Each `agent()` prompt still carries owned files, deliverable, and verification.
- [ ] No `Date.now()`, `new Date()`, `Math.random()`, or TypeScript syntax.
- [ ] Loops inside the script carry a hard cap independent of the predicate.
- [ ] Run-level cumulative cost ceiling declared before launch.
- [ ] Any bounded coverage (top-N, sampling, no-retry) is logged, not silent.
- [ ] Scale of fan-out was explicitly chosen by the user, not inferred.

## Cross-References

- Loop shapes, termination, dedup rule: [loop-orchestration.md](loop-orchestration.md)
- Execution-surface selection (thread / worker / team / manager): [execution-surfaces.md](execution-surfaces.md)
- Worker report schema and merge contract: [output-contracts.md](output-contracts.md)
- Cumulative cost ceilings and fan-out economics: [cost-discipline.md](cost-discipline.md)
- CI-safe and blueprint deterministic-plus-agentic flows: [noninteractive-and-blueprints.md](noninteractive-and-blueprints.md)
- Named harness patterns (blueprint, planner-generator-evaluator): [../../agents-subagents/references/harness-patterns.md](../../agents-subagents/references/harness-patterns.md)
- Claude Code vs Codex runtime asymmetry: [../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md](../../ai-coding-agents-tasks/references/loop-and-graph-runtime-surfaces.md)
