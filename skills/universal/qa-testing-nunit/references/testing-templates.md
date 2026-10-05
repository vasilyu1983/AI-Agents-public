# Testing Templates

## Table of Contents

- [Purpose](#purpose)
- [Template Map](#template-map)
- [Recommended Default](#recommended-default)
- [Controller-Focused API Migration Default](#controller-focused-api-migration-default)
- [API Full-Cycle Parallelism Contract](#api-full-cycle-parallelism-contract)
- [Healthcheck Endpoint Template](#healthcheck-endpoint-template)
- [Migration Traceability Outputs](#migration-traceability-outputs)

## Purpose
Use this guide to pick the right copy-ready template and the rules that go with it. The code lives in `assets/`; this file does not duplicate it.

## Template Map

| Need | Template | Notes |
|---|---|---|
| Handler/use-case fixture | [`nunit-handler-fixture-template.cs`](../assets/nunit-handler-fixture-template.cs) | Fluent `Given...` helpers returning the fixture |
| Handler/use-case tests | [`nunit-handler-tests-template.cs`](../assets/nunit-handler-tests-template.cs) | `InstancePerTestCase` + constraint-model assertions |
| Controller API test class | [`nunit-api-tests-template.cs`](../assets/nunit-api-tests-template.cs) | Declares `IOrdersApiClient`; static shared runtime |
| Controller API fixture + runtime | [`nunit-api-fixture-template.cs`](../assets/nunit-api-fixture-template.cs) | Owns DB launcher, WireMock, app factory, client |
| Request builder | [`nunit-api-request-builder-template.cs`](../assets/nunit-api-request-builder-template.cs) | Seeded Bogus fakers |
| `TestCaseSource` data | [`nunit-api-test-case-sources-template.cs`](../assets/nunit-api-test-case-sources-template.cs) | Named `TestCaseData` |
| WireMock wrapper + helpers | [`nunit-wiremock-template.cs`](../assets/nunit-wiremock-template.cs) | Dynamic port; one helper per upstream |
| SQL Server + migrators | [`nunit-database-launcher-template.cs`](../assets/nunit-database-launcher-template.cs) | Pinned images, ordered migrators, table checks |

The four API templates, the WireMock template, and the database launcher are designed to be copied as one set: each type is declared exactly once across them. Copying a single file on its own leaves unresolved references by design; do not paste in local stub copies of types that another template already declares (that is how duplicate-type CS0101 errors appear).

## Recommended Default
- Use two files for each handler/use case:
  - `<Feature>Fixture.cs`
  - `<Feature>Tests.cs`
- Add extra partial files only when scenario families are large.

## Controller-Focused API Migration Default
- Organize API tests around controller/test family, not around legacy feature-file grouping.
- Use one fixture per controller/test family.
- Keep migration parity in test behavior, then document parity in migration trace artifacts.

## API Full-Cycle Parallelism Contract
- The API templates use one shared runtime per controller fixture and one lightweight fixture facade per test case.
- Keep fixture-level parallelism only. Do not add `ParallelScope.Children` or `ParallelScope.All` while the runtime, API client, or WireMock state is shared.
- Reset shared mutable state in `[SetUp]` before constructing the per-test facade.
- `[OneTimeSetUp]`/`[OneTimeTearDown]` must be `static` under `LifeCycle.InstancePerTestCase`.

## Healthcheck Endpoint Template
Keep `[Test]` together with `[TestCase]`, and let `[CancelAfter]` bound the polling loop through the injected token.

```csharp
[Test]
[TestCase("/health/live")]
[TestCase("/health/startup")]
[TestCase("/health/ready")]
[CancelAfter(10_000)]
public async Task HealthCheck_Should_Return_Healthy(string url, CancellationToken cancellationToken)
{
    while (true)
    {
        using var response = await ApiTestContext.Client.GetAsync(url, cancellationToken);
        if (response.StatusCode == HttpStatusCode.OK)
        {
            return;
        }

        await Task.Delay(100, cancellationToken);
    }
}
```

## Migration Traceability Outputs
- Create matrix mapping old scenario name -> new test method.
- Create per-feature migration trace table with step/block parity status.
- Create controller-focused fixture/test map documenting fixture ownership.
