# Backtesting Template

Use this as the evaluation contract for a forecasting run.

```yaml
backtest:
  dataset_id: "replace_me"
  series_id_col: "unique_id"
  time_col: "ds"
  target_col: "y"
  frequency: "D"
  horizon: 28
  window_type: "rolling_origin" # rolling_origin | expanding | rolling
  step_size: 7
  min_train_points: 180
  n_windows: 5
  cutoff_policy: "features and labels must use data available up to each cutoff_timestamp only"
  known_future_covariates: []
  baselines:
    - "naive"
    - "seasonal_naive"
  metrics:
    point:
      - "mae"
      - "wape"
      - "mase"
    probabilistic: []
    business: []
  reporting_slices:
    - "series_family"
    - "volume_band"
  output_fields:
    - "cutoff_timestamp"
    - "forecast_timestamp"
    - "horizon"
    - "y_true"
    - "y_pred"
    - "model_version"
```

Checklist:

- [ ] Temporal ordering preserved
- [ ] Cutoff timestamp explicit
- [ ] Multiple windows tested
- [ ] Baselines included
- [ ] Horizon-specific error analyzed
