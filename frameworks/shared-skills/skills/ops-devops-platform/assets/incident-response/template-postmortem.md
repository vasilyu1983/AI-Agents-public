# Incident Postmortem Template

*Purpose: Capture facts, root cause, and corrective actions after SEV incidents (blameless).*

## When to Use

- Any production incident with customer impact or SLO burn
- SEV-1 / SEV-2 (required), SEV-3 (recommended)

---

## Core

## Template

## Summary

- Incident ID:
- Start/End time (timezone):
- Detection source (alert, customer report, internal):
- Severity:
- Services/systems impacted:
- Customer impact summary:
- SLO/SLI impact (error budget burn, if applicable):
- Primary on-call / incident commander:

## Timeline

| Time       | Event/Action            |
|------------|------------------------|
| 00:03 UTC  | Alert fired            |
| 00:05 UTC  | On-call responded      |
| 00:10 UTC  | Escalation paged       |
| ...        | ...                    |

## Impact (What Users Experienced)

- User/business impact:
- Scope (tenants/regions/features):
- Duration and peak impact window:
- Data impact: none / delayed / incorrect / lost (explain):

## Detection and Response

- Detection quality (actionable? noisy? missing signal?):
- Triage notes (first hypotheses and what was ruled out):
- Mitigation steps (what stopped the bleeding):
- Recovery steps (what restored normal service):

## Root Cause (Why It Happened)

- Trigger event:
- Proximate cause:
- Contributing factors (tech/process/people/systemic):
- Why existing controls failed (tests, monitors, reviews, guardrails):

## Remediation

- Immediate fix (already done):
- Long-term fix (planned):
- Rollback strategy (if fix causes issues):

## Lessons Learned

- What worked:
- What didn’t:
- Documentation/process gaps:

## Action Items

| Owner    | Task/Follow-up        | Due Date   |
|----------|----------------------|------------|
| Alice    | Update runbook       | 2024-05-15 |
| Bob      | Add alert for X      | 2024-05-18 |
| ...      | ...                  | ...        |

## Evidence and References

- Dashboards:
- Logs/traces:
- Deployments/changes during window:
- Related incidents:

## Quality Checklist (Gate to Close)

- [ ] Blameless review
- [ ] Action items have owners and due dates
- [ ] Customer communication completed (if applicable)
- [ ] Runbooks/docs updated
- [ ] Monitoring/alerting gaps addressed

---

## Optional: AI/Automation

- Summarize timeline from incident channel and logs (human-verified)
- Cluster alerts and propose contributing factors (human-validated)
- Draft action items and owners (human-approved)

### Bounded Claims

- Automation can miss context and nuance; humans own conclusions and commitments.
