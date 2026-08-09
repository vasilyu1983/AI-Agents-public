# Semantic Layer Patterns

> Purpose: Decide whether you need a semantic layer, then pick the right style of semantic serving for analytics, BI, APIs, and AI / NLQ consumers.

---
## Table of Contents

- [Decision Tree: Do You Need A Semantic Layer?](#decision-tree-do-you-need-a-semantic-layer)
- [Quick Reference](#quick-reference)
- [Pattern 1: dbt Semantic Layer](#pattern-1-dbt-semantic-layer)
- [models/semantic/sem_orders.yml](#modelssemanticsemordersyml)
- [Pattern 2: Lightdash Semantic Layer + Metrics Catalog](#pattern-2-lightdash-semantic-layer-metrics-catalog)
- [Pattern 3: Cube As Headless Serving Layer](#pattern-3-cube-as-headless-serving-layer)
- [Pattern 4: Warehouse-Native Semantics](#pattern-4-warehouse-native-semantics)
- [Snowflake Semantic Views](#snowflake-semantic-views)
- [Databricks Unity Catalog Metric Views](#databricks-unity-catalog-metric-views)
- [Consumer-Fit Rules](#consumer-fit-rules)
- [Migration: Ad-Hoc SQL To Governed Metrics](#migration-ad-hoc-sql-to-governed-metrics)
- [Phase 1: Inventory](#phase-1-inventory)
- [Phase 2: Define](#phase-2-define)
- [Phase 3: Validate](#phase-3-validate)
- [Phase 4: Cut Over](#phase-4-cut-over)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Decision Tree: Do You Need A Semantic Layer?

```text
START: Are the same business metrics being reimplemented in multiple places?
│
├─ NO
│  └─ Keep governed marts only; no semantic layer required yet
│
└─ YES
   │
   ├─ Are most consumers already dbt-native?
   │  ├─ YES -> Compare dbt Semantic Layer and Lightdash
   │  └─ NO
   │
   ├─ Do you need embedded analytics or product-facing APIs?
   │  ├─ YES -> Cube
   │  └─ NO
   │
   ├─ Are you committed to a single warehouse platform?
   │  ├─ Snowflake -> Semantic Views
   │  ├─ Databricks -> Unity Catalog Metric Views
   │  └─ NO -> dbt Semantic Layer, Lightdash, or Cube
   │
   └─ Do consumers need a business-friendly metric catalog as much as a query layer?
      ├─ YES -> Lightdash or a semantic layer paired with a strong catalog
      └─ NO -> dbt Semantic Layer or warehouse-native can be enough
```

---

## Quick Reference

| Option | Best For | Strength | Watch-Out |
|--------|----------|----------|-----------|
| dbt Semantic Layer | dbt-native governed metrics | Keeps semantic definitions close to dbt models | Best fit only when dbt is already central |
| Lightdash | dbt-first BI with metrics catalog and AI-facing docs | Good consumer UX and cataloging | Less suited for application-serving APIs |
| Cube | Headless BI, embedded analytics, APIs | Strong serving layer and caching | Extra infrastructure layer |
| Snowflake Semantic Views | Snowflake-first teams | Native semantics and governance | Single-platform lock-in |
| Databricks Metric Views | Databricks-first teams | Governed metrics integrated with Unity Catalog and AI/BI | Single-platform lock-in |

---

## Pattern 1: dbt Semantic Layer

**Status (June 2026)**: MetricFlow open sourced under Apache 2.0 (Oct 2025, v0.209+). Latest: v0.211 (May 2026). Power BI integration in preview; Tableau Cloud and Trino support GA.

**Use when**

- Canonical metric logic should live next to dbt transformation code
- Most consumers already operate through dbt-native workflows
- The team wants governed reusable metrics without introducing a separate serving product first

**Example**

```yaml
# models/semantic/sem_orders.yml
semantic_models:
  - name: orders
    model: ref('fct_orders')
    defaults:
      agg_time_dimension: ordered_at
    entities:
      - name: order_id
        type: primary
      - name: customer_id
        type: foreign
    measures:
      - name: gross_revenue
        agg: sum
        expr: amount
      - name: order_count
        agg: count
    dimensions:
      - name: ordered_at
        type: time
        type_params:
          time_granularity: day
      - name: order_status
        type: categorical
```

**Guardrails**

- Source semantic models from stable marts, not raw staging models.
- Keep default time dimension explicit.
- Certify metric definitions before exposing them broadly.

---

## Pattern 2: Lightdash Semantic Layer + Metrics Catalog

**Use when**

- You already model in dbt
- Consumers need a business-friendly metrics catalog, verified docs, and self-serve BI
- AI / NLQ use cases need governed metric descriptions, tags, and ownership metadata

**Operating pattern**

- Keep metrics and dimensions described in dbt / Lightdash-aligned metadata.
- Use tags, groups, descriptions, and verified metric workflows consistently.
- Treat the metrics catalog as part of governance, not just a convenience UI.

**Guardrails**

- Do not let Lightdash become the only place metric semantics exist; keep code as the source of truth.
- Hide noisy dimensions by default.
- Review access rules for sensitive metrics and dimensions.

---

## Pattern 3: Cube As Headless Serving Layer

**Use when**

- Metrics must be served to applications, embedded analytics, or external consumers
- You need API-first access, caching, and multi-tenant serving controls

**Example**

```javascript
cube('Orders', {
  sql: `select * from analytics.fct_orders`,

  measures: {
    grossRevenue: {
      sql: 'amount',
      type: 'sum'
    },
    orderCount: {
      type: 'count'
    }
  },

  dimensions: {
    orderedAt: {
      sql: 'ordered_at',
      type: 'time'
    },
    orderStatus: {
      sql: 'order_status',
      type: 'string'
    }
  }
});
```

**Guardrails**

- Keep Cube definitions aligned with the canonical mart contract.
- Pre-aggregate only known hot query shapes.
- Treat Cube as serving infrastructure, not as a substitute for upstream modeling discipline.

---

## Pattern 4: Warehouse-Native Semantics

### Snowflake Semantic Views

**Use when**

- Snowflake is the primary long-term platform
- The team wants native governance and semantic definitions in the same control plane
- Additional serving infrastructure is undesirable

**Guardrails**

- Validate how the view is consumed by dashboards, notebooks, and AI / NLQ tools before standardizing.
- Keep portability expectations low; this is a Snowflake-native choice.

### Databricks Unity Catalog Metric Views

**Use when**

- Databricks is the warehouse and governance center
- Consumers include dashboards, Genie / AI/BI, alerts, and SQL users
- The team values governed YAML-defined metrics in Unity Catalog

**Guardrails**

- Validate query and permission behavior for each consumer type.
- Document platform limitations before committing.

---

## Consumer-Fit Rules

| Consumer Type | Preferred Pattern |
|--------------|-------------------|
| Standard BI dashboards | dbt Semantic Layer, Lightdash, or warehouse-native |
| Business metric catalog | Lightdash, DataHub/OpenMetadata + semantic source |
| Embedded analytics / product APIs | Cube |
| AI / NLQ in warehouse-native environment | Lightdash, Snowflake Semantic Views, Databricks Metric Views |
| Small analytics team with few repeated metrics | No semantic layer yet |

---

## Migration: Ad-Hoc SQL To Governed Metrics

### Phase 1: Inventory

- Collect repeated dashboard SQL and notebook logic
- Identify conflicting KPI definitions
- Decide which marts become the semantic source

### Phase 2: Define

- Define entities, measures, dimensions, filters, and default time dimensions
- Publish owners, descriptions, and access rules

### Phase 3: Validate

- Compare new and old outputs over an agreed historical window
- Check latency, query costs, and consumer usability

### Phase 4: Cut Over

- Point consumers to the governed layer
- Freeze or deprecate duplicate definitions
- Monitor query failures and user confusion closely

Use `../assets/semantic-layer-migration-checklist.md` as the working checklist.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Adding a semantic layer before marts are stable | Metrics drift immediately | Clean marts first |
| Exposing every column as a business dimension | Noisy UX and brittle semantics | Curate dimensions intentionally |
| Using semantic layers as a transformation engine | Hard-to-test business logic | Keep transformations upstream |
| No access model for sensitive metrics | Governance failure | Define row / column / tenant rules early |
| Running parallel metric definitions forever | Trust collapse | Set sunset dates and owners |

---

## Cross-References

- `modeling-patterns.md` — Define stable marts before semantic serving
- `contracts-catalogs-lineage.md` — Publish owners, lineage, and catalog context
- `release-and-ci-patterns.md` — Roll out semantic changes with dual-run validation
- `metric-governance.md` — Version and deprecate metric definitions safely
