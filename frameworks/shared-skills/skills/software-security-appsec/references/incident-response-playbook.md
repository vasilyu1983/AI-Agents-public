# Security Incident Response Playbook (Jan 2026)

Comprehensive incident response procedures covering team structure, detection, containment, evidence handling, communication, remediation, recovery, and post-incident review. Designed for software teams from seed-stage startups to enterprise.

---

## IR Team Composition and Roles

Every incident needs clear ownership. Scale team size to incident severity.

| Role | Responsibility | Who (Typical) |
|------|---------------|---------------|
| **Incident Commander (IC)** | Owns decision authority, coordinates response, sets priorities | Engineering manager, senior SRE, CISO |
| **Technical Lead** | Investigates root cause, directs containment and remediation | Senior engineer with domain knowledge |
| **Communications Lead** | Drafts internal/external messaging, manages stakeholder updates | Head of comms, product manager, legal |
| **Scribe** | Records timeline, decisions, actions in real time | Any team member |
| **Subject Matter Expert** | Provides domain-specific knowledge (e.g., auth, infra, data) | Relevant engineer or architect |

### Escalation Contact Sheet

Maintain a living document with:

- Primary and backup for each role
- Phone numbers (not just Slack handles)
- Timezone coverage
- External contacts: legal counsel, cyber insurance broker, forensics firm
- Regulatory contacts: DPA (GDPR), state AG offices (US breach laws)

```text
TEMPLATE:
Role                 | Primary          | Backup           | Phone
Incident Commander   | [Name]           | [Name]           | +1-XXX-XXX-XXXX
Technical Lead       | [Name]           | [Name]           | +1-XXX-XXX-XXXX
Communications Lead  | [Name]           | [Name]           | +1-XXX-XXX-XXXX
Legal Counsel        | [Firm/Name]      | [Firm/Name]      | +1-XXX-XXX-XXXX
Forensics Retainer   | [Firm]           | —                | +1-XXX-XXX-XXXX
Cyber Insurance      | [Broker/Carrier] | —                | +1-XXX-XXX-XXXX
```

---

## Detection and Triage

### Severity Classification

| Severity | Definition | Response Time | Escalation |
|----------|-----------|---------------|------------|
| **P0 — Critical** | Active data breach, credential compromise affecting production, ransomware, supply chain attack | Immediate (< 15 min) | IC + CISO + Legal + Exec |
| **P1 — High** | Confirmed vulnerability actively exploited, unauthorized access detected, customer PII exposed | < 1 hour | IC + Technical Lead + Comms |
| **P2 — Medium** | Vulnerability discovered (not exploited), suspicious activity requiring investigation, failed intrusion attempt | < 4 hours | Technical Lead + Security team |
| **P3 — Low** | Minor policy violation, low-risk vulnerability, security tool misconfiguration | < 24 hours | Security team standard triage |

### Triage Decision Tree

```text
Alert received:
  ├─ Is there active data exfiltration?
  │   └─ YES → P0, activate IR team immediately
  ├─ Are production credentials compromised?
  │   └─ YES → P0, begin secret rotation
  ├─ Is unauthorized access confirmed?
  │   ├─ To customer data → P0
  │   └─ To internal systems → P1
  ├─ Is a known vulnerability being exploited?
  │   └─ YES → P1
  ├─ Suspicious activity, no confirmed impact?
  │   └─ P2, investigate within 4 hours
  └─ Policy violation or configuration issue?
      └─ P3, standard workflow
```

### Detection Sources

| Source | What It Catches | Priority |
|--------|----------------|----------|
| SIEM alerts (Splunk, Datadog, ELK) | Anomalous patterns, correlation rules | Automated, high priority |
| WAF/IDS (Cloudflare, AWS WAF) | Known attack signatures, rate anomalies | Automated |
| Dependency scanner (Snyk, Dependabot) | Vulnerable packages | Automated, P2-P3 |
| Bug bounty / responsible disclosure | External findings | Manual, severity varies |
| Customer report | Data they should not see, account compromise | Manual, triage immediately |
| Employee report | Suspicious email, credential phishing | Manual, triage within 1 hour |
| Code review finding | Hardcoded secrets, auth bypass | Manual, P2-P3 |

---

## Containment Procedures by Incident Type

### Credential Leak

```text
IMMEDIATE (< 30 minutes):
1. Identify scope: which credentials, where leaked (GitHub, logs, public repo)
2. Rotate all affected credentials:
   - API keys → generate new, revoke old
   - Database passwords → rotate, update connection strings
   - JWT signing keys → rotate, invalidate all active sessions
   - SSH keys → regenerate and redeploy
3. Audit access logs for compromised credential usage
4. Check for unauthorized changes made with compromised credentials
5. Force logout all sessions if user-facing tokens compromised

FOLLOW-UP (< 4 hours):
6. Enable MFA on affected accounts if not already active
7. Review and restrict credential scope (least privilege)
8. Scan entire codebase and CI/CD for additional hardcoded secrets
9. Implement or verify secret scanning (GitHub Advanced Security, GitLeaks)
```

