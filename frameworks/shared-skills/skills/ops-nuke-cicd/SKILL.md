---
name: ops-nuke-cicd
description: "Designs and troubleshoots NUKE-based CI/CD pipelines for .NET services. Use when refactoring target graphs, splitting test flows, publishing reports, or diagnosing slow pipelines."
compatibility: Repo-local — NUKE .NET pipelines with repo-specific targets.
version: "1.1"
last_validated: 2026-07-11
---

# NUKE CI/CD

## Quick Reference
- Start from existing `nuke/Build.cs` targets and preserve output contracts before refactoring.
- Keep target graph intent explicit: use `DependsOn` for hard prerequisites, `After` for ordering, `Triggers` for composed flows, and `OnlyWhenDynamic` for runtime gates.
- Choose one repository test platform and keep it consistent across CI and local runs: `VSTest` or `Microsoft.Testing.Platform`.
- If the repo uses .NET 10 `Microsoft.Testing.Platform` mode, do not assume VSTest-specific options such as `--logger` or collectors still apply.
- Use this skill for pipeline orchestration and build contracts, not for application-service refactors or NUnit fixture internals.
- Separate fast local feedback (`build + filtered tests`) from full CI validation (`unit + api + db + merged coverage`).
- Run preflight checks before expensive targets: SDK version, Docker availability (when required), and expected file paths.
- Prefer `--artifacts-path` when direct `dotnet test` runs need isolated output roots.
- Use category filters intentionally, including exclusion filter patterns such as `TestCategory!=ComponentTests&TestCategory!=DbTests&TestCategory!=ApiTest`.
- Keep `UnitTest` scoped to non-API categories and create a dedicated `ApiTest` target for `TestCategory=ApiTest`.
- Keep `TestAll` composed from `UnitTest + ApiTest (+ DbTest)` and coverage merge.
- When migrating from legacy docker-compose/SpecFlow orchestration, decommission compose-first test flow and keep pipeline focused on NUnit API categories.
- Avoid running parallel `dotnet test` invocations against the same project output path in one job to prevent file-lock/MSBuild manifest failures.
- Use dynamic host-port reservation for Docker-backed test infrastructure — no hard-coded localhost ports.
- Resolve Docker host from Testcontainers API or `DOCKER_HOST` in CI — never assume `localhost` reaches containers.
- Wire new test suites into the canonical pipeline entry point as part of feature delivery, not follow-up cleanup.
- Keep shell commands robust for `zsh`: avoid unquoted globs in direct shell commands and validate paths before `sed/cat/ls`.
- Emit coverage and test artifacts deterministically (`coverage.cobertura.xml`, HTML summary, JUnit XML).
- Use Dockerfiles when the repo needs custom packaging or hardening; consider `/t:PublishContainer` for simpler SDK-native images.
- When using `/t:PublishContainer`, set `ContainerFamily=jammy-chiseled` for chiseled images; non-root (UID 1654) and port 8080 are defaults since .NET 8 — do not assume port 80.
- NUKE's `DotNetTest` helper is VSTest-oriented and does not support Microsoft.Testing.Platform (NUKE issue #1584, confirmed open, no maintainer commitment, as of 2026-07-11). VSTest remains the **default** `dotnet test` mode on .NET 10 — MTP mode is opt-in via a `test.runner` entry in `global.json`. Never assume a repo is on MTP just because it targets .NET 10; check `global.json` and project SDK settings first. Once a repo does opt in, drive MTP runners via `ProcessTasks.StartProcess`, not `DotNetTasks.DotNetTest`.
- Generate SBOM as a first-class NUKE target (sbom-tool or CycloneDX .NET); attest NuGet/container artifacts with `actions/attest-build-provenance`; commit `packages.lock.json` and restore with `RestoreLockedMode=true` in CI.
- NuGet signature verification is on by default since the .NET 8 SDK; run `dotnet nuget verify` as a preflight gate for produced `.nupkg` artifacts.
- Publish digest-pinned image references into `deploy.env` or CI-native outputs, prefer structured digest outputs, and emit provenance/SBOM when supported.
- Use `IsLocalBuild` only for performance and output-path concerns, not correctness.
- If the task shifts into service implementation details, switch to `$software-csharp-backend`.
- If the task shifts into fixture design, WireMock/Testcontainers setup, or anti-flake test structure, switch to `$qa-testing-nunit`.

## When Not to Use This Skill
- The repo does not use NUKE (plain MSBuild targets, Cake, PowerShell/Bash-only pipelines, or CI-native workflows with no build-automation layer) — this skill's target-graph, `DotNetTasks`, and NUKE-idiom guidance does not transfer; use `$ops-devops-platform` or `$ops-platform-engineer` instead.
- The question is "should we adopt NUKE at all" rather than "how do we fix/extend our existing NUKE pipeline" — that is a build-tool selection decision (NUKE vs Cake vs raw MSBuild vs CI-native YAML), not something this skill's repo-local troubleshooting scope covers.
- NUKE's GitHub Actions pipeline *generation* feature (`nuke.build/docs/cicd/github-actions/`) is used to scaffold the workflow YAML itself — that is a one-time generator invoked from the NUKE CLI, not a target-graph design question; treat generated YAML as a starting point to review, not a runtime behavior to debug with this skill's target-graph tools.
- A failure is actually in NUnit fixture logic, WireMock stub setup, or test flakiness root-causing — hand off to `$qa-testing-nunit` rather than treating it as a pipeline/target problem.

