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

## Port and Host Allocation
- Never hard-code host ports for Docker-backed test infrastructure (brokers, databases, caches). Use dynamic port allocation from Testcontainers or the OS.
- One fixed-port collision is enough to break the entire component suite. Validate stability with an "occupied port" regression test — intentionally occupy the old fixed ports and confirm the suite still passes.
- Resolve the Docker host from Testcontainers or `DOCKER_HOST` instead of assuming `localhost`. CI runners may use remote Docker hosts where loopback is wrong.

## CI Stability Checklist
- Cap parallelism if shared resources are contested.
- Mark known long-running categories separately.
- Ensure cleanup runs even when setup partially fails.
- No hard-coded host ports in Docker-backed test infrastructure.
