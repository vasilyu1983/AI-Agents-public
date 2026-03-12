# DevOps Platform Runbook Starter

Use this template to create consistent, actionable runbooks for on-call engineers.

---

## Core

## Service Overview

- Service/system name:
- Owner team:
- On-call rotation:
- Primary region(s)/environment(s):
- Dependencies (DB, cache, queue, third parties):
- Critical user journeys:

## SLOs and Safety Limits

- SLO targets (latency, availability, freshness where applicable):
- Error budget policy (paging thresholds, burn-rate alerts):
- Data sensitivity (PII/PHI/PCI): yes/no (notes):

## Standard Checks (First 5 Minutes)

- [ ] Confirm scope: single tenant vs all tenants, single region vs global
- [ ] Check recent changes (deploys/config/infra) in the last 60 minutes
- [ ] Check dashboards: latency, error rate, saturation, dependency health
- [ ] Check logs/traces with correlation IDs
- [ ] Verify if incident is ongoing or already recovering

## Common Alerts

### Alert: High Error Rate

- Trigger:
- Impact:
- Likely causes:
- Immediate mitigations (safe actions):
  - Option A:
  - Option B:
- Verification steps (how to confirm improvement):
- Escalation criteria:

### Alert: High Latency

- Trigger:
- Impact:
- Likely causes:
- Immediate mitigations (safe actions):
- Verification steps:
- Escalation criteria:

### Alert: Dependency Unavailable

- Trigger:
- Impact:
- Likely causes:
- Immediate mitigations (safe actions):
- Verification steps:
- Escalation criteria:

## Safe Mitigations (Pre-Approved)

- Feature flags (names + effect):
- Rate limiting / circuit breaker actions:
- Traffic shedding / load shedding:
- Rollback procedure:
- Read-only mode procedure:

## Escalation and Communication

- Incident commander criteria:
- Escalation contacts (primary/backup):
- Customer communication triggers:
- Status page ownership:

## Post-Incident Follow-Up

- Link to postmortem template: `assets/incident-response/template-postmortem.md`
- Required updates after incident:
  - [ ] Update this runbook with new learnings
  - [ ] Add/adjust alerts if signal was missing or noisy
  - [ ] Add regression tests or guardrails where applicable

---

## Optional: AI/Automation

- Summarize current incident state from dashboards/logs (human-verified)
- Suggest likely dependency chain based on service graph (human-validated)
- Draft comms updates from structured incident fields (human-approved)

### Bounded Claims

- Automation can be wrong; never execute mitigations without explicit approval.
