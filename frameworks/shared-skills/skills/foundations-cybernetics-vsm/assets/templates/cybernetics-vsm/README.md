# Cybernetics and VSM Primitives — Composition Guide

11 domain-agnostic cybernetics and VSM primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-feedback-loops.md](01-feedback-loops.md) | Runaway growth or oscillation from unchecked dynamics |
| 2 | [02-ashbys-law.md](02-ashbys-law.md) | Control collapse when environmental variety exceeds controller capacity |
| 3 | [03-vsm-system-1.md](03-vsm-system-1.md) | Centralised execution bottleneck; no operational autonomy |
| 4 | [04-vsm-system-2.md](04-vsm-system-2.md) | Thrashing and interference between operational units |
| 5 | [05-vsm-system-3.md](05-vsm-system-3.md) | Local optima divergence; S1 units optimise against each other |
| 6 | [06-vsm-system-3-star.md](06-vsm-system-3-star.md) | S2/S3 filters distort ground truth before it reaches management |
| 7 | [07-vsm-system-4.md](07-vsm-system-4.md) | Strategy-execution gap; S3 unaware of environment shifts |
| 8 | [08-vsm-system-5.md](08-vsm-system-5.md) | Identity crisis or policy vacuum; S3/S4 conflict never resolved |
| 9 | [09-recursion-levels.md](09-recursion-levels.md) | Applying VSM at wrong scale; mismatch of model and organisation |
| 10 | [10-variety-engineering.md](10-variety-engineering.md) | Management overload or information starvation from unbalanced variety |
| 11 | [11-algedonic-channels.md](11-algedonic-channels.md) | Crisis hidden by normal reporting hierarchy until it is too late |

---

## Domain Scenario Stacks

### Agent-Team Topology Audit

- **Objective**: verify that an agent hierarchy is viable and identify failure points before deployment.
- **Stack**: #3 (S1 — verify agent autonomy and scope) + #4 (S2 — check for coordination between agents) + #5 (S3 — confirm orchestrator has policy not execution role) + #2 (Ashby — audit controller variety) + #10 (variety engineering — design attenuation if orchestrator overloaded) + #11 (algedonic — ensure critical failures bypass orchestrator to human)
- **Add if recursive hierarchy**: #9 (recursion levels — assign VSM roles at each nesting level)

### Startup Operating System

- **Objective**: design a lightweight governance model that scales without creating command bottlenecks.
- **Stack**: #9 (recursion — choose 2–3 levels) + #3 (S1 — define squad autonomy) + #6 (S3* — spot-check mechanism for founders) + #7 (S4 — assign environmental scanning) + #8 (S5 — write identity document) + #1 (feedback loops — one per key performance variable)
- **Add for platform bottleneck**: #2 (Ashby audit) + #10 (variety engineering — self-service amplifiers)

### Incident Escalation Design

- **Objective**: build a production incident response system that reaches decision authority before damage is severe.
- **Stack**: #11 (algedonic — trigger threshold + direct route to S5) + #8 (S5 — define who holds ultimate authority for incident decisions) + #1 (feedback loop — balancing loop: alert → diagnose → remediate → verify) + #6 (S3* — use post-mortem as ground truth audit) + #10 (variety engineering — ensure dashboards attenuate noise, surface deviation only)

### Platform Team Scaling

- **Objective**: prevent a platform team from becoming a bottleneck as consumer demand grows.
- **Stack**: #2 (Ashby — measure platform team's variety vs. consumer demand variety) + #10 (variety engineering — self-service APIs amplify platform variety; request templates attenuate demand variety) + #4 (S2 — add coordination between consuming teams to prevent conflicting requests) + #5 (S3 — platform policy layer, not per-request approval) + #1 (feedback loops — lead time and consumer satisfaction as balancing goals)

### Organisational Redesign After Rapid Growth

- **Objective**: restore viability after headcount growth has broken informal coordination.
- **Stack**: #9 (recursion — re-identify levels for current size) + #4 (S2 — install formal coordination between units that previously self-coordinated informally) + #5 (S3 — formalise resource allocation and accountability agreements) + #7 (S4 — ensure someone still owns environmental scanning; do not let growth absorb it) + #8 (S5 — restate identity now that company has changed shape)
- **Add for cascading conflicts**: #11 (algedonic — install crisis bypass before the next incident)

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — domain-agnostic overview, anti-patterns, and decision checklist
- [`../../../data/sources.json`](../../../data/sources.json) — primary sources
