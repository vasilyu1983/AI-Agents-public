# DevOps Best Practices

*Purpose: Operational guidance for safe, efficient, and auditable infrastructure automation, deployment, and reliability engineering in cloud-native environments.*

---

## Core Patterns

### Pattern 1: Safe Infrastructure Changes

**Use when:** Managing production changes with Infrastructure as Code (Terraform, CloudFormation, etc.)

**Structure:**
```

1. Write and test changes in a feature branch.
2. Run automated `terraform plan`/`cloudformation validate` in CI.
3. Require pull request review from a peer or SRE.
4. Apply changes via CI/CD runner with restricted credentials.
5. Record all changes (logs, plan/apply diffs) in version control or audit logs.

```

**Checklist:**
- [ ] Infrastructure code in version control
- [ ] Peer review required before merge
- [ ] Automated validation in pipeline
- [ ] Change is tracked and auditable
- [ ] Sensitive credentials managed via secrets backend

---

### Pattern 2: Blue-Green & Canary Deployments

**Use when:** Deploying applications/services with minimal user impact

**Structure:**
```

1. Deploy new version (green) alongside current (blue).
2. Run health checks on green.
3. Shift small % of traffic to green (canary phase).
4. Monitor SLOs, logs, errors for N minutes.
5. If healthy, route all traffic to green; otherwise, rollback.

```

**Checklist:**
- [ ] Parallel environments provisioned
- [ ] Automated health and readiness checks
- [ ] Metrics/alerts active during rollout
- [ ] Rollback plan in place and tested

---

### Pattern 3: Incident Response Escalation

**Use when:** Responding to production alerts, outages, or service degradation

**Structure:**
```

1. On-call receives and acknowledges alert (5 min SLA)
2. Assess impact (severity, affected users, systems)
3. Page escalation (SRE, Dev, Management as needed)
4. Initiate incident comms (status page, stakeholders)
5. Follow incident runbook for triage and resolution
6. Begin postmortem process if SEV-1/SEV-2

```

**Checklist:**
- [ ] On-call rotation documented and tested
- [ ] Escalation contacts up-to-date
- [ ] Incident comms template ready
- [ ] Postmortem template in use
- [ ] Blameless review process

---

## Decision Matrices

| Situation                | Approach                   | Validation                |
|--------------------------|----------------------------|---------------------------|
| Major change (prod)      | Peer review, CI plan, canary| Plan reviewed, logs checked|
| Minor change (dev/stage) | Auto-apply in pipeline      | Automated tests pass       |
| Alert: non-critical      | Wait for next standup       | Ack'd in incident tracker  |
| Alert: critical/SEV-1    | Page on-call, escalate      | Response time < SLA, issue tracked |

---

## Common Anti-Patterns

- AVOID: Direct change to production (no review)  
  - Risk of accidental outage, no audit trail.  
  - BEST: All production changes via code, review, and CI/CD.

- AVOID: Overprivileged CI/CD runners  
  - Attack surface for credentials or data exfiltration.  
  - BEST: Least-privilege roles, rotate tokens, no human secrets in code.

- AVOID: No automated rollbacks  
  - Manual errors and slow recovery.  
  - BEST: Scripts and runbooks for automated rollback tested regularly.

- AVOID: No post-incident analysis  
  - Repeat failures, lack of learning.  
  - BEST: Schedule blameless postmortems after every major incident.

---

## Quick Reference

### Pre-Deployment Checklist

- [ ] All infra/app code in version control
- [ ] Changes reviewed and approved
- [ ] Automated test suite passes
- [ ] Rollback script/runbook ready
- [ ] Health checks defined and monitored
- [ ] Stakeholders notified if high-risk

### CI/CD Best Practices

- Use immutable build artifacts
- Store pipeline configs as code (e.g., `.github/workflows/`, `.gitlab-ci.yml`)
- Tag and version every release
- Enforce secrets scanning on push
- Auto-expire old build credentials

---

## Edge Cases & Fallbacks

- If CI/CD pipeline fails: Block deploy, alert owner, require manual approval for override.
- If blue-green rollout fails: Roll traffic fully back to stable ("blue") env, auto-notify team.
- If incident detection tools down: Enable fallback monitoring (infra, external uptime checker), escalate to SRE lead.

---

## Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns in DevOps automation, reference these centralized utilities:

- [config-validation.md](../../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+, secrets management (1Password, Doppler, Vault)
- [resilience-utilities.md](../../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, circuit breaker, OTel spans for service health
- [logging-utilities.md](../../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry integration for structured logging
- [observability-utilities.md](../../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics for infrastructure monitoring
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) — Test factories, fixtures for infrastructure tests

---

*This guide focuses on safe, auditable, and high-velocity DevOps operations. All practices are actionable and ready for direct use in cloud-native teams.*
