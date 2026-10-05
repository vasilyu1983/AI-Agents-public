# Dotnet Coding Standards

## Project structure
- Organize by capability and layer, not by technical type only.
- Keep API/presentation thin; place use-case logic in application layer.
- Keep infrastructure adapters isolated behind interfaces.
- Set solution-wide build rules (nullable, warnings as errors, analyzer level) once in `Directory.Build.props`, not per project.

## Dependency boundaries
- Enforce inward dependency direction: presentation -> application -> domain.
- Prevent domain from referencing infrastructure packages.
- Avoid static service locators and hidden global dependencies.

## Dependency injection
- Register dependencies by role and lifetime:
  - `Singleton` for stateless/shared expensive resources.
  - `Scoped` for request-bound services and data sessions.
  - `Transient` for lightweight stateless components.
- Validate container at startup when possible.
- A singleton or `BackgroundService` that needs a scoped service (such as `DbContext`) creates a scope per unit of work through `IServiceScopeFactory`; never inject the scoped service directly.
- Prefer constructor injection; avoid method/property injection except narrow framework cases.

## Outbound HTTP clients
- Always resolve `HttpClient` through `IHttpClientFactory` (`AddHttpClient<TClient>()` or a named client) instead of `new HttpClient()` per call or per request — pooled `SocketsHttpHandler` instances avoid socket exhaustion under load.
- Never use a single `static readonly HttpClient` as a substitute for the factory unless you also configure `PooledConnectionLifetime` yourself; a bare static instance never rotates connections and goes DNS-stale after upstream failover.
- Combine `AddHttpClient` with `AddStandardResilienceHandler()` (see `references/reliability-and-resilience.md`) rather than hand-rolling retry/timeout logic per client. Add it once per client: not on top of a handler that `ConfigureHttpClientDefaults` already adds.

## Serialization
- Default to `System.Text.Json` for new code; it is the built-in, source-generator-capable, allocation-lean serializer and the one ASP.NET Core's model binding/OpenAPI pipeline assumes.
- Reach for `Newtonsoft.Json` only when the repository already depends on a Newtonsoft-only feature it cannot migrate off (e.g., certain contract resolvers, `JsonConverter` ecosystems, or a third-party library that hard-requires it) — do not add it to a new project by habit.
- Use `JsonSerializerContext` source generation for hot paths and any Native AOT/trimmed deployment; reflection-based `System.Text.Json` still works outside AOT but source generation is strictly faster and trim-safe.

## Garbage collector mode
- ASP.NET Core defaults to Server GC, which sizes heap count to the visible processor count — appropriate for a dedicated, CPU-bound API host but prone to over-allocating memory on small or shared containers.
- On `net8.0`, DATAS is opt-in. For high-density hosting (many small containers per node) or memory-constrained pods, either enable DATAS (`DOTNET_GCDynamicAdaptationMode=1`) or switch to Workstation GC.
- On `net9.0`+, DATAS is on by default, so there is nothing to enable. The live question is the reverse. Microsoft's benchmark shows DATAS costs a few percent of peak throughput in exchange for a much smaller working set. On dedicated, throughput-bound pods, disable it only after measuring, and check the DATAS docs page for the target framework's current behavior.
- Treat GC mode as a measured deployment decision (watch working-set and pause-time telemetry after a change), not a default left unexamined.

## Configuration and options
- Bind strongly typed options per bounded context.
- Validate options on startup (`ValidateOnStart`) for critical settings.
- Keep secrets outside source control and outside plain config files.
- Separate runtime policies (timeouts, retry counts, limits) into options.

## Layering rules
- Keep transport DTOs and persistence documents outside core domain models.
- Map data at boundaries; do not leak ORM/driver entities into domain/application.
- Keep cross-cutting concerns (logging, metrics, auth) in decorators/middleware where possible.

## Implementation checklist
- Does each project have one clear responsibility?
- Does each dependency point inward?
- Are options typed, validated, and environment-safe?
