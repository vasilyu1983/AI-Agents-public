# Test Platform Modes and CLI

## Purpose
Keep `dotnet test`, coverage, and reporting behavior coherent as repositories move from VSTest-oriented flows to `Microsoft.Testing.Platform`.

## Platform Rule
- Choose one repository test platform per command path and keep local and CI behavior aligned.
- Keep VSTest-compatible guidance only for repos that still depend on VSTest loggers, collectors, or `Microsoft.NET.Test.Sdk` behavior.
- If the repo opts into `Microsoft.Testing.Platform`, review runner-specific arguments before changing logging or coverage switches.

## Current .NET Guidance
- `dotnet test` remains the main entry point for both VSTest and `Microsoft.Testing.Platform` flows.
- **VSTest is still the default mode of `dotnet test` on the .NET 10 SDK.** MTP mode is opt-in: add a `test.runner` entry to `global.json` (`{"test":{"runner":"Microsoft.Testing.Platform"}}`). Do not assume a repo runs MTP just because it targets .NET 10 — verify `global.json` and project-level MTP settings (`EnableNUnitRunner`, `EnableMSTestRunner`, `TestingPlatformDotnetTestSupport`) before changing test-runner arguments.
- A repo can also run MTP-native tests *while staying in VSTest mode* by setting `TestingPlatformDotnetTestSupport=true` (MSBuild property, defaults to `false`). This is the legacy interop path Microsoft is deprecating in favor of full `global.json` MTP mode — treat it as a hint the repo hasn't fully migrated yet, not as MTP mode itself.
- Use `--artifacts-path` when CLI-driven runs need isolated output roots per project.
- Terminal Logger (`--tl`) behavior is now part of normal `dotnet test` ergonomics; disable it only when a CI log parser or export step requires plain console output.

## Practical Guardrails
- Do not assume VSTest collectors or `--logger` values will behave the same once the repo switches runner mode.
- Do not mix projects that require incompatible test platforms in one shared pipeline path without explicit branching.
- Keep one documented source of truth for runner mode: `global.json`, repo wrapper scripts, or the NUKE build layer.

## Failure Diagnostics
- Missing or changed test-report output after a runner migration: confirm whether the repo is still in VSTest mode.
- Coverage flags accepted locally but not in CI: compare runner selection, SDK version, and wrapper command path.
- Unexpected `dotnet test` output layout: check whether `--artifacts-path` or repo-specific output directories were changed.

## NUKE + Microsoft.Testing.Platform Limitation (Current — NUKE issue #1584)

**Status: unresolved as of 2026-07-11. NUKE issue #1584 (opened Dec 22 2025) is open, has no maintainer-assigned milestone, and no PR has landed; thread activity is from affected users, not the NUKE maintainer.**

NUKE's built-in test helpers — `DotNetTest`, coverage collector wiring — are VSTest-oriented. They do **not** natively support `Microsoft.Testing.Platform` (MTP). This matters because:

- MTP adoption is repo-by-repo and opt-in, not automatic. A repo only runs in MTP mode if it explicitly sets `test.runner` in `global.json` (or, in the legacy interop path, `TestingPlatformDotnetTestSupport=true`). Do not infer MTP mode from the target framework alone.
- xUnit v3 and TUnit are MTP-only runners (no VSTest fallback) — if a repo has migrated to either, it has necessarily opted into MTP somewhere. NUnit and MSTest support MTP but can still run under classic VSTest.
- VSTest-specific options such as `--logger trx;LogFileName=results.xml` and data-collector XML (`/p:CollectCoverage=true` via Coverlet VSTest adapter) do **not** apply in MTP mode.

**Workaround until NUKE issue #1584 is resolved:** invoke the MTP test runner via NUKE's process API instead of the `DotNetTest` fluent helper.

```csharp
// MTP workaround: drive the test runner directly via Exec/ProcessTasks
// Do NOT use DotNetTasks.DotNetTest — it uses VSTest-oriented options
Target UnitTest => _ => _
    .DependsOn(Compile)
    .Executes(() =>
    {
        ProcessTasks.StartProcess(
            ToolPathResolver.GetPathExecutable("dotnet"),
            $"run --project {TestProjectPath} -- --report-trx --report-trx-filename unit-test-result.trx",
            workingDirectory: RootDirectory
        ).AssertZeroExitCode();
    });
```

Key constraints in MTP mode:
- Use MTP-native reporting flags (`--report-trx`, `--report-junit`) instead of `--logger` VSTest arguments.
- Coverage must use a MTP-compatible collector extension (e.g. `Microsoft.Testing.Extensions.CodeCoverage`) configured via `runsettings` or MTP extension registration, not the VSTest Coverlet collector.
- Do not mix MTP and VSTest invocation paths in one pipeline — pick one per project.
