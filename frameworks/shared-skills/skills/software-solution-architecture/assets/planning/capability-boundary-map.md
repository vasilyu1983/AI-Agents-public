# Capability And Boundary Map

Use this when the solution spans multiple teams, systems, or vendors and you need a clear ownership map before deciding integration style or migration waves.

## Capability Map

| Capability / Journey Slice | Business Owner | Engineering Owner | Primary System | System Of Record | Boundary Type | Notes |
|----------------------------|----------------|-------------------|----------------|------------------|---------------|-------|
| Example: Customer onboarding | Operations | Platform team | Onboarding portal | CRM | Trust + data boundary | Sync to KYC vendor only after approval |

## Boundary Questions

- Which system is authoritative for each critical entity?
- Which boundaries are trust, compliance, tenancy, or residency boundaries?
- Which teams approve contract changes across each boundary?
- Which capabilities should stay decoupled even if a single platform eventually hosts them?

## Output Check

Before moving on, confirm that the capability map names:

- what changes now
- what stays external
- what is deliberately deferred
