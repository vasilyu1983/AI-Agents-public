# Analytics Modeling Patterns

> Purpose: Practical patterns for designing marts that are stable enough for dashboards, semantic layers, APIs, and AI / NLQ consumers.

---
## Table of Contents

- [Decision Tree: Pick The Final Model Shape](#decision-tree-pick-the-final-model-shape)
- [Core Principles](#core-principles)
- [Layer Architecture](#layer-architecture)
- [Staging Rules](#staging-rules)
- [Intermediate Rules](#intermediate-rules)
- [Mart Rules](#mart-rules)
- [Pattern 1: Star Schema](#pattern-1-star-schema)
- [Pattern 2: Wide Table / Pre-Joined Mart](#pattern-2-wide-table-pre-joined-mart)
- [Pattern 3: Activity Schema / Event Mart](#pattern-3-activity-schema-event-mart)
- [Choosing Between Star, Wide, And Activity](#choosing-between-star-wide-and-activity)
- [Contracts On Marts](#contracts-on-marts)
- [Semantic Boundary Rules](#semantic-boundary-rules)
- [Dimensional Modeling Rules](#dimensional-modeling-rules)
- [Facts](#facts)
- [Dimensions](#dimensions)
- [Time](#time)
- [Data Contract Checklist](#data-contract-checklist)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Decision Tree: Pick The Final Model Shape

```text
START: What are consumers actually doing with this dataset?
│
├─ Executive / BI reporting with repeated joins and reusable metrics
│  └─ Default to a star schema (facts + dimensions)
│
├─ High-concurrency dashboarding with fixed dimensions and simple metrics
│  └─ Consider a wide table or pre-joined mart
│
├─ Behavioral analysis, paths, funnels, retention, or event exploration
│  └─ Use an activity schema / event mart
│
└─ Multiple use cases mixed together
   └─ Split them into separate marts or semantic definitions
```

---

## Core Principles

- One model, one grain.
- Staging models normalize sources; they are not user-facing APIs.
- Intermediate models compose logic; marts expose stable business interfaces.
- Final models should optimize for comprehension first, warehouse cleverness second.
- If metric consumers disagree on row inclusion, the contract is not finished.

---

## Layer Architecture

| Layer | Purpose | Naming Pattern | Contract Default | Notes |
|------|---------|----------------|------------------|-------|
| Staging | Source cleanup, typing, standardization | `stg_*` | No | Keep close to source semantics |
| Intermediate | Business logic composition and reuse | `int_*` | Selective | Safe place for reusable joins and filters |
| Marts | Consumer-facing facts, dimensions, wide tables | `fct_*`, `dim_*`, `mart_*` | Yes for shared assets | Treat as APIs |
| Semantic | Governed metrics and curated dimensions | platform-specific | Yes | Add only when it improves reuse |

### Staging Rules

- Preserve source granularity.
- Rename fields to stable business-friendly names.
- Cast data types once.
- Keep source-system quirks visible in staging, not hidden in marts.

### Intermediate Rules

- Reuse logic across marts instead of copy-pasting joins.
- Build conformed dimensions or shared filtered subsets here.
- Keep intermediate tables out of BI tools unless they are deliberately published.

### Mart Rules

- Document grain in the model description and catalog.
- Publish owners, freshness expectations, and quality status.
- Prefer additive measures in marts; use semantic layers for reusable ratio logic where needed.

---

## Pattern 1: Star Schema

**Use when**

- Many dashboards reuse the same entities and measures
- Analysts need flexible slicing by business dimensions
- The team wants a clean boundary before adding a semantic layer

**Structure**

- Facts contain measurable business events at one grain
- Dimensions provide descriptive context
- Fact foreign keys point to conformed dimensions

**Typical example**

| Model | Grain | Notes |
|------|-------|-------|
| `fct_orders` | one row per order | additive revenue measures |
| `dim_customer` | one row per customer | descriptive attributes |
| `dim_product` | one row per product | reusable classification |

**Guardrails**

- Do not embed customer attributes directly in every fact unless latency and concurrency require it.
- Keep slowly changing logic explicit.
- Avoid two facts with nearly identical semantics and different filters.

---

## Pattern 2: Wide Table / Pre-Joined Mart

**Use when**

- Dashboard workloads are repetitive and high-concurrency
- Consumers do not need many custom joins
- You need low operational friction for BI users

**Good fit**

- Executive scorecards
- Revenue reporting with fixed segmentation
- Operational dashboards with stable dimensions

**Watch-outs**

- Wide tables can hide duplicated business logic.
- Schema growth becomes expensive when every new dimension lands in the same table.
- They are poor substitutes for event analysis or exploratory work.

**Rule**

Use wide tables intentionally for serving, not because upstream modeling was skipped.

---

## Pattern 3: Activity Schema / Event Mart

**Use when**

- You analyze journeys, funnels, retention, or feature adoption
- Time-ordered behavior matters more than dimensional elegance
- You need one reusable base for many behavioral metrics

**Typical fields**

- `entity_id`
- `activity_ts`
- `activity_name`
- `activity_properties`
- key business dimensions for segmentation

**Guardrails**

- Keep event naming stable.
- Normalize the few segmentation dimensions that matter most.
- Do not force every behavioral metric into a classic fact/dimension pattern if it destroys event meaning.

---

## Choosing Between Star, Wide, And Activity

| Requirement | Default Choice | Why |
|------------|----------------|-----|
| Reusable KPI reporting | Star schema | Best general-purpose business model |
| Fixed dashboards with heavy concurrency | Wide table | Fewer joins, simpler consumption |
| Behavioral analytics | Activity schema | Preserves event semantics |
| AI / NLQ over governed metrics | Star + semantic layer | Clean business entities and metric reuse |
| Embedded analytics API | Star or activity + semantic layer / headless serving | Separation between modeling and serving |

---

## Contracts On Marts

Add contracts on marts that are shared, reused, or externally consumed.

Good contract candidates:

- Executive KPI marts
- Shared domain facts and dimensions
- Semantic-layer source models
- Tables consumed by reverse ETL, APIs, or AI surfaces

Avoid contracting:

- Temporary debugging tables
- Early exploration models
- Rapidly changing staging work in active source migrations

---

## Semantic Boundary Rules

- Marts define trusted business entities and clean measures.
- Semantic layers define curated metric interfaces and consumer-facing dimensions.
- Do not put every transformation in the semantic layer.
- Do not push business-critical metric logic into dashboards only.

---

## Dimensional Modeling Rules

### Facts

- Grain must be explicit.
- Measures should be business-meaningful and testable.
- Foreign keys should be nullable only when business semantics permit it.

### Dimensions

- Prefer stable surrogate or business keys.
- Keep slowly changing policy explicit.
- Store descriptive fields once unless wide-table serving requires duplication.

### Time

- Use one default business time field per model.
- Distinguish event time from load time and snapshot time.

---

## Data Contract Checklist

- [ ] Grain documented
- [ ] Primary key or uniqueness expectation defined
- [ ] Required columns listed
- [ ] Freshness target documented
- [ ] Owner assigned
- [ ] Downstream consumers known

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Mixed grains in one mart | Impossible to reason about counts and sums | Split the model or define a clearer grain |
| Dashboard-only metric logic | Drift and silent inconsistency | Move logic into marts or semantic layer |
| Over-normalized BI layer | Analysts rebuild joins repeatedly | Publish conformed dimensions or a serving mart |
| One mega-wide table for everything | Slow change velocity, unclear ownership | Create domain marts with clear contracts |
| Event data forced into rigid star design | Journey logic becomes brittle | Keep a behavioral mart or activity schema |

---

## Cross-References

- `tool-comparison.md` — Pick the transformation and serving stack
- `semantic-layer-patterns.md` — Add governed metric serving only where it pays off
- `contracts-catalogs-lineage.md` — Apply contracts, ownership, lineage, and catalog rules
- `data-quality-testing.md` — Turn model assumptions into executable checks
