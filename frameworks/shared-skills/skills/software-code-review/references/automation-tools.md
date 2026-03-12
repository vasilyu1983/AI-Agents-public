# Code Review Automation Tools & Setup 

Modern code review combines automated checks with manual review for maximum effectiveness. **Automation finds 60-70% of issues**, letting human reviewers focus on architecture, logic, and business concerns.

## Automation Strategy

### Three-Layer Approach

**Layer 1: Pre-commit checks (Local)**
- Runs on developer machine before commit
- Fast feedback (seconds)
- Catches obvious issues early

**Layer 2: PR checks (CI/CD)**
- Runs on every pull request
- Comprehensive analysis (minutes)
- Blocks merge if critical issues found

**Layer 3: Continuous monitoring (Production)**
- Runs on deployed code
- Security scanning, dependency updates
- Weekly reports

## Essential Tools by Category

### 1. Code Linters

**JavaScript/TypeScript**:
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-strict/recommended",
    "plugin:security/recommended"
  ],
  "plugins": ["security", "sonarjs"],
  "rules": {
    "complexity": ["error", 10],
    "max-depth": ["error", 3],
    "max-lines-per-function": ["error", 50],
    "sonarjs/cognitive-complexity": ["error", 15]
  }
}
```

**Python**:
```toml
# pyproject.toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "B", "C90"]
ignore = ["E501"]

[tool.ruff.mccabe]
max-complexity = 10
```

**Go**:
```bash
# .golangci.yml
linters:
  enable:
    - gofmt
    - govet
    - staticcheck
    - gosec
    - errcheck
    - ineffassign
```

### 2. Code Formatters

**JavaScript/TypeScript** - Prettier:
```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

**Python** - Black:
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

**Go** - gofmt (built-in):
```bash
gofmt -w .
```

### 3. Static Analysis

**SonarQube/SonarCloud** (Multi-language):
```yaml
# sonar-project.properties
sonar.projectKey=my-project
sonar.sources=src
sonar.tests=tests
sonar.coverage.exclusions=**/*test*/**
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Quality gates
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

**CodeClimate** (Multi-language):
```yaml
# .codeclimate.yml
version: "2"
checks:
  argument-count:
    enabled: true
    config:
      threshold: 4
  complex-logic:
    enabled: true
    config:
      threshold: 4
  file-lines:
    enabled: true
    config:
      threshold: 250
  method-complexity:
    enabled: true
    config:
      threshold: 5
  method-lines:
    enabled: true
    config:
      threshold: 25
