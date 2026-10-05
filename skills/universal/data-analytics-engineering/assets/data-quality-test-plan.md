# Data Quality Test Plan

## Model Inventory

| Model | Tier | Grain | Contracted | Owner | Serving use |
| --- | --- | --- | --- | --- | --- |
|  | critical / standard / exploratory |  | yes / no |  | dashboard / API / AI / notebook |

## Required Checks

| Model | Check type | Rule | Severity | Run stage | Alert target |
| --- | --- | --- | --- | --- | --- |
|  | schema / uniqueness / relationships / freshness / volume / distribution / audit / anomaly |  | warn / error | PR / deploy / scheduled |  |

## Release Gates

- [ ] Critical models have schema and freshness checks
- [ ] Every contracted model has explicit owner and escalation path
- [ ] Dual-run comparison exists for changed KPI logic
- [ ] Failure thresholds are defined for deploy blocking vs warning-only

## Monitoring

- Freshness SLO:
- Query latency SLO for semantic layer:
- Incident channel:
- Runbook:
