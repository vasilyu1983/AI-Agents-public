# Discrete Controller Contract and Demonstration

Use this before translating a continuous formula into an autoscaler, pacer or admission controller.

| Contract item | Required decision and verification |
|---|---|
| Units and sign | State measurement/setpoint units, actuator units, positive plant direction and output mapping. With e=60−82=-22 and u=.05e=-1.1, autoscaling uses reverse action delta_replicas=-u=+1.1. |
| Period | Measure actual elapsed time with a monotonic clock. Define acceptable jitter, maximum gap and stale-sensor fallback; never integrate repeatedly over the same measurement. |
| Derivative | Use filtered derivative-on-measurement when setpoint kick matters; specify filter bandwidth and noise assumptions. Differentiation amplifies noise even without a setpoint step. |
| Quantization | Specify integer replica rounding, minimum dwell time and hysteresis. Test limit cycles; continuous gains alone do not certify quantized behavior. |
| Saturation | Clamp in actuator units and feed the applied action back to anti-windup. Stop integral increments pushing farther into either bound; permit unwinding. Include downstream overrides/limits. |
| Startup and transfer | Initialize integral to match the current actuator for bumpless transfer: I_out=u_current−Kp*e minus other contributions. Track applied output during manual control; define reset on stale/model-invalid data. |
| Failure | Define safe bounded action for missing/nonfinite samples, solver timeout, actuator failure and exhausted retry budget. A retry budget exhaustion stops retries. |
| Coupling | Identify other loops sharing sensors or actuators; test the composite loop under delay and saturation. |

Run the detachable, standard-library demonstration from the bundle root:

```bash
python3 scripts/controller_demo.py --self-test
```

The demo uses a first-order gain-one plant with a five-second time constant, two-second delay and fixed bounded sensor disturbance. A deliberately infeasible target saturates the actuator, followed by a feasible target. It compares conditional integration with an unprotected integral and checks both upper/lower outward freezing and inward unwinding. Metrics are maximum recovery overshoot, finite-window settling time, actuator-bound violations and integrated absolute effort. The protected case settles in 28.3 seconds in this specified model; the unprotected case does not settle within the 70-second recovery window. These are reproducible synthetic results, not production benchmarks or a stability proof.

The demo does not implement a production PID, derivative filtering, irregular sampling or autoscaling. Validate those contract items on the identified plant before deployment. Reference: Åström and Murray, [Feedback Systems](https://fbsbook.org), PID/anti-windup treatment; [MathWorks PID controller](https://www.mathworks.com/help/simulink/slref/pidcontroller.html), clamping and back-calculation conventions.
