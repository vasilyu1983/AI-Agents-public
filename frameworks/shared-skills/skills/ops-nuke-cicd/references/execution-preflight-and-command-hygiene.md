# Execution Preflight and Command Hygiene

## Purpose
Reduce avoidable CI/local failures caused by missing prerequisites, bad paths, shell quoting, and glob expansion.

## Preflight Checklist
- Confirm repository root and expected working directory before running path-sensitive commands.
- Confirm required SDK/runtime versions before build or test runs.
- Confirm Docker availability before running API/DB/component suites that need containers.
- Confirm target files/directories exist before running `sed`, `cat`, or `ls` against hardcoded paths.

## Port and Endpoint Preflight
- No hard-coded localhost ports in Docker-backed test configurations — use dynamic host-port reservation for container endpoints.
- Resolve the externally reachable Docker host from Testcontainers API or `DOCKER_HOST` env var instead of assuming `127.0.0.1`.
- Provide env var overrides (`KAFKA_BOOTSTRAP`, `DB_HOST`, etc.) so developers can point tests at manual local instances when needed.
- Regression check: tests must still pass when the old fixed ports are intentionally occupied.

## Shell Safety Rules
- Prefer `rg --files` and explicit file lists over broad shell globs.
- Quote command arguments that include special characters or whitespace.
- Avoid patterns that depend on shell-specific glob behavior.
- For complex commands, test a narrow path first before expanding scope.

## Test Scope Guardrails
- If user constraints exclude infra-dependent suites, do not run those suites implicitly.
- Run feasible targets first (`BuildAll`, `LocalUnitTest`, scoped API/DB tests when available).
- Report skipped targets with clear reason and exact follow-up command.

## Frequent Failure Patterns and Fixes
- `no such file or directory`: verify path from repo root and discover files with `rg --files`.
- `no matches found` (zsh glob): replace raw glob with `rg --files <dir> | rg <pattern>`.
- shell parse/syntax errors: simplify quoting and split compound commands.
- build log file locked: avoid concurrent NUKE runs that write to the same temp log file.

## NuGet Signed-Package Verification

Starting with the .NET 8 SDK, NuGet signature verification is **enabled by default** on restore. No explicit opt-in is required. Packages from nuget.org are verified against the author and repository signatures at restore time.

To explicitly verify a downloaded package or audit a package file before use:

```csharp
Target VerifyPackages => _ => _
    .Executes(() =>
    {
        // Verify all .nupkg files in the artifacts output
        foreach (var package in ArtifactsDirectory.GlobFiles("**/*.nupkg"))
        {
            ProcessTasks.StartProcess(
                ToolPathResolver.GetPathExecutable("dotnet"),
                $"nuget verify \"{package}\"",
                workingDirectory: RootDirectory
            ).AssertZeroExitCode();
        }
    });
```

Preflight rules:
- Do not disable signature verification in CI (`DOTNET_NUGET_SIGNATURE_VERIFICATION=false`) unless the package source is a private feed with unsigned packages — and document the exception explicitly.
- Add `VerifyPackages` as a preflight or post-restore gate in the target graph when the pipeline produces or consumes signed `.nupkg` artifacts.
- Source: https://learn.microsoft.com/en-us/dotnet/core/tools/nuget-signed-package-verification

## Verification
- Run one narrow command successfully before batch command execution.
- Re-run failing target in isolation after fixing preflight issues.
- Keep final report explicit about prerequisites and skipped validations.
