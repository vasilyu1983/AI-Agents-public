# Goal-Mode Loops

Moved from the former tasks skill. Loop shapes and termination predicates are owned by `agents-swarm-orchestration/references/loop-orchestration.md`; this content is pending a move there and is kept here unchanged until then. The task-runtime rule that stays in the SKILL.md: a goal-mode task carries a hard wall-clock cap and an iteration cap, and the real score is re-checked on termination.


Codex exposes a `/goal` command and Goose ships its own `/goal` loop — two first-party implementations of the same pattern: act → score → check goal → continue or terminate. The same loop shape can be built on top of any agent runtime (Claude Code subagent, custom SDK harness, scheduled Routine). Two failure modes dominate when the loop is wired to a vague target:

- **Early give-up.** Score function is unsatisfiable in the obvious direction → agent halts after a few minutes claiming "good enough."
- **Infinite flail.** Score function never converges → agent rewrites the same files indefinitely, burning tokens with no progress.

Both modes share the same root cause: the *check goal* step is underspecified. Fixes below are first-party patterns from Chris Hayduk (OpenAI, 2026-05-11).

### Pattern — Quantitative goal + constraints

Replace qualitative goals with a measurable target plus an explicit constraint set. The agent terminates when target ≥ threshold AND no constraint is violated.

- **Anti-pattern:** "Make the code better." / "Improve this paper."
- **Pattern:** "Reduce runtime of code in `specific_file.py` by 20% without causing regressions in existing unit and integration tests."

Required fields for any goal-mode prompt:

1. **Target metric** — runtime, accuracy, line count, lint score, completed-items count.
2. **Direction + magnitude** — "reduce by 20%", "raise above 0.85", "down to ≤ 50 lines".
3. **Constraint set** — tests that must keep passing, files that must not change, APIs that must not break.
4. **Termination signal** — exact command or file state the agent can read to confirm it is done.

### Pattern — Checklist-as-score (qualitative → quantitative)

When the real goal is qualitative (formatting compliance, style guide adherence, doc completeness), convert it to a binary checklist:

1. Extract the qualitative spec into a markdown checklist with N items (Hayduk's NeurIPS→ICML conversion produced 200+ items from a LaTeX style file).
2. Instruct the agent: "Goal complete when all N of N items are checked off."
3. Each item can itself be vague — the model reasons about per-item completion better than per-goal completion.
4. Have the agent mutate the checklist file as it works, so progress is persisted and inspectable.

Why this works: a fuzzy "is the paper formatted correctly?" decision becomes N narrow "is rule K satisfied?" decisions, each of which the model can self-check with reasonable reliability.

### Pattern — Tight feedback loop

The goal-mode loop is bounded by per-iteration scoring time. Drop scoring cost without compromising signal:

- For ML/training tasks: smaller model + subsampled dataset (Hayduk: NanoFold dataset cut scoring from days to minutes for protein-structure architecture search).
- For codebases: scoped test subset that exercises the affected path, not full suite.
- For builds: incremental builds, not clean rebuilds.

This is the same minification principle as dev-loop test speedups, applied to the *evaluation* step of an RL-style agent loop instead of to verification.

### When bare goal-mode is not enough

Goal-mode is a ralph-style loop: same prompt repeats with the goal-state read back each iteration. Extra iterations buy score only while the check step discriminates; compare against a single-pass baseline before paying for more. A bare ralph loop also hits three ceilings:

1. **Ambiguity bottleneck.** Each iteration's output is the next iteration's input. One underspecified decision early in the run can shift everything downstream. More token spend does not repair a missing acceptance decision. Fix: ask the smallest set of questions needed to resolve load-bearing choices, then write the answers into the task contract. See [`dev-workflow-planning`](../../dev-workflow-planning/SKILL.md) for writing the task contract.

2. **Context-shape bottleneck.** Long histories can accumulate irrelevant material even with token headroom. Separate contexts can help independent work or clean review, but they add briefing, coordination, and synthesis cost and are not universally better. Choose a single agent or an orchestrator/implementer/reviewer split from the dependency shape, then compare completion quality and total usage. See [`../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md).

3. **Cross-context memory bottleneck.** Multi-day runs cross compaction or session boundaries, and runtime-provided recovery differs. Persist the minimum task state needed to resume and test that the target runtime actually reloads it; filesystem-backed journaling is one option, not proof that every new window otherwise loses all prior state. See [`long-horizon-journaling.md`](../../dev-workflow-planning/references/long-horizon-journaling.md).

Goal-mode plus a feedback loop can fit short-horizon quantitative goals. For multi-day product work, choose clarification, multiple agents, and durable state only where the task's ambiguity, independence, and resume needs justify them; validate the combination against a simpler baseline rather than treating every component as mandatory.

### Anti-pattern — Letting compaction carry multi-day state

Goal-mode runs that last hours or days exceed the practical window of in-memory transcript compaction. Force state to the filesystem instead. See [`long-horizon-journaling.md`](../../dev-workflow-planning/references/long-horizon-journaling.md) in `dev-workflow-planning` for the canonical 3-file (`PLAN.md` / `EXPERIMENTS.md` / `EXPERIMENT_NOTES.md`) pattern.

### Recipe — Wiring a goal-mode task

1. Convert user intent → quantitative goal + constraint set. If qualitative, build the checklist first as a planning step.
2. Stand up the cheapest scoring command that still discriminates progress; record it in the task definition.
3. Seed `PLAN.md` with the initial approach. Mount `EXPERIMENTS.md` + `EXPERIMENT_NOTES.md` as the agent's persistent scratchpad.
4. Spawn the goal-mode task with a hard wall-clock cap and an iteration cap; both should be generous but finite.
5. On termination, check the *real* score (not the agent's self-reported claim) before accepting the result.

Source: Chris Hayduk, *Using Codex Goals Effectively* (2026-05-11). Generalizable beyond Codex — the same pattern works for Claude Code subagents driving toward a measurable target.

