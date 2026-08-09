# Incident Response Playbook Template

Production-ready incident response workflow for critical system failures.

---

## Incident Severity Levels

```
P0 - CRITICAL (Complete System Down)
- Service completely unavailable
- Data loss or corruption
- Security breach
- Response time: < 5 minutes
- Resolution target: < 2 hours

P1 - HIGH (Major Feature Broken)
- Core functionality unavailable
- Significant user impact (>25%)
- Revenue-generating feature down
- Response time: < 15 minutes
- Resolution target: < 4 hours

P2 - MEDIUM (Degraded Performance)
- Performance degradation
- Secondary feature broken
- Moderate user impact (5-25%)
- Response time: < 1 hour
- Resolution target: < 24 hours

P3 - LOW (Minor Issue)
- Cosmetic issues
- Low user impact (<5%)
- Workaround available
- Response time: < 4 hours
- Resolution target: < 1 week
```

---

## Phase 1: Detection & Triage (0-15 minutes)

### Detection Checklist

```
[ ] Alert received or user report
    Time: _______________
    Source: _______________

[ ] Verify issue is real (not false alarm)
    [ ] Check multiple data sources
    [ ] Reproduce if possible
    [ ] Confirm user impact

[ ] Assess initial severity
    Current severity: [ ] P0 [ ] P1 [ ] P2 [ ] P3

[ ] Determine scope
    Affected services: _______________
    Affected users: _______________
    Geographic regions: _______________
```

### Initial Actions

```
[ ] Create incident ticket
    Ticket #: _______________
    Title: _______________

[ ] Start incident log (timeline)
    Start time: _______________

[ ] Notify on-call engineer
    Engineer: _______________
    Notified at: _______________

[ ] Open incident channel (Slack/Teams)
    Channel: #incident-_______________
```

---

## Phase 2: Assembly & Communication (15-30 minutes)

### Assemble Response Team

```
[ ] Incident Commander (IC)
    Name: _______________
    Role: Coordinate response, make decisions

[ ] Technical Lead
    Name: _______________
    Role: Lead investigation and remediation

[ ] Communications Lead
    Name: _______________
    Role: Stakeholder updates, customer communication

[ ] Subject Matter Experts (as needed)
    [ ] Database expert: _______________
    [ ] Security expert: _______________
    [ ] Infrastructure expert: _______________
    [ ] Domain expert: _______________
```

### Communication Setup

```
[ ] Establish communication norms
    [ ] All communication in incident channel
    [ ] No side conversations
    [ ] Status updates every 30 minutes minimum
    [ ] Use clear, objective language

[ ] Create status page (if customer-facing)
    URL: _______________

[ ] Notify stakeholders
    [ ] Engineering leadership
    [ ] Product team
    [ ] Customer support
    [ ] Sales (if B2B)
    [ ] External customers (if needed)
```

---

## Phase 3: Investigation (Parallel with Mitigation)

### Gather Evidence

```
RECENT CHANGES:
[ ] Check deployment history
    Last deployment: _______________
    Changes: _______________

[ ] Review configuration changes
    Changes: _______________

[ ] Check infrastructure changes
    Changes: _______________

MONITORING DATA:
[ ] Check error rate
    Normal: _______________
    Current: _______________
    Spike started: _______________

[ ] Check latency metrics
    Normal P95: _______________
    Current P95: _______________

[ ] Check resource usage
    CPU: _______________
    Memory: _______________
    Disk: _______________

LOGS:
[ ] Filter logs by time window
    Time window: _______________

[ ] Search for error patterns
    Key errors: _______________

[ ] Find affected request IDs
    Sample request ID: _______________

TRACES:
[ ] Analyze distributed trace
    Trace ID: _______________
    Bottleneck: _______________

EXTERNAL DEPENDENCIES:
[ ] Check third-party status pages
    [ ] AWS Status: _______________
    [ ] Stripe Status: _______________
    [ ] [Other]: _______________

[ ] Test external API connectivity
    Status: _______________
```

### Form Hypothesis

```
HYPOTHESIS 1:
Description: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low
Test: _______________

HYPOTHESIS 2:
Description: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low
Test: _______________

HYPOTHESIS 3:
Description: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low
Test: _______________
```

---

## Phase 4: Mitigation (Immediate Response)

### Decision Tree

```
Is root cause known?
- YES -> Implement targeted fix
  - Can fix be deployed quickly (<10 min)?
    - YES -> Deploy fix
    - NO  -> Consider rollback first
  - Verify fix resolves issue

- NO -> Implement general mitigation
  - Can we rollback recent deployment?
    - YES -> Rollback
    - NO  -> Try other mitigations
  - Can we disable affected feature?
    - Use feature flag to disable
  - Can we route traffic elsewhere?
    - Use load balancer to shift traffic
  - Can we scale resources?
    - Increase replicas/instances
```

### Mitigation Options

