# Code Quality Metrics Under AI Assistance

Operational reference for tracking whether AI coding tools maintain, improve, or degrade code quality. Covers defects, complexity, testing, security, technical debt, and the guardrails required to keep AI-generated code at production standard.

---

## Defect Metrics

### Core Defect Metrics

| # | Metric | Formula | AI-Team Target | Alert Threshold |
|---|--------|---------|---------------|-----------------|
| 1 | Bug Density (per KLOC) | Bugs found / (Lines of code / 1000) | < 2.0 | > 5.0 |
| 2 | Bug Density (per Feature) | Bugs found / Features shipped | < 0.3 | > 1.0 |
| 3 | Defect Escape Rate | Bugs found in production / Total bugs found | < 15% | > 30% |
| 4 | Rework Rate | PRs with follow-up fix within 14 days / Total PRs | < 10% | > 20% |
| 5 | Mean Time to Detect (MTTD) | Average time from defect introduction to detection | < 48 hours | > 2 weeks |
| 6 | Defect Clustering | Gini coefficient of bugs across modules | < 0.6 | > 0.8 |
| 7 | Regression Rate | Bugs introduced by fixes / Total fixes | < 5% | > 15% |

### Metric Details

**Bug Density (per KLOC)** — The foundational quality metric. Compare AI-assisted code vs non-AI code by tagging commits. Important: AI-generated code tends to have higher LOC for equivalent functionality, which can artificially deflate per-KLOC density while total bugs increase. Always track per-feature density alongside per-KLOC.

**Defect Escape Rate** — The most important quality metric for AI adoption. Measures what percentage of defects reach production before being caught. AI code that passes review but fails in production indicates:
- Reviewers rubber-stamping AI output
- Test coverage gaps on AI-generated paths
- AI generating plausible-looking but subtly incorrect code

Track monthly. A rising escape rate after AI adoption demands immediate intervention.

**Rework Rate** — Percentage of merged PRs that require a follow-up PR to fix issues within 14 days (configurable window). AI-assisted PRs with higher rework rates indicate developers are merging AI output without sufficient review.

Calculation:
```
For each merged PR:
  1. Find follow-up PRs that modify the same files within 14 days
  2. Filter to those with commit messages indicating a fix (heuristic: contains "fix", "bug", "revert", "correct")
  3. Rework Rate = count of reworked PRs / total merged PRs
```

**Mean Time to Detect (MTTD)** — Average time between when a defect-introducing commit is merged and when the defect is reported. Shorter MTTD means your quality gates (tests, monitoring, observability) are catching problems early. AI-generated defects often have longer MTTD because they can be semantically correct but logically flawed — tests pass, but behavior is wrong.

**Defect Clustering** — Measures whether bugs concentrate in specific modules or are distributed evenly. A Gini coefficient near 1.0 means all bugs are in a few modules. After AI adoption, watch for new clusters forming in areas where AI was heavily used — this signals the AI model is producing systematically flawed output for certain patterns.

**Regression Rate** — Bugs introduced when fixing other bugs. AI tools can increase regression rate if developers use AI to generate quick fixes without understanding the broader system impact. Track by comparing bug-fix PRs that introduce new bugs vs total bug-fix PRs.

### Defect Tracking by AI Involvement

Tag every bug with the degree of AI involvement in the code that introduced it:

| Tag | Definition | Action if Elevated |
|-----|-----------|-------------------|
| `ai-generated` | Bug is in code primarily written by AI | Review AI prompt/context quality |
| `ai-modified` | Bug is in human code modified by AI | Review AI edit suggestions |
| `ai-reviewed-only` | AI reviewed but didn't write the code | Review AI review accuracy |
| `no-ai` | No AI involvement | Baseline comparison |

---

## Code Complexity Tracking

### Complexity Metrics

