# API Testing with NUnit

## Purpose
Use this guide for black-box or near-black-box API tests.

## Test Scope
- Boot the API host with production-like middleware.
- Exercise endpoints through HTTP client, not controller internals.
- Validate both transport contract and domain effect.

## Full-Cycle Pattern (API -> DB)
1. Start infra in `[OneTimeSetUp]`:
   - Testcontainers for owned stateful dependencies (DB, broker).
   - WireMock for external HTTP dependencies.
   - test host factory wired to those dependency endpoints.
2. In `[SetUp]`, create HTTP client + typed API client and construct per-test fixture.
3. Arrange via fixture `Given...` helpers and request builders.
4. Execute API call through client.
5. Assert transport contract and persisted state/side effects.
6. In `[TearDown]`, dispose per-test fixture and HTTP client.
7. In `[OneTimeTearDown]`, stop and dispose all infra deterministically.

## NUnit-Specific Coverage Notes
- Beyond the usual happy/validation/auth/upstream-failure cases, add idempotency checks for repeated operations (same request or idempotency key) and concurrency-conflict checks (for example an optimistic-concurrency version conflict mapped to `409 Conflict`).
- Assert `ProblemDetails` shape for failures, not just the status code.

## Database Migration Verification
- Add one dedicated migration verification test suite that checks:
  - the database launcher starts correctly,
  - migrations run in the expected order,
  - required schema tables exist before API tests execute.
