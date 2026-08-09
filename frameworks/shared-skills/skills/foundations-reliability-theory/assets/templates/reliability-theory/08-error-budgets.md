# Primitive: Error Budgets

## Definition

An **error budget** is the maximum allowable unreliability in a given window, derived from an SLO. It converts an availability or latency target into an amount of "badness" that can be spent on failures, deployments, and experiments before breaching the SLO.

```
Error budget = 1 - SLO target
Annual error budget = (1 - SLO) × window_duration
```

**Example**: 99.9% monthly SLO → error budget = 0.001 × 43,800 min/month = **43.8 minutes/month**.

The error budget creates a single number that aligns development speed (spend budget on deploys) with operational stability (preserve budget for users). When the budget is exhausted, releases pause until it replenishes.

## When to Use

- Setting service-level objectives and their corresponding tolerance for failures.
- Deciding whether to prioritise feature work or reliability work (budget state drives the decision).
- Negotiating between product and SRE/ops on acceptable deployment risk.
- Measuring reliability improvement over time: does the budget trend toward being spent, preserved, or frequently exhausted?
- Triggering freeze policies and post-incident reviews (budget exhaustion is the threshold).

## Inputs

| Input | Description |
|-------|-------------|
| SLO target | e.g. 99.9% availability, p99 latency ≤ 200ms |
| Measurement window | Rolling 30 days is standard; can be quarterly |
| Good/bad event definition | What counts as a "bad" request or event against the SLO |
| Consumption tracking | Actual reliability data over the window |

## Outputs

- Error budget remaining (absolute time or request count).
- Burn rate: how fast the budget is being consumed vs. the steady-state rate.
- Alert thresholds: 2% window remaining at current burn rate → deploy freeze.
- Budget exhaustion date projection at current burn rate.

## Error Budget Arithmetic

### Availability-Based

```
Window:      30 days = 43,800 minutes
SLO:         99.95%
Budget:      0.0005 × 43,800 = 21.9 minutes downtime/month
Consumed:    12 minutes (from incidents)
Remaining:   9.9 minutes  (45% of budget left)
```

### Request-Rate-Based

```
Total requests this period:   10,000,000
SLO:                          99.9% success rate
Budget:                       0.001 × 10,000,000 = 10,000 errors
Errors observed:              6,200
Remaining:                    3,800 errors  (38% of budget)
```

### Multi-Window Burn Rate (SRE Workbook approach)

Fast burn detection: if the 1-hour burn rate would exhaust the monthly budget in less than 72 hours, page immediately.

```
Fast burn threshold = monthly_budget / 72h  × 1h   → if consumed > threshold, page
Slow burn threshold = monthly_budget / 336h × 6h   → if consumed > threshold, ticket
```

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Measuring burn weekly when traffic is bursty | Weekly aggregation hides multi-hour exhaustion events; paging is late | Use multi-window burn rate: 1-hour and 6-hour windows alongside the monthly window |
| SLO set to match current measured reliability | Error budget is always near-full; teams get no reliability signal | Set SLO to the level customers actually need, not the level you currently achieve |
| Including maintenance windows in availability SLO denominator | Artificially inflates availability numerator; budget appears larger | Exclude planned maintenance from both numerator and denominator, or use a separate maintenance SLO |
| Error budget shared across unrelated services | Budget exhausted by one service silences another service's deploys | Maintain per-service budgets; never pool across independent services |
| Treating error budget exhaustion as a failure | Teams game the SLO to avoid consequences | Treat exhaustion as a signal for reliability investment, not a punishable event |

## Worked Example

A streaming API has a 99.5% monthly availability SLO. In March, two incidents occurred:

```
Incident 1: 8-minute outage (deploy gone wrong)
Incident 2: 15-minute degradation at 50% error rate → 7.5 effective minutes
Total consumed: 8 + 7.5 = 15.5 minutes

March budget:    0.005 × 43,800 = 219 minutes
Remaining:       219 - 15.5 = 203.5 minutes  (92.9% remaining)
```

Budget is healthy. The team can safely run 3 more risky deploys (each historically consuming ~5 minutes) and the planned infrastructure migration (~60 minutes estimated risk). If burn rate suddenly spikes — e.g., a slow memory leak consuming 10 minutes/day — the 1-hour multi-window alert triggers before the monthly budget is threatened.

## Calibration Note: GenAI / LLM Services

Burn-rate alerting thresholds calibrated on non-GenAI incident profiles underestimate true budget consumption for GenAI cloud services. Empirical analysis of Microsoft's GenAI cloud incidents (Yan et al. 2025, ISSRE) shows:

- **Root cause distribution differs**: GenAI incidents — infrastructure 27.2%, configuration 24.5%, code bugs 21.5% — diverge from classical SRE profiles where code bugs typically dominate.
- **Ad-hoc fixes are more common**: 22.4% of GenAI incident resolutions vs. 54.7% for traditional services, meaning existing runbooks transfer poorly and MTTR is structurally longer.
- **Monitor false-alarm rate is elevated**: 11.0% vs. 3.8%, which can exhaust alert-handling capacity and mask real budget consumption.

When operating a GenAI service, re-calibrate burn-rate alert thresholds from your own incident history rather than inheriting non-GenAI baselines. The multi-window approach (primitive 08) remains the right structure; the threshold values require re-fitting.

## Sources

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4.
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 5 (Alerting on SLOs — multi-window, multi-burn-rate alerting).
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley. (Foundational availability arithmetic underlying SLO maths.)
- Yan, H. et al. (2025). An Empirical Study of Production Incidents in Generative AI Cloud Services. ISSRE 2025. arXiv:2504.08865.
