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

## Migration Guidance (SpecFlow/Taffy -> NUnit)
- Rewrite scenarios into controller-focused API tests.
- Preserve scenario parity, but avoid step-by-step translation of legacy Given/When/Then files.
- Keep test intent in assertions, not in copied step text.
- Add explicit migration parity artifacts (matrix + per-feature trace).

## Core Pattern
1. Arrange request payload and prerequisite state.
2. Send HTTP request through configured client.
3. Assert status code and response body contract.
4. Verify persistence/event side effects when relevant.

## What to Assert
- Expected status code and media type.
- Required fields in success and error payloads.
- Contract details for `ProblemDetails` failures.
- Idempotency and conflict behavior where applicable.

## Coverage Baseline
- Happy path.
- Validation failure.
- Domain/business-rule failure.
- AuthN/AuthZ failure when endpoint is protected.
- Dependency failure translation when upstream calls are involved.
- Idempotency checks for repeated operations (same transaction id / same confirmation id / same payout id).
- Concurrency conflict checks (for example repository version conflict to `409 Conflict`).

## Mandatory Migration Verification Add-on
- Add one dedicated migrator verification test suite that checks:
  - DB launcher starts correctly,
  - migrators run in expected order,
  - required schema tables exist before API tests execute.
