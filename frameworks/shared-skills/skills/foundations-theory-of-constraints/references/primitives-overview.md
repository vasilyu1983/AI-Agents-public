---
description: Domain-agnostic overview of 11 TOC primitives — five focusing steps, drum-buffer-rope, throughput accounting, evaporating cloud, current/future reality trees, prerequisite and transition trees, critical chain, policy constraints, and thinking processes.
last_verified: 2026-05-02
status: stable
---

# Theory of Constraints Primitives Overview

## Table of Contents

- [Why TOC Works](#why-toc-works)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why TOC Works

Every system has exactly one constraint at any given time — the step, rule, or resource that limits total output. Improving anything else increases local efficiency without increasing system throughput. TOC works because it refuses to let attention scatter: all improvement energy goes to the constraint, and only to the constraint, until it is broken and a new one emerges.

| Failure Mode | TOC Diagnosis | What Goes Wrong Without TOC |
|-------------|--------------|---------------------------|
| Local optimization everywhere | Constraint invisible; every team improves their own step | Throughput flat; costs rise; morale falls as effort yields no output |
| Throughput plateau despite investment | Physical constraint elevated before policy constraint identified | New capacity immediately throttled by the unchanged policy |
| Projects chronically late | Individual task padding hoarded; no shared buffer | Student syndrome and Parkinson's Law consume all safety |
| Recurring conflicts between teams | Conflict sustained by an invalid assumption | Endless negotiation; no resolution; symptoms recur |
| Roadmap driven by stakeholder pressure | No T/CU ranking; work not sequenced by throughput impact | Low-value work crowds out high-leverage items |

---

## Primitive Index

11 primitives, each in its own playbook under [`../assets/templates/theory-of-constraints/`](../assets/templates/theory-of-constraints/).

| # | Primitive | Failure Mode It Addresses | Primary Domains |
|---|-----------|--------------------------|-----------------|
| 1 | [Five Focusing Steps](../assets/templates/theory-of-constraints/01-five-focusing-steps.md) | Improvement energy scattered across non-constraints | All domains — universal entry point |
| 2 | [Drum-Buffer-Rope](../assets/templates/theory-of-constraints/02-drum-buffer-rope.md) | WIP floods system; constraint starves | Production, software delivery, ops, incident response |
| 3 | [Throughput Accounting](../assets/templates/theory-of-constraints/03-throughput-accounting.md) | Cost-accounting bias drives local optimization | Product mix, pricing, roadmap prioritization |
| 4 | [Evaporating Cloud](../assets/templates/theory-of-constraints/04-evaporating-cloud.md) | Conflict resolved by compromise; invalid assumption unchallenged | Team conflicts, strategy debates, policy decisions |
| 5 | [Current Reality Tree](../assets/templates/theory-of-constraints/05-current-reality-tree.md) | Root cause misidentified; symptoms treated repeatedly | Root-cause analysis, incident post-mortems, org diagnosis |
| 6 | [Future Reality Tree](../assets/templates/theory-of-constraints/06-future-reality-tree.md) | Solution untested; side effects unexpected | Strategy design, change management, product planning |
| 7 | [Prerequisite Tree](../assets/templates/theory-of-constraints/07-prerequisite-tree.md) | Implementation stalls on unacknowledged obstacles | Project planning, organizational change, OKR execution |
| 8 | [Transition Tree](../assets/templates/theory-of-constraints/08-transition-tree.md) | Action plan has no explicit logic connecting steps | Task-level execution, change management, onboarding |
| 9 | [Critical Chain](../assets/templates/theory-of-constraints/09-critical-chain.md) | Projects late despite individual tasks on-time | Software delivery, product launches, cross-team projects |
| 10 | [Policy Constraints](../assets/templates/theory-of-constraints/10-policy-constraints.md) | Throughput capped by rules/metrics, not capacity | Knowledge work, service ops, compliance-heavy environments |
| 11 | [Thinking Processes](../assets/templates/theory-of-constraints/11-thinking-processes.md) | Wrong TP tool chosen for the situation | Any TOC application — tool-selection guide |

---

## Anti-Patterns by Domain

### Software Delivery / Engineering

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| Improving the non-bottleneck team | 5FS violated — energy on non-constraint | Identify constraint first; freeze non-constraint improvements |
| Adding engineers to a policy-constrained pipeline | Physical elevation before policy constraint resolved | Audit approval gates and deploy policies before hiring |
| Tracking milestone dates, not buffer health | Critical path thinking in a CCPM project | Switch to buffer consumption reporting |

### Product / Roadmap

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| Features ranked by stakeholder volume | No T/CU ranking; constraint ignored | Rank by Throughput per Constraint Unit |
| Shipping everything to everyone | Product mix not optimized | T/CU product mix analysis; drop or defer low-T/CU items |
| Strategy blocked by an unresolved conflict | Evaporating Cloud not applied | Build the cloud; challenge the assumption sustaining the conflict |

### Operations / Incident Response

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| On-call team flooded with intake | No rope; new work enters regardless of constraint load | Apply DBR rope: freeze intake when on-call queue exceeds threshold |
| Buffer managed as inventory, not time | Misapplied DBR | Enforce "buffer = time slot," not "buffer = extra tasks" |
| Recurring incidents traced to the same root cause | CRT never built; symptoms patched not causes | Build a CRT from the last five post-mortem UDEs |

### Projects / Change Management

| Anti-Pattern | TOC Diagnosis | Fix |
|-------------|--------------|-----|
| Projects late despite individual tasks "on time" | Student syndrome and Parkinson's Law unchecked | Apply CCPM: strip individual padding, pool into Project Buffer |
| Change initiative stalls mid-implementation | PRT not built; obstacles unacknowledged | Build the PRT before starting; surface every obstacle |
| Action plan has no logic connecting steps | Transition Tree not used | Add "need" and "effect" to every action |

---

## Decision Checklist

- [ ] **Where to focus**: Is the constraint identified? → Five Focusing Steps (#1)
- [ ] **Flow scheduling**: Is WIP flooding a step? → Drum-Buffer-Rope (#2)
- [ ] **Financial decision**: Is the decision being made on margin instead of T/CU? → Throughput Accounting (#3)
- [ ] **Conflict resolution**: Is a team deadlocked on two seemingly incompatible actions? → Evaporating Cloud (#4)
- [ ] **Root cause**: Are multiple UDEs present with no shared explanation? → Current Reality Tree (#5)
- [ ] **Solution design**: Is a proposed change untested for side effects? → Future Reality Tree (#6)
- [ ] **Implementation planning**: Are obstacles standing in the way of an agreed injection? → Prerequisite Tree (#7)
- [ ] **Action planning**: Are steps unclear or unlogically connected? → Transition Tree (#8)
- [ ] **Project scheduling**: Is a project chronically late despite task-level effort? → Critical Chain (#9)
- [ ] **Invisible constraint**: Is throughput not improving despite available capacity? → Policy Constraints (#10)
- [ ] **Tool selection**: Unsure which TP tool to use? → Thinking Processes overview (#11)

---

## Sources

Primary books and references for all 11 primitives:

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press.
- Goldratt, E.M. & Fox, R.E. (1986). *The Race*. North River Press.
- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press.
- Goldratt, E.M. (1994). *It's Not Luck*. North River Press.
- Goldratt, E.M. (1997). *Critical Chain*. North River Press.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press/St. Lucie Press.
- Corbett, T. (1998). *Throughput Accounting*. North River Press.
- Newbold, R.C. (1998). *Project Management in the Fast Lane*. St. Lucie Press.
- Scheinkopf, L.J. (1999). *Thinking for a Change*. CRC Press.
- Leach, L.P. (2000). *Critical Chain Project Management*. Artech House.
- Schragenheim, E. & Dettmer, H.W. (2001). *Manufacturing at Warp Speed*. CRC Press.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press.
- Schragenheim, E., Dettmer, H.W. & Patterson, J.W. (2009). *Supply Chain Management at Warp Speed*. CRC Press.
