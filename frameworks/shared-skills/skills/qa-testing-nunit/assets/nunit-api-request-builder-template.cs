using Bogus;

namespace Company.Product.Tests.Api;

internal sealed class TransactionRequestBuilder
{
    private readonly Faker<CreatePaymentTransactionRequest> _targetFaker;
    private Faker<TransactionDetailsRequest> _detailsFaker;
    private Faker<CurrencyConversionRequest>? _conversionFaker;

    internal TransactionRequestBuilder()
    {
        _targetFaker = new Faker<CreatePaymentTransactionRequest>();
        _detailsFaker = new Faker<TransactionDetailsRequest>()
            .RuleFor(x => x.Currency, _ => "USD");
    }

    internal TransactionRequestBuilder WithParties(IList<Party> parties)
    {
        _targetFaker.RuleFor(x => x.ParticipatingParties, parties);
        return this;
    }

    internal TransactionRequestBuilder WithCurrency(string currency)
    {
        _detailsFaker.RuleFor(x => x.Currency, currency);
        return this;
    }

    internal TransactionRequestBuilder WithCurrencyConversion(string receivingCurrency)
    {
        _conversionFaker = new Faker<CurrencyConversionRequest>()
            .RuleFor(x => x.CurrencyRateHash, Guid.NewGuid().ToString("D"))
            .RuleFor(x => x.ReceivingCurrency, receivingCurrency);
        return this;
    }

    internal TransactionRequestBuilder WithoutCurrencyConversion()
    {
        _conversionFaker = null;
        return this;
    }

    internal CreatePaymentTransactionRequest Build()
    {
        return _targetFaker
            .RuleFor(x => x.TransactionDetails, _detailsFaker.Generate())
            .RuleFor(x => x.CurrencyConversion, _conversionFaker?.Generate())
            .Generate();
    }
}

internal sealed class CreatePaymentTransactionRequest
{
    public IList<Party> ParticipatingParties { get; set; } = [];

    public TransactionDetailsRequest TransactionDetails { get; set; } = new();

    public CurrencyConversionRequest? CurrencyConversion { get; set; }
}

internal sealed class TransactionDetailsRequest
{
    public string Currency { get; set; } = string.Empty;
}

internal sealed class CurrencyConversionRequest
{
    public string CurrencyRateHash { get; set; } = string.Empty;

    public string ReceivingCurrency { get; set; } = string.Empty;
}

internal sealed class Party;
