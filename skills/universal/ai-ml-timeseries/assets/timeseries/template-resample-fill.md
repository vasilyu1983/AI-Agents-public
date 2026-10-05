# Resample and Fill Template

Use this when normalizing timestamp frequency and gap handling.

```yaml
resample_fill:
  frequency: "D"
  aggregation_method: "sum" # sum | mean | max | min | count | custom
  timezone: "UTC"
  duplicate_policy: "aggregate"
  missing_timestamp_policy: "explicit_gap_table"
  target_fill: "leave_missing" # leave_missing | zero | forward_fill | seasonal_interpolate
  covariate_fill:
    known_future_covariates: "forward_fill"
    future_unknown_covariates: "do_not_fill_into_future"
  drop_threshold: 0.2
```

Checklist:

- [ ] Frequency justified by business need
- [ ] Missing timestamp policy explicit
- [ ] No leakage introduced by fill rules
- [ ] Rolling window alignment validated after resampling
