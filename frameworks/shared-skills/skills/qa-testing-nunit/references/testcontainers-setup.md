# Testcontainers Setup

## Purpose
Use this guide for ephemeral infrastructure in integration and component tests.

## Container Lifecycle
- Create container definitions with fixed image tags.
- Start containers before executing tests.
- Wait for readiness via health check or explicit probe.
- Dispose containers reliably after test execution.
- For API full-cycle suites, keep containers static and start them once in `[OneTimeSetUp]`.
- Create required schema/collections/topics during one-time setup after readiness.
- For SQL databases, prefer one-shot migrator containers over ad-hoc schema SQL in test code.

## Database Launcher + Migrator Pattern
- Keep database startup orchestration in `DatabaseLauncher`.
- Run DB and migrators in one shared docker network so migrators connect via network alias.
- Use `MigratorContainer` + `MigratorContainerBuilder` for migrator startup; avoid hand-crafted per-call `ContainerBuilder` code.
- Start migrator containers as short-lived jobs and wait for exit code `0`.
- Mount migration folders into migrator container (`/sql`, optional `/sql/component-tests`).
- Use the migrator command already exposed by the repository's migrator image or helper; keep the command path and migration mount explicit in the fixture.
- Do not add custom ready-check parameters in tests; rely on wait strategy + startup timeout.
- Resolve migration paths from the repository root instead of from the test runner's transient working directory.
- Reuse an existing repository `DatabaseLauncher` or migrator-container helper when one exists; otherwise start from `assets/nunit-database-launcher-template.cs`.

## Ordered Migrator Chain (SQL Server Migration Cases)
- Run dependency migrators first.
- Run service/domain migrator last.
- Validate required tables after each critical step.
- Add fixture-level launch options when some suites do not require all migrators/DBs.

## Template
- Use `assets/nunit-database-launcher-template.cs` as the starting point for:
  - `DatabaseLauncher`
  - `<Db>Containers`
  - `MigratorContainers`
  - `MigratorContainerBuilder` + exit-code wait strategy
  - optional migrator launch options and verification hooks

## Isolation Rules
- Prefer per-fixture containers for expensive dependencies.
- Use unique database/schema/topic names per test where shared container is used.
- Avoid cross-test state leakage through explicit cleanup.
- Dispose per-test scopes/clients in `[TearDown]` even when containers are shared across all tests.

## Configuration
- Inject container connection details through test host configuration.
- Keep startup timeout explicit and environment-aware.
- Emit startup logs on readiness failure.
- When using multiple containers (for example DB + broker + schema registry), compose them with one shared test network.

## Host and Port Allocation
- Never hard-code host ports for container endpoints. Use dynamic port allocation and inject the resolved port into connection strings and broker metadata.
- Resolve the externally reachable Docker host from Testcontainers or the `DOCKER_HOST` environment variable — never assume `localhost`. CI runners (e.g., GitLab with Docker-in-Docker or remote Docker hosts) may not bind containers to loopback.
- For message brokers (Kafka, RabbitMQ): inject the resolved host into advertised listener or connection endpoint configuration, not just the client connection string.
- Support environment variable overrides so developers can still use `localhost` explicitly for local manual runs.
- Validate with an "occupied port" regression test: intentionally occupy any previously hard-coded ports and confirm the suite still passes on dynamic allocation.

## Common Targets
- Relational databases for persistence behavior.
- Message brokers for async flow verification.
- Caches for TTL/eviction-related behavior.
