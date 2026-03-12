# Documentation Freshness Tracking

Track documentation staleness, detect drift from code, and maintain up-to-date docs across your codebase.

---

## Contents

- Overview
- Freshness Metadata Standards
- Automated Staleness Detection
- CI/CD Freshness Gates
- Observability Dashboards
- Integration with Code Changes
- Freshness Review Process
- Monthly Documentation Freshness Review
- Tools and Integrations
- Related Resources

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

## Automated Staleness Detection

Recommended (cross-platform): use `scripts/docs_freshness_report.py` from this skill to generate a Markdown freshness report from `last_verified` frontmatter.

Example:

```bash
python3 frameworks/shared-skills/skills/qa-docs-coverage/scripts/docs_freshness_report.py --docs-root docs/
```

Note: the bash snippets below assume GNU userland (example: `date -d`). On macOS, prefer the Python script or adapt commands accordingly.

### Git-Based Freshness Analysis

Compare doc modification dates against related code:

```bash
#!/bin/bash
# check-doc-freshness.sh

DOC_FILE="$1"
CODE_PATTERN="$2"

# Get last doc update
DOC_DATE=$(git log -1 --format="%ct" -- "$DOC_FILE")

# Get last code update for related files
CODE_DATE=$(git log -1 --format="%ct" -- "$CODE_PATTERN")

# Calculate drift in days
DRIFT=$(( (CODE_DATE - DOC_DATE) / 86400 ))

if [ $DRIFT -gt 30 ]; then
  echo "WARNING: $DOC_FILE is $DRIFT days behind code changes"
  exit 1
fi

echo "OK: $DOC_FILE is fresh (drift: $DRIFT days)"
```

### Usage Example

```bash
# Check if API docs are fresh relative to controllers
./check-doc-freshness.sh docs/api/users.md "src/controllers/users*.ts"
```

### Batch Freshness Report

```bash
#!/bin/bash
# generate-freshness-report.sh

echo "# Documentation Freshness Report"
echo "Generated: $(date -I)"
echo ""
echo "| Document | Last Updated | Code Updated | Drift (days) | Status |"
echo "|----------|--------------|--------------|--------------|--------|"

find docs/ -name "*.md" | while read doc; do
  DOC_DATE=$(git log -1 --format="%cs" -- "$doc" 2>/dev/null || echo "unknown")

  # Extract code_paths from frontmatter if present
  CODE_PATHS=$(grep -A1 "code_paths:" "$doc" | tail -1 | sed 's/- //')

  if [ -n "$CODE_PATHS" ]; then
    CODE_DATE=$(git log -1 --format="%cs" -- "$CODE_PATHS" 2>/dev/null || echo "unknown")

    if [ "$DOC_DATE" != "unknown" ] && [ "$CODE_DATE" != "unknown" ]; then
      DOC_TS=$(date -d "$DOC_DATE" +%s)
      CODE_TS=$(date -d "$CODE_DATE" +%s)
      DRIFT=$(( (CODE_TS - DOC_TS) / 86400 ))

      if [ $DRIFT -gt 60 ]; then
        STATUS="STALE"
      elif [ $DRIFT -gt 30 ]; then
        STATUS="WARNING"
      else
        STATUS="OK"
      fi
    else
      DRIFT="N/A"
      STATUS="UNKNOWN"
    fi
  else
    CODE_DATE="N/A"
    DRIFT="N/A"
    STATUS="NO_TRACKING"
  fi

  echo "| $doc | $DOC_DATE | $CODE_DATE | $DRIFT | $STATUS |"
done
```

---

## CI/CD Freshness Gates

### GitHub Actions

