public class CreateOrderHandler : ICommandHandler<CreateOrder>
{
    private readonly ILogger _logger;

    public async Task HandleAsync(CreateOrder command)
    {
        var __scopeItems = new Dictionary<string, object>
        {
            ["Id"] = command.Id
        };
        using var _scope = _logger.BeginScope(__scopeItems);
        _logger.LogInformation("Creating order {Id}", command.Id);
    }
}
