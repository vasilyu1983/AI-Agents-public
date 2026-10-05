# Lag and Rolling Feature Template

Use this when specifying leakage-safe temporal features.

```yaml
feature_spec:
  series_id_col: "unique_id"
  time_col: "ds"
  target_col: "y"
  lags:
    - 1
    - 7
    - 14
    - 28
  seasonal_lags:
    - 7
    - 28
  rolling_features:
    - name: "rolling_mean_7"
      source: "y"
      shift: 1
      window: 7
      agg: "mean"
    - name: "rolling_std_28"
      source: "y"
      shift: 1
      window: 28
      agg: "std"
  ewm_features:
    - name: "ewm_mean_28"
      source: "y"
      shift: 1
      span: 28
  calendar_features:
    - "day_of_week"
    - "month"
    - "quarter"
  leakage_checks:
    group_by_series: true
    shift_target_before_rollup: true
    known_future_covariates_only_at_horizon: true
```

Checklist:

- [ ] Lags reference past timestamps only
- [ ] Rolling windows are computed after a shift
- [ ] Features grouped by series
- [ ] Seasonal lags added when needed
