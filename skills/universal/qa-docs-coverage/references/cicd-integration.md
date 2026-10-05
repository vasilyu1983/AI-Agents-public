# CI/CD Integration for Documentation

Use CI/CD to stop documentation quality from drifting after the audit. Keep gates cheap, targeted, and aligned to risk.

## Table of Contents

- [Default gate design](#default-gate-design)
- [Recommended toolchain](#recommended-toolchain)
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
  `markdownlint-cli2` (current stable — verify at github.com/DavidAnson/markdownlint-cli2/releases before pinning)
- Prose quality:
  `vale` — install the [official binary](https://github.com/vale-cli/vale/releases) or use the [official GitHub Action](https://github.com/vale-cli/vale-action); `npx vale` does not install this Go CLI. Confirm the release before pinning.
- Local links:
  `check_local_links.py`
- External links:
  `check_external_links.py` or `lychee`; check the [official releases](https://github.com/lycheeverse/lychee/releases) before pinning the Action
- OpenAPI linting:
  `spectral` and `redocly lint`; check each installed version's documented format support before choosing one for OpenAPI, AsyncAPI, or Arazzo
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

The Action major tags below were checked against their maintainers' examples; check releases and the project's runtime files again before adopting them. This workflow assumes the repository has the named `docs/`, `openapi/`, and `asyncapi/` paths and a `.node-version` file.

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
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - uses: actions/setup-node@v7
        with:
          node-version-file: ".node-version"

      - name: Lint markdown
        run: npx markdownlint-cli2 "docs/**/*.md"

      - name: Lint prose
        uses: vale-cli/vale-action@v3
        with:
          files: docs/

      - name: Check local links
        run: python3 skills/universal/qa-docs-coverage/scripts/check_local_links.py docs/

      - name: Check external links
        run: python3 skills/universal/qa-docs-coverage/scripts/check_external_links.py docs/ --allow-host localhost --allow-host 127.0.0.1

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
          python3 skills/universal/qa-docs-coverage/scripts/docs_freshness_report.py \
            --repo-root . \
            --docs-root docs/ \
            --fail-on P1 \
            --out docs-freshness-report.md
          cat docs-freshness-report.md >> "$GITHUB_STEP_SUMMARY"
```

## GitLab CI example

Run the same checks on merge requests and the default branch using a project-owned CI image. Install Vale from a reviewed, pinned release in that image; do not copy the old `curl | tar` example or assume Vale comes from npm. Keep `docs_freshness_report.py --fail-on P1` in the job so a stale critical doc fails the pipeline.

## External link checking notes

Prefer a dedicated external checker over relying only on Markdown tooling.

Use the bundled script when you need:
- host allowlists
- retry logic
- simple CI integration
- repo-local control

Use `lychee` when you want a mature CI-oriented external checker with caching and broad protocol support.

## Freshness gates

Canonical thresholds for this skill (see [freshness-tracking.md](freshness-tracking.md)):
- P1: 30 days
- P2: 60 days
- P3: 90 days

Recommended behavior:
- run `docs_freshness_report.py --fail-on P1` so CI fails only on stale P1 docs; stale P2/P3 are reported but do not block (the script's default matches this — pass `--fail-on none` to disable staleness failures entirely, or a lower priority to tighten the gate)
- add `--fail-on-missing-metadata` separately to fail CI on missing metadata for critical docs

## Anti-patterns

- blocking every PR for every documentation gap
- using one generic docs gate for every repo regardless of risk
- linting syntax without validating contracts, links, or runbook reality
- auto-publishing AI-generated docs directly from CI

## Related resources

- [freshness-tracking.md](freshness-tracking.md)
- [api-docs-validation.md](api-docs-validation.md)
- [runbook-testing.md](runbook-testing.md)
