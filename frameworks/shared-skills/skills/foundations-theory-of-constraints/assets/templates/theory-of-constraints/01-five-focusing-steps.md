# Primitive: Five Focusing Steps (5FS)

**Source**: Goldratt 1984, *The Goal*; Cox & Spencer 1998, *The Constraints Management Handbook*.

## Definition

The Five Focusing Steps are the core operating loop of Theory of Constraints. They direct all improvement energy toward the system's single weakest link — the constraint — rather than spreading it across all steps.

1. **Identify** the constraint: find the single resource, policy, or step that limits system throughput.
2. **Exploit** the constraint: squeeze maximum output from the constraint without additional spend.
3. **Subordinate** everything else: adjust all non-constraints to feed the constraint optimally.
4. **Elevate** the constraint: invest to permanently increase constraint capacity if steps 2–3 are insufficient.
5. **Repeat**: once a constraint is broken, return to step 1 — a new constraint has emerged.

## When to Use

- Prioritizing where to invest improvement effort across a multi-step process.
- Sprint or quarterly planning when multiple bottlenecks compete for attention.
- Diagnosing why throughput is not increasing despite local optimizations.

## Inputs

- A measurable throughput metric (orders shipped, features deployed, revenue recognized).
- A map of the process steps with observed or measured capacity and utilization.
- Current WIP levels per step.

## Outputs

- A ranked list: one identified constraint, confirmed exploitations, a subordination plan for non-constraints, and an elevation decision.
- A "do not improve" list: non-constraint steps that should be held stable.

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| Improving the wrong step | Constraint misidentified (often confused with highest-utilization step) | Measure actual queue depth and wait time, not just utilization |
| Elevating before exploiting | Capital spent before obvious slack reclaimed | Mandate exploit + subordinate sprint before any capacity investment |
| Breaking the constraint without updating the plan | New constraint emerges silently | Schedule a 5FS review after every elevation; the loop never ends |
| Subordination ignored | Teams optimize locally and starve the constraint | Freeze WIP limits on non-constraints until constraint is exploited |
| Treating policy as physical | A rule or metric creates the constraint but is assumed unchangeable | See primitive 10 (Policy Constraints) |

## Worked Example

**Context**: A software team ships 8 features per sprint. The deploy pipeline takes 4 days; coding takes 2 days; QA takes 6 days. Sprint velocity is blocked by QA.

1. **Identify**: QA queue depth is 3× coding queue depth — QA is the constraint.
2. **Exploit**: pair developers to run QA in parallel; eliminate exploratory retests by introducing automated smoke checks. QA throughput rises from 8 to 11 features without new headcount.
3. **Subordinate**: coding team stops pulling new tickets when QA has > 4 items in queue; deploy pipeline given priority scheduling for QA-cleared builds.
4. **Elevate** (if needed): hire one QA specialist or invest in test automation if steps 2–3 still cap throughput below target.
5. **Repeat**: after elevation, deploy pipeline (now 4 days end-to-end) becomes the new constraint.

## Sources

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press/St. Lucie Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (general TOC-systems reference; 5FS itself is Goldratt's, not a Dettmer-specific chapter)
