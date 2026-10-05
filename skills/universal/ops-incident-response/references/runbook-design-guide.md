# Runbook Design Guide

Practical guidance for writing incident runbooks that are short enough to use under pressure.

## Key Rules

- Start with trigger conditions, not background theory.
- Put mitigation actions before diagnosis depth for SEV1 and SEV2 cases.
- Keep every step imperative and observable.
- Link to dashboards, logs, and feature flags with exact names.
- Include rollback, owner, and escalation points.

## Recommended Structure

1. Service name and scope.
2. Symptoms and alert triggers.
3. Immediate checks.
4. Safe mitigations and rollback actions.
5. Deep-dive diagnostics.
6. Escalation contacts and dependencies.
7. Recovery validation steps.

## Quality Gate

- A new on-call engineer can execute the first five minutes without extra context.
- Every command or dashboard reference is current.
- Every risky action includes a guardrail or approval note.
