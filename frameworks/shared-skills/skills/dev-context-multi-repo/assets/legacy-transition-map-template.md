# Legacy Transition Map

Use this template to map legacy components to target services and sequence the cutover work. Adjust ordering based on dependency constraints, blast radius, validation cost, customer impact, and deadlines rather than forcing one universal rollout rule.

## Service Migration Matrix

| Legacy Component | Target Component | Relation | Migration Status | Risk | Suggested Order | Notes |
|------------------|------------------|----------|------------------|------|-----------------|-------|
| legacy-a | service-a | replaces | not-started | medium | 1 | Standard migration path |
| legacy-b | service-b | splits-from | partial | high | 2 | Requires contract bridge |

## Sequencing Factors

- Dependency constraints: which upstream or downstream systems must move first?
- Validation window: how long must old and new paths run in parallel?
- Data migration: which services need storage backfill or dual-write support?
- Contract migration: which packages, schemas, or message topics change?
- External deadlines: which customer, compliance, or provider dates affect cutover order?

## Rollout Stages

1. **Adapt** - refactor or extend the target service to handle the legacy use case.
2. **Parallel run** - dual-publish, dual-read, or route mirrored traffic where needed.
3. **Validate** - compare behavior, reconcile mismatches, and confirm success metrics.
4. **Cut over** - switch consumers and operators to the target path only.
5. **Clean up** - remove the old path, temporary bridges, and transitional toggles.

## Per-Service Notes

| Service | Pre-requisites | Validation Window | Rollback Trigger | Special Handling |
|---------|----------------|-------------------|------------------|------------------|
| service-a | None | 7 days | Error-rate regression | Standard runbook |
| service-b | Schema v3 published | 14 days | Reconciliation mismatch | Provider-specific bridge |

## Cross-Cutting Concerns

| Concern | Affected Components | Change Needed | Owner |
|---------|---------------------|---------------|-------|
| Messaging | service-a, service-b | Topic and consumer cutover | Platform team |
| Data | service-b | Backfill and rollback plan | Data team |
| Contracts | shared package x | Versioned client upgrade | API owners |
