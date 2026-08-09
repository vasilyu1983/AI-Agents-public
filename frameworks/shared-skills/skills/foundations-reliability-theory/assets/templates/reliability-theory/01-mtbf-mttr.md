# Primitive: MTBF and MTTR

## Definition

**Mean Time Between Failures (MTBF)** is the average elapsed time between one failure and the next in a repairable system. **Mean Time To Repair (MTTR)** is the average time to restore the system to full operation after a failure.

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
| Including planned maintenance downtime in failure count | MTBF appears higher than true failure rate | Separate planned and unplanned stops before computing |
| Measuring MTTR from detection, not from occurrence | MTTR understates true repair burden; hides detection lag | Record failure occurrence time separately from alert time |
| Using a window too short for rare failures | Single event dominates estimate; high variance | Use ≥10× MTBF worth of observation time for stable estimates |
| Treating MTBF as exponentially distributed when it is not | Calculations that assume constant hazard rate become invalid | Validate distribution shape before applying exponential formulas (see primitive 03) |
| Arithmetic average of MTBF values across parallel subsystems | Incorrect — parallel availability is not the average of series availabilities | Use the composition formulas in primitive 10 |

## Worked Example

A payment gateway ran for 8,760 hours (one year) and had 12 incidents. Total downtime summed to 6 hours.

```
MTBF = 8,760 / 12 = 730 hours  (~30 days between failures)
MTTR = 6 / 12 = 0.5 hours  (30 minutes to restore)

Availability = MTBF / (MTBF + MTTR) = 730 / 730.5 ≈ 0.99932  (99.93%)
```

A target of 99.9% (three nines) requires either fewer or shorter failures. The 99.93% figure means there is headroom — the error budget (primitive 08) can absorb planned changes without breaching the SLO.

## Domain Caveats

**LLM / GenAI cloud services — re-calibrate baselines before applying standard MTTR targets.**
Empirical analysis of 4 years of production incidents across Microsoft's GenAI cloud services (ISSRE 2025) found that GenAI incidents take **1.83× longer to mitigate** than equivalent non-GenAI cloud incidents (median TTM 1.12 vs. 0.65 time units). Monitor false-alarm rates are also elevated: **11.0% vs. 3.8%** for traditional services. Do not transfer MTTR baselines or alarm-threshold calibrations from non-GenAI services to LLM-in-the-loop systems without re-measuring from your own incident history. (Yan et al. 2025, arXiv:2504.08865.)

**LLM agent systems — MTBF alone is insufficient; use a three-axis reliability model.**
Single-run success rate masks substantial reliability gaps in agent architectures. ReliabilityBench (Gupta 2026) demonstrates that perturbations drop success from 96.9% to 88.1% at perturbation intensity ε=0.2, and API-level faults (rate limiting, timeouts) produce further degradation that MTBF averaging conceals. For LLM agent systems, extend MTBF analysis with three axes:
1. **Consistency** — pass^k rate across ≥10 repeated identical runs.
2. **Robustness** — performance degradation across semantically equivalent task variants (ε=0.1–0.3).
3. **Fault tolerance** — per-failure-type impact (timeout, rate limit, schema drift).
(Gupta, A. 2026. arXiv:2601.06112.)

**Sparse evaluation data — adaptive sampling can tighten confidence intervals 3–5×.**
When evaluating AI system reliability from benchmark or test runs, confidence intervals on pass-rate estimates can be tightened dramatically using adaptive evaluation designs rather than uniform sampling. Factorized Active Querying (FAQ) achieves up to 5× effective sample size gain while maintaining valid frequentist CI coverage. Apply as an analogue to sparse failure-data problems wherever direct failure observation is expensive. (Wu, Nair & Candès 2026. arXiv:2601.20251.)

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapter 4.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- Yan, H. et al. (2025). An Empirical Study of Production Incidents in Generative AI Cloud Services. ISSRE 2025. arXiv:2504.08865.
- Gupta, A. (2026). ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions. arXiv:2601.06112.
- Wu, S., Nair, Y., & Candès, E. J. (2026). Efficient Evaluation of LLM Performance with Statistical Guarantees. arXiv:2601.20251.
