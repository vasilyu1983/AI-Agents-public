# CI/CD Integration for Documentation

This resource provides patterns for integrating documentation checks into CI/CD pipelines and PR workflows.

**Updated January 2026**: Added Spectral API linting, Swagger Coverage integration, AI-assisted doc generation triggers, and freshness tracking.

---

## Contents

- Overview
- PR Template Documentation Checklist
- CI/CD Coverage Gates
- Pre-Commit Hooks
- Documentation Linters
- Automated Documentation Coverage Reports
- Summary
- Recommendations
- Automated Reminders
- Anti-Patterns to Avoid
- Best Practices
- API Contract Validation (January 2026)
- API Coverage Tools
- Freshness Tracking in CI
- AI-Assisted Documentation (Optional)
- Complete CI/CD Pipeline Example
- Related Resources

## Overview

Automated documentation checks ensure that documentation stays current and new components are documented before merging. This guide covers:

1. PR template additions
2. CI/CD coverage gates
3. Pre-commit hooks
4. Documentation linters
5. API contract validation (Spectral, AsyncAPI CLI)
6. Coverage tools (Swagger Coverage, OpenAPI Coverage)
7. Freshness tracking integration
8. Automated reminders

---

## PR Template Documentation Checklist

### GitHub Pull Request Template

Add to `.github/pull_request_template.md`:

```markdown
## Documentation Checklist

Please ensure documentation is updated for this PR:

- [ ] **New APIs**: Added to OpenAPI spec or API reference
- [ ] **New events/messages**: Added to event catalog with schema
- [ ] **Configuration changes**: Updated configuration reference
- [ ] **Breaking changes**: Noted in CHANGELOG.md with migration guide
- [ ] **Architecture changes**: ADR created if introducing new pattern
- [ ] **Database changes**: ER diagram updated, migration documented
- [ ] **External integrations**: Integration guide updated

**Documentation Location**: [Link to updated docs]

**N/A**: Check here if no documentation changes needed [ ]
```

### GitLab Merge Request Template

Add to `.gitlab/merge_request_assets/default.md`:

```markdown
## Documentation Changes

- [ ] API documentation updated
- [ ] Event schemas documented
- [ ] Configuration changes documented
- [ ] Breaking changes in CHANGELOG
- [ ] ADR created (if applicable)

**Docs Link**: [Link]
```

### BitBucket Pull Request Template

Add to `pull_request_template.md`:

```markdown
## Documentation

- [ ] Updated relevant documentation
- [ ] Added examples if introducing new feature
- [ ] Updated CHANGELOG for user-facing changes

**Note**: If no documentation needed, explain why below.
```

---

## CI/CD Coverage Gates

### GitHub Actions

Create `.github/workflows/docs-check.yml`:

```yaml
name: Documentation Coverage Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for comparison

      - name: Check API Documentation Coverage
        run: |
          # Count total controllers
          CONTROLLERS=$(find . -name "*Controller.cs" | wc -l)

          # Count documented endpoints in OpenAPI
          if [ -f "openapi/spec.yaml" ]; then
            DOCUMENTED=$(yq '.paths | keys | length' openapi/spec.yaml)
          else
            DOCUMENTED=0
          fi

          echo "Total Controllers: $CONTROLLERS"
          echo "Documented Endpoints: $DOCUMENTED"

          # Warning if significant gap
          if [ $CONTROLLERS -gt $(($DOCUMENTED + 5)) ]; then
            echo "::warning::Some APIs may be undocumented"
          fi

      - name: Check for Undocumented Public APIs
        run: |
          # Find public API controllers
          PUBLIC_APIS=$(rg "public class.*Controller" --type cs --files-with-matches)

          # Check if each has corresponding doc
          MISSING=0
          for file in $PUBLIC_APIS; do
            CONTROLLER=$(basename $file .cs)
            if ! grep -q "$CONTROLLER" docs/api/*.md 2>/dev/null; then
              echo "::warning file=$file::$CONTROLLER may need documentation"
              MISSING=$((MISSING + 1))
            fi
          done

          if [ $MISSING -gt 0 ]; then
            echo "::warning::Found $MISSING potentially undocumented controllers"
          fi

      - name: Check CHANGELOG Updated
        run: |
          # Check if CHANGELOG.md was updated in this PR
          if git diff --name-only origin/main HEAD | grep -q "CHANGELOG.md"; then
            echo "CHANGELOG.md updated [check]"
          else
            # Check if this is a feature/fix branch
            if [[ "$GITHUB_HEAD_REF" =~ ^(feature|fix)/ ]]; then
              echo "::warning::Consider updating CHANGELOG.md for user-facing changes"
            fi
          fi

      - name: Check for Broken Links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          folder-path: 'docs'
          config-file: '.github/markdown-link-check-config.json'

      - name: Lint Markdown Files
        uses: avto-dev/markdown-lint@v1
        with:
          args: './docs'
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
docs-check:
  stage: test
  script:
    # Check API coverage
    - CONTROLLERS=$(find . -name "*Controller.cs" | wc -l)
    - DOCUMENTED=$(grep -r "## Endpoints" docs/api/ | wc -l)
    - echo "Controllers: $CONTROLLERS, Documented: $DOCUMENTED"
    - |
      if [ $CONTROLLERS -gt $(($DOCUMENTED + 5)) ]; then
        echo "Warning: Potential documentation gap"
      fi

    # Check for broken links
    - npm install -g markdown-link-check
    - find docs/ -name "*.md" -exec markdown-link-check {} \;

  only:
    - merge_requests
    - main
```

### Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    stages {
        stage('Documentation Check') {
            steps {
                script {
                    // Count controllers
                    def controllers = sh(
                        script: "find . -name '*Controller.cs' | wc -l",
                        returnStdout: true
                    ).trim()

                    // Count documented endpoints
                    def documented = sh(
                        script: "grep -r '## Endpoints' docs/api/ | wc -l",
                        returnStdout: true
                    ).trim()

                    echo "Controllers: ${controllers}, Documented: ${documented}"

                    // Warning if gap exists
                    if (controllers.toInteger() > documented.toInteger() + 5) {
                        currentBuild.result = 'UNSTABLE'
                        error "Documentation coverage warning"
                    }
                }
            }
        }

        stage('Markdown Lint') {
            steps {
                sh 'npx markdownlint docs/'
            }
        }
    }
}
```

---

## Pre-Commit Hooks

### Git Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check if CHANGELOG.md exists and branch is feature/fix
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" =~ ^(feature|fix)/ ]]; then
    # Check if any staged files are code changes
    CODE_CHANGES=$(git diff --cached --name-only | grep -E '\.(cs|ts|py|go|java)$')

    if [ -n "$CODE_CHANGES" ]; then
        # Check if CHANGELOG.md is staged
        if ! git diff --cached --name-only | grep -q "CHANGELOG.md"; then
            echo "WARNING: Consider updating CHANGELOG.md for this feature/fix"
            echo "Continue anyway? (y/n)"
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
fi

# Check for TODO comments in staged files
TODO_COUNT=$(git diff --cached | grep -c "TODO:")
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "Found $TODO_COUNT TODO comments in staged changes"
    echo "Consider documenting or creating tickets for TODOs"
fi

exit 0
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Husky Pre-Commit Hook (Node.js)

Install Husky:

```bash
npm install --save-dev husky
npx husky install
```

Create `.husky/pre-commit`:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Check if package.json changed without updating README
if git diff --cached --name-only | grep -q "package.json"; then
    if ! git diff --cached --name-only | grep -q "README.md"; then
        echo "[WARNING]  package.json changed, consider updating README.md"
    fi
fi

# Lint markdown files
npx markdownlint 'docs/**/*.md'
```

---

## Documentation Linters

### Markdown Linting

Install markdownlint:

```bash
npm install -g markdownlint-cli
```

Create `.markdownlint.json`:

```json
{
  "default": true,
  "MD013": false,
  "MD033": false,
  "MD041": false,
  "line-length": false,
  "no-inline-html": false,
  "first-line-h1": false
}
```

Run linter:

```bash
markdownlint 'docs/**/*.md'
```

### Vale Prose Linter

Install Vale:

```bash
brew install vale  # macOS
```

Create `.vale.ini`:

```ini
StylesPath = .vale/styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = write-good, proselint
```

Run linter:

```bash
vale docs/
```

### Link Checking

Install markdown-link-check:

```bash
npm install -g markdown-link-check
```

Create `.github/markdown-link-check-config.json`:

```json
{
  "ignorePatterns": [
    {
      "pattern": "^http://localhost"
    }
  ],
  "timeout": "20s",
  "retryOn429": true,
  "retryCount": 3,
  "fallbackRetryDelay": "30s"
}
```

Run link check:

```bash
find docs/ -name "*.md" -exec markdown-link-check {} \;
```

---

## Automated Documentation Coverage Reports

### Coverage Report Script

Create `scripts/check-docs-coverage.sh`:

```bash
#!/bin/bash

# Configuration
DOCS_DIR="docs"
SRC_DIR="src"
REPORT_FILE="docs-coverage-report.md"

# Count components
CONTROLLERS=$(find $SRC_DIR -name "*Controller.cs" | wc -l)
SERVICES=$(find $SRC_DIR -name "*Service.cs" | wc -l)
DBCONTEXTS=$(find $SRC_DIR -name "*DbContext.cs" | wc -l)

# Count documentation
API_DOCS=$(find $DOCS_DIR/api -name "*.md" | wc -l)
SERVICE_DOCS=$(find $DOCS_DIR/services -name "*.md" | wc -l)
DATA_DOCS=$(find $DOCS_DIR/data -name "*.md" | wc -l)

# Calculate coverage
API_COVERAGE=$(awk "BEGIN {printf \"%.0f\", ($API_DOCS/$CONTROLLERS)*100}")
SERVICE_COVERAGE=$(awk "BEGIN {printf \"%.0f\", ($SERVICE_DOCS/$SERVICES)*100}")
DATA_COVERAGE=$(awk "BEGIN {printf \"%.0f\", ($DATA_DOCS/$DBCONTEXTS)*100}")

# Generate report
cat > $REPORT_FILE << EOF
# Documentation Coverage Report

Generated: $(date +"%Y-%m-%d %H:%M:%S")

## Summary

| Category | Components | Documented | Coverage |
|----------|------------|------------|----------|
| APIs | $CONTROLLERS | $API_DOCS | $API_COVERAGE% |
| Services | $SERVICES | $SERVICE_DOCS | $SERVICE_COVERAGE% |
| Data | $DBCONTEXTS | $DATA_DOCS | $DATA_COVERAGE% |

## Recommendations

$(if [ $API_COVERAGE -lt 80 ]; then echo "- Improve API documentation coverage (currently $API_COVERAGE%)"; fi)
$(if [ $SERVICE_COVERAGE -lt 60 ]; then echo "- Improve service documentation coverage (currently $SERVICE_COVERAGE%)"; fi)
$(if [ $DATA_COVERAGE -lt 60 ]; then echo "- Improve data documentation coverage (currently $DATA_COVERAGE%)"; fi)
EOF

echo "Report generated: $REPORT_FILE"
cat $REPORT_FILE
```

Make executable:

```bash
chmod +x scripts/check-docs-coverage.sh
```

Run in CI:

```yaml
- name: Generate Coverage Report
  run: ./scripts/check-docs-coverage.sh

- name: Upload Coverage Report
  uses: actions/upload-artifact@v3
  with:
    name: docs-coverage-report
    path: docs-coverage-report.md
```

---

## Automated Reminders

### GitHub Issue Templates

Create `.github/ISSUE_TEMPLATE/documentation.md`:

```markdown
---
name: Documentation Request
about: Request documentation for a component
title: '[DOCS] '
labels: 'documentation'
assignees: ''
---

## Component to Document

**Type**: API / Service / Data / Event / Config

**Location**: `path/to/component`

**Priority**: P1 / P2 / P3

## Documentation Needed

- [ ] Purpose and responsibilities
- [ ] API reference (if applicable)
- [ ] Configuration options (if applicable)
- [ ] Examples
- [ ] Integration guide

## Context

[Why is this documentation needed?]
```

### Slack Reminders (via GitHub Actions)

Create `.github/workflows/weekly-docs-reminder.yml`:

```yaml
name: Weekly Documentation Reminder

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - name: Send Slack Reminder
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "[DOCS] Weekly Documentation Reminder",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "[DOCS] *Weekly Documentation Reminder*\n\nPlease review documentation backlog and update coverage:\n- Priority 1 gaps: <link to backlog>\n- Documentation coverage: <link to report>"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Anti-Patterns to Avoid

### 1. Blocking Merges for Non-Critical Docs

Do NOT block PRs for P3 (nice to have) documentation gaps.

```yaml
# Bad: Fails build for any missing docs
- name: Check Docs
  run: |
    if [ $UNDOCUMENTED -gt 0 ]; then
      exit 1  # Blocks all PRs
    fi

# Good: Warning for P3, error for P1
- name: Check Docs
  run: |
    if [ $P1_UNDOCUMENTED -gt 0 ]; then
      exit 1  # Blocks PR
    elif [ $P3_UNDOCUMENTED -gt 0 ]; then
      echo "::warning::Nice-to-have docs missing"
    fi
```

### 2. Overly Strict Markdown Linting

Do NOT enforce pedantic markdown rules that slow down documentation.

```json
// Bad: Too many rules
{
  "MD001": true,
  "MD003": true,
  "MD004": true,
  "MD005": true,
  ...50 more rules...
}

// Good: Focus on critical rules
{
  "default": true,
  "MD013": false,  // Line length
  "MD033": false,  // Inline HTML (useful for tables)
  "MD041": false   // First line h1
}
```

### 3. Ignoring Documentation Updates

Do NOT skip documentation checks for "urgent" fixes.

```yaml
# Bad: Allows skipping checks
if: github.event.pull_request.labels.*.name != 'skip-docs-check'

# Good: Always check, but only warn for hotfixes
if: github.event.pull_request.labels.*.name == 'hotfix'
  run: echo "::warning::Hotfix - docs check skipped, follow up required"
```

---

## Best Practices

1. **Start with warnings, not errors**: Introduce checks gradually
2. **Make checks fast**: Documentation checks should add <30 seconds to CI
3. **Provide clear error messages**: Tell developers exactly what's missing
4. **Link to templates**: Include links to documentation templates in error messages
5. **Track coverage trends**: Generate reports over time to show improvement
6. **Celebrate improvements**: Highlight teams/PRs that improve documentation coverage

---

## API Contract Validation (January 2026)

### Spectral for OpenAPI/AsyncAPI Linting

Install and configure Spectral for API documentation standards:

```bash
npm install -g @stoplight/spectral-cli
```

Create `.spectral.yaml`:

```yaml
extends: ["spectral:oas", "spectral:asyncapi"]

rules:
  # Require descriptions for all operations
  operation-description: error

  # Require examples for request/response bodies
  oas3-valid-media-example: error

  # Require tags for organization
  operation-tag-defined: error

  # Custom: Require error response documentation
  operation-4xx-response:
    description: "Operations must document 4xx error responses"
    given: "$.paths[*][*]"
    then:
      field: "responses"
      function: schema
      functionOptions:
        schema:
          anyOf:
            - required: ["400"]
            - required: ["401"]
            - required: ["403"]
            - required: ["404"]
```

GitHub Actions integration:

```yaml
- name: Lint OpenAPI Spec
  run: |
    npx spectral lint openapi/spec.yaml --fail-severity error

- name: Lint AsyncAPI Spec
  run: |
    npx spectral lint asyncapi/events.yaml --fail-severity error
```

### AsyncAPI CLI Validation

```bash
npm install -g @asyncapi/cli
```

```yaml
- name: Validate AsyncAPI
  run: |
    asyncapi validate asyncapi/events.yaml
    asyncapi diff asyncapi/events.yaml asyncapi/events-previous.yaml --fail-on-breaking
```

---

## API Coverage Tools

### Swagger Coverage

Track which endpoints are documented vs tested:

```bash
# Install
npm install -g swagger-coverage-commandline

# Generate coverage report
swagger-coverage-commandline -s openapi/spec.yaml -i postman/newman-results.json
```

GitHub Actions integration:

```yaml
- name: Run API Tests
  run: newman run postman/collection.json --reporters cli,json --reporter-json-export newman-results.json

