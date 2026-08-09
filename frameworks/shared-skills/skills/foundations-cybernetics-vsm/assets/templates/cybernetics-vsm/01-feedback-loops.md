# Primitive 1: Feedback Loops

## Definition

A feedback loop exists when the output of a system is routed back as an input that modifies future output. Two types:

- **Negative (balancing) loop**: output deviation from a goal triggers a corrective action that reduces the deviation. Produces stability.
- **Positive (reinforcing) loop**: output amplifies the condition that produced it. Produces growth or collapse.

Every viable system requires at least one negative feedback loop to maintain any goal state.

## When to Use

- Any time a variable must be kept within bounds (latency, burn rate, error rate, NPS).
- When designing adaptive behaviour in agents or processes.
- When diagnosing why a system oscillates, drifts, or explodes.
- Before adding a reinforcing loop — ensure a corresponding balancing loop exists.

## Inputs

| Input | Description |
|-------|-------------|
| Goal variable | The desired state or setpoint (e.g., p99 latency < 200 ms) |
| Sensor | Mechanism that measures current state |
| Comparator | Logic that calculates deviation from goal |
| Effector | Mechanism that acts to reduce deviation |
| Delay | Time between sensing and effector action |

## Outputs

| Output | Description |
|--------|-------------|
| Regulated state | Variable held near goal despite disturbances |
| Stability envelope | Range within which the system remains stable |
| Loop map | Diagram of causal links with polarity (+/−) and delay markers |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Oscillation | Delay too long relative to loop gain | Reduce gain or shorten feedback delay |
| Drift | Sensor inaccurate or comparator miscalibrated | Audit measurement accuracy; recalibrate setpoint |
| Runaway | Reinforcing loop without a balancing counterpart | Introduce a limiting condition or a goal-seeking loop |
| Goal erosion | Goal variable lowered to match performance rather than vice versa | Lock goal independently; audit who can change the setpoint |

## Worked Example

**Context**: An agent orchestrator must keep queue depth below 100 tasks.

**Balancing loop design**:
1. Goal: queue depth ≤ 100.
2. Sensor: orchestrator polls queue length every 30 seconds.
3. Comparator: if depth > 80 (80% threshold), trigger scale-out signal.
4. Effector: spawn one additional worker agent per 20 tasks above threshold.
5. Delay: ~60 s from detection to worker available.

**Reinforcing loop risk**: if workers are spawned without a ceiling, successful task completion frees more tasks into the queue (backpressure from upstream), creating unbounded growth. Add a hard ceiling: maximum 10 workers regardless of queue depth.

## Sources

- Wiener, N. (1948). _Cybernetics_. MIT Press. Ch. 4, "Feedback and Oscillation" — negative feedback as the basis of purposive, goal-seeking behaviour.
- Beer, S. (1979). _Heart of Enterprise_. Wiley. Feedback as the first-order management mechanism. (Chapter numbering not independently re-verified for this 2026 audit — cite by topic, not chapter number, until confirmed against a physical/scanned copy.)
- Ashby, W.R. (1956). _An Introduction to Cybernetics_. Chapman & Hall. Ch. 5 "Stability" and ch. 12 "The Error-controlled Regulator" — homeostasis and error-controlled regulation. *(2026-07 correction: earlier draft cited ch. 7–9, which are "Quantity of Variety" / "Transmission of Variety" / "Incessant Transmission" — variety-transmission chapters, not error-controlled regulation. Corrected against the verified 1957 first-edition table of contents.)*
- Sterman, J.D. (2000). _Business Dynamics_. McGraw-Hill. Feedback loop notation, delays, and oscillation (ch. 5–6, unverified against primary copy — treat as approximate).
