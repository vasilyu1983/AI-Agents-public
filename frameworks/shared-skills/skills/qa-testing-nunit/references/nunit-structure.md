# NUnit Structure

## Purpose
Use this guide to define predictable structure for NUnit-based test suites.

## Project Layout
- Mirror production modules in `tests/` to keep ownership clear.
- Separate fast unit tests from slower API/component tests.
- Group shared helpers under a dedicated utility namespace.

## Naming
- Name files `*Tests.cs`.
- Name fixture/setup helpers `*Fixture.cs`.
- Name tests as behavior statements: `Should_<Result>_When_<Condition>`.

## File Pattern
- Start with two files for each handler/use case:
  - `<Feature>Fixture.cs`: dependency wiring + deterministic Given helpers.
  - `<Feature>Tests.cs`: NUnit lifecycle and test methods.
- Use `partial` classes for both fixture and tests when scenario matrix grows by route/provider/product variant.
- Keep one base `Tests.cs` + one base `Fixture.cs` and extend with variant-specific partial files only as needed.

## API Full-Cycle Variant
- Use controller-focused structure as default migration target:
  - one fixture per controller/test family,
  - one base controller test class,
  - optional scenario split files (`.Positive.cs`, `.Negative.cs`, `.Validation.cs`, `.Query.cs`, `.Refund.cs`).
- Keep one base API fixture file (`<Controller>ApiFixture.cs`) for:
  - scenario helper methods (`Given...`),
  - repository checks,
  - API client helper methods.
- Keep fixture and test file names aligned to controller scope, not legacy feature-file scope.

## SpecFlow Migration Layout Rules
- Do not preserve legacy feature grouping when it conflicts with controller boundaries.
- Keep behavior parity in test methods, but rewrite structure into controller-focused suites.
- Add migration trace artifacts documenting scenario-to-test mapping and fixture ownership.

## Categories
- Apply categories consistently (`ApiTest`, `ComponentTests`, `DbTests`).
- Keep category usage aligned with build filters.

## Lifecycle Conventions
- Use `[SetUp]` for per-test initialization.
- Use `[OneTimeSetUp]` only for expensive shared resources within one fixture scope.
- Keep teardown explicit and idempotent.
- For API tests, combine `[Parallelizable]` + `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]`.

## Assertion Style
- Assert one behavior per test.
- Verify status/result first, then payload/side effects.
- Prefer expressive assertions over chained manual checks.