### Data Breach

```text
IMMEDIATE (< 15 minutes):
1. Determine data type: PII, financial, health, credentials
2. Identify affected records count and user population
3. Preserve evidence (do NOT delete logs or affected data)
4. Block the attack vector (disable endpoint, block IP, revoke access)
5. Engage legal counsel (triggers notification obligations)

CONTAINMENT (< 2 hours):
6. Isolate affected systems (network segmentation)
7. Capture forensic images of affected servers/databases
8. Review access logs for data exfiltration timeline
9. Determine if breach is ongoing or contained
10. Begin notification timeline tracking (GDPR: 72 hours starts now)

COMMUNICATION (< 24 hours):
11. Internal stakeholder briefing
12. Regulatory notification assessment (see Legal section below)
13. Customer notification preparation
14. Media holding statement if public exposure likely
```

### DDoS Attack

```text
IMMEDIATE:
1. Confirm DDoS vs traffic spike (check source distribution)
2. Activate CDN/WAF DDoS protection (Cloudflare Under Attack, AWS Shield)
3. Enable aggressive rate limiting
4. Scale infrastructure if auto-scaling available
5. Block identified attack IPs/ranges at edge

SUSTAINED ATTACK:
6. Engage CDN/hosting provider support
7. Implement geographic filtering if attack is region-specific
8. Enable CAPTCHA on critical endpoints
9. Consider temporary maintenance mode for non-critical services
10. Monitor for secondary attacks (DDoS as distraction)
```

### Supply Chain Compromise

```text
IMMEDIATE:
1. Identify compromised package, version, and scope
2. Check SBOM: which services use the affected package?
3. Pin to last known good version
4. Block deployment pipeline
5. Scan for indicators of compromise (IOCs) specific to the package

CONTAINMENT:
6. Audit what the compromised package could access (env vars, network, filesystem)
7. Rotate any credentials the package could have exfiltrated
8. Review build artifacts for tampering
9. Check for persistence mechanisms (cron jobs, modified configs)
10. Report to package registry (npm, PyPI) and relevant CERT
```

---

## Evidence Collection

### Log Preservation

```bash
# Immediately preserve logs before rotation or deletion
# Application logs
aws s3 cp /var/log/app/ s3://incident-evidence/INC-2026-001/app-logs/ --recursive

# Access logs
aws s3 cp /var/log/nginx/ s3://incident-evidence/INC-2026-001/access-logs/ --recursive

# Database audit logs
pg_dump --table=audit_log > incident_audit_$(date +%Y%m%d_%H%M%S).sql

# Cloud provider audit trail
aws cloudtrail lookup-events \
  --start-time "2026-01-15T00:00:00Z" \
  --end-time "2026-01-16T00:00:00Z" \
  > cloudtrail_events.json
```

### Forensic Imaging

| Asset Type | Tool | Procedure |
|------------|------|-----------|
| Cloud VM | Cloud provider snapshot | Create snapshot before any changes; tag with incident ID |
| Container | `docker commit` + `docker save` | Capture running state; preserve image layers |
| Database | Point-in-time snapshot | Use cloud provider snapshot; do not rely on logical backup alone |
| Memory | `LiME` (Linux), cloud memory capture | Capture before reboot; volatile evidence lost on power cycle |

### Chain of Custody

Every piece of evidence must have:

```text
Evidence ID: INC-2026-001-E003
Description: Application server access logs, Jan 15-16 2026
Collected by: [Name], [Role]
Collection time: 2026-01-16T14:30:00Z
Collection method: aws s3 cp from production server
Hash (SHA-256): a3f2b1c4d5e6f7...
Storage location: s3://incident-evidence/INC-2026-001/
Access restricted to: IR team members only
```

---

## Communication Templates

### Internal Stakeholder Notification (P0/P1)

```text
SUBJECT: [SECURITY INCIDENT] INC-2026-XXX — [Brief Description]

SEVERITY: P[X]
STATUS: [Investigating | Contained | Remediated]
INCIDENT COMMANDER: [Name]

WHAT HAPPENED:
[1-2 sentence description of what was detected]

CURRENT IMPACT:
- Users affected: [count or scope]
- Data involved: [type of data, if known]
- Services affected: [list]

CURRENT ACTIONS:
1. [Action taken or in progress]
2. [Action taken or in progress]

NEXT UPDATE: [Time] or in [X] hours
BRIDGE: [Slack channel / video link]

DO NOT:
- Discuss externally until Communications Lead approves
- Share details outside the listed distribution
```

### Customer Notification (Data Breach)

