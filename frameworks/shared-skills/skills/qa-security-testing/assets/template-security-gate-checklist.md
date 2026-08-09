# Security Gate Checklist: {{PROJECT_NAME}}

## Pre-Merge Gates (Every PR)

- [ ] SAST scan passes (no new high/critical findings)
- [ ] Secret scanning passes (no detected secrets)
- [ ] Dependency audit passes (no critical/high CVEs)
- [ ] IaC scanning passes (if IaC files changed)
- [ ] Security regression tests pass
- [ ] New suppressions have documented justification

## Pre-Deploy Gates (Staging)

- [ ] DAST scan on staging completes with no new high/critical findings
- [ ] Container image scan passes (no critical CVEs)
- [ ] Base image is from approved list and up to date
- [ ] All pre-merge gates were green for included commits
- [ ] Authenticated scan covers protected endpoints

## Release Gates

- [ ] All pre-merge and pre-deploy gates are green
- [ ] No open critical vulnerabilities past SLA
- [ ] No open high vulnerabilities past SLA
- [ ] SBOM generated and archived
- [ ] Vulnerability SLA compliance verified
- [ ] Scheduled DAST scan results reviewed (if due)
- [ ] Dependency license compliance verified

## Incident Response Readiness

- [ ] Secret rotation procedure documented and tested
- [ ] Security contact and escalation path current
- [ ] Incident response runbook accessible
- [ ] Monitoring and alerting configured for security events

## Periodic Review Items

- [ ] Suppression list reviewed this quarter
- [ ] Scanner rules and policies updated
- [ ] Base image policy reviewed
- [ ] SLA targets reviewed against actual performance
- [ ] Security regression test coverage reviewed

## Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Security lead | {{name}} | {{date}} | {{Approved/Blocked}} |
| Engineering lead | {{name}} | {{date}} | {{Approved/Blocked}} |
| Release manager | {{name}} | {{date}} | {{Approved/Blocked}} |
