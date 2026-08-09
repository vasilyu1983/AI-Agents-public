# Theory of Constraints Primitives — Composition Guide

11 domain-agnostic TOC primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Core Question It Answers |
|---|------|--------------------------|
| 1 | [01-five-focusing-steps.md](01-five-focusing-steps.md) | Where should all improvement energy go? |
| 2 | [02-drum-buffer-rope.md](02-drum-buffer-rope.md) | How do we schedule flow around the constraint? |
| 3 | [03-throughput-accounting.md](03-throughput-accounting.md) | How do we measure and decide using T, I, OE? |
| 4 | [04-evaporating-cloud.md](04-evaporating-cloud.md) | How do we dissolve a conflict without compromise? |
| 5 | [05-current-reality-tree.md](05-current-reality-tree.md) | What is the root cause of our undesirable effects? |
| 6 | [06-future-reality-tree.md](06-future-reality-tree.md) | Will our proposed injection actually fix the problem? |
| 7 | [07-prerequisite-tree.md](07-prerequisite-tree.md) | What intermediate objectives must we achieve first? |
| 8 | [08-transition-tree.md](08-transition-tree.md) | What specific actions, in what order, with what logic? |
| 9 | [09-critical-chain.md](09-critical-chain.md) | How do we schedule projects to prevent buffer misuse? |
| 10 | [10-policy-constraints.md](10-policy-constraints.md) | Is the constraint a rule or metric, not a resource? |
| 11 | [11-thinking-processes.md](11-thinking-processes.md) | Which TP tools do I need for my situation? |

---

## Composition Scenarios

### Roadmap Re-Prioritization

- **Objective**: rank work by impact on system throughput, not by team preference or stakeholder volume.
- **Stack**: [01-five-focusing-steps.md](01-five-focusing-steps.md) (identify constraint) + [03-throughput-accounting.md](03-throughput-accounting.md) (rank by T/CU) + [10-policy-constraints.md](10-policy-constraints.md) (check whether constraints are policy-driven)
- **Add if conflict over priority**: [04-evaporating-cloud.md](04-evaporating-cloud.md)

### Incident-Mode Flow Restoration

- **Objective**: restore throughput in a degraded or overloaded system without adding headcount.
- **Stack**: [02-drum-buffer-rope.md](02-drum-buffer-rope.md) (synchronize flow around the constraint) + buffer management (color-coded status: green/yellow/red) + [01-five-focusing-steps.md](01-five-focusing-steps.md) (exploit before elevating)

### Policy Debugging

- **Objective**: diagnose why throughput is not improving despite adequate capacity.
- **Stack**: [05-current-reality-tree.md](05-current-reality-tree.md) (trace UDEs to root cause) + [04-evaporating-cloud.md](04-evaporating-cloud.md) (dissolve the conflict sustaining the policy) + [06-future-reality-tree.md](06-future-reality-tree.md) (validate the policy change injection)

### Strategy Deployment (Full TP Sequence)

- **Objective**: design and implement a strategic change from diagnosis to execution.
- **Stack**: [05-current-reality-tree.md](05-current-reality-tree.md) → [04-evaporating-cloud.md](04-evaporating-cloud.md) → [06-future-reality-tree.md](06-future-reality-tree.md) → [07-prerequisite-tree.md](07-prerequisite-tree.md) → [08-transition-tree.md](08-transition-tree.md)

### Project Delivery Acceleration

- **Objective**: reduce project delivery time and late-finish rate without adding headcount.
- **Stack**: [09-critical-chain.md](09-critical-chain.md) (restructure scheduling and buffer placement) + [01-five-focusing-steps.md](01-five-focusing-steps.md) (identify the resource constraint in the project)
- **Add if approval process is the constraint**: [10-policy-constraints.md](10-policy-constraints.md)

### Financial Decision Under Constraint

- **Objective**: make a product mix, pricing, or investment decision that maximizes throughput.
- **Stack**: [03-throughput-accounting.md](03-throughput-accounting.md) (T/CU ranking) + [01-five-focusing-steps.md](01-five-focusing-steps.md) (confirm which resource is the constraint before ranking)

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — decision checklist, anti-patterns, full primitive index
