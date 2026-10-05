# Primitive: MTBF and MTTR

## Definition

**Mean Time Between Failures (MTBF)** here means average operating (up) time between failures in a repairable system, excluding downtime. If a source uses elapsed failure-to-failure cycle time instead, do not add MTTR again in the availability denominator. **Mean Time To Repair (MTTR)** is the average time to restore the system to full operation after a failure.

MTBF measures how often a system fails. MTTR measures how quickly it recovers. Together they are the two levers for improving availability.

## When to Use

- Sizing maintenance schedules and spare-part inventories.
- Comparing two system designs before purchase or build.
- Computing availability targets (feeds directly into primitive 02).
- Setting SLOs and error budgets (feeds into primitive 08).
- Post-incident analysis when you need to track whether reliability trends are improving.

## Inputs

| Input | Description |
|-------|-------------|
| Total operating time | Sum of all up-time hours in the observation window |
| Number of failures | Count of distinct failure events in the same window |
| Total downtime | Sum of all repair durations in the window |

## Outputs

```
MTBF = Total operating time / Number of failures
MTTR = Total downtime / Number of failures
```

**Units**: hours, minutes, or any consistent time unit. The ratio matters — do not mix units.

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Counting planned maintenance as unplanned failure | Extra counted events lower estimated MTBF and change its meaning | Separate event classes and state which downtime the SLI includes |
| Measuring MTTR from detection, not from occurrence | MTTR understates true repair burden; hides detection lag | Record failure occurrence time separately from alert time |
| Using a window too short for rare failures | Single event dominates estimate; high variance | Choose observation time from desired rate precision and confidence; report sparse/zero-failure uncertainty |
| Treating MTBF as exponentially distributed when it is not | Calculations that assume constant hazard rate become invalid | Validate distribution shape before applying exponential formulas (see primitive 03) |
| Arithmetic average of MTBF values across parallel subsystems | Incorrect — parallel availability is not the average of series availabilities | Use the composition formulas in primitive 10 |

## Worked Example

A payment gateway accumulated 8,760 operating hours and had 12 incidents. Total downtime summed to 6 hours.

```
MTBF = 8,760 / 12 = 730 hours  (~30 days between failures)
MTTR = 6 / 12 = 0.5 hours  (30 minutes to restore)

Availability = MTBF / (MTBF + MTTR) = 730 / 730.5 ≈ 0.99932  (99.93%)
```

This observed time-based availability exceeds a 99.9% target under the stated downtime definition. Remaining error budget depends on the actual SLI and window (primitive 08); the mean is not a guarantee that a planned change stays within budget.

## Domain Caveats

**LLM / GenAI cloud services — re-calibrate baselines before applying standard MTTR targets.**
As reported in [Yan et al. v2, VIII-A](https://arxiv.org/html/2504.08865v2#S8.SS1), normalized **average** TTM is 1.12 vs. 0.65 in Microsoft incidents; their rounded ratio is ≈1.72. VIII-B separately states 1.83×, an unresolved internal discrepancy; unrounded data are unavailable. These are neither medians nor a controlled comparison of equivalent incidents. Table I's monitor false-positive proportions, 11.0% vs 3.8%, concern monitor-detected tickets. Re-measure local recovery and detection.

**LLM agent systems — MTBF alone is insufficient; use a three-axis reliability model.**
Single-run success rate masks substantial reliability gaps in agent architectures. ReliabilityBench (Gupta 2026) demonstrates that perturbations drop success from 96.9% to 88.1% at perturbation intensity ε=0.2, and API-level faults (rate limiting, timeouts) produce further degradation that MTBF averaging conceals. For LLM agent systems, extend MTBF analysis with three axes:
1. **Consistency** — all-k consistency at a declared k, with independent repeated task groups and per-run intervals.
2. **Robustness** — performance degradation across semantically equivalent task variants (ε=0.1–0.3).
3. **Fault tolerance** — per-failure-type impact (timeout, rate limit, schema drift).
(Gupta, A. 2026. arXiv:2601.06112.)

**Finite benchmark evaluation — adaptive sampling can improve query efficiency.**
[Wu, Nair & Candès (2026), abstract and §4](https://arxiv.org/html/2601.20251v1), report up to 5× effective sample size: the same interval width as uniform sampling with fewer queries. This is not a 3–5× reduction in interval width. FAQ uses historical benchmark outcomes and finite-population inference; validate those conditions before using it, and do not extrapolate its query savings to sparse operational failures.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapter 4.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- Yan, H. et al. (2025). An Empirical Study of Production Incidents in Generative AI Cloud Services. ISSRE 2025. arXiv:2504.08865.
- Gupta, A. (2026). ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions. arXiv:2601.06112.
- Wu, S., Nair, Y., & Candès, E. J. (2026). Efficient Evaluation of LLM Performance with Statistical Guarantees. arXiv:2601.20251.
