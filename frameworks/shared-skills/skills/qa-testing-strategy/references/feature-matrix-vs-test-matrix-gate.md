# Feature Matrix vs Test Matrix Gate

Use this gate before release to ensure implemented features have direct, auditable test evidence.

## Objective

Prevent release drift where backlog/features are marked complete but test coverage is missing or indirect.

## Gate Steps

1. Enumerate release-scoped features/backlog IDs.
2. Map each feature to direct test evidence:
   - unit/integration/contract/e2e
   - file path + case identifier
3. Classify status:
   - `direct` (explicit test)
   - `indirect` (covered as side effect)
   - `none`
4. Assign risk and owner for each non-direct item.
5. Block release if critical item is `none` without approved waiver.

## Evidence Rules

- Evidence must be machine-locatable (`path`, test name, grep-able ID).
- "We manually tested it" is supplemental, not replacement for direct test evidence.
- Waivers must include expiry date and follow-up owner.

## Suggested Query Pattern

```bash
# Example: find tests mentioning feature IDs or endpoint paths
rg -n "BL-023|BL-024|/api/feature-x|feature_x" e2e tests src --glob "**/*.{spec,test}.{ts,tsx,js}"
```

## Release Decision Rule

- `GO`: all critical features have direct evidence or approved waiver.
- `NO-GO`: any critical feature lacks direct evidence and no waiver.
