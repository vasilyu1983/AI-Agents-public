# CI Scripts — qa-api-testing-contracts

Runnable bash scripts for API contract-testing CI gates. Each script is POSIX-bash-portable, fails fast on missing env vars, and prints a stable status line on success.

Copy any script into your pipeline or call it from a CI job step.

---

## Scripts

### `pact_can_i_deploy.sh`

**Purpose:** Gate a deployment by querying the Pact Broker `can-i-deploy` endpoint. Exits non-zero if the pacticipant version has unverified or failed pact verifications for the target environment.

**Required env vars:**

| Variable | Description |
|---|---|
| `PACT_BROKER_BASE_URL` | Base URL of the Pact Broker or PactFlow instance |
| `SERVICE` | Pacticipant name (consumer or provider) |
| `GIT_SHA` | Version string to check (usually the current commit SHA) |

**Optional env vars:**

| Variable | Default | Description |
|---|---|---|
| `PACT_BROKER_TOKEN` | _(none)_ | Bearer token for PactFlow or authenticated brokers |
| `TO_ENVIRONMENT` | `production` | Target environment name |

**Exit codes:** `0` = safe to deploy; `1` = unsafe or error.

**GitHub Actions snippet:**

```yaml
- name: Pact can-i-deploy
  env:
    PACT_BROKER_BASE_URL: ${{ secrets.PACT_BROKER_BASE_URL }}
    PACT_BROKER_TOKEN: ${{ secrets.PACT_BROKER_TOKEN }}
    SERVICE: my-service
    GIT_SHA: ${{ github.sha }}
    TO_ENVIRONMENT: production
  run: bash scripts/pact_can_i_deploy.sh
```

**GitLab CI snippet:**

```yaml
pact-can-i-deploy:
  stage: deploy-gate
  script:
    - bash scripts/pact_can_i_deploy.sh
  variables:
    SERVICE: my-service
    GIT_SHA: $CI_COMMIT_SHA
    TO_ENVIRONMENT: production
```

---

### `schemathesis_baseline.sh`

**Purpose:** Run Schemathesis property-based checks (`--checks all`) against an OpenAPI spec. Uses `uvx` so no persistent install is required. Prints a stable summary line for CI log parsing.

**Required env vars:**

| Variable | Description |
|---|---|
| `OPENAPI_URL` | URL or local path to the OpenAPI spec (e.g. `http://localhost:8000/openapi.json` or `./openapi.yaml`) |

**Optional env vars:**

| Variable | Default | Description |
|---|---|---|
| `SCHEMATHESIS_MAX_EXAMPLES` | `200` | Max Hypothesis examples per test case |
| `SCHEMATHESIS_BASE_URL` | _(from spec)_ | Override base URL for requests |
| `SCHEMATHESIS_WORKERS` | `auto` | Number of parallel workers |

**Exit codes:** `0` = all checks passed; `1` = one or more checks failed.

**GitHub Actions snippet:**

```yaml
- name: Schemathesis baseline
  env:
    OPENAPI_URL: http://localhost:8000/openapi.json
  run: bash scripts/schemathesis_baseline.sh
```

**GitLab CI snippet:**

```yaml
schemathesis-baseline:
  stage: test
  script:
    - bash scripts/schemathesis_baseline.sh
  variables:
    OPENAPI_URL: http://localhost:8000/openapi.json
```

---

### `buf_breaking_check.sh`

**Purpose:** Detect breaking changes in `.proto` files by running `buf breaking` against a reference (git branch, tag, or buf registry module). Fails the build on any breaking change.

**Required env vars:**

| Variable | Description |
|---|---|
| `REMOTE` | Against-target for `buf breaking`. Examples: `.git#branch=main`, `buf.build/acme/petapis:v1.0.0`, `../proto-baseline` |

**Optional env vars:**

| Variable | Default | Description |
|---|---|---|
| `BUF_INPUT` | `.` | Proto root or module to check |
| `BUF_CONFIG` | _(auto-discovered)_ | Path to `buf.yaml` |

**Exit codes:** `0` = no breaking changes; `1` = breaking changes detected or error.

**GitHub Actions snippet:**

```yaml
- name: buf breaking check
  env:
    REMOTE: .git#branch=main
  run: bash scripts/buf_breaking_check.sh
```

**GitLab CI snippet:**

```yaml
buf-breaking:
  stage: test
  script:
    - bash scripts/buf_breaking_check.sh
  variables:
    REMOTE: .git#branch=main
```

---

### `spectral_lint.sh`

**Purpose:** Lint an OpenAPI, AsyncAPI, or Arazzo document with Spectral. Fails on violations at or above the configured severity.

**Required env vars:**

| Variable | Description |
|---|---|
| `OPENAPI_FILE` | Path to the API spec file to lint |

**Optional env vars:**

| Variable | Default | Description |
|---|---|---|
| `SPECTRAL_RULESET` | `.spectral.yaml` | Path or URL to the Spectral ruleset |
| `SPECTRAL_FAIL_SEVERITY` | `error` | Minimum severity that causes a non-zero exit (`hint` \| `info` \| `warn` \| `error`) |

**Exit codes:** `0` = lint passed; `1` = violations found at or above fail-severity, or Spectral error.

**GitHub Actions snippet:**

```yaml
- name: Spectral lint
  env:
    OPENAPI_FILE: openapi.yaml
  run: bash scripts/spectral_lint.sh
```

**GitLab CI snippet:**

```yaml
spectral-lint:
  stage: test
  script:
    - bash scripts/spectral_lint.sh
  variables:
    OPENAPI_FILE: openapi.yaml
```

---

## Notes

- All scripts use `set -euo pipefail` and the `: "${VAR:?}"` pattern — missing required env vars cause an immediate descriptive error.
- Install prerequisites before running: `pact-broker` CLI (via gem or Docker), `uvx` (from `uv`), `buf`, and `spectral` (via npm or npx).
- Scripts are intentionally thin wrappers. Pass additional flags by extending the `EXTRA_ARGS` arrays inside each script or by wrapping the script call in your CI step.
