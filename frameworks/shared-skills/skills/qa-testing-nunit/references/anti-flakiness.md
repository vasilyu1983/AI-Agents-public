# Anti-Flakiness

## Purpose
Use this guide to eliminate nondeterminism in NUnit API/component/integration tests.

## Determinism Rules
- Freeze time or inject clock abstraction.
- Use fixed random seeds or deterministic data builders.
- Avoid real network calls outside controlled test doubles/containers.

## Concurrency and Timing
- Replace arbitrary sleeps with polling + timeout.
- Set explicit timeouts for async operations.
- Keep retry policies in tests intentional and bounded.

## Isolation
- Reset shared state between tests.
- Use unique identifiers per test run.
- Prevent static mutable state bleed.

## Diagnostics
- Log correlation IDs and request/response bodies on failure.
- Persist container and WireMock logs for failed tests.
- Include fixture startup and teardown timing in failure output.

## Port Collision Regression
- Validate that tests still pass when previously hard-coded ports are intentionally occupied. This confirms the suite is truly decoupled from fixed port assumptions.
- Treat port collision as a first-class regression scenario when migrating from hard-coded to dynamic port allocation.

## CI Stability Checklist
- Cap parallelism if shared resources are contested.
- Mark known long-running categories separately.
- Ensure cleanup runs even when setup partially fails.
