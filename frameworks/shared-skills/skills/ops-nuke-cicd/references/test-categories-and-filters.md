# Test Categories and Filters

## Purpose
Control test scope with predictable category filters so local and CI runs execute the intended suites.

## Category Strategy
- Use category names as contract: `ApiTest`, `DbTests`, `ComponentTests`, plus default unit tests.
- Keep category assignment explicit in NUnit attributes.
- Keep NUKE filter expressions centralized per target.
- Keep API migration suites under `ApiTest` and exclude them from `UnitTest`.

## Filter Patterns
- Unit-only exclusion pattern:
```text
TestCategory!=ComponentTests&TestCategory!=DbTests&TestCategory!=ApiTest
```
- API-only pattern:
```text
TestCategory=ApiTest
```
- DB-only pattern:
```text
TestCategory=DbTests
```

## Target Mapping Example
```csharp
Target UnitTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter("TestCategory!=ComponentTests&TestCategory!=DbTests&TestCategory!=ApiTest")));

Target ApiTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter("TestCategory=ApiTest")));

Target DbTest => _ => _
    .Executes(() => DotNetTasks.DotNetTest(s => s
        .SetFilter("TestCategory=DbTests")));
```

## Migration Refactor Rules
- If migrating from compose/SpecFlow flow, remove legacy orchestration targets from test graph.
- Keep one dedicated `ApiTest` target over API test projects.
- Keep `TestAll` composed from `BuildAll + UnitTest + ApiTest (+ DbTest) + coverage merge`.

## Validation Checks
- Verify each category has at least one test.
- Verify unit target excludes integration categories.
- Verify CI composed target includes all mandatory categories.
- Verify filter strings are identical between local and CI paths when scope should match.

## Common Failure Modes
- Category typo causes tests to silently skip.
- Broad exclusion filters hide suites that should run.
- Project-level test target mismatch (wrong `.csproj`) drops expected tests.
- Running parallel `dotnet test` on the same project output causes intermittent file-lock/MSBuild failures.
