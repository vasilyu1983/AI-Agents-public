# Semantic Layer Patterns

> Purpose: Operational guide for choosing, implementing, and governing semantic layers that translate raw warehouse tables into governed, reusable metric definitions. Freshness anchor: Q1 2026.

---

## Decision Tree: Choosing a Semantic Layer Approach

```
START: Do you need governed, reusable metrics across multiple consumers?
│
├─ NO → Ad-hoc SQL with documented conventions is sufficient
│
├─ YES → Are you already using dbt as your transformation layer?
│   │
│   ├─ YES → Is your team >5 analysts querying independently?
│   │   │
│   │   ├─ YES → dbt Semantic Layer + MetricFlow
│   │   │        (native integration, single source of truth)
│   │   │
│   │   └─ NO → dbt metrics with exposures
│   │            (lighter lift, still governed)
│   │
│   └─ NO → Do you need sub-second query latency for dashboards?
│       │
│       ├─ YES → Cube (pre-aggregation + caching layer)
│       │
│       └─ NO → Do you have a modern warehouse with native semantics?
│           │
│           ├─ YES (BigQuery, Databricks) → Warehouse-native semantic layer
│           │
│           └─ NO → Cube or LookML depending on existing stack
```

---

## Quick Reference: Semantic Layer Tools (2026)

| Tool | Best For | Query API | Caching | Governance | License |
|------|----------|-----------|---------|------------|---------|
| dbt Semantic Layer + MetricFlow | dbt-native shops | GraphQL, JDBC | Warehouse-level | Built-in | dbt Cloud (paid) |
| Cube | Multi-source, low-latency | REST, GraphQL, SQL | Pre-aggregation + in-memory | Role-based | Open core |
| LookML (Looker) | Google Cloud stack | Looker API | PDTs + in-memory | Explore-level | Google Cloud |
| BigQuery Semantic Layer | BQ-only environments | BQ SQL | Materialized views | IAM-integrated | GCP pricing |
| Databricks Unity Catalog | Databricks lakehouse | SQL, REST | Delta caching | Unity Catalog ACLs | Databricks pricing |
| Apache Superset Semantic Layer | Open-source BI | REST | Redis/Memcached | Role-based | Apache 2.0 |

---

## Core Concepts

### Metric Definition Components

- **Measures**: Aggregations applied to columns (SUM, COUNT, AVG, COUNT_DISTINCT)
- **Dimensions**: Attributes for grouping and filtering (categorical, time-based)
- **Entities**: Join keys that connect semantic models (user_id, order_id)
- **Filters**: Default or required constraints applied to metrics
- **Grain**: The lowest level of detail a metric supports

### Metric Types

| Type | Definition | Example |
|------|-----------|---------|
| Simple | Single measure, one aggregation | `total_revenue = SUM(amount)` |
| Derived | Calculation across measures | `aov = total_revenue / order_count` |
| Cumulative | Running aggregation over time | `cumulative_revenue = SUM(amount) OVER time` |
| Ratio | Division of two measures | `conversion_rate = orders / sessions` |
| Filtered | Base metric + mandatory filter | `us_revenue = total_revenue WHERE country='US'` |

---

## Operational Patterns

### Pattern 1: MetricFlow in dbt (dbt Semantic Layer)

- **Use when**: Already on dbt Cloud, team queries metrics via downstream tools
- **Implementation**:

```yaml
# models/semantic/sem_orders.yml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_date
    model: ref('fct_orders')
    entities:
      - name: order_id
        type: primary
      - name: customer_id
        type: foreign
    measures:
      - name: order_total
        agg: sum
        expr: amount
      - name: order_count
        agg: count
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: order_status
        type: categorical

# models/semantic/metrics.yml
metrics:
  - name: revenue
    type: simple
    type_params:
      measure: order_total
    filter: |
      {{ Dimension('order__order_status') }} = 'completed'

  - name: average_order_value
    type: derived
    type_params:
      expr: revenue / order_count
      metrics:
        - name: revenue
        - name: order_count
```

### Pattern 2: Cube Pre-Aggregation Layer

- **Use when**: Need sub-second dashboards, multiple data sources, or headless BI
- **Implementation**:

```javascript
// schema/Orders.js
cube('Orders', {
  sql: `SELECT * FROM public.fct_orders`,

  preAggregations: {
    ordersByDay: {
      measures: [Orders.totalRevenue, Orders.count],
      dimensions: [Orders.status],
      timeDimension: Orders.createdAt,
      granularity: 'day',
      refreshKey: {
        every: '1 hour'
      }
    }
  },

  measures: {
    count: { type: 'count' },
    totalRevenue: {
      sql: 'amount',
      type: 'sum',
      format: 'currency'
    },
    averageOrderValue: {
      sql: `${totalRevenue} / NULLIF(${count}, 0)`,
      type: 'number',
      format: 'currency'
    }
  },

  dimensions: {
    status: { sql: 'status', type: 'string' },
    createdAt: { sql: 'created_at', type: 'time' }
  }
});
```

