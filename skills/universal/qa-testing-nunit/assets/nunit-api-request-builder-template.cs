using Bogus;

namespace Company.Product.Tests.Api;

// Deterministic builder: seed Bogus so a failing case replays with the same data.
internal sealed class OrderRequestBuilder
{
    private const int Seed = 12345;

    private readonly Faker<CreateOrderRequest> _targetFaker;
    private readonly Faker<OrderLineRequest> _lineFaker;
    private Faker<DiscountRequest>? _discountFaker;

    internal OrderRequestBuilder()
    {
        _targetFaker = new Faker<CreateOrderRequest>().UseSeed(Seed);
        _lineFaker = new Faker<OrderLineRequest>()
            .UseSeed(Seed)
            .RuleFor(x => x.Currency, _ => "USD")
            .RuleFor(x => x.Quantity, f => f.Random.Int(1, 5));
    }

    internal OrderRequestBuilder WithCustomer(Guid customerId)
    {
        _targetFaker.RuleFor(x => x.CustomerId, customerId);
        return this;
    }

    internal OrderRequestBuilder WithCurrency(string currency)
    {
        _lineFaker.RuleFor(x => x.Currency, currency);
        return this;
    }

    internal OrderRequestBuilder WithDiscount(string code)
    {
        _discountFaker = new Faker<DiscountRequest>()
            .UseSeed(Seed)
            .RuleFor(x => x.Code, code);
        return this;
    }

    internal OrderRequestBuilder WithoutDiscount()
    {
        _discountFaker = null;
        return this;
    }

    internal CreateOrderRequest Build(int lineCount = 1)
    {
        return _targetFaker
            .RuleFor(x => x.Lines, _ => _lineFaker.Generate(lineCount))
            .RuleFor(x => x.Discount, _ => _discountFaker?.Generate())
            .Generate();
    }
}

// ---- Placeholders: replace with your API's request contracts ----

internal sealed class CreateOrderRequest
{
    public Guid CustomerId { get; set; }

    public IList<OrderLineRequest> Lines { get; set; } = [];

    public DiscountRequest? Discount { get; set; }
}

internal sealed class OrderLineRequest
{
    public string Currency { get; set; } = string.Empty;

    public int Quantity { get; set; }
}

internal sealed class DiscountRequest
{
    public string Code { get; set; } = string.Empty;
}
