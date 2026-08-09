# Primitive: Prerequisite Tree (PRT)

**Source**: Goldratt (1994), *It's Not Luck*; Dettmer 2007, *The Logical Thinking Process* (Prerequisite Tree chapter — verify chapter number against your printing before citing it precisely).

## Definition

The Prerequisite Tree (PRT) is a TOC Thinking Process tool for planning the implementation path from the current state to a complex objective. It surfaces the obstacles that stand in the way and derives the Intermediate Objectives (IOs) needed to overcome them.

**Logic**: Unlike the CRT and FRT (which use sufficiency / "If…Then"), the PRT uses necessity logic: "In order to achieve [Objective], I must first achieve [IO], because [Obstacle] exists."

**Structure**:
- Start from the desired objective (often the top of the FRT).
- Brainstorm every obstacle that could prevent achieving it.
- For each obstacle, define the minimum Intermediate Objective that overcomes it.
- Sequence the IOs: some IOs are prerequisites for others; map the dependency order.

## When to Use

- Implementation planning after a Future Reality Tree (primitive 06) has validated the injection.
- When a goal is clear but the path is not, and resistance or obstacles are anticipated.
- Project planning for multi-team initiatives with interdependencies.
- Onboarding a new capability or process with organizational change risk.

## Inputs

- The injection or objective from the FRT.
- A realistic inventory of obstacles (technical, organizational, resource, political).

## Outputs

- A sequenced list of Intermediate Objectives with their corresponding obstacles.
- A dependency map: which IOs must be completed before others.
- The first IO: the immediate next action with the highest prerequisite burden.

## Failure Modes

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| PRT skipped; team jumps from FRT to action | IOs omitted; project stalls on first obstacle | Always extract at least three obstacle-IO pairs before starting |
| Obstacles stated as IOs | "We need buy-in" is an obstacle, not an IO | IOs are positive achievements: "Buy-in from VP secured" |
| All IOs treated as parallel | Dependencies between IOs ignored | Map IO-to-IO dependencies explicitly |
| Obstacles understated | Optimism bias; obstacles only from easy domains | Include organizational, political, and skill-gap obstacles |
| PRT not updated when new obstacles emerge | Static document not maintained | Treat PRT as a living backlog; review weekly during implementation |

## Worked Example

**Objective**: Introduce weekly constraint-aligned prioritization meeting (from FRT example).

| Obstacle | Intermediate Objective |
|---------|----------------------|
| No one owns the meeting | Assign a named facilitator with authority to enforce the agenda |
| No agreed prioritization criteria | Define and ratify T/CU-based ranking criteria before first meeting |
| Calendar fragmentation — no shared slot | Negotiate a recurring 30-minute slot that all key stakeholders can attend |
| Async pre-read not yet in place | Create a standard pre-read template and assign prep ownership |

**Sequence**: Criteria → Facilitator → Pre-read template → Calendar slot → First meeting.

The PRT reveals that ratifying criteria is the prerequisite for everything else — start there.

## Sources

- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. (Prerequisite Tree chapter; confirm exact number against your printing)
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press.