## MTP Migration Decision Framework
NUKE issue #1584 (open, unresolved as of 2026-07-11) means a repo cannot get first-class NUKE support for Microsoft.Testing.Platform today. Before recommending an MTP migration inside a NUKE pipeline, weigh:
- **Stay on VSTest** if the repo has no immediate driver (no xUnit v3/TUnit adoption pressure, VSTest coverage/logger tooling works) — VSTest remains the default and best-supported path through NUKE's `DotNetTest` helper.
- **Migrate only if forced** — e.g., a test framework upgrade (xUnit v3, TUnit) is MTP-only and unavoidable. In that case, accept the `ProcessTasks.StartProcess` workaround (see `references/test-platform-modes-and-cli.md`) as the interim pattern, and flag to the team that NUKE's fluent test helpers are not usable for that project until #1584 closes.
- **Do not partially migrate a solution** — running some projects VSTest and others MTP inside one `dotnet test` invocation is explicitly unsupported by Microsoft's own docs; keep migration scoped to whole solutions or explicitly branch the NUKE target per project group.
- **Re-verify #1584's status** before committing to either path on a long-lived project — this is exactly the kind of unresolved upstream issue that can close without notice; check it fresh rather than trusting a cached answer.

## Workflow
1. Model or review target graph sequencing and execution constraints.
Load `references/nuke-target-graph-design.md`.
2. Design the build-test loop for early failures and rapid signal.
Load `references/build-test-feedback-loop.md`.
3. Lock repository test platform and CLI mode before changing reporting or runner arguments.
Load `references/test-platform-modes-and-cli.md`.
4. Define and verify test category filters for unit/API/DB/component separation.
Load `references/test-categories-and-filters.md`.
5. Implement coverage and test reporting with merge/publish outputs.
Load `references/coverage-and-reporting.md`.
6. Implement Docker build/push with tag + digest capture and deployment outputs.
Load `references/docker-build-push-patterns.md`.
7. Enforce stable artifact contracts and CI/provider output exports.
Load `references/ci-output-contracts-and-provenance.md`.
8. Tune local vs CI behavior without hiding pipeline defects.
Load `references/local-vs-ci-behavior.md`.
9. Harden reliability, logs, and diagnostics for CI incident response.
Load `references/pipeline-reliability-and-observability.md`.
10. Run command hygiene and environment preflight checks before final run.
Load `references/execution-preflight-and-command-hygiene.md`.
11. Run anti-pattern review before finalizing.
Load `references/nuke-pipeline-antipatterns.md`.

## ASCII Flow

```text
NUKE pipeline request or failure
  -> Inspect existing Build.cs targets and CI entry points
  -> Model target graph: DependsOn, After, Triggers, runtime gates
  -> Lock test platform and category contract
     +-- fast local -> build plus filtered tests
     +-- full CI -> unit plus API/DB/component plus merged coverage
  -> Stabilize artifacts: JUnit, coverage, HTML, env outputs, digest
  -> Harden Docker and external-service behavior when present
  -> Run preflight checks for SDK, Docker, paths, shell quoting, and CI env
  -> Execute canonical target and inspect logs before final guidance
```

## Decision Tree
- If target ordering is incorrect or unexpected targets run, use `references/nuke-target-graph-design.md`.
- If feedback loop is too slow or flaky, use `references/build-test-feedback-loop.md`.
- If the repo is moving to .NET 10 test flows, MTP, or mixed runner behavior is suspected, use `references/test-platform-modes-and-cli.md`.
- If test scope is wrong in CI or local runs, use `references/test-categories-and-filters.md`.
- If coverage or JUnit artifacts are missing/partial, use `references/coverage-and-reporting.md`.
- If Docker outputs are not traceable or digest pinning is missing, use `references/docker-build-push-patterns.md`.
- If downstream jobs cannot consume artifacts, env outputs, or provenance metadata, use `references/ci-output-contracts-and-provenance.md`.
- If local and CI behavior diverge unexpectedly, use `references/local-vs-ci-behavior.md`.
- If failures are hard to debug from logs, use `references/pipeline-reliability-and-observability.md`.
- If failures come from shell quoting, glob expansion, missing files, or environment prerequisites, use `references/execution-preflight-and-command-hygiene.md`.
- If pipeline quality regresses during refactors, use `references/nuke-pipeline-antipatterns.md`.
- If Docker-backed tests pass locally but fail in CI, use `references/local-vs-ci-behavior.md` + `references/execution-preflight-and-command-hygiene.md`.
- If a new test suite exists but is not running in CI, use `references/nuke-target-graph-design.md`.

