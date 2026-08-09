# Flake, Reproducibility, Contamination, and Leakage

## Table of Contents

- [Why eval flake is dangerous](#why-eval-flake-is-dangerous)
- [Reproducibility controls](#reproducibility-controls)
- [pass@k and aggregation](#passk-and-aggregation)
- [Quarantine, don't ignore](#quarantine-dont-ignore)
- [Contamination vs leakage](#contamination-vs-leakage)
- [Checklist](#checklist)

## Why eval flake is dangerous

Both the system under test and an LLM judge are stochastic. A verdict that flips
run-to-run produces false regressions (block a good release) and false passes
(ship a real one), and it destroys trust in the whole eval. Flake is not noise to
average away silently — a case whose verdict is unstable is a **broken test**.

## Reproducibility controls

- **Judge temperature near 0.** The judge is an instrument; it should not be
  creative. (Note: some inference providers reject `temperature=0` — use a tiny
  value like `0.001`; see huggingface-community-evals.)
- **Pin seeds** where the runtime supports them (sampling seed, dataset shuffle
  seed), and record the seed in every result. But know the limit: **a seed does
  not guarantee bitwise reproducibility.** Batch size and request batching,
  GPU/hardware and kernel versions, mixture-of-experts routing, tensor-parallel
  reductions, and (especially) hosted API providers all introduce nondeterminism
  a seed cannot pin — most commercial endpoints are not reproducible even at
  `temperature=0` with a fixed seed. Use seeds to *reduce* variance and to
  reproduce within one environment; rely on pass@k and quarantine (below), not
  seeds, as the real defense against flake.
- **Pin versions.** Model version, framework version, tokenizer, and prompt are
  all part of the instrument. Record them with every result; a changed version
  invalidates comparison to history.
- **Fix decoding params** (max tokens, top_p, stop sequences) across runs; a
  truncated answer can silently fail a faithfulness check.

## pass@k and aggregation

For inherently stochastic tasks, a single run is not a measurement:

- Run each case **k times** (k=3-5 typical) and aggregate: majority vote for
  verdicts, or report pass@k / mean ± stddev.
- Use the **variance** as a signal: high per-case variance means the case (or the
  judge prompt) is underspecified.
- Do not mix k=1 and k=5 results in the same aggregate without saying so.

## Quarantine, don't ignore

When a case's verdict flips across runs:

1. **Quarantine** it out of the blocking gate.
2. Investigate: ambiguous rubric, underspecified expected output, or genuine
   model nondeterminism.
3. Rewrite the case to be deterministic, or move it to a non-blocking signal set.
4. **Report quarantined cases in the gate output** — silently dropping them turns
   a flaky eval into a falsely-green one (fail loud).

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

## Checklist

- [ ] Judge temperature low; seeds and versions pinned and recorded (knowing seeds don't guarantee bitwise reproducibility, esp. via hosted APIs)
- [ ] Stochastic tasks run k times with variance reported
- [ ] Flaky cases quarantined and reported, not silently averaged
- [ ] Eval set checked for benchmark contamination
- [ ] Tuning data held out from the eval set (no testset leakage)
- [ ] Decoding params fixed across runs
