namespace Company.Product.Tests.Api;

internal static class TransactionApiTestCaseSources
{
    internal static IEnumerable<TestCaseData> ValidPayouts()
    {
        yield return new TestCaseData(PayoutFakers.CardPayoutFaker().Generate());
        yield return new TestCaseData(PayoutFakers.CryptoPayoutFaker().Generate());
        yield return new TestCaseData(PayoutFakers.WalletPayoutFaker().Generate());
    }

    internal static IEnumerable<TestCaseData> SupportedCurrencies()
    {
        yield return new TestCaseData("USD");
        yield return new TestCaseData("EUR");
        yield return new TestCaseData("GBP");
    }
}

internal static class PayoutFakers
{
    internal static Bogus.Faker<object> CardPayoutFaker() => new Bogus.Faker<object>();

    internal static Bogus.Faker<object> CryptoPayoutFaker() => new Bogus.Faker<object>();

    internal static Bogus.Faker<object> WalletPayoutFaker() => new Bogus.Faker<object>();
}
