# Reliability and Dependencies

NUnit/Testcontainers-specific rules for choosing real vs simulated dependencies, component-test boundaries, eventual assertions, and flake prevention.

## Dependency Strategy

| Scenario | Use |
|---|---|
| Third-party HTTP API contract, deterministic payloads, fast upstream-failure paths | WireMock (`wiremock-setup.md`) |
| Owned database: transaction semantics, query behavior, migrations | Testcontainers (`testcontainers-setup.md`) |
| Owned broker: ack, retry, ordering | Testcontainers |

- API full-cycle default: WireMock for external HTTP, Testcontainers for owned stateful infrastructure. State the split in fixture setup comments.
- Component tests: real composition root for the module under test; replace only out-of-process dependencies; keep DB/broker real when behavior depends on their semantics. Drive through the public component API and assert output plus state transitions, not private details.
- API-component hybrid: drive the test through HTTP with a real web app host, then verify database and message side effects. The per-test fixture object orchestrates the Given/When helpers.
- Keep each component test to one end-to-end scenario, and limit permutations so the suite's runtime stays acceptable; push input permutations down to unit tests.

## Container Topology (Cost vs Isolation)

| Topology | NUnit mechanism | Isolation | Cost |
|---|---|---|---|
| Container per controller fixture | static runtime + `[OneTimeSetUp]` in the fixture | Strongest; fixtures parallelize freely | N containers; heavy for SQL Server |
| One container per namespace/assembly, database or schema per fixture | `[SetUpFixture]` owns the container; each fixture creates its own database | Good if every fixture uses a unique DB name | One container start |

- Choose by measuring: container start time × fixture count vs the risk of cross-fixture leakage. Do not default to per-fixture containers for dozens of fixtures without weighing it.
- Size `LevelOfParallelism` to Docker host memory/CPU, not to the runner's core count.
- Reset data between tests with an explicit cleanup step (for example a Respawn-style table reset), not by restarting containers.

## Eventual Assertions

```csharp
public static async Task Eventually(
    Func<Task<bool>> condition,
    TimeSpan timeout,
    TimeSpan interval,
    Func<Task<string>>? describeState = null)
{
    var deadline = DateTimeOffset.UtcNow + timeout;

    while (DateTimeOffset.UtcNow < deadline)
    {
        if (await condition())
        {
            return;
        }

        await Task.Delay(interval);
    }

    var state = describeState is null ? "n/a" : await describeState();
    Assert.Fail($"Condition not met within {timeout}. Last observed state: {state}");
}
```

- No `Thread.Sleep` or fixed `Task.Delay` as a wait; poll with explicit timeout and interval per scenario.
- Widen a timeout only after confirming the condition is correct, never to hide a race.

## Determinism
- Time: inject `TimeProvider` (.NET 8+) and use `FakeTimeProvider` (`Microsoft.Extensions.TimeProvider.Testing`) in tests instead of `DateTime.UtcNow`.
- Data: seed fakers (`Faker<T>.UseSeed(...)`) and use unique IDs per test.
- No real network calls outside WireMock or containers.
- No static mutable state shared across fixtures.

## Ports and Hosts
- Never hard-code host ports for Docker-backed infrastructure or WireMock. Use dynamic ports and read the mapped port back.
- Resolve the Docker host from Testcontainers (`container.Hostname`) or `DOCKER_HOST`, never assume `localhost`; CI runners with Docker-in-Docker or remote hosts break loopback assumptions.
- Validate with an "occupied port" regression test: bind the previously hard-coded ports, then confirm the suite still passes.

## Flake Diagnostics
- On failure, emit correlation IDs, request/response bodies, container logs, WireMock request logs, and fixture startup/teardown timing.
- `[Retry]` is not a fix for an unexplained flake; see `assertions-and-diagnostics.md` for retry rules.
- CI stability: cap parallelism for contested categories, tag long-running categories, and make cleanup run even after partial setup failure.
