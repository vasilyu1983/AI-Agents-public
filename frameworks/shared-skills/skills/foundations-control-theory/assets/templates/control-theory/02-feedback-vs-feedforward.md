# Mechanism: Feedback vs. Feedforward Control

**Sources**: Åström & Murray, *Feedback Systems* Ch. 1-2 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 1 (2019).

## Definition

Two fundamental control architectures for driving a system toward a target:

**Feedback (closed-loop)**: Measures the output, computes the error, and applies a corrective signal. Reacts to disturbances *after* they appear in the measurement.

```
Setpoint → [Controller] → [Plant] → Output
                ↑                      |
                └──── Measurement ─────┘
```

**Feedforward (open-loop)**: Uses a model of the disturbance or plant to compute the corrective signal *before* the error appears in the measurement.

```
Known disturbance → [Feedforward model] → [Summing junction] → [Plant] → Output
                                                  ↑
                    Setpoint → [Feedback controller] (optional)
```

**Combined**: Feedforward handles known, predictable disturbances. Feedback corrects residual model error.

## When to Use

| Pattern | Use Feedback | Use Feedforward | Use Both |
|---------|-------------|----------------|---------|
| Disturbance is measurable and predictable | — | Yes | — |
| Disturbance is unpredictable or unmeasured | Yes | — | — |
| Plant model is accurate | — | Yes | — |
| Model has significant uncertainty | Yes | — | — |
| Need fast response to known inputs | — | Yes | — |
| Need steady-state accuracy despite model error | Yes | — | Yes |

Practical examples:
- **Budget pacing**: Feedforward = schedule-aware bid adjustment (predict low-traffic hours). Feedback = error correction when spend drifts from target.
- **Autoscaling**: Feedforward = time-of-day warm-up. Feedback = CPU/latency error correction.
- **Agent loop**: Feedforward = token budget pre-allocation per step. Feedback = overspend correction.

## Inputs

| Input | Feedback | Feedforward |
|-------|----------|-------------|
| Output measurement | Required | Not required |
| Disturbance measurement | Not required | Required |
| Plant model | Optional (improves gains) | Required |
| Setpoint | Required | Required |

## Outputs

Both architectures produce a control signal `u(t)`. In combined systems:

```
u(t) = u_feedback(t) + u_feedforward(t)
```

## Failure Modes

| Failure | Architecture | Fix |
|---------|-------------|-----|
| Slow disturbance rejection | Feedback only | Add feedforward for measurable disturbances |
| Sensitivity to model error | Feedforward only | Add feedback loop to correct residual error |
| Oscillation | Feedback with high gain | Tune gains; add derivative term |
| Over-correction on predictable patterns | Feedback without feedforward | Add feedforward; reduce feedback gain |
| Model drift over time | Feedforward-heavy | Add feedback to maintain setpoint tracking |

## Worked Example: Budget Pacing

**Context**: Daily ad budget $1000; historical data shows 40% of traffic arrives between 8am–12pm.

Feedforward: At midnight, pre-allocate bid multiplier schedule:
```
8am–12pm: spend_rate = 0.40 × (budget/day_length) × 2.5
12pm–8pm: spend_rate = 0.45 × (budget/day_length) × 1.33
8pm–12am: spend_rate = 0.15 × (budget/day_length) × 0.75
```

Feedback: Every 15 minutes, check actual vs. planned cumulative spend:
```
e = planned_spend − actual_spend
if e > 0: increase bid multiplier proportionally
if e < 0: decrease bid multiplier proportionally
```

Combined: The feedforward handles the predictable daily pattern; the feedback corrects for unexpected traffic spikes or drops.

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 1-2. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 1.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 1-3.