| Metric | Tool | What It Measures | AI Concern |
|--------|------|-----------------|------------|
| Cyclomatic Complexity | radon (Python), complexity-report (JS), gocyclo (Go) | Number of independent paths through code | AI generates long functions with many branches |
| Cognitive Complexity | SonarQube, SonarCloud | How difficult code is for humans to understand | AI code can be syntactically simple but semantically confusing |
| Code Duplication Rate | SonarQube, jscpd, PMD CPD | Percentage of code that is duplicated | AI tends to generate similar-but-not-identical blocks |
| Afferent/Efferent Coupling | NDepend, JDepend, deptrac | How interconnected modules are | AI may not respect architectural boundaries |
| Function Length | Linters (ESLint, Pylint) | Lines per function/method | AI generates longer functions than experienced developers |

### Complexity Drift Monitoring

Track these weekly, graphed over time:

**Before/After AI Adoption:**

| Metric | Pre-AI Baseline | 3-Month Post-AI | 6-Month Post-AI | Target |
|--------|----------------|-----------------|-----------------|--------|
| Mean cyclomatic complexity | {baseline} | {measure} | {measure} | ≤ baseline + 10% |
| P90 cyclomatic complexity | {baseline} | {measure} | {measure} | ≤ baseline |
| Code duplication rate | {baseline} | {measure} | {measure} | ≤ baseline |
| Mean function length | {baseline} | {measure} | {measure} | ≤ baseline + 15% |
| Coupling between modules | {baseline} | {measure} | {measure} | ≤ baseline |

**Alert Rules:**
- Mean cyclomatic complexity increases > 10% over rolling 30-day window: investigate
- Code duplication rate increases > 5 percentage points: investigate
- Mean function length increases > 20%: enforce lint rules

### Complexity Reduction Strategies for AI Code

1. **Constrain AI output** — Include maximum function length and complexity rules in AI context (CLAUDE.md, .cursorrules)
2. **Post-generation refactoring** — Use AI itself to refactor its own output: "Break this function into smaller functions"
3. **Lint enforcement** — CI fails on complexity thresholds, regardless of whether code is AI-generated
4. **Architecture documentation** — Provide AI with module boundaries and coupling rules in context

---

## Test Coverage Impact

### Coverage Metrics

| Metric | Definition | AI-Team Target | Measurement Tool |
|--------|-----------|---------------|-----------------|
| Line Coverage | % of lines executed by tests | > 80% | Istanbul, Coverage.py, JaCoCo |
| Branch Coverage | % of conditional branches exercised | > 70% | Istanbul, Coverage.py, JaCoCo |
| Path Coverage | % of execution paths tested | > 50% | Specialized tools per language |
| Mutation Score | % of code mutations caught by tests | > 60% | Stryker, mutmut, PIT |
| Test-to-Code Ratio | Lines of test code / Lines of production code | 1:1 to 2:1 | LOC count |
| Flaky Test Rate | Tests that pass/fail non-deterministically / Total tests | < 2% | CI history analysis |

### AI-Generated Test Quality Assessment

AI excels at generating tests but the generated tests have systematic weaknesses:

| Strength | Weakness |
|----------|----------|
| High line coverage quickly | Tests often test implementation, not behavior |
| Good at happy-path testing | Weak on edge cases and error paths |
| Fast boilerplate generation | May assert on incidental behavior (brittle tests) |
| Consistent style | May miss domain-specific invariants |
| Good at mimicking existing test patterns | May duplicate test logic instead of using fixtures |

### Mutation Testing as Quality Gate

Standard coverage metrics are insufficient for AI-generated tests. A test suite can have 90% line coverage but fail to catch real bugs because the tests assert on the wrong things.

**Mutation testing** introduces small changes (mutations) to production code and checks whether tests fail. If tests still pass after a mutation, they are not actually verifying behavior.

**Process:**
1. Run mutation testing monthly (or on AI-generated test files)
2. Compare mutation scores: AI-generated tests vs human-written tests
3. Target: AI-generated test mutation score within 10% of human-written tests
4. If gap exceeds 10%: AI tests are superficial and need manual augmentation

**Mutation Score Benchmarks:**

