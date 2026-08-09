---
name: qa-testing-nunit
description: "Designs NUnit-based C# test suites for API, component, and integration coverage. Use when creating fixtures, wiring Testcontainers, or reducing flaky CI behavior."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Testing (NUnit)

## Quick Start

1. Classify test scope: API, component, or integration.
2. Lock runtime constraints: Docker availability, framework target, and excluded suites.
3. Choose fixture pattern: one fixture per controller or handler family.
4. Wire dependencies: Testcontainers for databases, WireMock for external services.
5. Run iteratively: `code → build → dotnet test → fix → repeat`.

## Quick Reference
- Classify test scope first: API, component, or integration.
- Lock runtime constraints before execution: Docker availability, framework target, and explicitly excluded suites.
- If the task mentions `dotnet test`, `Microsoft.Testing.Platform`, `global.json`, adapters, or coverage/logging switches, verify the repo's current runner mode first and use current primary sources from `data/sources.json`.
- Use this skill for test-suite architecture and fixture behavior, not for general service implementation or CI graph refactors.
- Default to two files per handler/use case: `<Feature>Fixture.cs` and `<Feature>Tests.cs`.
- For full-cycle API tests, use controller-focused structure: one fixture per controller/test family and one base `ApiTest.cs` + `ApiFixture.cs` (split by scenario family only when needed).
- Do not translate SpecFlow/Taffy step definitions into C# line-by-line; rewrite scenario intent into idiomatic API tests.
- For API migrations, avoid one global shared setup fixture; each controller/test family fixture owns its own dependencies.
- Fixture ownership for API tests should include DB launcher + migrators + WireMock + WebApplicationFactory + client.
- Keep API fixture-shared runtime parallel-safe: fixture-level parallelism is fine, but do not enable child-test parallelism when WireMock stubs, clients, or mutable runtime state are shared.
- Why `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]` pairs with `[Parallelizable]`: NUnit's default `SingleInstance` lifecycle shares one fixture object across every test method, so instance fields become a race condition the moment two of its tests run concurrently. `InstancePerTestCase` gives each test its own instance, isolating instance-field state; it does **not** isolate `static` fields or external shared resources (containers, WireMock servers), which is why `[OneTimeSetUp]`/`[OneTimeTearDown]` must stay `static` under this lifecycle and shared runtime still needs its own reset discipline in `[SetUp]`.
- Reset mutable state in `[SetUp]`; dispose all owned infra in `[OneTimeTearDown]`.
- For DB bootstrapping, use the `DatabaseLauncher + MigratorContainer` pattern (see `assets/nunit-database-launcher-template.cs`); if the repo already has an established launcher/migrator helper, follow it instead of forking.
- Use whatever migrator command the repo's existing migrator container exposes (e.g. `migrateup -m /sql`); avoid custom ready-check arguments inside tests — drive readiness from the container wait strategy.
- Keep migrator ordering explicit (dependency migrators first, domain migrator last) and support fixture-level optional migrator toggles when some suites do not need all DBs.
- Add explicit migrator verification tests that assert launcher startup, migrator completion/order, and required tables.
- Use iterative quality loop: `code -> build -> run tests -> fix -> repeat`.
- For health endpoints, use `[Test] + [TestCase] + [CancelAfter(...)]` with method signature `(string url, CancellationToken cancellationToken)`; keep `[Test]` together with `[TestCase]` to avoid NUnit analyzer issues.
- Prefer analyzer-friendly NUnit usage and richer diagnostics: use `Assert.Multiple` or `Assert.EnterMultipleScope` for related assertions, and use `TestContext.Progress` or fixture diagnostics when failures need more context.
- If user excludes infra-dependent suites (for example component tests requiring Docker), run feasible categories first and report exactly what remains unvalidated.
- If the task shifts into service design or backend refactoring, switch to `$software-csharp-backend`.
- If the task shifts into `nuke/Build.cs`, test runner selection, category target wiring, or CI artifact publication, switch to `$ops-nuke-cicd`.

