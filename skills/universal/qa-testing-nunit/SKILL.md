---
name: qa-testing-nunit
description: "Designs NUnit-based C# test suites for API, component, and integration coverage. Use when creating fixtures, wiring Testcontainers, or reducing flaky CI behavior."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# QA Testing (NUnit)

## Quick Reference
- Classify test scope first: API, component, or integration.
- Lock runtime constraints before execution: Docker availability, framework target, and explicitly excluded suites.
- If the task mentions `dotnet test`, `Microsoft.Testing.Platform`, `global.json`, adapters, or coverage/logging switches, verify the repo's current runner mode first and use current primary sources from `data/sources.json`.
- Use this skill for test-suite architecture and fixture behavior, not for general service implementation or CI graph refactors.
- Separate setup from test methods when setup is non-trivial: a fixture class holds dependency wiring and `Given...` helpers; the test class holds the NUnit lifecycle and assertions.
- Group full-cycle API tests by controller or endpoint family. Avoid one global shared setup fixture; each family's fixture owns its database container and migrations, HTTP stubs, `WebApplicationFactory`, and client.
- Keep API fixture-shared runtime parallel-safe: fixture-level parallelism is fine, but do not enable child-test parallelism when WireMock stubs, clients, or mutable runtime state are shared.
- Why `[FixtureLifeCycle(LifeCycle.InstancePerTestCase)]` pairs with `[Parallelizable]`: NUnit's default `SingleInstance` lifecycle shares one fixture object across every test method, so instance fields become a race condition the moment two of its tests run concurrently. `InstancePerTestCase` gives each test its own instance, isolating instance-field state; it does **not** isolate `static` fields or external shared resources (containers, WireMock servers), which is why `[OneTimeSetUp]`/`[OneTimeTearDown]` must stay `static` under this lifecycle and shared runtime still needs its own reset discipline in `[SetUp]`.
- Reset mutable state in `[SetUp]`; dispose all owned infra in `[OneTimeTearDown]`.
- For database bootstrapping, start the database container, run each migration set as a one-shot container that must exit with code `0`, then check the required tables (starting point: `assets/nunit-database-launcher-template.cs`). If the repo already has a launcher or migration helper, reuse it instead of forking.
- Run migrations with the command the repo's migration image already documents; drive readiness from the container wait strategy, not from custom ready-check arguments inside tests.
- Keep migrator ordering explicit (dependency migrators first, domain migrator last) and support fixture-level optional migrator toggles when some suites do not need all DBs.
- Add explicit migrator verification tests that assert launcher startup, migrator completion/order, and required tables.
- For health endpoints, use `[Test] + [TestCase] + [CancelAfter(...)]` with method signature `(string url, CancellationToken cancellationToken)`; keep `[Test]` together with `[TestCase]` to avoid NUnit analyzer issues.
- Prefer analyzer-friendly NUnit usage and richer diagnostics: use `Assert.Multiple` or `Assert.EnterMultipleScope` for related assertions, and use `TestContext.Progress` or fixture diagnostics when failures need more context.
- If user excludes infra-dependent suites (for example component tests requiring Docker), run feasible categories first and report exactly what remains unvalidated.
- If the task shifts into service design or backend refactoring, switch to `$software-csharp-backend`.
- If the task shifts into `nuke/Build.cs`, test runner selection, category target wiring, or CI artifact publication, switch to `$ops-nuke-cicd`.

## Current-Facts Protocol
- Treat runner mode, package versions, analyzer behavior, adapter requirements, and CLI/coverage switches as volatile current-state facts.
- Verify version-sensitive guidance against `data/sources.json` before recommending package changes or command-line flags.
- Keep repository-wide `dotnet test`, MTP, coverage, and CI wiring in `$ops-nuke-cicd`; keep this skill focused on fixture design and suite structure.
- Package, adapter, runner-mode, and coverage facts live in `references/test-platform-modes.md`; assertion-library licensing lives in `references/assertions-and-diagnostics.md`. Look up current versions on NuGet before pinning.

## Workflow
1. Define boundary, dependencies, expected assertion depth, and environment constraints.
Load `references/nunit-structure.md`. If the request touches `dotnet test`, runner mode, adapters, or CLI flags, also load `references/test-platform-modes.md`.
2. Select fixture composition and lifecycle.
Load `references/fixture-pattern.md` and `references/testing-templates.md`.
3. Implement scenario tests for the target layer.
Load `references/api-testing-nunit.md`; for component tests, the boundaries section of `references/reliability-and-dependencies.md`.
4. Choose double vs real dependency strategy and container topology.
Load `references/reliability-and-dependencies.md`, then `references/wiremock-setup.md` or `references/testcontainers-setup.md`.
5. Add resilient async and eventual-consistency assertions, and harden against flakes.
Load `references/reliability-and-dependencies.md` and `references/assertions-and-diagnostics.md`.
6. Keep the templates consistent.
Copy the API asset set together (see the template map in `references/testing-templates.md`).
7. Tune execution in CI.
Load `references/ci-parallelism-sharding.md` and `references/infrastructure-troubleshooting.md`.
8. Validate changed suites through build-test feedback targets.
Record SDK, runner mode, target framework, filter, discovered/executed/skipped counts, result path, and container or stub diagnostics. A build or `--list-tests` proves discovery only; a green filtered run proves only that category and target framework. For NUKE-based repositories, run the repo's build target and the category test targets that cover the change; use `$ops-nuke-cicd` for pipeline-target changes.

