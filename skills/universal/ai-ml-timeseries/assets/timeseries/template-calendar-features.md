# Calendar Feature Template

Use this for known-future calendar and event drivers.

```yaml
calendar_features:
  timezone: "UTC"
  base_features:
    - "day_of_week"
    - "day_of_month"
    - "month"
    - "quarter"
    - "is_weekend"
    - "iso_week"
  holiday_calendar: "replace_me"
  event_flags:
    - "black_friday"
    - "cyber_monday"
    - "end_of_quarter"
  future_known_covariates: true
  future_unknown_covariates: []
```

Checklist:

- [ ] Timezone aligned
- [ ] Event features region-specific
- [ ] Only known-future events projected into the horizon