```text
SUBJECT: Important Security Notice from [Company]

Dear [Customer],

We are writing to inform you of a security incident that may have
affected your account information.

WHAT HAPPENED:
[Clear, factual description. Avoid jargon.]

WHAT INFORMATION WAS INVOLVED:
[Specific data types: email, name, etc. Be precise.]

WHAT WE ARE DOING:
[Actions taken to contain and remediate]

WHAT YOU CAN DO:
- [Specific action: change password, enable MFA, monitor accounts]
- [Specific action: contact information for questions]

We sincerely apologize for this incident. We are committed to
protecting your information and have taken the following steps to
prevent a recurrence: [brief list].

For questions: [dedicated support email/phone]
Incident details: [status page URL]

[Name], [Title]
```

### Regulatory Notification Checklist

```text
REGULATION          | DEADLINE        | REQUIRED CONTENT
GDPR (EU/EEA)      | 72 hours to DPA | Nature, categories, approx records,
                    |                 | consequences, measures taken
CCPA/CPRA (CA)     | "Expedient"     | Categories, rights, what happened
HIPAA (US health)  | 60 days (>500)  | Description, types, steps to protect,
                    | annual (<500)   | investigation, contact, mitigation
PCI DSS            | Immediately     | Card brands, acquirer, forensic
                    |                 | investigation details
SEC (public co.)   | 4 business days | Material cybersecurity incident
                    | after materiality| description
State breach laws  | Varies by state | See state-specific requirements
```

---

## Remediation Checklists

### Secret Rotation

- [ ] Identify all secrets that may be compromised
- [ ] Generate new secrets (strong entropy, proper length)
- [ ] Update secrets in secrets manager (not in code or CI/CD variables)
- [ ] Deploy updated configuration to all affected services
- [ ] Verify services function correctly with new secrets
- [ ] Revoke old secrets (after confirming new ones work)
- [ ] Audit secret access logs for unauthorized use during exposure window

### Access Revocation

- [ ] Identify compromised accounts or sessions
- [ ] Force logout all active sessions for affected accounts
- [ ] Require password reset with MFA verification
- [ ] Revoke OAuth tokens and API keys for affected users
- [ ] Review and remove unauthorized access grants
- [ ] Audit privilege escalation attempts

### Patch Deployment

- [ ] Identify vulnerable code or dependency
- [ ] Develop or obtain patch
- [ ] Test patch in staging environment
- [ ] Deploy to production (hotfix pipeline)
- [ ] Verify fix addresses the vulnerability
- [ ] Scan for similar vulnerabilities elsewhere in codebase
- [ ] Update WAF rules if applicable (virtual patching)

---

## Recovery Procedures

### Service Restoration

```text
RECOVERY SEQUENCE:
1. Verify containment is complete (no ongoing attack)
2. Deploy patched/remediated code
3. Restore from clean backups if data was corrupted
4. Gradually re-enable services (canary → staged → full)
5. Monitor closely for 24-48 hours post-restoration
6. Verify all security controls are active
7. Confirm logging and alerting are functioning
```

### Monitoring Enhancement

After every incident, add or improve monitoring:

| What to Add | Why | Tool |
|-------------|-----|------|
| Alert for the specific attack pattern | Catch recurrence | SIEM rule |
| Anomaly detection on affected data store | Detect similar attacks | Datadog, CloudWatch |
| Canary tokens in sensitive locations | Early warning for access | canarytokens.org |
| Enhanced logging on affected endpoints | Deeper visibility | Application logging |
| Failed auth rate alert | Brute-force detection | Rate limiter + alerting |

---

## Post-Incident Review (Blameless Postmortem)

### Template

```text
INCIDENT POSTMORTEM: INC-2026-XXX
Date: [Date]
Duration: [Start] to [Resolved]
Severity: P[X]
Authors: [IR team members]

SUMMARY
[2-3 sentence overview of what happened and impact]

TIMELINE (UTC)
[Time] — [Event]
[Time] — [Event]
[Time] — [Event]
(Include detection, escalation, containment, remediation, resolution)

IMPACT
- Users affected: [count]
- Data exposed: [type and scope]
- Downtime: [duration]
- Financial impact: [estimate if available]

ROOT CAUSE
[Technical explanation of the vulnerability or failure]

CONTRIBUTING FACTORS
1. [Factor that enabled or worsened the incident]
2. [Factor]

WHAT WENT WELL
- [Effective detection, fast response, good communication]

WHAT COULD BE IMPROVED
- [Gaps in detection, slow escalation, unclear ownership]

ACTION ITEMS
| ID | Action | Owner | Deadline | Priority |
|----|--------|-------|----------|----------|
| 1  | [Fix]  | [Who] | [When]   | P[X]     |
| 2  | [Fix]  | [Who] | [When]   | P[X]     |

LESSONS LEARNED
[Key takeaways for the broader team]
```

