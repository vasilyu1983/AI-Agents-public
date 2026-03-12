# Automated Quality Gates for Pull Requests

Enforce code quality automatically in PRs using CI/CD pipelines and quality gates.

## Contents

- CI/CD Quality Gate Checklist
- GitHub Actions Quality Gates
- GitLab CI Quality Gates
- Pre-commit Hooks (Local Quality Gates)
- Quality Metrics & Thresholds
- PR Status Checks (GitHub)
- Automated PR Comments
- Skipping Quality Gates (Emergency Hotfixes)
- Quality Gate Exemptions
- Monitoring Quality Trends
- Related Resources

---

## CI/CD Quality Gate Checklist

### Essential Gates

**Must-have for all projects**:

- [ ] All tests pass (unit, integration, e2e)
- [ ] Code coverage > threshold (e.g., 80%)
- [ ] No linter errors
- [ ] No security vulnerabilities (SAST scan)
- [ ] No secrets in code
- [ ] PR size < 1000 lines (warning)

### Advanced Gates

**Recommended for production applications**:

- [ ] Performance benchmarks pass
- [ ] Bundle size < threshold
- [ ] Accessibility (a11y) checks pass
- [ ] API compatibility check (no breaking changes)
- [ ] Dependency license check
- [ ] Code complexity metrics (cyclomatic complexity)
- [ ] Documentation coverage
- [ ] Docker image scan (if applicable)

---

## GitHub Actions Quality Gates

### Merge Queue Support (Required for GitHub Merge Queue)

**IMPORTANT**: If your repository uses GitHub merge queue, you MUST include the `merge_group` event trigger. Without this, status checks won't run when PRs are added to the merge queue, causing merges to fail.

```yaml
on:
  pull_request:
    branches: [main, develop]
  merge_group:  # Required for merge queue!
    branches: [main]
```

**Third-party CI providers**: Update your CI configuration to run when branches matching `gh-readonly-queue/{base_branch}/*` are pushed. These are temporary branches created by the merge queue.

### Merge Queue Configuration Options

When configuring merge queue in **Settings -> Branches -> Branch protection**:

| Setting | Description | Recommendation |
| ------- | ----------- | -------------- |
| Build concurrency | Max parallel CI builds (1-100) | 5-10 for balanced throughput |
| Minimum group size | PRs to batch before testing | 2-3 for busy repos |
| Maximum group size | Max PRs per batch | 5-10 to limit blast radius |
| Wait timeout | Max time waiting for CI | 60-120 minutes |
| Only merge non-failing | Skip flaky test failures | Enable if tests are flaky |

**Best practices for merge queues**:

- Keep CI fast (< 15 min) to maximize throughput
- Fix flaky tests - they cause unnecessary queue delays
- Use caching and parallelism to reduce CI time
- Monitor time-in-queue and failure rates
- Consider batching PRs to reduce redundant CI runs

See [GitHub merge queue documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) for full configuration options.

---

### Complete PR Checks Workflow

**File**: `.github/workflows/pr-checks.yml`

```yaml
name: PR Quality Gates

on:
  pull_request:
    branches: [main, develop]
  merge_group:  # Support merge queue
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # For accurate coverage diffs

      # Setup
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      # Tests
      - name: Run unit tests
        run: npm test -- --coverage

      - name: Check coverage threshold
        run: |
          COVERAGE=$(npm test -- --coverage --silent | grep -oP '\d+(?=%)')
          if [ "$COVERAGE" -lt 80 ]; then
            echo "[FAIL] Coverage $COVERAGE% below 80% threshold"
            exit 1
          fi
          echo "[OK] Coverage $COVERAGE% meets threshold"

      - name: Run integration tests
        run: npm run test:integration

      - name: Run E2E tests
        run: npm run test:e2e

      # Code Quality
      - name: Lint code
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Check code formatting
        run: npm run format:check

      # Security
      - name: Security scan (Snyk)
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}

      # Performance
      - name: Run performance benchmarks
        run: npm run bench

      - name: Check bundle size
        uses: andresz1/size-limit-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      # PR Size Check
      - name: Check PR size
        uses: CodeSeoul/pr-size-labeler@v1
        with:
          maximum: 1000
          labels: |
            {
              "0": "size/XS",
              "100": "size/S",
              "300": "size/M",
              "500": "size/L",
              "1000": "size/XL"
            }

      # Upload Results
      - name: Upload coverage reports
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

      - name: Comment PR with results
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '[OK] All quality gates passed!'
            })
```

---

## GitLab CI Quality Gates

### Complete MR Checks Pipeline

**File**: `.gitlab-ci.yml`

