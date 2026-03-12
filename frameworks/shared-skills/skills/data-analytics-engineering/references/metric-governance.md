# Metric Governance

> Purpose: Operational framework for managing the full lifecycle of business metrics — definition standards, ownership, versioning, certification, deprecation, and conflict resolution. Freshness anchor: Q1 2026.

---

## Decision Tree: Is This Metric Ready for Production?

```
START: New metric request received
│
├─ Does a canonical metric already exist for this concept?
│   │
│   ├─ YES → Can the existing metric be reused or filtered?
│   │   │
│   │   ├─ YES → Use existing metric with dimension filter
│   │   │        (do NOT create a duplicate)
│   │   │
│   │   └─ NO → Document why existing metric is insufficient
│   │            → Propose modification or new derived metric
│   │            → Route through metric review process
│   │
│   └─ NO → Continue to definition phase ↓
│
├─ Has the metric been defined with all required fields?
│   │
│   ├─ NO → Complete metric definition template (see below)
│   │
│   └─ YES → Has the metric been validated against known values?
│       │
│       ├─ NO → Run validation tests against existing reports
│       │
│       └─ YES → Has the metric been reviewed by domain owner?
│           │
│           ├─ NO → Submit for peer review
│           │
│           └─ YES → CERTIFY and publish to metric catalog
```

---

## Metric Definition Template

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | snake_case, verb-free, noun-based | `monthly_recurring_revenue` |
| `display_name` | Human-readable label | Monthly Recurring Revenue |
| `abbreviation` | Standard short form | MRR |
| `description` | One-sentence business definition | Sum of all active subscription amounts normalized to monthly billing |
| `type` | simple, derived, cumulative, ratio | derived |
| `formula` | Exact calculation logic | `SUM(subscription_amount * normalization_factor) WHERE status = 'active'` |
| `grain` | Lowest supported time granularity | daily |
| `dimensions` | Allowed grouping dimensions | plan_type, region, acquisition_channel |
| `filters` | Default filters applied | status = 'active', is_test = false |
| `owner` | Team or individual | @revenue-team |
| `source_model` | dbt model or table reference | `ref('fct_subscriptions')` |
| `certified` | Certification status | true / false / pending |
| `version` | Semantic version | 2.1.0 |

### Optional Fields

| Field | Description |
|-------|-------------|
| `related_metrics` | Metrics commonly used alongside this one |
| `known_limitations` | Edge cases, exclusions, or caveats |
| `refresh_frequency` | How often underlying data updates |
| `slo` | Freshness and accuracy targets |
| `tags` | Categorization labels |
| `deprecated_aliases` | Former names this metric was known by |

---

## Naming Standards

### Convention Rules

| Rule | Good | Bad |
|------|------|-----|
| snake_case, lowercase | `total_revenue` | `TotalRevenue`, `total-revenue` |
| Noun-based, no verbs | `order_count` | `count_orders`, `get_order_count` |
| Include time scope if inherent | `monthly_recurring_revenue` | `mrr` (as primary name) |
| Prefix with domain for ambiguity | `marketing_qualified_leads` | `qualified_leads` |
| No abbreviations in name | `customer_acquisition_cost` | `cac` (use as abbreviation field) |
| Specify aggregation type | `average_order_value` | `order_value` |

### Dimension Naming

| Rule | Good | Bad |
|------|------|-----|
| snake_case, noun-based | `plan_type` | `planType`, `plan-type` |
| Include entity prefix if ambiguous | `customer_region` | `region` (which entity?) |
| Use `_at` suffix for timestamps | `created_at` | `creation_date`, `created` |
| Use `_date` suffix for date-only | `order_date` | `order_day` |
| Boolean: `is_` or `has_` prefix | `is_active` | `active`, `status_active` |

---

## Ownership Assignment

### RACI Matrix for Metrics

