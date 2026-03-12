# Data Mesh Patterns

> Purpose: Operational guide for implementing data mesh architecture — domain ownership, data products, self-serve platform, and federated governance. Includes readiness assessment and migration from centralized architecture. Freshness anchor: Q1 2026.

---

## Decision Tree: Ready for Data Mesh?

```
START: Considering data mesh adoption
│
├─ Do you have >3 distinct business domains producing data?
│   │
│   ├─ NO → Centralized data team is likely sufficient
│   │        Data mesh overhead will not pay off
│   │
│   └─ YES → Is your central data team a bottleneck?
│       │
│       ├─ NO → Current model is working; optimize, don't restructure
│       │
│       └─ YES → Do domain teams have (or can hire) data engineers?
│           │
│           ├─ NO → Invest in hiring/training first
│           │        Mesh without domain capability fails
│           │
│           └─ YES → Do you have executive sponsorship across domains?
│               │
│               ├─ NO → Build the case; mesh requires organizational change
│               │
│               └─ YES → Is your data platform mature enough for self-serve?
│                   │
│                   ├─ NO → Build self-serve platform first (Phase 1)
│                   │        Then migrate domains incrementally
│                   │
│                   └─ YES → READY — Start with 2-3 pilot domains
```

---

## Quick Reference: Data Mesh Principles (2026)

| Principle | What It Means | What It Does NOT Mean |
|-----------|--------------|----------------------|
| Domain ownership | Domain teams own their analytical data | Every team builds everything from scratch |
| Data as a product | Data has SLOs, docs, schema, discoverability | Every dataset is a "product" |
| Self-serve platform | Shared infrastructure reduces per-domain effort | No central team exists |
| Federated governance | Global standards, local execution | No governance at all |

---

## Domain Ownership Boundaries

### Identifying Domain Boundaries

| Signal | Indicates Domain Boundary |
|--------|--------------------------|
| Different business capability | Orders vs Payments vs Marketing |
| Different data sources | Separate operational databases |
| Different stakeholders | Finance team vs Product team |
| Different change cadence | Real-time events vs monthly reports |
| Different compliance requirements | PII-heavy vs public data |

### Domain Boundary Checklist

- [ ] Each domain maps to a business capability (not a team)
- [ ] Domain has clear data ownership (source-of-truth systems)
- [ ] Domain can independently develop and deploy data products
- [ ] Cross-domain dependencies are explicit and contractual
- [ ] No circular dependencies between domains

### Example Domain Map

```
┌─────────────────────────────────────────────────────────┐
│                    E-Commerce Company                      │
├──────────────┬──────────────┬──────────────┬─────────────┤
│   Orders     │  Customers   │  Inventory   │  Marketing  │
│              │              │              │             │
│ - fct_orders │ - dim_cust   │ - fct_stock  │ - fct_camps │
│ - fct_returns│ - fct_ltv    │ - fct_supply │ - fct_attrib│
│ - fct_refunds│ - dim_segments│ - dim_products│ - fct_spend│
│              │              │              │             │
│ Owner: OPS   │ Owner: CX    │ Owner: SUPPLY│ Owner: MKT  │
└──────────────┴──────────────┴──────────────┴─────────────┘
```

---

## Data Product Specification

### Required Components

| Component | Description | Example |
|-----------|-------------|---------|
| Schema | Versioned schema contract | Protobuf, JSON Schema, dbt YAML |
| SLO | Freshness, completeness, accuracy targets | Freshness <4h, completeness >99.5% |
| Documentation | Business context, column descriptions | Auto-generated from dbt docs |
| Discovery | Registered in data catalog | Listed in DataHub/Atlan |
| Lineage | Upstream and downstream dependencies | dbt lineage graph |
| Quality tests | Automated validation suite | dbt tests + anomaly monitors |
| Access policy | Who can read, how to request access | IAM roles + request workflow |
| Contact | Responsible team and escalation path | Slack channel + PagerDuty |

### Data Product YAML Template

