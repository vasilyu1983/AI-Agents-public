# Assertions and Diagnostics

## Purpose
Use this guide to keep NUnit assertions expressive, analyzer-friendly, and easy to debug in CI.

## Grouped Assertions
- Use `Assert.Multiple` or `Assert.EnterMultipleScope` when one response or state snapshot needs several related checks.
- Keep grouped assertions for one behavior surface only; do not turn them into mini end-to-end scripts.
- Assert status or primary outcome first, then payload shape and side effects.

## Diagnostics
- Use `TestContext.Progress` for live diagnostic breadcrumbs that should appear during execution.
- Use `TestContext.Out` or fixture-specific logs for structured post-failure context.
- Include correlation IDs, request bodies, response bodies, container logs, and WireMock request logs when they materially reduce triage time.

## Analyzer-Friendly Patterns
- Keep `[Test]` with `[TestCase]` on parameterized tests when analyzer expectations require it.
- Prefer explicit cancellation and timeout attributes over hidden sleeps.
- Keep helper methods deterministic and avoid assertion logic hidden inside fixture setup.

## NUnit 4.5 Classic Assert Restoration

NUnit 4.0 did not delete classic asserts outright — it moved `Assert.AreEqual`, `Assert.IsNotNull`, `Assert.IsFalse`, etc. out of `NUnit.Framework.Assert` and into `NUnit.Framework.Legacy.ClassicAssert` (source callers had to rename `Assert.X` to `ClassicAssert.X` or add a `global using ClassicAssert = NUnit.Framework.Legacy.ClassicAssert;` alias). NUnit 4.5 (2025) restored the old call syntax by adding C# 14 extension methods on `NUnit.Framework.Assert` that forward to `ClassicAssert` — so `Assert.AreEqual(...)` compiles again, but only under the C# 14 language version. `NUnit.Framework.Legacy.ClassicAssert` still exists and works on any C# version; use it (or the constraint model `Assert.That(x, Is.EqualTo(y))`) on C# 13 and below. A few classic asserts still require the explicit `ClassicAssert` class even on C# 14 (verify current gaps against `docs.nunit.org` before assuming full parity).

## Assertion Library Selection

NUnit's built-in `Assert` (constraint model + `Assert.Multiple`) is the safe default and has zero licensing risk. If the team wants a fluent BDD-style API, choose deliberately:

| Library | Status (verified 2026-06-09) | When to use |
|---|---|---|
| **NUnit constraints** | Free, MIT, ships with NUnit 4 | Default. `Assert.That(x, Is.EqualTo(y))` covers most needs. |
| **Shouldly** | Free, BSD-3, actively maintained | Drop-in fluent API (`x.ShouldBe(y)`); recommended fluent fallback; cleaner error messages for simple assertions. |
| **AwesomeAssertions** | Free, Apache-2.0 (FluentAssertions 7 community fork) | Source-compatible swap-in for legacy FA codebases; namespace rename from `FluentAssertions` to `AwesomeAssertions`. |
| **FluentAssertions 7.x** | Free, Apache-2.0 (frozen; critical fixes only) | Pin to `<= 7.2.0` if already in use; do not upgrade past v7. |
| **FluentAssertions 8.x** | **Commercial license required** for non-OSS use | Only adopt with a paid Xceed license; otherwise stay on FA 7 or migrate. |

### FluentAssertions 8.x — license trap

FluentAssertions changed to a Xceed commercial license at v8.0.0 (released January 2025), initially reported at ~$130/dev/year. Xceed has since introduced additional tiers (a lower-cost, no-support option was reported around $14.95/dev/year later in 2025) — pricing has moved at least once since launch and may move again. Do not quote a fixed number without checking: as of 2026-07-11, verify current tiers at https://xceed.com/fluent-assertions-faq/ before budgeting or recommending a purchase. Any closed-source or commercial repo upgrading past v7.x without a paid license is in violation. Verify before recommending:

- New repos: do not add FluentAssertions. Use NUnit constraints or Shouldly.
- Existing FA usage: pin to `FluentAssertions <= 7.2.0` or migrate to AwesomeAssertions (near-zero-effort, drop-in namespace swap) or Shouldly (rename pass).
- Always check `data/sources.json` and the FA NuGet page for current licensing posture before bumping the version.

## Retry Guidance
- Use `[Retry]` only for truly transient infrastructure edges you understand and can explain.
- Do not use retries to mask shared-state bugs, readiness mistakes, or flaky eventual-consistency assertions.
- If retries are needed, record the underlying failure mode and keep the retry count intentionally low.