| Score | Interpretation |
|-------|---------------|
| > 80% | Strong test suite — mutations reliably caught |
| 60-80% | Adequate — some gaps in assertion quality |
| 40-60% | Weak — tests present but not catching real bugs |
| < 40% | Superficial — coverage without verification |

### Flaky Test Management

AI-generated tests have a higher flaky rate due to:
- Hardcoded timing assumptions
- Non-deterministic test ordering dependencies
- Implicit environment dependencies
- Snapshot tests that break on style changes

**Tracking:**
- Tag AI-generated tests in test files (comment or metadata)
- Monitor flaky rate separately for AI vs human tests
- Quarantine flaky tests automatically (fail → retry → quarantine if intermittent)
- Target: AI-generated flaky rate ≤ 1.5x human-generated flaky rate

---

## Security Vulnerability Tracking

### Vulnerability Metrics

| Metric | Formula | Target | Alert |
|--------|---------|--------|-------|
| Vuln Introduction Rate | New SAST findings per sprint | Stable or decreasing | > 20% increase over 3 sprints |
| Critical Vuln Rate | Critical/High findings per sprint | 0 critical, < 2 high | Any critical |
| Dependency Vuln Count | Known CVEs in dependencies | < 5 medium, 0 high/critical | Any high/critical |
| Secrets Exposure Incidents | Credentials/tokens committed | 0 | Any occurrence |
| OWASP Top 10 Violations | Violations by category per quarter | Decreasing | Any new category appearing |
| Fix Time (Security) | Days from finding to fix | < 7 days (critical), < 30 days (high) | Exceeding SLA |

### CWE Category Distribution Under AI

AI-generated code tends to introduce specific vulnerability types more frequently:

| CWE Category | Risk Level with AI | Why |
|--------------|-------------------|-----|
| CWE-798: Hardcoded Credentials | High | AI may generate placeholder secrets that reach production |
| CWE-89: SQL Injection | Medium-High | AI may generate string concatenation instead of parameterized queries |
| CWE-79: Cross-Site Scripting | Medium | AI may skip output encoding in generated templates |
| CWE-22: Path Traversal | Medium | AI-generated file operations may not sanitize paths |
| CWE-502: Deserialization | Medium | AI may use unsafe deserialization by default |
| CWE-200: Information Exposure | Medium-High | AI may include verbose error messages with internal details |
| CWE-287: Auth Bypass | Low-Medium | AI may generate auth logic with subtle bypass conditions |
| CWE-330: Weak Randomness | Medium | AI may use Math.random() for security-sensitive operations |

### Security Scanning Integration

**Required scans for AI-generated code:**

| Scan Type | Tool Examples | When | Blocks Merge? |
|-----------|--------------|------|---------------|
| SAST | Semgrep, CodeQL, SonarQube | Every PR | Yes (critical/high) |
| Secret Detection | Gitleaks, TruffleHog, detect-secrets | Pre-commit + PR | Yes (any finding) |
| Dependency Scan | Dependabot, Snyk, Trivy | Daily + PR | Yes (critical) |
| Container Scan | Trivy, Grype | Build pipeline | Yes (critical) |
| License Compliance | FOSSA, Snyk | Weekly | No (advisory) |

### OWASP Top 10 Tracking

Track violations by category per quarter. Identify trends specific to AI-generated code.

| OWASP Category | Tracking Method | AI-Specific Concern |
|---------------|----------------|-------------------|
| A01: Broken Access Control | SAST + manual review | AI may generate RBAC with gaps |
| A02: Cryptographic Failures | SAST | AI may use deprecated algorithms |
| A03: Injection | SAST + DAST | AI may generate unsanitized inputs |
| A04: Insecure Design | Architecture review | AI lacks system-level security context |
| A05: Security Misconfiguration | Config scanning | AI may generate insecure defaults |
| A06: Vulnerable Components | Dependency scan | AI may suggest outdated packages |
| A07: Auth Failures | SAST + pen test | AI-generated auth logic needs extra review |
| A08: Data Integrity Failures | SAST | AI may skip integrity checks |
| A09: Logging Failures | SAST + review | AI may over-log (sensitive data) or under-log |
| A10: SSRF | SAST + DAST | AI-generated HTTP calls may not validate URLs |

