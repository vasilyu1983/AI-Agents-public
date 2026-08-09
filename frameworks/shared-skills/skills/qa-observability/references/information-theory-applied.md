# Information Theory Applied to Observability

> **Gate before invoking:** Check [`foundations-information-theory` § When to Apply](../../foundations-information-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Cross-skill reference: applies primitives from `foundations-information-theory` to the observability domain.  
Primitives live in `../../foundations-information-theory/assets/templates/information-theory/`.  
Sibling applied reference: `control-theory-applied.md` (in-progress)._

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — Log Entropy as a Noise/Value Measure](#p1--log-entropy-as-a-noisevalue-measure)
  - [P2 — Alert-Fatigue Diagnosis via Entropy of Triggered Alerts](#p2--alert-fatigue-diagnosis-via-entropy-of-triggered-alerts)
  - [P3 — Trace-Cardinality Budgets via Channel Capacity Reasoning](#p3--trace-cardinality-budgets-via-channel-capacity-reasoning)
  - [P4 — KL-Drift on Latency/Error-Rate Distributions for Anomaly Detection](#p4--kl-drift-on-latencyerror-rate-distributions-for-anomaly-detection)
  - [P5 — Information Bottleneck for Log Compaction](#p5--information-bottleneck-for-log-compaction)
  - [P6 — Span-Level Redundancy Elimination](#p6--span-level-redundancy-elimination)
  - [P7 — Sampling Rate as a Rate-Distortion Tradeoff](#p7--sampling-rate-as-a-rate-distortion-tradeoff)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Logging Every Event "For Debugging" Without an Entropy Check](#a1--logging-every-event-for-debugging-without-an-entropy-check)
  - [A2 — Using Pearson Correlation on Noisy Metric Pairs to Claim Causation](#a2--using-pearson-correlation-on-noisy-metric-pairs-to-claim-causation)
  - [A3 — Alert Thresholds Without Distributional Context](#a3--alert-thresholds-without-distributional-context)
  - [A4 — KL Asymmetry Confusion in Drift Detection](#a4--kl-asymmetry-confusion-in-drift-detection)
  - [A5 — Sampling Decisions Made on Volume, Not Per-Trace Mutual Information](#a5--sampling-decisions-made-on-volume-not-per-trace-mutual-information)
- [Recipes](#recipes)
  - [R1 — Alert-Noise Audit](#r1--alert-noise-audit)
  - [R2 — Sampling Budget by Service](#r2--sampling-budget-by-service)
  - [R3 — Drift Detection on Latency Distributions](#r3--drift-detection-on-latency-distributions)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Log Entropy as a Noise/Value Measure

**Primitive**: [Shannon Entropy (#1)](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

**Problem**: Log pipelines accumulate messages whose actual information value is unknown. High-volume logs are not necessarily high-value logs. Engineers add verbosity during development and rarely prune it. The result is storage cost, noise that buries real signals, and slow query performance in tools like Datadog Log Management or Elastic.

**Approach**: Treat the message distribution of a logger or log source as a discrete probability distribution. Compute Shannon entropy H over the histogram of distinct message templates (after log parsing/clustering):

```
H(L) = −Σ_{t} p(t) log₂ p(t)
```

where t is a parsed log template (e.g., via Drain or OpenTelemetry log grouping) and p(t) is the fraction of log lines matching template t.

- **Low H, high volume**: one template dominates (e.g., a heartbeat). Near-zero information per byte. Safe to sample aggressively or drop.
- **High H, moderate volume**: each line carries distinct signal. Preserve.
- **High H, very high volume**: inspect whether high entropy reflects genuine diversity or unbounded cardinality injection (user IDs in message bodies). The latter is anti-pattern A1.

**Tooling anchor**: Datadog Log Pattern Analysis, Honeycomb derived columns with `GROUP BY` on message template, or a Prometheus histogram of log-line categories via the OpenTelemetry filelog receiver with `regex` parsing.

**Outcome**: A per-logger entropy score that drives retention policy. Loggers below H-threshold get downsampled; loggers above threshold get preserved or promoted to structured events.

---

### P2 — Alert-Fatigue Diagnosis via Entropy of Triggered Alerts

**Primitive**: [Shannon Entropy (#1)](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md), [Mutual Information (#2)](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

**Problem**: On-call engineers stop responding to alerts when every alert fires constantly. Alert fatigue is an information-theoretic failure: the alert channel carries near-zero mutual information with real incidents.

**Approach**: Build a distribution over alert-rule firings over a 30-day window. Compute H(A) where A is the alert-rule identity random variable:

```
H(A) = −Σ_{r} p(r) log₂ p(r)
```

Then compute I(A; I) — mutual information between alert firings and confirmed incidents (labeled from PagerDuty or OpsGenie post-mortems). A rule with high firing frequency but low I(A_r; I) is noise: it fires often but predicts no incident.

Rules to silence or raise the threshold:
- Fires frequently (high marginal contribution to H(A))
- Low I(A_r; I) — uncorrelated with any incident in the labeling window

Rules to keep and investigate further:
- Fires rarely but whenever it fires, an incident follows — high precision, high MI per firing

**Tooling anchor**: Prometheus `ALERTS` metric + Alertmanager inhibit rules. Datadog Alert History export. PagerDuty incident webhook for labeling. A weekly cron over the alert log computes this audit automatically (see Recipe R1).

---

### P3 — Trace-Cardinality Budgets via Channel Capacity Reasoning

**Primitive**: [Channel Capacity (#5)](../../foundations-information-theory/assets/templates/information-theory/05-channel-capacity.md), [Redundancy & Compression (#11)](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md)

**Problem**: High-cardinality span attributes (user IDs, request URLs with query parameters, full SQL queries) injected as OpenTelemetry span tags blow up storage cost in Honeycomb, Jaeger, or Tempo. Teams add attributes without a budget.

**Approach**: Model each span attribute slot as a channel. The useful information capacity of an attribute is bounded by the entropy of the downstream use case it serves (incident detection, latency attribution, user-journey analysis). Attributes with entropy exceeding the query resolution needed are not more valuable — they are more expensive.

Concretely:
1. For each span attribute, compute H(attr) over observed values in a 7-day window.
2. Compute the marginal MI gain: I(attr; SLO_breach) or I(attr; incident) using the incident labels.
3. Set a cardinality budget C per service: total number of unique attribute-value combinations ≤ 2^C, where C is the capacity in bits allocated to that service in the backend.
4. Drop or hash-truncate attributes where H(attr) >> I(attr; outcome): they carry entropy but no useful information for downstream queries.

**Tooling anchor**: Honeycomb cardinality warnings, OpenTelemetry Collector `filter` and `transform` processors for attribute truncation. Grafana Tempo tag value count APIs.

**Outcome**: A per-service attribute budget in bits, enforced at the Collector layer, that keeps backend costs predictable without blindly dropping spans.

---

### P4 — KL-Drift on Latency/Error-Rate Distributions for Anomaly Detection

**Primitive**: [KL Divergence (#3)](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md), [Fano's Inequality (#9)](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md)

**Problem**: Latency distributions are non-Gaussian (long-tailed, bimodal during cold starts, multi-modal across request types). Static z-score thresholds misfire on non-Gaussian tails and miss slow degradation that doesn't spike a mean. SLO burn-rate alerts catch end-state failures but not early distributional drift.

**Approach**: Maintain a baseline distribution P (rolling 7-day histogram, percentile bins or kernel density) and compute D_KL(P_current ‖ P_baseline) daily:

```
D_KL(P_t ‖ P_0) = Σ_{b} p_t(b) · log₂[p_t(b) / p_0(b)]
```

where b are histogram buckets (e.g., Prometheus `le` buckets from `http_request_duration_seconds`).

Alert tiers:
- D_KL < 0.05 nats: nominal
- 0.05 ≤ D_KL < 0.2 nats: investigate (slow degradation candidate)
- D_KL ≥ 0.2 nats: alert (distribution has materially changed)

Use Fano's inequality to bound the downstream impact: if residual entropy H(outcome | features) is high, classification-based incident routing will underperform, giving a lower bound on false-negative rate.

**KL direction**: compute D_KL(P_current ‖ P_baseline) (forward KL) because you want to penalize regions the current distribution places mass on that the baseline does not — this is the mean-seeking direction that catches tail expansion. See Anti-Pattern A4 for the asymmetry trap.

**Tooling anchor**: Prometheus histogram metric `histogram_quantile`, Grafana's native histogram support. Datadog Distribution Metrics. Python `scipy.stats.entropy` for offline validation.

---

### P5 — Information Bottleneck for Log Compaction

**Primitive**: [Information Bottleneck (#8)](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md), [MDL Principle (#7)](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md)

**Problem**: Log retention is expensive. Naive compaction (drop oldest, keep newest) discards logs that may be the best predictors of future incidents. What survives should maximally predict incidents (high I(T; incident)) while discarding irrelevant detail (low I(T; raw_log)).

**Approach**: Frame log compaction as an information bottleneck (IB) problem. Let X be the raw log stream, Y be confirmed incidents (binary: incident / no-incident within the next T hours), and T be the compressed representation:

```
min_{p(T|X)} I(X; T) − β · I(T; Y)
```

- I(X; T): bits retained from the raw log (cost)
- I(T; Y): bits about future incidents preserved in the retained log (value)
- β: retention budget parameter (higher β → keep more, at higher cost)

In practice:
1. Cluster log lines into templates (MDL: pick the model with the shortest description length that still separates incident-preceding logs from normal logs).
2. For each template cluster, compute I(cluster; incident_within_1h).
3. Retain clusters above I-threshold; drop the rest in long-term cold storage.
4. Apply MDL (#7) as a sanity check: a compaction scheme that requires more bits to describe than it saves is not worth implementing.

**Tooling anchor**: Datadog Log Rehydration policies, AWS CloudWatch Log Groups with Subscription Filters, OpenTelemetry Collector `batch` + `filter` pipeline. Offline: Python sklearn clustering on log embeddings + incident label join.

---

### P6 — Span-Level Redundancy Elimination

**Primitive**: [Redundancy & Compression (#11)](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md), [Mutual Information (#2)](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

**Problem**: Auto-instrumentation libraries (OpenTelemetry Java agent, Node.js auto-instrument) emit many spans per request. In a monolith or co-located microservice cluster, 60–80% of spans may be redundant: they share the same latency, same attributes, and carry no additional diagnostic information beyond what parent spans already contain.

**Approach**: Compute the redundancy R for a candidate child span s given its parent p:

```
R(s|p) = H_max(s) − H(s | p)
       ≈ 1 − I(s; diagnosis) / H(s)
```

where:
- H_max(s) is the max entropy if all span attributes were independent of the parent
- H(s | p) is the conditional entropy of the span's attributes given the parent's attributes
- I(s; diagnosis) is the mutual information between this span's unique attributes and the diagnosis outcome

High R(s|p) → span is nearly deterministically predictable from its parent → strong candidate for inline summarization or removal.

In OpenTelemetry terms: spans where `db.statement`, `http.url`, and `duration_ms` are all predictable from the parent span's attributes and the parent's `duration_ms` are redundant. Collapse them using a Collector `spanmetrics` connector rather than forwarding the raw span.

**Tooling anchor**: OpenTelemetry Collector `spanmetrics` connector, Grafana Tempo span filtering, Honeycomb derived columns for span deduplication. Jaeger dependency graph for visual inspection of redundant hop clusters.

---

### P7 — Sampling Rate as a Rate-Distortion Tradeoff

**Primitive**: [Rate-Distortion (#6)](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md)

**Problem**: Every sampling decision implicitly picks a point on the rate-distortion curve. Uniform sampling at a fixed rate (e.g., 1% head-based sampling) treats all traces as equal in diagnostic value and equal in distortion cost — both assumptions are wrong. The result is simultaneously over-sampling boring traces and under-sampling rare, high-value paths.

**Approach**: Frame sampling as a rate-distortion problem:

```
R(D) = min_{p(x̂|x): E[d(x, x̂)] ≤ D} I(X; X̂)
```

where:
- X: the trace (source)
- X̂: the sampled trace (reconstruction)
- d(x, x̂): distortion = diagnostic loss from not capturing trace x (proxy: severity × rarity)
- R: the sampling rate (bits per trace forwarded to the backend)

Practical allocation:
1. Assign each trace a distortion weight: `w = error_rate × (1 / prior_frequency)`. High-error, rare traces have high distortion weight.
2. Allocate sampling budget R (total traces per second your backend can ingest) to minimize total expected distortion under that budget.
3. High-w traces: sample at 100%. Low-w traces (common, healthy): sample at 0.1%–1%.

This is tail-based sampling with an information-theoretic justification. The key insight: the optimal sampling rate for trace class c is proportional to `√(w_c)` under a squared-error distortion model (water-filling analog from rate-distortion theory).

**Tooling anchor**: OpenTelemetry Collector `tailsampling` processor with policy composition. Honeycomb's Dynamic Sampling (DynSample). Datadog APM Adaptive Sampling. See also `references/sampling-strategies.md`.

---

## Anti-Patterns

### A1 — Logging Every Event "For Debugging" Without an Entropy Check

**Primitive**: [Shannon Entropy (#1)](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

**Symptom**: A logger emits `"Processing item {id}"` for every item in a batch loop. 10,000 items = 10,000 log lines. In Datadog or Splunk, this pattern inflates ingestion costs by 10–100× with near-zero marginal information.

**Why it's wrong**: High volume ≠ high entropy. A log stream that repeats the same template with only an ID varying has entropy H ≈ H(ID distribution). If IDs are uniform random UUIDs, H is technically high — but I(log; useful_outcome) ≈ 0 because no downstream query ever filters on arbitrary item ID. The bits are there, but they carry no actionable signal.

**Fix**: Before adding a log statement, ask: what query will this enable? If the answer is "I'll grep for the ID", confirm the ID appears elsewhere (span attribute, structured event) before adding per-item logging. Apply Pattern P1: measure the template distribution and set a per-logger volume budget. Use structured events with `count` instead of per-item log lines.

---

### A2 — Using Pearson Correlation on Noisy Metric Pairs to Claim Causation

**Primitive**: [Mutual Information (#2)](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

**Symptom**: An engineer plots `cpu_usage` vs `p99_latency` in Grafana, computes Pearson r = 0.62, and reports "CPU causes latency." The same correlation appears between two uncorrelated metrics during a shared traffic surge.

**Why it's wrong**: Pearson correlation measures linear, pairwise, unconditional dependence. It misses nonlinear relationships (the latency spike starts only when CPU > 80%, which is a threshold effect), and it is inflated by shared confounders (traffic volume drives both metrics simultaneously). MI I(CPU; latency) captures all statistical dependence, including nonlinear, but requires careful estimation — naive plug-in estimators are positively biased on small samples (see the anti-pattern in the foundations skill).

**Fix**:
1. Use MI with bootstrap confidence intervals rather than Pearson r for dependency screening.
2. Condition on traffic volume to separate the confounder: compute I(CPU; latency | traffic) using a conditional histogram estimator.
3. Use Granger causality or cross-correlation with lag to suggest causal direction; confirm with load experiments, not correlation coefficients.
4. In Datadog Notebooks or Grafana Explore, add a third variable (request rate) to the scatter before drawing conclusions.

---

### A3 — Alert Thresholds Without Distributional Context

**Primitive**: [KL Divergence (#3)](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

**Symptom**: `ALERT if p99_latency > 500ms`. The threshold was set once during load testing and never revisited. During a weekend traffic trough, the p99 naturally rises to 520ms with no user impact. Noisy alert fires; on-call ignores it.

**Why it's wrong**: A fixed threshold is a degenerate distributional model: it compares one sample from a distribution against a point boundary. The z-score improvement (`(x − μ) / σ`) is better but still assumes Gaussianity. Latency distributions are log-normal or multimodal. A z-score alarm on a bimodal distribution fires during normal regime transitions.

**Fix**: Use D_KL(P_current ‖ P_baseline) as the alarm condition (Pattern P4). KL captures full distributional shift, not just mean/variance movement. Calibrate the threshold on the KL distribution of false-alarm windows (days with no incident) to set a specificity target (e.g., 95th percentile of no-incident KL as the alert floor). JSD is preferable when the baseline distribution itself is updated dynamically, as it is symmetric and bounded in [0, log 2].

---

### A4 — KL Asymmetry Confusion in Drift Detection

**Primitive**: [KL Divergence (#3)](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

**Symptom**: A drift detector computes D_KL(P_baseline ‖ P_current) — baseline as the numerator. It misses the case where P_current places mass in new tail regions that P_baseline never saw, because the forward KL penalizes P_baseline missing P_current's mass, but here the direction is reversed. The detector is blind to tail expansion.

**Why it's wrong**: D_KL(P ‖ Q) = Σ p(x) log[p(x)/q(x)]. When P = baseline and Q = current, this expression is large where the baseline assigns mass that the current distribution does not — it detects shrinkage of coverage. It is **not** large where the current distribution explores new territory the baseline never covered, because those terms have p(x) = 0 and contribute nothing to the sum. Drift via new latency tail expansion goes undetected.

**Fix**:
- For expansion detection (new failure modes, tail growth): compute D_KL(P_current ‖ P_baseline) — current as numerator, baseline as denominator. This fires when P_current places mass where P_baseline has near-zero probability.
- For regression detection (the current distribution no longer covers baseline modes): compute D_KL(P_baseline ‖ P_current).
- For a symmetric alarm that catches both: use JSD = ½ D_KL(P ‖ M) + ½ D_KL(Q ‖ M) with M = ½(P+Q). JSD is bounded in [0, log 2] and has no infinity risk from zero-support mismatches (M always covers both supports).
- Always document which direction you chose and why, in the alert rule's metadata.

---

### A5 — Sampling Decisions Made on Volume, Not Per-Trace Mutual Information

**Primitive**: [Rate-Distortion (#6)](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md), [Mutual Information (#2)](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

**Symptom**: A service sampling policy reads: "keep 1% of all traces, chosen uniformly at random." A checkout service processes 10,000 successful transactions per minute and 2 failed transactions per minute. The policy keeps ~100 successful traces and maybe 0 or 1 failed traces. Incidents involving the 2 failed traces are invisible.

**Why it's wrong**: Uniform sampling treats all traces as equal in information value. Under any reasonable distortion measure where d(failure, no_sample) >> d(success, no_sample), uniform sampling places 99% of its budget on low-distortion traces. The rate-distortion tradeoff is optimized only when sampling rate is proportional to the distortion weight, not proportional to volume.

**Fix**: Implement priority-class sampling:
1. Tag traces at span creation with a priority: error → 100%, slow (> 2× p99 threshold) → 50%, normal → 0.1%.
2. Use the OpenTelemetry Collector `tailsampling` processor with `status_code` and `latency` policies.
3. Allocate the remaining volume budget (after 100%-sampled errors are reserved) to normal traces using the remaining capacity.
4. Review I(trace_class; incident) quarterly and adjust priority weights accordingly (Pattern P7).

---

## Recipes

### R1 — Alert-Noise Audit

**Goal**: Identify low-MI alert rules and silence or raise their thresholds. Reduce weekly alert volume while maintaining incident recall.

**Primitives used**: Shannon Entropy (#1), Mutual Information (#2).

**Inputs**:
- Alert firing log: `(timestamp, rule_name, fired: bool)` for 30 days
- Incident log: `(timestamp, incident_id, resolved_at)` from PagerDuty or OpsGenie

**Steps**:

1. **Build the alert-rule distribution.** Count firings per rule r over 30 days. Compute empirical p(r) = count(r) / total_firings. Compute H(A) = −Σ p(r) log₂ p(r).

2. **Label coincident incidents.** For each alert firing, check whether a confirmed incident opened within ±30 minutes. Create a binary label `incident_coincident ∈ {0, 1}` per firing event.

3. **Compute per-rule MI.** For each rule r, estimate:
   ```
   I(rule_r; incident) = H(incident) − H(incident | rule_r_fired)
   ```
   using the 2×2 contingency table: [fired × incident, fired × no-incident, not-fired × incident, not-fired × no-incident].

4. **Score rules.** Rank rules by MI per firing (MI / frequency). Low MI, high frequency = noise. High MI, low frequency = high-value signal.

5. **Threshold decision**:
   - MI per firing < 0.01 bits AND firing frequency > 10/day: mark for silence or threshold raise.
   - MI per firing > 0.1 bits: preserve regardless of frequency.
   - Between: review with on-call team.

6. **Validate recall before silencing.** Confirm that silenced rules contribute < 5% of incident detections in the historical window using a leave-one-out check.

**Example output** (Prometheus alert rule annotation):
```yaml
- alert: HighMemoryUsage
  annotations:
    mi_per_firing: "0.004"
    firing_frequency_per_day: "23"
    audit_recommendation: "silence — low MI, high noise"
    audit_date: "2026-05-02"
```

**Tooling**: Datadog alert history CSV export, OpsGenie schedule API, Python `scipy.stats.entropy` + `sklearn.metrics.mutual_info_score`. Prometheus query: `count_over_time(ALERTS{alertstate="firing"}[30d])`.

---

### R2 — Sampling Budget by Service

**Goal**: Allocate a fixed trace-ingestion budget (total spans/second to backend) across services to maximize total information about incidents under that budget.

**Primitives used**: Shannon Entropy (#1), Rate-Distortion (#6).

**Inputs**:
- Per-service span volume: `spans_per_second[service]`
- Per-service incident-relevant entropy: H(service) estimated from the distribution of span outcome classes (success, client-error, server-error, slow, timeout)
- Total budget: B spans/second (Honeycomb, Tempo, or Jaeger ingest limit)

**Steps**:

1. **Estimate per-service entropy.** For each service, group spans into outcome buckets and compute:
   ```
   H(svc) = −Σ_{outcome} p(outcome|svc) · log₂ p(outcome|svc)
   ```
   Services with H close to log₂(5) ≈ 2.32 bits (all outcomes equally likely) are informationally rich. Services with H ≈ 0 (all spans are successes) are low-value.

2. **Compute information rate.** Multiply H(svc) by the volume to get raw information throughput:
   ```
   info_rate(svc) = H(svc) × spans_per_second(svc)
   ```

3. **Allocate under budget.** To maximize total information retained under budget B, allocate sampling rate s(svc) ∈ [0, 1] per service to solve:
   ```
   maximize Σ_{svc} s(svc) · info_rate(svc)
   subject to: Σ_{svc} s(svc) · spans_per_second(svc) ≤ B
   ```
   This is a fractional knapsack: sort by info_rate / spans_per_second = H(svc) per span, and fill greedily from the highest-entropy-per-span services until budget is exhausted. High-H services get s = 1.0 (or 100% tail-sample priority). Low-H services get s = remaining_budget / their_volume.

4. **Floor for rare failures.** Override: any service with server-error rate > 0.1% gets s_error_class = 1.0 regardless of entropy score (rate-distortion distortion weight floor).

5. **Apply in Collector config.** Set `tailsampling` processor policies with computed rates per service name attribute.

**Example allocation** (3 services, budget = 500 spans/s):

| Service | Volume (spans/s) | H(svc) | H/span | Allocated rate |
|---------|-----------------|--------|--------|----------------|
| checkout-api | 100 | 2.1 bits | 2.1 | 100% (full) |
| catalog-svc | 5,000 | 0.3 bits | 0.3 | 8% |
| health-check | 10,000 | 0.01 bits | 0.01 | 0% (dropped) |

**Tooling**: OpenTelemetry Collector `tailsampling` processor, Honeycomb DynSample, Datadog APM ingestion controls. Prometheus `otelcol_processor_tail_sampling_*` metrics to monitor budget adherence.

---

### R3 — Drift Detection on Latency Distributions

**Goal**: Detect distributional shift in service latency before it reaches SLO burn-rate thresholds, using KL divergence on Prometheus histogram data. Bound downstream impact using Fano's inequality.

**Primitives used**: KL Divergence (#3), Fano's Inequality (#9).

**Inputs**:
- Prometheus `http_request_duration_seconds_bucket` with `le` labels (histogram)
- 7-day rolling baseline window P
- Daily evaluation window P_t (last 24 hours)
- Incident labels from the past 90 days (for Fano bound calibration)

**Steps**:

1. **Extract baseline distribution P.** Query Prometheus for the normalized bucket histogram over the baseline window:
   ```promql
   increase(http_request_duration_seconds_bucket{job="checkout-api"}[7d])
   ```
   Normalize to probabilities: `p_0(b) = count(b) / total_count`.

2. **Extract today's distribution P_t.** Same query over the last 24 hours.

3. **Compute KL divergence.** For each bucket b:
   ```
   D_KL(P_t ‖ P_0) = Σ_b p_t(b) · log₂[p_t(b) / p_0(b)]
   ```
   Add Laplace smoothing (add ε = 1e-9 to all buckets) before division to avoid log(0).

4. **Alert tiers** (calibrate thresholds on 90-day no-incident baseline):
   ```
   KL < 0.05 nats  →  nominal, no action
   0.05–0.20 nats  →  INFO: slow degradation possible, check dashboards
   0.20–0.50 nats  →  WARN: page secondary, attach KL value and P_t histogram
   > 0.50 nats     →  CRIT: page primary, escalate per incident runbook
   ```

5. **Compute Fano impact bound.** If the downstream incident classifier uses latency features, Fano's inequality gives a lower bound on its error rate:
   ```
   P_e ≥ (H(incident | latency_features) − 1) / log₂|incident_classes|
   ```
   High residual entropy H(incident | latency_features) means the latency shift alone cannot reliably predict incident type — additional signals (error rate, saturation) must be correlated before routing the page.

6. **Alert annotation.** Attach the KL value, the histogram shift visualization (P_0 vs P_t overlaid), and the Fano bound to the alert body for the on-call engineer.

**Example Prometheus recording rule**:
```yaml
groups:
  - name: latency_drift
    rules:
      - record: job:latency_kl_divergence:daily
        expr: |
          sum by (job, le) (
            increase(http_request_duration_seconds_bucket[1d])
          )
        # Post-process in Python or Grafana panel to compute KL from normalized buckets

      - alert: LatencyDistributionDrift
        expr: latency_kl_divergence_score > 0.20
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Latency distribution has drifted (KL={{ $value | humanize }} nats)"
          runbook: "https://wiki/runbooks/latency-drift"
```

**Tooling**: Prometheus histograms, Grafana Heatmap for P_0 vs P_t visualization, Python `scipy.special.rel_entr` for offline KL computation, Datadog Distribution Metrics with `p50`/`p95`/`p99` track for cross-validation.

---

## Composition

These patterns and recipes compose with each other and with the foundations skill's composition recipes:

| Starting point | Add | Result |
|---|---|---|
| R1 (alert-noise audit) | P2 (MI scoring) | Alert rule MI score → Alertmanager `inhibit_rules` driven by computed MI, not manual intuition |
| R2 (sampling budget) | P7 (rate-distortion) | Water-filling allocation replaces the greedy knapsack when service entropies and volumes are correlated |
| R3 (KL drift) | P5 (IB log compaction) | When KL > WARN threshold, trigger elevated log retention for the drifting service — IB parameter β shifts to retain more until incident resolves |
| P3 (cardinality budgets) | P6 (span redundancy) | Cardinality budget sets the ceiling; redundancy analysis identifies which attributes to keep within that ceiling |
| P4 (KL anomaly) + P5 (IB compaction) | R3 (drift recipe) | Full pipeline: drift triggers increased retention, IB filters for incident-predictive logs within the retained set |

For multi-signal compositions (latency drift + error rate + saturation), apply the context-window budget recipe from the foundations skill: rank signals by I(signal; incident), prune redundant signals using conditional entropy H(signal_i | signal_j), and allocate dashboard real-estate and alert budget proportionally.

---

## Sources

Primitive playbooks (canonical references for all formulas above):

- [`01-shannon-entropy.md`](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md) — H(X) definition, discrete/continuous, failure modes
- [`02-mutual-information.md`](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md) — I(X;Y), estimation bias, MINE/NWJ estimators
- [`03-kl-divergence.md`](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md) — D_KL, asymmetry, JSD, forward vs reverse
- [`05-channel-capacity.md`](../../foundations-information-theory/assets/templates/information-theory/05-channel-capacity.md) — C = max I(X;Y), throughput ceiling reasoning
- [`06-rate-distortion.md`](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md) — R(D), Blahut-Arimoto, Gaussian case
- [`07-mdl-principle.md`](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md) — MDL = L(M) + L(D|M), model selection
- [`08-information-bottleneck.md`](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md) — IB objective, β parameter, phase transitions
- [`09-fano-inequality.md`](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md) — P_e lower bound from residual entropy
- [`11-redundancy-compression.md`](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md) — R = H_max − H(X), compression budget

External primary sources (verify versions and availability before citing in production runbooks):

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed. — foundational formulas, KL and MI definitions.
- OpenTelemetry Collector documentation: tail sampling processor — https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor
- Prometheus documentation: histogram and recording rules — https://prometheus.io/docs/practices/histograms/
- Honeycomb documentation: Dynamic Sampling — https://docs.honeycomb.io/manage-data-volume/sampling/
- Datadog documentation: Log Pattern Analysis — https://docs.datadoghq.com/logs/explorer/analytics/patterns/
- Grafana Tempo documentation: tag cardinality — https://grafana.com/docs/tempo/latest/

Sibling references in this skill:
- `references/sampling-strategies.md` — sampling primitives and tail-sampling configuration
- `references/alerting-strategies.md` — alert rule design, multi-window burn rate
- `references/log-aggregation-patterns.md` — log pipeline design and cost control
- `references/anti-patterns-best-practices.md` — observability anti-pattern catalog