If Testcontainers or WireMock is part of the oracle, require evidence that the intended dependency started, became ready, received the expected interaction, and was cleaned up. List excluded suites explicitly instead of calling the NUnit run complete.

## Resources
- [NUnit Structure](references/nunit-structure.md): project layout, naming, categories, and lifecycle conventions.
- [Fixture Pattern](references/fixture-pattern.md): fixture boundaries, shared setup, teardown, and composition.
- [Testing Templates](references/testing-templates.md): template map, parallelism contract, and healthcheck template.
- [API Testing with NUnit](references/api-testing-nunit.md): endpoint-level tests with HTTP assertions and contract checks.
- [Test Platform Modes](references/test-platform-modes.md): runner-mode checks for `dotnet test`, MTP, adapters, and repo-level CLI drift.
- [Reliability and Dependencies](references/reliability-and-dependencies.md): WireMock vs Testcontainers, container topology, component boundaries, eventual assertions, determinism, and flake rules.
- [WireMock Setup](references/wiremock-setup.md): deterministic stubs, request verification, and failure simulation.
- [Testcontainers Setup](references/testcontainers-setup.md): container lifecycle, readiness, and test isolation.
- [Assertions and Diagnostics](references/assertions-and-diagnostics.md): grouped assertions, analyzer-safe patterns, and richer failure output.
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
- [NUnit Database Launcher Template](assets/nunit-database-launcher-template.cs): database container, ordered one-shot migration containers, optional migration toggles, and table checks.

## Navigation

- Start with `## Workflow`; use `## Failure Triage` for symptom-first debugging and `## Related Skills` for handoffs.

## When Not to Use This Skill (Judgment Calls)

- The question is "should we even have this test" (risk-based coverage priority, what to test at all) — use `$qa-testing-strategy` first, then return here for how to build it.
- The failing thing is a `dotnet test`/MTP/VSTest runner-mode mismatch, coverage collector wiring, or CI target graph, not fixture/test code — use `$ops-nuke-cicd`; do not try to fix runner-mode drift by editing test files.
- The task is implementing or fixing production/service code exposed by a failing test — switch to `$software-csharp-backend`; writing tests around a bug is this skill's job, fixing the bug is not.
- The suite in question is browser/E2E (Playwright, Selenium) rather than API/component/integration in-process or Testcontainers-backed — use `$qa-testing-playwright` or the relevant mobile/UI skill instead.
- A flaky test's root cause is unclear after one pass of `references/reliability-and-dependencies.md` — do not keep guessing fixes; add diagnostics (correlation IDs, container/WireMock logs, timing) first, reproduce deterministically, and only then patch. Silently adding `[Retry]` to hide an unexplained flake is a regression, not a fix.

## Failure Triage (Symptom → Likely Cause → First Move)

| Symptom | Likely cause class | First move |
|---|---|---|
| Test passes alone, fails in full run | Shared mutable state or fixture lifecycle mismatch | Check `[FixtureLifeCycle]`/`[Parallelizable]` combination; confirm `[SetUp]` actually resets everything the failing test reads |
| Test passes locally, fails only in CI | Port collision, Docker host assumption (`localhost` vs remote Docker host), or resource contention under CI parallelism | Check for hard-coded ports/hosts (`references/reliability-and-dependencies.md`, `references/testcontainers-setup.md`); reduce parallelism for the failing category as a diagnostic, not a permanent fix |
| Intermittent timeout on eventually-consistent assertions | Fixed sleep instead of polling, or timeout too tight for CI-under-load | Replace with the `Eventually` helper in `references/reliability-and-dependencies.md`; widen timeout only after confirming the condition is correct, not to paper over a race |
| `dotnet test` silently discovers 0 tests after an upgrade | Adapter major version mismatched to MTP generation, or mixed VSTest/MTP in one solution | Check adapter ↔ MTP ↔ TFM matrix in `references/test-platform-modes.md` before touching test code; add `--minimum-expected-tests` under MTP so this fails the run instead of passing green |
| Coverage report is empty or missing after enabling MTP | A VSTest-only coverage collector left in place; it silently no-ops under MTP | Swap to an MTP-native coverage extension: look up the current package pairing in `references/test-platform-modes.md` and confirm it in the package's own docs |
| Migrator-dependent test fails with a missing-table error | Migrator ordering issue, not a test bug | Check `references/infrastructure-troubleshooting.md` migrator-ordering section before adding retries or longer timeouts |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-csharp-backend](../software-csharp-backend/SKILL.md) | Backend service implementation |
| [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md) | NUKE pipeline targets and CI wiring |
| `dev-structured-logs` | Structured logging migration |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy |
| [qa-testing-playwright](../qa-testing-playwright/SKILL.md) | Browser/E2E suites (out of scope here) |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
