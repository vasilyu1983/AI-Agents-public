# Cybernetics and VSM Formal Theory Map

Use this map when a task needs the theory behind the primitive playbooks, not just a recipe.

## Theory Spine

| Construct | What It Formalizes | Operational Test |
|-----------|--------------------|------------------|
| System-in-focus | The boundary of the system being diagnosed | Can you say what is inside, outside, and controlled by the system? |
| First-order cybernetics | Control of an observed system | Is the controller outside the process it regulates? |
| Second-order cybernetics | Control where the observer/controller is part of the system | Does the controller change the system by observing or intervening? |
| Feedback loop | Measurement, comparison, action, and delay | Is there a goal variable, sensor, comparator, actuator, and lag? |
| Requisite variety | Regulator capacity relative to environmental disturbance variety | Can the controller generate enough distinct responses for the disturbances? |
| VSM recursion | A viable system contains viable subsystems and belongs to a larger viable system | Can every level define its own S1-S5 without collapsing into the level above? |
| Homeostasis | Stability through balancing loops | Does the system return to an acceptable range after disturbance? |
| Algedonic signal | Exceptional pain/pleasure signal bypassing normal channels | Is there a thresholded escalation path that avoids routine reporting delay? |

## VSM Function Map

| VSM Function | Necessary Role | Failure If Missing |
|--------------|----------------|--------------------|
| System 1 - Operations | Autonomous units doing the work | Central bottleneck; no local adaptation |
| System 2 - Coordination | Damp oscillation between S1 units | Thrashing, duplicated work, resource conflict |
| System 3 - Internal control | Optimize the present operational system | Local optima dominate whole-system performance |
| System 3* - Audit | Direct reality check from S3 to S1 | Filtered reports hide ground truth |
| System 4 - Intelligence | Scan environment and future options | Strategy lags environment change |
| System 5 - Policy/identity | Close governance and resolve S3/S4 tension | Identity drift, unresolved policy conflict |

## Requisite Variety Pattern

1. List disturbances the system must survive.
2. Estimate their variety: distinct states that require distinct responses.
3. List regulator responses available at the same time scale.
4. Add attenuators where environmental variety is too high: aggregation, standards, exception filters, queues, APIs.
5. Add amplifiers where regulator variety is too low: delegated authority, tooling, automation, self-service, training.
6. Check the latency of the control loop; late variety is not effective variety.

## Recursion Rules

- Do not map VSM once for the whole organization and stop. Repeat the map at each viable level.
- A team can be S1 of a division and also have its own S1-S5 internally.
- Do not confuse rank with recursion. A senior person can perform S2 or S4; title does not define system function.
- If two levels share the same S5 without local identity, the lower level may not be viable.

## What Counts as Evidence

- Valid VSM diagnosis: explicit system boundary, recursion level, named S1-S5 functions, missing-function evidence, and channel design.
- Valid Ashby claim: named disturbances, response repertoire, variety attenuators/amplifiers, and timing assumptions.
- Valid algedonic design: threshold, bypass path, receiving authority, rate limit, and test cadence.

## Source Anchors

- Beer: VSM systems, recursion, S3*, algedonic channels, viable organization diagnosis.
- Ashby: requisite variety, regulator-system variety relation, good regulator implications.
- Wiener: feedback and cybernetic control foundation.
- Conant and Ashby: good regulator theorem; a regulator must embody a model of the system.
- Medina (2011): the only large-scale, contemporaneous VSM field deployment (Project Cybersyn, Chile 1971–1973) with a rigorous archival history — use as the reality check against embellished claims about what VSM has actually demonstrated at national scale. See `patterns-scenarios-traps.md` for the fact-vs-myth table.
