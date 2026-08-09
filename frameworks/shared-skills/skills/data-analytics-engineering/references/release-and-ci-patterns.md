# Release And CI Patterns

> Purpose: Roll out analytics-engineering changes safely: PR validation, deploy gating, dual-run comparisons, backfills, and semantic-layer cutovers.

---
## Table of Contents

- [Default Delivery Flow](#default-delivery-flow)
- [dbt Delivery Pattern](#dbt-delivery-pattern)
- [PR Checks](#pr-checks)
- [Release Notes](#release-notes)
- [Good Fit](#good-fit)
- [SQLMesh Delivery Pattern](#sqlmesh-delivery-pattern)
- [PR / Preview Checks](#pr-preview-checks)
- [Release Notes](#release-notes)
- [Good Fit](#good-fit)
- [Dual-Run Validation For Metric Changes](#dual-run-validation-for-metric-changes)
- [Minimum Process](#minimum-process)
- [Backfills](#backfills)
- [Before Running A Backfill](#before-running-a-backfill)
- [After Running A Backfill](#after-running-a-backfill)
- [Semantic Layer Cutover](#semantic-layer-cutover)
- [Safe Path](#safe-path)
- [Do Not Do This](#do-not-do-this)
- [Post-Deploy Monitoring](#post-deploy-monitoring)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Default Delivery Flow

| Phase | Goal | Typical Checks |
|------|------|----------------|
| PR | Catch syntax and logic errors early | parse / compile, local tests, changed-model validation |
| Pre-deploy | Preview impact | plan / state diff, quality checks, comparison queries |
| Deploy | Apply safely | build / plan apply, contract enforcement, alert routing |
| Post-deploy | Confirm no consumer regressions | freshness, diff checks, latency, incident watch |

---

## dbt Delivery Pattern

### PR Checks

```bash
dbt deps
dbt parse
dbt build --select state:modified+
```

### Release Notes

- Use state-aware selection for changed assets
- Block deploy on contracted model failures
- Re-run comparison queries for executive KPI changes

### Good Fit

- Teams already standardized on dbt CI / CD
- Transformations and semantics are both dbt-centered

---

## SQLMesh Delivery Pattern

### PR / Preview Checks

```bash
sqlmesh test
sqlmesh plan dev
sqlmesh plan prod
```

### Release Notes

- Review change categories carefully
- Use forward-only only when the business accepts no backfill
- Treat plan review as a release-control step, not a formality

### Good Fit

- Teams that value explicit rollout plans and environment isolation

---

## Dual-Run Validation For Metric Changes

Use dual-run comparisons when:

- KPI logic changes materially
- A semantic layer replaces dashboard SQL
- Backfills or redefinitions may change historical numbers

### Minimum Process

1. Run old and new definitions over the agreed historical window
2. Compare absolute and percentage deltas
3. Explain expected differences before cutover
4. Require owner sign-off on unexpected differences

---

## Backfills

### Before Running A Backfill

- Confirm the business reason
- Estimate warehouse cost and runtime
- Check downstream dependencies
- Decide whether consumer-facing dashboards need annotation

### After Running A Backfill

- Re-run freshness and quality checks
- Reconfirm semantic-layer outputs if they depend on the changed model
- Notify consumers if historical reporting changed

---

## Semantic Layer Cutover

### Safe Path

- Keep existing dashboards alive during validation
- Compare governed metric outputs against legacy SQL
- Move one dashboard or consumer group at a time where possible
- Add short-lived monitoring on query failures, latency, and adoption

### Do Not Do This

- Replace every dashboard definition at once
- Retire legacy logic before validation finishes
- Assume semantic-layer output matches legacy dashboards without proof

---

## Post-Deploy Monitoring

Monitor at least:

- Freshness failures
- Row-count or volume shifts on critical marts
- Query failures in semantic or BI layer
- Material metric deltas after release
- Consumer-reported confusion or missing fields

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No preview of downstream impact | Surprising breakage in production | Use state diffs or plan review |
| KPI refactor with no side-by-side comparison | Trust erosion | Dual-run before cutover |
| Backfill run with no communications plan | Historical numbers change silently | Publish release note and metric-change notice |
| Semantic migration as a big-bang rewrite | Hard to isolate failures | Phase consumers over |

---

## Cross-References

- `data-quality-testing.md` — Tests and audits that power release gates
- `metric-governance.md` — Communication and versioning around changes
- `semantic-layer-patterns.md` — Migration and cutover implications
- `contracts-catalogs-lineage.md` — Contract changes require explicit rollout care
