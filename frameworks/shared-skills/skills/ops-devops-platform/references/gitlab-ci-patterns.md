# GitLab CI Patterns

*Purpose: Operational patterns and gotchas for medium-to-large GitLab CI estates with parent/child pipelines. Focuses on the things that bite teams in production, not basic syntax.*

## Table of Contents

- [Root-as-Dispatcher Pattern](#root-as-dispatcher-pattern)
- [The MR Variable Trap](#the-mr-variable-trap)
- [Shared Env Bootstrap (`.pre.yml` Pattern)](#shared-env-bootstrap-preyml-pattern)
- [Matrix Jobs for Multi-Script Sources](#matrix-jobs-for-multi-script-sources)
- [Aggregate Pipeline Files](#aggregate-pipeline-files)
- [SQLMesh-on-CI: Read the Command, Not the Job Name](#sqlmesh-on-ci-read-the-command-not-the-job-name)
- [Validation Checklist Before Merge](#validation-checklist-before-merge)
- [Common Change Recipes](#common-change-recipes)

## Root-as-Dispatcher Pattern

For repos with more than ~5 distinct workflows (deploy, ingestion, schema migration, image build, etc.), keep `.gitlab-ci.yml` as a **trigger-only router**. Real work lives in child pipeline files under `.gitlab/`.

```yaml
# .gitlab-ci.yml — dispatcher only
sqlmesh_branch_plan:
  stage: trigger
  trigger:
    include: .gitlab/.sqlmesh_plan.yml
    strategy: depend          # parent waits on child outcome
    forward:
      yaml_variables: true
      pipeline_variables: true
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^sqlmesh_.*/'
```

**Rules of thumb:**

- Edit `.gitlab-ci.yml` only when **dispatch** changes (new top-level route, new `ENVIRONMENT` / `APPLICATION` value).
- Edit a child file when **job behavior** changes.
- Preserve `strategy: depend` unless coupling is intentionally being relaxed.
- Preserve `forward.yaml_variables` and `forward.pipeline_variables` when a child pipeline reads variables defined or computed at root.

## The MR Variable Trap

GitLab's predefined variable availability is **not uniform across pipeline kinds**. The single most common production bug:

> `CI_COMMIT_BRANCH` is **not available** in merge request pipelines.

| Variable | Branch pipeline | MR pipeline | Child pipeline (from MR) |
|---|---|---|---|
| `CI_COMMIT_BRANCH` | Yes | No | No |
| `CI_COMMIT_REF_NAME` | Yes (branch/tag) | Yes (always `HEAD`) | depends on context |
| `CI_MERGE_REQUEST_SOURCE_BRANCH_NAME` | No | Yes | only if forwarded |
| Custom `SOURCE_BRANCH` (root-defined, forwarded) | Yes | Yes | Yes |

**Pattern**: when an MR job needs the source branch name (e.g. for a branch-scoped SQLMesh environment), define `SOURCE_BRANCH` at root and forward it explicitly. Don't assume a variable that works in `rules:` at root is also available inside the child job's `script:`.

> Reference: <https://docs.gitlab.com/ci/variables/predefined_variables/>

## Shared Env Bootstrap (`.pre.yml` Pattern)

Centralize secret/credential export in one job; every downstream job that needs it depends on `pre`.

```yaml
# .gitlab/.pre.yml
pre:
  stage: pre
  script:
    - echo "DB_HOST=$DB_HOST" >> .env_prod
    - echo "DB_PASSWORD=$DB_PASSWORD" >> .env_prod
    # ... export many CI variables ...
  artifacts:
    paths: [.env_prod]
    expire_in: 1 hour
```

```yaml
# .gitlab/.deploy_prod_extension.yml
.deploy_prod:
  stage: deploy_prod
  needs: [pre]
  before_script:
    - set -e
    - while IFS= read -r line; do export "$line"; done < .env_prod
```

Source-specific deploy jobs `extends: .deploy_prod` and inherit the env automatically.

**Anti-patterns:**

- Re-exporting the same secrets in every child pipeline → drift.
- Dropping `needs: [pre]` "to speed things up" → silent missing-variable failures at runtime.
- Replacing the `grep`/`export` pattern in one file but not the others → inconsistent env shape.

## Matrix Jobs for Multi-Script Sources

For ingestion that runs the same script with different inputs (e.g. multiple GA properties), use `parallel.matrix` over copy-paste jobs:

```yaml
.google_analytics_load:
  extends: .deploy_prod
  variables:
    BATCH_SIZE: "10000"
  script:
    - python dlt/google_analytics.py --property "$PROPERTY_ID"
  parallel:
    matrix:
      - PROPERTY_ID: "111111"
      - PROPERTY_ID: "222222"
      - PROPERTY_ID: "333333"
```

Use a single-script job (no matrix) for one-off integrations.

## Aggregate Pipeline Files

Group source jobs by trigger context, not alphabetically:

- `.sources_full.yml` — full refresh batch
- `.sources_all_incremental.yml` — scheduled incrementals
- `.sources_test.yml` — manual / debug runs

When adding a new source: create the source fragment under `.gitlab/sources/`, then include it in **every** aggregate it should run in. Forgetting the second step is a common silent bug — the source merges to main and never runs in production.

Commented-out includes are usually intentional (paused source). Don't re-enable them as a side effect.

## SQLMesh-on-CI: Read the Command, Not the Job Name

Job labels lie. The actual `sqlmesh` command is what matters:

| Command | Effect |
|---|---|
| `sqlmesh plan "$SOURCE_BRANCH" --auto-apply` on gateway `dwh` | Updates the **branch environment** on the prod gateway. Not a promotion. |
| `sqlmesh plan --auto-apply` on gateway `dwh` | **Promotes to `prod`** (no env arg → targets `prod`). |
| `sqlmesh plan <env>` on test gateway | Updates a non-prod environment on the test gateway. |

When reviewing SQLMesh CI changes, read job name, comments, and the actual command — and confirm all three describe the same behavior. Mismatches between "it's just a gate" and "it auto-applies on prod gateway" are how production gets unintentionally rewritten.

> Reference: <https://sqlmesh.readthedocs.io/en/stable/reference/cli/>

## Validation Checklist Before Merge

1. Trace the include chain from `.gitlab-ci.yml` to the edited file. Confirm `rules:` still match the intended trigger.
2. Every `include:` path resolves.
3. Every script variable is set in the job, inherited from `.pre.yml`, or provided by GitLab CI/CD vars — and is **available in this pipeline kind** (branch vs MR vs child).
4. Stage names referenced in jobs are declared in the same child file.
5. New scheduled/web-triggered route → root has matching `rules:` for the intended `ENVIRONMENT` + `APPLICATION` values.
6. SQLMesh jobs: command targets the environment the job name and docs claim it does.
7. Shell scripts keep `set -e` / `set -euo pipefail` defaults. Do not weaken without reason.

## Common Change Recipes

**New ingestion source:**
1. Create `.gitlab/sources/.<name>.yml` extending `.deploy_prod`.
2. Add to relevant aggregate(s) — `.sources_all_incremental.yml`, `.sources_full.yml`, etc.
3. Update `.gitlab-ci.yml` only if a new top-level dispatch route is needed.

**New SQLMesh CI flow:**
1. Edit the dedicated SQLMesh child file, not the root dispatcher.
2. Keep branch-plan, MR-gate, apply-test, and prod flows in **separate** files; the split is intentional.
3. Preserve `pre → sqlmesh job` dependency chain when the job needs `.env_prod`.

**Schema migration / copy:**
- Helper scripts under `.gitlab/service_scripts/`.
- Preserve artifact handoff (e.g. `postgres_get_prod_schemas → postgres_put_test_schemas`) when changing the flow.

**Docker image build:**
- Limit edits to `.gitlab/.docker-build.yml` and root trigger rules unless the build image or registry itself changes.
