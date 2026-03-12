# Testing Templates

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
    private static readonly TransactionControllerApiFixture Fixture = new();

    [OneTimeSetUp]
    public static Task OneTimeSetUp() => Fixture.InitializeAsync();

    [OneTimeTearDown]
    public static async Task OneTimeTearDown() => await Fixture.DisposeAsync();

    [SetUp]
    public Task SetUp() => Fixture.ResetAsync();
}
```

## API Full-Cycle Fixture Template (`<Controller>ApiFixture.cs`)
```csharp
internal sealed partial class TransactionControllerApiFixture : IAsyncDisposable
{
    private readonly TransactionApiFixtureRuntime _runtime = new();

    public Task InitializeAsync() => _runtime.InitializeAsync();

    public Task ResetAsync() => _runtime.ResetAsync();

    public ValueTask DisposeAsync() => _runtime.DisposeAsync();
}
```

## Migration Traceability Outputs
- Create matrix mapping old scenario name -> new test method.
- Create per-feature migration trace table with step/block parity status.
- Create controller-focused fixture/test map documenting fixture ownership.
