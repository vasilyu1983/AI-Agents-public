---
description: Incident Response — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Incident Response

**Typical scenario**

You need fast triage plus a remediation strategy for a production outage or severe regression.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "incident"`.

Scenario: Checkout success rate dropped sharply after the last deploy. Users can begin checkout but many payments fail before confirmation.

Required context:
- Symptoms, timeline, impacted services
- Optional context: logs, traces, dashboards, and recent deploy history

Instructions:
- ops-incident-commander owns triage flow, hypotheses, and final incident summary
- qa-debugger traces likely failure points in code and recent changes
- qa-observability-lead inspects logs, traces, and metrics for failure signatures
- qa-resilience-reviewer evaluates rollback, containment, and guardrail options
- Run the first analysis round in parallel
- ops-incident-commander synthesizes likely root cause, immediate next action, and evidence gaps
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for incident command, debugging, observability, and resilience.

Incident:
- checkout success rate dropped after the last deploy
- users can start checkout but many fail before confirmation

Rules:
- first analysis round runs in parallel
- qa-debugger focuses on code and recent changes
- observability_lead focuses on logs, traces, and metrics
- resilience_reviewer focuses on rollback, containment, and mitigation
- incident_commander synthesizes the likely root cause and immediate action

Wait for all workers, then produce:
- most likely failure chain
- confidence level
- immediate action recommendation
- missing evidence to confirm it
```

**Debate-first variant**

Use debate when the real choice is rollback now versus fix forward behind a mitigation.
