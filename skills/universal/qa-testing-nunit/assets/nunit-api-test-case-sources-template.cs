using NUnit.Framework;

namespace Company.Product.Tests.Api;

// Use with [TestCaseSource(typeof(OrderApiTestCaseSources), nameof(OrderApiTestCaseSources.ValidOrders))].
internal static class OrderApiTestCaseSources
{
    internal static IEnumerable<TestCaseData> ValidOrders()
    {
        yield return new TestCaseData(new OrderRequestBuilder().Build(lineCount: 1)).SetName("Single line");
        yield return new TestCaseData(new OrderRequestBuilder().Build(lineCount: 3)).SetName("Multiple lines");
        yield return new TestCaseData(new OrderRequestBuilder().WithDiscount("WELCOME10").Build()).SetName("With discount");
    }

    internal static IEnumerable<TestCaseData> SupportedCurrencies()
    {
        yield return new TestCaseData("USD");
        yield return new TestCaseData("EUR");
        yield return new TestCaseData("GBP");
    }
}
