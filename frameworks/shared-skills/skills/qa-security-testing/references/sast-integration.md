# SAST Integration Guide

Static Application Security Testing integration patterns for CI/CD pipelines. Covers Semgrep and CodeQL as primary tools, with guidance on custom rules, baseline management, and false positive triage.

## Table of Contents

- [Tool Selection](#tool-selection)
- [Semgrep Setup](#semgrep-setup)
- [Basic CI Integration (GitHub Actions)](#basic-ci-integration-github-actions)
- [.github/workflows/semgrep.yml](#githubworkflowssemgrepyml)
- [Custom Rule Writing](#custom-rule-writing)
- [.semgrep/custom-rules/no-raw-sql.yml](#semgrepcustom-rulesno-raw-sqlyml)
- [Rule Management Strategy](#rule-management-strategy)
- [Baseline Management](#baseline-management)
- [Generate baseline](#generate-baseline)
- [CI scan showing only new findings (Semgrep App handles this automatically)](#ci-scan-showing-only-new-findings-semgrep-app-handles-this-automatically)
- [For OSS: use diff-aware scanning with --baseline-commit](#for-oss-use-diff-aware-scanning-with-baseline-commit)
- [CodeQL Setup](#codeql-setup)
- [GitHub Actions Integration](#github-actions-integration)
- [.github/workflows/codeql.yml](#githubworkflowscodeqlyml)
- [Custom CodeQL Queries](#custom-codeql-queries)
- [CodeQL vs Semgrep Decision](#codeql-vs-semgrep-decision)
- [False Positive Triage](#false-positive-triage)
- [Triage Workflow](#triage-workflow)
- [Common False Positive Categories](#common-false-positive-categories)
- [Language-Specific Guidance](#language-specific-guidance)
- [Metrics to Track](#metrics-to-track)

## Tool Selection

| Tool | Best For | Licensing | CI Speed |
|------|----------|-----------|----------|
| Semgrep | Fast scanning, custom rules, broad language support | Free OSS engine (Community Edition) + paid Cloud Platform | Fast (seconds to low minutes) |
| OpenGrep | Drop-in Semgrep CE replacement; restores cross-function taint analysis removed from CE | LGPL-2.1, fully free | Fast (seconds to low minutes) |
| CodeQL | Deep dataflow analysis, GitHub-native integration | Free for public repos, GHAS license for private | Slower (minutes to tens of minutes) |
| Snyk Code | IDE + CI with AI-assisted remediation | Commercial | Moderate |

**Default recommendation**: start with Semgrep (or OpenGrep if you need cross-function taint analysis without a paid plan) for speed and flexibility. Add CodeQL if you need deep dataflow analysis or are already on GitHub Advanced Security.

**OpenGrep note (January 2025)**: In late 2024, Semgrep moved cross-function taint analysis, fingerprinting, and related CE features to its commercial platform. OpenGrep is a community fork backed by a consortium of appsec vendors (Aikido, Endor Labs, Jit, Orca Security) that restores these features under the original LGPL-2.1 license. It is fully backward-compatible with Semgrep rule format, JSON output, and SARIF output. GitHub: https://github.com/opengrep/opengrep.

**Semgrep Managed Scanning (GA October 2025)**: Adds repositories in bulk and delivers SAST, SCA, and secrets scanning from Semgrep-hosted infrastructure without adding a CI workflow. Useful for bulk onboarding. Malicious dependency detection (detecting malware, typosquatting, credential-stealing packages) became GA in November 2025.

## Semgrep Setup

### Basic CI Integration (GitHub Actions)

```yaml
# .github/workflows/semgrep.yml
name: Semgrep SAST
on:
  pull_request: {}
  push:
    branches: [main]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container:
      image: semgrep/semgrep
    steps:
      - uses: actions/checkout@v4
      - run: semgrep ci
        env:
          SEMGREP_RULES: >-
            p/default
            p/owasp-top-ten
            p/security-audit
          # For Semgrep App managed policies:
          # SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

### Custom Rule Writing

Write rules for patterns specific to your codebase. Common targets:

- Framework-specific auth bypass patterns
- Unsafe deserialization in your stack
- Custom SQL/ORM query patterns that bypass parameterization
- Logging patterns that might leak sensitive data

```yaml
# .semgrep/custom-rules/no-raw-sql.yml
rules:
  - id: no-raw-sql-execution
    patterns:
      - pattern: $DB.execute($QUERY, ...)
      - pattern-not: $DB.execute($QUERY, $PARAMS, ...)
    message: >
      Raw SQL execution without parameterized query detected.
      Use parameterized queries to prevent SQL injection.
    severity: ERROR
    languages: [python]
    metadata:
      category: security
      cwe: ["CWE-89"]
      owasp: ["A05:2025 - Injection"]  # was A03:2021; many rule-packs still emit the 2021 tag
```

### Rule Management Strategy

1. **Start with curated rulesets**: `p/default` + `p/owasp-top-ten` for broad coverage.
2. **Add language-specific packs**: `p/python`, `p/javascript`, `p/java`, etc.
3. **Write custom rules** for your framework patterns (auth middleware, ORM usage, logging).
4. **Suppress with inline comments** when false positive is confirmed:
   ```python
   value = request.args.get("q")  # nosemgrep: python.flask.security.xss
   ```
5. **Review suppressions quarterly**: search for `nosemgrep` and verify each is still valid.

### Baseline Management

For existing codebases with many pre-existing findings:

1. Run initial scan and export findings to a baseline file.
2. Configure CI to report only new findings (diff-aware scanning).
3. Schedule a backlog reduction cadence for baseline findings.
4. Track baseline size as a metric — it should trend downward.

```bash
# Generate baseline
semgrep --config p/default --json --output baseline.json .

# CI scan showing only new findings (Semgrep App handles this automatically)
# For OSS: use diff-aware scanning with --baseline-commit
semgrep ci --baseline-commit origin/main
```

## CodeQL Setup

### GitHub Actions Integration

```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly deep scan

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    strategy:
      matrix:
        language: [javascript, python]  # Add your languages
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: +security-and-quality
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
```

### Custom CodeQL Queries

CodeQL uses a purpose-built query language (QL) for deep dataflow analysis:

```ql
/**
 * @name SQL injection from user input
 * @description Finds SQL queries built from user-controlled data
 * @kind path-problem
 * @problem.severity error
 * @security-severity 9.0
 * @id custom/sql-injection
 */

import javascript
import DataFlow::PathGraph
import semmle.javascript.security.dataflow.SqlInjectionQuery

from SqlInjection::Configuration cfg, DataFlow::PathNode source, DataFlow::PathNode sink
where cfg.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "SQL injection from $@.", source.getNode(), "user input"
```

### CodeQL vs Semgrep Decision

- **Use Semgrep when**: you need fast feedback on PRs, want easy custom rules, need broad language coverage, or want a single tool across multiple CI platforms.
- **Use CodeQL when**: you need deep interprocedural dataflow analysis, are on GitHub and want native integration, or need to trace complex vulnerability paths across function boundaries.
- **Use both when**: CodeQL runs on push/schedule for deep analysis, Semgrep runs on every PR for fast feedback.

## False Positive Triage

### Triage Workflow

1. **Verify**: reproduce the finding manually or confirm the vulnerable code path is reachable.
2. **Classify**: true positive (fix it), false positive (suppress with reason), or accepted risk (document and track).
3. **Act**:
   - True positive: create a ticket, assign owner, set SLA.
   - False positive: add inline suppression with comment explaining why.
   - Accepted risk: document in risk register, set review date.

### Common False Positive Categories

| Pattern | Why It Is FP | How to Suppress |
|---------|-------------|-----------------|
| Sanitized input flagged as injection | Scanner cannot see sanitization | Inline suppress with "sanitized by X" |
| Test/fixture data flagged as hardcoded secret | Not real credentials | Exclude test directories from secret rules |
| Dead code path flagged | Code is unreachable | Suppress and schedule removal |
| Framework-handled pattern | Framework provides protection | Write custom rule that accounts for framework |

## Language-Specific Guidance

| Language | Focus Areas | Key Rules |
|----------|------------|-----------|
| Python | Injection (SQL, command, template), deserialization, SSRF | `p/python`, `p/django`, `p/flask` |
| JavaScript/TypeScript | XSS, prototype pollution, path traversal, SSRF | `p/javascript`, `p/typescript`, `p/react` |
| Java | Injection, deserialization, XXE, LDAP injection | `p/java`, `p/spring` |
| Go | Command injection, path traversal, race conditions | `p/golang` |
| C# | SQL injection, XSS, insecure deserialization | `p/csharp` |

## Metrics to Track

- **New findings per PR**: should stabilize over time.
- **Mean time to triage**: target under 2 business days.
- **False positive rate**: if above 30%, tune rules or add custom patterns.
- **Baseline reduction**: track pre-existing findings trending toward zero.
- **Suppression count**: review quarterly, should not grow unbounded.