```

**ESLint Plugin Security** (JavaScript):
```bash
npm install --save-dev eslint-plugin-security
```

### 4. Security Scanners

**Snyk** (Dependency vulnerabilities):
```yaml
# .github/workflows/security.yml
name: Security Scan
on: [pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

**Trivy** (Container security):
```bash
trivy image --severity HIGH,CRITICAL myimage:latest
```

**Semgrep** (Code patterns):
```yaml
# .semgrep.yml
rules:
  - id: hardcoded-secret
    patterns:
      - pattern: password = "..."
    message: Hardcoded password detected
    severity: ERROR
```

### 5. Test Coverage Tools

**JavaScript** - Istanbul/NYC:
```json
// package.json
{
  "scripts": {
    "test": "jest --coverage",
    "test:coverage": "jest --coverage --coverageThreshold='{\"global\":{\"branches\":80,\"functions\":80,\"lines\":80}}'"
  }
}
```

**Python** - Coverage.py:
```toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

**Go** - Built-in:
```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 6. AI-Powered Review Tools ()

**GitHub Copilot for Pull Requests**:
- Generates PR summaries
- Suggests reviewers
- Identifies potential issues
- Free for GitHub Enterprise

**Qodo (formerly Codium)**:
```yaml
# .qodo.yml
features:
  pr_reviewer: true
  auto_improve: true
  test_generation: true

pr_reviewer:
  auto_review: true
  inline_suggestions: true
  security_check: true
```

**CodeRabbit**:
- AI code reviews
- Learning from team patterns
- Context-aware suggestions

**Amazon CodeGuru**:
```yaml
# buildspec.yml
phases:
  pre_build:
    commands:
      - aws codeguru-reviewer associate-repository
      - aws codeguru-reviewer create-code-review
```

### 7. Dependency Management

**Dependabot** (GitHub):
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "team-leads"
    labels:
      - "dependencies"
```

**Renovate** (Multi-platform):
```json
{
  "extends": ["config:base"],
  "rangeStrategy": "bump",
  "packageRules": [
    {
      "updateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
```

### 8. Stack-Aware Merge Queues (2026)

Stacked PRs break large changes into sequential, dependent pull requests. Stack-aware merge queues treat these stacks as first-class citizens, validating entire stacks atomically rather than testing each PR independently.

**Graphite**:

```bash
# Install CLI
npm install -g @withgraphite/graphite-cli

# Create stacked PRs
gt stack submit

# Queue entire stack for merge
gt stack merge
```

- Treats PR stacks as first-class citizens
- Runs CI on entire stack atomically (top PR contains all changes)
- **74% reduction** in median merge time (Ramp Engineering)
- Eliminates CI redundancy across stack
- [graphite.com](https://graphite.com/)

**Aviator**:

```yaml
# aviator.yaml
merge_rules:
  - name: default
    conditions:
      - base_branch: main
    merge_mode:
      type: parallel
      parallel_mode:
        max_parallel_builds: 5
    enable_stacked_prs: true
```

- Stack-aware queue with partial stack support
- Speculative execution with intelligent bisection
- [aviator.co](https://aviator.co/)

**Meta Sapling**:

```bash
# Sapling SCM with built-in stacking
sl stack  # View current stack
sl submit # Submit stack for review
```

- Source control system with native stacking support
- [sapling-scm.com](https://sapling-scm.com/)

**Measured Benefits**:

| Team | Improvement | Source |
|------|-------------|--------|
| Ramp | 74% faster merges, 3x velocity | Graphite case study |
| Asana | 7 hours/week saved per engineer | Graphite blog |
| Shopify | 15-25% CI cost savings | Projected savings |

**When to Use**:

- Large features requiring multiple dependent changes
- Teams with >10 engineers experiencing merge conflicts
- High-velocity teams with frequent deployments
- When review bottlenecks slow delivery

## CI/CD Pipeline Configuration

### GitHub Actions Example

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint

  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run format:check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm test -- --coverage
      - name: Coverage check
        run: |
          if [ $(cat coverage/coverage-summary.json | jq '.total.lines.pct') -lt 80 ]; then
            echo "Coverage below 80%"
            exit 1
          fi

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      - run: npm audit --audit-level=high

  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: sonarsource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: qodo-ai/pr-agent@main
        env:
          QODO_API_KEY: ${{ secrets.QODO_API_KEY }}
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - security
  - quality

lint:
  stage: lint
  script:
    - npm ci
    - npm run lint

test:
  stage: test
  script:
    - npm ci
    - npm test -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

security:
  stage: security
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker run --rm -v $(pwd):/src aquasec/trivy fs /src

code_quality:
  stage: quality
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner
```

## Pre-commit Hooks

**Husky + lint-staged** (JavaScript):

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{js,ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "jest --bail --findRelatedTests"
    ],
    "*.{json,md}": ["prettier --write"]
  }
}
```

**pre-commit** (Python):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
```

## Tool Selection Matrix

| Tool Category | Small Teams (< 10) | Medium Teams (10-50) | Large Teams (50+) |
|--------------|-------------------|---------------------|-------------------|
| **Linter** | ESLint/Pylint | ESLint + plugins | ESLint + SonarQube |
| **Formatter** | Prettier/Black | Prettier/Black | Prettier/Black |
| **Static Analysis** | ESLint plugins | CodeClimate | SonarQube Enterprise |
| **Security** | npm audit/pip-audit | Snyk | Snyk + Semgrep |
| **Coverage** | Built-in | Built-in + Codecov | SonarQube + Codecov |
| **AI Review** | GitHub Copilot | Qodo/CodeRabbit | CodeRabbit Enterprise |
| **Dependencies** | Dependabot | Dependabot + Renovate | Renovate + Snyk |

## Configuration Best Practices

### 1. Fail Fast, Fail Clear

```yaml
# Good - Clear failure message
- name: Check coverage
  run: |
    COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "[FAIL] Coverage is $COVERAGE%, minimum is 80%"
      echo "Run 'npm test -- --coverage' locally to see gaps"
      exit 1
    fi
```

### 2. Cache Dependencies

```yaml
# GitHub Actions
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### 3. Parallel Execution

```yaml
# Run independent checks in parallel
jobs:
  lint:
    # ...
  test:
    # ...
  security:
    # ...
# These all run simultaneously
```

### 4. Progressive Enhancement

**Phase 1**: Basic checks (week 1)
- Linter
- Formatter
- Basic tests

**Phase 2**: Quality gates (week 2-3)
- Coverage requirements
- Security scanning
- Static analysis

**Phase 3**: Advanced automation (month 2+)
- AI-powered review
- Automated dependency updates
- Performance regression testing

## Metrics Dashboard

### What to Track

```yaml
# Example metrics.yml
code_quality:
  coverage_threshold: 80
  max_complexity: 10
  max_function_length: 50
  max_file_length: 300

security:
  max_high_vulnerabilities: 0
  max_medium_vulnerabilities: 5
  dependency_update_lag_days: 14

review_process:
  max_review_time_hours: 24
  max_pr_size_lines: 400
  required_approvals: 2

performance:
  build_time_minutes: 5
  test_time_minutes: 3
  deploy_time_minutes: 10
```

### Visualization Tools

**SonarQube Dashboard**:
- Technical debt ratio
- Code smells
- Security hotspots
- Coverage trends

**CodeClimate Dashboard**:
- Maintainability grade
- Test coverage
- Code duplication
- Complexity trends

**Custom Grafana Dashboard**:
```sql
-- PR metrics
SELECT
  DATE(created_at) as date,
  AVG(time_to_first_review) as avg_review_time,
  AVG(lines_changed) as avg_pr_size,
  COUNT(*) as total_prs
FROM pull_requests
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
```

## Cost Considerations

### Open Source (Free)
- ESLint, Prettier, Black
- GitHub Actions (2000 min/month)
- Dependabot
- SonarCloud (public repos)

### Small Team ($50-200/month)
- GitHub Team ($4/user)
- Snyk ($25/month)
- CodeClimate ($249/month for small team)

### Enterprise ($500+/month)
- SonarQube Enterprise
- Snyk Enterprise
- CodeRabbit Teams
- GitHub Enterprise

## Troubleshooting

### Common Issues

**False Positives**:
```javascript
// Suppress specific rules when necessary
/* eslint-disable-next-line security/detect-object-injection */
const value = obj[dynamicKey];
```

**Slow CI**:
```yaml
# Cache everything possible
- uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      ~/.cache
      node_modules
```

**Flaky Tests**:
```javascript
// Retry flaky tests automatically
jest.retryTimes(3, { logErrorsBeforeRetry: true });
```

## Resources

- **GitHub Actions**: https://docs.github.com/actions
- **SonarQube**: https://docs.sonarqube.org/
- **Snyk**: https://docs.snyk.io/
- **ESLint**: https://eslint.org/docs/
- **Semgrep**: https://semgrep.dev/docs/
