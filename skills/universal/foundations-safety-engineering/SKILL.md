---
name: foundations-safety-engineering
description: "Analyzes hazards in systems or AI agents: STPA, guardrails, safety cases, incident analysis. Use when an agent can take actions or send payments."
version: "1.0"
last_validated: 2026-09-27
---

# Safety Engineering Foundations

Derive constraints that prevent unacceptable losses, including losses from interactions between functioning components. Scope the analysis to the requested system and decision; analysis does not authorize external actions.

## When to use

**Use when** a task asks what could go wrong with a system or agent, which guardrails an agent that can take real actions (payments, deletes, deploys, messages) needs, for a hazard analysis or STPA, for a safety case for an AI system, or for an incident analysis that goes beyond one root cause.

For failure rates, repair/availability models, FMEA, and fault-tree probabilities, use [reliability theory](../foundations-reliability-theory/SKILL.md). For proving specified model properties, use [formal methods](../foundations-formal-methods/SKILL.md). Operational incident response and security hardening remain with their existing owners.

## Quick Reference

- **Put guardrails at the mutation boundary.** A prompt instruction feeds the planner's process model. It does not constrain the system.
- **Name the depth.** A reversible, low-impact change gets a single hazard row. Irreversible actions, money movement or delegated authority get full STPA. A decision-maker who must accept residual risk gets a safety case.
- **Standards are pointers.** Name SOTIF, ISO/PAS 8800 or UL 4600 only through the [standards map](references/standards-map.md), and never as evidence of conformance.

## Workflow

1. Define system boundary, stakeholders, lifecycle phase, unacceptable losses, and environmental assumptions. Separate an accident/loss from a hazardous system state. Invert each hazard into a system-level constraint (H → SC). Past about seven to ten system-level hazards, group them and refine later (STPA Handbook rule of thumb).
2. Model controllers, controlled processes, control actions, feedback, and process-model assumptions. Include humans and interacting controllers when relevant.
3. Read [STPA analysis](references/stpa-analysis.md) and examine each action in four categories: omission, unsafe provision, timing/order, and inappropriate duration where applicable.
4. For each unsafe control action (UCA), identify context and hazard; invert it into a controller constraint, make it testable, and assign an owner. Explore stale/missing feedback, flawed process models, conflicting commands, and unsafe execution paths, including functioning components.
5. Fill the [traceability worksheet](assets/templates/safety-traceability.md). Read [assurance and boundaries](references/assurance-and-boundaries.md) before making completion or safety claims. Use the synthetic examples ([rollback](references/completed-example.md), [payment agent](references/agent-stpa-payments.md)) as illustrations, not risk estimates.
6. If an argued case is required, structure it with [safety cases](references/safety-cases.md). For a past incident, run [CAST](references/cast-incident-analysis.md) instead of steps 3–4.

## Completion criteria

Every analyzed UCA links to a hazard and loss, a constraint, and planned or observed verification. Record excluded scenarios, unknowns, residual hazards, owners, and review triggers. A scenario with no test evidence remains a proposed mitigation.

Do not equate uptime with safety, assign fabricated event probabilities, or describe an STPA diagram as proof. This skill provides analysis and assurance structure; it does not certify compliance, establish acceptable risk, or grant approval authority. Respect authorization already supplied and identify any specific additional action requiring authorization without creating universal approval loops.

## Navigation

- [STPA analysis](references/stpa-analysis.md) — four categories and loss-scenario derivation.
- [Assurance and boundaries](references/assurance-and-boundaries.md) — evidence and limits.
- [Completed example](references/completed-example.md) — synthetic rollback interaction.
- [Agent STPA: payments](references/agent-stpa-payments.md) — read when an LLM agent can take irreversible actions; worked losses → UCAs → guardrail → bypass test.
- [Safety cases](references/safety-cases.md) — read when someone needs an argued case: CAE/GSN, defeaters, frontier-AI argument families.
- [CAST incident analysis](references/cast-incident-analysis.md) — read for a post-incident analysis beyond root cause.
- [Safety-II, resilience, STAMP](references/safety-ii-and-stamp.md) — read when failures come from normal work variability or "worked as designed".
- [Standards map](references/standards-map.md) — read before naming SOTIF, ISO/PAS 8800, or UL 4600; pointers only.
- [Traceability worksheet](assets/templates/safety-traceability.md) — output artifact.
- [Formal methods](../foundations-formal-methods/SKILL.md) — read when a control constraint must be checked over a protocol model (invariants, counterexamples), not only argued.
- [Dated primary sources](data/sources.json) — verified source and cutoff.
