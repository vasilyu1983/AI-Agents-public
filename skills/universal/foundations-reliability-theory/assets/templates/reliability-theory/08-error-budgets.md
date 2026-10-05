# Primitive: Error Budgets

## Definition

An **error budget** is the maximum allowable unreliability in a given window, derived from an SLO. It converts an availability or latency target into an amount of "badness" that can be spent on failures, deployments, and experiments before breaching the SLO.

```
Error budget = 1 - SLO target
Budget (minutes) = (1 - SLO) × window_minutes   # window is a parameter
```

**Example**: 99.9% SLO → error budget = 0.001 × window_minutes: **40.3 min** over a 28-day window (40,320 min), **43.2 min** over 30 days (43,200 min), **43.8 min** per average calendar month (43,800 min = 8,760 h / 12).

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
| Measurement window | A four-week rolling window is the SRE Workbook's "good general-purpose interval" (implementing-slos); rolling 30 days is common; quarterly for planning |
| Good/bad event definition | What counts as a "bad" request or event against the SLO |
| Consumption tracking | Actual reliability data over the window |

## Outputs

- Error budget remaining (absolute time or request count).
- Burn rate: how fast the budget is being consumed vs. the steady-state rate.
- Alert thresholds: multiwindow burn-rate pages and tickets (see below); budget exhaustion → release policy (e.g. freeze) per the agreed error-budget policy.
- Budget exhaustion date projection at current burn rate.

## Error Budget Arithmetic

### Availability-Based

```
Window:      30 days = 43,200 minutes
SLO:         99.95%
Budget:      0.0005 × 43,200 = 21.6 minutes downtime per 30 days
Consumed:    12 minutes (from incidents)
Remaining:   9.6 minutes  (44% of budget left)
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

Burn rate = observed error rate / (1 − SLO). A burn rate of 1 spends exactly the whole budget over the period. The Workbook's formula: **budget consumed = burn rate × alerting window / period** (its examples use a 30-day period).

SRE Workbook ch. 5 "Alerting on SLOs", Table 5-8 (recommended parameters for a 99.9% SLO; https://sre.google/workbook/alerting-on-slos/):

| Severity | Long window | Short window | Burn rate | Budget consumed |
|----------|-------------|--------------|-----------|-----------------|
| Page | 1 h | 5 min | 14.4 | 2% |
| Page | 6 h | 30 min | 6 | 5% |
| Ticket | 3 d | 6 h | 1 | 10% |

Fire only when **both** the long and the short window exceed the burn rate: the long window gives significance, the short window makes the alert reset quickly once the burn stops. Re-derivation on a 720 h period: 0.02 × 720 / 1 = 14.4; 0.05 × 720 / 6 = 6; 0.10 × 720 / 72 = 1. At 14.4× a 30-day budget is gone in 720 / 14.4 = 50 h.

Low traffic: at a few hundred requests per hour a single failure can exceed 14.4×. The Workbook's remedies are synthetic traffic, aggregating small services into one monitored group, product changes so one failure costs less, or reconsidering whether one failure's budget impact reflects user impact. A minimum-event gate on the alert expression is a common implementation of the same idea. Alert implementation (recording rules, routing) is owned by [qa-observability `slo-design-guide.md`](../../../../qa-observability/references/slo-design-guide.md).

## Measurement Limits (decide before trusting the arithmetic)

- **Request-based vs time-based SLI.** Request-based (good events / total events) makes the budget scale with traffic. Time-based (good slices / total slices, a slice is "good" if its error rate is under a threshold) weights a quiet 3 a.m. minute the same as peak and hides partial outages that stay under the slice threshold. Do not compare budgets across the two definitions.
- **Low traffic is a statistics problem.** With n events and 0 failures, a one-sided 95% upper bound on the error rate is 1 − 0.05^(1/n) ≈ 3/n. Showing an error rate at or below 0.1% with zero failures needs n ≥ ln 0.05 / ln 0.999 ≈ 2,995 events. Below that, one failure is noise against a 99.9% SLO: gate alerts on a minimum event count or use the remedies above. Interval machinery: [decision-and-validation.md](../../../references/decision-and-validation.md).
- **Latency SLIs are proportions, not percentiles.** The Workbook defines latency SLIs as "the proportion of requests that were faster than some threshold" (https://sre.google/workbook/implementing-slos/). Percentiles cannot be averaged across instances or windows, and the p99 of a call chain is not the sum of per-hop p99s. Compose from histograms or good-event counts. Fan-out amplifies tails: if each of N parallel backends is slow with probability p, the request is slow with probability 1 − (1 − p)^N (p = 1%, N = 100 → 63%).
- **Dependency rule.** "If a single component is a critical dependency for a particularly high-value interaction, its reliability guarantee should be at least as high as the reliability guarantee of the dependent action" (Workbook, implementing-slos). Allocation across series dependencies: primitive 11.

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Measuring burn weekly when traffic is bursty | Weekly aggregation hides multi-hour exhaustion events; paging is late | Use Table 5-8: 1 h/5 min and 6 h/30 min pages, 3 d/6 h ticket |
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

March budget:    0.005 × 44,640 (31 days) = 223.2 minutes
Remaining:       223.2 - 15.5 = 207.7 minutes  (93.1% remaining)
```

Budget is healthy. The team can safely run 3 more risky deploys (each historically consuming ~5 minutes) and the planned infrastructure migration (~60 minutes estimated risk). A slow memory leak consuming 10 minutes/day is a burn rate of only 10 × 31 / 223.2 ≈ 1.4: neither page (14.4 or 6) fires. Only the 3 d/6 h burn-rate-1 ticket catches it: the 3-day window reaches burn 1 after about 72 / 1.39 ≈ 52 h, when ≈21.6 minutes (≈10% of budget) are spent. Slow leaks are ticket work, not pages.

## Calibration Note: GenAI / LLM Services

As reported in [Yan et al., arXiv:2504.08865v2](https://arxiv.org/html/2504.08865v2), Sections VI-A/B/C give Microsoft-specific root-cause shares: infrastructure 27.2%, configuration 24.5%, code bugs 21.5%. Sections VII-E and VIII-A show ad-hoc fixes were **less common** for GenAI (22.4%) than non-GenAI (54.7%). IV-A, Table I gives monitor-detected false-positive alarms of 11.0% vs 3.8%. These are study-specific incident/monitor proportions, not error-budget burn rates.

Check local recovery and monitor precision; choose burn alerts from the good-event SLI, SLO, window and response needs. False alarms do not themselves consume the SLO budget. This comparison supplies no universal threshold adjustment or proof that transferred runbooks cause longer recovery.

## Sources

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4.
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 5 (Alerting on SLOs — multi-window, multi-burn-rate alerting).
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley. (Foundational availability arithmetic underlying SLO maths.)
- Yan, H. et al. (2025). An Empirical Study of Production Incidents in Generative AI Cloud Services. ISSRE 2025. arXiv:2504.08865.
