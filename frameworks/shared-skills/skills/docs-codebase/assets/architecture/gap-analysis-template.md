# Gap Analysis - [System Name]

> **Date:** YYYY-MM-DD  
> **Status:** Draft | Final  
> **Scope:** [Repos, services, or documents analyzed]  
> **Evidence Base:** [Links to profiles, source code paths, or as-is documentation]  
> **Method:** Use [qa-docs-coverage](../../../qa-docs-coverage/SKILL.md) to discover components, rank gaps, and collect evidence. Use this template to publish the resulting assessment.

## How to Read This Document

Each gap should include:
- **Severity:** `HIGH`, `MEDIUM`, or `LOW`
- **Blocker:** whether it blocks the next migration, launch, or decommissioning step
- **Evidence:** a source code path, document section, or generated profile reference
- **Addressed By:** the ADR, task, or target component expected to resolve the gap

## [Category Name]

### GAP-01: [Title] [HIGH]
- **Evidence:** `path/to/file.ext:line` or `docs/path.md#Section`
- **Risk:** [What happens if unresolved]
- **Blocker:** Yes / No
- **Addressed By:** [ADR, task, or target service]
- **Notes:** [Validation window, dependency, or owner]

### GAP-02: [Title] [MEDIUM]
- **Evidence:** `path/to/file.ext:line`
- **Risk:** [Operational or delivery impact]
- **Blocker:** Yes / No
- **Addressed By:** [ADR, task, or target service]
- **Notes:** [Any sequencing details]

## Risk Summary

| Gap ID | Category | Severity | Blocker | Summary | Addressed By |
|--------|----------|----------|---------|---------|--------------|
| GAP-01 | Messaging | HIGH | Yes | Topic cutover undefined | ADR-012 |

## Summary Statistics

| Severity | Count | Blockers |
|----------|-------|----------|
| HIGH | 0 | 0 |
| MEDIUM | 0 | 0 |
| LOW | 0 | 0 |

## Next Actions

1. Link each HIGH gap to a concrete resolution owner.
2. Confirm blockers are reflected in the migration plan or backlog.
3. Re-run the assessment after the next major architecture change or delivery phase.