```yaml
# data-products/orders/product.yml
apiVersion: data-mesh/v1
kind: DataProduct
metadata:
  name: orders
  domain: order-management
  owner: orders-team
  contact:
    slack: "#orders-data"
    pagerduty: orders-data-oncall
  tags: [core, revenue, certified]

spec:
  description: >
    Canonical order data including all order lifecycle events,
    line items, and payment status.

  outputs:
    - name: fct_orders
      type: table
      schema: analytics.orders
      format: delta  # or iceberg, parquet
      refresh: hourly
      grain: one row per order
      columns:
        - name: order_id
          type: string
          description: Unique order identifier
          pii: false
        - name: customer_id
          type: string
          description: FK to customers domain
          pii: false
        - name: total_amount
          type: decimal(10,2)
          description: Gross order total before discounts
          pii: false
        - name: email
          type: string
          description: Customer email at time of order
          pii: true
          masking: hash

  slo:
    freshness:
      warn: 2h
      error: 4h
    completeness:
      target: 99.5%
      measured_on: order_id
    accuracy:
      validation: monthly reconciliation with finance system

  dependencies:
    upstream:
      - source: raw.ecommerce.orders
        type: database
      - source: raw.ecommerce.order_items
        type: database
    downstream:
      - consumer: finance-domain/fct_revenue
      - consumer: marketing-domain/fct_attribution

  quality:
    tests:
      - unique: order_id
      - not_null: [order_id, customer_id, total_amount, created_at]
      - freshness: {column: created_at, warn: 2h, error: 4h}
      - volume_anomaly: {sensitivity: 3, training_days: 30}
```

---

## Self-Serve Data Platform Design

### Platform Capabilities Matrix

| Capability | Purpose | Tools (2026) |
|------------|---------|-------------|
| Data ingestion | Move data from sources to lake | Fivetran, Airbyte, custom connectors |
| Transformation | SQL/Python transforms | dbt, Spark, SQLMesh |
| Storage | Managed lake/warehouse | Iceberg on S3, Delta Lake, Snowflake |
| Orchestration | Schedule and monitor pipelines | Dagster, Airflow, Prefect |
| Quality | Automated testing and monitoring | Elementary, Great Expectations, Monte Carlo |
| Catalog | Discovery and documentation | DataHub, Atlan, dbt Explorer |
| Access control | Fine-grained permissions | Unity Catalog, Lake Formation, custom IAM |
| Compute | On-demand query engines | Trino, Spark, Snowflake, BigQuery |
| Observability | Pipeline and data health | Elementary, Monte Carlo, Datadog |

### Platform Team Responsibilities

- Build and maintain shared infrastructure
- Provide templates and blueprints for domain teams
- Enforce global governance standards via automation
- Support domain teams (not own their data)
- Manage cross-cutting concerns (security, cost, compliance)

### Platform Blueprint: Domain Onboarding

```
1. Domain requests onboarding → Platform team provisions:
   ├─ Dedicated schema/namespace in warehouse
   ├─ IAM roles (domain-admin, domain-write, domain-read)
   ├─ dbt project template with CI/CD pipeline
   ├─ Monitoring dashboards (freshness, quality, cost)
   └─ Catalog registration automation

2. Domain team configures:
   ├─ Source connections
   ├─ Transformation models
   ├─ Quality tests
   ├─ Data product definitions
   └─ Access policies for consumers

3. Platform validates:
   ├─ Schema contracts registered
   ├─ SLOs defined
   ├─ Quality tests passing
   ├─ Documentation complete
   └─ Catalog entry published
```

---

## Federated Computational Governance

### Global Standards (Enforced by Platform)

| Standard | Enforcement | Mechanism |
|----------|------------|-----------|
| Naming conventions | Automated | CI linter |
| Schema contract registration | Automated | Deploy gate |
| Minimum test coverage | Automated | CI check |
| PII classification | Semi-automated | Scanner + manual review |
| SLO definition | Automated | Required field in product spec |
| Documentation completeness | Automated | dbt docs coverage check |
| Cost guardrails | Automated | Query cost limits, alerts |

### Local Decisions (Owned by Domain)

