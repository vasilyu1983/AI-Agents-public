# Incident Metrics Guide

Use metrics to improve response quality, not to punish responders.

## Core Metrics

- `MTTD`: issue starts to confirmed detection.
- `MTTA`: alert to first responder action.
- `MTTM`: acknowledgement to user-impact mitigation.
- `MTTR`: issue start to full recovery.
- Postmortem completion rate.
- Action-item closure rate.

## MTTx Distributional Caveat (May 2026)

The "M" (mean) in MTTD/MTTA/MTTM/MTTR is statistically misleading. Incident durations follow power-law or heavy-tailed distributions: a handful of multi-hour SEV1s will dominate the mean while the median remains low. Štěpán Davidovič's "Incident Metrics in SRE" (Google SRE / O'Reilly) states that MTTR and MTTM are "poorly suited for decision making or trend analysis in the context of production incidents."

**Do not delete the MTTx metrics** — they remain useful as shorthand labels for the four phases. Do not use their *means* alone for trend analysis or team comparison.

### Preferred Alternatives

| Instead of | Use |
|------------|-----|
| Mean MTTR for trend analysis | p50 / p90 / p99 of incident duration, broken out by severity and service |
| Mean MTTM for SLO breach comparison | Incident frequency / rate (incidents per week by severity class) alongside duration percentiles |
| Company-wide MTTR average | Per-service, per-severity percentile cohorts |

Percentile-based analysis reveals whether slow outliers are improving, which the mean obscures entirely.

**Reference**: Davidovič, Štěpán. "Incident Metrics in SRE." Google SRE / O'Reilly. https://sre.google/resources/practices-and-processes/incident-metrics-in-sre/

## Interpretation Rules

- Break metrics down by severity and service, not only by company average.
- Report p50/p90/p99 alongside (or instead of) means for duration metrics.
- Pair speed metrics with quality metrics such as reopen rate and repeated incident class.
- Investigate step changes after alerting, deployment, or org changes.
- Treat incident frequency/rate as a leading indicator; duration percentiles as a lagging one.
