# Time Series EDA Template

Use this to structure a forecasting-specific data review.

```yaml
ts_eda:
  dataset_id: "replace_me"
  series_id_col: "unique_id"
  time_col: "ds"
  target_col: "y"
  frequency_candidate: "D"
  summary:
    start_date: "YYYY-MM-DD"
    end_date: "YYYY-MM-DD"
    num_series: 1
  timestamp_checks:
    sorted: true
    duplicates: "count_or_examples"
    missing_timestamps: "count_or_examples"
    timezone_aligned: true
  seasonality_review:
    detected_cycles: []
    trend: "replace_me"
    changepoints: []
  outlier_review:
    method: "rolling"
    flagged_examples: []
  notes:
    data_quality_issues: []
    leakage_risks: []
```

Checklist:

- [ ] Frequency validated
- [ ] Missing timestamps identified
- [ ] Timezone and DST reviewed
- [ ] Seasonality documented
- [ ] Leakage risks noted before modelling
