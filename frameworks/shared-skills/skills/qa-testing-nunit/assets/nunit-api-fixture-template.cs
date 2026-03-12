using Microsoft.Extensions.DependencyInjection;

namespace Company.Product.Tests.Api;

internal sealed partial class TransactionControllerApiFixture : IAsyncDisposable
{
    private readonly TransactionApiFixtureRuntime _runtime = new();

    internal ITransactionsApiClient ApiClient => _runtime.ApiClient;

    internal Task InitializeAsync() => _runtime.InitializeAsync();

    internal Task ResetAsync() => _runtime.ResetAsync();

    public ValueTask DisposeAsync() => _runtime.DisposeAsync();

    internal async Task<TransactionControllerApiFixture> GivenTransactionExistsAsync(PaymentTransactionDto transaction)
    {
        await _runtime.WithScopeAsync(async scope =>
        {
            var database = scope.ServiceProvider.GetRequiredService<IMongoDatabase>();
            var transactions = database.GetCollection<PaymentTransactionDto>("paymentTransactions");
            await transactions.InsertOneAsync(transaction);
        });

        return this;
    }

    internal async Task<TransactionControllerApiFixture> GivenOutboundTransferCanBeCreatedAsync()
    {
        await _runtime.WithWireMockAsync(server =>
        {
            var cardTransferWiremockServer = new CardTransferWiremockServer(server, Guid.NewGuid());
            cardTransferWiremockServer.GivenOutboundTransferCanBeCreated(new object());
        });

        return this;
    }
}

internal sealed class TransactionApiFixtureRuntime : IAsyncDisposable
{
    private DatabaseLauncher? _databaseLauncher;
    private WireMockServerWrapper? _wireMockServer;
    private CustomWebApplicationFactory? _factory;
    private IServiceScope? _scope;

    internal ITransactionsApiClient ApiClient { get; private set; } = null!;

    internal async Task InitializeAsync()
    {
        _databaseLauncher = new DatabaseLauncher();
        _ = await _databaseLauncher.LaunchAsync();

        _wireMockServer = new WireMockServerWrapper();
        _wireMockServer.Start();

        _factory = new CustomWebApplicationFactory(_wireMockServer.Url);
        var httpClient = _factory.CreateClient();
        ApiClient = RestService.For<ITransactionsApiClient>(httpClient);

        _scope = _factory.Services.CreateScope();
        await ResetAsync();
    }

    internal async Task ResetAsync()
    {
        if (_wireMockServer is not null)
        {
            _wireMockServer.Reset();
        }

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
        // Replace with DB cleanup for your storage.
        _ = serviceProvider;
        return Task.CompletedTask;
    }
}

internal interface ITransactionsApiClient;
internal interface IMongoDatabase
{
    IMongoCollection<TDocument> GetCollection<TDocument>(string name);
}

internal interface IMongoCollection<T>
{
    Task InsertOneAsync(T entity);
}

internal sealed class PaymentTransactionDto;
internal sealed class WireMockServerWrapper : IDisposable
{
    internal string Url => "http://127.0.0.1:8080";
    internal void Start() { }
    internal void Reset() { }
    public void Dispose() { }
}

internal sealed class CardTransferWiremockServer
{
    internal CardTransferWiremockServer(WireMockServerWrapper wireMockServer, Guid userId)
    {
        _ = wireMockServer;
        _ = userId;
    }

    internal void GivenOutboundTransferCanBeCreated(object request) => _ = request;
}

internal sealed class CustomWebApplicationFactory : IAsyncDisposable
{
    internal CustomWebApplicationFactory(string wireMockUrl) => _ = wireMockUrl;
    internal IServiceProvider Services { get; } = new ServiceCollection().BuildServiceProvider();
    internal HttpClient CreateClient() => new();
    public ValueTask DisposeAsync() => ValueTask.CompletedTask;
}

internal static class RestService
{
    internal static T For<T>(HttpClient client) where T : class
    {
        _ = client;
        throw new NotImplementedException();
    }
}
