public class CreateOrderHandler : ICommandHandler<CreateOrder>
{
    private readonly ILogger _logger;

    public async Task HandleAsync(CreateOrder command)
    {
        _logger.LogInformation("Creating order " + command.Id);
    }
}
