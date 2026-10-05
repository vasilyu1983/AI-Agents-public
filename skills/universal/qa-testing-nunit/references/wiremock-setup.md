# WireMock Setup

## Purpose
Use this guide to simulate HTTP dependencies deterministically. The copy-ready wrapper and dependency-helper code lives in [`assets/nunit-wiremock-template.cs`](../assets/nunit-wiremock-template.cs); this file holds the rules.

## Setup Pattern
- Start one WireMock server per test fixture, or per test when isolation requires it. `WireMockServer.Start(...)` without a port binds a free port; read the URL back from `server.Url` and inject it into the app under test. Never hard-code the stub host or port.
- Bind stubs to explicit method, path, headers, and body predicates.
- Return deterministic status/body/latency for each scenario.
- For API full-cycle suites, start one wrapper in `[OneTimeSetUp]` and stop it in `[OneTimeTearDown]`.
- Reconfigure stubs per test through fixture `Given...` helper methods.
- Use one typed helper class per upstream dependency (for example `InventoryApiWiremockServer`) and keep raw `Request.Create()` calls inside these helpers.
- Give every helper the same constructor shape (it takes the shared server wrapper). Pass per-scenario values, such as the acting user ID, into the `Given...` method, not into shared constructor state.
- In API component suites, couple one wrapper instance to one controller-fixture runtime so fixture classes can run in parallel without cross-controller stub state.
- If a controller fixture shares one runtime across test cases, keep child-test parallelism disabled and reset mappings before each test.

## Stub Rules
- Keep stub definitions close to scenario intent.
- Use named helpers for common upstream responses.
- Reset mappings and request logs between tests (`server.Reset()`).

## Verification
- Assert expected outbound calls (count + payload semantics) from the server's request log.
- Assert no unexpected calls for negative scenarios.
- Keep provider-specific stubs grouped in fixture partial files (`Fixture.ProviderA.cs`, `Fixture.ProviderB.cs`, etc.).

## Failure Simulation
- Model timeout, 4xx, 5xx, malformed payload, and slow responses.
- Verify API/component mapping behavior for each failure class.
