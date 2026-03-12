using AwesomeAssertions;
using Microsoft.Extensions.DependencyInjection;
using NUnit.Framework;

namespace Company.Product.Tests.Handlers;

[Parallelizable]
[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]
[TestOf(typeof(CreateEntityCommandHandler))]
internal sealed partial class CreateEntityCommandHandlerTests
{
    private CreateEntityCommandHandlerFixture _fixture = null!;

    [SetUp]
    public Task SetUp()
    {
        IServiceProvider services = BuildServices();
        _fixture = new CreateEntityCommandHandlerFixture(services);
        return Task.CompletedTask;
    }

    [Test]
    public async Task Should_Create_Entity_When_Request_Is_Valid()
    {
        // Arrange
        var command = new CreateEntityCommand(Guid.NewGuid());
        _fixture.GivenCommand(command)
            .GivenValidationPassed();

        // Act
        var result = await _fixture.SendAsync(command);

        // Assert
        result.Should().BeSuccessful();
    }

    private static IServiceProvider BuildServices()
    {
        var services = new ServiceCollection();

        // Register handler and test doubles here.
        return services.BuildServiceProvider();
    }
}

internal sealed class CreateEntityCommandHandler;
