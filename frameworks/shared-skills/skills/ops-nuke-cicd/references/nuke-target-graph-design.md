# NUKE Target Graph Design

## Purpose
Design a readable and deterministic target graph that works for both local developer commands and CI pipelines.

## Target Relationship Rules
- Use `DependsOn` for hard prerequisites that must execute before a target.
- Use `After` when both targets may run, but you need execution order.
- Use `Triggers` for high-level orchestration targets that compose lower-level targets.
- Use `OnlyWhenDynamic(...)` to gate expensive stages using runtime conditions.

## Practical Graph Pattern
1. Restore/build foundations.
2. Fast checks (unit tests) early.
3. Slower checks (API/DB/component/integration) after fast gates.
4. Aggregation targets (coverage/report merge) after all required tests.
5. Packaging/publishing stages after quality gates.

## Migration Graph Pattern (Legacy Compose to NUnit API)
1. Keep `BuildAll` as compile gate.
2. Keep `UnitTest` excluding `ApiTest`/`DbTests`/`ComponentTests`.
3. Keep `ApiTest` as dedicated category run over API test projects.
4. Keep `DbTest` separate if present.
5. Keep `TestAll` as orchestration trigger only.
6. Remove compose orchestration targets and environment plumbing once decommissioned.

## Example Structure
```csharp
Target UnitTest => _ => _
    .DependsOn(BuildAll)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() => { /* dotnet test filter excludes ApiTest */ });

Target ApiTest => _ => _
    .DependsOn(BuildAll)
    .After(UnitTest)
    .OnlyWhenDynamic(IsBuildRequired)
    .Executes(() => { /* dotnet test filter=ApiTest */ });

Target TestAll => _ => _
    .Triggers(BuildAll, UnitTest, ApiTest, DbTest, MergeCodeCoverageReports);
```

## Design Checks
- Verify each target has a single clear responsibility.
- Verify high-level orchestration targets avoid direct implementation logic.
- Verify graph ordering prevents expensive work before fast failures are known.
- Verify graph names communicate intent (`UnitTest`, `ApiTest`, `TestAll`, `BuildAndPushImagesAll`).

## New Suite Wiring Rules
- Any new Docker-backed test suite (component, integration, Kafka) must have a dedicated NUKE target wired into the canonical pipeline graph from day one. Do not create suites that can only run manually or outside the pipeline.
- Verify the new target does not create a circular dependency in the `Triggers`/`DependsOn` graph.
- Pipeline wiring is part of feature completion, not follow-up cleanup.
- A Docker-backed suite should have an explicit validation lane separate from fast unit tests, gated behind Docker availability checks.

## Failure Diagnostics
- If expected prerequisites do not run, check `DependsOn`.
- If order is wrong despite execution, check `After`.
- If targets are unexpectedly skipped, inspect `OnlyWhenDynamic` conditions.
- If orchestration misses steps, inspect `Triggers` definitions.
- If a new test suite runs locally but is not executed in CI, verify it has an explicit NUKE target and is included in the orchestration graph.
