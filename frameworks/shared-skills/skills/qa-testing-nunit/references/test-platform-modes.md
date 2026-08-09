# Test Platform Modes

## Purpose
Use this guide when NUnit advice depends on the repository's current test runner or `dotnet test` mode.

## What To Check First
- Whether the repo is still using VSTest-oriented behavior or has adopted `Microsoft.Testing.Platform`.
- Whether `global.json`, package references, or build scripts pin a specific test runner path.
- Whether the repo still depends on `NUnit3TestAdapter` for discovery or execution.

## Current Runner Rules
- Do not assume logger, coverage collector, or adapter behavior is identical across runner modes.
- Treat package and CLI guidance as version-sensitive; verify against `data/sources.json` before recommending commands.
- Keep fixture and suite design in this skill, but route repository-wide runner/coverage/CI changes to `$ops-nuke-cicd`.

## Version Decision (verify against sources before relying)

The NUnit framework package moves fast. NUnit 4.6.1 is the current stable release (May 2026); do not pin examples to older 4.x in new projects. NUnit 4 requires minimum .NET Framework 4.6.2 or .NET 6.0.

### Adapter ↔ MTP ↔ Minimum TFM Matrix

| NUnit3TestAdapter | MTP generation | Minimum TFM | Notes |
|---|---|---|---|
| 4.x | None (VSTest only) | .NET Framework 4.6.1 / netcoreapp2.1 | No MTP support |
| 5.x | MTP 1.x (up to 1.9) | .NET Core 3.1 | Enable with `<EnableNUnitRunner>true</EnableNUnitRunner>` |
| 6.x | MTP 2.0 | .NET 8.0 | Dropped .NET Core 3 support; assembly loading moved to AssemblyLoadContext for .NET 8+ |

Current stable: **NUnit3TestAdapter 6.2.0** (March 2026). The name "NUnit3TestAdapter" covers both NUnit 3 and 4.

Picking the wrong adapter major for an MTP-based repo causes silent test-discovery failures. Confirm the adapter major ↔ MTP generation ↔ minimum TFM match before recommending a pin.

### dotnet test modes (.NET 10 SDK vs. earlier)

`dotnet test` now operates in two distinct modes:

- **VSTest mode** (default for .NET 9 SDK and earlier): original behavior; runs MTP projects only when `TestingPlatformDotnetTestSupport=true` is set and `Microsoft.Testing.Platform.MSBuild` is referenced.
- **MTP mode** (introduced with .NET 10 SDK): opt-in via `global.json`; does not require `TestingPlatformDotnetTestSupport`; passes MTP-native arguments directly without the extra `--` separator.

To enable MTP mode in `global.json`:
```json
{
    "test": {
        "runner": "Microsoft.Testing.Platform"
    }
}
```

Migration steps from VSTest mode to MTP mode:
1. Add `test.runner` to `global.json`.
2. Remove `TestingPlatformDotnetTestSupport` from project files.
3. Remove `TestingPlatformCaptureOutput` and `TestingPlatformShowTestsFailure`.
4. Remove the extra `--` separator: `dotnet test -- --report-trx` → `dotnet test --report-trx`.
5. Replace `dotnet test MySolution.sln` with `dotnet test --solution MySolution.sln`.

Running MTP projects under VSTest mode is considered legacy in favor of MTP mode. VSTest support for MTP will be removed in MTP version 2 when running with the .NET 10 SDK; it remains for .NET 9 SDK and earlier.

### Enabling MTP in NUnit projects

Add to the test project `.csproj`:
```xml
<PropertyGroup>
  <EnableNUnitRunner>true</EnableNUnitRunner>
  <OutputType>Exe</OutputType>
  <!-- For VSTest mode of dotnet test only: -->
  <TestingPlatformDotnetTestSupport>true</TestingPlatformDotnetTestSupport>
</PropertyGroup>
```

Set `TestingPlatformDotnetTestSupport` in `Directory.Build.props` to avoid a mixed VSTest/MTP solution — mixing is unsupported.

## NUnit-Specific Implications
- `FixtureLifeCycle`, `Parallelizable`, analyzers, and assertion patterns remain valid regardless of runner mode.
- Discovery, logging, and coverage behavior may change when the repo moves to `Microsoft.Testing.Platform`.
- If a user asks how to change `dotnet test` arguments, category filters in CI, or coverage/report publication, hand off to `$ops-nuke-cicd`.

## Coverage Tooling Under MTP

`coverlet.collector` and `coverlet.msbuild` **cannot** be used with MTP — both rely on VSTest infrastructure. Use one of:

| Package | When to use |
|---|---|
| `coverlet.MTP` | Coverlet-compatible coverage natively in MTP; outputs json/lcov/opencover/cobertura |
| `Microsoft.Testing.Extensions.CodeCoverage` | Microsoft's closed-source free coverage extension; supports managed and native code; requires `--coverage` flag |

`coverlet.collector` is only valid in VSTest mode. Repos migrating from VSTest to MTP must swap to `coverlet.MTP` or `Microsoft.Testing.Extensions.CodeCoverage`.

## Red Flags
- Advice copied from an older repo assumes `NUnit3TestAdapter` without checking package references.
- A request mixes VSTest collectors or logger switches with `Microsoft.Testing.Platform` assumptions.
- The repo changed test runner mode, but the skill response still treats command-line behavior as static.
- Using `coverlet.collector` with MTP — it silently produces no coverage output.
- Using NUnit3TestAdapter 5.x with MTP 2.0 (requires adapter 6.x).