```
OPTION 1: ROLLBACK
[ ] Identify last known good version
    Version: _______________

[ ] Execute rollback procedure
    [ ] Update deployment manifest
    [ ] Deploy previous version
    [ ] Verify rollback successful

[ ] Monitor for 15 minutes
    [ ] Error rate decreasing
    [ ] Functionality restored
    [ ] No new issues

OPTION 2: TARGETED FIX
[ ] Implement minimal fix
    Change: _______________

[ ] Test fix in staging
    [ ] Smoke tests pass
    [ ] No regression

[ ] Deploy via canary (if time permits)
    [ ] 10% traffic
    [ ] Monitor for 10 minutes
    [ ] 100% traffic

[ ] Verify fix
    [ ] Error rate normal
    [ ] Functionality restored

OPTION 3: FEATURE DISABLE
[ ] Identify feature flag
    Flag: _______________

[ ] Disable feature
    [ ] Update flag value
    [ ] Verify feature disabled

[ ] Confirm mitigation
    [ ] Error rate reduced
    [ ] System stable

OPTION 4: TRAFFIC ROUTING
[ ] Redirect traffic to backup region/service
    [ ] Update load balancer rules
    [ ] Verify traffic shifted

[ ] Monitor backup capacity
    [ ] Adequate resources
    [ ] Performance acceptable

OPTION 5: SCALE RESOURCES
[ ] Increase capacity
    [ ] Scale replicas: from ___ to ___
    [ ] Increase instance size

[ ] Wait for autoscaling
    [ ] New instances healthy
    [ ] Load distributed

[ ] Verify mitigation
    [ ] Response time improved
    [ ] Error rate reduced
```

---

## Phase 5: Verification & Monitoring

```
[ ] Verify mitigation successful
    [ ] Error rate returned to baseline
    [ ] Latency back to normal
    [ ] Functionality fully restored
    [ ] User reports ceased

[ ] Announce mitigation
    Posted in #incident channel: _______________
    Status page updated: _______________

[ ] Continue monitoring
    [ ] Watch for 30 minutes
    [ ] Check for new errors
    [ ] Verify metrics stable

[ ] Adjust severity if needed
    New severity: [ ] P0 [ ] P1 [ ] P2 [ ] P3
    Reason: _______________
```

---

## Phase 6: Resolution (Permanent Fix)

```
[ ] Root cause identified
    Root cause: _______________

[ ] Implement permanent fix
    Description: _______________

[ ] Test thoroughly
    [ ] Unit tests
    [ ] Integration tests
    [ ] Load tests
    [ ] Manual testing

[ ] Code review
    Reviewer: _______________
    Approved: [ ] Yes [ ] No

[ ] Deploy to staging
    [ ] Smoke tests pass
    [ ] Regression tests pass

[ ] Deploy to production
    [ ] Canary deployment
    [ ] Monitor for 1 hour
    [ ] Full rollout

[ ] Verify resolution
    [ ] No recurrence in 24 hours
    [ ] Metrics stable
    [ ] No related issues

[ ] Close incident
    Closed at: _______________
    Duration: _______________
```

---

## Phase 7: Postmortem (Within 48 hours)

### Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date:** [YYYY-MM-DD]
**Duration:** [X hours Y minutes]
**Severity:** [P0/P1/P2/P3]
**Impact:** [Brief description of user impact]

## Summary

[1-2 paragraph summary of what happened]

## Timeline (All times in UTC)

| Time | Event |
|------|-------|
| HH:MM | Alert triggered: [error rate spike] |
| HH:MM | Incident declared, team assembled |
| HH:MM | Investigation started |
| HH:MM | Hypothesis formed: [description] |
| HH:MM | Mitigation deployed: [rollback/fix] |
| HH:MM | Issue resolved |
| HH:MM | Monitoring confirmed stable |
| HH:MM | Incident closed |

## Root Cause

[Detailed explanation of what caused the incident]

**Technical Details:**
- Component: [service/database/infrastructure]
- Direct cause: [e.g., missing index, null pointer, timeout]
- Contributing factors: [e.g., increased load, configuration error]

## Impact

**Users Affected:** [number or percentage]
**Requests Failed:** [count]
**Data Loss:** [Yes/No - if yes, describe extent]
**Revenue Impact:** [if applicable]
**SLA Breach:** [Yes/No - if yes, credit amount]

## What Went Well

- [e.g., Fast detection via monitoring]
- [e.g., Effective team coordination]
- [e.g., Rollback procedure worked smoothly]

## What Went Wrong

- [e.g., No alerting for this failure mode]
- [e.g., Communication delays]
- [e.g., Insufficient testing before deployment]

## Action Items

| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Add monitoring for [condition] | [Name] | [Date] | High |
| Improve testing for [scenario] | [Name] | [Date] | High |
| Update runbook with [info] | [Name] | [Date] | Medium |
| Add validation for [input] | [Name] | [Date] | Medium |

## Lessons Learned

- [Key takeaway 1]
- [Key takeaway 2]
- [Key takeaway 3]
```

### Postmortem Checklist

```
[ ] Schedule postmortem meeting (within 48 hours)
    Date/Time: _______________
    Attendees: _______________

