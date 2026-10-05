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
- When setup is non-trivial, keep dependency wiring and deterministic `Given...` helpers in a fixture class, and the NUnit lifecycle and test methods in the test class. Name them as a pair.
- Use `partial` classes when the scenario matrix grows by route, provider, or product variant; keep one base file per class and add variant files only as needed.

## API Full-Cycle Variant
- Group API tests by controller or endpoint family, with one fixture per family.
- Keep scenario helpers (`Given...`), persisted-state checks, and API client helpers in that family's fixture.
- Align fixture and test names with the controller or endpoint scope.

## Categories
- Use one consistent category naming scheme across the solution.
- Keep category usage aligned with build filters.

## Lifecycle Conventions
- Use `[SetUp]` for per-test initialization.
- Use `[OneTimeSetUp]` only for expensive shared resources within one fixture scope.
- Keep teardown explicit and idempotent.
- For API tests, combine `[Parallelizable]` + `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]`.

## NUnit 4 Framework Baseline
- NUnit 4 requires minimum .NET Framework 4.6.2 or .NET 6.0. Do not add NUnit 4 to .NET 5 or below targets. NUnit 5 (pre-release) drops net6.0; see `test-platform-modes.md`.
- NUnit 4.0 moved classic assert methods (`Assert.AreEqual`, `Assert.IsNotNull`, etc.) to `NUnit.Framework.Legacy.ClassicAssert`; NUnit 4.5 restores the old `Assert.X` call syntax via C# 14 extension methods that forward to `ClassicAssert`. On C# 13 or below (or when avoiding classic asserts entirely), use `ClassicAssert.X` or the constraint model: `Assert.That(x, Is.EqualTo(y))`.
- Look up the current stable NUnit release on NuGet and pin its newest patch; treat pre-release majors as evaluation-only.

## Assertion Style
- Assert one behavior per test.
- Verify status/result first, then payload/side effects.
- Prefer expressive assertions over chained manual checks.
