# Information Theory Applied to Observability

This is a pointer, not a method library. The formulas, estimators and their limits live in [foundations-information-theory](../../foundations-information-theory/SKILL.md#when-to-apply). Use that skill only when a defined telemetry decision needs distribution, dependence or compression analysis. For initial instrumentation and ordinary SLO alerting, use this skill's direct references instead.

Before any analysis changes collection, write down: the incident and diagnosis tasks, the loss per event class, privacy and forensic retention requirements, the budget, and a rollback owner.

## Where each telemetry question goes

| Telemetry question | Primitive (foundations template) | Applied owner in this skill |
|---|---|---|
| Is this log stream concentrated or noisy? | [Shannon entropy](../../foundations-information-theory/assets/templates/information-theory/01-shannon-entropy.md) | [log aggregation](log-aggregation-patterns.md) |
| Does this alert rule carry information about incidents? | [Mutual information](../../foundations-information-theory/assets/templates/information-theory/02-mutual-information.md) | [alerting strategies](alerting-strategies.md) |
| Has the latency distribution drifted? | [KL divergence](../../foundations-information-theory/assets/templates/information-theory/03-kl-divergence.md) | [alerting strategies](alerting-strategies.md) |
| How should a trace budget be split across services? | [Rate-distortion](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md) | [sampling strategies](sampling-strategies.md) |
| Can logs be compacted into structured summaries? | [Information bottleneck](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md), [MDL](../../foundations-information-theory/assets/templates/information-theory/07-mdl-principle.md) | [log aggregation](log-aggregation-patterns.md) |

## Telemetry traps to check first

- **Low entropy is not safe deletion.** A stream of normal records with one critical forensic event has low entropy. Test removal against held-out diagnosis tasks and retention duties.
- **Low mutual information does not license silencing a rule.** Rare useful rules score low because incidents are rare. Estimate from windows that include non-firing periods, and compare precision, severity recall and detection delay.
- **KL on Prometheus classic histograms needs disjoint counts.** `le` buckets are cumulative: difference adjacent buckets, keep the terminal bucket, and normalize once. Zero baseline mass gives infinite KL, so disclose any smoothing. Keep SLO burn-rate alerts alongside any drift warning.
- **Information bits are not storage cost.** Measure bytes, unique values and query cost directly.
- **Dependence is not causation.** MI, correlation or lag screen candidates; a causal claim needs an intervention.

## Sources

Implementation settings must be checked against current primary docs before deployment: the [OpenTelemetry tail sampling processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor) and [Prometheus histograms](https://prometheus.io/docs/practices/histograms/).
