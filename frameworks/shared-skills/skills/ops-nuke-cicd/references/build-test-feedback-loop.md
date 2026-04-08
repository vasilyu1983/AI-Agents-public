# Build-Test Feedback Loop

## Goal
Return useful failure signal quickly in local runs while preserving full confidence in CI.

## Iterative Quality Loop
Use this cycle continuously:
1. Edit code and tests.
2. Build (`BuildAll` or equivalent target).
3. Run relevant tests (`LocalUnitTest`, `ApiTest`, `DbTest`, `TestAll`).
4. Fix failures and repeat.

## Loop Design
- Keep compile and lightweight tests first.
- Keep integration-like tests in dedicated targets (`ApiTest`, `DbTest`, `ComponentTests`) after unit success.
- Keep one composed target (`TestAll`) for CI to avoid missing mandatory stages.

## Fast-Feedback Baseline
1. `Restore`
2. `BuildAll`
3. `UnitTest` with filtered categories
4. Optional local-only shortcuts for developer iteration

## CI-Confidence Baseline
1. `BuildAll`
2. `UnitTest`
3. `ApiTest`
4. `DbTest`
5. Coverage/report merge target

## Recommended Sequencing
```csharp
Target LocalUnitTest => _ => _
    .Triggers(BuildAll, UnitTest);

Target TestAll => _ => _
    .Triggers(BuildAll, UnitTest, ApiTest, DbTest, MergeCodeCoverageReports);
```

## Common Command Examples
Use repo wrappers when present:
```bash
./build.sh BuildAll
./build.sh LocalUnitTest
./build.sh ApiTest
./build.sh TestAll
```

Direct NUKE invocation:
```bash
nuke BuildAll
nuke LocalUnitTest
nuke ApiTest
nuke TestAll
```

## Performance Controls
- Use `EnableNoRestore()` in test targets when restore was already completed.
- Use `EnableNoBuild()` for tests when binaries are already produced by earlier targets.
- Use minimal verbosity by default and elevate only for diagnostics.
- Run integration tests only where required by scope.
- For one project, do not run multiple `dotnet test` commands in parallel in the same job.

## Pipeline Wiring as Feature Completion
- New test suites (especially Docker-backed component tests) must be wired into the canonical pipeline path as part of feature completion, not as follow-up cleanup.
- Docker-backed suites need an explicit validation lane and must not accidentally create circular NUKE target graphs.
- Treat pipeline wiring failures as blocking — an unwired suite gives false confidence that the feature is tested.

## Failure Diagnostics
- Slow local loop: confirm local target is not triggering API/DB/component suites.
- Repeated restore/build overhead: confirm `NoRestore` and `NoBuild` settings.
- CI timeout risk: split large suites by category and review container startup readiness.
- Intermittent MSBuild lock failures: sequence test invocations per project and avoid output-path contention.
- New test suite not running in CI: verify the suite's target is reachable from the canonical pipeline entry point without circular dependencies.