---

## Technical Debt Accumulation

### Debt Metrics

| Metric | Definition | Measurement | AI Concern |
|--------|-----------|-------------|------------|
| Technical Debt Ratio | Remediation cost / Development cost | SonarQube | AI generates code faster than debt is addressed |
| Architecture Fitness | Automated architecture rule compliance | ArchUnit, Fitness Functions | AI may violate architectural boundaries |
| API Compatibility Breaks | Breaking changes in internal/external APIs | API diff tools, contract tests | AI may not know API contracts |
| Documentation-to-Code Ratio | Doc lines / Code lines | LOC analysis | AI-generated code often lacks inline documentation |
| Dead Code Accumulation | Unreachable code growth rate | SonarQube, tree-shaking analysis | AI generates code that duplicates existing functions |
| TODO/FIXME Density | Comment markers per KLOC | grep/search | AI may introduce placeholder comments that persist |

### Debt Tracking Dashboard

Track monthly, trend over 12 months:

```
Technical Debt Scorecard — {Month} {Year}

SONARQUBE DEBT RATIO
  Current: {n} days
  Trend: {↑/↓/→} ({delta} from last month)
  Rating: {A/B/C/D/E}

ARCHITECTURE COMPLIANCE
  Rules passing: {n} / {total} ({pct}%)
  New violations this month: {n}
  AI-attributed violations: {n}

CODE FRESHNESS
  Files not modified in 12 months: {pct}%
  Dead code estimate: {pct}%
  Deprecated API usage: {n} call sites

DOCUMENTATION
  Public API doc coverage: {pct}%
  Inline comment density: {n} per 100 LOC
  Stale documentation files: {n}
```

### Architecture Fitness Functions

Automated tests that verify architectural rules are not violated. Critical when AI generates code that may not respect boundaries.

| Rule | Implementation | Frequency |
|------|---------------|-----------|
| Layer dependencies (e.g., UI cannot import DB) | ArchUnit / custom lint | Every PR |
| Module boundary enforcement | Import analysis | Every PR |
| Maximum dependency depth | Dependency graph analysis | Weekly |
| API versioning compliance | Contract tests | Every PR |
| Database migration safety | Migration linter | Every PR |
| Package size limits | Bundle analysis | Every PR |

### Dead Code Management

AI tools accelerate dead code accumulation through two mechanisms:
1. **Replacement without deletion** — AI generates a new implementation; the old one is not removed
2. **Speculative generation** — AI generates helper functions or utility code that is never called

**Detection:**
- Run tree-shaking analysis monthly (for JS/TS: webpack, rollup; for Java: ProGuard; for Python: vulture)
- Track unreachable code percentage over time
- Flag files with zero imports/references

**Prevention:**
- Include "remove dead code" as an explicit step in AI-assisted refactoring workflows
- Configure linters to warn on unused exports, unused variables, unused functions
- Quarterly dead code cleanup sprints

---

## Quality Guardrails for AI-Generated Code

### Mandatory Review Rules

| Rule | Scope | Implementation |
|------|-------|---------------|
| No auto-merge for AI-generated PRs | All AI-assisted PRs | CODEOWNERS or branch protection requiring human approval |
| Security-sensitive paths require 2 reviewers | Auth, crypto, payment, PII handling | CODEOWNERS with 2+ required reviewers for sensitive paths |
| AI-generated tests require human test review | All AI-generated test files | PR label triggers additional review requirement |
| Large AI PRs (> 500 lines) require architecture review | PRs over threshold | Automated PR size check + escalation |

### Automated Quality Gates (CI/CD Integration)

