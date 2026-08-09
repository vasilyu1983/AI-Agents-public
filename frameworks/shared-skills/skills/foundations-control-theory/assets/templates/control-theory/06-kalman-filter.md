# Mechanism: Kalman Filter

**Sources**: Kalman, R.E. (1960), "A New Approach to Linear Filtering and Prediction Problems," ASME J. Basic Engineering 82:35-45. Åström & Murray, *Feedback Systems* Ch. 8 (2020). Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems* Ch. 8 (2019).

## Definition

The **Kalman filter** is a recursive state estimator for linear systems with Gaussian noise. It fuses a model-based prediction with noisy sensor measurements to produce the **minimum-variance estimate** of the true state.

Two-step cycle:

**Predict** (propagate state forward using model):
```
x̂⁻(k) = A·x̂(k−1) + B·u(k−1)          (prior state estimate)
P⁻(k)  = A·P(k−1)·Aᵀ + Q               (prior covariance)
```

**Update** (correct prediction using measurement):
```
K(k)   = P⁻(k)·Cᵀ · [C·P⁻(k)·Cᵀ + R]⁻¹   (Kalman gain)
x̂(k)  = x̂⁻(k) + K(k)·[y(k) − C·x̂⁻(k)]   (posterior state estimate)
P(k)   = [I − K(k)·C]·P⁻(k)                (posterior covariance)
```

Where:
- `Q` = process noise covariance (model uncertainty)
- `R` = measurement noise covariance (sensor uncertainty)
- `K` = Kalman gain (how much to trust the measurement vs. the prediction)

When `R` is large (noisy sensor), `K` is small — trust the model more. When `Q` is large (uncertain model), `K` is large — trust the measurement more.

## When to Use

- State cannot be measured directly but can be inferred from noisy observations.
- Sensor measurements are noisy and model predictions are available.
- Feeding estimated state into an MPC or PID controller ([05-mpc.md](05-mpc.md), [01-pid-control.md](01-pid-control.md)).
- Tracking slowly-changing states in distributed systems (e.g., true service latency behind noisy P99 measurements).
- Anomaly detection: compare `y(k) − C·x̂⁻(k)` (innovation) to expected noise; large innovations signal anomalies.

**Extended Kalman Filter (EKF)**: linearizes nonlinear systems around the current estimate. Use when system dynamics are nonlinear.

## Inputs

| Input | Description |
|-------|-------------|
| System matrices `A, B, C` | State-space model |
| Noise covariances `Q, R` | Tuning parameters: model uncertainty, sensor noise |
| Measurements `y(k)` | Noisy sensor outputs |
| Control inputs `u(k)` | Known actuator commands |

## Outputs

| Output | Description |
|--------|-------------|
| State estimate `x̂(k)` | Best estimate of true system state |
| Error covariance `P(k)` | Uncertainty in the estimate |
| Innovation `y − Cx̂⁻` | Residual; use for anomaly detection |
| Kalman gain `K` | Sensor-vs-model trust weighting |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Filter diverges | Q or R misspecified; unobservable state | Verify observability first ([03-observability-controllability.md](03-observability-controllability.md)); re-tune Q and R |
| Overconfident estimate | R set too small | Increase R to reflect true sensor noise |
| Slow adaptation to changes | Q set too small | Increase Q; use adaptive Kalman filter |
| Poor nonlinear tracking | Linear model used on nonlinear system | Use EKF or Unscented Kalman Filter (UKF) |
| Initialization matters | Bad initial P(0) | Set P(0) large (high initial uncertainty); filter converges within a few steps |

## Worked Example: Service Latency Estimation

**Problem**: P99 latency metric is noisy (sensor noise R = 25ms²). True latency changes slowly (model noise Q = 1ms²). True latency unknown; estimate from noisy measurements.

```
State: x = true_latency
Model: x(k) = x(k−1)  (slowly-varying random walk; A = 1, B = 0)
Sensor: y(k) = x(k) + noise  (C = 1)

Q = 1,  R = 25  (model trusted more than sensor)

Step k=1: y=110ms
  x̂⁻ = 100 (initial guess)
  P⁻  = 10 + 1 = 11
  K   = 11 / (11 + 25) = 0.306
  x̂  = 100 + 0.306·(110 − 100) = 103ms
  P   = (1 − 0.306)·11 = 7.6

Step k=2: y=95ms
  x̂⁻ = 103
  P⁻  = 7.6 + 1 = 8.6
  K   = 8.6 / (8.6 + 25) = 0.256
  x̂  = 103 + 0.256·(95 − 103) = 100.9ms
```

The filter smooths the noisy 110ms/95ms readings to a stable ~101ms estimate.

## Sources

- Kalman (1960), ASME J. Basic Engineering 82:35-45.
- Åström & Murray, *Feedback Systems*, Ch. 8. [https://fbsbook.org](https://fbsbook.org)
- Franklin, Powell & Emami-Naeini, *Feedback Control of Dynamic Systems*, Ch. 8.
- Welch & Bishop, "An Introduction to the Kalman Filter," UNC-Chapel Hill TR 95-041. [https://www.cs.unc.edu/~welch/kalman/](https://www.cs.unc.edu/~welch/kalman/)
