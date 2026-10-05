---
name: ops-nuke-cicd
description: "Designs and troubleshoots NUKE-based CI/CD pipelines for .NET services. Use when refactoring target graphs, splitting test flows, publishing reports, or diagnosing slow pipelines."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# NUKE CI/CD

## Quick Reference
- Start from the repo's existing NUKE `Build.cs` targets and preserve output contracts before refactoring.
- Keep target graph intent explicit: use `DependsOn` for hard prerequisites, `After` for ordering, `Triggers` for composed flows, and `OnlyWhenDynamic` for runtime gates.
- Choose one repository test platform and keep it consistent across CI and local runs: `VSTest` or `Microsoft.Testing.Platform`.
- Use this skill for pipeline orchestration and build contracts, not for application-service refactors or NUnit fixture internals.
- Separate fast local feedback (`build + filtered tests`) from full CI validation (`unit + api + db + merged coverage`).
- Run preflight checks before expensive targets: SDK version, Docker availability (when required), and expected file paths.
- Prefer `--artifacts-path` when direct `dotnet test` runs need isolated output roots.
- Map each test category to one target and one filter. Keep the category names in one place (for example a constants class), use one naming style for all of them, and make the unit target exclude every non-unit category.
- Keep one composed CI target (for example `TestAll`) over the build, every category target, and the coverage merge. When a legacy test orchestration path is replaced, remove its targets and environment plumbing instead of leaving them dormant.
- Avoid running parallel `dotnet test` invocations against the same project output path in one job to prevent file-lock/MSBuild manifest failures.
- Use dynamic host-port reservation for Docker-backed test infrastructure — no hard-coded localhost ports.
- Resolve Docker host from Testcontainers API or `DOCKER_HOST` in CI — never assume `localhost` reaches containers.
- Wire new test suites into the canonical pipeline entry point as part of feature delivery, not follow-up cleanup.
- Keep shell commands robust for `zsh`: avoid unquoted globs in direct shell commands and validate paths before `sed/cat/ls`.
- Emit coverage and test artifacts deterministically (`coverage.cobertura.xml`, HTML summary, JUnit XML).
- Use Dockerfiles when the repo needs custom packaging or hardening; consider `/t:PublishContainer` for simpler SDK-native images.
- When using `/t:PublishContainer`, set `ContainerFamily` to a chiseled container family that matches the base image; non-root (UID 1654) and port 8080 are defaults since .NET 8 — do not assume port 80.
- NUKE issue #1584 tracks `DotNetTest` support for Microsoft.Testing.Platform; check the issue and current helper API before selecting a workaround. In MTP mode, VSTest-specific options such as `--logger` and data collectors do not apply. VSTest remains the default `dotnet test` mode on .NET 10. Before selecting runner arguments, check `global.json`, any runner override supported by the installed SDK, and project SDK settings; targeting .NET 10 alone does not select MTP. If the NUKE helper still lacks MTP support, invoke the runner through `ProcessTasks.StartProcess`.
- Generate SBOM as a first-class NUKE target (sbom-tool or CycloneDX .NET); attest NuGet/container artifacts with `actions/attest-build-provenance`; commit `packages.lock.json` and restore with `RestoreLockedMode=true` in CI.
- NuGet signature verification is on by default since the .NET 8 SDK; run `dotnet nuget verify` as a preflight gate for produced `.nupkg` artifacts.
- Publish digest-pinned image references into `deploy.env` or CI-native outputs, prefer structured digest outputs, and emit provenance/SBOM when supported.
- Use `IsLocalBuild` only for performance and output-path concerns, not correctness.
- If the task shifts into service implementation details, switch to `$software-csharp-backend`.
- If the task shifts into fixture design, WireMock/Testcontainers setup, or anti-flake test structure, switch to `$qa-testing-nunit`.

## When Not to Use This Skill
- The repo does not use NUKE (plain MSBuild targets, Cake, PowerShell/Bash-only pipelines, or CI-native workflows with no build-automation layer) — this skill's target-graph, `DotNetTasks`, and NUKE-idiom guidance does not transfer; use `$ops-devops-platform` instead.
- The question is "should we adopt NUKE at all" rather than "how do we fix/extend our existing NUKE pipeline" — that is a build-tool selection decision (NUKE vs Cake vs raw MSBuild vs CI-native YAML), not something this skill's troubleshooting scope covers.
- NUKE's GitHub Actions pipeline *generation* feature (`nuke.build/docs/cicd/github-actions/`) is used to scaffold the workflow YAML itself — that is a one-time generator invoked from the NUKE CLI, not a target-graph design question; treat generated YAML as a starting point to review, not a runtime behavior to debug with this skill's target-graph tools.
- A failure is actually in NUnit fixture logic, WireMock stub setup, or test flakiness root-causing — hand off to `$qa-testing-nunit` rather than treating it as a pipeline/target problem.

