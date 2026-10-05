# Control Theory Applied to Observability

The control math (PID, dead time, Kalman filtering, anti-windup, gain scheduling) lives in [`foundations-control-theory`](../../foundations-control-theory/SKILL.md). Check its [When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) section first; it also covers deciding what to measure before choosing controller gains. This file keeps only the alerting rules.

## Rules that are specific to alerting

| Question | Rule | Primitive |
|---|---|---|
| The alert flaps around its threshold. | Add hysteresis. In Prometheus, `for:` delays firing and `keep_firing_for:` keeps an alert firing for a set time after the condition was last met ([alerting rules docs](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)). Alertmanager `resolve_timeout` does not do this; it only applies to alerts that arrive without an end time. For burn-rate alerts, the short window already gives a fast, clean reset. | [01-pid-control](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md) |
| We want earlier warning on fast ramps. | Rate of change is noisy. Smooth before differentiating (`deriv()` fits a least-squares slope over a range; use it on a subquery of a `rate()`), and treat it as a ticket-level early signal. The 14.4× 1h/5m tier is usually early enough to page. | same |
| How long after the event does the page arrive? | Measure pipeline dead time end to end with a synthetic error injection: SDK export interval, collector batching, scrape interval, rule evaluation interval, `for:`, Alertmanager `group_wait`, and notifier delivery. Record the measured value per environment; do not assume a typical figure. | [07-dead-time-compensation](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md) |
| Several weak signals disagree about health. | A fused health estimate (Kalman-style weighting by signal noise) can serve as a dashboard or triage aid. Do not page on it unless it is validated against labelled incidents; page on the SLO burn. | [06-kalman-filter](../../foundations-control-theory/assets/templates/control-theory/06-kalman-filter.md) |
| A long incident keeps re-paging. | Stop re-notification from accumulating during a known incident: Alertmanager `repeat_interval`, inhibition from the incident's top-event alert, or a silence tied to the incident ticket. | [08-anti-windup](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md) |

## Related

- [alerting-strategies.md](alerting-strategies.md): routing, inhibition, alert tests
- [slo-design-guide.md](slo-design-guide.md#canonical-multi-window-burn-rate-table): canonical burn-rate table
- [reliability-theory-applied.md](reliability-theory-applied.md), [queueing-theory-applied.md](queueing-theory-applied.md), [information-theory-applied.md](information-theory-applied.md)
