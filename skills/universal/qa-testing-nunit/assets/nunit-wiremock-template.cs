using Newtonsoft.Json;
using WireMock.RequestBuilders;
using WireMock.ResponseBuilders;
using WireMock.Server;
using WireMock.Settings;

public sealed class WireMockServerWrapper : IDisposable
{
    private WireMockServer _wireMockServer = null!;

    public WireMockServer Server => _wireMockServer;
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
}

public sealed class DependencyWiremockServer(WireMockServerWrapper serverWrapper)
{
    private readonly WireMockServer _wireMockServer = serverWrapper.Server;

    public void GivenSuccess()
    {
        _wireMockServer
            .Given(Request.Create()
                .UsingMethod("GET")
                .WithPath("/v1/resource"))
            .RespondWith(Response.Create()
                .WithStatusCode(200)
                .WithHeader("Content-Type", "application/json")
                .WithBodyAsJson(_ => new { ok = true }));
    }
}