## Current-Facts Protocol
- Treat runner mode, package versions, analyzer behavior, adapter requirements, and CLI/coverage switches as volatile current-state facts.
- Verify version-sensitive guidance against `data/sources.json` before recommending package changes or command-line flags.
- Keep repository-wide `dotnet test`, MTP, coverage, and CI wiring in `$ops-nuke-cicd`; keep this skill focused on fixture design and suite structure.
- Current stable versions (verified 2026-06-09): NUnit 4.6.1, NUnit3TestAdapter 6.2.0, NUnit.Analyzers 4.14.0.
- NUnit 4 minimum TFM: .NET Framework 4.6.2 or .NET 6.0.
- NUnit3TestAdapter 6.x supports MTP 2.0 and requires .NET 8+; adapter 5.x supports MTP 1.x with .NET Core 3.1+.
- dotnet test has two modes: VSTest mode (default, .NET 9 SDK and earlier) and MTP mode (opt-in via global.json, .NET 10 SDK). Running MTP under VSTest mode is legacy as of .NET 10.
- FluentAssertions v8 is commercially licensed (Xceed); new repos must use NUnit constraints, Shouldly, or AwesomeAssertions.
- coverlet.collector is VSTest-only; use coverlet.MTP or Microsoft.Testing.Extensions.CodeCoverage for MTP mode.

## Workflow
1. Define boundary, dependencies, expected assertion depth, and environment constraints.
Load `references/nunit-structure.md`. If the request touches `dotnet test`, runner mode, adapters, or CLI flags, also load `references/test-platform-modes.md`.
2. Select fixture composition and lifecycle.
Load `references/fixture-pattern.md` and `references/testing-templates.md`.
3. Implement scenario tests for the target layer.
Load `references/api-testing-nunit.md` or `references/component-testing-nunit.md`.
4. Choose double vs real dependency strategy.
Load `references/dependency-strategy-matrix.md`, then `references/wiremock-setup.md` or `references/testcontainers-setup.md`.
5. Add resilient async and eventual-consistency assertions.
Load `references/async-eventual-assertions.md` and `references/assertions-and-diagnostics.md`.
6. Harden suite against flaky behavior.
Load `references/anti-flakiness.md`.
7. Tune execution in CI.
Load `references/ci-parallelism-sharding.md` and `references/infrastructure-troubleshooting.md`.
8. Validate changed suites through build-test feedback targets.
For NUKE-based repositories, run `BuildAll`, `LocalUnitTest`, `ApiTest`/`DbTest` as needed, then `TestAll`; use `$ops-nuke-cicd` for pipeline-target changes.
9. If this is a migration from SpecFlow-style assets, produce migration trace artifacts.
Use `$docs-codebase` with migration matrix and feature trace templates.

## Resources
- [NUnit Structure](references/nunit-structure.md): project layout, naming, categories, and lifecycle conventions.
- [Fixture Pattern](references/fixture-pattern.md): fixture boundaries, shared setup, teardown, and composition.
- [Testing Templates](references/testing-templates.md): copy-ready fixture/Testcontainers/WireMock templates.
- [API Testing with NUnit](references/api-testing-nunit.md): endpoint-level tests with HTTP assertions and contract checks.
- [Component Testing with NUnit](references/component-testing-nunit.md): in-process integration tests across collaborating components.
- [Test Platform Modes](references/test-platform-modes.md): runner-mode checks for `dotnet test`, MTP, adapters, and repo-level CLI drift.
- [Dependency Strategy Matrix](references/dependency-strategy-matrix.md): decide WireMock vs Testcontainers by scenario.
- [WireMock Setup](references/wiremock-setup.md): deterministic stubs, request verification, and failure simulation.
- [Testcontainers Setup](references/testcontainers-setup.md): container lifecycle, readiness, and test isolation.
- [Async Eventual Assertions](references/async-eventual-assertions.md): polling, timeouts, and message-driven verification.
- [Assertions and Diagnostics](references/assertions-and-diagnostics.md): grouped assertions, analyzer-safe patterns, and richer failure output.
- [Anti-Flakiness](references/anti-flakiness.md): reliability rules for stable execution.
- [CI Parallelism and Sharding](references/ci-parallelism-sharding.md): split test execution safely and efficiently.
- [Infrastructure Troubleshooting](references/infrastructure-troubleshooting.md): diagnose startup failures, port collisions, and readiness issues.
- [Skill Sources](data/sources.json): curated NUnit, .NET runner, Testcontainers, WireMock.Net, and package references for current-state checks.

