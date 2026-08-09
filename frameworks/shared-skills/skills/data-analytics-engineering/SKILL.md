---
name: data-analytics-engineering
description: Builds analytics engineering layers for metrics, contracts, and BI-ready models. Use when shaping dbt or SQLMesh marts, metric governance, lineage, or data quality.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Data Analytics Engineering

Code-defined marts, metrics as APIs, contracts on critical interfaces, semantic layers only where they improve reuse or AI/BI consumption, and metadata systems that expose owners, lineage, quality, and governance to both humans and agents.

Primary sources: `data/sources.json`. Refresh time-sensitive claims against official docs before giving definitive recommendations.

## When to Use

- Choose or improve an analytics engineering stack (`dbt`, `SQLMesh`, `Coalesce`)
- Define marts, grains, dimensions, facts, wide tables, or activity schemas
- Design or migrate a semantic layer (`dbt Semantic Layer`, `Lightdash`, `Cube`, warehouse-native)
- Add data contracts, metric governance, ownership, catalogs, and lineage
- Build data quality checks, freshness monitoring, anomaly detection, and release gates
- Prepare BI-ready models for dashboards, notebooks, APIs, or AI/NLQ analytics

## When NOT to Use

- Lakehouse or ingestion architecture -> [data-lake-platform](../data-lake-platform/SKILL.md)
- Product/event instrumentation, attribution, or identity resolution -> `marketing-product-analytics`
- OLTP tuning, indexes, locks, or transactional database operations -> [data-sql-optimization](../data-sql-optimization/SKILL.md)
- Metabase API automation -> [data-metabase](../data-metabase/SKILL.md)
- ML feature engineering, experiments, or model evaluation -> [ai-ml-data-science](../ai-ml-data-science/SKILL.md)

## Triage Checklist

Run through these before any recommendation:

- [ ] What are the canonical business metrics and who owns each one?
- [ ] Serving requirements: dashboards, notebooks, APIs, embedded analytics, or AI/NLQ?
- [ ] Transformation baseline: `dbt`, `SQLMesh`, visual tooling, or warehouse SQL only?
- [ ] Which datasets are contract-worthy (downstream consumers depend on schema, freshness, semantics)?
- [ ] Semantic layer needed, or are well-governed marts sufficient today?
- [ ] Which metadata systems already cover catalog, lineage, ownership, access, and quality?

## Stack Status (July 2026)

| Tool | Status | Key 2026 Fact |
|------|--------|---------------|
| dbt Core | v2.0 in alpha; open source, Apache 2.0, built on Fusion foundations | [Upgrade guide](https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v2) |
| dbt Fusion | GA on Snowflake (dbt platform); preview on BigQuery/Redshift; private preview on Databricks; no GA date confirmed yet | New dbt-platform projects default to Fusion; local/CLI Fusion still preview across adapters |
| dbt + SDF | SDF Labs acquired Jan 2025; Rust SQL compiler is now the Fusion engine | Enables column-level lineage and typed SQL |
| MetricFlow | Open sourced Apache 2.0 (Oct 2025, v0.209+); latest v0.211 (May 12, 2026) | Anchors the Open Semantic Interchange (OSI) v1.0 spec (Jan 2026) with Snowflake, Databricks, Salesforce, ThoughtSpot, Atlan, Alation, Denodo |
| SQLMesh | Contributed to Linux Foundation by Fivetran (announced March 25, 2026, KubeCon EU); Apache 2.0 | Fivetran acquired SQLMesh's creator, Tobiko Data, in Sept 2025; founding LF members include Benzinga, CloudKitchens, Harness, Infinite Lambda, Jump AI, Minerva |

