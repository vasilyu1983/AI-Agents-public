# SLO Error-Budget Burn Rate as Incident Trigger

SLO-based alerting shifts incident triggers from threshold breaches on individual metrics to budget consumption rate — catching problems early whether they are fast (spike) or slow (steady bleed).

## Core Concept: Burn Rate

Burn rate is how fast the error budget is being consumed relative to the window. A burn rate of 1 means the budget is being consumed exactly at the pace that would exhaust it by the end of the SLO window. A burn rate of 10 means it will be gone in 10% of the window.

The Google SRE Workbook identifies "2% budget consumption in one hour, 5% budget consumption in six hours, and 10% budget consumption in three days" as reasonable starting numbers for a 30-day SLO window. Source: https://sre.google/workbook/alerting-on-slos/ (verified 2026-07-11).

## Burn Rate → Severity Mapping

The first three rows below are Google's documented defaults for a 30-day SLO window (burn rate = fraction of budget consumed × window ÷ elapsed time). The fourth row is this skill's own extension, not a Google-sourced number — treat it as a starting hypothesis, not an authority-backed threshold.

| Burn rate window | Budget consumed | Source | Trigger | Suggested severity |
|------------------|----------------|--------|---------|-------------------|
| High: 14.4× over 1 h | 2% in 1 h | Google SRE Workbook | Page immediately | SEV1 |
| High: 6× over 6 h | 5% in 6 h | Google SRE Workbook | Page immediately | SEV2 |
| Medium: 1× over 3 d | 10% in 3 d | Google SRE Workbook | Ticket or Slack alert | SEV3 |
| Low: sustained low-rate burn | Budget on track to exhaust before window ends, at current rate | This skill (unverified default — calibrate locally) | Scheduled review | No page |

These thresholds are starting points, not fixed law. Calibrate against your actual SLO window (many teams use rolling 28-day or 30-day windows — the two are close enough that Google's ratios transfer, but recompute the exact burn-rate multiplier for your window length using `burn_rate = budget_fraction × window_hours / elapsed_hours`) and the cadence at which your service naturally consumes budget in healthy operation.

## Postmortem Prioritization via Error-Budget Remaining

Error-budget remaining at time of incident informs how urgently a postmortem must produce action items:

- **Budget exhausted or < 5% remaining**: postmortem is high-urgency; action items must be scheduled before the next SLO window or freeze non-reliability work.
- **5–20% remaining**: standard postmortem timeline (48-hour draft, 5-business-day publish).
- **> 20% remaining**: lightweight postmortem acceptable; focus on contributing factors rather than full structured review.

## Process Expectations

1. **Declare on budget rate, not just error rate.** A slow error-rate bleed that will exhaust the budget by day 20 of a 28-day window is a SEV2, even if the instantaneous error rate looks low.
2. **Track budget remaining in the incident channel.** Post current budget consumed as part of status updates so the IC can calibrate urgency.
3. **Reset severity if budget crosses a threshold mid-incident.** An incident starting at SEV2 that consumes an additional 3% during response should be escalated to SEV1.
4. **Include budget consumed in the postmortem summary.** The timeline entry at resolution should state total budget consumed during the incident.

## Scope Note

This reference covers the process design for SLO-based triggering. SLI/SLO configuration and monitoring tool setup are out of scope for this skill — see `qa-observability` for that.
