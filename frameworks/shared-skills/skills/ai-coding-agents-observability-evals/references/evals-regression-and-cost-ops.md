# Evals, Regression, And Cost Ops

Treat coding-agent evals as a release discipline, not a side project.

## Contents

- Core eval pack and iterative self-extension
- Scoring, judge controls, and pairwise evaluation
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

SlopCodeBench (arXiv:2603.24755v1) provides preprint evidence for this failure mode in its Python track. Its anti-slop and plan-first prompts improved initial quality, but did not halt the quality-degradation slope or consistently improve correctness. Treat prompt changes as evaluated interventions, not as sufficient controls.

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

## LLM-as-judge bias and flake control

When a golden task uses `method: llm_judge`, the judge is itself a model with
failure modes. Treat its scores as a calibrated instrument, not ground truth.

- **Self-preference bias**: do not judge an agent with the same model/config that
  produced the output. A model rates its own style higher. Use a different judge
  model, or a deterministic check, for the gate that blocks release.
- **Length / verbosity bias**: judges reward longer patches and longer
  explanations even when shorter is correct. Pin the rubric to behavior
  (compiles, tests pass, blast radius) and penalize unnecessary diff size
  explicitly so verbosity cannot buy a passing score.
- **Position bias** (pairwise mode): when comparing two candidate runs, judges
  favor whichever is shown first. Always run both orderings and require both to
  agree; count disagreement as a tie, not a win.
- **Flake / non-determinism**: model judges and the agents under test are both
  stochastic. Run each task N times (pass@k or majority vote), fix judge
  temperature low, and treat a task whose verdict flips run-to-run as a
  *broken golden task*, not a real regression — quarantine and rewrite it.

For the full judge-bias taxonomy, calibration mechanics, and threshold
derivation, see the `ai-evals` skill.

## Pairwise and preference evals

Absolute pass/fail is not enough when you are choosing between two harness
versions, two prompts, or two models. Add a pairwise track:

- Show the judge both candidates' transcripts for the same golden task.
- Swap order on a second pass (position-bias guard above).
- Aggregate to a win rate with confidence intervals, not a single tally.
- Gate on win rate **and** absolute cost/latency, so a "better" candidate that
  doubled cost is surfaced as a trade, not a silent win.

## Release gates

Block release when any of these regress materially:

- pass rate on seeded critical defects
- verifier catch rate
- median or p95 cost per task family
- median or p95 latency for common tasks
- false-positive or false-negative rate on code-review tasks
- candidate-versus-baseline structural-quality slope on iterative packs
- strict, isolated, core, or regression results at late checkpoints, even when the final aggregate remains acceptable

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
