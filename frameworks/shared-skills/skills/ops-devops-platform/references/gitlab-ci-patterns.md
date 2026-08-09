# GitLab CI Patterns

Reusable patterns for a medium-sized GitLab pipeline. All names and values are
fictional. Adapt stages, images, runners, and environments to the target
repository.

## Contents

- [Keep the root pipeline readable](#keep-the-root-pipeline-readable)
- [Rules for branch and merge-request pipelines](#rules-for-branch-and-merge-request-pipelines)
- [Workflow-level duplicate prevention](#workflow-level-duplicate-prevention)
- [Pass generated values with dotenv artifacts](#pass-generated-values-with-dotenv-artifacts)
- [Matrix jobs](#matrix-jobs)
- [Child pipeline for an independent component](#child-pipeline-for-an-independent-component)
- [SQLMesh validation job](#sqlmesh-validation-job)
- [Caching and artifacts](#caching-and-artifacts)
- [Deployment controls](#deployment-controls)
- [Validation checklist](#validation-checklist)
- [Common mistakes](#common-mistakes)

## Keep the root pipeline readable

Use the root file for global defaults, stages, and includes. Put cohesive job
families in descriptively named include files.

```yaml
# .gitlab-ci.yml
stages: [validate, test, package, deploy]

default:
  interruptible: true
  retry:
    max: 1
    when: [runner_system_failure, stuck_or_timeout_failure]

include:
  - local: ci/includes/quality.yml
  - local: ci/includes/package.yml
  - local: ci/includes/deploy.yml
```

Avoid turning the root file into a directory of thin trigger jobs. A child
pipeline is useful when a component needs an independent graph, permissions,
or lifecycle—not merely to shorten a YAML file.

## Rules for branch and merge-request pipelines

Use `CI_PIPELINE_SOURCE` to distinguish pipeline types. Do not assume
`CI_COMMIT_BRANCH` exists in a merge-request pipeline.

```yaml
lint:
  stage: validate
  script: ./scripts/lint.sh
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

For the merge-request source branch, use
`CI_MERGE_REQUEST_SOURCE_BRANCH_NAME` inside a merge-request rule.

## Workflow-level duplicate prevention

Prevent a push pipeline and a merge-request pipeline from running for the same
commit when only one is useful.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS'
      when: never
    - if: '$CI_COMMIT_BRANCH'
```

Test workflow changes against pushes, merge requests, tags, schedules, and
manual runs before adoption.

## Pass generated values with dotenv artifacts

Use a dotenv report for non-secret values produced by one job and consumed by
another.

```yaml
prepare-version:
  stage: validate
  script:
    - VERSION="0.0.${CI_PIPELINE_IID}"
    - printf 'BUILD_VERSION=%s\n' "$VERSION" > build.env
  artifacts:
    reports:
      dotenv: build.env

package:
  stage: package
  needs: [prepare-version]
  script:
    - ./scripts/package.sh "$BUILD_VERSION"
```

Dotenv artifacts are not a secret store. Keep credentials in protected,
masked CI variables or an approved secret manager.

## Matrix jobs

Use a matrix when the job body is identical and only a small set of parameters
changes.

```yaml
unit-test:
  stage: test
  parallel:
    matrix:
      - RUNTIME: ['3.11', '3.12']
        DATABASE: [postgres]
  image: "python:${RUNTIME}-slim"
  services:
    - name: postgres:17-alpine
      alias: db
  script:
    - ./scripts/test.sh "$DATABASE"
```

Keep the matrix bounded. If combinations need different scripts or permissions,
use separate jobs.

## Child pipeline for an independent component

```yaml
component-pipeline:
  stage: test
  trigger:
    include:
      - local: components/reporting/ci.yml
    strategy: depend
  rules:
    - changes:
        - components/reporting/**/*
```

Choose whether variables are forwarded explicitly. Review inherited variables
before allowing a child pipeline to reach a protected environment.

## SQLMesh validation job

Keep validation and production application as separate jobs with separate
permissions.

```yaml
sqlmesh-validate:
  image: python:3.12-slim
  stage: test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  before_script:
    - pip install -r requirements.lock
  script:
    - sqlmesh format --check
    - sqlmesh test --gateway ci
    - sqlmesh plan "mr_${CI_MERGE_REQUEST_IID}" --gateway ci --no-prompts
```

The validation identity should have access only to disposable CI data. A
protected deployment job should review and apply the production plan.

## Caching and artifacts

- Cache downloaded dependencies that can be reconstructed.
- Use artifacts for outputs a downstream job must consume.
- Key caches with the relevant lockfile checksum.
- Set explicit artifact retention.
- Never cache credentials, local environment files, or production exports.

```yaml
cache:
  key:
    files: [requirements.lock]
  paths: [.cache/pip]
  policy: pull-push
```

## Deployment controls

```yaml
deploy-production:
  stage: deploy
  environment:
    name: production
  resource_group: production
  script: ./scripts/deploy.sh
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
  allow_failure: false
```

Protect the environment and required variables in GitLab. Use `resource_group`
to serialize deployments that must not overlap.

## Validation checklist

1. Every local include path exists.
2. Stage names are declared in the final composed pipeline.
3. `rules` cover the intended pipeline sources without duplicates.
4. `needs` matches actual artifact and ordering dependencies.
5. Secrets are masked, protected, and absent from artifacts and logs.
6. Merge-request jobs do not depend on branch-only variables.
7. Child pipelines receive only the variables they need.
8. Production jobs are protected, serialized, and independently authorized.
9. Dependency versions and container images are pinned according to policy.
10. CI Lint or the pipeline editor validates the merged configuration.

## Common mistakes

- Using `only`/`except` and `rules` inconsistently across related jobs.
- Treating a dotenv artifact as confidential storage.
- Rebuilding the same dependency cache in every job.
- Applying a production data plan in a merge-request validation job.
- Forwarding all parent variables to an untrusted child pipeline.
- Adding `allow_failure: true` to a required quality gate.
- Copying organization-specific hosts, runner tags, project IDs, or pipeline
  filenames into a reusable public example.
