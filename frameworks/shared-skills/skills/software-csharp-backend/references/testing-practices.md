# Testing Practices

## Scope by risk and boundary
- Unit tests: validate branch logic and invariants with deterministic inputs.
- Component tests: validate collaborating classes with near-real wiring.
- Integration/API tests: validate contracts, persistence, and infrastructure behavior.
- For API full-cycle tests, use Testcontainers for owned infrastructure and WireMock for external HTTP dependencies.

## Test design rules
- Keep one behavioral assertion focus per test.
- Name tests as behavior + condition + expected outcome.
- Use builders/fixtures to reduce setup noise.
- Avoid hidden shared mutable state across tests.
- Default to a two-file handler test structure: `<Feature>Fixture.cs` + `<Feature>Tests.cs`.
- Split fixture/tests into additional `partial` files only when scenario matrix grows large (for example by route/provider).
- For API suites, keep one base `ApiTest.cs` + `ApiFixture.cs` and split scenarios into partial files (`.Positive.cs`, `.Negative.cs`, `.Validation.cs`) when needed.
- Use dedicated request builders and `TestCaseSources` for large input matrices.

## Anti-flaky tactics
- Control time (fake clock where practical).
- Avoid sleeping; use polling assertions with bounded timeout.
- Use isolated test data per case.
- Keep external dependency setup deterministic (Testcontainers/WireMock).

## Async and eventual consistency
- Await all async operations.
- Assert eventual outcomes with retry-until-timeout helper methods.
- Keep timeouts tight enough to fail fast but realistic for CI variance.

## Coverage expectations
- Test happy path and expected failures for every critical use case.
- Add regression tests for every production defect fix.
- Prefer meaningful scenario coverage over raw line-coverage chasing.

## Suite maintenance
- Quarantine and fix flaky tests immediately.
- Keep category tags consistent for CI routing.
- Remove redundant tests when behavior is already covered at lower cost.
- Prefer shared fixture APIs (`Given...`, `Send...`) over repeated arrange logic inside tests.