## MTP Migration Decision Framework
Check NUKE issue #1584 and the installed helper API before recommending an MTP migration inside a NUKE pipeline. Then weigh:
- **Stay on VSTest** if VSTest coverage/logger tooling meets the repo's needs and its test framework supports the adapter. xUnit v3 supports VSTest through `xunit.runner.visualstudio`; a v3 upgrade alone does not force MTP.
- **Migrate when the selected framework requires MTP**, for example TUnit, or when a measured benefit justifies it. If the installed NUKE helper still lacks MTP support, use the `ProcessTasks.StartProcess` workaround (see `references/test-platform-modes-and-cli.md`) and document that limitation.
- **Do not partially migrate a solution** — running some projects VSTest and others MTP inside one `dotnet test` invocation is explicitly unsupported by Microsoft's own docs; keep migration scoped to whole solutions or explicitly branch the NUKE target per project group.
- **Re-verify #1584's status and helper behavior** before committing to either path on a long-lived project.

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

12. Verify each pipeline claim at the matching stage: target selection from the execution plan or target log, command execution from exit codes and test/build output, and downstream consumption from the collector or deploy job reading the exact artifact path, digest, or exported variable. Compiling `Build.cs` or inspecting `DependsOn` proves graph syntax only. If Docker, credentials, or the CI provider is unavailable, report those stages as unexecuted and name the exact canonical target that remains.

## Symptom → Reference

| Symptom | Primary reference | Secondary reference |
|---------|------------------|---------------------|
| Tests pass locally, fail in CI | `references/local-vs-ci-behavior.md` | `references/execution-preflight-and-command-hygiene.md` |
| Docker-backed tests pass locally, fail in CI | `references/local-vs-ci-behavior.md` | `references/execution-preflight-and-command-hygiene.md` |
| Pipeline or feedback loop is slow, flaky, or stalls | `references/nuke-target-graph-design.md` | `references/build-test-feedback-loop.md` |
| Wrong tests run (too many or too few) | `references/test-categories-and-filters.md` | `references/nuke-target-graph-design.md` |
| Coverage or JUnit artifacts missing / partial | `references/coverage-and-reporting.md` | `references/ci-output-contracts-and-provenance.md` |
| Unexpected target ordering or skipped targets | `references/nuke-target-graph-design.md` | `references/nuke-pipeline-antipatterns.md` |
| `dotnet test` args break after .NET 10 / MTP migration, or mixed runner behavior is suspected | `references/test-platform-modes-and-cli.md` | `references/coverage-and-reporting.md` |
| Digest missing or mutable image tag shipped to deploy | `references/docker-build-push-patterns.md` | `references/ci-output-contracts-and-provenance.md` |
| Downstream job cannot read artifacts or `deploy.env` | `references/ci-output-contracts-and-provenance.md` | `references/local-vs-ci-behavior.md` |
| Hard to diagnose failure from CI logs | `references/pipeline-reliability-and-observability.md` | `references/execution-preflight-and-command-hygiene.md` |
| Shell quoting / glob / missing-file errors | `references/execution-preflight-and-command-hygiene.md` | — |
| New test suite not running in CI | `references/nuke-target-graph-design.md` | `references/nuke-pipeline-antipatterns.md` |
| Pipeline quality regresses during refactor | `references/nuke-pipeline-antipatterns.md` | `references/build-test-feedback-loop.md` |

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
| [NUKE Target Template: Build and Test](assets/nuke-target-template-build-test.cs) | Starting point when scaffolding or refactoring build, per-category test, and composed test targets with one category list, filters, and coverage collection. Target and category names are illustrative. |
| [NUKE Target Template: Docker Build Push Digest](assets/nuke-target-template-docker-push-digest.cs) | Starting point when implementing a Docker image build, tag, push, and digest-capture target that emits a deployment reference. |
| [Test Result and Coverage Publishing Checklist](assets/test-result-coverage-publishing-checklist.md) | Use before finalising any coverage or test-reporting change to verify all output paths, formats, and CI collector config are in sync. |
| [CI Troubleshooting Checklist](assets/ci-troubleshooting-checklist.md) | Use during an active CI failure to work through target graph, test platform, Docker, artifact, and verbosity diagnostics in order. |
| [PR Pipeline Quality Checklist](assets/pr-pipeline-quality-checklist.md) | Use at PR review time to verify that target graph, test platform, coverage, Docker, provenance, and artifact contracts are intact. |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
