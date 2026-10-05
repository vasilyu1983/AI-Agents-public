using NUnit.Framework;

[assembly: Parallelizable(ParallelScope.Fixtures)]
// Size to the Docker host, not to CPU count: each parallel fixture here starts its own
// SQL Server container + WireMock + app host. Measure memory per fixture before raising.
[assembly: LevelOfParallelism(4)]

namespace Company.Product.Tests.Api;

[Category("Api")]
[TestFixture]
[Parallelizable]
[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]
internal sealed partial class OrdersControllerApiTest
{
    private static readonly OrdersControllerApiSharedRuntime SharedRuntime = new();
    private OrdersControllerApiFixture _fixture = null!;

    [OneTimeSetUp]
    public static Task OneTimeSetUp() => SharedRuntime.InitializeAsync();

    [OneTimeTearDown]
    public static async Task OneTimeTearDown() => await SharedRuntime.DisposeAsync();

    [SetUp]
    public async Task SetUp()
    {
        await SharedRuntime.ResetAsync();
        _fixture = new OrdersControllerApiFixture(SharedRuntime);
    }

    [Test]
    public async Task Should_Create_Order_When_Request_Is_Valid()
    {
        // Arrange
        var request = new OrderRequestBuilder().Build();

        // Act
        var response = await _fixture.ApiClient.CreateAsync(request, CancellationToken.None);

        // Assert
        Assert.That(response.StatusCode, Is.EqualTo(201));
    }
}

// CreateOrderRequest and OrderRequestBuilder live in nunit-api-request-builder-template.cs.

internal sealed class ApiResponse
{
    internal int StatusCode { get; init; }
}

// Declared once here; nunit-api-fixture-template.cs reuses it (a second declaration is CS0101).
internal interface IOrdersApiClient
{
    Task<ApiResponse> CreateAsync(CreateOrderRequest request, CancellationToken cancellationToken);
}
