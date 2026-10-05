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

**Worked example — p95 latency autoscaler:** Use a declared discrete positional controller u[k]=u_base+Kp·e[k]+Ki·I[k] with e=latency−target and I[k]=I[k−1]+e[k]·dt, followed by replica/rate bounds. At target 200 ms and latency 320 ms, Kp = 0.05 replicas/ms and initial I = 0 give a proportional contribution of 6 replicas; adding this contribution repeatedly to the previous command would define a different controller. For a hypothetical next 30 s with constant error 80 ms, the unconstrained integral increment is 2400 ms·s; Ki = 0.01 would add 24 replicas before saturation handling. Block integration only when it pushes farther into the active bound, permit unwinding, and account for startup delay. These arithmetic inputs are illustrative and provide no oscillation period or tuning recommendation. Use the contract above and the replay helper below before designing plant-specific tuning.

Run the detachable, standard-library demonstration from the bundle root:

```bash
python3 scripts/controller_demo.py --self-test
python3 scripts/test_controller_demo.py
```

The demo uses a first-order gain-one plant with a five-second time constant, two-second delay and fixed bounded sensor disturbance. A deliberately infeasible target saturates the actuator, followed by a feasible target. It compares conditional integration with an unprotected integral and checks both upper/lower outward freezing and inward unwinding. Metrics are maximum excess above target after the first downward target crossing, finite-window settling time, actuator-bound violations and integrated absolute effort. Post-crossing excess is null if the target is never crossed; the initial offset at the setpoint change is excluded. The protected case settles in 28.3 seconds in this specified model; the unprotected case does not settle within the 70-second recovery window. These are reproducible synthetic results, not production benchmarks or a stability proof.

The demo does not implement a production PID, derivative filtering, irregular sampling or autoscaling. Validate those contract items on the identified plant before deployment. Reference: Åström and Murray, [Feedback Systems](https://fbsbook.org), PID/anti-windup treatment; [MathWorks PID controller](https://www.mathworks.com/help/simulink/slref/pidcontroller.html), clamping and back-calculation conventions.

The integral helper rejects nonfinite inputs and arithmetic overflow before returning a command; the caller must choose the bounded fallback for this error.
