# Information Theory Applied to Observability

Content reviewed: 2026-09-17. These are local analysis methods, not universal retention or paging rules.

Use [foundations-information-theory](../../foundations-information-theory/SKILL.md#when-to-apply) when a defined telemetry decision needs distribution, dependence, or compression analysis. For initial instrumentation and ordinary SLO alerting, use this skill's direct recipes. Before changing collection, specify incident/diagnosis tasks, class-specific loss, privacy and forensic retention requirements, budget, and a rollback owner.

## Table of Contents

- [Patterns](#patterns)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
- [Composition](#composition)
- [Sources and related references](#sources-and-related-references)

## Patterns

### P1 — Log Entropy as a Distribution Summary

[Shannon entropy](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md): `H(L) = -sum p(t) log2 p(t)` in bits over parsed templates in a stated time window.

Low entropy means concentrated template frequencies. It does not mean safe deletion: 999,999 normal records and one critical forensic event have low entropy. High entropy can reflect arbitrary IDs rather than useful diagnosis. Inspect template-specific tasks, rare-event coverage, join keys, and retention obligations before proposing aggregation or sampling.

**Artifact:** template counts, parser definition, window, entropy estimate with uncertainty, required queries/events, and a held-out diagnosis comparison. The entropy estimate screens candidates; the task comparison controls the decision.

### P2 — Alert-Fatigue Diagnosis via Labeled Windows

Estimate [mutual information](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md) between binary rule firing A and incident label Y in equally defined windows, including non-firing windows: `I(A;Y)=H(Y)-H(Y|A)`. The latter averages conditional entropy over both A values. Do not estimate from firing-only records or call MI divided by frequency a validated value score.

Rare useful rules can have small MI because incident prevalence is small. Incomplete labels and overlapping windows bias estimates. Compare precision, severity-specific recall, detection delay, redundant coverage and on-call workload with uncertainty; low MI alone never licenses silencing.

**Artifact:** window/label definition, full contingency table, uncertainty method respecting temporal dependence, unique incident detections, and shadow-review recommendation.

### P3 — Trace-Cardinality Budgets

Attribute entropy is not backend capacity. `I(attribute;Y) <= H(Y)` bounds information about the specified label, not the usefulness of an identifier for forensic joins or other tasks. Hash truncation can introduce collisions.

Measure actual bytes, unique values, query/index cost and collision/join consequences. Compare attribute removal with held-out diagnosis and required queries. Use empirical backend budgets in bytes/spans/second; label any `log2(number of values)` as support-size bits, not measured channel capacity.

**Artifact:** attribute inventory, task coverage, cost measurements, privacy constraints, candidate transform and replay results.

### P4 — KL Drift on Latency Distributions

[KL divergence](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md): `D_KL(P_current || P_baseline)=sum p_current(b) log2[p_current(b)/p_baseline(b)]` is in bits. Natural logarithms instead give nats; never mix units.

Use common, disjoint bucket supports. Prometheus classic `le` counts are cumulative: difference adjacent cumulative counts, retain the terminal bucket and normalize once. Check nonnegative counts and nonzero totals. Baseline must exclude the evaluation window. Match service, route mix, traffic and seasonal regimes. Positive current mass at zero baseline mass produces infinite KL; disclose any smoothing and its sensitivity, or use JSD (bounded by 1 bit with log2). Neither direction guarantees detection of every tail shift.

Calibrate thresholds on separate development windows against incident severity, missed-event loss and tolerated pages; validate on held-out chronological windows. Distribution drift need not mean harm and is not a causal diagnosis. Keep SLO burn-rate and rare-event detectors independently.

[Fano's inequality](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md), for a finite K>=2 class label and a classifier using only X, bounds **total classification error**. A loose bound in bits is `max(0,(H(Y|X)-1)/log2 K)`. It does not bound class-conditional false negatives. For binary labels this loose bound is generally vacuous. Estimated conditional entropy has uncertainty and model/support assumptions; never derive it from a KL score or page from it.

**Artifact:** disjoint counts, supports, units, baseline separation, smoothing choice, calibrated threshold, confusion matrices and measured class-specific recall.

### P5 — Information Bottleneck for Log Compaction

[IB](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md): `min I(X;T)-beta I(T;Y)` defines compression relative to a chosen label Y. Information bits are not automatically storage cost; measure actual bytes separately. Beta trades representation complexity against that particular prediction task, not universal forensic value.

Evaluate candidate structured summaries against multiple required diagnosis/replay tasks. Preserve mandatory raw evidence outside the experimental compaction pool. [MDL](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md) can compare encoding schemes, but the shortest encoding does not prove clinical, operational, or incident relevance.

**Artifact:** representation schema, labeled tasks, actual byte savings, held-out loss/recall/delay, lost-query inventory and rollback plan.

### P6 — Span-Level Redundancy Analysis

Separate predictability from diagnosis value. `H(S|P)` (bits) measures residual child-span uncertainty given parent features. For H(S)>0, `I(S;P)/H(S)` is a normalized predictability score. Undefined zero-denominator cases require explicit handling.

Diagnostic increment is instead `I(S;Y|P)`. It is not `H_max(S)-H(S|P)` and is not interchangeable with `1-I(S;Y)/H(S)`. A child can be predictable yet needed for evidence, causality timing or joins. Estimated conditional MI can miss rare cases and feature interactions.

**Artifact:** parent/child feature schema, both measures with estimator limitations, required dependency/join coverage, and removal replay on held-out incident tasks. Collector aggregation may add metrics; do not assume a connector automatically removes original spans.

### P7 — Sampling as a Task-Loss Budget

[Rate-distortion](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md) provides a model once source X, reconstruction, and task loss d are defined. Its rate R is information bits per source symbol, not traces/second. `severity / frequency` is only an uncalibrated proxy unless a loss model supports it.

For a linear missed-event objective, minimize `sum v_c*l_c*(1-s_c)` subject to `sum v_c*b_c*s_c <= B`, with sampling fraction s, incoming volume v, measured loss l and cost b. Reserve required coverage first. Remaining independent classes sort by l/b; uncertainty and interactions can invalidate this model. There is no universal square-root sampling law.

For **stratified mean-estimation variance**, a different objective is `min sum a_c/n_c` subject to `sum b_c*n_c<=B`, where `a_c=W_c^2*sigma_c^2`. Independent sampling and variance/cost estimates give `n_c=sqrt(a_c/(lambda*b_c))`; derive this by setting `-a_c/n_c^2+lambda*b_c=0`. Apply floors, caps and recompute lambda. This estimates a mean, not incident recall. Never transfer its allocation to diagnosis without validation.

**Artifact:** chosen objective, units, constraints, objective-specific derivation, inclusion probabilities and observed losses. Tail sampling decisions must be trace-consistent; account for incomplete traces, buffering, multi-service correlation and overload.

## Anti-Patterns

- **A1:** Delete low-entropy logs. Replace with task/forensic coverage and held-out removal tests.
- **A2:** Treat MI, correlation or lag as causation. Use dependence screening; causal claims need an intervention or identification argument.
- **A3:** Replace SLO alerting with universal KL gates. Retain direct user-impact alerts and calibrate optional drift warnings locally.
- **A4:** Call forward/reverse KL automatically tail-safe. Check support, smoothing and task-specific sensitivity explicitly.
- **A5:** Allocate all budget to high-entropy services. Reserve rare-event and normal-traffic coverage and optimize a declared objective.

## Recipes

### R1 — Alert-Noise Audit

1. Define time windows and independent incident labels, including no-fire periods; record missing labels.
2. Compute the complete 2x2 table per rule, MI in bits, precision, severity recall, detection delay and uncertainty.
3. Replay proposed threshold/removal changes on held-out chronological incidents; inspect cases uniquely detected by that rule.
4. Shadow the change with on-call reviewers. Decide against predeclared tolerated misses/pages, with rollback.

Example decision record (illustrative, no invented measured result):

```yaml
rule: HighMemoryUsage
label_window: declared before evaluation
mi_unit: bits
unique_severe_detections: pending
held_out_recall: pending
recommendation: shadow evaluation; retain until reviewed
```

### R2 — Sampling Budget by Service

1. Measure volume and bytes per trace class, joint-service traces and backend budget; choose diagnosis loss or estimation objective.
2. Reserve forensic/rare-event requirements and a normal-traffic floor. If reservations exceed budget, disclose infeasibility; seek budget or explicit coverage change rather than silently dropping them.
3. Solve the remaining declared allocation. Check caps/floors and measured overhead; publish inclusion probabilities.
4. Replay held-out incidents and normal queries, then run a reversible canary. Track diagnosis loss, missing traces, ingestion bytes and overload.

**Synthetic linear-loss example:** B=50 storage units/s. Two independent classes each arrive at 100 traces/s, cost 1 unit/trace, and have assumed missed-trace losses 10 and 1. Required floors retain 10 traces/s from each class, consuming 20 units. Allocate remaining 30 to the higher-loss class: fractions .4 and .1. Expected loss is `60*10+90*1=690` assumed loss units/s; a feasible .25/.25 allocation gives `75*10+75*1=825`. This follows only from the declared linear separable loss model. Neither number measures real diagnosis loss or proves appropriate floors.

| Required output | Example above | Production evidence |
|---|---|---|
| Volume/cost | 100/s each, 1 unit each | Measured trace volume and bytes |
| Loss | Assumed 10 vs 1 | Validated task-specific loss |
| Constraints | 10/s floors, B=50 | Required coverage and backend limits |
| Decision | .4/.1 under model | Held-out incident loss and canary |

A low-entropy health-check service does not automatically receive zero sampling. No fixed percentage is universally safe.

### R3 — Drift Detection on Latency Distributions

1. Extract separate baseline/current cumulative histograms, difference to disjoint counts and normalize on common support.
2. Compute KL bits (or JSD bits), disclose support/smoothing and compare route/traffic regimes.
3. Select local thresholds on development data; test false pages, detection delay and class-specific misses on held-out windows.
4. Attach the distributions, units, calibration version and investigation checklist to a warning. Page based on the validated policy and user impact, not a Fano false-negative claim.

## Composition

Combine drift, error-rate and saturation as candidate evidence, while retaining rare-event coverage and checking joint feature effects. Feature MI does not set dashboard area, retention quotas or page authority. Each composition returns measured cost, task loss, coverage, uncertainty and rollback conditions.

## Sources and related references

Canonical formulas: [information theory](../../foundations-information-theory/SKILL.md) and its linked primitive templates. The consumer-specific gates here are analysis proposals, not findings attributed to those sources.

Implementation configuration must be checked against current primary documentation before deployment:

- [OpenTelemetry tail sampling processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor)
- [Prometheus histogram documentation](https://prometheus.io/docs/practices/histograms/)

Applied owners: [sampling strategies](sampling-strategies.md), [alerting strategies](alerting-strategies.md), and [log aggregation](log-aggregation-patterns.md).
