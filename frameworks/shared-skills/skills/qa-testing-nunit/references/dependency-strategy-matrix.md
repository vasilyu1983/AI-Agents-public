# Dependency Strategy Matrix

## Purpose
Use this matrix to choose WireMock or Testcontainers per dependency and test goal.

## Decision Matrix
- Need strict external API contract simulation with deterministic payloads: Use WireMock.
- Need database transaction semantics, query behavior, or migration checks: Use Testcontainers.
- Need broker behavior (ack, retry, ordering): Use Testcontainers.
- Need fast negative-path coverage for upstream HTTP failures: Use WireMock.
- Need confidence in production-like integration behavior: Prefer Testcontainers.

## Combined Strategy
- Use WireMock for third-party HTTP APIs.
- Use Testcontainers for owned stateful infrastructure.
- Keep this split explicit in fixture setup comments.
- For API full-cycle tests, this combined strategy is the default baseline.
