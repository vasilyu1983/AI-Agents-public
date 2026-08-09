# Coverage and Reporting

## Purpose
Produce machine-consumable and human-readable outputs from all test stages with stable paths and names.

## Required Outputs
- Per-run coverage collector output in Cobertura format.
- Merged coverage artifact for CI quality gates.
- HTML summary for quick inspection.
- JUnit XML files per suite for CI test reports.

## Platform Alignment
- Pick coverage and logger arguments that match the repository test platform.
- VSTest-oriented collector and logger patterns are still valid for many repos, but they are not universal once the repo adopts `Microsoft.Testing.Platform`.
- When invoking `dotnet test` directly, prefer `--artifacts-path` or one stable NUKE-owned artifacts root to avoid output collisions.

## VSTest-Oriented DotNet Test Pattern
```csharp
DotNetTasks.DotNetTest(s => s
    .SetDataCollector("XPlat Code Coverage;Format=cobertura")
    .SetResultsDirectory($"{ArtifactsDirectory}/coverage-report")
    .AddLoggers($"junit;LogFilePath={ArtifactsDirectory}/{{assembly}}-unit-test-result.xml;MethodFormat=Class;FailureBodyFormat=Verbose"));
```

## Coverage Merge Pattern
Use ReportGenerator to merge all `coverage.cobertura.xml` files:
```csharp
ReportGenerator(s => s
    .SetReports($"{ArtifactsDirectory}/coverage-report/**/coverage.cobertura.xml")
    .SetTargetDirectory($"{ArtifactsDirectory}/coverage-report")
    .SetAssemblyFilters("-*.Tests", "-*.Tests.*")
    .SetReportTypes(ReportTypes.Cobertura, ReportTypes.HtmlSummary));
```

## Publish Checklist
- Verify Cobertura XML exists after each relevant test target.
- Verify merged `Cobertura.xml` and HTML summary exist after merge target.
- Verify JUnit files are emitted with stable filename patterns.
- Verify logger and coverage options still match the chosen test platform after SDK or runner migrations.
- Verify CI collects all paths using wildcard-safe patterns.

## Failure Diagnostics
- Empty merged report: check `SetReports` glob and suite execution.
- Missing JUnit files: check logger string and results path permissions.
- Missing outputs after runner migration: confirm whether the repo switched from VSTest behavior to `Microsoft.Testing.Platform`.
- Unexpected coverage drop: confirm all intended targets feed merge stage.
