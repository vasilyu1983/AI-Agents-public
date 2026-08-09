# Security Test Plan: {{PROJECT_NAME}}

## Scope

- **Application**: {{APPLICATION_NAME}}
- **Type**: {{web app | API | mobile | infrastructure}}
- **Environment**: {{staging URL or target}}
- **Languages/Frameworks**: {{list}}
- **Compliance**: {{SOC 2 | PCI DSS | HIPAA | none}}

## Attack Surface

| Surface | Description | Risk Level |
|---------|-------------|------------|
| {{e.g., Public API}} | {{description}} | {{Critical/High/Medium/Low}} |
| {{e.g., Admin panel}} | {{description}} | {{Critical/High/Medium/Low}} |
| {{e.g., File upload}} | {{description}} | {{Critical/High/Medium/Low}} |

## Tool Selection

| Category | Tool | Rationale |
|----------|------|-----------|
| SAST | {{Semgrep / CodeQL}} | {{why}} |
| SCA | {{Dependabot / Snyk / Trivy}} | {{why}} |
| DAST | {{ZAP / Nuclei}} | {{why}} |
| Secret scanning | {{gitleaks / TruffleHog}} | {{why}} |
| Container scanning | {{Trivy / Grype}} | {{why, if applicable}} |
| IaC scanning | {{Checkov / Trivy}} | {{why, if applicable}} |

## CI Gate Policy

| Stage | Tools | Gate Rule |
|-------|-------|-----------|
| Pre-merge | SAST, secrets, SCA | Block on: {{criteria}} |
| Pre-deploy | DAST, container scan | Block on: {{criteria}} |
| Scheduled | Full DAST, registry scan | Findings feed triage backlog |
| Release | All gates | Block if: {{criteria}} |

## Vulnerability SLAs

| Severity | Time to Remediate | Escalation Path |
|----------|-------------------|-----------------|
| Critical | {{24h}} | {{who}} |
| High | {{7d}} | {{who}} |
| Medium | {{30d}} | {{who}} |
| Low | {{90d}} | {{who}} |

## Triage Workflow

1. Finding detected by scanner.
2. Triage owner: {{team/person}}.
3. Classify: true positive / false positive / accepted risk.
4. True positive: create ticket, assign owner, set SLA deadline.
5. False positive: suppress with documented reason.
6. Accepted risk: document in risk register, set review date.

## Security Regression Tests

| Past Vulnerability | Test Location | Status |
|-------------------|---------------|--------|
| {{VULN-ID: description}} | {{tests/security/test_file.py}} | {{active}} |

## Reporting

- **Dashboard**: {{location or tool}}
- **Report cadence**: {{weekly / sprint / monthly}}
- **Metrics tracked**: mean time to remediate, open count by severity, scan coverage
- **Stakeholders**: {{list}}

## Review Schedule

- Tool configuration review: {{quarterly}}
- Suppression list review: {{quarterly}}
- SLA compliance review: {{monthly}}
- Full pipeline audit: {{annually}}
