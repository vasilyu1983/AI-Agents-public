# Mechanism: Anti-Windup

**Sources**: Åström & Murray, *Feedback Systems* Ch. 10 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 4 (2019). Bohn & Atherton (1995), "An analysis package comparing PID anti-windup strategies," IEEE Control Systems.

## Definition

**Integrator windup** occurs when a PID controller's integral term accumulates indefinitely during saturation — when the actuator is already at its limit and cannot apply the computed control signal. When saturation ends, the large accumulated integral causes a large overshoot before the controller can correct back.

```
Without anti-windup (bad):
  Integral keeps accumulating while u is clamped at u_max.
  When saturation ends: massive overshoot as integral "unwinds."

With anti-windup:
  When actuator saturates: freeze or back-calculate the integral so it
  reflects the actual applied signal, not the ideal unclamped signal.
```

Three standard anti-windup techniques:

**1. Clamping (freeze integral at saturation)**:
```
if u ≥ u_max or u ≤ u_min:
  do not update integral term
else:
  integrate normally
```

**2. Back-calculation (continuous-time)**:
```
dI/dt = e(t) + (u_sat − u_unsat) / T_t
where T_t = tracking time constant (tuning parameter ≈ √(T_i · T_d))
u_sat = clamp(u_unsat, u_min, u_max)
```

**3. Conditional integration**:
```
Only integrate when sign(e) matches sign(u_unsat − u_sat).
Prevents integration in the wrong direction during saturation.
```

## When to Use

- Any PID controller where the actuator has hard limits (always — no actuator is unlimited).
- Autoscaling: replica count has a hard ceiling; integral winds up at max replicas.
- Budget pacing: bid multiplier clamped at platform maximum; integral accumulates over floor/ceiling.
- Rate limiters: throughput cap is a hard limit; the I-term should not accumulate beyond it.
- Agent loops: token allocation has an absolute cap; integrate only while budget is available.

**Default**: include anti-windup in every PID implementation. Leaving it out is the implementation anti-pattern.

## Inputs

| Input | Description |
|-------|-------------|
| Error `e(t)` | Setpoint − measurement |
| Actuator limits `u_min, u_max` | Hard constraints on the control signal |
| Tracking constant `T_t` | Back-calculation tuning (technique 2) |
| Integration accumulator `I` | Current integral state to be conditionally frozen |

## Outputs

| Output | Description |
|--------|-------------|
| Clamped control signal `u_sat` | Applied to actuator; never exceeds limits |
| Bounded integral `I` | Does not accumulate beyond what the actuator can apply |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Overshoot after saturation | Anti-windup missing or disabled | Add clamping or back-calculation |
| Slow recovery from saturation | T_t too large (back-calculation too slow) | Reduce T_t; try clamping instead |
| Oscillation near limits | T_t too small (over-aggressive back-calc) | Increase T_t |
| Wrong integral direction | Actuator saturated in wrong direction | Use conditional integration; verify limit logic |
| Windup on min-side | Only max-side clamp implemented | Clamp both min and max |

## Worked Example: Budget Pacing Anti-Windup

**Problem**: Bid multiplier is clamped between 0.1× and 3×. Target CPM = $5. Actual CPM = $8 (overspending). Integral term keeps accumulating "increase bid" despite multiplier already at 3×.

```
Without anti-windup:
  Multiplier stuck at 3× for 2 hours.
  Integral accumulates: I = Σe·Δt = +50 CPM-minutes.
  When CPM drops to $4: multiplier should drop, but integral unwinds first.
  → bid stays near 3× for another hour → overspend.

With clamping anti-windup:
  When multiplier = 3×: freeze I. Do not accumulate.
  When CPM drops to $4: I = 0 (frozen); controller responds immediately.
  → correct multiplier applied within one control cycle.
```

## Sources

- Åström & Murray, *Feedback Systems*, Ch. 10. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 4.
- Bohn & Atherton (1995), IEEE Control Systems 15(2):34-40.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 4.
