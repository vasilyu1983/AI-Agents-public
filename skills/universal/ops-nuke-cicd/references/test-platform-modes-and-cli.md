# Test Platform Modes and CLI

## Purpose
Keep `dotnet test`, coverage, and reporting behavior coherent as repositories move from VSTest-oriented flows to `Microsoft.Testing.Platform`.

## Platform Rule
- Choose one repository test platform per command path and keep local and CI behavior aligned.
- Keep VSTest-compatible guidance only for repos that still depend on VSTest loggers, collectors, or `Microsoft.NET.Test.Sdk` behavior.
- If the repo opts into `Microsoft.Testing.Platform`, review runner-specific arguments before changing logging or coverage switches.

## Current .NET Guidance
- `dotnet test` remains the main entry point for both VSTest and `Microsoft.Testing.Platform` flows.
- **VSTest is the default mode of `dotnet test` on the .NET 10 SDK.** Select MTP with a `test.runner` entry in `global.json` (`{"test":{"runner":"Microsoft.Testing.Platform"}}`). Newer SDKs may also support a `DOTNET_TEST_RUNNER` environment override; check the [installed SDK's runner-selection rules](https://learn.microsoft.com/dotnet/core/tools/dotnet-test) and the effective environment before changing arguments. Also inspect project-level MTP settings (`EnableNUnitRunner`, `EnableMSTestRunner`, `TestingPlatformDotnetTestSupport`).
- A repo can also run MTP-native tests *while staying in VSTest mode* by setting `TestingPlatformDotnetTestSupport=true` (MSBuild property, defaults to `false`). This is the legacy interop path Microsoft is deprecating in favor of full `global.json` MTP mode — treat it as a hint the repo hasn't fully migrated yet, not as MTP mode itself.
- Use `--artifacts-path` when CLI-driven runs need isolated output roots per project.
- Terminal Logger (`--tl`) behavior is now part of normal `dotnet test` ergonomics; disable it only when a CI log parser or export step requires plain console output.

## Practical Guardrails
- Do not assume VSTest collectors or `--logger` values will behave the same once the repo switches runner mode.
- Do not mix projects that require incompatible test platforms in one shared pipeline path without explicit branching.
- Document the effective runner selection, including an environment override when the installed SDK supports it, in the repo wrapper or NUKE build layer.

## Failure Diagnostics
- Missing or changed test-report output after a runner migration: confirm whether the repo is still in VSTest mode.
- Coverage flags accepted locally but not in CI: compare runner selection, SDK version, and wrapper command path.
- Unexpected `dotnet test` output layout: check whether `--artifacts-path` or repo-specific output directories were changed.

## NUKE + Microsoft.Testing.Platform Limitation (NUKE issue #1584)

**Check the issue's current status (for example `gh issue view 1584 --repo nuke-build/nuke`) and the installed NUKE helper API before relying on the workaround below.**

NUKE issue #1584 documents a VSTest-oriented `DotNetTest` helper and coverage wiring. If the installed helper still lacks native `Microsoft.Testing.Platform` (MTP) support, this matters because:

- MTP adoption is opt-in, not automatic. Check `global.json` and supported runner overrides for MTP mode; `TestingPlatformDotnetTestSupport=true` is a separate legacy interop path through VSTest mode. Do not infer runner mode from the target framework alone.
- xUnit v3 supports both MTP and VSTest; VSTest requires `xunit.runner.visualstudio` and `Microsoft.NET.Test.Sdk`. TUnit uses MTP and has no VSTest adapter. NUnit and MSTest support both platforms.
- VSTest-specific options such as `--logger trx;LogFileName=results.xml` and data-collector XML (`/p:CollectCoverage=true` via Coverlet VSTest adapter) do **not** apply in MTP mode.

**Workaround if the installed NUKE helper still lacks MTP support:** invoke the MTP test runner via NUKE's process API instead of the `DotNetTest` fluent helper.

```csharp
// MTP workaround: drive the test runner directly via Exec/ProcessTasks
// Do NOT use DotNetTasks.DotNetTest — it uses VSTest-oriented options
Target UnitTest => _ => _
    .DependsOn(Compile)
    .Executes(() =>
    {
        // --report-trx needs the Microsoft.Testing.Extensions.TrxReport package in the test project;
        // without it the test app rejects the option.
        ProcessTasks.StartProcess(
            ToolPathResolver.GetPathExecutable("dotnet"),
            $"run --project {TestProjectPath} -- --report-trx --report-trx-filename unit-test-result.trx",
            workingDirectory: RootDirectory
        ).AssertZeroExitCode();
    });
```

Key constraints in MTP mode:
- Use MTP-native reporting options instead of `--logger` VSTest arguments. `--report-trx` is not built in: it requires `Microsoft.Testing.Extensions.TrxReport`, or the test app rejects the option. `--report-junit` likewise requires `Microsoft.Testing.Extensions.JUnitReport`, which Microsoft marks experimental; confirm its options with the test app's `--help` before wiring a collector to it.
- Coverage must use a MTP-compatible collector extension (e.g. `Microsoft.Testing.Extensions.CodeCoverage`) configured via `runsettings` or MTP extension registration, not the VSTest Coverlet collector.
- Do not mix MTP and VSTest invocation paths in one pipeline — pick one per project.
