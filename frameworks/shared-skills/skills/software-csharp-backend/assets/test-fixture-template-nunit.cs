using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using NUnit.Framework;

namespace Company.Product.Tests.Component;

[TestFixture]
[Category("ComponentTests")]
public sealed class ProcessOrderServiceTests
{
    private ServiceProvider _serviceProvider = null!;
    private CancellationTokenSource _cancellationTokenSource = null!;

    [SetUp]
    public async Task SetUpAsync()
    {
        _cancellationTokenSource = new CancellationTokenSource(TimeSpan.FromSeconds(10));

        var services = new ServiceCollection();
        services.AddLogging();
        services.AddScoped<IOrderRepository, InMemoryOrderRepository>();
        services.AddScoped<IProcessOrderService, ProcessOrderService>();

        _serviceProvider = services.BuildServiceProvider(validateScopes: true);

        await SeedAsync(_serviceProvider, _cancellationTokenSource.Token);
    }

    [TearDown]
    public async Task TearDownAsync()
    {
        _cancellationTokenSource.Cancel();
        _cancellationTokenSource.Dispose();

        await _serviceProvider.DisposeAsync();
    }

    [Test]
    public async Task ExecuteAsync_WhenOrderExists_ReturnsSuccess()
    {
        using var scope = _serviceProvider.CreateScope();
        var service = scope.ServiceProvider.GetRequiredService<IProcessOrderService>();

        var result = await service.ExecuteAsync(new ProcessOrderCommand(Guid.Parse("11111111-1111-1111-1111-111111111111"), "tester"), _cancellationTokenSource.Token);

        Assert.That(result.Success, Is.True);
        Assert.That(result.ErrorCode, Is.Null);
    }

    private static Task SeedAsync(IServiceProvider serviceProvider, CancellationToken cancellationToken)
    {
        _ = serviceProvider;
        _ = cancellationToken;
        return Task.CompletedTask;
    }

    private sealed class InMemoryOrderRepository : IOrderRepository
    {
        public Task<OrderAggregate?> GetByIdAsync(Guid orderId, CancellationToken cancellationToken)
        {
            _ = cancellationToken;
            var exists = orderId == Guid.Parse("11111111-1111-1111-1111-111111111111");
            return Task.FromResult(exists ? new OrderAggregate() : null);
        }

        public Task SaveAsync(OrderAggregate order, CancellationToken cancellationToken)
        {
            _ = order;
            _ = cancellationToken;
            return Task.CompletedTask;
        }
    }
}
