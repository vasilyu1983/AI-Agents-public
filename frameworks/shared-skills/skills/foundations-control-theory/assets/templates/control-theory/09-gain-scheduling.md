# Mechanism: Gain Scheduling

**Sources**: Åström & Murray, *Feedback Systems* Ch. 11 (2020). Rugh & Shamma (2000), "Research on gain scheduling," Automatica 36(10):1401-1425. Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 9 (2019).

## Definition

**Gain scheduling** extends linear control to nonlinear systems by operating multiple linear controllers — each tuned for a specific operating region — and switching or interpolating between them based on a **scheduling variable** that indicates the current operating condition.

```
Scheduling variable: σ(t) — e.g., load, request rate, time of day, temperature

For each operating point σ_i:
  Design linear controller C_i with gains (Kp_i, Ki_i, Kd_i)
  Valid for σ ∈ [σ_i_low, σ_i_high]

At runtime:
  Observe σ(t)
  Select (or interpolate between) the appropriate controller gains
  Apply selected gains to standard PID/state-feedback structure

Interpolation (smooth scheduling):
  α = (σ − σ_i) / (σ_{i+1} − σ_i)   (linear interpolation weight)
  K(σ) = (1−α)·K_i + α·K_{i+1}
```

## When to Use

- System dynamics change significantly with operating condition (nonlinear plant).
- Single fixed-gain controller performs poorly across the full operating range.
- Operating regions are predictable and distinguishable by a measurable variable.
- A nonlinear controller is too complex to implement or certify.

Practical examples:
- **Autoscaler with load regimes**: Different PID gains for low-load (<30%), mid-load (30–70%), high-load (>70%).
- **Budget pacing with campaign age**: Early campaign (high uncertainty) → high I-term; mature campaign (good history) → lower I-term.
- **Retry/backoff**: At low error rates, aggressive retry; at high error rates, conservative backoff with different gains.
- **Agent loop**: Different planning depth and tool-call rate limits for short vs. long tasks.
- **Thermal control**: Aircraft at takeoff (high dynamic pressure) vs. cruise (low dynamic pressure) — classic gain scheduling domain.

## Inputs

| Input | Description |
|-------|-------------|
| Scheduling variable `σ` | Observable signal that indicates operating regime |
| Operating point models | Linear plant models at each design point σ_i |
| Controller gains per region | `(Kp_i, Ki_i, Kd_i)` tuned at each σ_i |
| Interpolation method | Linear, look-up table, or fuzzy scheduling |

## Outputs

| Output | Description |
|--------|-------------|
| Scheduled gains `K(σ)` | Controller gains appropriate for current operating point |
| Control signal `u(t)` | Applied using scheduled gains |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Bump at region boundary | Abrupt gain switch causes transient | Use smooth interpolation; add bumpless transfer logic |
| Poor performance in transition | Gains tuned only at steady-state points | Add intermediate design points; ensure interpolation is dense |
| Scheduling variable lags reality | σ measured with delay | Apply gain changes proactively; use dead-time compensation ([07-dead-time-compensation.md](07-dead-time-compensation.md)) |
| Wrong regime detected | σ is noisy | Low-pass filter σ before scheduling decision |
| Integral state not reset | Switching without reinitializing integral | Transfer integral state smoothly during switching |

## Worked Example: Autoscaler Gain Scheduling

**Context**: A Kubernetes cluster exhibits different dynamics at different load levels. Single PID tuned for mid-load oscillates at both extremes.

```
Operating regions:
  σ_1: CPU < 30%   → gains tuned for light load: Kp=0.03, Ki=0.005
  σ_2: 30%–70% CPU → gains tuned for normal:     Kp=0.05, Ki=0.010
  σ_3: CPU > 70%   → gains tuned for high load:  Kp=0.08, Ki=0.015

Scheduling variable: 5-minute moving average of cluster CPU utilization

Smooth interpolation at boundary (60%–70%):
  α = (CPU% − 60) / (70 − 60)
  Kp = (1−α)·0.05 + α·0.08

Result: No bump at boundary; correct response across the full load range.
```

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 11. [https://fbsbook.org](https://fbsbook.org)
- Rugh & Shamma (2000), Automatica 36(10):1401-1425.
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 9.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 6.
