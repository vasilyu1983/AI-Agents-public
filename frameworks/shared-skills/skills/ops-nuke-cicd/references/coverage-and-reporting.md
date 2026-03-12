# Coverage and Reporting

## Purpose
Produce machine-consumable and human-readable outputs from all test stages with stable paths and names.

## Required Outputs
- Per-run coverage collector output in Cobertura format.
- Merged coverage artifact for CI quality gates.
- HTML summary for quick inspection.
- JUnit XML files per suite for CI test reports.

## DotNet Test Output Pattern
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
- Verify CI collects all paths using wildcard-safe patterns.

## Failure Diagnostics
- Empty merged report: check `SetReports` glob and suite execution.
- Missing JUnit files: check logger string and results path permissions.
- Unexpected coverage drop: confirm all intended targets feed merge stage.

