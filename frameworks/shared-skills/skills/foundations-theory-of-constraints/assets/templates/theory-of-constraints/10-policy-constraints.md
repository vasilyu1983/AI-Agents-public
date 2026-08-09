# Primitive: Policy Constraints

**Source**: Goldratt (1990), *The Haystack Syndrome*; Schragenheim & Dettmer 2001, *Manufacturing at Warp Speed*; Dettmer 2007, *The Logical Thinking Process* (general reference — Dettmer's book does not have a dedicated "policy constraint" chapter; the concept is distributed across the Intermediate Objectives Map and Current Reality Tree material).

## Definition

A policy constraint is a constraint created by rules, measurements, or decisions — not by physical capacity. It is the most common constraint type in service, knowledge-work, and product organizations, and the most frequently misdiagnosed as a physical constraint.

**Types of policy constraints**:
- **Measurement policies**: metrics that reward local efficiency at the expense of system throughput (e.g., "maximize utilization" rewards every team running hot, which destroys flow).
- **Decision rules**: approvals, sign-off chains, or intake gates that throttle throughput regardless of capacity.
- **Behavioral policies**: norms around WIP, multitasking, or escalation that were designed for a prior context.
- **Incentive misalignment**: individual bonuses tied to metrics that conflict with throughput (e.g., cost-per-unit bonuses that reward large batches, which increase I and reduce T).

**Why policy constraints are dangerous**: they are invisible. Physical capacity constraints show up as queue depth and wait time. Policy constraints show up as "the system isn't flowing but we can't find a bottleneck."

**Detection heuristic**: if elevating a physical constraint doesn't improve throughput, a policy constraint is likely upstream of or co-present with the physical constraint.

## When to Use

- Throughput is not improving despite adding capacity.
- A team is hitting its limits but the measured utilization of individual steps looks fine.
- A Current Reality Tree (primitive 05) identifies root causes that are rules or metrics, not resources.
- Before elevating (buying more capacity), always check for policy constraints first.

## Inputs

- A list of the active measurement systems and metrics that drive daily behavior.
- Decision rights and approval chains.
- Observed behaviors that seem irrational from a throughput perspective.

## Outputs

- A classified list: physical constraints vs. policy constraints.
- For each policy constraint: the rule or metric that creates it, the behavior it drives, and the throughput damage.
- A proposed policy change (injection for the FRT).

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Treating all constraints as physical | Policy constraints invisible without deliberate audit | Ask "why is this step slow?" until you reach a rule, not a resource |
| Changing one policy without updating linked policies | Policies cluster; fixing one often exposes or creates another | Map all policies driving the bottleneck behavior together |
| Metric changed without changing incentives | Teams optimize the new metric in the old way | Align the incentive structure with the new metric simultaneously |
| "We can't change that policy" accepted without challenge | Policy treated as immutable | Apply the Evaporating Cloud (primitive 04): surface the assumption that the policy is unchangeable |
| Policy constraint resolved but physical limit ignored | Swap problem: removing policy constraint reveals physical capacity gap | After resolving policy constraints, re-run 5FS to find the new (possibly physical) constraint |

## Worked Example

**Context**: A software platform team's deployment frequency is low (2 deploys/week). Engineers say the deploy pipeline is fast (15 minutes). The constraint appears invisible.

**Policy audit**:
- Rule 1: "All deployments require VP-level sign-off for production." — 24–48 hour approval lag.
- Rule 2: "Deploys only allowed on Tuesdays and Thursdays." — Driven by an old risk policy from an incident 3 years ago.
- Metric: Engineers measured on "features completed," not "features shipped" — no incentive to push through the approval gate.

**Policy constraint identified**: VP sign-off rule + fixed deploy days.

**Injection**: replace VP sign-off with automated quality gates (CI passing + canary metrics green) for standard deploys; reserve VP sign-off for major releases only. Remove fixed-day restriction.

**Result**: deploy frequency rises from 2/week to 10+/week with no new engineering capacity.

## Sources

- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press.
- Schragenheim, E. & Dettmer, H.W. (2001). *Manufacturing at Warp Speed*. CRC Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (general reference; no single dedicated chapter — confirm any chapter-level citation against your printing)
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
