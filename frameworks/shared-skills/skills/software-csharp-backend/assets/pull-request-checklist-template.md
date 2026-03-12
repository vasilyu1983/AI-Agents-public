# Backend Pull Request Checklist

## Scope and architecture
- [ ] The change has a clear use-case boundary and does not expand unrelated service responsibilities.
- [ ] Dependency direction and layer boundaries remain correct.
- [ ] API/CQRS endpoint changes use `$csharp-api-cqrs` conventions when applicable.

## Code quality
- [ ] Naming, nullability, and async/cancellation handling follow team standards.
- [ ] Expected business failures are modeled explicitly (not exception-driven).
- [ ] Configuration is strongly typed and validated on startup.

## Data access
- [ ] Query/write shape is intentional, and N+1 risks are addressed.
- [ ] Pagination strategy is explicit and stable.
- [ ] Transaction/idempotency behavior is documented for retries and duplicate delivery.

## Reliability and operations
- [ ] Timeouts/retries/circuit settings are explicit for outbound dependencies.
- [ ] Structured logs, traces, and metrics were added or updated for new behavior.
- [ ] Health checks still represent real readiness/liveness semantics.

## Security
- [ ] Input validation and authorization checks are present at correct boundaries.
- [ ] No secrets, tokens, or sensitive data are exposed in code or telemetry.
- [ ] Secure defaults are preserved (least privilege, production-safe settings).

## Testing and delivery
- [ ] Unit/component/integration tests match the risk of the change.
- [ ] New behavior includes positive and failure-path coverage.
- [ ] Flaky patterns were avoided (no arbitrary sleeps, no shared mutable fixture state).
- [ ] Validation commands and outcomes are listed in the PR description.
