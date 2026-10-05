# Forecast Model Template

Use this to define the forecast package, not just the estimator.

```yaml
forecast_model:
  name: "replace_me"
  family: "global_boosting" # local_classical | global_boosting | deep_sequence | tsfm | hierarchical
  model_class: "LGBMRegressor"
  version: "v0.1.0"
  target:
    series_id_col: "unique_id"
    time_col: "ds"
    target_col: "y"
    frequency: "D"
  horizon: 28
  forecast_mode: "point" # point | quantile | distribution
  covariates:
    static_features: []
    known_future_covariates: []
    future_unknown_covariates: []
  training_window:
    start: "YYYY-MM-DD"
    end: "YYYY-MM-DD"
    cutoff_policy: "train rows available up to cutoff_timestamp only"
  validation:
    scheme: "rolling_origin"
    windows: 5
    primary_metric: "mase"
  baselines:
    - "naive"
    - "seasonal_naive"
  outputs:
    model_artifact: "path/to/model"
    metrics_report: "path/to/report"
    forecast_table: "path/to/predictions"
    feature_importance: true
  fallback:
    strategy: "seasonal_naive"
    trigger: "model failure or invalid forecast"
```

Checklist:

- [ ] Baseline compared
- [ ] Known-future covariates documented
- [ ] No leakage
- [ ] Validation horizon matches deployment horizon
- [ ] Fallback defined