## Templates
- [NUnit Handler Fixture Template](assets/nunit-handler-fixture-template.cs): base fixture for setup wiring and deterministic scenario configuration.
- [NUnit Handler Tests Template](assets/nunit-handler-tests-template.cs): base test class using fixture with Arrange/Act/Assert flow.
- [NUnit API Fixture Template](assets/nunit-api-fixture-template.cs): API fixture for controller-focused API-to-database full-cycle tests.
- [NUnit API Tests Template](assets/nunit-api-tests-template.cs): base API test class with fixture isolation and parallel-safe lifecycle.
- [NUnit API Request Builder Template](assets/nunit-api-request-builder-template.cs): deterministic request builder for scenario setup.
- [NUnit API TestCaseSources Template](assets/nunit-api-test-case-sources-template.cs): reusable `TestCaseData` source methods.
- [NUnit WireMock Template](assets/nunit-wiremock-template.cs): `WireMockServerWrapper` and per-dependency `*WiremockServer` helper pattern.
- [NUnit Database Launcher Template](assets/nunit-database-launcher-template.cs): `DatabaseLauncher`, ordered migrator chain, optional migrator toggles, and startup verification hooks.

## ASCII Flow

```text
NUnit testing request
  -> Classify API, component, integration, or infrastructure-backed scope
  -> Verify runner mode, target framework, Docker availability, and excluded suites
  -> Choose fixture shape and dependency strategy: real, fake, WireMock, Testcontainers
  -> Add deterministic Arrange/Act/Assert tests with rich diagnostics
  -> Run dotnet build/test with targeted filters before widening
  -> Fix flakes through isolation, readiness checks, and parallelism boundaries
```

## Navigation

- `## Workflow` and `## Quick Reference` for the baseline sequence
- `## Resources` and `## Templates` for deeper materials
- `## When Not to Use This Skill` and `## Failure Triage` for scope boundaries and symptom-first debugging
- `## Related Skills` for broader QA and .NET handoffs

## When Not to Use This Skill (Judgment Calls)

- The question is "should we even have this test" (risk-based coverage priority, what to test at all) — use `$qa-testing-strategy` first, then return here for how to build it.
- The failing thing is a `dotnet test`/MTP/VSTest runner-mode mismatch, coverage collector wiring, or CI target graph, not fixture/test code — use `$ops-nuke-cicd`; do not try to fix runner-mode drift by editing test files.
- The task is implementing or fixing production/service code exposed by a failing test — switch to `$software-csharp-backend`; writing tests around a bug is this skill's job, fixing the bug is not.
- The suite in question is browser/E2E (Playwright, Selenium) rather than API/component/integration in-process or Testcontainers-backed — use `$qa-testing-playwright` or the relevant mobile/UI skill instead.
- A flaky test's root cause is unclear after one pass of `references/anti-flakiness.md` — do not keep guessing fixes; add diagnostics (correlation IDs, container/WireMock logs, timing) first, reproduce deterministically, and only then patch. Silently adding `[Retry]` to hide an unexplained flake is a regression, not a fix.

## Failure Triage (Symptom → Likely Cause → First Move)

| Symptom | Likely cause class | First move |
|---|---|---|
| Test passes alone, fails in full run | Shared mutable state or fixture lifecycle mismatch | Check `[FixtureLifeCycle]`/`[Parallelizable]` combination; confirm `[SetUp]` actually resets everything the failing test reads |
| Test passes locally, fails only in CI | Port collision, Docker host assumption (`localhost` vs remote Docker host), or resource contention under CI parallelism | Check for hard-coded ports/hosts (`references/anti-flakiness.md`, `references/testcontainers-setup.md`); reduce parallelism for the failing category as a diagnostic, not a permanent fix |
| Intermittent timeout on eventually-consistent assertions | Fixed sleep instead of polling, or timeout too tight for CI-under-load | Replace with the polling template in `references/async-eventual-assertions.md`; widen timeout only after confirming the condition is correct, not to paper over a race |
| `dotnet test` silently discovers 0 tests after an upgrade | Adapter major version mismatched to MTP generation, or mixed VSTest/MTP in one solution | Check adapter ↔ MTP ↔ TFM matrix in `references/test-platform-modes.md` before touching test code |
| Coverage report is empty or missing after enabling MTP | `coverlet.collector`/`coverlet.msbuild` left in place (VSTest-only, silently no-ops under MTP) | Swap to `coverlet.MTP` or `Microsoft.Testing.Extensions.CodeCoverage` per `references/test-platform-modes.md` |
| Migrator-dependent test fails with a missing-table error | Migrator ordering issue, not a test bug | Check `references/infrastructure-troubleshooting.md` migrator-ordering section before adding retries or longer timeouts |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-csharp-backend](../software-csharp-backend/SKILL.md) | Backend service implementation |
| [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md) | NUKE pipeline targets and CI wiring |
| `dev-structured-logs` | Structured logging migration |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy |
| [qa-testing-playwright](../qa-testing-playwright/SKILL.md) | Browser/E2E suites (out of scope here) |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

