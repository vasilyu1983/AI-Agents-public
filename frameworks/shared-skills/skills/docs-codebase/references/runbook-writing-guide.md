# Runbook Writing Guide

How to write operational runbooks that work at 3 AM under pressure.

---

## Runbook Types

| Type | Trigger | Example |
|------|---------|---------|
| **Incident response** | Alert fires or user report | "Database replication lag > 30s" |
| **Deployment** | Scheduled release | "Deploy payments-service to production" |
| **Maintenance** | Scheduled window | "Rotate TLS certificates" |
| **Rollback** | Failed deployment or regression | "Rollback payments-service to previous version" |
| **Disaster recovery** | Major outage or data loss | "Restore database from backup" |

Every alert in your monitoring system should link to a runbook. If an alert has no runbook, either write one or delete the alert.

---

## Standard Structure

Every runbook follows the same skeleton. Consistency matters more than cleverness.

```markdown
# [Runbook Title]

**Last tested:** YYYY-MM-DD | **Owner:** [Team] | **Duration:** [X min] | **Severity:** [Critical/High/Medium]

## Prerequisites
- [ ] Access to [system/tool]
- [ ] Permissions: [specific role or group]

## Steps

### 1. [Action verb] — [What this accomplishes]
[exact command]
**Expected:** [output]
**If this fails:** [recovery action or escalation]

### 2. [Next step] ...

## Verification
- [ ] [Check 1]
- [ ] [Check 2]

## Rollback
[How to undo if the procedure made things worse]

## Escalation
| Condition | Contact | Channel |
|-----------|---------|---------|
| [condition] | [name/team] | [Slack/phone/PagerDuty] |
```

---

## Writing for 3 AM

The reader is tired, stressed, and possibly unfamiliar with this system. Write accordingly.

**Do:**
- Number every step. No prose between steps unless it is a decision point.
- Use exact commands. Copy-pasteable, with placeholders clearly marked: `[CLUSTER_NAME]`.
- State expected output after every command. The reader needs to know they are on the right track.
- Provide "if this fails" after every step. Do not assume the happy path.
- Use bold for decision points: **If the output shows X, go to step 5. Otherwise, continue.**

**Avoid:**
- Background explanations. Link to architecture docs instead.
- Ambiguous language: "you may need to", "consider", "it depends".
- Multiple options without a recommendation. Pick the default path.
- Jargon without definition. The on-call engineer may be from a different team.

**Placeholder convention:** Use `[ALL_CAPS_WITH_UNDERSCORES]` for values the reader must fill in (e.g., `kubectl rollout restart deployment/[SERVICE_NAME] -n [NAMESPACE]`). List all placeholders and their sources in Prerequisites.

---

## Runbook Testing

An untested runbook is a guess, not a procedure.

**Testing methods:**

| Method | Frequency | Purpose |
|--------|-----------|---------|
| **Dry run** | After every edit | Walk through steps without executing destructive commands |
| **Game day** | Quarterly | Execute the full runbook in a staging environment |
| **Tabletop exercise** | Monthly | Team talks through the runbook verbally, identifies gaps |
| **Chaos engineering** | Quarterly | Inject the failure, execute the runbook for real |

**Dry run checklist:**
- [ ] Every command is syntactically valid
- [ ] Every placeholder has a documented source
- [ ] Every "expected output" matches current system behavior
- [ ] Every escalation contact is still correct
- [ ] Rollback steps have been reviewed

**After each test, update the "Last tested" date at the top of the runbook.**

---

## Ownership and Review Cadence

| Event | Action |
|-------|--------|
| Runbook created | Assign owner (team, not individual) |
| Every incident that uses a runbook | Update with lessons learned within 48 hours |
| Quarterly review | Owner verifies all steps, contacts, and outputs are current |
| Team member leaves | Transfer ownership explicitly; do not leave orphaned runbooks |
| Service architecture changes | Review all runbooks for affected service |

**Ownership rule:** If no team claims a runbook, escalate to engineering management. Orphaned runbooks are a reliability risk.

---

## Integration with Incident Management

Link runbooks directly into alerting and incident tools. Add the runbook URL to every alert's `runbook_url` field (PagerDuty, OpsGenie, Grafana).

**Example alert config:**

```yaml
alerts:
  - name: "Database replication lag > 30s"
    severity: critical
    runbook_url: "https://wiki.internal/runbooks/db-replication-lag"
    escalation_policy: "database-team"
```

**Incident channel first message:** Post severity, runbook link, and on-call name within 2 minutes. Do not make responders search for the runbook.

---

## Runbook Quality Checklist

Use before publishing or during quarterly review.

- [ ] Title is specific; last tested date is within 90 days
- [ ] Owner assigned; estimated duration stated
- [ ] Prerequisites and required access listed
- [ ] Every step numbered, starts with action verb, has copy-pasteable command
- [ ] Placeholders marked with `[ALL_CAPS]` and documented in prerequisites
- [ ] Expected output follows every command
- [ ] "If this fails" present for each step
- [ ] Rollback section exists and is tested
- [ ] Escalation contacts are current
- [ ] No credentials or secrets hardcoded
- [ ] Linked from the corresponding alert
- [ ] Reviewed after every incident that used it

---

## Anti-Patterns

- **Untested runbooks.** A runbook that has never been executed may contain wrong commands or stale outputs. Test or delete.
- **Wall of prose.** Runbooks are step-by-step procedures, not documentation. Remove paragraphs that do not guide the next action.
- **Missing rollback.** Every procedure that changes production state needs an undo path. If impossible, state that and document the blast radius.
- **Stale escalation contacts.** A disconnected phone number during an incident wastes critical minutes. Verify quarterly.
- **Credentials in the runbook.** Never hardcode secrets. Reference a vault path instead.
- **One runbook for everything.** Split into one runbook per alert or procedure. Keep each focused.
- **No link from the alert.** Every alert must include a `runbook_url`. Do not make responders search.

---

## Related Resources

- [production-gotchas-guide.md](production-gotchas-guide.md) - Documenting known operational issues
- [documentation-testing.md](documentation-testing.md) - Automated verification of doc accuracy
- [contributing-guide-standards.md](contributing-guide-standards.md) - Review and ownership patterns
