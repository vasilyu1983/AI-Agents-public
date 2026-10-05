# {{SERVICE_NAME}} Runbook

> **Owner:** {{TEAM_OR_INDIVIDUAL_OWNER}}
> **Last verified:** {{LAST_VERIFIED_DATE}}
> **Review cadence:** {{REVIEW_CADENCE}} (e.g., quarterly, after each incident)
> **Runbook status:** {{STATUS}} (active | draft | deprecated)

---

## Service Overview

| Field | Value |
|---|---|
| **Service name** | {{SERVICE_NAME}} |
| **Short description** | {{ONE_LINE_DESCRIPTION}} |
| **Primary owner** | {{OWNER_NAME}} ({{OWNER_EMAIL_OR_SLACK}}) |
| **Secondary owner / backup** | {{BACKUP_OWNER}} |
| **Repo** | {{REPO_URL}} |
| **Deploy pipeline** | {{CI_CD_LINK}} |
| **Dashboards** | {{DASHBOARD_URL}} |
| **Logs** | {{LOG_AGGREGATION_URL}} |
| **Alerts** | {{ALERTING_PLATFORM_LINK}} |

---

## SLOs

| Metric | Target | Measurement window |
|---|---|---|
| Availability | {{SLO_AVAILABILITY}} % (e.g., 99.9%) | {{WINDOW}} (e.g., rolling 30d) |
| Latency (p99) | < {{SLO_LATENCY_P99}} ms | {{WINDOW}} |
| Error rate | < {{SLO_ERROR_RATE}} % | {{WINDOW}} |

Error budget calculation: `(1 - target_availability) * window_minutes`. At 99.9% over 30 days → 43.2 minutes/month.

---

## Quick Diagnostics

Run these checks first on any page or alert before going deeper.

```bash
# 1. Is the service up?
curl -sf {{HEALTH_ENDPOINT_URL}} || echo "HEALTH CHECK FAILED"

# 2. Recent error rate (last 15 min)
{{LOG_QUERY_OR_CLI_COMMAND_FOR_ERRORS}}

# 3. Resource pressure (CPU / memory)
{{RESOURCE_CHECK_COMMAND}}

# 4. Downstream dependencies alive?
{{DEPENDENCY_HEALTH_COMMAND}}
```

Replace placeholder commands with real CLI invocations for your stack. Keep this section runnable from a terminal with standard credentials.

---

## Common Alerts → Response

### Alert: {{ALERT_NAME_1}}

**What it means:** {{ALERT_DESCRIPTION_1}}

**Severity:** {{P1 | P2 | P3}}

**Triage steps:**
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}

**Resolution:** {{EXPECTED_RESOLUTION}}

**Escalate if:** {{ESCALATION_CONDITION}} (e.g., persists > 15 min after step 3)

---

### Alert: {{ALERT_NAME_2}}

**What it means:** {{ALERT_DESCRIPTION_2}}

**Severity:** {{P1 | P2 | P3}}

**Triage steps:**
1. {{STEP_1}}
2. {{STEP_2}}

**Resolution:** {{EXPECTED_RESOLUTION}}

**Escalate if:** {{ESCALATION_CONDITION}}

---

<!-- Add more alert blocks as needed. One block per distinct alert name. -->

---

## Escalation Path

| Level | Contact | When to escalate | How |
|---|---|---|---|
| On-call engineer | {{ONCALL_ROTATION_LINK}} | Any P1; P2 unresolved > 30 min | PagerDuty / Slack `{{ONCALL_CHANNEL}}` |
| Team lead | {{TEAM_LEAD_NAME}} | P1 customer impact; SLO breach | Slack DM + phone |
| Director / Incident Commander | {{DIRECTOR_NAME}} | Declared incident; data loss risk | Phone + incident bridge `{{BRIDGE_LINK}}` |

**Incident declaration threshold:** {{DECLARATION_THRESHOLD}} (e.g., P1 unresolved > 15 min or user-visible data loss).

---

## Rollback Procedure

Use this procedure when a bad deploy needs to be reverted.

**Prerequisites:** You have deploy pipeline access and the prior release tag `{{PREVIOUS_STABLE_TAG}}`.

```bash
# Step 1: Identify the last known-good deploy
{{COMMAND_TO_LIST_RECENT_DEPLOYS}}

# Step 2: Pin the rollback target
ROLLBACK_TAG={{PREVIOUS_STABLE_TAG}}

# Step 3: Trigger rollback
{{ROLLBACK_COMMAND_OR_PIPELINE_LINK}}

# Step 4: Verify health after rollback
curl -sf {{HEALTH_ENDPOINT_URL}} && echo "Rollback healthy"

# Step 5: Confirm error rate returning to baseline (wait 5 min)
{{LOG_QUERY_OR_CLI_COMMAND_FOR_ERRORS}}
```

**Expected rollback time:** {{ROLLBACK_DURATION}} (e.g., 3–7 minutes).

**Do not rollback if:** {{ROLLBACK_EXCEPTION}} (e.g., rollback would undo a database migration — contact DBA first).

---

## Dependencies

| Dependency | Type | Owner | What breaks if it is down |
|---|---|---|---|
| {{DEP_NAME_1}} | {{upstream \| downstream \| sidecar}} | {{DEP_OWNER_1}} | {{FAILURE_IMPACT_1}} |
| {{DEP_NAME_2}} | {{upstream \| downstream \| sidecar}} | {{DEP_OWNER_2}} | {{FAILURE_IMPACT_2}} |

**Circuit-breaker behavior:** {{DESCRIBE_CIRCUIT_BREAKER_OR_FALLBACK}} (e.g., "falls back to cached response for up to 30 s").

---

## Postmortem Links

| Date | Incident | Link | Key fix |
|---|---|---|---|
| {{INCIDENT_DATE_1}} | {{INCIDENT_TITLE_1}} | {{POSTMORTEM_LINK_1}} | {{KEY_FIX_1}} |
| {{INCIDENT_DATE_2}} | {{INCIDENT_TITLE_2}} | {{POSTMORTEM_LINK_2}} | {{KEY_FIX_2}} |

Add new rows after each postmortem is published. Do not summarize — link directly to the canonical postmortem document.

---

## Additional Notes

{{ANY_SERVICE_SPECIFIC_CONTEXT_THAT_DOES_NOT_FIT_ABOVE}}

Examples of useful additions:
- Known flaky behaviors and safe workarounds.
- Feature flags that affect this service and how to toggle them.
- Scheduled maintenance windows.
- Compliance or data-sensitivity notes (e.g., "this service processes PII — do not log request bodies").
