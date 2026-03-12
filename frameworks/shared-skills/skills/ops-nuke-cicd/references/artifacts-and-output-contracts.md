# Artifacts and Output Contracts

## Purpose
Define stable outputs that downstream CI/CD jobs can consume without repo-specific assumptions.

## Contract Principles
- Keep artifact locations deterministic and version-control-friendly.
- Keep filenames stable across local and CI contexts.
- Keep environment variable names backward-compatible.
- Treat output contracts as public interfaces of the pipeline.

## Core Outputs
- `artifacts/coverage-report/**/coverage.cobertura.xml`
- `artifacts/coverage-report/index.html` (or equivalent HTML summary)
- `artifacts/*-unit-test-result.xml`
- `artifacts/*-api-test-result.xml`
- `artifacts/*-db-test-result.xml`
- `deploy.env` (path depends on local vs CI mode)

## deploy.env Behavior
- Local run: commonly write to repo root `./deploy.env`.
- CI run: commonly write to `${CiProjectDirectory}/deploy.env`.
- Include only variables with known values; avoid placeholder keys.

## Producer/Consumer Mapping
- Build targets produce binaries and container images.
- Test targets produce JUnit and raw coverage files.
- Merge target produces merged Cobertura + HTML summary.
- Output target writes deployment env contract for deploy stage.

## Change Management Rules
- If output names/locations change, update all CI collectors and deploy consumers in the same change.
- Keep one source of truth for artifact directory variables.
- Add guard checks when contract files are mandatory for downstream targets.

