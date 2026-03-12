# WireMock Setup

## Purpose
Use this guide to simulate HTTP dependencies deterministically.

## Setup Pattern
- Start one WireMock server per test fixture or per test when isolation requires it.
- Bind stubs to explicit method, path, headers, and body predicates.
- Return deterministic status/body/latency for each scenario.
- For API full-cycle suites, start one wrapper in `[OneTimeSetUp]` and stop in `[OneTimeTearDown]`.
- Reconfigure stubs per test through fixture `Given...` helper methods.
- Use one typed helper class per upstream dependency (`CustomerTariffApiWiremockServer`, `GoRulesWiremockServer`, etc.) and keep raw `Request.Create()` calls inside these helpers.
- Keep helper class constructors uniform: `public sealed class XyzWiremockServer(WireMockServerWrapper serverWrapper)` with `private readonly WireMockServer _wireMockServer = serverWrapper.Server;`.
- In API component suites, couple one wrapper instance to one fixture instance so fixtures can run in parallel without shared stub state.

## Template: Wrapper
```csharp
public sealed class WireMockServerWrapper : IDisposable
{
    private WireMockServer _wireMockServer = null!;

    public WireMockServer Server => _wireMockServer;
    public HttpClient HttpClient => _wireMockServer.CreateClient();
    public string Url => _wireMockServer.Url!;

    public void Start()
    {
        Start(new JsonSerializerSettings
        {
            NullValueHandling = NullValueHandling.Include
        });
    }

    public void Start(JsonSerializerSettings jsonSerializerSettings)
    {
        _wireMockServer = WireMockServer.Start(new WireMockServerSettings
        {
            StartAdminInterface = true,
            JsonSerializerSettings = jsonSerializerSettings
        });
    }

    public void Reset() => _wireMockServer.Reset();
    public void Dispose() => _wireMockServer.Dispose();
    public void Stop() => Dispose();
}
```

## Template: Dependency Helper
```csharp
public sealed class CustomerTariffApiWiremockServer(WireMockServerWrapper serverWrapper, Guid userId)
{
    private readonly WireMockServer _wireMockServer = serverWrapper.Server;

    public void GivenCustomerTariffs(Guid customerId, CustomerTariffsResponse response)
    {
        _wireMockServer
            .Given(Request.Create()
                .UsingMethod("GET")
                .WithPath("/customer/tariffs")
                .WithHeader("X-On-Behalf-Of-User", userId.ToString())
                .WithParam("customerId", customerId.ToString()))
            .RespondWith(Response.Create()
                .WithStatusCode(200)
                .WithHeader("Content-Type", "application/json")
                .WithBodyAsJson(_ => response));
    }
}
```

## Stub Rules
- Keep stub definitions close to scenario intent.
- Use named helpers for common upstream responses.
- Reset mappings and request logs between tests.

## Verification
- Assert expected outbound calls (count + payload semantics).
- Assert no unexpected calls for negative scenarios.
- Keep provider-specific stubs grouped in fixture partial files (`Fixture.Card2Card.cs`, `Fixture.Crypto.cs`, etc.).

## Failure Simulation
- Model timeout, 4xx, 5xx, malformed payload, and slow responses.
- Verify API/component mapping behavior for each failure class.
