# Dependency Scanning Guide

SCA (Software Composition Analysis) tool configuration, vulnerability SLA implementation, auto-merge policies, SBOM generation, and license compliance.

## Table of Contents

- [Tool Selection](#tool-selection)
- [Dependabot Configuration](#dependabot-configuration)
- [.github/dependabot.yml](#githubdependabotyml)
- [Renovate Configuration](#renovate-configuration)
- [Vulnerability SLA Implementation](#vulnerability-sla-implementation)
- [Default SLA Table](#default-sla-table)
- [SLA Adjustments](#sla-adjustments)
- [CI Enforcement](#ci-enforcement)
- [GitHub Actions: fail on unresolved critical/high CVEs](#github-actions-fail-on-unresolved-criticalhigh-cves)
- [Auto-Merge Policy](#auto-merge-policy)
- [When to Auto-Merge](#when-to-auto-merge)
- [Safety Checks for Auto-Merge](#safety-checks-for-auto-merge)
- [SBOM Generation](#sbom-generation)
- [CycloneDX](#cyclonedx)
- [JavaScript/Node.js](#javascriptnodejs)
- [Python](#python)
- [Multi-language with Trivy](#multi-language-with-trivy)
- [SPDX](#spdx)
- [Using Trivy](#using-trivy)
- [Using syft (Anchore)](#using-syft-anchore)
- [SBOM in CI](#sbom-in-ci)
- [For compliance: also push to a dependency-track or similar platform](#for-compliance-also-push-to-a-dependency-track-or-similar-platform)
- [License Compliance](#license-compliance)
- [Common License Categories](#common-license-categories)
- [Enforcement](#enforcement)
- [With Trivy](#with-trivy)
- [With license-checker (Node.js)](#with-license-checker-nodejs)
- [Transitive Dependency Risk](#transitive-dependency-risk)

## Tool Selection

| Tool | Best For | Model | Key Strength |
|------|----------|-------|-------------|
| Dependabot | GitHub-native, zero-config PRs | Free (GitHub) | Automatic PRs, version updates |
| Snyk Open Source | Multi-platform, fix PRs, license compliance | Free tier + commercial | Fix suggestions, reachability analysis |
| Renovate | Flexible scheduling, grouping, auto-merge | Open source | Highly configurable, multi-platform |
| Trivy (fs mode) | CLI scanning, CI integration | Open source | Fast, offline capable, multi-target |
| `npm audit` / `pip-audit` | Language-native quick checks | Built-in | Zero-install for that ecosystem |

**Default recommendation**: Dependabot for GitHub repos (zero friction) + Trivy in CI for additional coverage and SBOM generation.

## Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "team-security"
    labels:
      - "dependencies"
      - "security"
    # Group minor and patch updates to reduce PR noise
    groups:
      production-dependencies:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
      major-updates:
        patterns:
          - "*"
        update-types:
          - "major"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Renovate Configuration

```json5
// renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    "security:openssf-scorecard",
    ":automergeMinor",
    ":automergePatch"
  ],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"],
    "assignees": ["team-security"]
  },
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true,
      "automergeType": "pr",
      "requiredStatusChecks": null
    },
    {
      "matchUpdateTypes": ["minor"],
      "automerge": true,
      "automergeType": "pr",
      "minimumReleaseAge": "3 days"
    },
    {
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "reviewers": ["team-leads"]
    }
  ],
  "schedule": ["before 7am on Monday"]
}
```

## Vulnerability SLA Implementation

### Default SLA Table

| Severity | CVSS Range | Time to Remediate | Escalation |
|----------|-----------|-------------------|------------|
| Critical | 9.0-10.0 | 24 hours | Immediate page to security lead |
| High | 7.0-8.9 | 7 days | Slack alert to team, ticket auto-created |
| Medium | 4.0-6.9 | 30 days | Weekly triage review |
| Low | 0.1-3.9 | 90 days | Monthly backlog review |

### SLA Adjustments

Adjust based on context:

- **Reachable vulnerability** (confirmed exploitable path): tighten SLA by one level.
- **Not reachable** (dependency used but vulnerable function not called): relax by one level, but still fix.
- **Dev-only dependency** (build tools, test frameworks): relax by one level.
- **Public-facing service**: tighten all SLAs.
- **High EPSS score** (FIRST.org Exploit Prediction Scoring System — probability of exploitation
  in the wild in the next 30 days; current model EPSS v4, 2025.03.14): treat roughly EPSS > 0.5 as
  an automatic escalation to Critical SLA regardless of the CVSS band, because it means attackers
  are already exploiting this CVE at scale — CVSS severity is irrelevant if exploitation is already
  happening. See [owasp-top-10-coverage.md § Triage: Severity vs. Exploitability vs.
  Reachability](owasp-top-10-coverage.md#triage-severity-vs-exploitability-vs-reachability) for the
  full CVSS + EPSS + reachability triage model.
- **CVSS version mismatch**: NVD now publishes both CVSS 3.1 and 4.0 for new CVEs, computed
  differently from the same vector. Do not treat a 3.1 score and a 4.0 score as interchangeable
  when comparing findings across an SLA backlog — check which version produced each score.

### CI Enforcement

```yaml
# GitHub Actions: fail on unresolved critical/high CVEs
- name: Audit dependencies
  run: |
    npm audit --audit-level=high
    # Or with Trivy:
    # trivy fs --severity CRITICAL,HIGH --exit-code 1 .
```

## Auto-Merge Policy

### When to Auto-Merge

| Update Type | Auto-Merge | Conditions |
|-------------|-----------|------------|
| Patch (x.x.PATCH) | Yes | All CI checks pass |
| Minor (x.MINOR.x) | Yes | All CI checks pass, 3-day age minimum |
| Major (MAJOR.x.x) | No | Requires manual review |
| Security patch | Yes | All CI checks pass, regardless of version bump |

### Safety Checks for Auto-Merge

1. Full test suite must pass (unit, integration, E2E).
2. No new security findings introduced.
3. Lock file is properly updated.
4. No breaking API changes detected (for libraries).

## SBOM Generation

### CycloneDX

```bash
# JavaScript/Node.js
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Python
pip install cyclonedx-bom
cyclonedx-py environment --output sbom.json

# Multi-language with Trivy
trivy fs --format cyclonedx --output sbom.json .
```

### SPDX

```bash
# Using Trivy
trivy fs --format spdx-json --output sbom.spdx.json .

# Using syft (Anchore)
syft . -o spdx-json > sbom.spdx.json
```

### SBOM in CI

```yaml
- name: Generate SBOM
  run: trivy fs --format cyclonedx --output sbom.json .

- name: Upload SBOM artifact
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.json

# For compliance: also push to a dependency-track or similar platform
```

## License Compliance

### Common License Categories

| Category | Examples | Typical Policy |
|----------|---------|----------------|
| Permissive | MIT, Apache-2.0, BSD | Allow |
| Weak copyleft | LGPL, MPL-2.0 | Allow with review |
| Strong copyleft | GPL, AGPL | Block or review required |
| No license | Unlicensed packages | Block |

### Enforcement

```bash
# With Trivy
trivy fs --scanners license --severity UNKNOWN,HIGH,CRITICAL .

# With license-checker (Node.js)
npx license-checker --failOn "GPL-3.0;AGPL-3.0"
```

## Transitive Dependency Risk

- Run `npm ls --all` or `pip show --verbose` to understand dependency trees.
- Focus remediation on dependencies with the most transitive dependents.
- Pin critical transitive dependencies when the direct dependency does not.
- Monitor for dependency confusion attacks: verify package names, use scoped registries.
- Track dependency health signals: maintenance activity, OpenSSF Scorecard, known malicious packages.