```yaml
stages:
  - test
  - quality
  - security

variables:
  COVERAGE_THRESHOLD: "80"

# Tests
test:unit:
  stage: test
  image: node:20-alpine
  script:
    - npm ci
    - npm test -- --coverage
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

test:integration:
  stage: test
  image: node:20-alpine
  services:
    - postgres:15
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
  script:
    - npm ci
    - npm run test:integration
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Code Quality
code-quality:
  stage: quality
  image: docker:stable
  services:
    - docker:stable-dind
  script:
    - docker run --rm
        -v $(pwd):/code
        codeclimate/codeclimate analyze
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

lint:
  stage: quality
  image: node:20-alpine
  script:
    - npm ci
    - npm run lint
    - npm run format:check
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Security
security:sast:
  stage: security
  image: returntocorp/semgrep
  script:
    - semgrep ci --config auto
  artifacts:
    reports:
      sast: gl-sast-report.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

security:dependency-scan:
  stage: security
  image: node:20-alpine
  script:
    - npm audit --audit-level=moderate
    - npm run license-check
  allow_failure: true
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

# Coverage Check
coverage-threshold:
  stage: quality
  image: node:20-alpine
  script:
    - |
      COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
      if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
        echo "[FAIL] Coverage $COVERAGE% below $COVERAGE_THRESHOLD% threshold"
        exit 1
      fi
      echo "[OK] Coverage $COVERAGE% meets threshold"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
```

---

## Pre-commit Hooks (Local Quality Gates)

### Using Husky + lint-staged

**Installation**:

```bash
npm install --save-dev husky lint-staged
npx husky install
npm pkg set scripts.prepare="husky install"
```

**Setup pre-commit hook**:

```bash
npx husky add .husky/pre-commit "npx lint-staged"
```

**Configuration** (`.lintstagedrc.json`):

```json
{
  "*.{js,jsx,ts,tsx}": [
    "eslint --fix",
    "prettier --write",
    "jest --bail --findRelatedTests"
  ],
  "*.{json,md,yml,yaml}": [
    "prettier --write"
  ],
  "*.{css,scss}": [
    "stylelint --fix",
    "prettier --write"
  ]
}
```

---

## Quality Metrics & Thresholds

### Recommended Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **Test Coverage** | < 80% | [FAIL] Blocking | Must add tests |
| **Linter Errors** | > 0 | [FAIL] Blocking | Must fix |
| **Security Vulnerabilities** | High/Critical | [FAIL] Blocking | Must patch |
| **PR Size** | > 1000 LOC | [WARNING] Warning | Consider splitting |
| **Cyclomatic Complexity** | > 10 | [WARNING] Warning | Consider refactoring |
| **Bundle Size Increase** | > 10% | [WARNING] Warning | Review dependencies |
| **Build Time** | > 10 min | ℹ Info | Optimize if possible |

---

## PR Status Checks (GitHub)

### Required Status Checks

Configure in **Settings -> Branches -> Branch protection rules**:

**Required checks before merging**:
- [OK] All tests pass
- [OK] Code coverage ≥ 80%
- [OK] No linter errors
- [OK] Security scan clean
- [OK] PR approved by 1+ reviewers

**Optional checks** (warnings only):
- [WARNING] PR size check
- [WARNING] Performance benchmarks
- [WARNING] Bundle size increase

---

## Automated PR Comments

### Coverage Report Comment

Using GitHub Actions:

```yaml
- name: Comment PR with coverage
  uses: romeovs/lcov-reporter-action@v0.3.1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    lcov-file: ./coverage/lcov.info
    title: "Coverage Report"
```

### Code Quality Summary

```yaml
- name: Comment PR with quality metrics
  uses: actions/github-script@v7
  with:
    script: |
      const coverage = process.env.COVERAGE;
      const lintErrors = process.env.LINT_ERRORS;
      const testResults = process.env.TEST_RESULTS;

      const body = `
      ## Quality Metrics

      | Metric | Value | Status |
      |--------|-------|--------|
      | Coverage | ${coverage}% | ${coverage >= 80 ? '[OK]' : '[FAIL]'} |
      | Lint Errors | ${lintErrors} | ${lintErrors == 0 ? '[OK]' : '[FAIL]'} |
      | Tests | ${testResults} | [OK] |
      `;

      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: body
      });
```

---

## Skipping Quality Gates (Emergency Hotfixes)

### When to Skip

**Only skip quality gates for**:
- Critical production outages
- Security vulnerabilities requiring immediate patch
- Data loss prevention

**How to skip** (use sparingly):

```bash
# Commit message bypass (if configured)
git commit -m "fix: critical security patch [skip-ci]"

# Or manual approval in GitHub/GitLab
```

**Post-hotfix requirements**:
- [ ] Create follow-up PR to add missing tests
- [ ] Document why gates were skipped
- [ ] Review in next team retrospective

---

## Quality Gate Exemptions

### Configuration Example

**`.quality-gates.yml`**:

```yaml
exemptions:
  - path: "legacy/**/*"
    reason: "Legacy code - gradual migration"
    checks:
      - coverage  # Don't block on coverage
    expires: "2025-12-31"

  - path: "scripts/**/*"
    reason: "Build scripts - different standards"
    checks:
      - complexity
      - coverage

  - path: "**/*.test.ts"
    reason: "Test files"
    checks:
      - complexity  # Tests can be complex
```

---

## Monitoring Quality Trends

### Track Over Time

**Metrics to monitor**:
- Average PR size
- Time to merge
- Test coverage trend
- Build success rate
- Security vulnerability count

**Tools**:
- **GitHub Insights** - Built-in PR metrics
- **Codecov** - Coverage trends
- **SonarQube** - Code quality trends
- **Grafana** - Custom dashboards

---

## Related Resources

- [PR Best Practices Guide](pr-best-practices.md) - PR size and review guidelines
- [Branching Strategies Comparison](branching-strategies.md) - Workflow patterns
- [Commit Conventions](commit-conventions.md) - Commit message standards
