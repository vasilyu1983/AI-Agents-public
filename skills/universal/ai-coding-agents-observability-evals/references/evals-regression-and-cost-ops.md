# Evals, Regression, And Cost Ops

Treat coding-agent evals as a release discipline, not a side project.

## Contents

- Core eval pack and iterative self-extension
- Scoring, and judge and pairwise pointers
- Release gates, cost controls, and edge cases

## Core eval pack

Every serious coding-agent runtime should have:

- **golden coding tasks** for bounded edits
- **golden review tasks** with known seeded defects
- **tool-choice tasks** where the correct path depends on search or inspection before editing
- **verification tasks** that punish self-approval and reward separate verification
- **multi-agent tasks** when the product supports workers, teammates, or coordinator flows
- **iterative self-extension tasks** that carry the agent's own workspace through evolving specifications
- **cost and latency baselines** per task family

## Iterative self-extension pack

Use a versioned trajectory pack for agents that repeatedly extend a repository. A trajectory starts from an empty or fixed seed workspace, then carries the candidate's own checkpoint output into the next evolved specification. Do not replace it with reference code between checkpoints: that erases the effect of the candidate's earlier design decisions.

At each checkpoint, collect:

- lineage: `trajectory_id`, `checkpoint_id`, `parent_checkpoint_id`, and `spec_version`
- workspace provenance: stable workspace identity plus a content hash
- correctness: strict, isolated, core, and regression results as separate fields
- structural-quality signals: erosion and verbosity
- operations: cost and duration

Keep the pack's detailed task construction, fresh-context protocol, and hidden black-box testing with [`../../qa-agent-testing/SKILL.md`](../../qa-agent-testing/SKILL.md). Keep the definitions and interpretation of erosion and verbosity with [`../../software-clean-code-standard/SKILL.md`](../../software-clean-code-standard/SKILL.md). This eval-ops layer owns versioning, telemetry, comparison, and release decisions.

Green tests at one checkpoint—or even a green final snapshot—do not prove extension robustness. Compare candidate and baseline across the full trajectory. Report per-checkpoint levels, candidate-versus-baseline slope, and late-checkpoint correctness regressions; do not collapse these into one final pass rate. Set gates from repeated runs on the product's own representative pack rather than importing a universal slope or metric threshold.

SlopCodeBench (arXiv:2603.24755v1) provides preprint evidence for this failure mode. Per its abstract, explicit quality guidance reduced initial verbosity and erosion by up to a third without affecting degradation rates; any claim about plan-first prompts or correctness is unsourced — verify against the paper. Treat prompt changes as evaluated interventions, not as sufficient controls.

## Score more than final correctness

Useful dimensions:

- final output correctness
- patch quality and blast radius
- tool-call precision
- retry discipline
- escalation quality
- verifier effectiveness
- latency
- token usage
- dollar cost

## Judges, pairwise runs, and flake

The judge and pairwise method (self-preference, position and length bias, both-orderings pairwise judging, flake quarantine) is owned by [`../../ai-evals/references/llm-judge-bias.md`](../../ai-evals/references/llm-judge-bias.md) and [`../../ai-evals/references/flake-and-reproducibility.md`](../../ai-evals/references/flake-and-reproducibility.md); paired significance and pack sizing are in [`../../ai-evals/references/eval-statistics.md`](../../ai-evals/references/eval-statistics.md). Coding-agent specifics only:

- Pin `llm_judge` rubrics to behavior (compiles, tests pass, blast radius), and keep a non-judge check (build, tests, schema) on any release-blocking gate.
- Score diff size against the minimal correct change, so neither a bloated nor a truncated patch can buy a pass; do not assume which direction the judge leans.
- A golden task whose verdict flips run to run is a broken task, not a regression: quarantine and rewrite it.
- Gate a pairwise win on quality **and** absolute cost/latency, so a winner that doubled cost shows up as a trade.

## Release gates

Block release when any of these regress materially:

- pass rate on seeded critical defects
- verifier catch rate
- median or p95 cost per task family
- median or p95 latency for common tasks
- false-positive or false-negative rate on code-review tasks
- candidate-versus-baseline structural-quality slope on iterative packs
- strict, isolated, core, or regression results at late checkpoints, even when the final aggregate remains acceptable
- any `harness_tamper` event: the agent changed test, grader, or CI paths during the task (hash those paths before and after; grade from a clean checkout of them)

Decide "regressed materially" with a paired test on the same tasks and a pre-declared minimum detectable effect, not by comparing each build's own confidence interval (see the SKILL.md expert-judgment note and `eval-statistics.md`).

## Cost tips

- Track provider cost per turn and per tool-heavy phase.
- Compare candidate changes against a fixed baseline corpus before rollout.
- Keep a “cheap smoke pack” and a “full release pack” so every change does not require full-cost evaluation.
- Add real production failures back into the corpus after they are fixed.

## Edge cases

- **Provider swaps**: Normalized pass rates can hide large cost drift, so compare quality and cost together.
- **Caching changes**: Prompt-cache improvements can change cost and latency even when quality is stable; track them explicitly.
- **New safety rules**: Approval or sandbox changes can reduce defect risk while increasing latency. Treat that as a deliberate trade, not noise.
- **Multi-agent systems**: Grade the coordinator and workers separately so you can see whether failures come from delegation or execution.

## Practical tip

If you can only afford one strict gate initially, make it:

- seeded-defect catch rate for review agents
- behavior-preserving pass rate for edit agents
- verification catch rate for multi-agent workflows