## Symptom → Reference

| Symptom | Primary reference | Secondary reference |
|---------|------------------|---------------------|
| Tests pass locally, fail in CI | `references/local-vs-ci-behavior.md` | `references/execution-preflight-and-command-hygiene.md` |
| Docker-backed tests pass locally, fail in CI | `references/local-vs-ci-behavior.md` | `references/execution-preflight-and-command-hygiene.md` |
| Pipeline is slow or stalls | `references/nuke-target-graph-design.md` | `references/build-test-feedback-loop.md` |
| Wrong tests run (too many or too few) | `references/test-categories-and-filters.md` | `references/nuke-target-graph-design.md` |
| Coverage or JUnit artifacts missing / partial | `references/coverage-and-reporting.md` | `references/ci-output-contracts-and-provenance.md` |
| Unexpected target ordering or skipped targets | `references/nuke-target-graph-design.md` | `references/nuke-pipeline-antipatterns.md` |
| `dotnet test` args break after .NET 10 / MTP migration | `references/test-platform-modes-and-cli.md` | `references/coverage-and-reporting.md` |
| Digest missing or mutable image tag shipped to deploy | `references/docker-build-push-patterns.md` | `references/ci-output-contracts-and-provenance.md` |
| Downstream job cannot read artifacts or `deploy.env` | `references/ci-output-contracts-and-provenance.md` | `references/local-vs-ci-behavior.md` |
| Hard to diagnose failure from CI logs | `references/pipeline-reliability-and-observability.md` | `references/execution-preflight-and-command-hygiene.md` |
| Shell quoting / glob / missing-file errors | `references/execution-preflight-and-command-hygiene.md` | — |
| New test suite not running in CI | `references/nuke-target-graph-design.md` | `references/nuke-pipeline-antipatterns.md` |
| Pipeline quality regresses during refactor | `references/nuke-pipeline-antipatterns.md` | `references/build-test-feedback-loop.md` |

## Do / Avoid
**Do**
- Keep targets deterministic and side effects explicit.
- Keep test stages isolated by category and risk profile.
- Keep coverage/report merge as a first-class target in the graph.
- Keep Docker outputs traceable through tag, digest, and exported env variables.
- Keep artifact paths and names stable across branches and CI systems.

**Avoid**
- Mixing orchestration and hidden side effects inside unrelated targets.
- Running expensive integration tests before compile/unit gates.
- Changing output file names without updating consumer jobs.
- Using local-only shortcuts that invalidate CI parity.
- Ignoring digest capture and shipping mutable image references.

## Navigation
- [NUKE Target Graph Design](references/nuke-target-graph-design.md)
- [Build-Test Feedback Loop](references/build-test-feedback-loop.md)
- [Test Platform Modes and CLI](references/test-platform-modes-and-cli.md)
- [Test Categories and Filters](references/test-categories-and-filters.md)
- [Coverage and Reporting](references/coverage-and-reporting.md)
- [Docker Build Push Patterns](references/docker-build-push-patterns.md)
- [CI Output Contracts and Provenance](references/ci-output-contracts-and-provenance.md)
- [Local vs CI Behavior](references/local-vs-ci-behavior.md)
- [Pipeline Reliability and Observability](references/pipeline-reliability-and-observability.md)
- [Execution Preflight and Command Hygiene](references/execution-preflight-and-command-hygiene.md)
- [NUKE Pipeline Antipatterns](references/nuke-pipeline-antipatterns.md)
- [Skill Sources](data/sources.json): curated official NUKE, .NET, container, and CI references for this skill.

## Assets

| Asset | When to use |
|-------|-------------|
| [NUKE Target Template: Build and Test](assets/nuke-target-template-build-test.cs) | Starting point when scaffolding or refactoring `Restore`/`BuildAll`/`UnitTest`/`ApiTest`/`TestAll` targets with category filters and coverage collection. |
| [NUKE Target Template: Docker Build Push Digest](assets/nuke-target-template-docker-push-digest.cs) | Starting point when implementing a Docker image build, tag, push, and digest-capture target that emits a deployment reference. |
| [Test Result and Coverage Publishing Checklist](assets/test-result-coverage-publishing-checklist.md) | Use before finalising any coverage or test-reporting change to verify all output paths, formats, and CI collector config are in sync. |
| [CI Troubleshooting Checklist](assets/ci-troubleshooting-checklist.md) | Use during an active CI failure to work through target graph, test platform, Docker, artifact, and verbosity diagnostics in order. |
| [PR Pipeline Quality Checklist](assets/pr-pipeline-quality-checklist.md) | Use at PR review time to verify that target graph, test platform, coverage, Docker, provenance, and artifact contracts are intact. |

## Fact-Checking
- Verify current .NET test-platform behavior, NUKE package semantics, and CI-provider artifact/output conventions before final guidance.
- Treat repo-local target names and category filters as local contracts, not generic NUKE defaults.
- If web access is unavailable, mark version-sensitive CLI or provider guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

