using System;

namespace Company.Product.Tests.Builders;

public sealed class OrderBuilder
{
    private Guid _orderId = Guid.NewGuid();
    private string _state = "Created";
    private string _requestedBy = "test-user";

    public OrderBuilder WithOrderId(Guid orderId)
    {
        _orderId = orderId;
        return this;
    }

    public OrderBuilder WithState(string state)
    {
        _state = state;
        return this;
    }

    public OrderBuilder WithRequestedBy(string requestedBy)
    {
        _requestedBy = requestedBy;
        return this;
    }

    public TestOrder Build()
    {
        return new TestOrder(_orderId, _state, _requestedBy);
    }
}

public sealed record TestOrder(Guid OrderId, string State, string RequestedBy);