| Activity | Domain Team | Analytics Eng | Data Platform | Stakeholder |
|----------|-------------|---------------|---------------|-------------|
| Define business logic | **A** | C | I | **R** |
| Implement in semantic layer | C | **R/A** | I | I |
| Validate correctness | C | **R** | I | **A** |
| Approve changes | **A** | C | I | C |
| Monitor data quality | I | **R** | C | I |
| Deprecate metric | **A** | **R** | I | C |

- **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

### Ownership Transfer Checklist

- [ ] New owner acknowledges responsibility
- [ ] Transfer documented in metric catalog
- [ ] Alert/monitor subscriptions updated
- [ ] Stakeholder notification sent
- [ ] Knowledge transfer session completed
- [ ] Access permissions updated

---

## Versioning Protocol

### Semantic Versioning for Metrics

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Bug fix (same intent, corrected logic) | Patch: x.x.+1 | 2.1.0 → 2.1.1 |
| New dimension or filter added | Minor: x.+1.0 | 2.1.0 → 2.2.0 |
| Calculation logic changed | Major: +1.0.0 | 2.1.0 → 3.0.0 |
| Name change (alias preserved) | Major: +1.0.0 | 2.1.0 → 3.0.0 |
| Grain change | Major: +1.0.0 | 2.1.0 → 3.0.0 |

### Version Change Workflow

1. **Propose**: PR with metric definition changes + migration notes
2. **Validate**: Run comparison tests (old vs new values)
3. **Review**: Domain owner approves
4. **Document**: Changelog entry with before/after values
5. **Deploy**: Update semantic layer
6. **Communicate**: Notify consumers via standard channel
7. **Deprecate old**: Follow deprecation workflow if major version

### Changelog Format

```markdown
## monthly_recurring_revenue v3.0.0 (2026-02-10)

### Breaking Change
- Excluded trial subscriptions from MRR calculation
- Previous: included all subscriptions with status IN ('active', 'trial')
- New: includes only subscriptions with status = 'active'

### Impact
- MRR will decrease by approximately 5-8%
- Affected dashboards: Executive Summary, Board Deck, Investor Report
- Migration: filter `is_trial = false` achieves equivalent result on v2.x

### Validation
- Compared v2.x vs v3.0.0 for last 12 months
- Diff report: [link to validation]
```

---

## Certification Process

### Certification Levels

| Level | Badge | Requirements | Review Cadence |
|-------|-------|-------------|----------------|
| **Draft** | - | Metric defined, not validated | N/A |
| **Reviewed** | - | Peer-reviewed, tests passing | N/A |
| **Certified** | Certified | Validated against source of truth, owner assigned, SLO defined | Quarterly |
| **Gold Standard** | Gold | Certified + used by executive reporting | Monthly |

### Certification Checklist

- [ ] Business definition reviewed by stakeholder
- [ ] Implementation matches business definition exactly
- [ ] Tests cover: not_null, range, freshness, anomaly detection
- [ ] Values validated against independent source (finance system, CRM)
- [ ] Owner assigned and acknowledged
- [ ] SLO defined (freshness, accuracy tolerance)
- [ ] Listed in metric catalog with all required fields
- [ ] At least one dashboard uses this metric correctly
- [ ] No conflicting definitions exist in the catalog
- [ ] Quarterly review scheduled

### Decertification Triggers

- Test failures unresolved for >48 hours
- Owner departed without transfer
- Source model deprecated
- Values diverge from source of truth by >2%
- No consumer usage for >90 days

---

## Deprecation Workflow

### Timeline

| Day | Action |
|-----|--------|
| 0 | Announce deprecation with reason and replacement metric |
| 0 | Add `deprecated: true` flag to metric definition |
| 7 | Notify all dashboard/report owners using the metric |
| 14 | Add deprecation warning to query results/API responses |
| 30 | Remove from default catalog views (still queryable) |
| 60 | Disable metric (queries return error with migration guide) |
| 90 | Delete metric definition from codebase |

### Deprecation Notice Template

