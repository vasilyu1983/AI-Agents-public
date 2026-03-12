# SBOM & Vulnerability Triage Checklist

Use this checklist to make vulnerability handling repeatable, auditable, and fast.

---

## Core

### 1) Intake

- [ ] Alert source: OSV / GHAS / Snyk / vendor advisory / internal pentest
- [ ] Package + version range affected
- [ ] Direct vs transitive dependency identified
- [ ] Runtime vs dev-only dependency confirmed
- [ ] SBOM available for the affected build artifact (commit SHA + build ID)

### 2) Exposure and Exploitability

- [ ] Is the vulnerable code path reachable in your product?
- [ ] Is the package shipped to production (or only used in CI/dev)?
- [ ] Is there a known exploit or active exploitation in the wild?
- [ ] Privileges required: unauthenticated / authenticated / admin / local only
- [ ] Data impact: confidentiality / integrity / availability

### 3) Severity and Prioritization

- [ ] Severity score captured (CVSS where available) and validated against your context
- [ ] Priority assigned based on exposure + exploitability (not score alone)
- [ ] Owner assigned (team + on-call contact)
- [ ] SLA applied (critical/high/medium/low) with due date

### 4) Remediation Options (Pick One)

- [ ] Upgrade to fixed version
- [ ] Patch via override/resolution (temporary; document removal date)
- [ ] Mitigate via configuration (disable feature / reduce surface)
- [ ] Isolate/contain (WAF rules, sandbox, permission tightening)
- [ ] Risk accept (requires explicit approval and a review date)

### 5) Verification

- [ ] Fix verified in dependency graph (lockfile, `npm ls`, `pipdeptree`, `cargo tree`)
- [ ] Build + tests passed (unit + integration as applicable)
- [ ] Rescan confirms vulnerability resolved
- [ ] Runtime verification done for critical issues (staging/canary)

### 6) Documentation and Follow-Up

- [ ] Incident log entry created (ticket ID, affected versions, fix commit)
- [ ] If secrets may be exposed, rotate and invalidate credentials
- [ ] If override used, create follow-up to remove it
- [ ] If root cause is process gap, add guardrail (policy, CI gate, training)

---

## Do / Avoid

### Do

- Do use SBOMs to answer “where is this running?” quickly
- Do treat transitive overrides as temporary and tracked debt
- Do combine vuln triage with rollout safety (canary, rollback, monitoring)

### Avoid

- Avoid accepting risk without a time-bounded review date
- Avoid upgrading blindly without verifying the vulnerability is actually removed
- Avoid using severity score alone to set priority

---

## Optional: AI/Automation

- Map alerts to SBOMs/builds and open tickets automatically (human-owned)
- Summarize advisory text into a 1-page triage brief (human-validated)
- Suggest remediation order by reachability and blast radius (human-approved)

### Bounded Claims

- Automation cannot reliably determine runtime reachability without instrumentation.
- Approval, prioritization, and risk acceptance remain human decisions.
