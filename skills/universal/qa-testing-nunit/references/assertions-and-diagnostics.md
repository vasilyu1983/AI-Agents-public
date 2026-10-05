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

NUnit 4.0 did not delete classic asserts outright — it moved `Assert.AreEqual`, `Assert.IsNotNull`, `Assert.IsFalse`, etc. out of `NUnit.Framework.Assert` and into `NUnit.Framework.Legacy.ClassicAssert` (source callers had to rename `Assert.X` to `ClassicAssert.X` or add a `global using ClassicAssert = NUnit.Framework.Legacy.ClassicAssert;` alias). NUnit 4.5.0 (2026-02-18) restored the old call syntax by adding C# 14 extension methods on `NUnit.Framework.Assert` that forward to `ClassicAssert` — so `Assert.AreEqual(...)` compiles again, but only under the C# 14 language version. `NUnit.Framework.Legacy.ClassicAssert` still exists and works on any C# version; use it (or the constraint model `Assert.That(x, Is.EqualTo(y))`) on C# 13 and below. Check `docs.nunit.org` before assuming every classic assert is forwarded.

## Assertion Library Selection

NUnit's built-in `Assert` (constraint model + `Assert.Multiple`) is the safe default and has zero licensing risk. If the team wants a fluent BDD-style API, choose deliberately:

| Library | Status (check licences and releases before adopting) | When to use |
|---|---|---|
| **NUnit constraints** | Free, MIT, ships with NUnit 4 | Default. `Assert.That(x, Is.EqualTo(y))` covers most needs. |
| **Shouldly** | Free, BSD-3, actively maintained | Drop-in fluent API (`x.ShouldBe(y)`); recommended fluent fallback; cleaner error messages for simple assertions. |
| **AwesomeAssertions** | Free, Apache-2.0 (community fork of FluentAssertions) | Swap-in for legacy FA codebases; namespace rename from `FluentAssertions` to `AwesomeAssertions`. It has had its own majors since the fork, so check its release notes for API drift. |
| **FluentAssertions 7.x** | Apache-2.0; check Xceed's current support statement for the 7.x line | Stay on 7.x (`[7.0,8.0)`) if already in use; do not upgrade to v8 without a licence. |
| **FluentAssertions 8.x** | **Commercial license required** for non-OSS use | Only adopt with a paid Xceed license; otherwise stay on FA 7 or migrate. |

### FluentAssertions 8.x — license trap

FluentAssertions moved to an Xceed commercial licence at v8.0.0. Licence terms and pricing change: read the licence on the NuGet package page and the Xceed FAQ (https://xceed.com/fluent-assertions-faq/) before adopting, upgrading, or budgeting. A closed-source or commercial repo on v8 without a licence is out of compliance. Verify before recommending:

- New repos: do not add FluentAssertions. Use NUnit constraints or Shouldly.
- Existing FA usage: constrain to `FluentAssertions` `[7.0,8.0)` or migrate to AwesomeAssertions (near-zero-effort, drop-in namespace swap) or Shouldly (rename pass).
- Always check `data/sources.json` and the FA NuGet page for current licensing posture before bumping the version.

## Retry Guidance
- Use `[Retry]` only for truly transient infrastructure edges you understand and can explain.
- Do not use retries to mask shared-state bugs, readiness mistakes, or flaky eventual-consistency assertions.
- If retries are needed, record the underlying failure mode and keep the retry count intentionally low.