Verify GA/preview status per adapter before recommending a Fusion cutover — it changes monthly; treat the table above as directional, not a substitute for the [Fusion availability page](https://docs.getdbt.com/docs/fusion/fusion-availability).

## Default Workflow

1. **Lock the metric contract first** — define KPI names, business logic, grain, owner, and dimensions in `assets/metric-dictionary.md`
2. **Choose one transformation baseline** — standardize on `dbt` or `SQLMesh` before debating semantic-layer tooling (`references/tool-comparison.md`)
3. **Model for consumption** — build `staging -> intermediate -> marts` layers, pick final shape (star, wide, or activity schema) with `references/modeling-patterns.md`
4. **Add contracts on critical interfaces** — enforce schema, ownership, freshness, and quality expectations (`references/contracts-catalogs-lineage.md`)
5. **Choose semantic serving only where it pays off** — use `references/semantic-layer-patterns.md` to decide between dbt-native, Lightdash, Cube, or warehouse-native
6. **Add release-safe quality controls** — static tests, freshness, audits, anomaly monitoring (`references/data-quality-testing.md` and `references/release-and-ci-patterns.md`)
7. **Publish discoverability and governance** — catalog assets, lineage, owners, and change notices (`references/metric-governance.md` and `assets/ownership-catalog-worksheet.md`)

## Decision: Choose Transformation Baseline

```text
What does your team care about most?
  Plan-based deployment, environment isolation, backfill control
    -> SQLMesh (now Linux Foundation / Apache 2.0)
  Broadest ecosystem, contracts, semantic layer, dbt-native CI
    -> dbt (Core v2 alpha or dbt platform with Fusion)
  Visual metadata-driven development, enterprise onboarding speed
    -> Coalesce
  Already on dbt and want faster compile + typed SQL
    -> Upgrade to dbt Fusion (GA on Snowflake; preview elsewhere)
```

## Decision: Add a Semantic Layer?

```text
Are the same business metrics reimplemented in 3+ places?
  NO -> Governed marts only; revisit when the answer flips to YES
  YES ->
    Most consumers are dbt-native?
      YES -> dbt Semantic Layer (MetricFlow) or Lightdash
    Need embedded analytics or product-facing APIs?
      YES -> Cube
    Single warehouse platform?
      Snowflake -> Snowflake Semantic Views
      Databricks -> Unity Catalog Metric Views
    Consumers need a business-friendly metric catalog as much as a query layer?
      YES -> Lightdash (or semantic layer + OpenMetadata/DataHub catalog)
```

## Quick Reference

| Task | Resource | When to Load |
|------|----------|-------------|
| Choose dbt vs SQLMesh vs Coalesce | `references/tool-comparison.md` | New stack selection or migration |
| Pick star vs wide vs activity schema | `references/modeling-patterns.md` | Designing marts and semantic boundaries |
| Decide whether to add a semantic layer | `references/semantic-layer-patterns.md` | Metrics reuse, NLQ, API, or BI serving |
| Add contracts, ownership, lineage, catalog | `references/contracts-catalogs-lineage.md` | Shared marts and governed datasets |
| Add tests, audits, anomaly checks, CI gates | `references/data-quality-testing.md` | Prevent regressions and stale data |
| Define metric lifecycle and deprecation | `references/metric-governance.md` | Executive metrics and shared KPI programs |
| Plan rollout, dual-run, backfills | `references/release-and-ci-patterns.md` | Safe deployment and migration |
| PII separation, vault pattern, pseudonymisation | `references/pii-vault-and-pseudonymisation.md` | LLM/AI-facing query surfaces or GDPR scope |
| Draft metric definitions | `assets/metric-dictionary.md` | New KPIs or metric refactors |
| Draft semantic layer design | `assets/semantic-layer-spec.md` | Serving layer design review |
| Draft quality coverage | `assets/data-quality-test-plan.md` | Model-by-model test planning |
| Communicate metric changes | `assets/metric-change-notice.md` | Breaking or non-breaking metric updates |
| Document owners and catalog fields | `assets/ownership-catalog-worksheet.md` | Governance and discoverability setup |
| Migrate to a semantic layer | `assets/semantic-layer-migration-checklist.md` | Ad-hoc SQL to governed metrics |
| Handle data quality incidents | `assets/data-quality-incident-runbook.md` | Failures, stale data, or contract breaks |

## CI/CD Quality Gate Checklist

**dbt projects (PR checks):**

```bash
dbt deps
dbt parse
dbt build --select state:modified+
```

- [ ] No contracted model failures
- [ ] Freshness checks pass for critical sources
- [ ] Comparison queries run for executive KPI changes
- [ ] Schema tests pass on all mart models
- [ ] Anomaly monitoring shows no new alerts post-deploy

**SQLMesh projects (PR/preview checks):**

```bash
sqlmesh plan --no-prompts dev
sqlmesh test
sqlmesh audit --models state:modified+
```

- [ ] Plan diff reviewed before `apply`
- [ ] Unit tests pass locally (no warehouse compute consumed)
- [ ] Audits pass on changed models
- [ ] Forward-only or backfill scope confirmed before deploy

## Operating Principles

1. **Metrics are APIs** — stable names, clear owners, versioned changes, explicit deprecation windows; do not change KPI semantics silently.
2. **One model, one grain** — a mart must have one unambiguous grain; create a separate model for a different grain instead of mixing.
3. **Contracts on shared interfaces** — required for executive marts, handoff tables, and models used by many teams; do not contract every transient staging model.
4. **Semantic layers are optional** — add when multiple consumers need governed reuse, NLQ/AI access, or product-grade metric APIs; skip when well-governed marts are enough.
5. **Metadata serves humans and agents** — require descriptions, owners, lineage, quality status, and access boundaries on high-value assets.

## Common Anti-Patterns

| Anti-Pattern | Root Cause | Fix |
|---|---|---|
| KPI logic in dashboards or notebooks | No governed mart | Define in mart or semantic model first |
| Multiple grains in one mart | Dashboard convenience | Create separate models per grain |
| Contracts on every staging model | Misapplied governance | Contract only shared, high-stakes interfaces |
| Semantic layer before marts are stable | Premature abstraction | Stabilize marts before defining entities/measures |
| Same 360 table for every request | No modeling discipline | One model, one grain, one purpose |
| Allowing AI/NLQ access to undocumented marts | Missing metadata | Require grain, owner, freshness contract before AI access |

## Known Traps

- Slowly changing dimensions leaking into KPI joins and silently changing historical numbers.
- Metric refactors that change semantics without a notice, owner sign-off, or deprecation window.
- Identity stitching, attribution, and semantic metrics coexisting without explicit precedence rules.
- Assuming a semantic layer removes the need for release discipline, data tests, and change communication.
- **Fan-out duplication**: joining a fact to a dimension with a hidden one-to-many relationship (e.g. multiple addresses per customer, multiple attribution touches per order) silently multiplies additive measures. Check row counts before and after every join added to a mart, not just at the end.
- **Non-additive measures in semantic layers**: ratios, distinct counts, and percentiles do not roll up by simple summation across dimensions. A semantic layer that lets consumers slice a pre-computed ratio by a new dimension will produce a plausible but wrong number unless the measure is defined to recompute from its base components at query time.
- **SCD Type 2 joins without effective-dating**: joining a fact table to a dimension's current row (instead of the row valid at the fact's event time) rewrites history every time a dimension attribute changes — a common source of "the numbers changed even though nothing happened this month."
- **Backfills without idempotency**: a backfill or reprocessing job that appends instead of replacing (or lacks a natural dedup key) creates silent double-counting that structural uniqueness tests may not catch if the test only runs on the latest partition.
- **Timezone/DST drift in freshness SLAs**: freshness windows defined in wall-clock local time break twice a year and near midnight UTC boundaries; define freshness thresholds in UTC and treat calendar-day grain as a modeling decision, not an accident of the source system's timestamp.
- **Simpson's paradox in aggregated KPIs**: an org-wide metric can move in the opposite direction of every underlying segment when segment mix shifts; before alerting on a KPI's overall trend, check whether segment-level trends actually agree with it.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/analytics_linter.py` | Validate, lint, and health-score a metric dictionary JSON file |

```bash
# Validate required fields, duplicate names, and undefined data sources
python scripts/analytics_linter.py validate --input data/valid-metric-dictionary.json

