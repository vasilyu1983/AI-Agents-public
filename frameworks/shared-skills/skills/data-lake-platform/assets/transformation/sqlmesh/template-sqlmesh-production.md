# SQLMesh Production Operations Template

This template describes a generic route from local development to a controlled
production deployment. It intentionally uses fictional names and placeholders.
Adapt it to the target repository's database, deployment platform, and change
approval process.

## Environment separation

Use separate credentials and, where practical, separate infrastructure for
local development, CI, and production.

```yaml
# config.yaml
gateways:
  local:
    connection:
      type: duckdb
      database: .local/warehouse.db

  ci:
    connection:
      type: postgres
      host: ${CI_DB_HOST}
      port: 5432
      user: ${CI_DB_USER}
      password: ${CI_DB_PASSWORD}
      database: ${CI_DB_NAME}

  production:
    connection:
      type: postgres
      host: ${PROD_DB_HOST}
      port: 5432
      user: ${PROD_DB_USER}
      password: ${PROD_DB_PASSWORD}
      database: ${PROD_DB_NAME}

default_gateway: local
model_defaults:
  dialect: postgres
```

Environment files may contain variable names, but committed examples must never
contain real credentials:

```dotenv
# .env.example
CI_DB_HOST=ci-database.example.invalid
CI_DB_USER=replace-me
CI_DB_PASSWORD=replace-me
CI_DB_NAME=analytics_ci
```

Load production values from the deployment platform's secret store. Prevent
commands from echoing secrets and mask them in CI logs.

## Repository layout

```text
analytics/
├── config.yaml
├── models/
│   ├── staging/
│   ├── core/
│   └── marts/
├── audits/
├── tests/
├── seeds/
└── scripts/
    └── verify_changes.sh
```

The layer names are examples. What matters is that each layer has a documented
input contract and that consumers know which schemas are stable.

## Local verification script

```bash
#!/usr/bin/env bash
set -euo pipefail

gateway="${SQLMESH_GATEWAY:-local}"
environment="${SQLMESH_ENVIRONMENT:-$(git branch --show-current)}"

if [[ -z "$environment" ]]; then
  echo "Unable to determine an environment name" >&2
  exit 2
fi

sqlmesh format --check
sqlmesh test --gateway "$gateway"
sqlmesh plan "$environment" --gateway "$gateway" --no-prompts
```

The script validates and previews. It does not auto-apply a production plan.

## Deployment sequence

1. Format and render changed models locally.
2. Run unit tests and audits against disposable data.
3. Create an isolated SQLMesh environment for the branch or pull request.
4. Review the plan for breaking and forward-only changes.
5. Apply to a non-production gateway.
6. Obtain the repository's required approval.
7. Apply the reviewed production plan using a protected job.
8. Monitor freshness, audit results, runtime, and downstream errors.
9. Remove temporary environments after their retention window.

Production application should require a protected branch or environment, a
least-privilege service identity, and a serialized deployment lock.

## Generic CI workflow

```yaml
name: sqlmesh-check

on:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.lock
      - run: sqlmesh format --check
      - run: sqlmesh test --gateway ci
      - run: sqlmesh plan "pr_${{ github.event.pull_request.number }}" --gateway ci --no-prompts
        env:
          CI_DB_HOST: ${{ secrets.CI_DB_HOST }}
          CI_DB_USER: ${{ secrets.CI_DB_USER }}
          CI_DB_PASSWORD: ${{ secrets.CI_DB_PASSWORD }}
          CI_DB_NAME: ${{ secrets.CI_DB_NAME }}
```

Pin third-party actions to immutable revisions where the repository's supply
chain policy requires it.

## Seed data

Seeds must be synthetic, minimal, and stable.

```csv
order_id,customer_id,order_status,ordered_at
1001,501,completed,2025-01-10T09:00:00Z
1002,502,cancelled,2025-01-10T10:00:00Z
```

Never copy production rows into a public fixture. Use reserved documentation
domains, non-routable identifiers, and obviously fictional values.

## Observability

Track at least:

- model duration and failure rate;
- last successful interval by model;
- audit failures and skipped intervals;
- row-count changes at stable grains;
- warehouse resource consumption;
- temporary environment age;
- deployment commit and operator identity.

Alert on user impact and violated data contracts rather than every transient
retry.

## Rollback and recovery

Before deployment, identify whether the change is reversible, forward-only, or
requires a data backfill. Record:

- the previous deployable revision;
- how to restore consumers while data is repaired;
- the acceptable recovery window;
- the owner who can approve a destructive restatement;
- how snapshots and temporary tables will be cleaned up.

Do not improvise a production restatement from a developer workstation.

## Troubleshooting

```bash
# Confirm configuration without exposing secrets.
sqlmesh info --gateway ci

# Render one model for inspection.
sqlmesh render marts.daily_order_totals --start 2025-01-01 --end 2025-01-02

# Preview a disposable environment.
sqlmesh plan investigation_123 --gateway ci --no-prompts
```

If a command behaves differently in CI, compare the SQLMesh version, dialect,
gateway selection, environment variables, and working directory before changing
model logic.

## Production checklist

- Configuration contains placeholders only; secrets come from managed storage.
- CI and production use distinct identities and databases.
- The plan is reviewed before production application.
- Deployment jobs are protected, serialized, and auditable.
- Tests and audits run on the same locked dependency versions used in release.
- Synthetic seeds contain no copied customer or employee data.
- Backfill, rollback, and temporary-environment cleanup are documented.
- Monitoring covers freshness, correctness, cost, and downstream impact.
