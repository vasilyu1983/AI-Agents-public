using NUnit.Framework;

[assembly: Parallelizable(ParallelScope.Fixtures)]
[assembly: LevelOfParallelism(4)]

namespace Company.Product.Tests.Api;

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

    [Test]
    public async Task Should_Create_Transaction_When_Request_Is_Valid()
    {
        // Arrange
        var request = new CreateTransactionRequest();

        // Act
        var response = await _fixture.ApiClient.CreateAsync(request, CancellationToken.None);

        // Assert
        Assert.That(response.StatusCode, Is.EqualTo(201));
    }
}

internal sealed class CreateTransactionRequest;

internal sealed class ApiResponse
{
    internal int StatusCode { get; init; }
}

internal interface ITransactionsApiClient
{
    Task<ApiResponse> CreateAsync(CreateTransactionRequest request, CancellationToken cancellationToken);
}