| Decision | Domain Authority |
|----------|-----------------|
| Transformation logic | Full |
| Refresh frequency (above SLO minimum) | Full |
| Additional quality tests | Full |
| Internal model structure | Full |
| Choice of additional tools | Within platform catalog |
| Team process and workflow | Full |

### Governance Automation

```yaml
# .github/workflows/data-product-ci.yml (conceptual)
name: Data Product CI
on:
  pull_request:
    paths:
      - 'data-products/**'

jobs:
  validate:
    steps:
      - name: Schema contract check
        run: validate-schema --product ${{ matrix.product }}

      - name: Test coverage check
        run: |
          coverage=$(dbt-coverage compute)
          if [ "$coverage" -lt 80 ]; then exit 1; fi

      - name: Naming convention lint
        run: lint-names --convention snake_case

      - name: PII scan
        run: pii-scanner --product ${{ matrix.product }}

      - name: SLO definition check
        run: validate-slo --product ${{ matrix.product }}

      - name: Documentation completeness
        run: dbt docs coverage --min 90
```

---

## Interoperability Standards

### Cross-Domain Data Contracts

```yaml
# contracts/orders-to-finance.yml
apiVersion: data-contract/v1
kind: DataContract
metadata:
  name: orders-to-finance
  provider: orders-domain
  consumer: finance-domain

spec:
  output:
    table: analytics.orders.fct_orders
    columns:
      - name: order_id
        type: string
        not_null: true
      - name: total_amount
        type: decimal(10,2)
        not_null: true
      - name: completed_at
        type: timestamp
    freshness:
      max_delay: 4h

  breaking_change_policy:
    notification: 14 days advance
    channel: "#data-contracts"
    approval_required: true

  testing:
    provider_tests:
      - schema_match
      - freshness_slo
      - volume_anomaly
    consumer_tests:
      - referential_integrity_with: fct_revenue
```

---

## Migration: Centralized to Mesh

### Phase 1: Foundation (Months 1-3)

- [ ] Assess organizational readiness (decision tree above)
- [ ] Define domain boundaries based on business capabilities
- [ ] Select 2-3 pilot domains with willing, capable teams
- [ ] Build self-serve platform MVP (templates, CI/CD, catalog)
- [ ] Define global governance standards

### Phase 2: Pilot (Months 4-6)

- [ ] Pilot domains create first data products
- [ ] Platform team provides hands-on support
- [ ] Establish cross-domain data contracts
- [ ] Validate governance automation
- [ ] Measure: time-to-production for new data products

### Phase 3: Scale (Months 7-12)

- [ ] Onboard remaining domains incrementally
- [ ] Migrate existing centralized models to domain ownership
- [ ] Build interoperability patterns for cross-domain queries
- [ ] Establish data product SLO monitoring
- [ ] Create domain data product review process

### Phase 4: Optimize (Month 12+)

- [ ] Retrospective on governance effectiveness
- [ ] Platform improvements based on domain feedback
- [ ] Advanced patterns: event-driven data products, real-time mesh
- [ ] Cost optimization per domain
- [ ] Maturity assessment across all domains

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Mesh without platform | Every domain reinvents infrastructure | Build self-serve platform FIRST |
| Forcing mesh on small orgs | Overhead exceeds benefit with <3 domains | Stay centralized until growth demands it |
| Domains without data engineers | Domain "ownership" means nobody owns it | Ensure each domain has capable staff |
| No governance standards | Inconsistent schemas, naming, quality | Federated governance with automated enforcement |
| Central team becomes "platform" in name only | Still bottleneck, just renamed | Platform must genuinely enable self-serve |
| All data is a "product" | Everything is special, nothing is prioritized | Tier data products by criticality |
| Ignoring cross-domain dependencies | Breaks cascade without warning | Explicit data contracts between domains |
| Big-bang migration | High risk, organizational resistance | Incremental, pilot-first approach |
| No executive sponsorship | Domains resist change without mandate | Secure top-down support before starting |

---

## Cross-References

- `data-quality-patterns.md` — Quality standards for data products
- `security-access-patterns.md` — Access control for cross-domain data
- `semantic-layer-patterns.md` — Metric definitions that span domains
- `metric-governance.md` — Governance model for shared metrics

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
