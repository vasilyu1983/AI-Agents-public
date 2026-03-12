# PR Pipeline Quality Checklist

- Target graph uses `DependsOn`/`After`/`Triggers` intentionally and minimally.
- Local fast path remains fast and still catches compile + core unit regressions.
- CI composed path includes mandatory suites and coverage merge target.
- Category filters are explicit and reviewed for accidental exclusions.
- Coverage outputs remain in Cobertura format and are merged consistently.
- JUnit files are generated with stable naming patterns.
- Docker images are tagged with traceable metadata and exported with digest references.
- `deploy.env` contract keys are stable and documented.
- Logging is sufficient to diagnose failing targets without rerunning entire pipeline.
- Cleanup targets do not remove artifacts needed by downstream steps.

