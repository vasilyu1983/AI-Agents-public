---
description: Feature Dev — extracted from monolith for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Feature Dev

**Typical scenario**

You need a staged team for a medium-risk feature that touches existing flows.

**Claude prompt**

```text
Create an agent team using the installed `dev-feature-delivery` members.

Scenario: Add team-level API keys to the billing admin panel so admins can create, rotate, and revoke keys with audit logging.

Required context:
- Acceptance criteria for key creation, rotation, revocation, and audit visibility
- Repo target: current project
- Optional artifacts if present: profiles/*.json, graphs/code-graph.json, reports/query-*.md

Instructions:
- dev-feature-researcher goes first and maps the relevant modules, constraints, and existing auth/audit patterns
- dev-feature-implementer works only after the research handoff is complete
- dev-feature-reviewer validates the implementation and calls out gaps before final synthesis
- Keep the workflow staged, not parallel
- Return research notes, implementation summary, review findings, and any follow-up fixes still needed
- Clean up the team when done
```

**Codex prompt**

```text
Run the installed feature_dev members as a staged pipeline.

Step 1:
- spawn feature_researcher
- task: map the code paths, models, and constraints for adding team-level API keys with audit logging
- prefer context artifacts first if available

Step 2:
- after the researcher finishes, spawn feature_implementer
- task: implement the feature using the research output as read-only context

Step 3:
- after implementation, spawn feature_reviewer
- task: review the resulting change for correctness, regression risk, and missing tests

Finish by synthesizing the pipeline output into:
- what changed
- what still needs work
- whether the feature is ready for merge
```
