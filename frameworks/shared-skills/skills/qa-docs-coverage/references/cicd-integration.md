# CI/CD Integration for Documentation

Use CI/CD to stop documentation quality from drifting after the audit. Keep gates cheap, targeted, and aligned to risk.

## Table of Contents

- [Default gate design](#default-gate-design)
- [Recommended toolchain](#recommended-2026-toolchain)
- [Pull request checklist](#pull-request-checklist)
- [Documentation](#documentation)
- [GitHub Actions example](#github-actions-example)
- [GitLab CI example](#gitlab-ci-example)
- [External link checking notes](#external-link-checking-notes)
- [Freshness gates](#freshness-gates)
- [Anti-patterns](#anti-patterns)
- [Related resources](#related-resources)

## Default gate design

Block on:
- broken local links in critical docs
- missing or invalid P1 documentation
- stale P1 docs with no owner
- API contract lint failures
- breaking contract changes without matching documentation updates

Warn on:
- P2 and P3 coverage gaps
- stale non-critical docs
- duplicate drafts or cleanup debt

## Recommended toolchain

- Markdown structure:
  `markdownlint-cli2` (v0.23.0+ as of July 2026)
- Prose quality:
  `vale` (project moved from errata-ai/vale to vale-cli/vale; supports LSP, custom Views for YAML/JSON/TOML, 12 rule types — confirm current version at github.com/vale-cli/vale/releases)
- Local links:
  `check_local_links.py`
- External links:
  `check_external_links.py` or `lychee` (v0.24.x current mid-2026, in GitHub Action)
- OpenAPI linting:
  `spectral` (supports OpenAPI, AsyncAPI, Arazzo v1) and `redocly lint` (v2.36.0+, supports OpenAPI, AsyncAPI, Arazzo)
- AsyncAPI validation:
  `asyncapi validate` and `spectral`
- Breaking-change detection:
  `oasdiff` (replaces Optic, whose repo was archived 2026-01-12)
- Docstring coverage (Python):
  `interrogate` or `docstr-coverage` — gate on presence, spot-check a sample for quality (see [api-docs-validation.md](api-docs-validation.md))
- Freshness:
  `docs_freshness_report.py`

## Pull request checklist

Add a lightweight documentation section to the PR template:

```markdown
## Documentation

- [ ] Public API or webhook changes are reflected in the contract/docs
- [ ] Event or job changes are reflected in internal docs/runbooks
- [ ] Breaking changes include migration guidance
- [ ] Critical docs updated or explicitly marked N/A with reason
```

## GitHub Actions example

```yaml
name: docs-quality

on:
  pull_request:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: actions/setup-node@v4
        with:
          node-version: "22"

      - name: Lint markdown
        run: npx markdownlint-cli2 "docs/**/*.md"

      - name: Lint prose
        run: npx vale docs

      - name: Check local links
        run: python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/check_local_links.py docs/

      - name: Check external links
        run: python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/check_external_links.py docs/ --allow-host localhost --allow-host 127.0.0.1

      - name: Lint OpenAPI
        run: npx @stoplight/spectral-cli lint openapi/openapi.yaml && npx @redocly/cli lint openapi/openapi.yaml

      - name: Validate AsyncAPI
        run: npx @asyncapi/cli validate asyncapi/asyncapi.yaml

      - name: Detect breaking API changes
        run: |
          docker run --rm -v "$PWD:/work" -w /work ghcr.io/oasdiff/oasdiff:latest \
            breaking openapi/base.yaml openapi/openapi.yaml

      - name: Freshness report
        run: |
          python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/docs_freshness_report.py \
            --repo-root . \
            --docs-root docs/ \
            --out docs-freshness-report.md
          cat docs-freshness-report.md >> "$GITHUB_STEP_SUMMARY"
```

## GitLab CI example

```yaml
docs_quality:
  stage: test
  image: node:22
  script:
    - apt-get update && apt-get install -y python3
    - npx markdownlint-cli2 "docs/**/*.md"
    - npx vale docs
    - python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/check_local_links.py docs/
    - python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/check_external_links.py docs/
    - npx @stoplight/spectral-cli lint openapi/openapi.yaml
    - npx @redocly/cli lint openapi/openapi.yaml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## External link checking notes

Prefer a dedicated external checker over relying only on Markdown tooling.

Use the bundled script when you need:
- host allowlists
- retry logic
- simple CI integration
- repo-local control

Use `lychee` when you want a mature CI-oriented external checker with caching and broad protocol support.

## Freshness gates

Typical thresholds:
- P1: 30 days
- P2: 60 days
- P3: 90 days

Recommended behavior:
- fail CI on stale P1 docs
- warn on stale P2 and P3 docs
- fail CI on missing metadata for critical docs

## Anti-patterns

- blocking every PR for every documentation gap
- using one generic docs gate for every repo regardless of risk
- linting syntax without validating contracts, links, or runbook reality
- auto-publishing AI-generated docs directly from CI

## Related resources

- [freshness-tracking.md](freshness-tracking.md)
- [api-docs-validation.md](api-docs-validation.md)
- [runbook-testing.md](runbook-testing.md)
