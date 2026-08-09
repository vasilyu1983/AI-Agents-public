# Code Review Checklist

## Severity rubric
- `Blocker`: correctness or security defect with production impact or data-risk potential.
- `High`: high-confidence regression, reliability break, or major operability gap.
- `Medium`: maintainability issue likely to create future defects.
- `Low`: stylistic or minor clarity improvements.

## Correctness and clarity
- Is behavior understandable without reading unrelated files?
- Are edge cases and failure modes explicitly handled?
- Do method and type names match business intent?

## Architecture and boundaries
- Does dependency direction remain inward?
- Is business logic isolated from transport and persistence concerns?
- Is cross-cutting logic implemented centrally rather than duplicated?
- For CQRS handlers, does `Handle` remain boundary-only with a small functional `DoHandle` pipeline?

## Data and performance
- Does query shape avoid N+1 and over-fetching?
- Are indexes and pagination strategy aligned with access patterns?
- Are transactions scoped and idempotency considerations explicit?

## Reliability
- Are timeout, retry, and circuit policies explicit for outbound I/O?
- Is cancellation propagated through async calls?
- Are background jobs idempotent and observable?

## Testing
- Do tests cover happy path plus expected failures?
- Are tests deterministic and free from unnecessary sleeps/time coupling?
- Is the test scope appropriate (unit vs integration vs component)?

## Observability and operations
- Are logs structured and free from sensitive data?
- Are metrics/traces sufficient to diagnose production failures?
- Are health checks meaningful for orchestration decisions?

## Security
- Are input validation and authorization checks complete?
- Are secrets handled via secure providers and never hard-coded?
- Are secure defaults preserved (least privilege, TLS, safe headers)?

## Common anti-patterns to block
- God services with mixed orchestration, domain, and infrastructure logic.
- Catch-all exception swallowing or broad retries without safeguards.
- Static/global state in request processing paths.
- Tests that depend on execution order or shared mutable fixtures.
