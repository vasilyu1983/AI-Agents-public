# Primitive: Hazard Functions

## Definition

The **hazard function** h(t), also called the failure rate or hazard rate, describes the instantaneous probability of failure at time t, given survival to time t.

```
h(t) = f(t) / R(t)
```

where f(t) is the failure probability density function and R(t) = 1 - F(t) is the reliability (survival) function.

Three canonical shapes govern most engineering systems:

| Shape | Name | h(t) Behaviour | Typical Cause |
|-------|------|----------------|---------------|
| Constant | Exponential (CFR) | h(t) = λ (flat) | Random external shocks; no wear; memoryless |
| Increasing | IFR — Increasing Failure Rate | h(t) rises with t | Wear-out, fatigue, degradation, ageing |
| Decreasing | DFR — Decreasing Failure Rate | h(t) falls with t | Infant mortality; early defects eliminated by use |

## When to Use

- Choosing the right lifetime distribution before applying MTBF formulas.
- Diagnosing whether a system is still in burn-in, useful-life, or wear-out phase.
- Validating that a constant failure-rate assumption (CFR) is appropriate before using exponential reliability formulas.
- Input to Weibull analysis (primitive 09) which parameterises all three shapes with a single shape parameter β.

## Inputs

| Input | Description |
|-------|-------------|
| Failure time data | Times-to-failure for a sample of units or events |
| Censoring indicators | Which units are still running (right-censored) |
| System phase | Known phase from operations or field history |

## Outputs

- h(t) estimate over time (numerical or plot).
- Classification: CFR / IFR / DFR.
- Recommended distribution family (exponential, Weibull, lognormal).

## Key Relationships

```
Reliability:          R(t) = exp(-∫₀ᵗ h(u) du)
CFR special case:     R(t) = exp(-λt),   MTBF = 1/λ
IFR Weibull (β>1):   h(t) = (β/η)(t/η)^(β-1)  — see primitive 09
DFR Weibull (β<1):   same formula; h(t) decreases when β < 1
```

## Failure Modes of This Primitive

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Assuming CFR without testing | Incorrect MTBF predictions outside useful-life phase | Plot h(t) empirically; test goodness-of-fit before selecting exponential |
| Smoothing over the DFR phase in new deployments | Infant-mortality failures attributed to "steady state"; root cause missed | Separate early (< burn-in threshold) failures from the main dataset |
| Ignoring right-censored data | Survivorship bias; h(t) underestimated | Use Kaplan-Meier or MLE with censoring (see primitive 09) |
| Estimating h(t) from too few failures | High-variance estimates; shape classification unreliable | Use primitive 09 confidence intervals; report uncertainty bounds |
| Conflating the hazard rate with the failure probability | h(t) is a rate (can exceed 1.0 for non-exponential distributions) | Keep units as failures per unit time; do not interpret as a probability directly |

## Worked Example

A cloud VM image is deployed to 500 instances. Failures are recorded over 90 days.

```
Days  0–7:   21 failures → h ≈ 21/(500×7)  = 0.006 failures/instance/day  (DFR — high)
Days  8–60:  18 failures → h ≈ 18/(479×53) ≈ 0.00071 failures/instance/day (CFR — stable)
Days 61–90: 14 failures → h ≈ 14/(461×30) ≈ 0.00101 failures/instance/day (IFR — rising)
```

The shape changes across phases — consistent with a bathtub curve (primitive 04). Applying a single exponential model to the full 90 days would give h ≈ 0.00119, understating early risk and overstating mid-life risk.

**Action**: apply burn-in screening for the first 7 days; re-evaluate hardware at day 60 for wear-out signals.

## Sources

- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- Weibull, W. (1951). A statistical distribution function of wide applicability. *Journal of Applied Mechanics*, 18(3), 293–297.