```yaml
# Example quality gate pipeline stages
quality_gates:
  - name: lint
    blocks_merge: true
    rules:
      - max_cyclomatic_complexity: 15
      - max_function_length: 50
      - max_file_length: 500
      - no_unused_imports: true

  - name: security
    blocks_merge: true
    rules:
      - sast_critical_findings: 0
      - sast_high_findings: 0
      - secret_detection_findings: 0
      - dependency_critical_cves: 0

  - name: test_quality
    blocks_merge: true
    rules:
      - line_coverage_minimum: 80
      - branch_coverage_minimum: 70
      - no_test_skips_without_reason: true

  - name: complexity
    blocks_merge: false  # advisory
    rules:
      - max_cognitive_complexity: 20
      - max_coupling_between_modules: 10
      - duplication_rate_max: 5
```

### AI-Specific Lint Rules

Add these rules to your linter configuration when AI tools are in use:

| Rule | Purpose | Severity |
|------|---------|----------|
| No hardcoded strings in auth/crypto paths | Prevent AI-generated placeholder secrets | Error |
| No `console.log` / `print` in production code | AI frequently leaves debug output | Warning |
| No `any` type in TypeScript (strict mode) | AI falls back to `any` when types are complex | Error |
| No string concatenation in SQL | Prevent AI-generated injection vulnerabilities | Error |
| No `TODO` or `FIXME` without issue link | Prevent AI placeholder comments from persisting | Warning |
| No functions exceeding 50 lines | Contain AI-generated monolithic functions | Warning |
| No unused parameters | AI may generate function signatures with extra parameters | Warning |
| Require error handling on async operations | AI may omit error handling for brevity | Error |

### Pre-Commit Hooks for Quality Enforcement

```bash
# .pre-commit-config.yaml additions for AI-assisted development
repos:
  - repo: local
    hooks:
      - id: check-secrets
        name: Detect secrets
        entry: detect-secrets-hook
        language: system
        stages: [commit]

      - id: check-complexity
        name: Complexity check
        entry: radon cc --min C --no-assert
        language: system
        types: [python]
        stages: [commit]

      - id: check-function-length
        name: Function length check
        entry: custom-lint --max-function-length 50
        language: system
        stages: [commit]
```

### Quality Scorecard Template

Use monthly to track overall quality trajectory.

```
Code Quality Scorecard — {Month} {Year}

DEFECTS
  Bug density (per KLOC):     {n}  [{↑/↓/→}]  Target: < 2.0
  Defect escape rate:         {n}% [{↑/↓/→}]  Target: < 15%
  Rework rate:                {n}% [{↑/↓/→}]  Target: < 10%
  Regression rate:            {n}% [{↑/↓/→}]  Target: < 5%

COMPLEXITY
  Mean cyclomatic complexity: {n}  [{↑/↓/→}]  Target: ≤ baseline + 10%
  Code duplication rate:      {n}% [{↑/↓/→}]  Target: ≤ baseline
  Mean function length:       {n}  [{↑/↓/→}]  Target: ≤ baseline + 15%

TESTING
  Line coverage:              {n}% [{↑/↓/→}]  Target: > 80%
  Branch coverage:            {n}% [{↑/↓/→}]  Target: > 70%
  Mutation score:             {n}% [{↑/↓/→}]  Target: > 60%
  Flaky test rate:            {n}% [{↑/↓/→}]  Target: < 2%

SECURITY
  New SAST findings/sprint:   {n}  [{↑/↓/→}]  Target: stable or decreasing
  Open critical/high vulns:   {n}  [{↑/↓/→}]  Target: 0 critical, < 2 high
  Secret exposure incidents:  {n}  [{↑/↓/→}]  Target: 0

TECHNICAL DEBT
  SonarQube debt ratio:       {rating} [{↑/↓/→}]  Target: A
  Dead code estimate:         {n}% [{↑/↓/→}]  Target: < 3%
  Architecture violations:    {n}  [{↑/↓/→}]  Target: 0 new

OVERALL QUALITY GRADE: {A/B/C/D/F}
  A: All metrics at target
  B: 1-2 metrics at alert threshold
  C: 3-4 metrics at alert threshold
  D: Any metric significantly past alert threshold
  F: Quality regression across multiple categories
```
