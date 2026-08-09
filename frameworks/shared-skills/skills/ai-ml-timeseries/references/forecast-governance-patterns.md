# Forecast Governance Patterns

Forecasting-specific handoff and governance patterns that sit between modelling and full MLOps.

Use this when a forecast needs to be operationally trustworthy, even if the user is not asking for a full deployment architecture.

## Required Forecast Contract

Every forecast package should record:

- forecast target and unit
- forecast horizon and cadence
- cutoff timestamp policy
- series scope and segmentation rules
- known-future covariates used
- metric definitions
- baseline comparison
- fallback rule
- model and feature lineage

If any of these are missing, the forecast is not decision-complete.

## Cutoff Timestamp Pattern

For each forecast run, store:

- `cutoff_timestamp`
- `forecast_created_at`
- `prediction_horizon`
- `data_through_timestamp`

This makes leakage reviews and incident analysis possible later.

## Fallback Pattern

Define a degraded mode before production handoff:

- naive or seasonal-naive fallback
- last-known-good model
- explicit "insufficient data" response when the history window is too short

Document when each fallback activates and how it is surfaced to downstream users.

## Forecast Lineage Pattern

Track the minimum lineage set:

- model version
- feature version
- training data window
- calibration or conformalization window
- code or pipeline version
- source data snapshot or extract timestamp

This is enough for most forecast debugging and model review tasks.

## Review Questions Before Handoff

Ask:

1. What was known at the cutoff?
2. Which covariates were assumed to be known in the future?
3. Which baseline did the model beat, and by how much?
4. Where does the model fail by horizon or segment?
5. What fallback is used when the model or data path fails?

## Checklist

- [ ] Forecast contract documented
- [ ] Cutoff timestamp recorded
- [ ] Known-future covariates documented
- [ ] Baseline comparison attached
- [ ] Horizon and slice failures summarized
- [ ] Fallback path defined
- [ ] Lineage metadata recorded
- [ ] Escalation to full MLOps identified if needed
