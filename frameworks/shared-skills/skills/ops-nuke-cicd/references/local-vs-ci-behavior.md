# Local vs CI Behavior

## Purpose
Tune execution for developer speed without sacrificing CI correctness.

## Branching Rules
- Use `IsLocalBuild` for performance choices and output paths.
- Keep test semantics equivalent unless scope intentionally differs.
- Keep pipeline correctness independent from local shortcuts.

## Typical Controls
- `SetNoBuild(IsLocalBuild)` in test targets when binaries are already built locally.
- `EnableNoRestore()` when restore was already executed in graph.
- Local output path for convenience; CI output path for collector compatibility.

## Performance Trade-offs
- `NoBuild` and `NoRestore` reduce local latency but can hide dependency issues if graph is wrong.
- Reusing prior local outputs speeds iteration but increases stale-artifact risk.
- CI should remain explicit and mostly self-sufficient.

## Recommended Pattern
```csharp
var outputFilePath = IsLocalBuild
    ? Path.Combine(".", "deploy.env")
    : Path.Combine(CiProjectDirectory, "deploy.env");
```

## Safeguards
- Ensure local targets still compile/test enough to catch obvious regressions.
- Ensure CI path always executes full quality gates before deploy outputs.
- Keep parity checks: run full `TestAll` locally before major CI pipeline changes.

## CI Docker Host Divergence
- When a CI runner uses a remote Docker daemon, `localhost` on the runner is not the Docker host. Tests that hard-code `127.0.0.1` or `localhost` as the broker/service endpoint will fail silently or connect to nothing.
- Test harnesses must resolve endpoints from `DOCKER_HOST` or Testcontainers host detection, not hard-coded loopback.
- Code-only fixes can make suites CI-compatible, but the final proof requires a real pipeline run on the target CI infrastructure.

## Failure Diagnostics
- Works locally, fails in CI: compare `IsLocalBuild` condition branches.
- CI-only missing files: inspect CI output path and artifact collector configuration.
- Local stale results: clear artifacts or force build/restore during troubleshooting.
- Tests pass locally but fail in CI with connection errors: check whether Docker containers are running on a remote host and endpoints assume localhost.

