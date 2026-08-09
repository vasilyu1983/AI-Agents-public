# API Contract Test Plan

## Overview

| Field | Value |
| --- | --- |
| System / API name | |
| Contract surfaces | REST / GraphQL / gRPC / AsyncAPI / Webhooks / Workflows |
| Canonical artifact(s) | |
| Artifact version(s) | |
| Owner | |
| Consumer inventory / registry | |
| Contract strategy | CDC / Schema-driven / Property-based / Mixed |
| Promotion gate | PR / Release / Deploy |

## Environments

| Environment | Base URL / Broker / Router | Auth / Signing | Notes |
| --- | --- | --- | --- |
| Development | | | |
| Staging | | | |
| Production | | | |

## Coverage Map

| Operation / Message / Workflow | Surface | Criticality | Test types | Status |
| --- | --- | --- | --- | --- |
| `GET /users/{id}` | REST | High | Lint, Diff, Contract, Auth | |
| `User.updated` | AsyncAPI | High | Schema, Replay, Ordering | |
| `invoice.paid` webhook | Webhook | Critical | Signature, Retry, Duplicate delivery | |
| `Checkout complete` | Arazzo workflow | Critical | Workflow, Negative, Timeout | |

## Test Types Checklist

- [ ] Artifact linting
- [ ] Breaking-change diff
- [ ] Executable contract tests
- [ ] Property-based HTTP hardening where relevant
- [ ] Authentication and authorization
- [ ] RFC 9457 problem responses where adopted
- [ ] Idempotency and duplicate delivery
- [ ] Pagination, cursors, ordering
- [ ] Retry, timeout, and eventual consistency behavior
- [ ] Webhook signing, replay, and retry handling
- [ ] Async DLQ / poison-message behavior
- [ ] Backward compatibility and consumer impact

## Data Strategy

| Aspect | Approach |
| --- | --- |
| Test data source | Fixtures / Factory / Seeded DB / Event fixtures |
| Data isolation | Per-test / Per-suite / Shared |
| Cleanup strategy | Teardown / Rollback / Auto-expiry |
| Sensitive data handling | Masked / Synthetic / Redacted before upload |

## Quality Gates

| Gate | Threshold | Blocking |
| --- | --- | --- |
| Lint | 100% pass | Yes |
| Breaking-change diff | 0 unapproved breaking changes | Yes |
| Contract tests | 100% pass for critical paths | Yes |
| Pact `can-i-deploy` | Must pass | Yes |
| GraphQL operations checks | Must pass when registry data exists | Yes |
| Buf breaking check | Must pass | Yes |
| Workflow verification | Must pass for critical outcomes | Yes |

## Tooling

| Purpose | Preferred tool(s) | Config / Notes |
| --- | --- | --- |
| Linting | Spectral / GraphQL Inspector / Buf | |
| CDC | Pact / PactFlow | |
| Schema-driven execution | Specmatic / Microcks | |
| Property-based HTTP | Schemathesis | |
| Functional adjunct | Postman | |
