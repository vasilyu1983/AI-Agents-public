# Flake, Reproducibility, Contamination, and Leakage

## Table of Contents

- [Why eval flake is dangerous](#why-eval-flake-is-dangerous)
- [Reproducibility controls](#reproducibility-controls)
- [pass@k and aggregation](#passk-and-aggregation)
- [Quarantine, don't ignore](#quarantine-dont-ignore)
- [Contamination vs leakage](#contamination-vs-leakage)
- [System-benchmark hazards](#system-benchmark-hazards)
- [Checklist](#checklist)

## Why eval flake is dangerous

Both the system under test and an LLM judge are stochastic. A verdict that flips
run-to-run produces false regressions (block a good release) and false passes
(ship a real one), and it destroys trust in the whole eval. Separate unstable grading from real variability in the system. Regrade frozen
outputs to test the instrument; rerun the system with a fixed grader to measure
reliability. An unstable system can be the result the eval should detect.

## Reproducibility controls

- **Judge temperature near 0.** The judge is an instrument; it should not be
  creative. Look up supported decoding parameters in the selected provider's
  official API docs; omitting an unsupported parameter is safer than substituting
  an arbitrary tiny value.
- **Pin seeds** where the runtime supports them (sampling seed, dataset shuffle
  seed), and record the seed in every result. But know the limit: **a seed does
  not guarantee bitwise reproducibility.** Batch size and request batching,
  GPU/hardware and kernel versions, mixture-of-experts routing, tensor-parallel
  reductions, and (especially) hosted API providers all introduce nondeterminism
  a seed cannot pin — most commercial endpoints are not reproducible even at
  `temperature=0` with a fixed seed. Use seeds to *reduce* variance and to
  reproduce within one environment; measure repeated-trial reliability rather
  than assuming the seed makes runs identical.
- **Pin versions.** Model version, framework version, tokenizer, and prompt are
  all part of the instrument. Record them with every result; a changed version
  invalidates comparison to history.
- **Store a run manifest with every score**: prompt version, model id and
  revision, dataset version or hash, grader/judge version, a hash of the full
  run config, the code commit, and the run time. Keep manifests with the results
  so any historical score can be re-run and two runs can be diffed field by
  field. A score without a manifest cannot back a release decision.
- **Fix decoding params** (max tokens, top_p, stop sequences) across runs; a
  truncated answer can silently fail a faithfulness check.

## pass@k and aggregation

For inherently stochastic tasks, one run records an outcome but cannot estimate
repeated-trial reliability:

- Choose **k** from the reliability claim, desired precision, and run budget;
  repeat each case and report pass@k / pass^k or a per-case success distribution.
  Majority voting over judges and repeated system trials measure different things.
- **pass@k vs pass^k — pick by the claim.** pass@k = P(at least one of k trials
  passes) measures *capability*; pass^k = P(all k trials pass) measures
  *reliability* (Yao et al., τ-bench, 2024, arXiv 2406.12045). In an
  illustrative case with independent trials and
  constant success probability 0.8, pass@5 = 1 − 0.2^5 ≈ 0.9997 and
  pass^5 = 0.8^5 ≈ 0.328. With heterogeneous tasks, estimate within task before
  averaging; exponentiating the aggregate pass rate changes the estimand. Gate
  anything a user or
  a release depends on repeatedly (agents, tool calls, blocking cases) on
  pass^k; use pass@k only for "can it ever do this" or best-of-N selection.
- Use variance to investigate rubric ambiguity, judge noise, simulator
  variation, and system failures; it does not identify the cause by itself.
- Do not mix k=1 and k=5 results in the same aggregate without saying so.

## Quarantine, don't ignore

When a case's verdict flips across runs:

1. Regrade frozen outputs to check whether the grader is unstable.
2. If the grader is broken, mark the affected blocking slice `inconclusive`,
   repair the rubric or implementation, and rerun it. Report any quarantine and
   the resulting coverage gap; quarantine does not authorize a pass.
3. If outcomes vary with a valid grader, retain those trials in the reliability
   analysis. [τ-bench](https://arxiv.org/html/2406.12045v1) deliberately measures
   this variation with pass^k rather than discarding inconsistent system cases.
4. Change a case or remove it from a blocking set only under a documented
   validity decision made independently of the candidate's observed score.

## Contamination vs leakage

Two distinct ways eval scores get inflated:

- **Benchmark contamination**: the model saw the *benchmark itself* in
  pretraining, so it memorized answers. Mitigate by preferring fresh/private eval
  sets, contamination-scanning your corpus against public benchmarks, and
  treating standard public benchmark scores as a floor, not proof.
- **Testset leakage**: *your own* tuning saw the eval cases — e.g. a synthetic
  testset generated from the same docs used to tune chunking/retrieval, or
  thresholds set on the test split. Mitigate by holding out source data that
  never touches tuning and confirming gold queries are not verbatim substrings of
  indexed content.

Both produce the same failure: confident high scores that do not transfer to
production.

## System-benchmark hazards

The sections above treat the model and judge as the instrument. When the
benchmark measures a *system* — latency, throughput, energy, cost per request,
on-device performance — the hardware and the room it sits in become part of the
instrument too. Four hazards, all from the systems-benchmarking literature
(Reddi, *Machine Learning Systems*, Ch. 12, 2025):

- **The hardware lottery.** A model's measured success can reflect how well it
  maps onto the dominant hardware rather than any intrinsic advantage. The
  textbook cites Hooker (2021) for the concept and gives the canonical example:
  the Transformer succeeded partly because its matrix multiplications match GPU
  capabilities, while architectures that map poorly to GPUs stay underexplored.
  The practical consequence: a model that is efficient on one GPU may be poor on
  a CPU or a custom accelerator, so **a single-platform benchmark cannot tell you
  whether you measured the model or the silicon.** Benchmark across the hardware
  you will actually deploy on. Note this hazard is *unintentional* — distinct
  from benchmark engineering, where a system is deliberately tuned to the test.

- **Lab-to-deployment gap.** Benchmarks reward single-metric optimization
  (speed, accuracy, throughput); real deployments balance power, cost,
  robustness, and tail latency at once. Optimizing average-case benchmark
  performance can silently neglect the tail-latency behavior that actually
  determines user experience. A state-of-the-art score is not a deployment
  decision.

- **Environmental conditions are reproducibility variables.** Ambient
  temperature (via thermal throttling), altitude and cooling efficiency,
  background processes competing for resources, network conditions, and power
  stability all move system-benchmark numbers. Treat them like seeds and
  versions: control what you can, and **document what you cannot control** so a
  reader can account for it. This is the systems analogue of the version-pinning
  rule above — an unrecorded thermal state invalidates comparison to history
  exactly as an unrecorded model version does.

- **Unreported confidence intervals.** The textbook names this directly: CIs
  around benchmark scores often go unreported, which obscures whether a measured
  difference is a genuine improvement or measurement noise. Same rule as
  `references/eval-statistics.md` — a difference without an interval is not a
  result — but the noise source here is hardware and environment, not sampling.

**Why this sits in this file:** these are reproducibility failures whose root
cause is outside the model. An eval can have pinned seeds, pinned versions, and
a clean held-out set and still be irreproducible because it ran on a throttling
laptop, or unfalsifiable because it ran on one accelerator.

## Checklist

- [ ] Judge temperature low; seeds and versions pinned and recorded (knowing seeds don't guarantee bitwise reproducibility, esp. via hosted APIs)
- [ ] Every score stored with its run manifest (prompt, model revision, dataset hash, grader version, config hash, commit)
- [ ] Stochastic tasks run k times with variance reported
- [ ] Grader defects produce inconclusive slices; genuine stochastic failures remain in reliability counts
- [ ] Eval set checked for benchmark contamination
- [ ] Tuning data held out from the eval set (no testset leakage)
- [ ] Decoding params fixed across runs
- [ ] For system/performance benchmarks: measured on the deployment hardware, not one platform (hardware lottery)
- [ ] Environmental conditions (thermal state, background load) controlled or documented
- [ ] Benchmark score differences reported with confidence intervals
