# Contracts, Catalogs, And Lineage

> Purpose: Operational guidance for turning shared data assets into governed interfaces with explicit schema, semantics, ownership, lineage, and discoverability.

---
## Table of Contents

- [What A Data Contract Should Cover](#what-a-data-contract-should-cover)
- [Decision Tree: Should This Asset Be Contracted?](#decision-tree-should-this-asset-be-contracted)
- [dbt Contract Example](#dbt-contract-example)
- [Metadata Platform Guidance](#metadata-platform-guidance)
- [OpenMetadata](#openmetadata)
- [DataHub](#datahub)
- [OpenLineage](#openlineage)
- [Minimum Catalog Fields](#minimum-catalog-fields)
- [Lineage Operating Model](#lineage-operating-model)
- [Minimum Viable Lineage](#minimum-viable-lineage)
- [Why This Matters In 2026](#why-this-matters-in-2026)
- [Ownership Rules](#ownership-rules)
- [AI / Agent Readiness Checklist](#ai-agent-readiness-checklist)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## What A Data Contract Should Cover

For analytics engineering, a useful contract usually covers four layers:

1. Schema: required columns, data types, keys
2. Semantics: grain, allowed dimensions, included / excluded rows
3. Freshness: update expectation and failure policy
4. Ownership: accountable owner, escalation path, and access boundaries

---

## Decision Tree: Should This Asset Be Contracted?

```text
START: Is the asset shared outside the creating team?
│
├─ NO
│  └─ Contract optional
│
└─ YES
   │
   ├─ Does a dashboard, semantic layer, API, or AI workflow depend on it?
   │  ├─ YES -> Contract it
   │  └─ MAYBE
   │
   ├─ Would a schema or semantic change break consumers?
   │  ├─ YES -> Contract it
   │  └─ NO -> Contract may be lightweight
   │
   └─ Is the asset a temporary exploration artifact?
      ├─ YES -> Do not contract yet
      └─ NO -> Contract it
```

---

## dbt Contract Example

```yaml
models:
  - name: fct_orders
    config:
      contract:
        enforced: true
    columns:
      - name: order_id
        data_type: string
      - name: ordered_at
        data_type: timestamp
      - name: amount
        data_type: numeric
```

Use this on shared marts and semantic-layer source models, not every staging file by default.

---

## Metadata Platform Guidance

### OpenMetadata

Use when you want:

- Data contracts and governance in the metadata plane
- Lineage, quality, domains, and collaboration in one system
- Agent / MCP-friendly metadata context for AI workflows

### DataHub

Use when you want:

- Rich metadata APIs and programmable governance
- Assertions, lineage, ownership, glossary, and incident workflows
- Strong integration story across many data systems

### OpenLineage

Use when you want:

- Standardized lineage events across orchestrators and transformation tools

Rule:

OpenLineage is a transport and interoperability layer. Pair it with a catalog such as DataHub or OpenMetadata for discoverability and governance.

---

## Minimum Catalog Fields

Every shared mart, metric, or semantic asset should expose:

- Name
- Description
- Grain
- Owner
- Upstream lineage
- Quality status
- Freshness expectation
- Access / sensitivity notes

If AI or NLQ tools read the metadata, also include:

- Business synonyms
- Default filters or exclusions
- Example business questions the asset answers

---

## Lineage Operating Model

### Minimum Viable Lineage

- Transformation lineage from source to mart
- Semantic-layer lineage from mart to metric
- Dashboard or consumer lineage for high-value outputs

### Why This Matters

- Humans need impact analysis before changes
- Agents need trustworthy context to answer data questions safely
- Governance programs need clear blast-radius visibility

---

## Ownership Rules

- One accountable owner per shared asset
- One escalation channel for incidents
- Domain ownership should align with business meaning, not whichever team wrote the SQL first

If the organization is using a data-product or data-mesh model, align contracts and ownership boundaries with domain boundaries instead of warehouse folders alone.

For broader data-product patterns, see [data-lake-platform data mesh patterns](../../data-lake-platform/references/data-mesh-patterns.md).

---

## AI / Agent Readiness Checklist

- [ ] Asset has a plain-language description
- [ ] Owner is visible
- [ ] Grain is explicit
- [ ] Lineage is available
- [ ] Quality / freshness status is queryable
- [ ] Sensitive fields are clearly labeled

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Schema contract without semantic contract | Consumers still interpret data differently | Add grain and row-inclusion rules |
| Catalog with no owner fields | Discovery without accountability | Ownership is mandatory |
| Lineage only in engineers' heads | Changes create surprise breakage | Publish lineage in the metadata plane |
| AI access to raw undocumented assets | Hallucinated or unsafe answers | Expose governed assets with metadata first |

---

## Cross-References

- `modeling-patterns.md` — Decide which marts deserve contracts
- `metric-governance.md` — Govern metrics on top of contracted assets
- `release-and-ci-patterns.md` — Roll out contract changes safely
- `data-quality-testing.md` — Enforce contract promises with tests and audits
