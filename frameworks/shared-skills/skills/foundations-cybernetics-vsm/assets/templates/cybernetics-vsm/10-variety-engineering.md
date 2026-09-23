# Primitive 10: Variety Engineering

## Definition

**Variety engineering** deliberately preserves, attenuates, transforms, or expands outcome-relevant distinctions on channels between levels of a system. In applied work, test whether each material disturbance can be distinguished and met by an effective response; do not compare raw event, attention, state-label, or lever counts as though they shared one unit.

Three primary mechanisms:

- **Attenuators**: reduce the variety arriving at a level. Examples: aggregation, filtering, exception-only reporting, sampling, summarisation, dashboards.
- **Amplifiers**: increase the effective variety a controller can exercise. Examples: delegation, standard playbooks, automation, self-service, sub-agents, decision support tools.
- **Transducers**: transform variety from one form to another, making it actionable at the receiving level. Examples: alerting systems, translation layers, analytics platforms that convert raw data into decision-relevant signals.

Variety engineering is applied on every channel between VSM levels — both upward (S1 → S3) and downward (S3 → S1).

## When to Use

- Designing reporting architectures, dashboards, and information flows.
- Reducing management overload when Ashby's Law audit reveals a variety gap.
- Designing APIs or interfaces between services to manage complexity.
- Building the information layer of an agent orchestration system.
- Diagnosing why an executive always has too much or too little information to act.

## Inputs

| Input | Description |
|-------|-------------|
| Coverage gap from Ashby audit | Material disturbance classes lacking a timely detectable and effective response path |
| Channel inventory | All channels between levels that carry information |
| Response constraints | Authority, latency, coupling, dependencies, and resources that determine whether each response works |
| Action latency | How quickly the controller must act (affects attenuation budget) |

## Outputs

| Output | Description |
|--------|-------------|
| Attenuated channels | Channels redesigned to reduce incoming variety |
| Amplified control surfaces | Mechanisms that expand controller's effective response range |
| Covered architecture | Channel map showing the signal and effective response for every material disturbance class |
| Residual coverage list | Uncovered or ineffective response paths requiring acceptance, attenuation, or escalation |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Over-attenuation (information starvation) | Important signals filtered out before reaching controller | Audit what is being filtered; restore high-stakes signals via algedonic channel |
| Under-attenuation (management overload) | Raw operational data reaching upper levels without aggregation | Introduce aggregation, sampling, and exception-only filters |
| Amplifier without governance | Delegation expands control surface but without accountability | Pair every amplifier with a feedback loop and accountability mechanism |
| Transducer mismatch | Raw data arrives in form that decision-makers cannot act on | Redesign transducer output to match the decision vocabulary of the receiving level |
| Static variety design | Variety engineering designed for current conditions; environment shifts | Build variety-engineering review into operational cadence |

## Worked Example

**Context**: An AI orchestrator receives telemetry from many executor instances. A human operations team must intervene on material failures. Instance counts, state labels, and daily attention slots nominate an overload risk but cannot be subtracted to prove a gap.

**Coverage audit**:
- Define outcome-relevant classes: transient retryable failure, capacity saturation, cost runaway, unsafe action attempt, compromised executor, and novel failure.
- For each class, record detection signal, routing SLA, authorized owner, effective intervention, shared dependencies, and fallback.
- The audit finds that unsafe actions are detected and blocked automatically, while novel failures reach humans without enough context to choose an intervention before the SLA expires. That failed path is the gap.

**Variety engineering interventions**:

1. **Attenuator — exception routing**: suppress routine healthy events while preserving security, safety, and novel-failure classes; validate false-negative risk rather than relying on a universal sigma threshold.
2. **Attenuator — aggregation dashboard**: aggregate operational health but retain drill-down signals needed to distinguish response classes.
3. **Amplifier — playbook automation**: bounded playbooks handle validated routine classes; humans receive novel or authorization-sensitive failures.
4. **Algedonic bypass**: any agent failure affecting >5% of fleet capacity triggers an immediate alert to human on-call, bypassing the dashboard layer (see primitive #11).
5. **Transducer — cost-attributed alerting**: raw log events transformed into "cost impact" language before reaching the ops team — converting technical signals to decision-relevant vocabulary.

**Result**: replayed incidents show each material class is detected, routed, and met by an authorized effective response within its SLA. The novel-failure path now includes diagnostic context and a safe containment action. Report observed coverage and misses, not a synthetic state-count reduction.

## Sources

- Beer, S. (1979). _Heart of Enterprise_. Wiley. Ch. 4–6: Variety engineering — amplifiers, attenuators, and the management of complexity.
- Beer, S. (1985). _Diagnosing the System for Organizations_. Wiley. Practical variety-engineering exercises (ch. 3–5).
- Ashby, W.R. (1956). _An Introduction to Cybernetics_. Chapman & Hall. Variety and the constraint of regulation (ch. 7–11).
- Hoverstadt, P. (2009). _The Fractal Organization_. Wiley. Variety engineering in organisational design (ch. 8).
- Schwaninger, M., & Ott, S.C. (2025). "Variety Engineering – A Cybernetic Concept with Practical Implications." In: *Computer Aided Systems Theory – EUROCAST 2024*. LNCS vol. 15173, Springer. DOI: 10.1007/978-3-031-82957-4_21. Provides a formal mathematical definition of variety engineering as mutual complexity amplification/attenuation between interacting agents; illustrates with ecological, social, and economic cases. Updated formalisation of the Schwaninger & Ott 2023 SRBS article.
