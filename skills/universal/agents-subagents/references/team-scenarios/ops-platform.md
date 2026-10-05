---
description: Ops Platform — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Ops Platform

**Typical scenario**

Your platform feels expensive, brittle, and slower to ship than it should be.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "ops-platform"`.

Scenario: Review the current deployment and platform setup because CI is slow, runtime visibility is weak, incidents take too long to diagnose, and infrastructure cost has climbed.

Required context:
- deployment model, incident pain, and cost concern
- optional artifacts: bills, logs, traces, SLO notes

Instructions:
- ops-platform-engineer reviews the platform operating model
- ops-cost-optimizer reviews waste and right-sizing opportunities
- qa-observability-lead reviews telemetry quality and missing signal
- qa-resilience-reviewer reviews failure handling and reliability posture
- Blind memos first, then one chaired synthesis of the platform-improvement plan
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn platform_engineer, cost_optimizer, observability_lead, and resilience_reviewer.

Task: review the platform because delivery is slow, visibility is weak, incidents are painful, and cost is rising.

Return:
- platform changes worth making first
- safe cost reductions
- main telemetry and resilience gaps
- rollout order
```

**Debate-first variant**

Use when the disagreement is "simplify platform aggressively" versus "keep current control and optimize incrementally."
