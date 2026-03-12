# Contract Change Checklist

Use this checklist before releasing API changes to production.

## Change Summary

| Field | Value |
| --- | --- |
| API | |
| Endpoint(s) affected | |
| Change type | Addition / Modification / Removal |
| PR/Ticket | |
| Release date | |

## Change Classification

### Breaking Changes (Require version bump)

- [ ] Removing fields or endpoints
- [ ] Changing field types (string to int, etc.)
- [ ] Changing required fields (optional to required)
- [ ] Renaming enum values
- [ ] Changing default behavior
- [ ] Reducing allowed values in enums
- [ ] Changing authentication requirements

### Non-Breaking Changes (Safe to release)

- [ ] Adding optional fields
- [ ] Adding new endpoints
- [ ] Adding new enum values (with backwards-compatible defaults)
- [ ] Deprecating fields (with migration period)
- [ ] Performance improvements (same contract)

## Compatibility Assessment

| Question | Answer |
| --- | --- |
| Backward compatible? | Yes / No |
| Version bump needed? | Major / Minor / Patch / None |
| Deprecation notice required? | Yes / No |
| Migration guide needed? | Yes / No |

## Validation Checklist

- [ ] Schema updated (OpenAPI/SDL/Proto)
- [ ] Schema validation passes
- [ ] Consumer contract tests pass
- [ ] Provider contract tests pass
- [ ] Existing integration tests pass
- [ ] Mocks updated to match new schema
- [ ] Documentation updated
- [ ] Release notes drafted
- [ ] Consumers notified (if breaking)

## Rollback Plan

| Step | Action |
| --- | --- |
| 1 | |
| 2 | |
| 3 | |

## Approvals

| Role | Name | Date |
| --- | --- | --- |
| API Owner | | |
| QA Lead | | |
| Consumer Rep | | |
