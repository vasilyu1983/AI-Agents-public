# CI Parallelism and Sharding

## Purpose
Use this guide to scale NUnit execution while keeping shared resources stable.

## Parallelism Rules
- Run unit tests with high parallelism.
- Limit API/component/integration parallelism when infrastructure is shared.
- Separate contention-heavy categories from fast categories.
- Prefer fixture-level parallelism for API suites that use isolated per-fixture dependencies.

## Fixture Isolation Preconditions
- Use one fixture per controller/test family.
- Ensure each fixture owns independent runtime dependencies.
- Reset mutable state in `[SetUp]`.
- Dispose owned runtime in `[OneTimeTearDown]`.

## NUnit Parallel Baseline for API Suites
- Assembly: `ParallelScope.Fixtures` with explicit level of parallelism.
- Test classes: `[Parallelizable]` + `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]`.
- Test category: `[Category("ApiTest")]`.

## Sharding Strategy
- Split by category first (`ApiTest`, `ComponentTests`, `DbTests`).
- Then shard by assembly or namespace.
- Keep shard duration balanced with historical timing.

## Guardrails
- Use unique identifiers for test data per shard.
- Reserve fixed ports only when unavoidable.
- Always collect container and test logs for failed shards.
- Avoid running multiple `dotnet test` commands in parallel against the same project output path.
