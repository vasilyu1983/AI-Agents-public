using FluentResults;
using MediatR; // MediatR 13.0.0+ ships under a non-Apache licence file (12.5.0 was Apache-2.0); check terms or call the handler directly.
using Microsoft.Extensions.DependencyInjection;

namespace Company.Product.Tests.Handlers;

internal sealed partial class CreateEntityCommandHandlerFixture
{
    private readonly IMediator _mediator;

    internal CreateEntityCommand Command { get; private set; } = null!;

    internal CreateEntityCommandHandlerFixture(IServiceProvider services)
    {
        _mediator = services.GetRequiredService<IMediator>();
    }

    internal CreateEntityCommandHandlerFixture GivenCommand(CreateEntityCommand command)
    {
        Command = command;
        return this;
    }

    internal CreateEntityCommandHandlerFixture GivenValidationPassed()
    {
        // Configure mocks/stubs for success path.
        return this;
    }

    internal CreateEntityCommandHandlerFixture GivenDependencyFailure()
    {
        // Configure mocks/stubs for failure path.
        return this;
    }

    internal Task<Result<CreateEntityResult>> SendAsync(CreateEntityCommand command)
        => _mediator.Send(command, CancellationToken.None);
}

internal sealed record CreateEntityCommand(Guid UserId) : IRequest<Result<CreateEntityResult>>;

internal sealed record CreateEntityResult(Guid EntityId);
