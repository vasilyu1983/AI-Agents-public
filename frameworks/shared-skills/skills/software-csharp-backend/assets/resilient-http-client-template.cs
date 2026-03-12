using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Http.Resilience;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace Company.Product.Integrations;

public static class OrdersApiClientRegistration
{
    public static IServiceCollection AddOrdersApiClient(this IServiceCollection services)
    {
        services
            .AddHttpClient<IOrdersApiClient, OrdersApiClient>((sp, client) =>
            {
                var options = sp.GetRequiredService<IOptions<OrdersApiOptions>>().Value;
                client.BaseAddress = new Uri(options.BaseUrl);
                client.Timeout = TimeSpan.FromSeconds(options.TimeoutSeconds);
            })
            .AddStandardResilienceHandler();

        return services;
    }
}

public sealed class OrdersApiOptions
{
    public string BaseUrl { get; init; } = string.Empty;

    public int TimeoutSeconds { get; init; } = 5;
}

public interface IOrdersApiClient
{
    Task<OrderStatusResponse> GetStatusAsync(Guid orderId, CancellationToken cancellationToken);
}

public sealed class OrdersApiClient : IOrdersApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OrdersApiClient> _logger;

    public OrdersApiClient(HttpClient httpClient, ILogger<OrdersApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<OrderStatusResponse> GetStatusAsync(Guid orderId, CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync($"/orders/{orderId}/status", cancellationToken);

        if (response.StatusCode == HttpStatusCode.NotFound)
        {
            return new OrderStatusResponse(orderId, "not_found");
        }

        response.EnsureSuccessStatusCode();

        var payload = await response.Content.ReadFromJsonAsync<OrderStatusResponse>(cancellationToken: cancellationToken);
        if (payload is null)
        {
            _logger.LogError("Orders API returned empty payload for order {OrderId}", orderId);
            throw new InvalidOperationException("Orders API response payload was empty.");
        }

        return payload;
    }
}

public sealed record OrderStatusResponse(Guid OrderId, string Status);
