# Metric Governance

> Purpose: Govern shared metrics like public interfaces: explicit owners, versioned changes, certification, catalog visibility, and deprecation discipline.

---
## Table of Contents

- [Decision Tree: Is This Metric Ready For Production?](#decision-tree-is-this-metric-ready-for-production)
- [Required Fields For A Production Metric](#required-fields-for-a-production-metric)
- [Ownership Model](#ownership-model)
- [Minimum Viable Ownership](#minimum-viable-ownership)
- [Governance Rule](#governance-rule)
- [Versioning Rules](#versioning-rules)
- [Use Semantic Versioning For Shared Metrics](#use-semantic-versioning-for-shared-metrics)
- [Breaking Change Examples](#breaking-change-examples)
- [Non-Breaking Examples](#non-breaking-examples)
- [Certification Levels](#certification-levels)
- [Deprecation Workflow](#deprecation-workflow)
- [Default Timeline](#default-timeline)
- [Catalog Requirements](#catalog-requirements)
- [Minimum Viable Metric Catalog](#minimum-viable-metric-catalog)
- [Tooling Guidance](#tooling-guidance)
- [Communication Rules](#communication-rules)
- [Review Cadence](#review-cadence)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Decision Tree: Is This Metric Ready For Production?

```text
START: Does the metric answer a repeatable business question?
│
├─ NO
│  └─ Keep it exploratory
│
└─ YES
   │
   ├─ Is the definition written in code or a governed semantic layer?
   │  ├─ NO -> Not production-ready
   │  └─ YES
   │
   ├─ Is the grain explicit and the owner assigned?
   │  ├─ NO -> Not production-ready
   │  └─ YES
   │
   ├─ Is there executable validation?
   │  ├─ NO -> Not production-ready
   │  └─ YES
   │
   └─ Is the metric cataloged and communicated to consumers?
      ├─ NO -> Publish first
      └─ YES -> Ready for certification
```

---

## Required Fields For A Production Metric

| Field | Required | Notes |
|------|----------|-------|
| Stable name | Yes | Avoid synonyms for the same KPI |
| Business definition | Yes | Plain-language interpretation |
| Grain | Yes | What one row or observation represents |
| Included / excluded rows | Yes | Prevent silent scope drift |
| Source model or semantic definition | Yes | Code-linked implementation |
| Business owner | Yes | Decision owner |
| Technical owner | Yes | Pipeline or semantic owner |
| Validation method | Yes | Test, audit, or comparison query |
| Freshness expectation | Yes | Especially for executive use |
| Change history | Recommended | Required once multiple teams consume it |

---

## Ownership Model

### Minimum Viable Ownership

- Business owner: signs off on meaning
- Technical owner: signs off on implementation and quality
- Consumer list: who must be warned if the metric changes

### Governance Rule

If a metric has no accountable owner, it cannot be certified.

---

## Versioning Rules

### Use Semantic Versioning For Shared Metrics

- `MAJOR`: breaking change to definition or scope
- `MINOR`: additive dimension, metadata, or non-breaking usability improvement
- `PATCH`: documentation or validation fix with no metric-result change

### Breaking Change Examples

- Revenue changes from booked to collected cash
- Active user switches from 30-day to 28-day window
- A filtered metric becomes unfiltered

### Non-Breaking Examples

- Add new documented dimension
- Improve descriptions or ownership metadata
- Add stronger validation without changing logic

---

## Certification Levels

| Level | Meaning | Minimum Bar |
|------|---------|-------------|
| Draft | Still under development | Definition exists, not yet trusted broadly |
| Team-ready | Safe for one team | Owner assigned, code-defined, basic validation |
| Certified | Safe for org-wide reporting | Strong validation, cataloged, communicated, reviewed |
| Deprecated | Do not adopt for new work | Replacement or sunset path defined |

---

## Deprecation Workflow

### Default Timeline

| Day | Action |
|----|--------|
| 0 | Announce deprecation and replacement path |
| 7 | Add warnings in catalog / dashboards |
| 30 | Remove from default views and new development guidance |
| 60+ | Retire if consumers have migrated |

Use `../assets/metric-change-notice.md` for the communication template.

---

## Catalog Requirements

### Minimum Viable Metric Catalog

| Capability | Required |
|-----------|----------|
| Searchable list of metrics | Yes |
| Business definition | Yes |
| Technical definition link | Yes |
| Owner and status | Yes |
| Freshness / quality signal | Recommended |
| Usage / popularity signal | Recommended |
| Related assets and lineage | Recommended |

### Tooling Guidance

- `dbt` docs / catalog surfaces are a good developer baseline.
- `Lightdash` metrics catalog is strong for business-facing metric discovery in dbt-first teams.
- `DataHub` and `OpenMetadata` are better fits when governance, ownership, lineage, assertions, or agent-facing context matter across many tools.
- `Notion` or `Confluence` can bootstrap a catalog, but they should not remain the system of record once shared metrics become operational dependencies.

---

## Communication Rules

- Announce every major metric change before deployment.
- For executive KPIs, require both business and technical approval.
- Keep the deprecation window explicit.
- Publish where consumers already work: catalog, dashboard banner, Slack / email, or release notes.

---

## Review Cadence

- Quarterly review for certified metrics
- Immediate review after incidents or major source-system changes
- Re-certify if the underlying contract or semantic logic changes materially

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| KPI logic lives only in dashboards | No shared source of truth | Move logic into marts or semantic layer |
| Spreadsheet metric registry | No executable governance | Keep the system of record in code / metadata platform |
| No owner on executive metric | No accountability during incidents | Owner required for certification |
| Metric changes without versioning | Historical comparison becomes misleading | Version and communicate |
| Per-team forks of the same KPI | Trust collapses | Canonical metric plus documented variants |

---

## Cross-References

- `contracts-catalogs-lineage.md` — Contracts and metadata operating model for governed metrics
- `data-quality-testing.md` — Validation required before certification
- `semantic-layer-patterns.md` — Where shared metric interfaces should live
- `release-and-ci-patterns.md` — Rollout and dual-run validation for metric changes
