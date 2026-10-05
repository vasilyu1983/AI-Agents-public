# ASP.NET Core API Patterns

## API style selection
- Use Controller-based APIs when you need filters, richer conventions, attribute routing control, or large teams maintaining many endpoints.
- Use Minimal APIs for smaller surface areas, vertical slices, and lightweight handlers with explicit dependency injection in delegates.
- Keep one style per module by default; mix styles only with clear boundaries.
- Treat Native AOT as an opt-in deployment profile for latency/footprint-sensitive, high-density, or fast-cold-start services (serverless, sidecars), not a default. Verify reflection-heavy libraries and serialization behavior before choosing it.
- Do not choose Native AOT by default when the service depends on any of the following:
  - EF Core. Microsoft documents EF NativeAOT and precompiled queries as "highly experimental" and recommends against deploying them to production.
  - Dynamic plugin or assembly loading.
  - Third-party libraries without published trim/AOT annotations.
- When AOT is a hard requirement, use raw ADO.NET or Dapper.AOT (a build-time interceptor generator) for the data layer. Plain Dapper relies on runtime reflection and IL emit, so it is not AOT-safe. Treat IL2xxx/IL3xxx publish warnings as build failures.
- Configure `JsonSerializerContext` source generation for `System.Text.Json` instead of relying on reflection-based (de)serialization.

## Middleware ordering baseline
- Keep error handling at the outer edge (`UseExceptionHandler` or equivalent middleware).
- Apply transport/security middlewares early (`HSTS`, `HTTPS redirection` where relevant).
- Register request timeout and rate-limiting middleware explicitly when the service is internet-facing or latency-sensitive.
- Place authentication before authorization.
- Place rate limiting and CORS before endpoint execution.
- Keep endpoint mapping (`MapControllers`, `MapGroup`) near the end.

## Validation and error contracts
- Validate at the transport boundary and return deterministic ProblemDetails responses.
- On `.NET 10`, minimal APIs have built-in DataAnnotations validation. Register it with `builder.Services.AddValidation()`. Keep FluentValidation only where rules are cross-field, async, or already standardized in the repo.
- Prefer `AddProblemDetails()` plus `IExceptionHandler` for centralized error translation.
- In `.NET 10`, review `SuppressDiagnosticsCallback` so handled exceptions still emit the diagnostics your operators expect.
- Use typed request models with explicit constraints; reject invalid input early.
- Keep domain/application failure mapping centralized (middleware/filter), not repeated per endpoint.
- Avoid leaking stack traces or internal exception details in production responses.

## Endpoint design defaults
- Propagate `CancellationToken` from endpoints to downstream services.
- Return stable response schemas and explicit status mappings (`200/201/400/404/409` at minimum).
- Use pagination contracts with stable sort keys for list endpoints.
- Require idempotency for retry-prone external write endpoints.
- Prefer `AddOpenApi()` / `MapOpenApi()` for built-in OpenAPI support. Treat `.WithOpenApi()` as deprecated in `.NET 10`. Generated documents default to OpenAPI 3.1 on .NET 10, so check client generators that expect 3.0.
- Stream large result sets with `IAsyncEnumerable<T>` (serialized incrementally by `System.Text.Json`) instead of buffering a `List<T>`. Pass the request `CancellationToken` through, for example with `[EnumeratorCancellation]`.
- For one-way server push, `.NET 10` adds `TypedResults.ServerSentEvents(...)` over an `IAsyncEnumerable<T>`. Use SignalR or WebSockets only when you need bidirectional traffic or fan-out groups.

## Health checks and graceful shutdown
- Expose separate liveness and readiness endpoints.
- Keep liveness dependency-free; include critical dependencies in readiness.
- Configure shutdown timeout and ensure in-flight/background work drains safely.
- Ensure startup fails fast on invalid configuration before serving traffic.

## Security and traffic controls
- Restrict CORS origins explicitly per environment.
- Apply endpoint/policy-based authorization close to business actions.
- Configure rate limiting for externally exposed and expensive endpoints via explicit named policies. Set `RejectionStatusCode` to 429; the middleware defaults to 503, which clients and proxies read as an outage.
- Apply request timeout policies per endpoint group when latency budgets differ materially.
- Enforce secure headers and disable development-only diagnostics in production.
