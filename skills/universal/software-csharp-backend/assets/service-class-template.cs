using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace Company.Product.Feature;

public interface IProcessOrderService
{
    Task<ProcessOrderResult> ExecuteAsync(ProcessOrderCommand command, CancellationToken cancellationToken);
}

public sealed record ProcessOrderCommand(Guid OrderId, string RequestedBy);

public sealed record ProcessOrderResult(bool Success, string? ErrorCode)
{
    public static ProcessOrderResult Ok() => new(true, null);

    public static ProcessOrderResult Fail(string errorCode) => new(false, errorCode);
}

public sealed class ProcessOrderService : IProcessOrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger<ProcessOrderService> _logger;

    public ProcessOrderService(IOrderRepository orderRepository, ILogger<ProcessOrderService> logger)
    {
        _orderRepository = orderRepository;
        _logger = logger;
    }

    public async Task<ProcessOrderResult> ExecuteAsync(ProcessOrderCommand command, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(command);

        var order = await _orderRepository.GetByIdAsync(command.OrderId, cancellationToken);
        if (order is null)
        {
            return ProcessOrderResult.Fail("order_not_found");
        }

        if (!order.CanProcess())
        {
            return ProcessOrderResult.Fail("order_invalid_state");
        }

        order.MarkProcessed(command.RequestedBy);

        await _orderRepository.SaveAsync(order, cancellationToken);

        _logger.LogInformation("Order {OrderId} processed by {RequestedBy}", command.OrderId, command.RequestedBy);

        return ProcessOrderResult.Ok();
    }
}

public interface IOrderRepository
{
    Task<OrderAggregate?> GetByIdAsync(Guid orderId, CancellationToken cancellationToken);

    Task SaveAsync(OrderAggregate order, CancellationToken cancellationToken);
}

public sealed class OrderAggregate
{
    public bool CanProcess() => true;

    public void MarkProcessed(string requestedBy)
    {
        _ = requestedBy;
    }
}
