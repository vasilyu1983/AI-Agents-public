# Primitive 2: Ashby's Law of Requisite Variety

## Definition

**Law of Requisite Variety** (Ashby 1956): Only variety can absorb variety. A regulator can control a system only if the regulator's variety (number of distinguishable states it can occupy or respond to) is at least equal to the variety of the disturbances it must handle.

Formal statement: `W(error) ≤ V(disturbance) − V(regulator)`

Where W(error) is the residual error, V(disturbance) is the variety of the environment the system faces, and V(regulator) is the variety the controller can exercise. To drive error to zero, V(regulator) must equal V(disturbance).

## When to Use

- Diagnosing why a management layer is overwhelmed or ineffective.
- Designing control planes for microservices, orchestrators, or platform teams.
- Deciding between amplifying controller variety vs. attenuating disturbance variety.
- Evaluating whether a new reporting layer will actually improve control or just add overhead.

## Inputs

| Input | Description |
|-------|-------------|
| Disturbance inventory | List of distinct states or events the environment can produce |
| Regulator inventory | List of distinct responses the controller can make |
| Channel capacity | Bandwidth between environment and regulator |
| Error tolerance | Acceptable residual variety (not all variety needs absorbing) |

## Outputs

| Output | Description |
|--------|-------------|
| Variety gap | V(disturbance) − V(regulator); positive gap = control deficit |
| Intervention options | Amplify regulator variety OR attenuate disturbance variety OR both |
| Feasibility assessment | Whether gap can be closed without redesign |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Management bottleneck | Regulator variety too low for disturbance variety | Attenuate incoming variety (exception-only reporting) or amplify via delegation |
| Over-engineering controls | Regulator variety exceeds disturbance variety | Simplify control surface; unused variety is waste |
| Channel saturation | Information channel between environment and regulator too narrow | Widen channel or compress variety before transmission |
| Goodhart's Law cascade | Regulator forces environment to appear low-variety by measuring only easy metrics | Audit measurement scope; include variety indicators, not just summary statistics |

## Worked Example

**Context**: A platform engineering manager oversees 8 product teams making platform requests. Each team has ~50 distinct request types. The manager's calendar allows ~20 focused decisions per week.

**Variety audit**:
- V(disturbance) = 8 teams × 50 request types = 400 distinguishable states per week (simplified).
- V(regulator) = 20 decisions per week.
- Variety gap = 380 — far exceeds manager's capacity.

**Interventions**:
1. Attenuation: introduce request templates that collapse 50 types to 8 standard categories. V(disturbance) → 64.
2. Amplification: delegate routine approval to tech leads. Manager handles only non-standard escalations.
3. Self-service: automate provisioning for the top 5 request types (50% of volume). V(disturbance) → ~32.
4. Result: manager handles ~32 distinguishable situations per week — within capacity.

## Sources

- Ashby, W.R. (1956). _An Introduction to Cybernetics_. Chapman & Hall. Ch. 11: Law of Requisite Variety, formal proof.
- Beer, S. (1979). _Heart of Enterprise_. Wiley. Variety engineering applied to management (chapter numbering not independently re-verified for this 2026 audit — cite by topic).
- Conant, R.C., & Ashby, W.R. (1970). Every good regulator of a system must be a model of that system. _International Journal of Systems Science_, 1(2), 89–97.
- Espinosa, A., & Walker, J. (2011). _A Complexity Approach to Sustainability_. Imperial College Press. Variety in organisational contexts.
