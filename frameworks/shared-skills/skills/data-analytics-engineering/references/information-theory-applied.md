# Information Theory Applied to Analytics Engineering

> **Gate before invoking:** Check [`foundations-information-theory` § When to Apply](../../foundations-information-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


> Purpose: Translate information-theory primitives into concrete patterns for dbt pipelines, warehouse analytics, and event data. Freshness anchor: May 2026.

---

## Table of Contents

- [Primitive Coverage Map](#primitive-coverage-map)
- [Patterns](#patterns)
  - [P1: Feature Selection via Mutual Information](#p1-feature-selection-via-mutual-information)
  - [P2: Anomaly Detection via Entropy and KL Drift on Event Distributions](#p2-anomaly-detection-via-entropy-and-kl-drift-on-event-distributions)
  - [P3: Schema-Change Drift Detection via KL on Field-Value Distributions](#p3-schema-change-drift-detection-via-kl-on-field-value-distributions)
  - [P4: Data-Quality Scoring via Field Entropy](#p4-data-quality-scoring-via-field-entropy)
  - [P5: Compression-Based Cohort Segmentation via MDL](#p5-compression-based-cohort-segmentation-via-mdl)
  - [P6: Channel-Capacity Reasoning for Data Pipelines](#p6-channel-capacity-reasoning-for-data-pipelines)
  - [P7: Cross-Source Event-Stream Caveats](#p7-cross-source-event-stream-caveats)
- [Anti-Patterns](#anti-patterns)
  - [A1: Pearson Correlation as Feature-Importance Proxy](#a1-pearson-correlation-as-feature-importance-proxy)
  - [A2: KL Asymmetry Misuse in Drift Dashboards](#a2-kl-asymmetry-misuse-in-drift-dashboards)
  - [A3: High-Cardinality Entropy Without Bias Correction](#a3-high-cardinality-entropy-without-bias-correction)
  - [A4: Raw Event Volume as Proxy for Information](#a4-raw-event-volume-as-proxy-for-information)
  - [A5: Cross-Version Perplexity Comparisons for Generative Models](#a5-cross-version-perplexity-comparisons-for-generative-models)
- [Recipes](#recipes)
  - [R1: Feature Selection for an ML Pipeline](#r1-feature-selection-for-an-ml-pipeline)
  - [R2: Schema-Drift Alerting with Fano-Style Error Bound](#r2-schema-drift-alerting-with-fano-style-error-bound)
  - [R3: Cohort Segmentation by MDL of Behavior Sequences](#r3-cohort-segmentation-by-mdl-of-behavior-sequences)
- [Composition: Layering Primitives in a Quality Pipeline](#composition-layering-primitives-in-a-quality-pipeline)
- [Sources](#sources)

---

## Primitive Coverage Map

| Primitive | # | Applied in Patterns / Recipes |
|-----------|---|-------------------------------|
| Shannon Entropy | 1 | P2, P4, R1, R2, R3 |
| Mutual Information | 2 | P1, R1 |
| KL Divergence | 3 | P2, P3, R2 |
| Cross-Entropy / Perplexity | 4 | P7, A5 |
| Channel Capacity | 5 | P6 |
| Rate-Distortion | 6 | P6 |
| MDL Principle | 7 | P5, R1, R3 |
| Information Bottleneck | 8 | P1 |
| Fano's Inequality | 9 | R2 |
| Typical Sets / AEP | 10 | P6 |
| Redundancy and Compression | 11 | P5, R3 |

Full primitive playbooks: [`../../foundations-information-theory/assets/templates/information-theory/`](../../foundations-information-theory/assets/templates/information-theory/)

---

## Patterns

### P1: Feature Selection via Mutual Information

**Problem.** Candidate features for a churn or conversion model are ranked by Pearson correlation with the target. Non-linear features are systematically undervalued; correlated feature pairs both enter the model, wasting capacity.

**Information-theory grounding.** Mutual information I(X;Y) = H(X) − H(X|Y) measures how many bits of target uncertainty a feature resolves, regardless of whether the relationship is linear (#2). Features that produce the same I(X;Y) and high I(X;other_features) are redundant and one can be dropped without information loss.

**Warehouse workflow.**

```sql
-- Step 1: compute empirical frequency tables for each candidate feature
-- against the binary target (churned = 1/0) in the marts layer.
-- Use decile bucketing for continuous features to keep the contingency
-- table manageable (10 bins × 2 target classes = 20 cells).
SELECT
    NTILE(10) OVER (ORDER BY days_since_last_login) AS days_bucket,
    churned,
    COUNT(*) AS n
FROM mart_user_features
GROUP BY 1, 2

-- Step 2: pass the contingency table to a Python dbt test or
-- an external Python step that computes:
--   MI(feature, target) with Paninski bias correction
--   NMI = MI / sqrt(H(feature) * H(target))   [normalized, 0–1]
```

**Decision rule.** Rank features by NMI. Add to the shortlist in NMI-descending order. Stop adding feature i if I(feature_i; already_selected) / I(feature_i; target) > 0.7 — the feature is mostly redundant. This is a greedy approximation to information-bottleneck compression (#8).

**Bias correction note.** For a contingency table with m × n cells and N total samples, the plug-in MI estimate has upward bias ≈ (m−1)(n−1)/(2N). Apply the Paninski correction before ranking. At n < 5,000 rows, inflated MI values can elevate noise features above informative ones.

**dbt integration.** Implement as a dbt macro or model-level Python test that reads the mart, builds contingency tables per feature column, and emits a `feature_mi_scores` seed. Gate the ML pipeline on `NMI > 0.05` to suppress zero-information features before model training.

**See.** [02-mutual-information.md](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md), [07-mdl-principle.md](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md), [08-information-bottleneck.md](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md)

---

### P2: Anomaly Detection via Entropy and KL Drift on Event Distributions

**Problem.** An event pipeline (`page_view`, `checkout_started`, `payment_completed`) emits varying volumes each day. You need to detect anomalies that are not merely volume changes — a schema bug that collapses all `event_type` values to one, or a tracking regression that floods one event type.

**Information-theory grounding.** Compute the Shannon entropy H(event_type distribution) of the daily event-type distribution (#1). A healthy distribution is spread across event types; a bug concentrates mass. Separately, compute D_KL(today_distribution ‖ baseline_distribution) to measure direction-aware drift from the rolling 30-day baseline (#3).

**SQL pattern.**

```sql
-- Build daily event-type frequency table
WITH daily AS (
    SELECT
        event_date,
        event_type,
        COUNT(*) AS n,
        SUM(COUNT(*)) OVER (PARTITION BY event_date) AS daily_total
    FROM events
    GROUP BY 1, 2
),
probabilities AS (
    SELECT
        event_date,
        event_type,
        n / daily_total AS p
    FROM daily
),
entropy AS (
    SELECT
        event_date,
        -SUM(p * LOG(p)) / LOG(2) AS entropy_bits   -- Shannon entropy in bits
    FROM probabilities
    GROUP BY 1
)
SELECT * FROM entropy
ORDER BY event_date
```

```sql
-- KL divergence: today vs. 30-day baseline
-- Add Laplace smoothing (ε = 1/total_events) to avoid log(0)
WITH baseline AS (
    SELECT event_type, (COUNT(*) + 1.0) / SUM(COUNT(*) + 1.0) OVER () AS q
    FROM events
    WHERE event_date BETWEEN CURRENT_DATE - 30 AND CURRENT_DATE - 1
    GROUP BY 1
),
today AS (
    SELECT event_type, (COUNT(*) + 1.0) / SUM(COUNT(*) + 1.0) OVER () AS p
    FROM events
    WHERE event_date = CURRENT_DATE
    GROUP BY 1
)
SELECT
    SUM(t.p * LOG(t.p / b.q)) / LOG(2) AS kl_divergence_bits
FROM today t
JOIN baseline b USING (event_type)
```

**Alert threshold.** Alert when `kl_divergence_bits > 0.5` or `entropy_bits < (0.6 × max_historical_entropy)`. The entropy floor catches distribution collapse; the KL threshold catches distributional shift. Tune both per pipeline based on acceptable false-positive rate.

**dbt integration.** Implement as a dbt source freshness extension or an Elementary custom metric. Log `entropy_bits` and `kl_divergence_bits` to a monitoring mart; graph them alongside event volume.

**See.** [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md), [03-kl-divergence.md](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

---

### P3: Schema-Change Drift Detection via KL on Field-Value Distributions

**Problem.** An upstream table changes its encoding for a categorical column — for example, `country_code` switches from ISO 3166-1 alpha-2 ("GB") to alpha-3 ("GBR"), or a `status` field gains new values. Row counts and null checks pass. Silent semantic drift reaches downstream marts.

**Information-theory grounding.** Compute D_KL(today_field_distribution ‖ reference_field_distribution) for categorical columns after each load (#3). Schema changes that redistribute mass across values show up as large KL even when row counts are identical. Compare forward and reverse KL: a large D_KL(today ‖ ref) with small D_KL(ref ‖ today) indicates new values not in the reference; a large reverse divergence indicates reference values disappearing from today.

**SQL pattern.**

```sql
-- Reference snapshot (last stable run, stored as a seed or snapshot model)
-- Today's distribution
WITH ref AS (
    SELECT field_value, freq / total AS q
    FROM ref_field_value_counts
    CROSS JOIN (SELECT SUM(freq) AS total FROM ref_field_value_counts)
),
today AS (
    SELECT
        COALESCE(field_value, '__null__') AS field_value,
        COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS p
    FROM staging_table
    GROUP BY 1
)
SELECT
    SUM(t.p * LOG(t.p / COALESCE(r.q, 0.001))) / LOG(2) AS kl_forward,
    SUM(r.q * LOG(r.q / COALESCE(t.p, 0.001))) / LOG(2) AS kl_reverse
FROM today t
FULL OUTER JOIN ref r USING (field_value)
```

**Alert logic.** `kl_forward > 1.0 bits` → new values appearing (possible upstream encoding change). `kl_reverse > 1.0 bits` → values disappearing (possible data loss or enum pruning). Both together: full schema reformat.

**Scope.** Apply to high-cardinality categorical fields on staging models that feed contracted marts. Do not apply to free-text fields (entropy is near-maximal and noisy) or primary keys (cardinality too high for stable distributions).

**See.** [03-kl-divergence.md](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md), [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

---

### P4: Data-Quality Scoring via Field Entropy

**Problem.** A mart has 80 columns. The team needs to prioritize which fields to document, test, and govern. High-null or near-constant fields are low value; high-entropy fields with diverse, informative values are high value.

**Information-theory grounding.** Shannon entropy H(field) measures how much information a field carries (#1). A field that is 95% NULL has near-zero entropy — it contributes almost no information to downstream consumers. A field with uniform distribution across 100 values has log₂(100) ≈ 6.6 bits — maximum entropy for its cardinality.

**Relative entropy score.**

```
quality_score(field) = H(field) / log₂(distinct_values(field))
```

This is normalized entropy, ranging from 0 (constant or all-null) to 1 (uniform distribution). Fields with `quality_score < 0.1` warrant investigation: they are either near-constant (remove or demote) or near-all-null (add a NOT NULL contract if they should be populated).

**SQL implementation.**

```sql
-- For each column, compute entropy from value frequency distribution
-- Example for a single column; wrap in a macro to sweep all columns
WITH freq AS (
    SELECT
        payment_method,
        COUNT(*) AS n,
        COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS p
    FROM mart_payments
    GROUP BY 1
),
entropy_calc AS (
    SELECT
        'payment_method'                          AS field_name,
        -SUM(p * LOG(p)) / LOG(2)                AS entropy_bits,
        LOG(COUNT(*)) / LOG(2)                    AS max_entropy_bits,
        (-SUM(p * LOG(p)) / LOG(2))
            / NULLIF(LOG(COUNT(*)) / LOG(2), 0)   AS relative_entropy
    FROM freq
)
SELECT * FROM entropy_calc
```

**Governance integration.** Emit a `field_entropy_profile` model. Join against the ownership catalog to flag fields owned by senior stakeholders with `relative_entropy < 0.1` — these are documentation priorities or candidates for deprecation. Use as an input to the data quality incident runbook (`assets/data-quality-incident-runbook.md`).

**Caveat.** Entropy measures information content, not correctness. A field with high entropy could be high-quality or could be a free-text junk column. Combine with a cardinality check and a NOT NULL rate.

**See.** [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

---

### P5: Compression-Based Cohort Segmentation via MDL

**Problem.** You have user behavior sequences — ordered lists of event types per session. You want to find the natural number of cohorts k without imposing a distance metric or assuming cluster shapes. Standard k-means requires a feature vector and a distance function; behavior sequences are variable-length and resist embedding.

**Information-theory grounding.** MDL (#7) treats model selection as description-length minimization. A clustering of k cohorts is better if the total description length L(model) + L(data|model) is shorter. Encode the model as the k representative sequences; encode data given the model as the compressed residuals. The k that minimizes total description length is the natural segmentation. Redundancy / compression (#11) frames the codec for residual encoding.

**Workflow.**

1. Encode each user's session as a string of event-type tokens (e.g., `"home→search→pdp→cart→checkout"`).
2. For candidate k in {2, 3, …, 12}:
   a. Run k-means or k-medoids on NCD-based distances (primitive #11, NCD = normalized compression distance between sequence pairs using zstd).
   b. Compute MDL(k) = L(k centroids, encoded as LZ-compressed representative strings) + Σ L(user_sequence | nearest_centroid, encoded as compressed residual from centroid).
3. Plot MDL(k) vs k. Pick the k at the elbow — where adding another cluster reduces L(data|model) less than it adds to L(model).

**Practical shortcut in SQL/dbt.** Encode sessions as fixed-length event-count vectors (e.g., COUNT of each of 20 event types) and use BIC as an MDL approximation. BIC ≈ -2·log(likelihood) + k·log(n) (primitive #7 worked example). Fit via an external Python step; write cluster assignments back as a dbt seed.

**Key property.** MDL-based segmentation penalizes overfitting automatically. A cluster that covers three users does not reduce description length enough to justify its existence — it will be merged into the MDL-optimal solution.

**See.** [07-mdl-principle.md](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md), [11-redundancy-compression.md](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md)

---

### P6: Channel-Capacity Reasoning for Data Pipelines

**Problem.** An ETL stage receives 500M raw events/day but downstream models only consume ~20M enriched records. Engineers keep increasing pipeline throughput without asking whether the extra events carry proportional information.

**Information-theory grounding.** Channel capacity C = max I(input; output) bounds the useful information a pipeline stage can pass through (#5). If the event stream has entropy rate H_rate nats per event (#10, Typical Sets / AEP), then beyond C events per second the extra events are statistically redundant — same information content but higher cost. Rate-distortion (#6) frames the tradeoff: you can emit fewer events at some acceptable distortion D and still reconstruct the useful signal.

**Capacity estimation.**

```
Effective events/day that carry new information
  ≈ 2^{H_rate_per_event} × (number of distinct event contexts)
```

Compare against actual event volume. If actual volume / effective events >> 10×, the pipeline is transmitting high redundancy. Candidates for event deduplication, aggregation, or sampling.

**Practical warehouse check.**

```sql
-- Estimate event-type transition entropy (proxy for H_rate)
WITH bigrams AS (
    SELECT
        event_type                                   AS e1,
        LEAD(event_type) OVER (
            PARTITION BY session_id ORDER BY event_timestamp
        )                                            AS e2,
        COUNT(*) OVER (PARTITION BY event_type)      AS n_e1
    FROM events
    WHERE event_date = CURRENT_DATE - 1
),
p_e2_given_e1 AS (
    SELECT e1, e2,
           COUNT(*) * 1.0 / MAX(n_e1) AS p
    FROM bigrams
    WHERE e2 IS NOT NULL
    GROUP BY 1, 2
),
conditional_entropy AS (
    SELECT e1, -SUM(p * LOG(p)) / LOG(2) AS h_e2_given_e1
    FROM p_e2_given_e1
    GROUP BY 1
)
SELECT AVG(h_e2_given_e1) AS avg_conditional_entropy_bits
FROM conditional_entropy
```

A low `avg_conditional_entropy_bits` (< 1 bit) means event transitions are highly predictable — the stream carries low information per event relative to volume. This is a signal to introduce micro-batch aggregation or to sample events before loading.

**See.** [05-channel-capacity.md](../../foundations-information-theory/assets/templates/information-theory/05-channel-capacity.md), [10-typical-sets-aep.md](../../foundations-information-theory/assets/templates/information-theory/10-typical-sets-aep.md), [06-rate-distortion.md](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md)

---

### P7: Cross-Tokenizer and Cross-Vendor Event-Stream Caveats

**Problem.** Two product surfaces emit "equivalent" events — web uses a JavaScript tracker that fires one `page_view` per route change; mobile uses a native SDK that fires one `screen_view` per screen render. A funnel mart joins them and counts total `view` events. Metrics diverge across segments with different platform mixes.

**Information-theory grounding.** Cross-entropy / perplexity comparisons are only valid under the same "tokenizer" — the same event schema and emission semantics (#4). Different SDKs and platforms produce different effective sequence lengths for the same user journey, directly analogous to the cross-tokenizer perplexity problem in language models. Normalizing by bits-per-byte (BPB) translates to normalizing event counts by a "session-normalized" base unit.

**Normalization pattern.**

Instead of summing raw events, normalize by canonical session steps:

```sql
-- Normalize web and mobile events to a common "step" unit
-- before joining into funnel metrics
SELECT
    user_id,
    platform,
    -- Web fires per route; mobile fires per screen — treat both as 1 step
    COUNT(DISTINCT CASE
        WHEN platform = 'web'    THEN page_path
        WHEN platform = 'mobile' THEN screen_name
    END) AS canonical_steps,
    COUNT(*) AS raw_events
FROM events
GROUP BY 1, 2
```

**Cross-vendor KL check.** Before merging two event streams, compute D_KL(stream_A_event_distribution ‖ stream_B_event_distribution). A large divergence signals that the two streams have different base distributions and should be kept in separate mart columns or flagged in the metric contract.

**Governance rule.** Any metric contract (`assets/metric-dictionary.md`) that joins multi-platform event streams must document: the normalization unit, which platforms are in scope, and whether raw counts or session-normalized counts are used.

**See.** [04-cross-entropy.md](../../foundations-information-theory/assets/templates/information-theory/04-cross-entropy.md), [03-kl-divergence.md](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

---

## Anti-Patterns

### A1: Pearson Correlation as Feature-Importance Proxy

**Symptom.** Feature selection for an ML pipeline selects features with the highest `ABS(pearson_corr(feature, target))`. Non-linear features — e.g., `days_since_last_login` with a threshold effect at 30 days — rank low. The model misses the most predictive signal.

**Why it fails.** Pearson correlation captures only linear dependence. Mutual information I(X;Y) captures all statistical dependence including monotone, threshold, and interaction effects. A feature with `pearson_corr ≈ 0` can have `I(X;Y) >> 0` if it partitions the target non-linearly.

**Fix.** Replace the correlation-based ranking with MI (see Pattern P1). Use NMI for bounded comparison. Apply Paninski or JVHW bias correction when n < 10,000 and cardinality is high.

**See.** [02-mutual-information.md](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

---

### A2: KL Asymmetry Misuse in Drift Dashboards

**Symptom.** A drift dashboard tracks `KL(today ‖ baseline)` and fires an alert. An engineer switches the direction to `KL(baseline ‖ today)` for a different pipeline without updating the threshold or the interpretation. Alerts fire at different sensitivities; the team loses trust in the monitor.

**Why it fails.** D_KL(P‖Q) penalizes P for assigning mass where Q assigns near-zero — it is sensitive to new categories appearing. D_KL(Q‖P) penalizes Q for assigning mass where P assigns near-zero — it is sensitive to old categories disappearing. The two measures have different scales and different false-positive profiles. Using them interchangeably produces incoherent drift signals.

**Fix.** Pick the direction intentionally: use `KL(today ‖ baseline)` to detect new mass (new event types, new field values); use `KL(baseline ‖ today)` to detect disappearing mass (deprecated values, data loss). Document the direction in the alert definition. If direction does not matter, use JSD = 0.5·KL(P‖M) + 0.5·KL(Q‖M) where M = 0.5·(P+Q) — JSD is symmetric and bounded in [0, 1].

**See.** [03-kl-divergence.md](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md)

---

### A3: High-Cardinality Entropy Without Bias Correction

**Symptom.** A data-quality score is computed as entropy across a `user_id` column with 1M unique values from a 1.1M row sample. The entropy reports 19.8 bits — nearly log₂(1M) = 19.9 bits. The field is flagged as high-quality. In reality, the plug-in entropy estimate is inflated by the Paninski bias for high-cardinality, near-unique fields.

**Why it fails.** For a sample of N observations over k bins, the plug-in entropy estimate has upward bias ≈ (k−1)/(2N). For k = 1M bins and N = 1.1M rows, bias ≈ 999,999 / 2,200,000 ≈ 0.45 bits. Near-unique identifiers have structurally inflated entropy estimates regardless of the true underlying distribution. Treating near-unique fields as "high information" conflates cardinality with informativeness.

**Fix.** Before computing entropy for quality scoring: (a) exclude near-unique fields (distinct_count / total_rows > 0.9) from entropy-based scoring — they are identifiers, not features; (b) apply Miller-Madow correction (`Ĥ_corrected = Ĥ_plugin − (k−1)/(2N)`) for moderate-cardinality fields; (c) prefer relative entropy (entropy / log₂(distinct_count)) to normalize across cardinalities.

**See.** [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md), [02-mutual-information.md](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md)

---

### A4: Raw Event Volume as Proxy for Information

**Symptom.** A weekly data health report tracks "events ingested" as the primary signal of pipeline health. A tracking bug doubles the volume of `page_view` events (each scroll fires two events instead of one). The health report goes green. KPIs derived from event counts are inflated.

**Why it fails.** Event volume is not event information. If every `page_view` event is a near-duplicate of the previous one, the marginal information content of each additional event approaches zero — its conditional entropy H(event_n | event_{n-1}) ≈ 0. More volume from a deterministic duplication bug does not add entropy to the stream; it adds redundancy (#11).

**Fix.** Track `entropy_bits` of the daily event-type distribution alongside raw volume (see Pattern P2). Alert when volume increases but entropy decreases — the canonical signal for duplication or distribution collapse. Add a `distinct_session_events / total_events` ratio as a redundancy proxy.

**See.** [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md), [11-redundancy-compression.md](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md)

---

### A5: Treating Perplexity as Comparable Across Model Versions

**Symptom.** A team fine-tunes an LLM product feature (e.g., a recommendation model or a natural-language query layer) and reports that version 2 has lower perplexity than version 1. Version 2 also changed the tokenizer. The comparison is invalid.

**Why it fails.** Perplexity = 2^{H(P,Q)} is conditioned on a specific vocabulary and tokenization scheme (#4). Two models that tokenize the same text into different sequence lengths produce structurally incomparable perplexity scores — shorter sequences inflate perplexity; longer sequences deflate it — even when information content is identical.

**Fix.** Normalize to bits-per-byte (BPB = cross-entropy / number of UTF-8 bytes in the evaluation corpus). BPB is tokenizer-agnostic. If the model does not expose per-token log-probabilities over raw bytes, use a fixed reference tokenizer across all versions. Document the normalization choice in the metric contract and alert on any version comparison that changes the tokenizer without re-deriving the baseline BPB.

**See.** [04-cross-entropy.md](../../foundations-information-theory/assets/templates/information-theory/04-cross-entropy.md)

---

## Recipes

### R1: Feature Selection for an ML Pipeline

**Goal.** Given a candidate pool of 50–200 warehouse columns, produce a shortlisted, de-duplicated feature set ranked by information content relative to a binary target (e.g., `churned`, `converted`), with bias correction and an MDL-based cutoff.

**Inputs.** A dbt mart with candidate feature columns and a target column. N ≥ 5,000 rows recommended.

**Steps.**

```
1. PREPARE
   - Pull the mart into a Python environment (dbt Python model or external step).
   - Bucket continuous columns into deciles (10 bins).
   - Encode nulls as a distinct bin value ('__null__').
   - Verify: N rows, k bins per feature, target is binary.
   → verify: each feature has ≥ 10 non-null rows per target class.

2. COMPUTE MI WITH BIAS CORRECTION  [Primitives #1, #2]
   For each candidate feature X:
     a. Build contingency table C[x_bin, target].
     b. Compute plug-in I(X;target) = Σ p(x,y) log(p(x,y)/p(x)p(y)).
     c. Apply Paninski correction:
          I_corrected = I_plugin − (m−1)(n−1) / (2N)
          where m = bins, n = 2 (binary target), N = rows.
     d. Normalize: NMI = I_corrected / sqrt(H(X) * H(target)).
   → verify: NMI ∈ [0, 1]; any NMI > 1 after correction signals estimation error — increase N.

3. RANK AND GREEDY SELECT  [Primitive #7 MDL framing]
   Sort features by NMI descending.
   Initialize selected = [top feature].
   For each remaining feature i (in NMI order):
     redundancy_ratio = I(feature_i; selected_features) / I(feature_i; target)
     If redundancy_ratio < 0.7: add to selected.
     Else: log as redundant with the feature it overlaps most.
   → verify: |selected| ≤ 30 for a typical churn model; if > 30, tighten threshold to 0.5.

4. MDL SHORTLIST CHECK  [Primitive #7]
   Compute approximate MDL(k) for the selected set:
     MDL = -2 * log_likelihood(logistic on k features) + k * log(N)
   Add features while MDL decreases. Stop at MDL minimum.
   → verify: MDL(k+1) > MDL(k) — confirms you are past the information gain / complexity tradeoff.

5. OUTPUT
   Write feature_mi_scores to a dbt seed:
     [feature_name, nmi, entropy_bits, redundancy_ratio, in_shortlist]
   Gate the ML training step on features where in_shortlist = true.
```

**Expected output.** 10–30 de-duplicated features ranked by NMI; redundant feature pairs flagged; MDL elbow identified. Typical NMI range for strong churn predictors: 0.05–0.35.

**See.** [02-mutual-information.md](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md), [07-mdl-principle.md](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md), [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

---

### R2: Schema-Drift Alerting with Fano-Style Error Bound

**Goal.** Alert on schema drift in a critical staging table — not just missing values or type changes, but distributional shifts in field values that will silently degrade downstream model accuracy. Bound the model error increase implied by the drift using Fano's inequality.

**Inputs.** A staging model with a reference distribution snapshot (stored as a dbt seed or snapshot model) and a daily incremental load.

**Steps.**

```
1. ESTABLISH BASELINE  [Primitive #3 KL, Primitive #1 Entropy]
   For each monitored categorical column:
     a. Compute reference distribution Q: {value: freq/total} over the last stable 30 days.
     b. Compute reference entropy H_ref = -Σ q(v) log₂ q(v).
     c. Store in a seed: ref_field_distributions.csv.
   → verify: each column has ≥ 20 distinct values in the reference; columns with < 20 values
     are too sparse for reliable KL — use chi-square test instead.

2. DAILY KL COMPUTATION  [Primitive #3]
   For each daily increment:
     a. Compute today's distribution P with Laplace smoothing:
          p(v) = (count(v) + ε) / (total + |vocab| * ε)   where ε = 1.
     b. Compute KL_forward = Σ p(v) * log₂(p(v) / q(v)).
     c. Compute KL_reverse = Σ q(v) * log₂(q(v) / p(v)).
   → verify: KL_forward and KL_reverse are finite (no division by zero; ε handles this).

3. FANO BOUND ON DOWNSTREAM MODEL ERROR  [Primitive #9]
   For the most drifted column (highest KL_forward):
     a. Estimate H(target | drifted_column_today) using:
          H_degraded ≈ H_ref_conditional + KL_forward
          (first-order approximation: drift adds bits to residual conditional entropy)
     b. Apply Fano lower bound:
          P_e_lower ≥ (H_degraded − 1) / log₂(|target_classes|)
     c. Compare to P_e_lower from the reference period.
     The difference ΔP_e is the minimum additional model error attributable to the drift.
   → verify: if ΔP_e > 0.05 (5 percentage points), escalate to a data quality incident;
     the drift is large enough to materially degrade downstream model performance.

4. ALERT ROUTING
   KL_forward ∈ (0.2, 1.0]:  INFO — distributional shift, monitor.
   KL_forward > 1.0:          WARN — schema change likely; block mart refresh if ΔP_e > 0.05.
   KL_reverse > 2.0:          WARN — values disappearing; potential data loss.
   ΔP_e > 0.10:               CRITICAL — escalate to data quality incident runbook.
   → verify: alerts route to the column owner from the ownership catalog.

5. OUTPUT
   daily_schema_drift model:
     [run_date, column_name, kl_forward, kl_reverse, h_ref, h_today, pe_lower_bound_delta, alert_level]
```

**Strongest property of this recipe.** The Fano-derived `ΔP_e` converts an abstract KL number into a concrete model-error statement that product and ML stakeholders can act on — "this drift will cost at least 7 percentage points of accuracy" is more actionable than "KL = 1.3."

**See.** [03-kl-divergence.md](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md), [09-fano-inequality.md](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md), [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

---

### R3: Cohort Segmentation by MDL of Behavior Sequences

**Goal.** Discover the natural number of user cohorts k from session-level event sequences without imposing a feature space or distance metric. Output: k cluster assignments written back to a mart dimension.

**Inputs.** An events mart with `(user_id, session_id, event_type, event_rank_in_session)`. Minimum 1,000 users; 5+ distinct event types.

**Steps.**

```
1. ENCODE SESSION SEQUENCES  [Primitive #11]
   For each user, concatenate their event types in session order into a string:
     "home→search→pdp→cart→pdp→checkout→confirm"
   Normalize to a fixed vocabulary of top-20 event types; map others to "__other__".
   → verify: median session length ≥ 3 events; if shorter, concatenate last 5 sessions per user.

2. COMPUTE PAIRWISE NCD  [Primitive #11]
   NCD(user_i, user_j) = [C(seq_i + seq_j) − min(C(seq_i), C(seq_j))] / max(C(seq_i), C(seq_j))
   Use zstd or bzip2 as the compressor C (stronger than gzip for short strings).
   NCD ≈ 0: users have similar behavior sequences.
   NCD ≈ 1: users have incompressible differences.
   → verify: NCD matrix is symmetric; diagonal is 0 (self-comparison).
   → note: for > 10,000 users, sample 2,000 representatives and assign the rest to
     nearest representative after clustering.

3. FIT CLUSTERS ACROSS CANDIDATE k  [Primitives #7, #11]
   For k in {2, 3, 4, ..., 15}:
     a. Run k-medoids on the NCD distance matrix (PAM algorithm).
     b. Compute MDL(k):
          L_model(k) = k * avg_compressed_centroid_length_bits
          L_data_given_model = Σ_users [compressed_length(seq_i | nearest_centroid)]
          MDL(k) = L_model(k) + L_data_given_model
   → verify: MDL(k) is monotonically dominated by L_data_given_model for small k
     and by L_model for large k; the minimum is the natural elbow.

4. SELECT OPTIMAL k  [Primitive #7]
   Pick k* = argmin MDL(k).
   If MDL curve is flat across 3 consecutive k values, pick the smallest (Occam's razor).
   → verify: k* ∈ {3, ..., 8} for most B2C products; if k* = 2 the data may be too sparse;
     if k* > 10 the event vocabulary may need consolidation.

5. WRITE BACK TO MART
   Join cluster assignments to the user dimension:
     [user_id, cohort_id, cohort_mdl_score, cohort_representative_sequence]
   Add cohort_id as a dimension to the metric dictionary.
   Document cohort semantics (qualitative label based on representative sequences).
   → verify: cluster sizes are not degenerate (no cluster < 2% of users);
     merge degenerate clusters into nearest neighbor.
```

**Expected output.** A `dim_user_cohort` model with k = 3–6 cohorts for most products. Each cohort has a representative behavior sequence and an MDL score measuring how compactly it describes its members.

**Practical shortcut.** If NCD computation is too expensive for your environment, substitute BIC as the MDL approximation (see Pattern P5 note). Fit Gaussian mixture models on 20-dimensional event-count feature vectors; BIC selects k. Less behaviorally precise than sequence MDL but runs in SQL + a lightweight Python step.

**See.** [07-mdl-principle.md](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md), [11-redundancy-compression.md](../../foundations-information-theory/assets/templates/information-theory/11-redundancy-compression.md), [01-shannon-entropy.md](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md)

---

## Composition: Layering Primitives in a Quality Pipeline

A production analytics quality pipeline can stack these patterns in sequence:

```
INGEST (daily ETL load)
  └─ P3: Schema-drift KL alert on staged field-value distributions
         → blocks mart refresh if KL_forward > 1.0

TRANSFORM (dbt mart build)
  └─ P4: Field entropy profile
         → flags low-entropy fields for governance review
  └─ P2: Event-type entropy + KL drift monitor
         → detects duplication bugs (volume up, entropy down)

SERVE (mart available to consumers)
  └─ P7: Cross-platform normalization check
         → validates event joins across SDKs before funnel metric publish

CONSUME (ML pipeline, BI dashboards)
  └─ P1: MI-based feature selection
         → fed by the mart; governed by feature_mi_scores seed
  └─ R2: Fano-bound error alert
         → schema drift translated to model error impact for ML consumers
  └─ P5/R3: MDL cohort segmentation
         → periodic (weekly) batch; output feeds dim_user_cohort
```

No single layer depends on another in real time — each is independently deployable as a dbt test, a dbt model, or an external Python step. The Fano bound (R2, step 3) is the deepest integration: it connects ingest-layer schema drift directly to downstream model-error estimates, making information theory actionable for non-technical stakeholders.

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed. Wiley. Chapters 2 (entropy, MI), 7 (channel capacity), 14 (MDL). Canonical reference for all primitives.
- Paninski, L. (2003). Estimation of entropy and mutual information. *Neural Computation*, 15(6), 1191–1253. Bias correction for discrete MI and entropy estimators.
- Paninski, L. (2003). Ibid. — the "Paninski caveat" on high-cardinality entropy estimation (Anti-Pattern A3).
- Fano, R. M. (1961). *Transmission of Information*. MIT Press. Origin of Fano's inequality (Recipe R2, step 3).
- Grünwald, P. (2007). *The Minimum Description Length Principle*. MIT Press. MDL for model selection and clustering (Patterns P5, Recipe R3).
- Cilibrasi, R. & Vitányi, P. M. B. (2005). Clustering by compression. *IEEE Transactions on Information Theory*, 51(4), 1523–1545. NCD foundation for Recipe R3.
- Rissanen, J. (1978). Modeling by shortest data description. *Automatica*, 14(5), 465–471. Original MDL paper.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423. Foundation for channel capacity and entropy.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*. Cambridge University Press. Available free at inference.org.uk/mackay/itila/.
- Miller, G. A. (1955). Note on the bias of information estimates. *Information Theory in Psychology*, 2, 95–100. Miller-Madow bias correction.
- Primitive playbooks in [`../../foundations-information-theory/assets/templates/information-theory/`](../../foundations-information-theory/assets/templates/information-theory/) — canonical per-primitive definitions, failure modes, and worked examples.
