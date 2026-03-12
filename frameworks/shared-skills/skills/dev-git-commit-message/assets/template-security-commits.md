# Security-Sensitive Commits Guide

Best practices for handling security-sensitive changes in git commits.

---

## Pre-Commit Security Checklist

### Before Every Commit

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] No credentials in configuration files
- [ ] No private keys or certificates
- [ ] No sensitive environment variables
- [ ] No internal URLs or IP addresses
- [ ] No PII (personal identifiable information)
- [ ] No proprietary algorithms exposed unintentionally

### Secrets Detection Tools

```bash
# Gitleaks (recommended)
gitleaks detect --source . --verbose

# TruffleHog (alternative)
trufflehog filesystem .

# git-secrets (AWS-focused)
git secrets --scan

# detect-secrets (Yelp)
detect-secrets scan
```

### Pre-Commit Hook Setup

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## Security-Related Commit Types

### Security Fix Commits

```
fix(security): patch XSS vulnerability in user input

Sanitize user input in comment fields to prevent
stored XSS attacks.

CVE: CVE-2024-12345
Severity: High
CVSS: 7.5

Closes #456
```

### Security Enhancement Commits

```
feat(security): add rate limiting to login endpoint

Implement token bucket rate limiting to prevent
brute force attacks on authentication.

- 5 attempts per 15 minutes per IP
- Exponential backoff after threshold
- Audit logging for rate limit events

Security-Review-By: @security-team
```

### Security Configuration Changes

```
chore(security): rotate API keys for payment service

Replace expired API keys with new credentials.
Old keys revoked in provider dashboard.

NOTE: Credentials stored in HashiCorp Vault, not in repo.
```

---

## Handling Accidental Secret Commits

### Immediate Response

```bash
# 1. Remove from working directory
rm path/to/secret-file

# 2. Remove from git history (if not pushed)
git reset --soft HEAD~1
# Edit to remove secret
git commit

# 3. If already pushed: ROTATE THE SECRET IMMEDIATELY
# Then remove from history:

# Option A: Interactive rebase (small number of commits)
git rebase -i HEAD~5
# Mark the commit as 'edit', remove secret, continue

# Option B: BFG Repo Cleaner (large history)
bfg --delete-files secret-file.txt
bfg --replace-text replacements.txt

# Option C: git-filter-repo (modern alternative)
git filter-repo --path secret-file.txt --invert-paths
```

### Post-Incident Checklist

- [ ] Secret rotated/revoked immediately
- [ ] Affected systems identified
- [ ] Access logs reviewed for unauthorized use
- [ ] Commit removed from all branches
- [ ] Force push to remote (with team notification)
- [ ] Incident documented
- [ ] Pre-commit hooks added to prevent recurrence

---

## Sensitive File Patterns

### .gitignore for Secrets

```gitignore
# Environment files
.env
.env.local
.env.*.local
*.env

# Credentials
credentials.json
service-account.json
*.pem
*.key
*.p12
*.pfx

# AWS
.aws/credentials
*.aws

# GCP
gcloud-*.json
*-credentials.json

# Terraform
*.tfvars
.terraform/
terraform.tfstate*

# IDE
.idea/
.vscode/settings.json

# Database
*.sqlite
*.db
dump.sql
```

### Files That Should NEVER Be Committed

| Pattern | Contains |
|---------|----------|
| `*.pem`, `*.key` | Private keys |
| `.env*` | Environment variables |
| `credentials.json` | Service account keys |
| `*.tfvars` | Terraform secrets |
| `id_rsa*`, `id_ed25519*` | SSH keys |
| `*.p12`, `*.pfx` | Certificates |
| `secrets.yaml` | Kubernetes secrets |
| `vault-*.json` | Vault tokens |

---

## Reversible vs Irreversible Changes

### Reversible (Can Be Amended)

- Commit message typos
- Wrong branch
- Forgotten files
- Formatting issues

```bash
# Amend last commit (before push)
git commit --amend

# Interactive rebase for older commits
git rebase -i HEAD~3
```

### Irreversible After Push (Treat as Permanent)

- Secrets in commit content
- PII in commit messages
- Breaking changes to public API
- License-incompatible code

> [WARNING] **Even after removal from git history, secrets may be:**
> - Cached by GitHub/GitLab
> - Indexed by search engines
> - Mirrored by CI systems
> - Downloaded by other developers
>
> **ALWAYS rotate exposed secrets.**

---

## Audit Trail Requirements

### When to Include Audit Information

```
fix(security): address authentication bypass

SECURITY ADVISORY: SA-2024-001
CVE: CVE-2024-XXXXX
CVSS: 9.1 (Critical)
CWE: CWE-287 (Improper Authentication)

Reported-By: security@researcher.com
Reviewed-By: @security-lead
Approved-By: @cto

Disclosure: Coordinated (public disclosure in 30 days)
```

### Security Commit Metadata

| Field | When Required | Format |
|-------|---------------|--------|
| CVE | Known vulnerability | CVE-YYYY-NNNNN |
| CVSS | Security fix | Score (e.g., 7.5) |
| CWE | Vulnerability fix | CWE-NNN |
| Reviewed-By | Security changes | @username |
| Advisory | Public disclosure | SA-YYYY-NNN |

---

## Branch Protection for Security

### GitHub Branch Protection Settings

```yaml
# Recommended settings for main branch
branch_protection:
  required_reviews: 2
  dismiss_stale_reviews: true
  require_code_owner_review: true
  required_status_checks:
    - security-scan
    - gitleaks
    - dependency-check
  enforce_admins: true
  restrict_pushes: true
```

### CODEOWNERS for Security Files

```
# .github/CODEOWNERS
/.env.example @security-team
/auth/ @security-team
/security/ @security-team
*.pem @security-team
/terraform/*.tf @security-team @devops
```

---

## Do / Avoid

### GOOD: Do

- Run secrets scan before every commit
- Rotate secrets immediately if exposed
- Use environment variables for credentials
- Document security fixes with CVE/CVSS
- Require security team review for auth changes
- Keep .gitignore updated for secret patterns
- Use pre-commit hooks for automated scanning

### BAD: Avoid

- Committing secrets "temporarily"
- Using hardcoded credentials in tests
- Storing real credentials in example files
- Assuming deleted secrets are safe
- Committing before secrets scan completes
- Using generic commit messages for security fixes
- Skipping review for "small" security changes

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **"Add secrets later"** | Secrets committed accidentally | Use env vars from start |
| **Secrets in tests** | Real credentials in repo | Use mocks/test credentials |
| **Force push to hide** | History still recoverable | Rotate + document |
| **Vague security commits** | No audit trail | Include CVE/CVSS |
| **Single reviewer** | Missed vulnerabilities | Require 2+ reviewers |
| **No pre-commit scan** | Secrets reach remote | Install gitleaks hook |

---

## Optional: AI/Automation

> **Note**: AI can detect patterns but should not be sole gatekeeper for security.

### Automated Detection

- Secret pattern matching (entropy-based)
- Known credential format detection
- PII identification (names, emails, SSNs)

### AI-Assisted Review

- Commit message security classification
- Dependency vulnerability correlation
- Breaking change impact analysis

### Bounded Claims

- AI detection has false positives/negatives
- Human review required for security commits
- Automated alerts need triage, not auto-action

---

## Related Resources

- [dev-git-workflow/references/validation-checklists.md](../../dev-git-workflow/references/validation-checklists.md)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)

---

**Last Updated**: December 2025
