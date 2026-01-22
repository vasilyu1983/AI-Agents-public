---
name: data-analytics-engineering
description: Analytics engineering for reliable metrics and BI readiness. Build transformation layers, dimensional models, semantic metrics, data quality tests, and documentation. Use when you need dbt or SQL transformation strategy, metrics definition, or analytics data modeling.
---

# Data Analytics Engineering

## Scope

- Define metrics, grains, and dimensional models.
- Build transformation layers and semantic models.
- Implement data quality tests and observability.
- Document datasets, lineage, and ownership.
- Align analytics outputs with BI and product needs.

## Ask For Inputs

- Business metrics and decision use cases.
- Source systems, data freshness, and latency needs.
- Existing warehouse, tooling, and orchestration.
- Expected data volumes and change cadence.
- Governance requirements and access controls.

## Workflow

1. Define metric dictionary and grains.
2. Design staging, intermediate, and mart layers.
3. Model dimensions and facts with clear keys.
4. Build semantic layer and metric definitions.
5. Add tests for freshness, nulls, ranges, and duplicates.
6. Document lineage, owners, and SLAs.
7. Plan rollout, backfills, and validation checks.

## Outputs

- Metric dictionary and semantic model.
- Data model with schema and grain definitions.
- Transformation plan and dbt or SQLMesh structure.
- Data quality test suite and alerting plan.
- Documentation and ownership map.

## Quality Checks

- Keep metric definitions stable and versioned.
- Avoid mixed grains in a single model.
- Ensure tests cover critical joins and aggregates.
- Validate against source of truth and historical baselines.

## Templates

- `assets/metric-dictionary.md` for metric definitions and owners.
- `assets/semantic-layer-spec.md` for entities, measures, and dimensions.
- `assets/data-quality-test-plan.md` for test coverage planning.

## Resources

- `references/modeling-patterns.md` for modeling guidance and data quality patterns.
- `references/tool-comparison-2026.md` for dbt vs SQLMesh vs Coalesce decision matrix.

## Related Skills

- Use [data-lake-platform](../data-lake-platform/SKILL.md) for platform architecture.
- Use [data-sql-optimization](../data-sql-optimization/SKILL.md) for query tuning.
- Use [ai-ml-data-science](../ai-ml-data-science/SKILL.md) for modeling and experiments.

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about analytics engineering, data modeling, or BI, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best tool for [analytics engineering/data modeling/BI]?"
- "What should I use for [transformation/semantic layer/metrics]?"
- "What's the latest in analytics engineering?"
- "Current best practices for [dbt/metrics layers/data quality]?"
- "Is [tool/approach] still relevant in 2026?"
- "[dbt] vs [SQLMesh] vs [other]?"
- "Best BI tool for [use case]?"
- "SQLMesh acquisition" or "Fivetran transformation"
- "Agentic analytics" or "AI data workflows"
- "Metric debt" or "metric governance"

### Required Searches

1. Search: `"analytics engineering best practices 2026"`
2. Search: `"[dbt/SQLMesh/semantic layer] vs alternatives 2026"`
3. Search: `"analytics engineering trends January 2026"`
4. Search: `"[specific tool] new releases 2026"`
5. Search: `"agentic analytics AI data 2026"` (for AI-related queries)

### What to Report

After searching, provide:

- **Current landscape**: What analytics tools/patterns are popular NOW
- **Emerging trends**: New tools, patterns, or standards gaining traction
- **Deprecated/declining**: Tools/approaches losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Key 2026 Developments

- **SQLMesh acquired by Fivetran (2025)**: Changes competitive dynamics
- **Semantic Layer + AI**: 300% accuracy improvement for LLM queries vs raw SQL
- **Agentic analytics**: AI agents autonomously building dashboards and detecting anomalies
- **Metric debt**: Governance concern for inconsistent metric definitions
- **dbt-expectations**: Now maintained by Metaplane (Dec 2024 fork)
- **Open Semantic Interchange (OSI)**: Emerging interoperability standard

### Example Topics (verify with fresh search)

- Transformation tools (dbt, SQLMesh, Coalesce)
- Semantic layers (dbt Semantic Layer, Cube, AtScale, warehouse-native)
- Metrics stores and headless BI
- Data quality tools (dbt tests, Elementary, dbt-expectations/Metaplane)
- BI platforms (Metabase, Superset, Lightdash, Hex)
- Data modeling patterns (dimensional, wide tables, activity schema)
- Analytics engineering workflows and CI/CD
- Agentic AI workflows for analytics
- Data mesh and domain-owned data products
