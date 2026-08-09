# Pipeline Reliability and Observability

## Purpose
Make failures obvious, reproducible, and fast to diagnose.

## Reliability Practices
- Fail fast on compile and unit-test errors before expensive stages.
- Keep target side effects deterministic and idempotent where possible.
- Keep container prerequisites explicit for API/DB test stages.
- Keep cleanup steps separated from required deploy-output generation.
- Keep project-level `dotnet test` invocations sequential when they target the same build output location.

## Logging Practices
- Log key runtime identifiers: build id, commit, image tag, and digest.
- Log start/end of expensive stages with clear target names.
- Use minimal default verbosity and targeted debug verbosity during incidents.
- Print Docker/environment diagnostics before integration-style tests.

## Observability Signals
- Stage duration and queue time trends.
- Pass/fail rates by test category.
- Coverage merge success/failure and report size deltas.
- Docker push digest extraction reliability.

## Incident Playbook
1. Locate first failing target.
2. Verify prerequisite target completion and gate conditions.
3. Inspect generated artifacts in expected locations.
4. Re-run failing target in isolation with elevated verbosity.
5. Patch root cause, then run composed target path to verify graph integrity.

## Useful Guardrails
- Enforce stable artifact names in CI config.
- Add explicit checks for required files before publish/deploy steps.
- Keep category filters under source control, not inline in CI YAML only.
- For repeated file-lock incidents, run tests with `NoBuild` after one upfront build and avoid concurrent test commands against same project output.
