# Contract Change Checklist

Use this checklist before merging or releasing contract changes.

## Change Summary

| Field | Value |
| --- | --- |
| System / API | |
| Surface | REST / GraphQL / gRPC / AsyncAPI / Webhook / Workflow |
| Endpoint(s) / message(s) / workflow(s) affected | |
| Change type | Addition / Modification / Removal |
| PR / Ticket | |
| Planned release date | |

## Breaking-Change Screening

- [ ] Removes or renames endpoint, field, message, event, or workflow step
- [ ] Tightens request validation or requiredness
- [ ] Changes auth, signing, or tenant-isolation semantics
- [ ] Changes error envelope or RFC 9457 problem shape consumed by clients
- [ ] Changes retry, replay, ordering, or idempotency behavior
- [ ] Reuses or renumbers protobuf fields
- [ ] Breaks GraphQL schema or collected client operations
- [ ] Changes webhook retry or signature behavior

## Compatibility Assessment

| Question | Answer |
| --- | --- |
| Backward compatible? | Yes / No |
| Version bump needed? | Major / Minor / Patch / None |
| Consumer migration needed? | Yes / No |
| Deprecation / sunset notice needed? | Yes / No |
| Workflow or async replay test needed? | Yes / No |

## Verification Checklist

- [ ] Canonical artifact updated
- [ ] Lint passes
- [ ] Breaking diff reviewed
- [ ] Consumer/provider contracts pass
- [ ] Pact `can-i-deploy` passes if applicable
- [ ] GraphQL registry checks pass if applicable
- [ ] `buf breaking` passes if applicable
- [ ] Async/webhook/workflow tests pass if applicable
- [ ] Mocks updated
- [ ] Docs and migration guidance updated
- [ ] Consumers notified if required

## Rollback / Recovery

| Step | Action |
| --- | --- |
| 1 | |
| 2 | |
| 3 | |

## Approvals

| Role | Name | Date |
| --- | --- | --- |
| API owner | | |
| QA / test owner | | |
| Consumer owner | | |
