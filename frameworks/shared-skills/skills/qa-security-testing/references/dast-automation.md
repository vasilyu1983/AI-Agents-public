# DAST Automation Guide

Dynamic Application Security Testing automation for CI/CD pipelines. Covers OWASP ZAP automation framework, Nuclei template scanning, authenticated scan setup, and staging environment integration.

## Table of Contents

- [Tool Selection](#tool-selection)
- [OWASP ZAP Automation Framework](#owasp-zap-automation-framework)
- [Basic CI Integration (GitHub Actions)](#basic-ci-integration-github-actions)
- [.github/workflows/dast-zap.yml](#githubworkflowsdast-zapyml)
- [Automation Framework Configuration](#automation-framework-configuration)
- [zap-automation.yaml](#zap-automationyaml)
- [API Scanning with OpenAPI](#api-scanning-with-openapi)
- [Nuclei Template Scanning](#nuclei-template-scanning)
- [Basic Setup](#basic-setup)
- [.github/workflows/nuclei.yml](#githubworkflowsnucleiyml)
- [Custom Templates](#custom-templates)
- [.nuclei-templates/custom/auth-bypass-check.yaml](#nuclei-templatescustomauth-bypass-checkyaml)
- [Template Categories for CI](#template-categories-for-ci)
- [Authenticated Scanning](#authenticated-scanning)
- [Token-Based Authentication (APIs)](#token-based-authentication-apis)
- [ZAP automation with bearer token](#zap-automation-with-bearer-token)
- [Nuclei with auth header](#nuclei-with-auth-header)
- [Session-Based Authentication (Web Apps)](#session-based-authentication-web-apps)
- [Auth Testing Best Practices](#auth-testing-best-practices)
- [Baseline Management](#baseline-management)
- [Handling Known Findings](#handling-known-findings)
- [ZAP: use rules file to manage alert thresholds](#zap-use-rules-file-to-manage-alert-thresholds)
- [zap-rules.tsv](#zap-rulestsv)
- [Format: alert_id  action  (IGNORE, WARN, FAIL)](#format-alertid-action-ignore-warn-fail)
- [CI Integration Patterns](#ci-integration-patterns)
- [When to Run DAST](#when-to-run-dast)
- [Performance Tips](#performance-tips)

## Tool Selection

| Tool | Best For | Model | Speed |
|------|----------|-------|-------|
| ZAP (by Checkmarx) | Comprehensive web app scanning, API scanning | Open source (FOSS) | Moderate (minutes to hours) |
| Nuclei | Template-based targeted scanning, known CVEs | Open source | Fast (seconds to minutes) |
| Burp Suite | Deep manual + automated testing | Commercial | Moderate |

**Default recommendation**: ZAP for broad automated scanning in CI, Nuclei for targeted checks against known vulnerability templates. Use Burp Suite for manual penetration testing augmentation.

**ZAP naming note**: ZAP left OWASP in September 2023 to obtain independent funding. In September 2024, Checkmarx hired the three core ZAP maintainers; the project is now officially "ZAP by Checkmarx" (zaproxy.org). It remains free and open-source. Documentation and GitHub Actions are unchanged: `zaproxy/action-full-scan`, `zaproxy/action-api-scan`. Version 2.17.0 shipped December 2025.

## OWASP ZAP Automation Framework

### Basic CI Integration (GitHub Actions)

```yaml
# .github/workflows/dast-zap.yml
name: DAST - OWASP ZAP
on:
  workflow_run:
    workflows: ["Deploy to Staging"]
    types: [completed]

jobs:
  zap-scan:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ZAP API Scan
        uses: zaproxy/action-api-scan@v0.9.0
        with:
          target: ${{ vars.STAGING_URL }}
          rules_file_name: zap-rules.tsv
          cmd_options: '-z "-configfile zap-config.prop"'
```

### Automation Framework Configuration

ZAP's Automation Framework uses YAML plans for repeatable scans:

```yaml
# zap-automation.yaml
env:
  contexts:
    - name: "app-context"
      urls:
        - "https://staging.example.com"
      includePaths:
        - "https://staging.example.com/.*"
      excludePaths:
        - "https://staging.example.com/logout.*"
      authentication:
        method: "browser"
        parameters:
          loginPageUrl: "https://staging.example.com/login"
          loginPageWait: 5
        verification:
          method: "response"
          pollFrequency: 60
          pollUnits: "requests"
          pollUrl: "https://staging.example.com/api/me"
          pollPostData: ""
  parameters:
    failOnError: true
    failOnWarning: false

jobs:
  - type: passiveScan-config
    parameters:
      maxAlertsPerRule: 10
      scanOnlyInScope: true

  - type: spider
    parameters:
      context: "app-context"
      maxDuration: 5
      maxDepth: 5

  - type: activeScan
    parameters:
      context: "app-context"
      maxRuleDurationInMins: 5
      maxScanDurationInMins: 30

  - type: report
    parameters:
      template: "sarif-json"
      reportDir: "/zap/reports"
      reportFile: "zap-report"
    risks:
      - high
      - medium
```

### API Scanning with OpenAPI

ZAP can import OpenAPI specs to drive API-specific scanning:

```yaml
jobs:
  - type: openapi
    parameters:
      apiUrl: "https://staging.example.com/api/v1/openapi.json"
      context: "app-context"
  - type: activeScan
    parameters:
      context: "app-context"
      policy: "API-Scan-Policy"
```

## Nuclei Template Scanning

### Basic Setup

```yaml
# .github/workflows/nuclei.yml
name: Nuclei Scan
on:
  workflow_run:
    workflows: ["Deploy to Staging"]
    types: [completed]

jobs:
  nuclei:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: projectdiscovery/nuclei-action@v2
        with:
          target: ${{ vars.STAGING_URL }}
          templates: "cves/,vulnerabilities/,misconfiguration/"
          severity: "critical,high,medium"
          sarif-export: nuclei-results.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: nuclei-results.sarif
```

### Custom Templates

Write templates for application-specific checks:

```yaml
# .nuclei-templates/custom/auth-bypass-check.yaml
id: auth-bypass-admin-endpoint
info:
  name: Admin Endpoint Auth Bypass Check
  severity: critical
  description: Verify admin endpoints require authentication
  tags: custom,auth

http:
  - method: GET
    path:
      - "{{BaseURL}}/admin"
      - "{{BaseURL}}/api/admin/users"
      - "{{BaseURL}}/api/internal/config"
    matchers-condition: or
    matchers:
      - type: status
        status:
          - 200
        condition: or
    # If we get 200 without auth, it is a finding
```

### Template Categories for CI

| Category | When to Run | Examples |
|----------|------------|---------|
| `cves/` | Weekly scheduled scan | Known CVE checks for your stack |
| `vulnerabilities/` | Staging deploy | Common vulnerability patterns |
| `misconfiguration/` | Staging deploy | Server misconfiguration, default creds |
| `exposures/` | Staging deploy | Sensitive file exposure, debug endpoints |
| Custom templates | Every staging deploy | Application-specific checks |

## Authenticated Scanning

### Token-Based Authentication (APIs)

```yaml
# ZAP automation with bearer token
env:
  contexts:
    - name: "api-context"
      authentication:
        method: "script"
        parameters:
          script: "auth-script.js"
          scriptEngine: "ECMAScript"
      users:
        - name: "test-user"
          credentials:
            username: "${API_TEST_USER}"
            password: "${API_TEST_PASS}"

# Nuclei with auth header
http:
  - method: GET
    path:
      - "{{BaseURL}}/api/protected"
    headers:
      Authorization: "Bearer {{auth_token}}"
```

### Session-Based Authentication (Web Apps)

1. Configure ZAP browser-based authentication with login page URL and form fields.
2. Define session verification endpoint (e.g., `/api/me` returning 200 when authenticated).
3. Set re-authentication triggers for when the session expires.
4. Use dedicated test accounts with appropriate permissions but limited blast radius.

### Auth Testing Best Practices

- Maintain dedicated test user accounts per permission level (admin, standard, read-only).
- Store credentials in CI secrets, never in config files.
- Test both authenticated and unauthenticated paths to detect auth bypass.
- Include horizontal privilege escalation checks (user A accessing user B's resources).

## Baseline Management

### Handling Known Findings

Not every finding can be fixed immediately. Use baselines to avoid CI noise:

1. Run initial full scan and export findings.
2. Review each finding: fix, suppress (with reason), or add to backlog.
3. Configure CI to fail only on new findings above baseline.
4. Review baseline monthly and reduce it over time.

```bash
# ZAP: use rules file to manage alert thresholds
# zap-rules.tsv
# Format: alert_id  action  (IGNORE, WARN, FAIL)
10021   IGNORE   # X-Content-Type-Options (accepted risk)
10038   WARN     # CSP header missing (tracked in backlog)
40012   FAIL     # XSS reflected (always block)
```

## CI Integration Patterns

### When to Run DAST

| Trigger | Scan Type | Duration Target |
|---------|-----------|-----------------|
| Staging deploy | Targeted scan (spider + active, limited scope) | Under 15 minutes |
| Weekly schedule | Full scan (all policies, deep crawl) | Up to 2 hours |
| Pre-release | Full scan + authenticated + API scan | Up to 2 hours |
| On-demand | Specific template/policy against target | Varies |

### Performance Tips

- Limit spider depth and duration for CI scans.
- Use API specs to drive scanning instead of crawling for API-only services.
- Run passive scanning always (nearly free), active scanning on staging only.
- Parallelize Nuclei template categories across CI jobs.
- Cache Nuclei templates to avoid re-downloading on every run.
