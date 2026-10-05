using Microsoft.Extensions.DependencyInjection;
using Refit;

namespace Company.Product.Tests.Api;

// Companion files (copy together; types are declared once across the set):
// - nunit-api-tests-template.cs          -> IOrdersApiClient, OrdersControllerApiTest
// - nunit-wiremock-template.cs           -> WireMockServerWrapper, DependencyWiremockServer
// - nunit-database-launcher-template.cs  -> DatabaseLauncher

internal sealed partial class OrdersControllerApiFixture : IAsyncDisposable
{
    private readonly OrdersControllerApiSharedRuntime _runtime;

    internal IOrdersApiClient ApiClient => _runtime.ApiClient;

    internal OrdersControllerApiFixture(OrdersControllerApiSharedRuntime runtime)
        => _runtime = runtime;

    public ValueTask DisposeAsync() => ValueTask.CompletedTask;

    internal async Task<OrdersControllerApiFixture> GivenOrderExistsAsync(OrderDto order)
    {
        await _runtime.WithScopeAsync(async scope =>
        {
            var store = scope.ServiceProvider.GetRequiredService<IOrdersStore>();
            await store.InsertAsync(order);
        });

        return this;
    }

    internal async Task<OrdersControllerApiFixture> GivenUpstreamDependencySucceedsAsync()
    {
        await _runtime.WithWireMockAsync(server =>
        {
            var dependency = new DependencyWiremockServer(server);
            dependency.GivenSuccess();
        });

        return this;
    }
}

internal sealed class OrdersControllerApiSharedRuntime : IAsyncDisposable
{
    private DatabaseLauncher? _databaseLauncher;
    private WireMockServerWrapper? _wireMockServer;
    private CustomWebApplicationFactory? _factory;
    private IServiceScope? _scope;

    internal IOrdersApiClient ApiClient { get; private set; } = null!;

    internal async Task InitializeAsync()
    {
        _databaseLauncher = new DatabaseLauncher();
        var database = await _databaseLauncher.LaunchAsync();

        _wireMockServer = new WireMockServerWrapper();
        _wireMockServer.Start(); // dynamic port; the URL is read back below

        _factory = new CustomWebApplicationFactory(database.MainConnectionString, _wireMockServer.Url);
        var httpClient = _factory.CreateClient();
        ApiClient = RestService.For<IOrdersApiClient>(httpClient);

        _scope = _factory.Services.CreateScope();
        await ResetAsync();
    }

    internal async Task ResetAsync()
    {
        // This runtime is shared across test cases for one controller fixture.
        // Keep child-test parallelism disabled and rebuild per-test facade state in SetUp.
        _wireMockServer?.Reset();

        if (_scope is not null)
        {
            await CleanupStateAsync(_scope.ServiceProvider);
        }
    }

    internal Task WithScopeAsync(Func<IServiceScope, Task> action)
    {
        if (_scope is null)
        {
            throw new InvalidOperationException("Fixture runtime is not initialized.");
        }

        return action(_scope);
    }

    internal Task WithWireMockAsync(Action<WireMockServerWrapper> action)
    {
        if (_wireMockServer is null)
        {
            throw new InvalidOperationException("WireMock server is not initialized.");
        }

        action(_wireMockServer);
        return Task.CompletedTask;
    }

    public async ValueTask DisposeAsync()
    {
        _scope?.Dispose();

        if (_factory is not null)
        {
            await _factory.DisposeAsync();
        }

        _wireMockServer?.Dispose();

        if (_databaseLauncher is not null)
        {
            await _databaseLauncher.DisposeAsync();
        }
    }

    private static Task CleanupStateAsync(IServiceProvider serviceProvider)
    {
        // Replace with DB cleanup for your storage (e.g. a Respawn-style reset).
        _ = serviceProvider;
        return Task.CompletedTask;
    }
}

// ---- Placeholders: replace with your application's real types ----

internal interface IOrdersStore
{
    Task InsertAsync(OrderDto order);
}

internal sealed class OrderDto;

// Stand-in for your WebApplicationFactory<Program> subclass that overrides the
// connection string and upstream base URL in ConfigureWebHost.
internal sealed class CustomWebApplicationFactory : IAsyncDisposable
{
    internal CustomWebApplicationFactory(string connectionString, string upstreamBaseUrl)
    {
        _ = connectionString;
        _ = upstreamBaseUrl;
    }

    internal IServiceProvider Services { get; } = new ServiceCollection().BuildServiceProvider();
    internal HttpClient CreateClient() => new() { BaseAddress = new Uri("http://localhost") };
    public ValueTask DisposeAsync() => ValueTask.CompletedTask;
}
