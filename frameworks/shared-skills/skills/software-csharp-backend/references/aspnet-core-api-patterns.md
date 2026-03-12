# ASP.NET Core API Patterns

## API style selection
- Use Controller-based APIs when you need filters, richer conventions, attribute routing control, or large teams maintaining many endpoints.
- Use Minimal APIs for smaller surface areas, vertical slices, and lightweight handlers with explicit dependency injection in delegates.
- Keep one style per module by default; mix styles only with clear boundaries.

## Middleware ordering baseline
- Keep error handling at the outer edge (`UseExceptionHandler` or equivalent middleware).
- Apply transport/security middlewares early (`HSTS`, `HTTPS redirection` where relevant).
- Place authentication before authorization.
- Place rate limiting and CORS before endpoint execution.
- Keep endpoint mapping (`MapControllers`, `MapGroup`) near the end.

## Validation and error contracts
- Validate at the transport boundary and return deterministic ProblemDetails responses.
- Use typed request models with explicit constraints; reject invalid input early.
- Keep domain/application failure mapping centralized (middleware/filter), not repeated per endpoint.
- Avoid leaking stack traces or internal exception details in production responses.

## Endpoint design defaults
- Propagate `CancellationToken` from endpoints to downstream services.
- Return stable response schemas and explicit status mappings (`200/201/400/404/409` at minimum).
- Use pagination contracts with stable sort keys for list endpoints.
- Require idempotency for retry-prone external write endpoints.

## Health checks and graceful shutdown
- Expose separate liveness and readiness endpoints.
- Keep liveness dependency-free; include critical dependencies in readiness.
- Configure shutdown timeout and ensure in-flight/background work drains safely.
- Ensure startup fails fast on invalid configuration before serving traffic.

## Security and traffic controls
- Restrict CORS origins explicitly per environment.
- Apply endpoint/policy-based authorization close to business actions.
- Configure rate limiting for externally exposed and expensive endpoints.
- Enforce secure headers and disable development-only diagnostics in production.
