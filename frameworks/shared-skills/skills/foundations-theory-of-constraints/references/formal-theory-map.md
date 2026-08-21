---
description: Formal theory map for Theory of Constraints foundations. Use to distinguish system constraints, policy constraints, and generic bottlenecks.
last_verified: 2026-08-14
status: stable
---

# Theory of Constraints Formal Theory Map

## Purpose

Use this map when a TOC recommendation needs a boundary between throughput constraint logic, scheduling practice, financial measurement, and Thinking Process diagrams.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Constraint focus | System goal, throughput limiter, exploitation/subordination | Five Focusing Steps | Constraint changes after improvement |
| Flow synchronization | Drum, buffer, rope, WIP release | DBR and S-DBR | Requires observable flow and buffer signals |
| Throughput accounting | Throughput, inventory, operating expense, T/CU | Product mix and investment decisions | Not a replacement for statutory accounting |
| Conflict resolution | Need, prerequisite, assumption, injection | Evaporating Cloud | Logic quality depends on assumption checks |
| Cause-effect logic | UDEs, core problem, injections, negative branches | CRT and FRT | Diagrams can encode false causal links |
| Execution logic | Obstacles, intermediate objectives, actions, expected effects | PRT and TT | Needs observable completion criteria |
| Project constraint management | Critical chain, project buffer, feeding buffers | CCPM | Buffer rules must be enforced operationally |
| Policy constraints | Rules, metrics, approvals, incentives | Invisible constraints | Policy diagnosis needs stakeholder evidence |

## CRT + System Dynamics (Multi-Causal Constraint Scenarios)

When multiple interacting UDEs resist single-root CRT analysis — particularly in complex multi-stakeholder environments — combine CRT with qualitative system dynamics (Qual SD) modeling. Mabin, V.J. & Cavana, R.Y. (2024), "A framework for using Theory of Constraints thinking processes and tools to complement qualitative system dynamics modelling", *System Dynamics Review* 40(4), e1768, DOI 10.1002/sdr.1768, propose a six-stage integration framework and argue the combination produces more collective insight than either method alone. Apply when: (1) more than three UDEs connect through feedback loops rather than simple chains, or (2) stakeholders disagree on cause arrows because the system has genuine circular causality. Bibliographic metadata verified via Crossref 2026-08-14; full text is paywalled, so the framework's claimed advantage is reported from the abstract and has not been independently assessed here.

## Relationship to Kanban and DevOps Flow

TOC is not a competitor to Kanban — the modern Kanban Method (David J. Anderson, mid-2000s onward) explicitly draws on TOC constraint logic: Kanban's WIP limits function as a rope, and "identify the bottleneck, exploit it, elevate it" is presented in Kanban literature as a direct application of 5FS. The practical distinction that matters for advising a team:

- **Kanban's default posture** treats the system as a balanced line regulated by WIP limits at every column; when any column is disrupted beyond its buffer, the whole board waits.
- **TOC/DBR's default posture** subordinates every step to a single named drum; only the drum's health determines whether the system is in danger, not every column's.
- In practice, most Kanban boards used in software teams are an *approximation* of DBR without an explicitly named drum — which is why a team can run Kanban for months without knowing where its actual constraint is. Overlaying 5FS (name the constraint explicitly) onto an existing Kanban board is a common, low-cost intervention: keep the WIP limits, add an explicit drum designation and a buffer-health metric at that one column.
- DevOps flow frameworks (Kim et al.'s *The Phoenix Project* / *DevOps Handbook* "First Way," Kersten's Flow Framework) are the industry-standard bridge translating this TOC-Kanban relationship into software delivery value streams; see `data/sources.json` for full citations.

This is a stable, well-documented relationship, not a novel 2026 claim — flag it for a user only when a team conflates "we run Kanban" with "we know our constraint," which is the common failure mode.

## Production Rule

Do not call a bottleneck a TOC constraint until it is tied to the system goal and current throughput limit. Every TOC intervention must identify the constraint, the exploitation move, the subordination rule, and the signal proving throughput improved.
