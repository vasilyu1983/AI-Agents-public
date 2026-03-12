# Infrastructure Troubleshooting

## Purpose
Use this guide to diagnose common test infrastructure failures.

## Startup Failures
- Verify container image tags are valid and pinned.
- Check readiness timeout vs actual startup duration.
- Print container logs before failing fixture setup.

## Port Collisions
- Prefer dynamic ports for local and CI runs.
- Expose chosen port in diagnostics.
- Avoid global static server instances across fixtures.

## Readiness Issues
- Wait on health endpoint or explicit query, not startup completion alone.
- Re-check connection strings from runtime configuration.
- Validate migration/seed step completed before first assertion.

## Migrator Ordering Issues
- Symptom: `Cannot find the object 'dbo.TPurseSections'`.
  - Cause: dependent migrator did not run before ledger/service migrator.
  - Fix: enforce deterministic migrator order and table checks between steps.
- Symptom: migrator exits but schema is incomplete.
  - Cause: wrong command/entrypoint or wrong mounted migration folder.
  - Fix: use canonical migrator command and verify bind mounts.

## Command Mismatch Issues
- Symptom: migrator behavior differs from reference repos.
  - Cause: custom command flags (for example `--readycheck`) diverge from baseline.
  - Fix: use default fluent migrator command `dotnet Sc.Tool.FluentMigrator.dll migrateup -m /sql` unless explicitly required otherwise.

## Cleanup Issues
- Dispose containers and servers in `OneTimeTearDown`.
- Guard teardown with null checks for partial setup failures.
- Surface teardown errors in test output.

## Build/Test Concurrency Issues
- Symptom: intermittent MSBuild/test failures with locked files.
  - Cause: parallel `dotnet test` runs against the same project output path.
  - Fix: run project-level test invocations sequentially or isolate output paths.

## Prerequisite Gaps
- If Docker/Testcontainers is unavailable, do not run container-dependent suites implicitly.
- Run feasible suites first (unit or non-container API tests).
- Report skipped categories explicitly with reason and follow-up command.
- Keep final validation summary clear about what is verified vs pending.
