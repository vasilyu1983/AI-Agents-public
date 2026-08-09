# Data Quality Testing For Analytics Pipelines

> Purpose: Turn modeling and governance assumptions into executable checks.

---
## Table of Contents

- [Decision Tree: What Type Of Quality Control Do You Need?](#decision-tree-what-type-of-quality-control-do-you-need)
- [Quick Reference](#quick-reference)
- [Baseline Quality Stack](#baseline-quality-stack)
- [Minimum For Shared Marts](#minimum-for-shared-marts)
- [Minimum For Semantic Layer Sources](#minimum-for-semantic-layer-sources)
- [dbt Pattern](#dbt-pattern)
- [Native Tests](#native-tests)
- [Freshness](#freshness)
- [SQLMesh Pattern](#sqlmesh-pattern)
- [What To Use](#what-to-use)
- [Release-Safe Flow](#release-safe-flow)
- [Anomaly Monitoring](#anomaly-monitoring)
- [When To Add It](#when-to-add-it)
- [Good Candidates](#good-candidates)
- [Do Not Do This](#do-not-do-this)
- [Great Expectations And Soda](#great-expectations-and-soda)
- [Coverage Targets](#coverage-targets)
- [CI / CD Checklist](#ci-cd-checklist)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Decision Tree: What Type Of Quality Control Do You Need?

```text
START: What failure are you trying to prevent?
│
├─ Schema / null / uniqueness / relationships
│  └─ Native tests in dbt or SQLMesh
│
├─ Freshness / volume / drift over time
│  └─ Freshness checks + audits + anomaly monitoring
│
├─ Business-rule failures on marts or metrics
│  └─ SQL assertions / audits against the serving model
│
└─ Cross-system or Python pipeline validation
   └─ Great Expectations or Soda, plus warehouse checks
```

---

## Quick Reference

| Tooling Layer | Best For | Default Role |
|--------------|----------|--------------|
| dbt native tests | Structural validation in dbt projects | Mandatory baseline |
| SQLMesh audits / tests | Structural and business-rule validation in SQLMesh projects | Mandatory baseline |
| dbt source freshness | Stale-source detection | Mandatory for critical raw sources |
| Elementary | dbt-oriented anomaly and observability | Optional enhancement |
| Great Expectations | Python / heterogeneous validation | Optional, non-dbt-heavy stacks |
| Soda | SQL-first validation across stacks | Optional, heterogeneous stacks |

---

## Baseline Quality Stack

### Minimum For Shared Marts

- Uniqueness or primary-key expectation
- Required column null checks
- Relationship checks on important foreign keys
- Freshness checks on raw sources or critical marts
- One business-rule assertion for the metric that matters most

### Minimum For Semantic Layer Sources

- Stable schema / contract
- Freshness or load timeliness validation
- Row-count or volume sanity check
- Comparison query for high-risk metric changes

---

## dbt Pattern

### Native Tests

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - not_null
          - unique
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```

### Freshness

```yaml
sources:
  - name: raw
    tables:
      - name: orders
        loaded_at_field: ingested_at
        freshness:
          warn_after: {count: 2, period: hour}
          error_after: {count: 4, period: hour}
```

**Runbook defaults**

- Use `dbt build` for model + test execution in CI or deploy steps
- Use `dbt source freshness` on a schedule for critical raw sources
- Fail deploys on contract or critical-mart test failures

---

## SQLMesh Pattern

### What To Use

- Use tests for expected outputs or model behavior
- Use audits for data-quality assertions that should return failing rows
- Use plans to preview how changes and backfills affect downstream models

### Release-Safe Flow

```bash
sqlmesh test
sqlmesh plan dev
sqlmesh plan prod
```

**Guardrails**

- Keep one audit per important business invariant instead of dozens of weak checks
- Review plan output before production application
- Pair audits with freshness or load-timeliness checks in the orchestration layer

---

## Anomaly Monitoring

### When To Add It

- Static rules exist already
- Stakeholders care about unusual but not strictly invalid changes
- Manual monitoring is no longer acceptable

### Good Candidates

- Volume anomalies on shared facts
- Freshness anomalies on pipeline arrival times
- Distribution shifts on important KPI inputs
- Schema drift alerts for externally owned sources

### Do Not Do This

- Add anomaly tooling before basic uniqueness and null checks exist
- Treat anomaly tools as the single source of truth for correctness

---

## Great Expectations And Soda

Use these when:

- Validation spans Python / Spark / warehouse / files
- The team is not dbt- or SQLMesh-centric
- You need a broader validation layer across systems

Use native transformation-tool checks first when the primary problem lives inside the transformation DAG.

---

## Coverage Targets

| Asset Type | Required Checks | Recommended Extras |
|-----------|-----------------|--------------------|
| Shared dimension | key uniqueness, not null, basic freshness | accepted values, volume trend |
| Shared fact | grain uniqueness, required FKs, freshness | volume trend, distribution checks |
| Executive KPI mart | all above + business-rule assertion | side-by-side comparison query |
| Semantic-layer source model | schema stability, freshness, metric sanity | anomaly and consumer query smoke tests |

---

## CI / CD Checklist

- [ ] PR validates syntax and dependency graph
- [ ] Changed models run structural tests
- [ ] Critical marts run business assertions
- [ ] Semantic-layer sources run comparison queries when KPI logic changes
- [ ] Deploy pipeline blocks on contracted model failure
- [ ] Scheduled checks handle freshness and anomaly monitoring

Use `release-and-ci-patterns.md` for rollout details.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Tests only on staging, none on marts | Shared outputs fail silently | Put tests where consumers rely on data |
| Freshness checks with no owner | Alerts are ignored | Assign owner and escalation path |
| Anomaly tooling replaces deterministic checks | Too many ambiguous alerts | Keep native structural tests first |
| Metric change ships without comparison query | Trust breaks after release | Dual-run key metrics before cutover |
| Warning-only everything | Regressions leak to production | Separate blocking and advisory checks clearly |

---

## Cross-References

- `modeling-patterns.md` — Model shape drives what to test
- `contracts-catalogs-lineage.md` — Contracts define what quality must guarantee
- `metric-governance.md` — Certification requires executable validation
- `release-and-ci-patterns.md` — Wire checks into PR, deploy, and backfill workflows
