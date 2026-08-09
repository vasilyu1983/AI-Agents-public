# Online and Production Evaluation

Offline evals tell you a candidate is *probably* better. Production tells you
whether it *actually* is, on real traffic, under real distribution shift. This
file covers the eval work that only exists once the system is serving users:
keeping offline and online in agreement, measuring on live traffic safely, and
catching drift before users do.

## Table of Contents

- [Why offline is not enough](#why-offline-is-not-enough)
- [Offline-online correlation](#offline-online-correlation)
- [A/B tests with guardrails](#ab-tests-with-guardrails)
- [Shadow and canary traffic](#shadow-and-canary-traffic)
- [Regression replay](#regression-replay)
- [Drift detection](#drift-detection)
- [Human-in-the-loop feedback](#human-in-the-loop-feedback)
- [Online judges and sampling](#online-judges-and-sampling)
- [Checklist](#checklist)

## Why offline is not enough

A frozen offline set is a fixed snapshot of yesterday's distribution. Production
moves: new user intents, seasonal phrasing, new doc corpus, upstream model
updates. A candidate that wins offline can lose online because (a) the offline
set under-represents the segment the change hurts, or (b) the metric that moved
offline doesn't drive the outcome that matters online. Treat offline as a
**filter** (cheap, fast, blocks obvious regressions) and online as the
**verdict** (expensive, slow, ground truth).

## Offline-online correlation

The single most valuable production-eval asset: a measured correlation between
your offline metric and the online outcome you actually care about (resolution
rate, deflection, conversion, thumbs-up).

- Periodically plot offline score vs the online KPI across past shipped changes.
  If they don't correlate, your offline metric is measuring the wrong thing —
  fix the offline metric before trusting it as a gate.
- A high offline win with no online movement means the offline set is gaming the
  metric or testing an off-path behavior.
- Re-check correlation after any major distribution shift; it decays.

## A/B tests with guardrails

The default online eval is a randomized A/B (or interleaving for ranking).

- **Primary metric**: pre-registered, the outcome you're optimizing.
- **Guardrail metrics**: things that must NOT regress even if the primary moves
  — latency P95, cost/request, refusal rate, safety-flag rate, error rate. A win
  on primary with a guardrail breach is not a ship.
- Apply the same statistics as offline: CIs, paired/interleaved analysis where
  possible, sequential-testing correction if you peek (peeking without it inflates
  false positives badly). See `eval-statistics.md`.
- **Interleaving** for ranking/retrieval changes detects differences with far
  less traffic than a classic A/B — prefer it when comparing rankers.
- Run long enough to cover a full cycle (weekday/weekend, business hours);
  novelty effects fade.

## Shadow and canary traffic

When you can't randomize on users yet:

- **Shadow**: run the candidate on a copy of live requests without serving its
  output. Compare to production silently. Catches latency, cost, crash, and gross
  quality regressions with zero user risk. The candidate's output is graded
  offline (deterministic checks + sampled judge), never shown.
- **Canary**: route a small % of real traffic to the candidate with automated
  rollback on guardrail breach. The bridge between shadow and full A/B.

## Regression replay

Continuously harvest production traces into the eval set:

- **Every escalation, thumbs-down, or incident becomes a replay case.** Replay it
  against each candidate before ship — this is how the regression slice stays
  representative of real failures, not synthetic ones (ties to
  `dataset-construction.md`).
- De-identify before storing (PII); keep the trace (inputs, retrieval, tools) so
  failures stay attributable.
- Replay is offline mechanically but production-sourced — it's the cheapest way
  to keep offline correlated with online.

## Drift detection

Production quality erodes without any code change. Monitor:

- **Input drift**: shift in request distribution (new intents, languages,
  lengths) — population stability index or embedding-cluster shift.
- **Output drift**: shift in response distribution (length, refusal rate, tool-
  call mix) — often the first sign of an upstream model or corpus change.
- **Quality drift**: rolling online judge/HITL score trending down.
- **Score-variance, not just mean**: an eval set that's getting *easier* (variance
  collapsing) means it's stale and no longer discriminating — refresh it.

Alert on drift; don't wait for the quarterly review.

## Human-in-the-loop feedback

- **Explicit signals** (thumbs, ratings) are sparse and biased toward extremes —
  useful as a trend, weak as ground truth.
- **Implicit signals** (edits, retries, copy, abandonment, follow-up "no that's
  wrong") are denser and often more honest. Instrument them.
- Route a sampled stream to human reviewers to maintain a fresh labeled set —
  this is what keeps the online judge calibrated (see `advanced-judging.md`) and
  what new offline cases are drawn from.
- Close the loop: reviewed failures → new eval cases → next candidate's gate.

## Online judges and sampling

Running an LLM judge on 100% of production traffic is usually too expensive.

- **Deterministic checks on 100%** (schema, citation present, refusal-when-must,
  safety classifier), **LLM judge on a sample** stratified by slice, **human on a
  smaller sample** for calibration.
- Same bias controls apply online as offline (different judge model, behavior-
  pinned rubric) — see `llm-judge-bias.md`.
- Log judge verdicts with the trace so online scores are auditable, not just a
  dashboard number.

## Checklist

- [ ] Offline metric's correlation to the online KPI is measured, not assumed
- [ ] A/B has a pre-registered primary plus guardrail metrics (latency, cost, safety, refusal)
- [ ] Peeking is corrected for (sequential testing) or avoided
- [ ] Interleaving used for ranking changes to save traffic
- [ ] Shadow/canary path exists for pre-randomization validation
- [ ] Escalations and thumbs-down auto-flow into the regression replay set
- [ ] PII removed from harvested traces
- [ ] Input/output/quality drift monitored with alerts, variance tracked not just mean
- [ ] Online judge runs on a stratified sample; deterministic checks run on all traffic
- [ ] HITL review stream feeds both judge calibration and new eval cases
