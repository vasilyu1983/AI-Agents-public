# Mechanism: Dead-Time Compensation (Smith Predictor)

**Sources**: Smith, O.J.M. (1957), "Closer control of loops with dead time," Chemical Engineering Progress 53(5):217-219. Åström & Murray, *Feedback Systems* Ch. 11 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 6 (2019).

## Definition

**Dead time** (transport lag or pure delay) is the time between applying a control input and observing any effect in the output. It is one of the hardest challenges for closed-loop control — a standard PID controller "sees" a stale measurement and overshoots or oscillates.

**Smith Predictor** removes the dead time from the feedback loop by using a model to predict what the output *would be* if there were no delay, and feeding that prediction to the controller:

```
Standard feedback (dead time L):
  Controller → Plant (delay L) → Output → [delay L] → Error

Smith Predictor structure:
  e_pred = y_measured − [model_no_delay(u) − model_with_delay(u)]
                         └────────────────────────────────────────┘
                                     internal model
  Controller sees e_pred (delay-free estimate of error)
  Outer loop: y_measured − setpoint = steady-state correction
```

The controller now designs against the delay-free model, and the predictor handles the transport lag separately.

**Key result**: With a perfect model, the Smith Predictor reduces the problem to controlling a delay-free system. In practice, the predictor is robust to moderate model mismatch.

## When to Use

- System has a known, approximately constant delay between action and measurement.
- PID controller is oscillating or unstable due to the lag (not due to gain issues alone).
- Process control with pipeline lag (fluid flow, thermal systems).
- Computing systems with propagation delay: CDN cache invalidation, multi-region replication lag.
- Autoscaling with instance startup time: the effect of adding replicas is not felt immediately.
- Retry/backoff with propagation time: downstream service recovery not visible for several seconds.

**Rule of thumb**: Use Smith Predictor when `L/T > 0.5` where `L` = dead time and `T` = dominant time constant. Below 0.5, detuned PID is often sufficient.

## Inputs

| Input | Description |
|-------|-------------|
| Dead time estimate `L` | How long before a control action has any effect |
| Plant model (no delay) | Transfer function or state-space model of the delay-free plant |
| Current measurement `y(t)` | Actual output |
| Control input `u(t)` | Applied control signal |

## Outputs

| Output | Description |
|--------|-------------|
| Predicted error `e_pred` | Delay-compensated error signal for the controller |
| Control signal `u(t)` | Corrective action with delay accounted for |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Oscillation persists | Dead time estimate wrong by > 30% | Re-identify delay; use adaptive delay estimator |
| Steady-state offset | Model gain error | Outer feedback loop corrects DC gain errors |
| Unstable under variable delay | Delay is not constant | Use filtered Smith Predictor or robust variant |
| Over-compensation | Delay estimate too large | Reduce `L` estimate; re-test step response |
| Model mismatch instability | Plant dynamics changed significantly | Retrain model; add model-mismatch detector |

## Worked Example: Autoscaler with Instance Startup

**Problem**: Adding a compute instance takes 90 seconds before it handles traffic. Without compensation, the scaler sees no effect for 90s, over-adds instances, then over-compensates when they all come online.

```
Configuration:
  L = 90 seconds (startup dead time)
  Plant model: capacity(t) = requested_replicas(t − L) × capacity_per_instance

Smith Predictor internal model:
  model_no_delay: capacity = requested_replicas × capacity_per_instance
  model_with_delay: same, but applied 90s later

Predicted error at time t:
  e_pred = target_capacity − (model_no_delay(u(t)) − model_with_delay(u(t))) − actual_capacity(t)

Controller acts on e_pred, not on the 90-second-stale actual measurement.
Result: scaler adds exactly the right number of instances without overshoot.
```

## Sources

- Smith (1957), Chemical Engineering Progress 53(5):217-219.
- Åström & Murray, *Feedback Systems*, Ch. 11. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 6.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 8.
