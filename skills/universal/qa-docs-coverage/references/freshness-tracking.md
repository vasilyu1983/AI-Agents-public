# Documentation Freshness Tracking

## Table of Contents

- [Overview](#overview)
- [Freshness Metadata Standards](#freshness-metadata-standards)
- [Doc-Rot vs. Staleness](#doc-rot-vs-staleness)
- [Automated Staleness Detection](#automated-staleness-detection)
- [CI/CD Freshness Gates](#cicd-freshness-gates)
- [Observability Dashboards](#observability-dashboards)
- [Integration with Code Changes](#integration-with-code-changes)
- [Freshness Review Process](#freshness-review-process)
- [Monthly Documentation Freshness Review](#monthly-documentation-freshness-review)
- [Tools and Integrations](#tools-and-integrations)
- [Related Resources](#related-resources)

Track documentation staleness, detect drift from code, and maintain up-to-date docs across your codebase.

---

## Overview

Documentation freshness is how current your docs are relative to the code they describe. Stale documentation is often worse than no documentation - it misleads developers and creates debugging overhead.

This guide covers:

1. Freshness metadata standards
2. Automated staleness detection
3. Git-based freshness analysis
4. CI/CD freshness gates
5. Observability dashboards

---

## Freshness Metadata Standards

### Required Metadata Fields

Add frontmatter to critical documentation:

```yaml
---
title: User Authentication API
last_verified: 2026-01-15
owner: "@backend-team"
review_cadence: monthly
code_paths:
  - src/auth/**
  - src/middleware/auth.ts
---
```

### Field Definitions

| Field | Required | Description |
| ----- | -------- | ----------- |
| `last_verified` | Yes | Date someone confirmed doc matches code (ISO 8601) |
| `owner` | Yes | Team or individual responsible for updates |
| `review_cadence` | Yes | How often to review (weekly, monthly, quarterly) |
| `code_paths` | Recommended | Glob patterns for related source files |
| `expires` | Optional | Hard deadline for mandatory review |

### Staleness Thresholds

| Priority | Max Age | Action |
| -------- | ------- | ------ |
| P1 (External APIs) | 30 days | Block deploys if stale |
| P2 (Internal APIs) | 60 days | Warning in CI |
| P3 (Config/Utils) | 90 days | Backlog item |

---

## Doc-Rot vs. Staleness

Age-based thresholds (below) catch neglect: nobody touched the doc in N days. They do not catch
rot, where a doc was verified recently but is now wrong because something else moved. Both
matter, but they need different detection methods and neither should be reported as the other.

Rot signals to check independent of `last_verified` age:

- **Referenced identifier vanished**: the doc names a function, CLI flag, endpoint, env var, or
  config key that a `grep`/AST search shows no longer exists in the `code_paths` the doc
  declares.
- **Silent drift in a declared code path**: `git log` on the doc's `code_paths` shows commits
  after the doc's `last_verified` date, but the doc's frontmatter did not move — the reviewer
  either missed it or the doc has no real reviewer.
- **Contradicted example**: the doc's sample request/response, error message, or CLI output no
  longer matches what running the current code actually produces.
- **Support ticket or incident conflict**: a ticket, incident channel message, or postmortem
  explicitly states the documented behavior is wrong. This is the strongest rot signal available
  and should override any freshness badge, however recent.
- **Two truths, no flag**: the doc describes both a deprecated flow and its replacement without
  marking which one is current — readers cannot tell which to follow, which is functionally
  equivalent to being wrong for whichever reader guesses incorrectly.

Rot is usually worse to leave in place than an honestly stale doc, because a `last_verified:
2026-01-15` badge signals false confidence exactly when the content is wrong. When a rot signal
and a fresh `last_verified` date disagree, treat the rot signal as authoritative and re-open the
doc for review regardless of its age.

---

## Automated Staleness Detection

Recommended (cross-platform): use `scripts/docs_freshness_report.py` from this skill to generate a Markdown freshness report from `last_verified` frontmatter.

Example:

```bash
python3 skills/universal/qa-docs-coverage/scripts/docs_freshness_report.py --docs-root docs/
```

`docs_freshness_report.py` already computes both age-based staleness and `code_paths` drift per
document (see the script's `--help`); it supersedes hand-rolled `git log`-based shell scripts for
this purpose, including on macOS where GNU-only flags like `date -d` are unavailable. Reach for a
one-off shell snippet only for an ad hoc check the script doesn't cover.

---

## CI/CD Freshness Gates

Use the shipped `docs_freshness_report.py --fail-on P1` (see
[cicd-integration.md](cicd-integration.md) for a full GitHub Actions and GitLab CI example) rather
than a hand-rolled `git log` loop — the script already applies the P1/P2/P3 thresholds above,
computes `code_paths` drift, and fails CI only at or above the priority you pass to `--fail-on`.

---

## Observability Dashboards

### Metrics to Track

| Metric | Description | Target |
| ------ | ----------- | ------ |
| `docs_coverage_percent` | % of components with docs | > 80% |
| `docs_freshness_p1` | % of P1 docs updated in 30 days | 100% |
| `docs_freshness_p2` | % of P2 docs updated in 60 days | > 90% |
| `docs_drift_days_avg` | Avg days between code and doc updates | < 14 |
| `docs_orphaned_count` | Docs referencing deleted code | 0 |

Wiring these metrics into Prometheus/Grafana or an equivalent dashboard is standard alerting-rule
and SQL work once `docs_freshness_report.py --json-out` gives you the per-doc rows; no
doc-specific query pattern is needed beyond grouping by `priority` and `owner` and applying the
P1/P2/P3 thresholds above.

---

## Integration with Code Changes

### PR Workflow: Detect Related Docs

```bash
#!/bin/bash
# find-related-docs.sh
# Run in PR to identify docs that may need updates

CHANGED_FILES=$(git diff --name-only origin/main HEAD)

echo "## Documentation Review Required"
echo ""

for file in $CHANGED_FILES; do
  # Find docs that reference this file
  RELATED_DOCS=$(grep -l "$file" docs/**/*.md 2>/dev/null)

  if [ -n "$RELATED_DOCS" ]; then
    echo "### $file"
    echo "Related docs to review:"
    echo "$RELATED_DOCS" | while read doc; do
      echo "- [ ] $doc"
    done
    echo ""
  fi
done
```

### Automated Doc Reminder Bot

If automated reminders are useful, compare changed paths with maintained `code_paths` metadata and report candidate docs as an advisory check. Validate file paths before passing them to another tool, and pass workflow data through environment variables or files; do not interpolate PR-controlled names into a `github-script` JavaScript template. [GitHub's action guidance](https://github.com/actions/github-script#passing-inputs-to-the-script) demonstrates the environment-variable boundary. Keep this separate from the blocking P1 freshness gate.

---

## Freshness Review Process

### Monthly Review Checklist

```markdown
## Monthly Documentation Freshness Review

**Date**: [YYYY-MM-DD]
**Reviewer**: [@username]

### P1 Documents (External APIs)

| Document | Last Verified | Action |
|----------|--------------|--------|
| docs/api/users.md | 2026-01-05 | [ ] Reviewed, current |
| docs/api/orders.md | 2025-12-15 | [ ] Needs update |

### P2 Documents (Internal)

| Document | Last Verified | Action |
|----------|--------------|--------|
| docs/events/order-created.md | 2025-11-20 | [ ] Updated |

### Orphaned Documentation

| Document | Issue | Action |
|----------|-------|--------|
| docs/api/legacy-v1.md | API deprecated | [ ] Archive |

### Summary

- Total reviewed: X
- Updated: Y
- Archived: Z
- Next review: [YYYY-MM-DD]
```

---

## Tools and Integrations

### Recommended Tools

| Tool | Purpose | Integration |
| ---- | ------- | ----------- |
| [Lychee](https://github.com/lycheeverse/lychee) (check the release before pinning in CI) | External link detection | CI/CD |
| [Vale](https://vale.sh/) (Go binary, not npm — install via `vale-cli/vale` release or `vale-cli/vale-action`; moved from errata-ai/vale; check releases for the current version) | Prose linting; LSP and Views support | Pre-commit |
| [Spectral](https://stoplight.io/open-source/spectral) | OpenAPI, AsyncAPI, and Arazzo v1 linting | CI/CD |
| [Mintlify](https://mintlify.com/) | AI-powered doc maintenance | Integration |

### Custom Scripts Location

Store freshness scripts in your repo:

```text
scripts/
├── check-doc-freshness.sh
├── generate-freshness-report.sh
├── find-related-docs.sh
└── update-doc-metadata.sh
```

---

## Related Resources

- [CI/CD Integration](cicd-integration.md) - Automated documentation checks
- [Priority Framework](priority-framework.md) - P1/P2/P3 classification
- [Audit Workflows](audit-workflows.md) - Systematic audit processes
- [Coverage Report Template](../assets/coverage-report-template.md) - Report structure
