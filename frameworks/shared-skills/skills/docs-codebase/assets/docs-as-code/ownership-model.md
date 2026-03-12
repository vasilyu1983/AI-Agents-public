# Docs Ownership Model (Core, Non-AI)

Purpose: make documentation freshness a first-class operational responsibility.

## Inputs

- Org structure (teams, on-call, product areas)
- Doc types in scope (README, runbooks, ADRs, API docs, user docs)

## Outputs

- Ownership map for doc types and areas
- Review cadence and escalation path for stale docs

## Core

### Ownership Roles

- **Directly Responsible Individual (DRI)**: accountable for updates and quality
- **Approver**: reviews for correctness (often tech lead or PM)
- **Steward**: maintains IA and standards (docs lead or platform team)

### Ownership Table

| Doc type | Owner (DRI) | Approver | Review cadence | Where tracked |
|----------|-------------|----------|----------------|--------------|
| README | {{TEAM}} | {{LEAD}} | Quarterly | PRs |
| Runbooks | {{ON_CALL_TEAM}} | {{SRE_LEAD}} | Monthly | Incident retros |
| ADRs | {{ARCH_TEAM}} | {{ARCH_LEAD}} | On change | ADR index |
| API docs | {{API_TEAM}} | {{API_LEAD}} | On release | CI |

### Freshness SLAs

- Runbooks: reviewed at least monthly or after incidents
- API docs: updated with every backward-incompatible change
- README quick start: updated when install/run commands change

### Enforcement Options

- CI checks for “last reviewed” dates
- Scheduled issues for upcoming reviews
- On-call post-incident action: update runbook + link

## Decision Rules

- If a doc is used during incidents, it must have an owner and a cadence.
- If a doc page has no owner, it is either assigned or deleted.

## Risks

- Ownership theatre (owners listed but no time allocated)
- Stale docs increase support burden and incident time

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Generate “stale docs” reports and draft updates; humans review before publishing.