```yaml
# In metric definition
deprecated: true
deprecated_at: "2026-02-10"
deprecated_reason: "Replaced by net_revenue_v2 which excludes test accounts"
replacement_metric: net_revenue_v2
migration_guide: |
  Replace `net_revenue` with `net_revenue_v2`.
  If you need the old behavior (including test accounts),
  use `net_revenue_v2` with filter `include_test_accounts = true`.
sunset_date: "2026-05-10"
```

---

## Conflict Resolution

### Common Conflicts

| Conflict | Resolution |
|----------|-----------|
| Two teams define same metric differently | Escalate to data council; one becomes canonical, other becomes variant with qualified name |
| Dashboard shows different number than finance report | Audit both calculations; align to source-of-truth system (usually finance) |
| Metric name ambiguous across domains | Add domain prefix: `marketing_revenue` vs `finance_revenue` |
| Stakeholder wants metric changed but others depend on it | Create new version; follow deprecation workflow for old |
| Historical values change after backfill | Document via changelog; communicate before and after values |

### Conflict Resolution Process

1. **Identify**: Document both definitions with exact SQL/logic
2. **Compare**: Run both calculations side-by-side for 90-day window
3. **Adjudicate**: Domain owner or data council decides canonical version
4. **Resolve**: Losing definition becomes either deprecated or renamed variant
5. **Communicate**: Announce resolution with rationale to all consumers

---

## Metric Catalog Requirements

### Minimum Viable Catalog

| Feature | Required | Recommended |
|---------|----------|-------------|
| Searchable metric list | Yes | - |
| Business definition for each metric | Yes | - |
| Technical implementation link | Yes | - |
| Owner and certification status | Yes | - |
| Lineage (upstream models) | - | Yes |
| Usage statistics (who queries) | - | Yes |
| Change history | - | Yes |
| Embedded preview chart | - | Yes |
| Related metrics | - | Yes |
| Data freshness indicator | - | Yes |

### Catalog Tools (2026)

| Tool | Integration | Cost |
|------|------------|------|
| dbt Explorer | dbt Cloud native | Included |
| Atlan | Multi-tool | Enterprise |
| Select Star | Warehouse-native | SaaS |
| DataHub | Open-source | Free |
| Notion/Confluence | Manual | Low |

---

## Stakeholder Communication Patterns

### Communication Matrix

| Event | Channel | Audience | Timing |
|-------|---------|----------|--------|
| New metric certified | Slack #data-announcements | All analysts | Same day |
| Metric definition change (minor) | Slack #data-announcements | Metric consumers | Before deploy |
| Metric definition change (major) | Email + Slack + meeting | All stakeholders | 2 weeks before |
| Metric deprecated | Email + dashboard banner | All consumers | 60 days before sunset |
| Metric outage / data issue | Slack #data-incidents | All consumers | Immediately |
| Quarterly metric review | Meeting invite | Domain owners + analytics | Scheduled quarterly |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Metrics defined only in spreadsheets | No version control, no CI, no lineage | Define in code (YAML in semantic layer) |
| No owner assigned | Nobody responsible when metric breaks | Ownership mandatory for certification |
| "Same metric, different number" in two dashboards | Erodes trust in data | Single canonical definition in semantic layer |
| Changing metric logic without versioning | Historical comparisons become invalid | Semantic versioning + changelog |
| Deprecating without replacement | Consumers left without guidance | Always provide migration path |
| Certifying once, never reviewing | Certified metrics drift from reality | Quarterly recertification with validation |
| Every request creates a new metric | Metric sprawl, overlapping definitions | Reuse + filter before creating new |
| No conflict resolution process | Disputes linger, parallel definitions persist | Formal escalation to data council |

---

## Cross-References

- `semantic-layer-patterns.md` — Technical implementation of governed metric definitions
- `data-quality-testing.md` — Test suites that validate metric correctness
- `data-mesh-patterns.md` — Domain ownership model for metric governance
- `permissions-collections.md` — Access control for metric consumption

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
