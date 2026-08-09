# Work Item Ticket Template (DoR/DoD + Acceptance Criteria)

Copy-paste into Jira/Linear/GitHub Issues to make work scannable, testable, and releasable.

---

## Core

### Summary

- Title:
- Type: feature / bug / tech debt / spike
- Owner:
- Priority:
- Milestone/Sprint:
- Stakeholders:

### Problem Statement

- What is broken or missing?
- Who is impacted?
- Why now?

### Scope

- In scope:
- Out of scope:

### Context / Links

- PRD/RFC:
- Designs:
- Logs/metrics:
- Related tickets:

### Acceptance Criteria (Required)

Pick one style and keep it testable.

Option A: checklist

- [ ] AC1:
- [ ] AC2:
- [ ] AC3:

Option B: Given/When/Then

```gherkin
Scenario: ...
  Given ...
  When ...
  Then ...
```

### Definition of Ready (Gate to Start)

Use the checklist and don't start until it's satisfied:

- [ ] DoR complete (see `assets/template-dor-dod.md`)
- [ ] Dependencies identified and unblocked
- [ ] Security/privacy considerations captured (PII/PHI/PCI, auth scope)
- [ ] Operability requirements captured (logging/metrics/tracing, alerts, runbook impact)
- [ ] Rollout strategy chosen (flag, canary, staged)

### Definition of Done (Gate to Close)

- [ ] DoD complete (see `assets/template-dor-dod.md`)
- [ ] Tests added/updated (unit + integration as applicable)
- [ ] Observability updated (dashboards/alerts if needed)
- [ ] Docs updated (public/internal)
- [ ] Rollback plan documented

### Implementation Plan (Tasks)

- [ ] Task 1:
- [ ] Task 2:
- [ ] Task 3:

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
|  |  |  |  |

### Validation Plan

- How will we verify in staging?
- What metrics/SLOs are expected to move?
- What is the rollback trigger?

---

## Optional: AI/Automation

- Draft acceptance criteria from the problem statement (human-reviewed)
- Suggest task breakdown and dependencies (human-validated)
- Produce a test plan outline and rollout checklist (human-owned)

### Bounded Claims

- AI drafts can miss edge cases and operational constraints.
- Priorities and trade-offs require team calibration.
