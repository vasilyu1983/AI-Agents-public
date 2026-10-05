# Test Platform Modes

## Purpose
Use this guide when NUnit advice depends on the repository's test runner, adapter, or `dotnet test` mode. Repository-wide runner selection, CLI arguments, CI wiring, and report publication belong to [`ops-nuke-cicd/references/test-platform-modes-and-cli.md`](../../ops-nuke-cicd/references/test-platform-modes-and-cli.md); this file keeps only the NUnit-specific parts.

## What To Check First
- `global.json` `test.runner` (MTP mode), plus any runner-selection environment variable the installed SDK supports (check the `dotnet test` docs for that SDK).
- Test project properties: `EnableNUnitRunner`, `OutputType`, `TestingPlatformDotnetTestSupport`.
- `NUnit3TestAdapter` major version and the test project's target framework.
- Coverage package: `coverlet.collector`/`coverlet.msbuild` (VSTest) vs `coverlet.MTP`/`Microsoft.Testing.Extensions.CodeCoverage` (MTP).

## Versions

Look up the current NUnit, NUnit3TestAdapter and NUnit.Analyzers releases on NuGet, and whether NUnit 5 has reached GA, before pinning.

| Package / runtime | Notes |
|---|---|
| NUnit 4 | Targets net462 / net6.0 / net8.0 |
| NUnit 5 | Check GA status on NuGet. The betas target net462 / net8.0 / net10.0 (net6.0 dropped). Do not adopt a pre-release for production |
| NUnit3TestAdapter | Name covers NUnit 3 and 4 |
| NUnit.Analyzers | Can flag unawaited async asserts ahead of NUnit 5; confirm the rule exists in the version you pin |
| .NET 8 LTS / .NET 9 STS | Check end-of-support dates on the .NET support policy page; plan the move to .NET 10 LTS + adapter 6.x before they lapse |

### NUnit 5 readiness (from the NUnit 5 pre-release notes; recheck at GA)
- `Assert.ThrowsAsync`, `Assert.CatchAsync`, `Assert.DoesNotThrowAsync` return `Task` and must be awaited, or the assertion is not evaluated.
- `TestDelegate` and `ActualValueDelegate` are removed (4.6 already converted them to `Action`/`Func<T>`).
- `[Platform("NET")]`/`"DotNET"` now mean modern .NET; use `NETFramework`/`DotNETFramework` for .NET Framework.

## Adapter ↔ MTP ↔ Minimum TFM Matrix

| NUnit3TestAdapter | MTP generation | Minimum TFM | Notes |
|---|---|---|---|
| 4.x | None (VSTest only) | .NET Framework 4.6.1 / netcoreapp2.1 | No MTP support |
| 5.x | MTP 1.x | .NET Core 3.1 | Enable with `<EnableNUnitRunner>true</EnableNUnitRunner>` |
| 6.x | MTP 2 | .NET 8.0 | Dropped .NET Core 3 support; assembly loading moved to AssemblyLoadContext for .NET 8+ |

Picking the wrong adapter major for an MTP-based repo causes silent test-discovery failures. Adapter 5.x with MTP 2 does not work; use 6.x.

## Runner Mode Facts
- **VSTest mode is the default for `dotnet test`, including on the .NET 10 SDK.** MTP mode is opt-in via `global.json` (`{"test":{"runner":"Microsoft.Testing.Platform"}}`) and was introduced with the .NET 10 SDK. Do not infer MTP mode from the target framework.
- Running MTP projects under VSTest mode (`TestingPlatformDotnetTestSupport=true`) is legacy; that path is removed in MTP 2 when run with the .NET 10 SDK and remains for .NET 9 SDK and earlier.
- Do not mix VSTest-mode and MTP-mode projects in one solution; set the MTP properties in `Directory.Build.props`.
- Migration steps (the `--` separator is now optional but may be kept; `--project`, `--solution`, `--test-modules`) live in the sibling file and the [MS Learn page](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test).

Enable the NUnit MTP runner in the test project:
```xml
<PropertyGroup>
  <EnableNUnitRunner>true</EnableNUnitRunner>
  <OutputType>Exe</OutputType>
</PropertyGroup>
```

## Guarding Against "0 Tests" Under MTP
- Exit code `8` is the zero-tests code. By default an all-skipped run still succeeds; `--zero-tests-policy strict` makes it fail (check the option exists in your MTP version).
- `--minimum-expected-tests <N>` fails the run with exit code `9` when fewer than N tests run. Use it in CI category runs so a discovery regression cannot pass green.
- `--report-trx` is not built in: reference `Microsoft.Testing.Extensions.TrxReport`, or the test app rejects the option (exit code 5).

## Coverage Under MTP

| Package | When to use |
|---|---|
| `coverlet.MTP` | Coverlet-compatible coverage natively in MTP; outputs json/lcov/opencover/cobertura |
| `Microsoft.Testing.Extensions.CodeCoverage` | Microsoft's free coverage extension; managed and native code; requires `--coverage` |

- `coverlet.collector` and `coverlet.msbuild` rely on VSTest and silently produce no coverage under MTP.
- `Microsoft.Testing.Extensions.CodeCoverage` defaults `IncludeTestAssembly` to `false` (VSTest defaulted to `true`), so coverage percentages shift after migration even with no code change.

## Red Flags
- Advice copied from an older repo assumes `NUnit3TestAdapter` behavior without checking package references.
- VSTest collectors or `--logger` switches mixed with MTP assumptions.
- `coverlet.collector` left in place after enabling MTP.
- Adapter 5.x paired with MTP 2.
