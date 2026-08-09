# Primitive 3: VSM System 1 — Operations

## Definition

**System 1 (S1)** comprises the operational units of a viable system: the parts that carry out the primary activities. Each S1 unit is itself a viable system at the next recursion level — it has its own management, its own feedback loops, and its own interaction with its local environment.

S1 units operate with **autonomy within policy**: they make decisions about how to execute their work without needing approval from S3, provided they stay within the constraints and resources allocated to them.

Key properties:
- Each S1 unit has an operational management layer (a mini-S3 within itself).
- S1 units interact directly with their local environments.
- S1 units are coordinated by S2 (not commanded by S3).
- S1 is where value is actually created.

## When to Use

- Designing team or squad boundaries.
- Defining the scope of microservices or bounded contexts.
- Assigning agent roles in a multi-agent system.
- Diagnosing whether execution units have genuine autonomy or are being micro-managed.

## Inputs

| Input | Description |
|-------|-------------|
| Primary activity definition | What value this unit produces |
| Environmental boundary | Which part of the external environment this unit interacts with |
| Resource allocation | Budget, compute, time, or headcount assigned by S3 |
| Policy constraints | Non-negotiable rules set by S3/S5 within which the unit operates |

## Outputs

| Output | Description |
|--------|-------------|
| Primary value | Products, services, data, or decisions produced |
| Operational state reports | Status signals to S3 and S2 |
| Local environment intelligence | Signals from the unit's environment, passed to S4 via S3 |
| Autonomy scope | Decision space the unit fills without upward escalation |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| S3 collapsed into S1 (micromanagement) | S3 makes execution decisions instead of setting policy | Redefine S3 role as policy-setter; return decision authority to S1 |
| S1 units operate in isolation | No S2 coordination; units unaware of each other | Install S2 coordination layer with shared scheduling and resource visibility |
| S1 autonomy without accountability | Units optimise locally with no S3 feedback loop | Establish performance monitoring and resource-negotiation interface to S3 |
| Boundary confusion | Multiple S1 units claim the same environmental segment | Clarify ownership boundaries; redesign using domain-driven design or capability mapping |

## Worked Example

**Context**: A product company has three product squads (growth, retention, monetisation).

**S1 mapping**:
- Each squad = one S1 unit.
- Growth squad's local environment: acquisition channels, paid media, referral loops.
- Retention squad's local environment: in-product engagement signals, support tickets, churn events.
- Monetisation squad's local environment: pricing experiments, revenue data, payment flows.

**Autonomy scope**: Each squad decides which experiments to run, which tools to use, and how to prioritise within their backlog — without approval from the product director (S3).

**S3 interface**: Weekly metrics review; resource negotiation at sprint boundary; policy update on revenue targets from S5.

**S2 coordination**: Shared calendar for experiment scheduling to prevent A/B test interference between squads.

## Sources

- Beer, S. (1972). _Brain of the Firm_. Allen Lane. Section "Autonomics — Systems One, Two, Three" — System One as the operational elements. *(2026-07 correction: earlier draft cited a standalone "Ch. 3"; the verified table of contents shows Systems One–Three treated together in one section, not as separate numbered chapters. Numbering also differs between the 1972 and 1981 2nd editions — cite by section title, not chapter number.)*
- Beer, S. (1985). _Diagnosing the System for Organizations_. Wiley. Practical S1 identification and boundary-drawing exercises.
- Hoverstadt, P. (2009). _The Fractal Organization_. Wiley. S1 autonomy and the recursion principle (ch. 2).
- Espinosa, A., & Walker, J. (2011). _A Complexity Approach to Sustainability_. Imperial College Press. S1 in complex adaptive systems.
