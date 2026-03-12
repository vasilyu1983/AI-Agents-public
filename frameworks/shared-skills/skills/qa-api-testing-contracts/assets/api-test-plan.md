# API Test Plan

## Overview

| Field | Value |
| --- | --- |
| API Name | |
| API Type | REST / GraphQL / gRPC |
| Schema Source | OpenAPI / SDL / Proto |
| Version | |
| Owner | |
| Consumer inventory | |
| Contract strategy | CDC (Pact) / Schema-driven / Both |
| CI gating target | PR / Release / Both |

## Environments

| Environment | Base URL | Auth Method | Notes |
| --- | --- | --- | --- |
| Development | | | |
| Staging | | | |
| Production | | | |

## Coverage Map

| Endpoint / Operation | Method | Criticality | Test Types | Status |
| --- | --- | --- | --- | --- |
| /users | GET | High | Schema, Happy, Negative | Covered |
| /users/{id} | GET | High | Schema, Happy, Auth | Covered |
| /users | POST | Critical | Schema, Happy, Negative, Idempotency | Covered |
| | | | | |

## Test Types Checklist

- [ ] Schema validation (response matches OpenAPI/SDL/Proto)
- [ ] Happy path (valid inputs, expected outputs)
- [ ] Negative testing (invalid inputs, error responses)
- [ ] Authentication and authorization
- [ ] Idempotency (POST/PUT/DELETE safety)
- [ ] Rate limiting and throttling
- [ ] Pagination and cursors
- [ ] Timeout and retry behavior
- [ ] Backward compatibility

## Data Strategy

| Aspect | Approach |
| --- | --- |
| Test data source | Fixtures / Factory / Seeded DB |
| Data isolation | Per-test / Per-suite / Shared |
| Cleanup strategy | Teardown / Transactional rollback |
| Sensitive data | Masked / Synthetic |

## CI Quality Gates

| Gate | Threshold | Blocking |
| --- | --- | --- |
| Schema validation | 100% pass | Yes |
| Breaking-change diff | 0 breaking changes | Yes |
| Contract tests | 100% pass | Yes |
| Functional tests | 95% pass | Yes |
| Response time p95 | < 500ms | No |
| Error rate | < 1% | Yes |

## Tools

| Purpose | Tool | Config Location |
| --- | --- | --- |
| Schema validation | Spectral / Prism | |
| Contract testing | Pact / Schemathesis | |
| Functional testing | Postman / pytest | |
| Mocking | WireMock / Prism | |
