# Time Series Metrics Template

Use this as the metric contract for a forecast evaluation.

```yaml
metric_plan:
  primary_point_metrics:
    - "mae"
    - "wape"
    - "mase"
  optional_point_metrics:
    - "rmse"
    - "smape"
  probabilistic_metrics:
    quantiles:
      - 0.1
      - 0.5
      - 0.9
    scores:
      - "pinball_loss"
      - "coverage"
  business_metrics: []
  report_by:
    horizon: true
    slices:
      - "series_family"
      - "volume_band"
  avoid_as_default:
    - "mape"
```

Checklist:

- [ ] Metrics aligned with the decision objective
- [ ] Horizon-specific results included
- [ ] Slice analysis included where relevant
- [ ] MAPE not used by default on zero-heavy targets
