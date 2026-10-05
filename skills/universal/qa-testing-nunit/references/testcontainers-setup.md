# Testcontainers Setup

## Purpose
Use this guide for ephemeral infrastructure in integration and component tests.

## Container Lifecycle
- Pin every image to an explicit tag or digest (never `:latest`), including migrator images.
- Start containers before executing tests.
- Wait for readiness via health check or explicit probe.
- Dispose containers reliably after test execution.
- For API full-cycle suites, keep containers static and start them once in `[OneTimeSetUp]`.
- Create required schema/collections/topics during one-time setup after readiness.
- For SQL databases, prefer one-shot migration containers over ad-hoc schema SQL in test code.

## Database Launcher and Migration Containers
- Keep database startup orchestration in one launcher class per test project.
- Run the database and migration containers in one shared Docker network so migrations connect via a network alias.
- Build each migration container in one factory method, not with hand-crafted `ContainerBuilder` code at every call site.
- Run migration containers as short-lived jobs and fail the setup unless the exit code is `0`.
- Copy migration folders into the migration container with `WithResourceMapping`; avoid host bind mounts, which break on remote Docker hosts (Testcontainers best practice #5).
- Use the command the repository's migration image already documents; keep the command and the in-container migrations path explicit in the fixture.
- Do not add custom ready-check parameters in tests; rely on the wait strategy and startup timeout.
- Resolve migration paths from the repository root instead of from the test runner's transient working directory.
- Reuse an existing repository launcher or migration helper when one exists; otherwise start from `assets/nunit-database-launcher-template.cs`.

## Ordered Migration Chain
- Run dependency migrations first.
- Run the service/domain migration last.
- Validate required tables after each critical step.
- Add fixture-level launch options when some suites do not require all migrations or databases.

## Template
- Use `assets/nunit-database-launcher-template.cs` as the starting point for:
  - the launcher class
  - the database container factory
  - the migration container factory with an exit-code check
  - optional migration launch options and table checks

## Isolation Rules
- Choose container-per-fixture vs a shared `[SetUpFixture]` container with a database per fixture deliberately; see the topology table in `reliability-and-dependencies.md`.
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
- Resolve the externally reachable Docker host from Testcontainers (`container.Hostname`) or the `DOCKER_HOST` environment variable — never assume `localhost`. CI runners that use Docker-in-Docker or a remote Docker host may not bind containers to loopback.
- For message brokers (Kafka, RabbitMQ): inject the resolved host into advertised listener or connection endpoint configuration, not just the client connection string.
- Support environment variable overrides so developers can still use `localhost` explicitly for local manual runs.
- Validate with an "occupied port" regression test: intentionally occupy any previously hard-coded ports and confirm the suite still passes on dynamic allocation.

## Common Targets
- Relational databases for persistence behavior.
- Message brokers for async flow verification.
- Caches for TTL/eviction-related behavior.