- name: Generate API Coverage Report
  run: |
    swagger-coverage-commandline \
      -s openapi/spec.yaml \
      -i newman-results.json \
      --output coverage-report

- name: Upload Coverage Report
  uses: actions/upload-artifact@v4
  with:
    name: api-coverage-report
    path: coverage-report/
```

### OpenAPI Coverage (open-api-coverage)

```bash
npm install open-api-coverage
```

```javascript
// coverage-check.js
const { CoverageCollector } = require('open-api-coverage');

const collector = new CoverageCollector({
  specPath: './openapi/spec.yaml'
});

// After running tests
const report = collector.getReport();
console.log(`API Coverage: ${report.coveragePercent}%`);

if (report.coveragePercent < 80) {
  console.error('API coverage below 80%');
  process.exit(1);
}
```

---

## Freshness Tracking in CI

### Check Documentation Age

```yaml
- name: Check P1 Doc Freshness
  run: |
    STALE=0
    for doc in docs/api/*.md; do
      AGE=$(( ($(date +%s) - $(git log -1 --format="%ct" -- "$doc")) / 86400 ))
      if [ $AGE -gt 30 ]; then
        echo "::error file=$doc::P1 doc is $AGE days stale (max 30)"
        STALE=$((STALE + 1))
      fi
    done
    [ $STALE -gt 0 ] && exit 1 || exit 0
```

See [freshness-tracking.md](freshness-tracking.md) for complete freshness tracking patterns.

---

## AI-Assisted Documentation (Optional)

### Trigger Doc Generation on Code Changes

```yaml
- name: Check for Undocumented Endpoints
  id: check-undoc
  run: |
    # Find new controllers without corresponding docs
    NEW_CONTROLLERS=$(git diff --name-only origin/main HEAD | grep -E 'Controller\.(ts|cs|py)$')
    UNDOC=""
    for ctrl in $NEW_CONTROLLERS; do
      DOC_NAME=$(basename "$ctrl" | sed 's/Controller.*//')
      if ! ls docs/api/*${DOC_NAME}* 2>/dev/null; then
        UNDOC="$UNDOC $ctrl"
      fi
    done
    echo "undocumented=$UNDOC" >> $GITHUB_OUTPUT

- name: Request AI Doc Draft
  if: steps.check-undoc.outputs.undocumented != ''
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `## Documentation Required

        New endpoints detected without documentation:
        ${{ steps.check-undoc.outputs.undocumented }}

        Consider using AI-assisted doc generation (Mintlify, DocuWriter.ai) and submit for review.`
      });
```

---

## Complete CI/CD Pipeline Example

```yaml
name: Documentation Quality Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  docs-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Markdown quality
      - name: Lint Markdown
        uses: avto-dev/markdown-lint@v1
        with:
          args: './docs'

      - name: Check Links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          folder-path: 'docs'

      # API contract validation
      - name: Lint OpenAPI
        run: npx @stoplight/spectral-cli lint openapi/spec.yaml --fail-severity error

      - name: Lint AsyncAPI
        run: npx @asyncapi/cli validate asyncapi/events.yaml

      # Coverage analysis
      - name: Check Documentation Coverage
        run: ./scripts/check-docs-coverage.sh

      # Freshness check (P1 only)
      - name: Check P1 Freshness
        run: |
          for doc in docs/api/*.md; do
            AGE=$(( ($(date +%s) - $(git log -1 --format="%ct" -- "$doc")) / 86400 ))
            [ $AGE -gt 30 ] && echo "::error::$doc is $AGE days stale" && exit 1
          done

      # Generate report
      - name: Generate Coverage Report
        run: ./scripts/generate-coverage-report.sh > $GITHUB_STEP_SUMMARY
```

---

## Related Resources

- [Audit Workflows](audit-workflows.md) - How to conduct documentation audits
- [Priority Framework](priority-framework.md) - How to prioritize documentation
- [Discovery Patterns](discovery-patterns.md) - How to find undocumented components
- [Freshness Tracking](freshness-tracking.md) - Documentation staleness detection
