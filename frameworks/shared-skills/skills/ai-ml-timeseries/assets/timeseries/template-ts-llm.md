# TS Foundation Model Template

Use this for zero-shot or covariate-aware TSFM benchmarks.

```yaml
tsfm_benchmark:
  model_name: "replace_me" # chronos | timesfm | other
  benchmark_mode: "zero_shot" # zero_shot | covariate_aware | adapted
  series_id_col: "unique_id"
  time_col: "ds"
  target_col: "y"
  frequency: "D"
  context_length: 256
  horizon: 28
  covariates:
    enabled: false
    known_future_covariates: []
  baselines:
    - "seasonal_naive"
    - "global_boosting"
  evaluation:
    point_metrics:
      - "mae"
      - "wape"
      - "mase"
    probabilistic_metrics: []
    slices:
      - "series_family"
      - "volume_band"
  runtime:
    batch_size: 32
    latency_budget_ms: 500
```

Checklist:

- [ ] Seasonal-naive baseline included
- [ ] No leakage
- [ ] Horizon-wise metrics reported
- [ ] Covariate support verified against current docs if used
- [ ] Compared against at least one strong non-TSFM model