### Postmortem Principles

- **Blameless**: Focus on systems and processes, not individuals
- **Honest**: Document what actually happened, not what should have happened
- **Actionable**: Every finding produces a tracked action item with an owner
- **Shared**: Publish internally (redacted if needed) so the whole org learns
- **Reviewed**: Follow up on action items at 30-day and 90-day marks

---

## Legal and Regulatory Notification Requirements

### GDPR 72-Hour Rule

```text
GDPR Article 33 — Notification to DPA:
- Deadline: 72 hours from awareness of breach
- "Awareness" = when you have reasonable certainty, not when alert fired
- If beyond 72 hours: must explain delay
- If risk to individuals: notify them directly (Article 34)

REQUIRED INFORMATION:
1. Nature of the breach (categories and approx. number of records)
2. Name and contact of DPO
3. Likely consequences
4. Measures taken or proposed to address the breach
```

### US State Breach Notification

| State | Deadline | Threshold | AG Notification |
|-------|----------|-----------|-----------------|
| California (CCPA/CPRA) | "Expedient" (typically 45 days) | Unencrypted PI | > 500 residents |
| New York (SHIELD Act) | "Expedient" | Private information | Any number |
| Texas | 60 days | Sensitive PI | > 250 residents |
| Florida | 30 days | PI | > 500 residents |
| Illinois (PIPA) | "Expedient" | PI | Any number |

**Note**: State laws change frequently. Verify current requirements with legal counsel for each incident.

---

## IR Automation — SOAR Playbooks

Security Orchestration, Automation, and Response (SOAR) can automate repetitive IR tasks.

### Automatable Actions

| Trigger | Automated Action | Tool |
|---------|------------------|------|
| GitHub secret detected | Revoke token, notify owner, create ticket | GitHub Advanced Security + webhook |
| Multiple failed logins (>10 in 5 min) | Temporary IP block, alert security team | WAF rule + SIEM |
| Known malicious IP detected | Block at edge, enrich with threat intel | Cloudflare + threat feed |
| Vulnerability scan finds critical CVE | Create P1 ticket, notify owners, block deploy | Snyk + Jira integration |
| Anomalous data access pattern | Capture session details, alert, prepare for containment | SIEM + SOAR |

### Example: Automated Secret Leak Response

```yaml
# GitHub Actions workflow for leaked secret response
name: Secret Leak Response
on:
  secret_scanning_alert:
    types: [created]

jobs:
  respond:
    runs-on: ubuntu-latest
    steps:
      - name: Get alert details
        id: alert
        uses: actions/github-script@v7
        with:
          script: |
            const alert = context.payload.alert;
            core.setOutput('type', alert.secret_type);
            core.setOutput('location', alert.html_url);

      - name: Create incident ticket
        uses: atlassian/gajira-create@v3
        with:
          project: SEC
          issuetype: Incident
          summary: 'Secret leaked: ${{ steps.alert.outputs.type }}'
          description: |
            A secret of type ${{ steps.alert.outputs.type }} was detected.
            Location: ${{ steps.alert.outputs.location }}
            Action required: Rotate immediately.

      - name: Notify security team
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: 'C0SECURITY'
          slack-message: |
            :rotating_light: Secret leak detected
            Type: ${{ steps.alert.outputs.type }}
            Action: Rotate immediately
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| No documented IR plan | Chaos during real incident | Write and rehearse IR plan quarterly |
| Single point of contact | Unavailable person blocks response | Primary + backup for every role |
| Investigating before containing | Attack continues during analysis | Contain first, investigate second |
| Deleting evidence during cleanup | Cannot determine scope or root cause | Preserve first, then clean |
| Blaming individuals in postmortem | People hide information next time | Blameless postmortem culture |
| Notifying only after full investigation | Regulatory deadlines missed | Start notification clock at awareness |
| No IR rehearsal | First real incident exposes all gaps | Quarterly tabletop exercises |
| Shared credentials for IR tools | Audit trail impossible | Individual accounts for all IR systems |

---

## References

- [NIST SP 800-61r3 — Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [SANS Incident Handler's Handbook](https://www.sans.org/white-papers/33901/)
- [GDPR Article 33 — Notification of a personal data breach](https://gdpr-info.eu/art-33-gdpr/)
- [CISA Incident Reporting](https://www.cisa.gov/reporting)
- [PagerDuty Incident Response Documentation](https://response.pagerduty.com/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and incident response patterns section
- [security-business-value.md](security-business-value.md) — Breach cost data and IR team ROI
- [supply-chain-security.md](supply-chain-security.md) — Supply chain incident response procedures
- [cryptography-standards.md](cryptography-standards.md) — Key rotation procedures referenced in remediation
- [common-vulnerabilities.md](common-vulnerabilities.md) — Vulnerability patterns that trigger incidents