[ ] Document timeline objectively
    [ ] No blame or finger-pointing
    [ ] Focus on systems, not people
    [ ] Include all relevant events

[ ] Identify root cause(s)
    [ ] Direct cause
    [ ] Contributing factors
    [ ] Systemic issues

[ ] Calculate impact
    [ ] Users affected
    [ ] Duration
    [ ] Revenue impact
    [ ] SLA compliance

[ ] List what went well
    [ ] Successful processes
    [ ] Effective tools
    [ ] Good decisions

[ ] List what went wrong
    [ ] Detection delays
    [ ] Communication gaps
    [ ] Process failures
    [ ] Missing tools/monitoring

[ ] Define action items
    [ ] Each has owner
    [ ] Each has due date
    [ ] Each has priority
    [ ] Each is specific and measurable

[ ] Share widely
    [ ] Engineering team
    [ ] Product team
    [ ] Executive team (if high severity)
    [ ] Public postmortem (if customer-facing)

[ ] Track action items
    [ ] Add to sprint/backlog
    [ ] Review in retrospectives
    [ ] Verify completion
```

---

## Communication Templates

### Initial Alert (Within 5 minutes)

```
INCIDENT ALERT

**Severity:** [P0/P1/P2/P3]
**Title:** [Brief description]
**Status:** Investigating

**Impact:**
- [What is broken]
- [How many users affected]
- [What functionality is unavailable]

**Response:**
- Incident Commander: [Name]
- Investigation started at [HH:MM]

**Next Update:** [HH:MM] or when status changes

**Incident Channel:** #incident-[id]
```

### Status Update (Every 30 minutes)

```
[CHART] INCIDENT UPDATE

**Severity:** [P0/P1/P2/P3]
**Title:** [Brief description]
**Status:** [Investigating / Mitigating / Resolved / Monitoring]

**Current Situation:**
[1-2 sentences on current state]

**Actions Taken:**
- [Action 1]
- [Action 2]

**Next Steps:**
- [Planned action 1]
- [Planned action 2]

**Next Update:** [HH:MM] or when status changes
```

### Resolution Announcement

```
[OK] INCIDENT RESOLVED

**Severity:** [P0/P1/P2/P3]
**Title:** [Brief description]
**Status:** Resolved
**Duration:** [X hours Y minutes]

**Resolution:**
[Brief description of fix]

**Impact Summary:**
- Users affected: [count/percentage]
- Duration: [HH:MM to HH:MM]

**Root Cause:**
[One sentence summary]

**Prevention:**
[What we're doing to prevent recurrence]

**Postmortem:** Will be shared within 48 hours

Thank you to [team members] for the swift response.
```

---

## Roles & Responsibilities

### Incident Commander (IC)

```
PRIMARY RESPONSIBILITIES:
- Declare incident severity
- Assemble response team
- Make executive decisions
- Coordinate communication
- Declare incident resolved

DURING INCIDENT:
- Stay calm and objective
- Delegate tasks clearly
- Track timeline
- Ensure regular status updates
- Manage stakeholder expectations
- Make go/no-go decisions on fixes
```

### Technical Lead

```
PRIMARY RESPONSIBILITIES:
- Lead investigation
- Form and test hypotheses
- Implement fixes
- Verify resolution
- Provide technical updates to IC

DURING INCIDENT:
- Focus on root cause analysis
- Coordinate with subject matter experts
- Make technical recommendations
- Ensure changes are safe
- Verify system stability
```

### Communications Lead

```
PRIMARY RESPONSIBILITIES:
- Draft status updates
- Communicate with stakeholders
- Update status page
- Handle customer inquiries
- Document timeline

DURING INCIDENT:
- Post updates every 30 minutes
- Translate technical details
- Manage expectations
- Maintain communication log
- Coordinate with support team
```

---

## Escalation Paths

### When to Escalate

```
IMMEDIATE ESCALATION (P0):
- Complete system outage
- Data loss or corruption
- Security breach
- Unable to mitigate within 30 minutes

- Page: Director of Engineering
- Page: CTO (after 1 hour)
- Notify: CEO (if customer-facing, after 2 hours)

ESCALATE IF STUCK (any severity):
- No progress after 1 hour
- Need additional expertise
- Require executive decision
- Cross-team coordination needed

- Ask: Senior engineers
- Escalate: Engineering manager
- Loop in: Director (if > 2 hours)
```

---

## Pre-Incident Preparation Checklist

```
[ ] On-call rotation defined
[ ] Escalation paths documented
[ ] Runbooks up to date
[ ] Monitoring and alerting configured
[ ] Incident channel template ready
[ ] Status page configured
[ ] Rollback procedures documented
[ ] Communication templates prepared
[ ] Team trained on incident response
[ ] Postmortem template ready
[ ] Regular incident drills conducted
```

---

> **Remember**: Stay calm, communicate clearly, and focus on resolution. Blameless postmortems lead to better systems.