### Pattern 3: Warehouse-Native Semantics (BigQuery)

- **Use when**: Fully on BigQuery, want zero additional infrastructure
- **Implementation**:

```sql
-- Create authorized view as semantic interface
CREATE OR REPLACE VIEW `project.analytics.v_revenue_metrics` AS
SELECT
  DATE_TRUNC(order_date, DAY) AS metric_date,
  region,
  SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS revenue,
  COUNT(DISTINCT order_id) AS order_count,
  SAFE_DIVIDE(
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END),
    COUNT(DISTINCT order_id)
  ) AS average_order_value
FROM `project.warehouse.fct_orders`
GROUP BY 1, 2;

-- Materialize for performance
CREATE MATERIALIZED VIEW `project.analytics.mv_revenue_daily`
AS SELECT * FROM `project.analytics.v_revenue_metrics`;
```

### Pattern 4: Headless BI via API

- **Use when**: Metrics consumed by applications, notebooks, Slack bots — not just dashboards
- **Components**:
  - Semantic layer as query engine (Cube, MetricFlow)
  - REST or GraphQL API for programmatic access
  - SDK for application embedding
  - Cache layer for repeated queries

```bash
# Cube REST API query example
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Authorization: Bearer ${CUBE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["Orders.totalRevenue"],
    "dimensions": ["Orders.status"],
    "timeDimensions": [{
      "dimension": "Orders.createdAt",
      "granularity": "month",
      "dateRange": ["2026-01-01", "2026-03-31"]
    }]
  }'
```

---

## Caching Strategies

| Strategy | Latency | Freshness | Complexity | Use When |
|----------|---------|-----------|------------|----------|
| No cache (pass-through) | 2-30s | Real-time | Low | Small data, few users |
| Warehouse materialized views | 1-5s | Scheduled | Low | Moderate load, single warehouse |
| Cube pre-aggregations | <1s | Configurable | Medium | High concurrency dashboards |
| Redis/Memcached query cache | <100ms | TTL-based | Medium | Repeated identical queries |
| Application-level cache | <50ms | Manual invalidation | High | Embedding in products |

### Cache Invalidation Checklist

- [ ] Define refresh schedule aligned with data loading cadence
- [ ] Set TTL shorter than data freshness SLO
- [ ] Implement cache warming for critical dashboards
- [ ] Monitor cache hit ratio (target >80% for production)
- [ ] Add manual invalidation endpoint for emergency refreshes
- [ ] Log cache misses for capacity planning

---

## Migration: Ad-Hoc SQL to Governed Metrics

### Phase 1: Inventory (Week 1-2)

- [ ] Audit existing dashboards for metric definitions
- [ ] Catalog all SQL containing business logic (CASE, SUM, filters)
- [ ] Identify conflicting definitions for same metric name
- [ ] Map metric consumers (dashboards, reports, notebooks, apps)

### Phase 2: Define (Week 3-4)

- [ ] Establish naming convention (see metric-governance.md)
- [ ] Write semantic model YAML for top 10 metrics
- [ ] Validate metric outputs match existing dashboard values
- [ ] Get stakeholder sign-off on canonical definitions

### Phase 3: Implement (Week 5-8)

- [ ] Deploy semantic layer infrastructure
- [ ] Migrate top 10 metrics to semantic definitions
- [ ] Connect one downstream consumer as pilot
- [ ] Set up monitoring for query latency and correctness

### Phase 4: Govern (Week 9+)

- [ ] Deprecate ad-hoc SQL versions with migration guide
- [ ] Enforce semantic layer for new metric requests
- [ ] Add CI checks for metric definition changes
- [ ] Publish metric catalog to stakeholders

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Metrics defined in BI tool only | No reuse, no versioning, drift across dashboards | Move to code-defined semantic layer |
| Every column exposed as dimension | Query explosion, confusing for consumers | Curate dimensions intentionally per metric |
| Pre-aggregating everything | Storage bloat, maintenance overhead | Pre-aggregate only high-traffic query patterns |
| No cache invalidation strategy | Stale data served to users silently | Align cache TTL with pipeline schedule |
| Semantic layer as afterthought | Adoption failure, parallel definitions persist | Treat as core infrastructure, not optional layer |
| Skipping validation during migration | Metric values silently change | Automated comparison tests before cutover |
| Single monolithic semantic model | Slow CI, merge conflicts, unclear ownership | One semantic model per domain or source model |
| Exposing raw IDs as dimensions | Meaningless to business users | Join to descriptive labels in semantic model |

---

## Cross-References

- `metric-governance.md` — Naming, versioning, and deprecation protocols for metrics
- `data-quality-testing.md` — Testing strategies for the models underlying semantic layers
- `data-mesh-patterns.md` — Domain ownership model that feeds semantic layer boundaries
- `monitoring-alerting-patterns.md` — Alerting on semantic layer query latency and errors

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
