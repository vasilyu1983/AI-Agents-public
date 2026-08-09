# Testing Templates

## Table of Contents

- [Purpose](#purpose)
- [Recommended Default](#recommended-default)
- [Controller-Focused API Migration Default](#controller-focused-api-migration-default)
- [API Full-Cycle Parallelism Contract](#api-full-cycle-parallelism-contract)
- [Fixture Template (`<Feature>Fixture.cs`)](#fixture-template-featurefixturecs)
- [Tests Template (`<Feature>Tests.cs`)](#tests-template-featuretestscs)
- [Healthcheck Endpoint Template](#healthcheck-endpoint-template)
- [API Full-Cycle Base Test Template (`<Controller>ApiTest.cs`)](#api-full-cycle-base-test-template-controllerapitestcs)
- [API Full-Cycle Fixture Template (`<Controller>ApiFixture.cs`)](#api-full-cycle-fixture-template-controllerapifixturecs)
- [Migration Traceability Outputs](#migration-traceability-outputs)

## Purpose
Use these templates as starting points for NUnit API/component/integration tests.

WireMock reference template: `assets/nunit-wiremock-template.cs`.
Database launcher reference template: `assets/nunit-database-launcher-template.cs`.

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
- The API template below uses one shared runtime per controller fixture and one lightweight fixture facade per test case.
- Keep fixture-level parallelism only. Do not add `ParallelScope.Children` or `ParallelScope.All` while the runtime, API client, or WireMock state is shared.
- Reset shared mutable state in `[SetUp]` before constructing the per-test facade.

## Fixture Template (`<Feature>Fixture.cs`)
```csharp
internal sealed partial class CreatePaymentTransactionHandlerFixture
{
    private readonly IMediator _mediator;
    private readonly InMemoryPaymentTransactionRepository _repository;

    internal CreatePaymentTransactionCommand Command { get; private set; } = null!;

    internal CreatePaymentTransactionHandlerFixture(IServiceProvider services)
    {
        _mediator = services.GetRequiredService<IMediator>();
        _repository = services.GetRequiredService<IPaymentTransactionRepository>() as InMemoryPaymentTransactionRepository
            ?? throw new InvalidOperationException("InMemory repository is required for tests.");
    }

    internal CreatePaymentTransactionHandlerFixture GivenCommand(CreatePaymentTransactionCommand command)
    {
        Command = command;
        return this;
    }

    internal CreatePaymentTransactionHandlerFixture GivenValidationPassed()
    {
        // Setup mocks/stubs here.
        return this;
    }

    internal Task<Result<CreatePaymentTransactionResult>> SendAsync(CreatePaymentTransactionCommand command)
        => _mediator.Send(command, CancellationToken.None);
}
```

## Tests Template (`<Feature>Tests.cs`)
```csharp
internal sealed partial class CreatePaymentTransactionHandlerTests
{
    private static readonly WireMockServerWrapper WireMockServerWrapper = new();
    private CreatePaymentTransactionHandlerFixture _fixture = null!;

    [OneTimeSetUp]
    public static void OneTimeSetUp() => WireMockServerWrapper.Start();

    [OneTimeTearDown]
    public static void OneTimeTearDown() => WireMockServerWrapper.Stop();

    [SetUp]
    public Task SetUp()
    {
        IServiceProvider services = BuildServices();
        _fixture = new CreatePaymentTransactionHandlerFixture(services);
        return Task.CompletedTask;
    }

    [Test]
    public async Task Should_Create_Transaction_When_Request_Is_Valid()
    {
        // Arrange
        var command = CreatePaymentTransactionCommandBuilder.New().Build();
        _fixture.GivenCommand(command)
            .GivenValidationPassed();

        // Act
        var result = await _fixture.SendAsync(command);

        // Assert
        // Note: .Should() here uses a fluent assertion library (Shouldly or AwesomeAssertions).
        // FluentAssertions v8+ requires a paid Xceed license for commercial repos.
        // Replace with Assert.That(result.IsSuccess, Is.True) if no fluent library is used.
        result.Should().BeSuccessful();
    }
}
```

## Healthcheck Endpoint Template
```csharp
[Test]
[TestCase("/health/live")]
[TestCase("/health/startup")]
[TestCase("/health/ready")]
[CancelAfter(10_000)]
public async Task HealthCheck_Should_Return_Healthy(string url, CancellationToken cancellationToken)
{
    HttpResponseMessage response;
    do
    {
        response = await PublicApiTestContext.Client.GetAsync(url, cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            await Task.Delay(100, cancellationToken);
        }
    }
    while (response.StatusCode != HttpStatusCode.OK);
}
```

## API Full-Cycle Base Test Template (`<Controller>ApiTest.cs`)
```csharp
[assembly: Parallelizable(ParallelScope.Fixtures)]

[Category("ApiTest")]
[TestFixture]
[Parallelizable]
[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]
internal sealed partial class TransactionControllerApiTest
{
    private static readonly TransactionControllerApiSharedRuntime SharedRuntime = new();
    private TransactionControllerApiFixture _fixture = null!;

    [OneTimeSetUp]
    public static Task OneTimeSetUp() => SharedRuntime.InitializeAsync();

    [OneTimeTearDown]
    public static async Task OneTimeTearDown() => await SharedRuntime.DisposeAsync();

    [SetUp]
    public async Task SetUp()
    {
        await SharedRuntime.ResetAsync();
        _fixture = new TransactionControllerApiFixture(SharedRuntime);
    }
}
```

## API Full-Cycle Fixture Template (`<Controller>ApiFixture.cs`)
```csharp
internal sealed partial class TransactionControllerApiFixture : IAsyncDisposable
{
    private readonly TransactionControllerApiSharedRuntime _runtime;

    internal TransactionControllerApiFixture(TransactionControllerApiSharedRuntime runtime)
        => _runtime = runtime;

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;
}
```

## Migration Traceability Outputs
- Create matrix mapping old scenario name -> new test method.
- Create per-feature migration trace table with step/block parity status.
- Create controller-focused fixture/test map documenting fixture ownership.
