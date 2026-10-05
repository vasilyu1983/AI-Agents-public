# Primitive 2: Ashby's Law of Requisite Variety

## Definition

**Law of Requisite Variety** (Ashby 1956): Only variety can absorb variety. A regulator must preserve the outcome-relevant distinctions needed to select effective responses to disturbances.

Under Ashby's finite-table conditions and logarithmic variety, the residual-outcome lower bound is `V(outcome) >= V(disturbance) − V(regulator)` (and variety is nonnegative). Regulator variety constrains the best attainable reduction; it does not upper-bound residual error.

V terms must use the same logarithmic measure and the partitions/conditions defined in Ashby §11/6–11/7. This formal relation does not license subtracting unlike operational counts such as tickets, request labels, decisions, people, or control knobs. For an applied audit, define which disturbances require different outcomes, what signal distinguishes each, and whether an effective response is selectable under timing, authority, coupling, and resource constraints.

## When to Use

- Diagnosing why a management layer is overwhelmed or ineffective.
- Designing control planes for microservices, orchestrators, or platform teams.
- Deciding between amplifying controller variety vs. attenuating disturbance variety.
- Evaluating whether a new reporting layer will actually improve control or just add overhead.

## Inputs

| Input | Description |
|-------|-------------|
| Disturbance classes | Outcome-relevant distinctions that require different treatment |
| Detection mapping | Signal that lets the regulator distinguish each class in time |
| Response mapping | Effective response, owner, authority, dependencies, and resource constraints per class |
| Channel capacity | Bandwidth between environment and regulator |
| Error tolerance | Acceptable residual variety (not all variety needs absorbing) |

## Outputs

| Output | Description |
|--------|-------------|
| Coverage gap | Disturbance classes with no timely detectable and effective response path |
| Intervention options | Amplify regulator variety OR attenuate disturbance variety OR both |
| Feasibility assessment | Whether uncovered paths can be closed without redesign |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Management bottleneck | Required distinctions are collapsed or effective responses cannot be selected in time | Attenuate incoming variety or amplify sensing, authority, automation, or delegation |
| Over-engineering controls | Response paths exist but do not cover a required distinction or are never usable | Simplify after verifying removal does not uncover a disturbance class |
| Channel saturation | Information channel between environment and regulator too narrow | Widen channel or compress variety before transmission |
| Goodhart's Law cascade | Regulator forces environment to appear low-variety by measuring only easy metrics | Audit measurement scope; include variety indicators, not just summary statistics |

## Worked Example

**Context**: A platform engineering manager oversees product teams making platform requests. Raw team, request-label, and calendar counts suggest overload but are not commensurate measures of requisite variety.

**Coverage audit**:
- Group requests by the outcome-relevant response they require: standard provisioning, quota change, breaking API migration, security exception, and novel escalation.
- Verify each class has a timely distinguishing signal and an authorized response path.
- The security-exception and novel-escalation classes both depend on the manager's unavailable calendar slot, so these paths fail the timing constraint. This is the deficit; `teams × request labels − decisions` is not evidence of its size.

**Interventions**:
1. Attenuation: request templates preserve the fields that distinguish security, migration, quota, and standard requests while collapsing irrelevant wording differences.
2. Amplification: tech leads receive bounded authority for standard provisioning and quota changes.
3. Self-service: automation handles standard provisioning with audit evidence and routes exceptions.
4. Re-test: every material class is detected and reaches an effective owner within its SLA; coupled failures and unauthorized exceptions still escalate. This closes the observed coverage gap without claiming cardinal equality.

## Sources

- Ashby, W.R. (1956). _An Introduction to Cybernetics_. Chapman & Hall. Ch. 11: Law of Requisite Variety, formal proof.
- Beer, S. (1979). _Heart of Enterprise_. Wiley. Variety engineering applied to management (chapter numbering not independently re-verified for this 2026 audit — cite by topic).
- Conant, R.C., & Ashby, W.R. (1970). Every good regulator of a system must be a model of that system. _International Journal of Systems Science_, 1(2), 89–97.
- Espinosa, A., & Walker, J. (2011). _A Complexity Approach to Sustainability_. Imperial College Press. Variety in organisational contexts.
