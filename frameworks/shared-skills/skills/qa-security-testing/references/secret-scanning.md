# Secret Scanning Guide

Detection of secrets in source code using gitleaks, TruffleHog, and GitHub secret scanning. Covers pre-commit hooks, CI integration, custom patterns, and remediation workflows.

## Table of Contents

- [Tool Selection](#tool-selection)
- [gitleaks Pre-Commit Setup](#gitleaks-pre-commit-setup)
- [Installation](#installation)
- [macOS](#macos)
- [Or download binary from GitHub releases](#or-download-binary-from-github-releases)
- [https://github.com/gitleaks/gitleaks/releases](#httpsgithubcomgitleaksgitleaksreleases)
- [Pre-Commit Hook](#pre-commit-hook)
- [.pre-commit-config.yaml](#pre-commit-configyaml)
- [Install pre-commit framework](#install-pre-commit-framework)
- [Run against all files (initial scan)](#run-against-all-files-initial-scan)
- [CI Integration (GitHub Actions)](#ci-integration-github-actions)
- [.github/workflows/secrets.yml](#githubworkflowssecretsyml)
- [Custom Patterns](#custom-patterns)
- [gitleaks Configuration](#gitleaks-configuration)
- [.gitleaks.toml](#gitleakstoml)
- [Extend default rules](#extend-default-rules)
- [Add custom patterns for internal systems](#add-custom-patterns-for-internal-systems)
- [Allowlist for known false positives](#allowlist-for-known-false-positives)
- [Common Custom Patterns](#common-custom-patterns)
- [Historical Scanning](#historical-scanning)
- [gitleaks: scan full history](#gitleaks-scan-full-history)
- [TruffleHog: deep history scan with verification](#trufflehog-deep-history-scan-with-verification)
- [TruffleHog: scan specific branch](#trufflehog-scan-specific-branch)
- [When to Run Historical Scans](#when-to-run-historical-scans)
- [Remediation Workflow](#remediation-workflow)
- [Immediate Response (Critical)](#immediate-response-critical)
- [Why Removal from Code Is Not Enough](#why-removal-from-code-is-not-enough)
- [Secret Management Best Practices](#secret-management-best-practices)
- [Secrets-in-CI Failure Modes (Beyond Committed Code)](#secrets-in-ci-failure-modes-beyond-committed-code)
- [Metrics](#metrics)

## Tool Selection

| Tool | Best For | Model | Key Strength |
|------|----------|-------|-------------|
| gitleaks | Pre-commit hooks + CI, fast, configurable | Open source | Speed, custom patterns, SARIF output |
| TruffleHog | Deep historical scanning, entropy detection | Open source + commercial | Git history scanning, verified secrets |
| GitHub Secret Scanning | Push protection, partner alerts | Free (public) / GHAS (private) | Zero-config, automatic partner notification |

**Default recommendation**: gitleaks for pre-commit hooks and CI gates, GitHub secret scanning for push protection on GitHub repos.

**gitleaks maintenance note (2026)**: gitleaks is declared feature-complete by its primary maintainer (no new features; security patches only). The maintainer's focus has shifted to a successor project called Betterleaks (created 2026-02-03, MIT-licensed, co-maintained with long-time gitleaks contributors — reached v1.1.1 by 2026-03-17 and v1.1.2 by 2026-04-08). gitleaks remains the dominant, battle-tested open-source option — keep it as your primary CI gate. Betterleaks is still young (weeks to a couple of months old at last check); pilot it in parallel (non-blocking) rather than replacing gitleaks outright until it has a longer track record and your rule/allowlist config has been ported and validated against it.

## gitleaks Pre-Commit Setup

### Installation

```bash
# macOS
brew install gitleaks

# Or download binary from GitHub releases
# https://github.com/gitleaks/gitleaks/releases
```

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.22.0  # or later — verify at gitleaks releases
    hooks:
      - id: gitleaks
```

```bash
# Install pre-commit framework
pip install pre-commit
pre-commit install

# Run against all files (initial scan)
pre-commit run gitleaks --all-files
```

### CI Integration (GitHub Actions)

```yaml
# .github/workflows/secrets.yml
name: Secret Scanning
on:
  pull_request: {}
  push:
    branches: [main]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for diff scanning
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Custom Patterns

### gitleaks Configuration

```toml
# .gitleaks.toml
title = "Custom gitleaks config"

# Extend default rules
[extend]
useDefault = true

# Add custom patterns for internal systems
[[rules]]
id = "internal-api-key"
description = "Internal API key pattern"
regex = '''INTERNAL_KEY_[A-Za-z0-9]{32}'''
secretGroup = 0
entropy = 3.5

[[rules]]
id = "database-connection-string"
description = "Database connection string with credentials"
regex = '''(?i)(postgres|mysql|mongodb)://[^:]+:[^@]+@[^/]+'''
secretGroup = 0

# Allowlist for known false positives
[allowlist]
description = "Global allowlist"
paths = [
  '''(.*/)?\.gitleaks\.toml$''',
  '''(.*/)?test/fixtures/.*''',
  '''(.*/)?__tests__/.*mock.*'''
]
regexTarget = "match"
regexes = [
  '''EXAMPLE_KEY_[A-Za-z0-9]+''',
  '''test-api-key-not-real'''
]
```

### Common Custom Patterns

| Pattern | Regex | Purpose |
|---------|-------|---------|
| Internal API keys | `COMPANY_KEY_[A-Z0-9]{24,}` | Company-specific key format |
| JWT tokens | `eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+` | Hardcoded JWTs |
| Private keys | `-----BEGIN (RSA\|EC\|OPENSSH) PRIVATE KEY-----` | Embedded private keys |
| Database URLs | `(postgres\|mysql)://[^:]+:[^@]+@` | Connection strings with creds |

## Historical Scanning

Scan the full git history for secrets that were committed and later removed:

```bash
# gitleaks: scan full history
gitleaks detect --source . --verbose --report-format sarif --report-path secrets-history.sarif

# TruffleHog: deep history scan with verification
trufflehog git file://. --only-verified --json > verified-secrets.json

# TruffleHog: scan specific branch
trufflehog git file://. --branch main --only-verified
```

### When to Run Historical Scans

- During initial security tooling setup on an existing repo.
- After a security incident to check for other exposed secrets.
- Quarterly as part of security hygiene.
- When onboarding a new repository into the security program.

## Remediation Workflow

### Immediate Response (Critical)

When a secret is detected in code:

1. **Rotate immediately**: generate a new secret and deploy it. The exposed secret must be considered compromised even if only in version control.
2. **Revoke the old secret**: disable or delete the exposed credential in the issuing service.
3. **Audit usage**: check access logs for the compromised credential for unauthorized use.
4. **Remove from history** (if needed): use `git filter-repo` to remove from git history. Note: this rewrites history and requires coordination.
5. **Add to .gitignore**: ensure the file containing secrets is gitignored if it was a config file.
6. **Post-mortem**: document how the secret was committed and add preventive controls.

### Why Removal from Code Is Not Enough

- Git history preserves every committed version. `git log -p` will show the secret.
- Forks, mirrors, and CI caches may have copies.
- Automated scanners (including malicious ones) watch public repos for exposed secrets.
- The only safe response is rotation + revocation.

### Secret Management Best Practices

- Use environment variables or secret managers (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager).
- Never commit `.env` files; always `.gitignore` them.
- Use CI/CD secret injection (GitHub Actions secrets, GitLab CI variables).
- Rotate secrets on a regular schedule, not just when exposed.
- Use short-lived tokens and OIDC federation where possible (e.g., GitHub OIDC for cloud provider access).

## Secrets-in-CI Failure Modes (Beyond Committed Code)

gitleaks and TruffleHog scan the repository — commits, working tree, history. That is necessary
but not sufficient: most real secret leaks a mature security program sees are not "someone
committed a key," they are the CI/CD platform itself handing the secret to an untrusted party.
Scan for these separately; a green gitleaks run does not mean the pipeline is safe.

- **Forked-PR privilege escalation via `pull_request_target` / `workflow_run`**: a workflow
  triggered by `pull_request_target` runs with the base repo's secrets available, but can be made
  to check out and execute the fork's (attacker-controlled) code. This is the single most common
  way public-repo CI/CD secrets get stolen — not a gitleaks miss, an architecture mistake. Audit
  every workflow using `pull_request_target` or `workflow_run`: it must never execute code from the
  PR head with secrets in scope. Prefer `pull_request` (no secrets) plus a separate,
  manually-approved privileged workflow for anything that needs them.
- **Secrets echoed into build/step logs**: `set -x`, verbose HTTP client logging, or a library that
  logs its full config (including a bearer token) at debug level will print a secret into the CI
  log, which is often more widely readable than the source repo (broader team access, longer
  retention, sometimes public on OSS CI). GitHub's log-masking only redacts values it saw
  registered as a secret through its own mechanism — it will not mask a token minted *inside* the
  job that never passed through `secrets.*`. Treat CI log scanning as a separate, mandatory target
  for gitleaks/TruffleHog, not an afterthought.
- **Secrets baked into build artifacts or caches**: a `.env` file copied into a Docker layer, a
  dependency cache that snapshots a `.npmrc` with an auth token, or a build artifact uploaded with
  `actions/upload-artifact` that includes a debug dump. These persist and are downloadable long
  after the job completes. Scan produced artifacts and image layers, not just source.
- **Long-lived cloud credentials in CI vs. OIDC federation**: a static AWS/GCP/Azure key stored as
  a CI secret is a permanent target — once leaked by any of the above paths, it is valid until
  someone notices and rotates it. Short-lived OIDC-federated credentials (GitHub OIDC → cloud
  provider role assumption) reduce blast radius to the workflow's runtime, typically minutes. This
  is a bigger risk reduction than any scanner tuning — prioritize migrating long-lived cloud keys
  to OIDC federation over incremental gitleaks rule tuning.
- **Third-party Actions/plugins with `id-token: write` or secrets access**: any action pinned to a
  mutable tag (not a SHA) is a supply-chain path to secret theft even if your own code never leaks
  anything — see the March 2026 Trivy/`trivy-action` compromise in
  [container-iac-scanning.md](container-iac-scanning.md), where a trusted scanner action itself was
  weaponized to exfiltrate CI secrets. Any workflow granting a third-party action access to secrets
  or `id-token: write` is in scope for this failure mode, not just scanner actions specifically.

## Metrics

| Metric | Target |
|--------|--------|
| Pre-commit hook adoption | 100% of developers |
| CI gate coverage | All repositories |
| Mean time to rotate (after detection) | Under 1 hour for critical |
| Historical scan frequency | Quarterly |
| False positive rate | Under 10% (tune patterns if higher) |
