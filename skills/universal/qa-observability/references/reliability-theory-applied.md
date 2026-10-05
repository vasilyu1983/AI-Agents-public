# Reliability Theory Applied to Observability

The reliability math (MTBF/MTTR, availability formulas, hazard functions, fault trees, FMEA, redundancy, error budgets) lives in [`foundations-reliability-theory`](../../foundations-reliability-theory/SKILL.md). Check its [When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) section first. Burn-rate alerting lives in the [canonical multi-window burn-rate table](slo-design-guide.md#canonical-multi-window-burn-rate-table). This file keeps only the observability-specific rules.

## Rules that are specific to telemetry

| Question | Rule | Primitive |
|---|---|---|
| How do we measure MTTR? | Measure from **occurrence** (first bad SLI sample), not from detection or acknowledgement. Store `started_at`, `detected_at`, `mitigated_at` and `resolved_at` separately, so time to detect and time to mitigate can be tracked apart. MTTR measured from the page hides detection lag. | [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| Which burn-rate windows? | Use the canonical table: 14.4× 1h/5m page, 6× 6h/30m page, 1× 3d/6h ticket. Each short window uses the *same* burn rate as its long window. | [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| Why not `1h > 14.4 AND 6h > 6`? | At a sustained 14.4× burn from a clean history, the 6h ratio reaches 6× only after 6h × 6 / 14.4 = 2.5h. The page arrives ~2.5h after onset instead of within minutes. | same |
| How fast does a single long-window ticket fire? | Time to cross = window × threshold / burn. Example: 2% errors on a 99.9% SLO = 20× burn; `3d > 1.5` crosses after 72h × 1.5 / 20 = 5.4h, plus any `for:`. Do the arithmetic before writing a "fires within N hours" acceptance criterion. | same |
| Should detectors be AND-ed or OR-ed? | AND lowers false positives but multiplies misses. With independent detectors that each catch 85% and 70% of real events, AND catches 0.85 × 0.70 = 59.5% (misses 40.5%); OR misses only 0.15 × 0.30 = 4.5%. The Workbook's long/short pairs are not independent detectors: the short window only confirms the burn is current. | [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| What should page? | The fault tree's **top event** (the SLO burn), not intermediate events. Keep component alerts as context and inhibit them in Alertmanager while the top-event alert fires. | [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) |
| What is missing from our instrumentation? | Run FMEA over failure modes and score **detection** from telemetry that exists today. High severity × low detectability = the next instrumentation work item. | [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| Why is the first hour after a deploy different? | Early-life (infant mortality) failure rates are higher. Watch new versions with a canary comparison against the old version rather than lowering global thresholds. | [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) |

## Related

- [alerting-strategies.md](alerting-strategies.md): burn-rate PromQL and why `sum by (service)` is required
- [`assets/monitoring/slo/prometheus-alert-rules.yaml`](../assets/monitoring/slo/prometheus-alert-rules.yaml) and its `promtool` test
- [queueing-theory-applied.md](queueing-theory-applied.md), [control-theory-applied.md](control-theory-applied.md), [information-theory-applied.md](information-theory-applied.md)
