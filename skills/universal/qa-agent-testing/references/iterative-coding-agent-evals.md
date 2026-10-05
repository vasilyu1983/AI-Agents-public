# Iterative Coding-Agent Evaluations

Use this protocol when the question is whether a coding agent can repeatedly extend its own prior implementation without losing correctness or accumulating structural problems. It adapts the evaluation design introduced by SlopCodeBench, a March 2026 preprint ([arXiv:2603.24755v1](https://arxiv.org/abs/2603.24755v1)).

## Contents

- [Carried-Workspace Protocol](#carried-workspace-protocol)
- [Correctness Slices](#correctness-slices)
- [Trajectory Aggregation](#trajectory-aggregation)
- [Longitudinal Quality Signals](#longitudinal-quality-signals)
- [Interpreting Prompt Interventions](#interpreting-prompt-interventions)
- [Evidence Limits](#evidence-limits)
- [Minimal Trajectory Record](#minimal-trajectory-record)
- [Source](#source)

## Carried-Workspace Protocol

Represent a problem as an ordered sequence of checkpoints. At checkpoint `Ci`, give the agent the current specification `xi` and the workspace it produced at `Ci-1`; the output becomes the workspace for the next checkpoint. Start `C1` from an empty workspace.

For every checkpoint:

1. Introduce an observable feature or contract extension. Do not reveal the intended internal architecture.
2. Start with fresh conversation, agent-session, installed-package, and shell-history state. Carry only the working directory. This forces the agent to recover prior decisions from the code rather than hidden conversational memory.
3. Run in a fresh isolated environment as a non-root user with a consistent tool baseline.
4. Evaluate through subprocesses or a served API. Tests should exercise external behavior rather than import private implementation details.
5. Preserve all earlier requirements as regression tests and record the produced workspace even when correctness fails.
6. Record correctness slices, quality signals, cost, and duration per produced checkpoint. If no workspace is produced, score subsequent correctness as zero but exclude missing workspaces from erosion and verbosity aggregates rather than imputing them.

This design exposes compounding consequences: a locally convenient design that passes `C1` remains the foundation for `C2` and later work.

## Correctness Slices

Categorize checkpoint tests before running the agent:

| Slice | Meaning |
|---|---|
| Core | Behavior explicitly stated or demonstrated by the current specification |
| Error | Required failure-mode behavior |
| Functionality | Held-out tests that exercise the current contract beyond shown examples |
| Regression | All tests retained from earlier checkpoints; absent at `C1` |

Report four checkpoint views rather than one pass rate:

- **Strict:** every current core, error, functionality, and prior regression test passes.
- **Isolated:** all current-checkpoint non-regression tests pass; this separates current implementation ability from cascading earlier failures.
- **Core:** current core tests pass, even if broader hidden or regression behavior fails.
- **Regression:** prior-checkpoint tests pass; report this slice directly so preservation failures do not disappear inside strict correctness.

Use held-out black-box tests for unbiased benchmark measurement. Do not confuse that with production TDAD: when the goal is safe delivery rather than unbiased capability estimation, provide the agent with targeted source-to-test context and known affected tests. Production can still retain a separate hidden suite for independent evaluation.

## Trajectory Aggregation

Checkpoint counts may differ across problems. Normalize each trajectory into five ordered phases:

- first checkpoint: `Start`
- last checkpoint: `Final`
- interior checkpoints: divide in order into `Early`, `Mid`, and `Late`
- if the interior count is not divisible by three, assign the extra checkpoint(s) to the earlier phase(s)

Keep per-checkpoint records as the source of truth. Use phase summaries only for comparing trajectory shapes; do not let aggregation hide individual collapse points.

## Longitudinal Quality Signals

Treat both measures as descriptive signals, not correctness predictors or universal release gates.

For every callable `f` in the workspace, define complexity mass as:

```text
mass(f) = CC(f) * sqrt(SLOC(f))
```

where `CC(f)` is cyclomatic complexity and `SLOC(f)` is source lines of code. SlopCodeBench defines structural erosion as:

```text
Erosion = sum(mass(f) for f where CC(f) > 10) / sum(mass(f) for all callables f)
```

The `CC > 10` cutoff is part of the paper's metric definition. Preserve it when reproducing the benchmark; do not promote it to a universal maintainability threshold.

Define a documented local set of redundant-code rules and a clone detector, then compute:

```text
Verbosity = count(AST-rule flagged lines union clone lines) / LOC
```

Deduplicate lines hit by multiple rules or both detectors before counting. Record the rule-set and detector versions so runs remain comparable. The paper used 137 targeted AST-grep rules; a local reproduction must either use that released rule set or state that its score is not directly comparable.

Record cost and wall-clock duration for each produced checkpoint. Track their direction across phases alongside correctness, erosion, and verbosity; do not infer that lower erosion or verbosity causes higher correctness.

## Interpreting Prompt Interventions

The paper's anti-verbosity and plan-first prompts improved the initial structural-quality baseline in its two-model prompt study, but did not significantly slow erosion or verbosity slopes, consistently improve correctness, or reduce cost. Therefore:

- use quality prompts as a possible starting-condition aid, not as a longitudinal control
- measure the whole trajectory after a prompt change
- test structural tooling, refactoring gates, or training interventions directly before claiming they prevent degradation

## Evidence Limits

- SlopCodeBench is a preprint, not settled peer-reviewed evidence.
- Its reported experiments evaluate only the Python track, although the specifications are described as language-agnostic.
- The maintained human-repository panel is a calibration reference, not a matched human-solution baseline.
- Erosion and verbosity measure distinct structural tendencies; the paper's sensitivity analysis does not support treating them as predictors of next-checkpoint correctness.
- Structural-discipline interventions beyond prompting were proposed, not tested.
- Do not turn paper averages, model rankings, metric cutoffs, or prompt-study effects into organizational targets without local validation.

## Minimal Trajectory Record

Use the iterative add-on in [`../assets/qa-harness-template.md`](../assets/qa-harness-template.md). At minimum, preserve checkpoint lineage, specification version, workspace identity or content hash, all correctness slices, erosion, verbosity, cost, and duration.

## Source

Orlanski, G. et al. "SlopCodeBench: Benchmarking How Coding Agents Degrade Over Long-Horizon Iterative Tasks." arXiv:2603.24755v1, March 2026. https://arxiv.org/abs/2603.24755v1
