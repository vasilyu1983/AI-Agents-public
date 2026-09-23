---
name: foundations-safety-engineering
description: Analyze system hazards and unsafe interactions. Use when assessing STPA, unsafe control actions, safety constraints, loss scenarios, or assurance traceability.
version: "1.0"
last_validated: 2026-09-17
---

# Safety Engineering Foundations

Derive constraints that prevent unacceptable losses, including losses from interactions between functioning components. Scope the analysis to the requested system and decision; analysis does not authorize external actions.

## When to use

**Use when** a task requests hazard analysis, STPA, unsafe control actions, system safety constraints, or an evidence argument connecting controls to prevention of specified losses.

For failure rates, repair/availability models, FMEA, and fault-tree probabilities, use [reliability theory](../foundations-reliability-theory/SKILL.md). For proving specified model properties, use [formal methods](../foundations-formal-methods/SKILL.md). Operational incident response and security hardening remain with their existing owners.

## Quick Reference

Hazard analysis → STPA reference; completion claims → assurance reference; deliverable → traceability worksheet.

## Workflow

1. Define system boundary, stakeholders, lifecycle phase, unacceptable losses, and environmental assumptions. Separate an accident/loss from a hazardous system state.
2. Model controllers, controlled processes, control actions, feedback, and process-model assumptions. Include humans and interacting controllers when relevant.
3. Read [STPA analysis](references/stpa-analysis.md) and examine each action in four categories: omission, unsafe provision, timing/order, and inappropriate duration where applicable.
4. For each unsafe control action (UCA), identify context and hazard; derive a testable constraint and assign an owner. Explore stale/missing feedback, flawed process models, conflicting commands, and unsafe execution paths, including functioning components.
5. Fill the [traceability worksheet](assets/templates/safety-traceability.md). Read [assurance and boundaries](references/assurance-and-boundaries.md) before making completion or safety claims. Use the [synthetic example](references/completed-example.md) as an illustration, not a risk estimate.

## Completion criteria

Every analyzed UCA links to a hazard and loss, a constraint, and planned or observed verification. Record excluded scenarios, unknowns, residual hazards, owners, and review triggers. A scenario with no test evidence remains a proposed mitigation.

Do not equate uptime with safety, assign fabricated event probabilities, or describe an STPA diagram as proof. This skill provides analysis and assurance structure; it does not certify compliance, establish acceptable risk, or grant approval authority. Respect authorization already supplied and identify any specific additional action requiring authorization without creating universal approval loops.

## Fact-Checking

Use the dated primary source for method claims and system-specific evidence for effectiveness claims. Keep synthetic scenarios separate from observed incidents. Verify later method or system changes before describing them as current.

## Navigation

- [STPA analysis](references/stpa-analysis.md) — four categories and loss-scenario derivation.
- [Assurance and boundaries](references/assurance-and-boundaries.md) — evidence and limits.
- [Completed example](references/completed-example.md) — synthetic rollback interaction.
- [Traceability worksheet](assets/templates/safety-traceability.md) — output artifact.
- [Dated primary sources](data/sources.json) — verified source and cutoff.