# Lint metric quality: missing owners, undocumented dimensions, naming, SLAs
python scripts/analytics_linter.py lint --input data/valid-metric-dictionary.json

# Generate a Markdown metric dictionary health report
python scripts/analytics_linter.py report \
  --input data/sample-metric-dictionary.json \
  --output metric-health-report.md
```

## Data

| File | Description |
|------|-------------|
| `data/sources.json` | Curated reference sources for this skill |
| `data/valid-metric-dictionary.json` | Production-valid 15-metric dictionary for smoke tests and quickstart examples |
| `data/sample-metric-dictionary.json` | Realistic 15-metric dictionary with intentional gaps for linting demos |

## Navigation

| File | Load When |
|------|-----------|
| [references/tool-comparison.md](references/tool-comparison.md) | Choosing or comparing dbt, SQLMesh, Coalesce, or semantic-layer tools |
| [references/modeling-patterns.md](references/modeling-patterns.md) | Designing mart layers, grain, star/wide/activity schemas |
| [references/semantic-layer-patterns.md](references/semantic-layer-patterns.md) | Deciding on and implementing a semantic serving layer |
| [references/contracts-catalogs-lineage.md](references/contracts-catalogs-lineage.md) | Adding data contracts, catalog metadata, and lineage on shared assets |
| [references/data-quality-testing.md](references/data-quality-testing.md) | Building test suites, freshness checks, and anomaly monitoring |
| [references/metric-governance.md](references/metric-governance.md) | Governing, versioning, and deprecating shared KPIs |
| [references/release-and-ci-patterns.md](references/release-and-ci-patterns.md) | CI/CD pipelines, dual-run validation, backfills, safe cutovers |
| [references/pii-vault-and-pseudonymisation.md](references/pii-vault-and-pseudonymisation.md) | Separating PII from analytical facts for LLM/AI or GDPR-scoped surfaces |
| [references/causal-inference-applied.md](references/causal-inference-applied.md) | DAG-driven feature selection, DML, observational ATE estimation |
| [references/information-theory-applied.md](references/information-theory-applied.md) | MI feature selection, KL drift detection, MDL clustering |
| [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) | Pipeline lag isolation, capacity reallocation, approval-queue debug |
| [references/network-science-applied.md](references/network-science-applied.md) | Centrality, PageRank, community detection applied to lineage graphs |

## Templates

- `assets/metric-dictionary.md`
- `assets/semantic-layer-spec.md`
- `assets/data-quality-test-plan.md`
- `assets/metric-change-notice.md`
- `assets/ownership-catalog-worksheet.md`
- `assets/semantic-layer-migration-checklist.md`
- `assets/data-quality-incident-runbook.md`

## Related Skills

- [data-lake-platform](../data-lake-platform/SKILL.md) — ingestion, table formats, orchestration, data mesh
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — transactional SQL performance and operational tuning
- `marketing-product-analytics` — event instrumentation and acquisition measurement
- [data-metabase](../data-metabase/SKILL.md) — Metabase automation and dashboard scripting
- [ai-ml-data-science](../ai-ml-data-science/SKILL.md) — experimentation and modeling workflows

## Current-Source Policy

- Prefer `trust_tier: primary` entries in `data/sources.json` for vendor capabilities, syntax, pricing, limits, and release-sensitive recommendations.
- For recommendation questions, refresh against current official docs and recent release notes.
- Separate verified facts from judgment calls; label strategic opinions explicitly.
- If web access is unavailable, state that the recommendation is partially unverified.

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