```yaml
name: Documentation Freshness Check

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 9 * * 1'  # Weekly Monday 9 AM

jobs:
  freshness-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git log

      - name: Check P1 Documentation Freshness
        run: |
          STALE_COUNT=0

          # Check each P1 doc
          for doc in docs/api/*.md; do
            DOC_DATE=$(git log -1 --format="%ct" -- "$doc")
            NOW=$(date +%s)
            AGE_DAYS=$(( (NOW - DOC_DATE) / 86400 ))

            if [ $AGE_DAYS -gt 30 ]; then
              echo "::error file=$doc::P1 doc is $AGE_DAYS days old (max 30)"
              STALE_COUNT=$((STALE_COUNT + 1))
            fi
          done

          if [ $STALE_COUNT -gt 0 ]; then
            echo "::error::Found $STALE_COUNT stale P1 documents"
            exit 1
          fi

      - name: Check P2 Documentation Freshness
        run: |
          for doc in docs/internal/*.md docs/events/*.md; do
            DOC_DATE=$(git log -1 --format="%ct" -- "$doc" 2>/dev/null) || continue
            NOW=$(date +%s)
            AGE_DAYS=$(( (NOW - DOC_DATE) / 86400 ))

            if [ $AGE_DAYS -gt 60 ]; then
              echo "::warning file=$doc::P2 doc is $AGE_DAYS days old (recommended max 60)"
            fi
          done

      - name: Generate Freshness Report
        run: |
          ./scripts/generate-freshness-report.sh > freshness-report.md
          cat freshness-report.md >> $GITHUB_STEP_SUMMARY
```

### GitLab CI

```yaml
doc-freshness:
  stage: validate
  script:
    - |
      STALE=0
      for doc in docs/api/*.md; do
        AGE=$(( ($(date +%s) - $(git log -1 --format="%ct" -- "$doc")) / 86400 ))
        if [ $AGE -gt 30 ]; then
          echo "STALE: $doc ($AGE days)"
          STALE=$((STALE + 1))
        fi
      done

      if [ $STALE -gt 0 ]; then
        echo "Found $STALE stale P1 documents"
        exit 1
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

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

### Prometheus Metrics (Example)

```yaml
# prometheus/docs-metrics.yml
groups:
  - name: documentation
    rules:
      - record: docs:freshness:stale_p1_count
        expr: count(docs_last_verified_days > 30 and docs_priority == "P1")

      - record: docs:freshness:stale_p2_count
        expr: count(docs_last_verified_days > 60 and docs_priority == "P2")

      - alert: StaleP1Documentation
        expr: docs:freshness:stale_p1_count > 0
        for: 1d
        labels:
          severity: warning
        annotations:
          summary: "P1 documentation is stale"
          description: "{{ $value }} P1 documents haven't been verified in 30+ days"
```

### Grafana Dashboard Query Examples

```sql
-- Average documentation drift by priority
SELECT
  priority,
  AVG(DATEDIFF(NOW(), last_verified)) as avg_drift_days
FROM docs_metadata
GROUP BY priority;

-- Stale documentation by team
SELECT
  owner,
  COUNT(*) as stale_count
FROM docs_metadata
WHERE DATEDIFF(NOW(), last_verified) >
  CASE priority
    WHEN 'P1' THEN 30
    WHEN 'P2' THEN 60
    ELSE 90
  END
GROUP BY owner
ORDER BY stale_count DESC;
```

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

```yaml
# .github/workflows/doc-reminder.yml
name: Documentation Reminder

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for Related Documentation
        id: check
        run: |
          CHANGED=$(git diff --name-only origin/main HEAD | grep -E '\.(ts|js|py|go|cs)$')
          RELATED_DOCS=""

          for file in $CHANGED; do
            DOCS=$(grep -rl "$file" docs/ 2>/dev/null || true)
            RELATED_DOCS="$RELATED_DOCS $DOCS"
          done

          if [ -n "$RELATED_DOCS" ]; then
            echo "found=true" >> $GITHUB_OUTPUT
            echo "docs<<EOF" >> $GITHUB_OUTPUT
            echo "$RELATED_DOCS" | tr ' ' '\n' | sort -u >> $GITHUB_OUTPUT
            echo "EOF" >> $GITHUB_OUTPUT
          fi

      - name: Comment on PR
        if: steps.check.outputs.found == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const docs = `${{ steps.check.outputs.docs }}`;
            const body = `## Documentation Review Reminder

            The following documentation may be affected by this PR:

            ${docs.split('\n').map(d => `- [ ] ${d}`).join('\n')}

            Please review and update if necessary.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

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
| [markdown-link-check](https://github.com/tcort/markdown-link-check) | Broken link detection | CI/CD |
| [Vale](https://vale.sh/) | Prose linting | Pre-commit |
| [Spectral](https://stoplight.io/spectral) | OpenAPI/AsyncAPI linting | CI/CD |
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
