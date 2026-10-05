# Operational Patterns and Standards

*Use when:* You need a fast safety gate or a routing index before loading a deeper reference file.

## Table of Contents
- Core standards
- Quick safety gates
- Reference routing

---

## Core Standards

- **GitOps first:** Git is the source of truth for steady-state cluster and application configuration. Use PR review, branch protection, and controller reconciliation instead of manual production applies.
- **Review-first IaC:** Infrastructure changes should produce a plan artifact, pass automated checks, and apply through a restricted CI runner with auditable logs.
- **Observability baseline:** OpenTelemetry is the telemetry standard; pair it with Prometheus/Grafana or a vendor suite, then add tracing/runtime tools only when the problem justifies them.
- **Platform engineering baseline:** Prefer golden paths with escape hatches, policy guardrails, and observable defaults rather than ticket-driven operations or black-box abstractions.
- **Incident response baseline:** Every SEV-1/SEV-2 needs an incident commander, explicit communications ownership, rollback/fix validation, and a blameless postmortem.
- **Cost and capacity baseline:** Tag resources early, set budgets before spend spikes, define autoscaling assumptions, and review right-sizing and error-budget signals on a regular cadence.

---

## Quick Safety Gates

### Before a Production Change

- [ ] Change is in version control with peer review
- [ ] Validation passed in CI and generated an auditable artifact
- [ ] Rollback or revert path is documented and tested
- [ ] Identity is short-lived or federated (OIDC/WIF), not a long-lived shared secret
- [ ] Health checks, smoke tests, and rollout verification are defined

### Before Incident Closure

- [ ] Metrics, logs, and traces returned to expected levels
- [ ] Customer-facing communication is updated or closed
- [ ] Follow-up work is captured with owners and due dates
- [ ] The postmortem is scheduled or already underway

---

## Reference Routing

- For production change control, rollout safety, and deployment checklists, read [devops-best-practices.md](devops-best-practices.md).
- For GitOps controllers, reconciliation, promotion, and progressive delivery, read [gitops-workflows.md](gitops-workflows.md).
- For internal developer portals, golden paths, and policy-driven platforms, read [platform-engineering-patterns.md](platform-engineering-patterns.md).
- For paging, incident roles, escalation ladders, and postmortems, read [sre-incident-management.md](sre-incident-management.md).
- For current tool comparisons across IaC, CI/CD, platform engineering, observability, security, and streaming, read [tool-landscape.md](tool-landscape.md).

---

This file is intentionally short. Use it as the routing and standards layer, not as a second deep-dive guide.
