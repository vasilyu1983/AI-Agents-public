---
description: Theory of Constraints applied to analytics engineering. Five Focusing Steps on data pipelines, throughput accounting on data-team time, CRT for freshness incidents, policy-constraint detection in dbt review queues, and DBR-style scheduling on shared compute. Grounds all patterns in dbt, warehouse, and governance reality.
last_verified: 2026-05-02
status: stable
---

# Theory of Constraints Applied: Data Pipelines, Data Teams, and Governance

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Primitive Coverage Map](#primitive-coverage-map)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Pipeline Lag Isolation via Five Focusing Steps](#p1--pipeline-lag-isolation-via-five-focusing-steps)
  - [P2 — Throughput Accounting on Data-Team Capacity](#p2--throughput-accounting-on-data-team-capacity)
  - [P3 — Current Reality Tree for Recurring Freshness Incidents](#p3--current-reality-tree-for-recurring-freshness-incidents)
  - [P4 — Policy-Constraint Detection in dbt PR Review Queues](#p4--policy-constraint-detection-in-dbt-pr-review-queues)
  - [P5 — DBR-Style Scheduling on Shared Compute](#p5--dbr-style-scheduling-on-shared-compute)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Optimizing Fast Models When Slow Upstream Sources Are the Bottleneck](#a1--optimizing-fast-models-when-slow-upstream-sources-are-the-bottleneck)
  - [A2 — Cost-Accounting on dbt Models Instead of Throughput-Accounting on Insights Delivered](#a2--cost-accounting-on-dbt-models-instead-of-throughput-accounting-on-insights-delivered)
  - [A3 — Treating Compute as the Constraint When Review SLA Is the Real Gate](#a3--treating-compute-as-the-constraint-when-review-sla-is-the-real-gate)
  - [A4 — Ignoring Policy Constraints in Pipeline Redesigns](#a4--ignoring-policy-constraints-in-pipeline-redesigns)
- [Recipes](#recipes)
  - [R1 — Pipeline Lag Identification: 5FS over DAG to Constraint Mart](#r1--pipeline-lag-identification-5fs-over-dag-to-constraint-mart)
  - [R2 — Data-Team Capacity Reallocation via Throughput Accounting](#r2--data-team-capacity-reallocation-via-throughput-accounting)
  - [R3 — Approval-Queue Debug: CRT to Evaporating Cloud to Future Reality Tree](#r3--approval-queue-debug-crt-to-evaporating-cloud-to-future-reality-tree)
- [Composition](#composition)
- [Primitive Links](#primitive-links)
- [Sources](#sources)

---

## Framing Note

Data engineering looks like a series of technical problems — slow models, stale dashboards, expensive queries, flaky freshness checks. Most of these are throughput problems in disguise. A data pipeline is a multi-step system. A data team is a capacity-constrained delivery system. Governance gates are policy constraints. The same TOC logic that fixes a factory production line applies here, directly and without translation loss.

This file is the applied layer of the `foundations-theory-of-constraints` skill. It translates the 11 TOC primitives into patterns that arise inside dbt projects, data warehouses, and analytics governance programs. Every pattern names the primitive it relies on and links to the corresponding template. Assumed stack: Snowflake or BigQuery, dbt (Core or Cloud), dbt Cloud CI, Elementary or Monte Carlo for observability, and a standard PR-based review workflow.

---

## Primitive Coverage Map

| Primitive | # | Applied in Patterns / Recipes |
|-----------|---|-------------------------------|
| Five Focusing Steps | 1 | P1, R1 |
| Drum-Buffer-Rope | 2 | P5, R2 |
| Throughput Accounting | 3 | P2, A2, R2 |
| Evaporating Cloud | 4 | R3 |
| Current Reality Tree | 5 | P3, R3 |
| Future Reality Tree | 6 | R3 |
| Policy Constraints | 10 | P4, A3, A4, R3 |

Full primitive playbooks: [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/)

---

## Pattern Catalog

### P1 — Pipeline Lag Isolation via Five Focusing Steps

**Primitive**: #1 Five Focusing Steps → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md)

**When to use.** A dashboard is running behind SLA — e.g., the executive revenue mart is expected fresh by 08:00 but consistently lands at 09:30. Engineers have made several dbt model optimizations but the SLA breach continues. The constraint has not been identified.

**The problem it solves.** A dbt DAG is a multi-step pipeline. Optimizing any model that is not the constraint does not move the SLA. Local optimizations accumulate (faster staging models, reduced intermediate scans) but end-to-end freshness is unchanged because the bottleneck mart is untouched. 5FS forces the team to find and fix the actual gate before touching anything else.

**Mechanic.**

1. **Identify** — Measure actual execution time and queue wait time per DAG layer, not just SQL duration. The constraint is the layer where wait time (time a model sits queued after its upstream completes) plus execution time is longest. In dbt Cloud, pull `run_results.json` per job; in Snowflake, query `QUERY_HISTORY` with `warehouse_name` and `queued_overload_time`.

   ```sql
   -- Snowflake: find the model layer with the highest total pipeline contribution
   -- (queued_overload_time = time spent waiting for warehouse slot)
   SELECT
       query_tag,   -- dbt sets this to the model name
       AVG(total_elapsed_time)        AS avg_exec_ms,
       AVG(queued_overload_time)      AS avg_queue_ms,
       AVG(total_elapsed_time + queued_overload_time) AS avg_total_wait_ms,
       COUNT(*)                       AS run_count
   FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
   WHERE start_time > DATEADD('day', -14, CURRENT_TIMESTAMP)
     AND query_tag LIKE 'dbt%'
   GROUP BY 1
   ORDER BY avg_total_wait_ms DESC
   LIMIT 20
   ```

2. **Exploit** — Before adding compute or rewriting SQL, squeeze the existing constraint capacity. Common exploitations:
   - Move the constraint model to a dedicated warehouse tier (prevent credit contention with concurrent jobs).
   - Enable incremental materialization if the model is currently full-refresh and the source rows are append-only.
   - Cluster or partition the constraint model's source tables on the join key.

3. **Subordinate** — Adjust non-constraint models to feed the constraint optimally. If staging models fan out to both the constraint mart and other marts, schedule the constraint-feeding path first. Freeze all optimization work on models downstream of the constraint until the constraint is resolved.

4. **Elevate** — If exploit + subordinate are insufficient, invest: increase warehouse size for the constraint job, add a second warehouse for parallel execution, or refactor the model into incremental + merge.

5. **Repeat** — After the constraint is broken, re-run step 1. The next constraint is typically the new heaviest model in the refreshed DAG profile.

**dbt application.** In dbt Cloud, tag the constraint model with `meta: {toc_constraint: true}` to make it visible in the catalog and prevent teammates from inadvertently deprioritizing it in CI scheduling.

**Failure mode to avoid.** Identifying the longest-running model by execution time alone, ignoring queue wait. A model with 10-minute execution and 0-minute queue wait contributes 10 minutes. A model with 3-minute execution and 25-minute queue wait contributes 28 minutes — it is the real constraint.

---

### P2 — Throughput Accounting on Data-Team Capacity

**Primitive**: #3 Throughput Accounting → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md)

**When to use.** A data team is fully utilized — every engineer has a full sprint — but stakeholders report that the insights they actually need are still not delivered. The team is optimizing locally (shipping models, fixing tests, refactoring staging) without maximizing throughput of finished, consumed insights.

**The problem it solves.** Cost-accounting thinking on a data team measures output in units that feel productive — models built, tests added, PRs merged — but these are investment (I) and operating expense (OE) proxies, not throughput. Throughput Accounting reframes the measurement: **Throughput (T)** is the rate at which insights reach decision-makers and generate business value. Every hour spent on work that does not advance a dashboard, metric, or decision is an OE cost that does not generate T.

**Mechanic.**

Translate the TOC financial triad into data-team terms:

| TOC term | Data-team meaning |
|----------|------------------|
| Throughput (T) | Insights delivered per sprint: dashboards shipped, metrics published, decisions directly enabled |
| Investment (I) | In-flight work: models in WIP, PRs open, features in review |
| Operating Expense (OE) | Engineer-hours spent regardless of insight delivery: meetings, refactors, doc, infra maintenance |

**T/CU (Throughput per Constraint Unit)** becomes: insights delivered per engineer-hour spent at the team's constraint stage. To compute it, identify the constraint stage first (typically the review/approval step — see P4), then rank backlog items by expected insights delivered divided by constraint-stage hours required.

**Decision rule.** Before adding a new data model to the sprint, ask: does this model unblock an in-flight insight delivery? If not, it is operating expense that competes for constraint time without adding T. Defer it, even if the model is technically interesting.

**Practical sprint application.**

```
Sprint backlog scoring:
  Item A: "Build fct_revenue_by_channel mart"
    → unblocks 3 executive dashboards → T contribution: HIGH
    → constraint stage (senior review): estimated 2 hours
    → T/CU: HIGH / 2h = strong candidate

  Item B: "Refactor stg_salesforce to improve test coverage"
    → no blocked downstream consumers
    → constraint stage: estimated 1 hour
    → T/CU: 0 unblocked insights / 1h = defer until constraint is free
```

**Failure mode to avoid.** Celebrating "models shipped" as throughput. Models in a mart that no one reads are inventory (I), not throughput. Include a "confirmed consumer" check in the definition of done for any new mart.

---

### P3 — Current Reality Tree for Recurring Freshness Incidents

**Primitive**: #5 Current Reality Tree → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md)

**When to use.** The same freshness incident — "the revenue mart is stale by morning" or "the orders dashboard showed yesterday's numbers during the all-hands" — recurs every two to four weeks despite repeated fixes. Each fix patches a different surface symptom.

**The problem it solves.** A recurring data incident is a classic CRT signal: multiple undesirable effects (UDEs) with a shared root cause that has never been surfaced. Patching each UDE individually keeps the root cause active and guarantees recurrence. The CRT connects all UDEs with "If…Then" logic chains and traces them to the one Core Problem that, if resolved, eliminates or weakens all UDEs simultaneously.

**Mechanic.**

Step 1: Collect 5–8 UDEs from the last six post-mortems. Write each as a concrete, negative, observable outcome — not a cause:

```
UDE 1: "fct_orders was stale at 08:00 on 2026-03-14"
UDE 2: "Snowflake warehouse ran out of credits at 07:45 on 2026-03-14"
UDE 3: "Ingestion job for Salesforce CRM ran 40 minutes late on 2026-03-12"
UDE 4: "dbt Cloud job for fct_revenue failed silently — no alert fired"
UDE 5: "On-call engineer did not see the failure until a stakeholder reported it"
UDE 6: "fct_orders model was re-run full-refresh instead of incremental after the March schema change"
```

Step 2: Build the "If…Then" chains upward. Start from two or three UDEs that seem related and trace their causes:

```
IF  Snowflake warehouse hit credit cap (UDE 2)
AND fct_orders was running full-refresh (UDE 6)
THEN  fct_orders run consumed 4× normal credits and caused timeout → UDE 1

IF  The March schema change was applied without reverting materialization strategy
AND there is no automated check that flags full-refresh on incremental-eligible models
THEN  fct_orders reverts to full-refresh silently after any schema migration → UDE 6
```

Step 3: Continue tracing until two or more chains converge on a single cause. The Core Problem is the cause that, if removed, would sever the most UDE chains. In the example above, the Core Problem is typically: *"There is no automated governance gate that enforces materialization strategy and alerts on deviation after schema changes."*

Step 4: Design an injection — the policy or automation that addresses the Core Problem — and validate it with a Future Reality Tree (primitive #6) before implementing.

**dbt integration.** The injection in most freshness incident CRTs is a combination of: (a) an Elementary or Monte Carlo freshness alert wired to PagerDuty or Slack, (b) a dbt model-level `meta` contract that specifies expected materialization strategy and raises a CI error if violated, and (c) a dbt-project-level test that checks `model.config.materialized` against the allowed list after any `dbt run --full-refresh`.

---

### P4 — Policy-Constraint Detection in dbt PR Review Queues

**Primitive**: #10 Policy Constraints → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md)

**When to use.** A data team has fast CI (dbt compilation + test suite runs in under 15 minutes), competent engineers, and no compute bottleneck — yet PRs from authoring to merge take 3–5 days on average. Adding engineers does not shorten the queue. The constraint is invisible because it is a policy, not a resource.

**The problem it solves.** In analytics engineering workflows, the most common policy constraints are: (1) review rules that require sign-off from a single senior engineer or data lead before any mart model can merge; (2) approval gates for data-governance teams before any model touching PII or financial metrics can deploy; (3) batch release windows ("we only deploy to production on Fridays") inherited from a prior incident or risk policy. These policies throttle throughput regardless of engineer count or compute power.

**Detection method.**

Measure the stages of a PR's lifecycle for the last 30 merged PRs:

```
Stage 1: Author open → first review requested          (time = T_author)
Stage 2: Review requested → first review comment       (time = T_wait_review)
Stage 3: First review comment → changes requested done (time = T_iteration)
Stage 4: Approved → merged                             (time = T_approval_to_merge)
```

Extract from GitHub API or dbt Cloud CI metadata. Sum total time. Identify the longest stage. If `T_wait_review + T_approval_to_merge` accounts for > 60% of total cycle time, the constraint is a review/approval policy, not authoring capacity.

```python
# Example: GitHub API pull request timeline analysis
import requests, statistics

repo = "org/analytics"
headers = {"Authorization": "Bearer <TOKEN>"}
prs = requests.get(
    f"https://api.github.com/repos/{repo}/pulls",
    params={"state": "closed", "per_page": 30},
    headers=headers
).json()

cycle_times = []
for pr in prs:
    created  = pr["created_at"]
    merged   = pr["merged_at"]
    if merged:
        delta_hours = (
            datetime.fromisoformat(merged.replace("Z",""))
            - datetime.fromisoformat(created.replace("Z",""))
        ).total_seconds() / 3600
        cycle_times.append(delta_hours)

print(f"Median PR cycle time: {statistics.median(cycle_times):.1f} hours")
print(f"P90 PR cycle time: {sorted(cycle_times)[int(0.9*len(cycle_times))]:.1f} hours")
```

**Policy audit checklist.**

- [ ] Does any mart model require a named individual's approval before merge?
- [ ] Is there a deploy-day restriction (e.g., "production deploys on Tuesdays only")?
- [ ] Does the data-governance gate apply equally to trivial doc changes and schema-breaking changes?
- [ ] Is there a separate approval path for PII-adjacent models that serializes behind a single reviewer?

**Injection patterns.** Replace blanket review requirements with tiered risk-based automation: CI gates (schema contract diff, affected-downstream-models count, PII column flag) replace manual review for low-risk changes; human approval is required only when the CI gate fires a `HIGH_RISK` flag. This is directly analogous to the deploy-sign-off removal in the TOC policy constraint worked example (see primitive #10).

---

### P5 — DBR-Style Scheduling on Shared Compute

**Primitive**: #2 Drum-Buffer-Rope → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md)

**When to use.** Multiple dbt jobs — nightly batch, ad-hoc analyst queries, CI test runs, and dashboard refresh jobs — compete for credits on a shared Snowflake or BigQuery warehouse. Credit usage spikes at peak hours, jobs queue up, SLAs breach, and the instinct is to either increase warehouse size or upgrade the account tier.

**The problem it solves.** Without DBR scheduling, every job enters the shared warehouse whenever it is triggered, generating unbounded WIP. The warehouse (the constraint — the step with finite capacity) is flooded. Elevating the warehouse (larger size, more credits) without controlling intake is the classic 5FS failure: elevating before subordinating. DBR controls the intake via the rope so that the warehouse never has more concurrent load than it can process at target SLA.

**DBR translation.**

| DBR term | Warehouse meaning |
|----------|------------------|
| Drum | Warehouse compute capacity (credits/hour) at the target SLA tier |
| Buffer | Time buffer before the constraint: jobs are scheduled to arrive at the warehouse N minutes before their downstream consumers need the results |
| Rope | Credit-usage cap that gates new job intake; new jobs wait in a queue rather than entering the warehouse when the cap is reached |

**Mechanic.**

1. **Set the drum**: determine the maximum credit consumption rate at which the warehouse meets SLA (measured from historical query profiles). Example: a Snowflake X-Large warehouse serving a 2-hour nightly batch window has a sustainable throughput of ~80 credit-hours of concurrent execution.

2. **Set the buffer**: identify the latest start time that allows the batch to complete before downstream dashboards refresh. Schedule the highest-priority jobs (executive marts, SLA-critical models) to start at `buffer_start = SLA_deadline − (p95_execution_time × 1.3)`. The 1.3× factor is the time buffer.

3. **Set the rope**: configure a job-scheduling policy that limits concurrent job intake to the drum rate. In dbt Cloud, use job thread settings and warehouse size per job to prevent credit stacking. In Snowflake, use resource monitors:

   ```sql
   -- Snowflake: resource monitor to cap warehouse credits per hour
   CREATE OR REPLACE RESOURCE MONITOR analytics_batch_cap
     WITH CREDIT_QUOTA = 50
     FREQUENCY = DAILY
     START_TIMESTAMP = IMMEDIATELY
     TRIGGERS
       ON 80 PERCENT DO NOTIFY
       ON 100 PERCENT DO SUSPEND;

   ALTER WAREHOUSE analytics_batch_wh
     SET RESOURCE_MONITOR = analytics_batch_cap;
   ```

4. **Subordinate**: schedule ad-hoc analyst queries and CI test runs to non-overlapping windows or to a separate warehouse tier. The batch (constraint) runs first and uninterrupted; ad-hoc jobs enter only after the batch window closes or on a separate resource.

**Buffer management.** Monitor credit consumption rate vs. the drum rate daily. If the batch consistently consumes < 60% of the drum without breaching SLA, the drum is oversized — downgrade the warehouse tier. If the buffer is routinely consumed (jobs start late relative to the buffer schedule), the constraint capacity needs elevation.

---

## Anti-Pattern Catalog

### A1 — Optimizing Fast Models When Slow Upstream Sources Are the Bottleneck

**Primitives implicated**: #1 Five Focusing Steps, #10 Policy Constraints

**Description.** An analytics engineer profiles the dbt DAG, finds that three intermediate models run for 8–12 minutes each, and spends two weeks refactoring them with better clustering, partitioning, and SQL rewrite. After the work, end-to-end freshness is unchanged. The slow models were not the constraint: the Fivetran or Airbyte ingestion job upstream of all three models completes at 07:15, setting the earliest possible start time for the entire DAG regardless of SQL performance.

**Why it fails.** 5FS step 1 (identify) was skipped. The engineer measured execution time on dbt models without measuring the ingestion completion time that gates the entire DAG. Optimizing any step upstream of the constraint — or downstream of the constraint before the constraint is fixed — does not move the SLA needle. It generates operating expense without generating throughput.

**Concrete example.** fct_revenue depends on stg_salesforce which depends on raw_salesforce (Fivetran). Fivetran completes at 07:15. dbt job starts at 07:15. stg_salesforce runs for 2 minutes. fct_revenue runs for 22 minutes. Dashboard is fresh by 07:37.

After optimization, stg_salesforce runs for 40 seconds, fct_revenue runs for 18 minutes. Dashboard is now fresh by 07:33 — a 4-minute improvement.

But: Fivetran completion time has variance of ±30 minutes due to Salesforce API rate limits. The real SLA breach driver is Fivetran, not dbt. A 4-minute SQL improvement does nothing when the source is late.

**Fix.** Before any optimization work, build a pipeline timing map: ingestion completion time, dbt job start time, and per-layer execution + queue time. Identify the constraint as the stage with the greatest contribution to SLA variance. Only then invest in SQL optimization — and only on the constraint layer.

---

### A2 — Cost-Accounting on dbt Models Instead of Throughput-Accounting on Insights Delivered

**Primitives implicated**: #3 Throughput Accounting

**Description.** A data team tracks its progress via cost-accounting proxies: Snowflake credits consumed per model, dbt model build count per sprint, number of tests added, lines of SQL refactored. These metrics measure operating expense and investment, not throughput. A sprint that adds 40 new models and 300 new tests with zero new insights delivered to business stakeholders scores well on cost-accounting metrics and contributes nothing to organizational T.

**Why it fails.** Throughput Accounting's core inversion is: T (revenue-generating output) first, I (in-progress inventory) minimize, OE (spend) minimize. Analytics teams that measure "models shipped" are measuring I, not T. A model that is built, tested, and documented but has no active consumer is pure inventory — it costs OE to maintain and adds zero T until someone uses it.

**Concrete example.** A data team spends Q1 rebuilding the staging layer from scratch (stronger contracts, better naming, full test coverage). 200 models refactored. 600 new tests. Snowflake credits reduced 15%. Zero new dashboards. Zero new decisions enabled. The business impact of Q1 is invisible to non-technical stakeholders because it was never framed in throughput terms.

**Fix.** Define T at the team level as "insights delivered per sprint": new dashboards confirmed in use, new metrics published and queried by stakeholders, and direct decision support delivered. Before committing refactor or infrastructure work to a sprint, evaluate it by: "Does this work unblock a specific T-generating deliverable within this sprint or next?" If yes, proceed. If not, it is deferred maintenance — schedule it in a dedicated maintenance sprint, not competing with T-generating work.

---

### A3 — Treating Compute as the Constraint When Review SLA Is the Real Gate

**Primitives implicated**: #10 Policy Constraints, #1 Five Focusing Steps

**Description.** End-to-end time from "engineer starts building a feature" to "feature in production" is 5 days on average. The team diagnoses the problem as compute: models are slow, CI takes 18 minutes, warehouse queries need optimization. The proposed solution is upgrading the warehouse tier and parallelizing CI. After the upgrade, CI runs in 10 minutes. The end-to-end time drops to 4.8 days. The constraint was never compute — it was the 2-day average wait for senior review and the 1-day wait for data-governance sign-off on PII-adjacent models.

**Why it fails.** Policy constraints are invisible. Physical constraints (slow queries, queue depth) show up in dashboards. Policy constraints (review SLA, approval gates) show up as "the work is done but it's not in prod yet" — a symptom that is easy to attribute to the last visible step (CI) rather than to the invisible approval queue.

**Detection test.** For any pipeline where total cycle time is more than 3× the sum of technical execution times, a policy constraint is almost certainly active. The gap between "technically done" and "in production" is the policy constraint's fingerprint.

**Fix.** See P4. Audit all review and approval rules before investing in compute. Apply 5FS step 1 across the full workflow, not just the technical steps.

---

### A4 — Ignoring Policy Constraints in Pipeline Redesigns

**Primitives implicated**: #10 Policy Constraints, #6 Future Reality Tree

**Description.** A data team designs a new pipeline architecture — migrating from a monolithic dbt project to a multi-project setup with separate domains, or adopting a new semantic layer — and models the new architecture's performance entirely in technical terms: execution time, credit cost, test coverage. The migration plan does not account for the approval steps that will be required under the new governance model: each cross-domain model reference will now require sign-off from the domain data owner; the semantic layer requires a formal metric registry review before any new metric is published.

After migration, the new architecture is faster per execution, but insight delivery slows by 40% because the approval queue that did not exist in the old architecture is now a policy constraint that was never designed around.

**Why it fails.** A Future Reality Tree (primitive #6) tests an injection for unintended side effects before implementation. A pipeline redesign that does not model governance and approval workflows as part of the new system will discover its policy constraints only in production, when they are expensive to change.

**Fix.** Before any architectural migration, explicitly map all approval, review, and governance steps in the proposed future state. For each new governance gate that the migration introduces, classify it as: (a) a policy constraint candidate — does it throttle throughput independently of technical capacity? If yes, redesign the gate before migration (risk-tiered automation, async review, pre-approved patterns) rather than inheriting the bottleneck in the new architecture.

---

## Recipes

### R1 — Pipeline Lag Identification: 5FS over DAG to Constraint Mart

**Scenario.** A nightly pipeline produces an executive revenue dashboard. The dashboard should be fresh by 07:00. It is consistently late by 1–2 hours. Three engineers have each optimized "their" part of the pipeline without fixing the SLA.

**Stack**: #1 Five Focusing Steps → constraint identification → exploit → subordinate

**Step 1: Build the pipeline timing map.**

Pull execution and queue times for every node in the DAG across the last 30 runs.

```sql
-- Snowflake: per-model execution and queue time for dbt jobs
-- Assumes dbt sets query_tag = model name (configure in dbt_project.yml)
WITH model_timing AS (
    SELECT
        query_tag                                              AS model_name,
        DATE_TRUNC('day', start_time)                         AS run_date,
        AVG(total_elapsed_time)                               AS avg_exec_ms,
        AVG(queued_overload_time)                             AS avg_queue_ms,
        AVG(total_elapsed_time + queued_overload_time)        AS avg_total_ms,
        PERCENTILE_CONT(0.95) WITHIN GROUP (
            ORDER BY total_elapsed_time + queued_overload_time
        )                                                     AS p95_total_ms,
        COUNT(*)                                              AS n_runs
    FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
    WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP)
      AND query_tag LIKE 'dbt+model+%'
      AND execution_status = 'SUCCESS'
    GROUP BY 1, 2
)
SELECT
    model_name,
    ROUND(AVG(avg_total_ms) / 1000, 1)    AS avg_total_sec,
    ROUND(AVG(avg_queue_ms) / 1000, 1)    AS avg_queue_sec,
    ROUND(AVG(p95_total_ms) / 1000, 1)    AS p95_total_sec
FROM model_timing
GROUP BY 1
ORDER BY p95_total_sec DESC
LIMIT 30;
```

Also pull ingestion completion time for each source:

```sql
-- dbt source freshness history (if using dbt Cloud API or Elementary)
SELECT
    source_name,
    identifier,
    snapshotted_at,
    max_loaded_at,
    DATEDIFF('minute', max_loaded_at, snapshotted_at) AS staleness_minutes
FROM dbt_source_freshness_history
WHERE snapshotted_at::date >= CURRENT_DATE - 30
ORDER BY source_name, snapshotted_at DESC;
```

**Step 2: Identify the constraint.**

- [ ] Does any source ingestion complete after the target dbt job start time? If yes, the ingestion is a pre-constraint gate — no dbt optimization can compensate.
- [ ] Which model has the highest p95 total time (execution + queue)?
- [ ] Does queue time account for > 30% of that model's total time? If yes, compute contention is the constraint expression, not SQL inefficiency.

Mark the constraint model in dbt with:

```yaml
# models/marts/fct_revenue.yml
models:
  - name: fct_revenue
    meta:
      toc_constraint: true
      constraint_reason: "p95 total 47 min; queue time 18 min (38%); gates executive dashboard SLA"
```

**Step 3: Exploit the constraint.**

Run the constraint model on a dedicated warehouse tier with no concurrent jobs sharing the slot:

```sql
-- Snowflake: dedicated warehouse for the constraint model
CREATE WAREHOUSE analytics_critical_wh
    WAREHOUSE_SIZE = 'X-LARGE'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Dedicated to SLA-critical constraint models';
```

In dbt:

```yaml
# profiles.yml or model config
models:
  +snowflake_warehouse: analytics_critical_wh  # override for all marts
  marts:
    fct_revenue:
      snowflake_warehouse: analytics_critical_wh  # explicit, auditable
```

Enable incremental materialization if the model is full-refresh and the source is append-only:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'  -- alert, don't silently revert
) }}
```

**Step 4: Subordinate non-constraint jobs.**

Move CI test runs, ad-hoc queries, and non-critical mart refreshes to off-peak windows or a separate warehouse. Freeze optimization work on non-constraint models until the SLA is met.

**Step 5: Verify and repeat.**

After exploitation, re-run the timing query (Step 1). Confirm the constraint model's p95 total time has dropped below the SLA window. If it has, the constraint may have shifted — repeat from Step 2.

→ **verify**: SLA breach rate drops below 5% over the following 14 days; constraint model p95 total time is < 60% of the SLA window.

---

### R2 — Data-Team Capacity Reallocation via Throughput Accounting

**Scenario.** A data team of four engineers has a full sprint backlog but cannot deliver the three business-critical dashboards stakeholders have requested. Engineers are not idle — they are fully utilized on infrastructure refactoring, test coverage expansion, and staging model maintenance. The team lead needs a framework to reallocate capacity without starting from scratch on the backlog.

**Stack**: #3 Throughput Accounting → T/CU ranking → #2 DBR (rope on non-T work)

**Step 1: Identify the constraint stage.**

Run the PR review lifecycle analysis from P4. For most four-person data teams, the constraint stage is senior review: one engineer (the lead or principal) reviews all mart models before merge. Constraint capacity = the lead's available review hours per sprint.

Example: lead has 8 review-hours per two-week sprint. Each dashboard-critical mart model requires ~2 review-hours. Constraint capacity = 4 models per sprint.

**Step 2: Score backlog items by T/CU.**

For each item, estimate: (a) the number of insights delivered or dashboards unblocked if shipped, and (b) constraint-stage hours required (review hours).

```
Item                               | T (insights unblocked) | CU (review-hours) | T/CU
fct_revenue_by_channel             | 3 (3 dashboards)       | 2                 | 1.5
fct_pipeline_coverage              | 2 (2 dashboards)       | 2                 | 1.0
stg_salesforce refactor            | 0 (no blocked consumer)| 1                 | 0.0
test_coverage_expansion (staging)  | 0 (no blocked consumer)| 0.5               | 0.0
fct_customer_health                | 1 (1 dashboard)        | 3                 | 0.33
```

**Ranking decision**: prioritize `fct_revenue_by_channel` and `fct_pipeline_coverage`. With 8 review-hours available, these two consume 4 hours and deliver 5 insights. `fct_customer_health` consumes 3 hours for 1 insight (T/CU = 0.33) — schedule it next sprint if the constraint is still 8 hours.

**Step 3: Apply the rope on non-T work.**

Limit non-T-generating work (refactors, test coverage, infra maintenance) to a fixed budget: no more than 20% of total engineer-hours per sprint. This is the DBR rope applied to the team's intake. New refactor requests enter a queue rather than the active sprint when the 20% budget is reached.

Communicate this budget explicitly in sprint planning:

```
Sprint budget:
  T-generating work (blocked insights): 80% = 3.2 engineer-weeks
  Maintenance / tech-debt (non-T):      20% = 0.8 engineer-weeks
  Any additional maintenance requests: → deferred backlog, reviewed at next planning
```

**Step 4: Track T, not models shipped.**

After the sprint, report:
- **T**: number of dashboards/insights delivered and confirmed in use by stakeholders
- **I**: number of open PRs at sprint end (WIP inventory)
- **OE**: engineer-hours spent on non-T work

A healthy sprint has high T, low I (no accumulating WIP), and bounded OE.

→ **verify**: T ≥ planned insights for two consecutive sprints; I (open PRs at sprint end) decreases to < 3; stakeholder satisfaction with delivery timeliness improves.

---

### R3 — Approval-Queue Debug: CRT to Evaporating Cloud to Future Reality Tree

**Scenario.** The data governance team requires all new models touching financial metrics or PII to be reviewed by a named governance reviewer before deployment. This policy was introduced after a compliance incident. The average wait time for governance sign-off is 4 days. The data team's effective throughput has dropped 30% since the policy was introduced. Both the data team and the governance team agree there is a problem but cannot agree on a solution: the data team wants to remove the gate; the governance team cannot accept that risk.

**Stack**: #5 CRT → #4 Evaporating Cloud → #6 Future Reality Tree

**Step 1: Build the CRT from UDEs.**

Collect the undesirable effects from both teams:

```
From data team:
  UDE 1: "Dashboard delivery is 4 days slower since the governance policy was introduced"
  UDE 2: "Engineers are batching changes to amortize the 4-day wait, increasing change size and risk"
  UDE 3: "Stakeholders are going around the data team to build ad-hoc Looker reports"

From governance team:
  UDE 4: "The governance reviewer is reviewing 15–20 models per week — unsustainable workload"
  UDE 5: "Most models reviewed are low-risk (naming changes, documentation, no schema change)"
  UDE 6: "The original compliance incident involved a high-risk schema change — none of the reviewed models match that risk profile"
```

Build the "If…Then" chains:

```
IF  all models touching financial/PII fields require governance review
AND the governance reviewer has capacity for ~5 high-quality reviews/week
THEN  the queue grows to 15–20 items/week → UDE 4 (reviewer overload)

IF  the review gate applies uniformly regardless of change risk
AND most changes are low-risk (UDE 5)
THEN  the gate generates no signal-to-noise improvement for compliance
  AND  the gate consumes reviewer capacity on non-compliance-relevant changes → UDE 5 + 6

IF  engineers face a 4-day queue for every change
THEN  engineers batch changes to amortize the wait → UDE 2
  AND  large batches increase diff size and actual review quality drops → self-reinforcing
```

Core Problem: *The governance gate applies uniform scrutiny to all financial/PII-touching changes regardless of risk level, saturating the reviewer's capacity with low-risk work and failing to provide meaningful protection for high-risk changes.*

**Step 2: Build the Evaporating Cloud.**

The conflict is:

```
Objective (A):     Protect financial/PII data integrity and maintain compliance
  → Requirement (B): Governance reviewer signs off on all financial/PII model changes
    → Want (D):     Apply the review gate to 100% of changes touching these fields

  → Requirement (C): Data team delivers insights at the pace business requires
    → Want (D'):    Remove or bypass the review gate to restore delivery velocity
```

The conflict between D and D' feels irresolvable — but it is sustained by a hidden assumption on the B→D arrow: *"Only manual human review of all changes can protect data integrity."*

Challenge the assumption:

- Is it true that 100% of financial/PII changes pose equal compliance risk? **No** — a documentation update, a column rename with no semantic change, and a schema-breaking rewrite are not equivalent risks.
- Is it true that manual review is the only mechanism to catch compliance violations? **No** — automated schema-diff checks, dbt contract enforcement, and column-level lineage tracing can detect high-risk changes without human review of every PR.

The injection that dissolves the cloud: **risk-tiered automation replaces blanket human review.** Low-risk changes (documentation, non-schema changes, backward-compatible additions) are cleared by CI automation. High-risk changes (schema-breaking modifications, new PII columns, financial metric logic changes) are routed to the governance reviewer with a pre-generated risk summary, reducing the reviewer's queue from 15–20 to 2–5 high-signal reviews per week.

**Step 3: Build the Future Reality Tree.**

Validate the injection against the UDEs before implementation:

```
Injection: implement risk-tiered CI gate for financial/PII models

→ IF  automation clears low-risk changes without human review
  AND  high-risk changes receive a pre-generated risk summary
  THEN  governance reviewer queue drops to 2–5 high-quality reviews/week → resolves UDE 4
  THEN  delivery time for low-risk changes drops to CI time (~15 min) → resolves UDE 1
  THEN  engineers no longer need to batch changes → resolves UDE 2
  THEN  stakeholders have less incentive to build shadow reports → resolves UDE 3
  THEN  high-risk changes receive focused, high-quality human review → resolves UDE 6
```

Check for Negative Branch Reservations:

- Could the automation miss a genuine high-risk change and let it through? **Mitigation**: classify by schema diff type (column drop, type cast change, new PII column flag) in the CI pipeline; any ambiguous change defaults to HIGH_RISK and requires human review.
- Could reviewers lower their guard on high-risk changes because of reduced volume? **Mitigation**: define a fixed high-risk review checklist (see `assets/data-quality-incident-runbook.md`) and require it to be completed as part of the merge comment.

**Implementation.**

```yaml
# .github/workflows/dbt_governance_check.yml
- name: Risk tier classification
  run: |
    python scripts/classify_governance_risk.py \
      --manifest target/manifest.json \
      --state target/state \
      --output governance_risk_report.json
  # Outputs: risk_tier = LOW | MEDIUM | HIGH for each changed model
  # HIGH models: block merge, request governance-team review
  # LOW/MEDIUM models: auto-approved by CI
```

→ **verify**: governance reviewer queue size drops to < 5 per week within 30 days; delivery cycle time for low-risk changes drops below 1 day; no compliance incidents attributable to auto-approved changes in the following 90 days.

---

## Composition

| Workflow | Entry primitive | Secondary | Close with |
|----------|----------------|-----------|-----------|
| SLA breach investigation | P1 Five Focusing Steps → constraint mart identification | P5 DBR if compute contention is the constraint expression | P3 CRT if breach recurs after fixing the constraint |
| Sprint capacity conflict | P2 Throughput Accounting → T/CU ranking | P5 DBR rope on non-T work | P4 policy-constraint audit if T/CU is good but delivery still slow |
| Recurring freshness incident | P3 CRT → Core Problem identification | P4 policy-constraint audit if Core Problem is a governance rule | R3 EC + FRT if the fix requires resolving a governance conflict |
| PR queue too long | P4 policy-constraint detection → stage timing | R3 CRT + EC + FRT for structural resolution | P2 T/CU to re-prioritize post-fix |

**Do not stack without identifying the constraint first.** Applying DBR scheduling (P5) before identifying whether the constraint is compute or review-SLA wastes the effort. Applying Throughput Accounting (P2) before identifying the constraint stage produces a T/CU ranking that optimizes for the wrong denominator. 5FS (P1) is always step zero.

---

## Primitive Links

| Pattern / Anti-Pattern | Primitive | File |
|------------------------|-----------|------|
| Pipeline lag isolation | #1 Five Focusing Steps | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md) |
| Data-team T/CU ranking | #3 Throughput Accounting | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md) |
| Freshness incident root cause | #5 Current Reality Tree | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md) |
| Approval-queue conflict resolution | #4 Evaporating Cloud | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md) |
| Governance redesign validation | #6 Future Reality Tree | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/06-future-reality-tree.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/06-future-reality-tree.md) |
| Review-queue policy constraint | #10 Policy Constraints | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md) |
| Shared compute scheduling | #2 Drum-Buffer-Rope | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md) |
| Optimizing non-bottleneck (A1) | #1 Five Focusing Steps | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md) |
| Cost-accounting bias (A2) | #3 Throughput Accounting | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md) |
| Invisible policy constraint (A3, A4) | #10 Policy Constraints | [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/10-policy-constraints.md) |

**Full primitive reference**: [`../../foundations-theory-of-constraints/SKILL.md`](../../foundations-theory-of-constraints/SKILL.md)

---

## Sources

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press. Foundation for Five Focusing Steps and the throughput-first mindset applied in P1 and P2.
- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press. Throughput Accounting (T, I, OE) and the T/CU product-mix ranking applied in P2 and R2.
- Corbett, T. (1998). *Throughput Accounting*. North River Press. Practical T/CU decision rules and the inversion of cost-accounting logic.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press/St. Lucie Press. DBR mechanics and policy constraint classification applied in P4, P5, and R1.
- Schragenheim, E. & Dettmer, H.W. (2001). *Manufacturing at Warp Speed*. CRC Press. Policy constraint taxonomy and detection patterns.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. CRT, EC, and FRT construction methodology applied in P3 and R3. Chapter 4 covers policy constraints in knowledge-work environments.
- Goldratt, E.M. (1994). *It's Not Luck*. North River Press. Evaporating Cloud construction and the "challenge every assumption on every arrow" discipline applied in R3.
- dbt Labs. *dbt run_results.json documentation*. [https://docs.getdbt.com/reference/artifacts/run-results-json](https://docs.getdbt.com/reference/artifacts/run-results-json). Pipeline timing extraction used in R1.
- Snowflake Inc. *QUERY_HISTORY view reference*. [https://docs.snowflake.com/en/sql-reference/account-usage/query_history](https://docs.snowflake.com/en/sql-reference/account-usage/query_history). `queued_overload_time` field used in P1 and R1 constraint identification queries.
- Snowflake Inc. *Resource Monitors documentation*. [https://docs.snowflake.com/en/user-guide/resource-monitors](https://docs.snowflake.com/en/user-guide/resource-monitors). Credit-cap mechanism used in P5 DBR rope implementation.
- Primitive playbooks in [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/) — canonical per-primitive definitions, failure modes, and worked examples for all 11 TOC primitives.
