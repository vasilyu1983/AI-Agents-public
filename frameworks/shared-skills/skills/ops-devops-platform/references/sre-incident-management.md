# SRE Incident Management

*Purpose: Operational patterns for responding to production incidents with defined SLAs, escalation procedures, communication protocols, and blameless postmortems.*

---

## Core Patterns

### Pattern 1: Incident Severity Classification

**Use when:** Triaging alerts and determining response urgency

**Severity Levels:**

**SEV-1 (Critical):**
- **Impact:** Complete service outage or data loss affecting >50% users
- **Examples:** Payment system down, database corruption, security breach
- **SLA Response:** <5 minutes acknowledgment, <15 minutes MTTR target
- **Escalation:** Immediate page to on-call SRE + Engineering Manager
- **Communication:** Public status page updated every 15 minutes

**SEV-2 (High):**
- **Impact:** Degraded service affecting <50% users or critical feature down
- **Examples:** Checkout flow error rate >5%, API latency P99 >2s
- **SLA Response:** <15 minutes acknowledgment, <1 hour MTTR target
- **Escalation:** Page on-call SRE, notify engineering lead
- **Communication:** Internal Slack updates every 30 minutes

**SEV-3 (Medium):**
- **Impact:** Non-critical feature degraded, no customer impact yet
- **Examples:** Background job queue backlog, minor performance regression
- **SLA Response:** <1 hour acknowledgment, <4 hours MTTR target
- **Escalation:** Slack notification to on-call engineer
- **Communication:** Ticket created, resolved during business hours

**SEV-4 (Low):**
- **Impact:** Cosmetic issue or improvement opportunity
- **Examples:** Logging errors, dashboard anomalies, optimization opportunities
- **SLA Response:** Next business day
- **Escalation:** None, addressed in next sprint
- **Communication:** Ticket backlog for prioritization

**Checklist:**
- [ ] Severity determined within 5 minutes of detection
- [ ] Escalation protocol followed based on severity
- [ ] Communication started within SLA timeframe
- [ ] Incident commander assigned (SEV-1/SEV-2)
- [ ] War room/bridge opened for coordination

---

### Pattern 2: Incident Response Workflow

**Use when:** Responding to any SEV-1 or SEV-2 incident

**Incident Lifecycle:**

```
Detection → Triage → Response → Resolution → Postmortem

Detection (Automated):
- Prometheus alert fires
- PagerDuty/Opsgenie pages on-call
- Auto-create incident ticket

Triage (5 min):
- On-call acknowledges alert
- Determine severity and impact
- Assign incident commander (SEV-1/SEV-2)

Response:
- Open war room (Zoom/Slack bridge)
- Gather relevant engineers
- Execute runbook for known issues
- Communicate to stakeholders

Resolution:
- Apply fix or rollback
- Verify metrics return to normal
- Monitor for 30+ minutes post-fix
- Mark incident resolved

Postmortem (Within 48 hours):
- Blameless review of timeline
- Root cause analysis (5 Whys)
- Action items to prevent recurrence
- Share learnings with team
```

**Checklist:**
- [ ] Alert acknowledged within SLA
- [ ] Severity assessed and escalation triggered
- [ ] Incident commander assigned (SEV-1/SEV-2)
- [ ] Communication channel opened (Slack/war room)
- [ ] Status page updated (if customer-facing)
- [ ] Runbook followed or troubleshooting documented
- [ ] Fix applied and validated
- [ ] Postmortem scheduled within 48 hours

**Roles During Incident:**
- **Incident Commander (IC):** Coordinates response, makes decisions
- **Communications Lead:** Updates status page, Slack, stakeholders
- **Technical Responders:** Engineers investigating and fixing issue
- **Scribe:** Documents timeline, actions, decisions in real-time

---

### Pattern 3: Escalation Ladder

**Use when:** Initial responder needs additional help or authority

**Escalation Tiers:**

```
Tier 1: On-Call Engineer (First Responder)
  ↓ (If unresolved after 15 min or needs help)
Tier 2: On-Call SRE + Service Owner
  ↓ (If unresolved after 30 min or SEV-1)
Tier 3: Engineering Manager + SRE Lead
  ↓ (If major outage >1 hour or critical business impact)
Tier 4: VP Engineering + CTO (Executive Escalation)
```

**Escalation Triggers:**
- **Time-based:** Incident unresolved after defined SLA
- **Complexity:** Issue requires expertise beyond on-call's domain
- **Impact:** Customer escalations or business-critical system down
- **Safety:** Security incident or data breach suspected

**Checklist:**
- [ ] Escalation contacts up-to-date in PagerDuty/Opsgenie
- [ ] On-call rotation covers 24/7 with backup
- [ ] Escalation SLAs documented and tested
- [ ] Executives aware of escalation criteria
- [ ] Escalation doesn't imply blame (blameless culture)

**Anti-Patterns to Avoid:**
- [FAIL] Escalating too late (heroics instead of asking for help)
- [FAIL] Skipping escalation tiers (going straight to CTO)
- [FAIL] No escalation path documented (chaos during outages)
- [FAIL] Escalation implies blame (people hide issues)

---

### Pattern 4: Blameless Postmortem

**Use when:** After every SEV-1/SEV-2 incident, and optionally for SEV-3

**Postmortem Structure:**

```markdown
# Incident Postmortem: [Brief Title]

## Metadata
- **Date:** 2025-01-20
- **Duration:** 2 hours 37 minutes
- **Severity:** SEV-1
- **Incident Commander:** Alice Chen
- **Responders:** Bob Smith, Carol Johnson, DevOps Team

## Executive Summary
One-paragraph description of what happened, impact, and resolution.

## Timeline (All times UTC)
- **14:32:** Alert fired: API error rate >10%
- **14:35:** On-call acknowledged, opened war room
- **14:40:** Identified root cause: database connection pool exhausted
- **14:52:** Applied fix: increased pool size from 50 to 200
- **15:15:** Metrics returned to normal, monitoring continues
- **17:09:** Declared incident resolved after 2+ hours stable

## Impact
- **Users Affected:** ~15,000 users (23% of active users)
- **Revenue Impact:** Estimated $12,000 in lost transactions
- **SLA Breach:** 99.9% uptime SLA missed (1.8 hours downtime)

## Root Cause Analysis (5 Whys)
1. **Why did API error rate spike?**
   - Database connections exhausted, new requests timed out
2. **Why were connections exhausted?**
   - Traffic spike from marketing campaign (3x normal load)
3. **Why didn't connection pool scale?**
   - Hard-coded limit of 50 connections in config
4. **Why wasn't this load-tested?**
   - Load testing only simulated 2x normal load, not 3x
5. **Why wasn't auto-scaling configured?**
   - Database connection pooling not integrated with auto-scaling system

**True Root Cause:** Static database connection pool configuration + insufficient load testing

## What Went Well
- Alert fired within 3 minutes of issue start
- On-call responded within SLA (5 min acknowledgment)
- War room assembled quickly with right engineers
- Fix applied within 20 minutes of root cause identification

## What Went Wrong
- No pre-incident load testing for 3x traffic scenarios
- Database connection pool hard-coded (not auto-scaling)
- No graceful degradation when connections exhausted
- Status page updated 25 minutes after incident start (missed SLA)

## Action Items
- [ ] [P0] Implement dynamic database connection pooling (@bob, due: 2025-01-27)
- [ ] [P1] Add load test for 5x traffic scenario (@carol, due: 2025-02-03)
- [ ] [P1] Configure graceful degradation (return cached data) (@alice, due: 2025-02-10)
- [ ] [P2] Automate status page updates via incident webhook (@devops, due: 2025-02-17)
- [ ] [P3] Review all hard-coded limits in infrastructure (@sre-team, due: 2025-02-28)

## Lessons Learned
- Load testing must cover extreme scenarios (3x+ traffic)
- All resource limits should be dynamic or monitored
- Status page automation reduces human error during incidents
```

**Checklist:**
- [ ] Postmortem written within 48 hours of resolution
- [ ] Timeline accurate with UTC timestamps
- [ ] Root cause analysis (5 Whys) completed
- [ ] Blameless language (no finger-pointing)
- [ ] Action items assigned with owners and due dates
- [ ] Postmortem reviewed with team and stakeholders
- [ ] Shared with broader engineering org for learning

**Blameless Language Examples:**
- [OK] "The system lacked auto-scaling configuration"
- [FAIL] "Bob forgot to configure auto-scaling"
- [OK] "Load testing didn't cover 3x traffic scenarios"
- [FAIL] "Carol should have load tested better"

---

## Decision Matrices

| Scenario | Severity | Response Time | Escalation | Communication |
|----------|----------|---------------|------------|---------------|
| Complete outage | SEV-1 | <5 min | Immediate page to SRE + EM | Status page every 15 min |
| Degraded service (<50% users) | SEV-2 | <15 min | Page SRE, notify EM | Slack updates every 30 min |
| Non-critical feature down | SEV-3 | <1 hour | Slack notification | Ticket created |
| Cosmetic issue | SEV-4 | Next business day | None | Backlog for sprint planning |

---

## Common Anti-Patterns

### Anti-Pattern 1: Blame Culture
- **Problem:** Postmortems focus on who made the mistake, not what failed
- **Risk:** Engineers hide issues, delays in escalation, repeat incidents
- **Remedy:** Blameless postmortems, focus on system improvements

**Example of Blameless Culture:**
- After incident, leadership says: "Thank you for responding quickly and fixing this. Let's learn what system changes can prevent this."
- NOT: "Why didn't you catch this in testing? This shouldn't have happened."

### Anti-Pattern 2: No Postmortems for SEV-3
- **Problem:** Only major incidents get postmortems, small issues repeat
- **Risk:** Death by a thousand cuts, no learning from near-misses
- **Remedy:** Lightweight postmortems for all SEV-3, full postmortems for SEV-1/SEV-2

### Anti-Pattern 3: Action Items Not Tracked
- **Problem:** Postmortem action items created but never completed
- **Risk:** Same incident repeats, loss of trust in postmortem process
- **Remedy:** Assign owners, due dates, and track in sprint planning

### Anti-Pattern 4: Hero Culture
- **Problem:** Celebrating "heroes" who worked 36 hours to fix incident
- **Risk:** Burnout, lack of sustainable on-call, brittle systems
- **Remedy:** Celebrate prevention and automation, not heroics

---

## Quick Reference

### Incident Response Checklist (SEV-1/SEV-2)

**First 5 Minutes:**
- [ ] Acknowledge alert in PagerDuty/Opsgenie
- [ ] Assess severity and impact
- [ ] Open incident war room (Zoom/Slack bridge)
- [ ] Assign incident commander (if SEV-1/SEV-2)
- [ ] Update status page (if customer-facing)

**First 15 Minutes:**
- [ ] Gather relevant engineers in war room
- [ ] Review recent deployments/changes
- [ ] Check monitoring dashboards for anomalies
- [ ] Execute runbook if known issue
- [ ] Escalate if needed (Tier 2)

**During Incident:**
- [ ] Scribe documents all actions in timeline
- [ ] Communications lead updates status page every 15-30 min
- [ ] IC makes decisions (rollback, deploy fix, etc.)
- [ ] Engineers troubleshoot and apply fix
- [ ] Avoid "too many cooks" (IC limits responders)

**After Fix Applied:**
- [ ] Monitor metrics for 30+ minutes post-fix
- [ ] Verify no secondary issues introduced
- [ ] Mark incident resolved in PagerDuty
- [ ] Update status page with resolution message
- [ ] Schedule postmortem within 48 hours

### On-Call Runbook Template

```markdown
# On-Call Runbook: [Service Name]

## Service Overview
- **Purpose:** What this service does
- **Dependencies:** Upstream and downstream services
- **SLA:** 99.9% uptime, P99 latency <500ms

## Common Alerts

### Alert: High Error Rate
- **Trigger:** Error rate >5% for 5 minutes
- **Severity:** SEV-2
- **Troubleshooting:**
  1. Check recent deployments: `kubectl rollout history deployment/service-name`
  2. Review logs: `kubectl logs -l app=service-name --tail=100`
  3. Check database connections: `kubectl exec -it db-pod -- psql -c "SELECT count(*) FROM pg_stat_activity;"`
  4. If deployment issue, rollback: `kubectl rollout undo deployment/service-name`

### Alert: High Latency
- **Trigger:** P99 latency >2s for 10 minutes
- **Severity:** SEV-3
- **Troubleshooting:**
  1. Check resource utilization: `kubectl top pods -l app=service-name`
  2. Review slow query logs: `kubectl logs -l app=service-name | grep "slow query"`
  3. Check downstream service health: `curl -s http://downstream-service/health`
  4. If resources exhausted, scale up: `kubectl scale deployment/service-name --replicas=10`

## Escalation Contacts
- **Service Owner:** Alice Chen (Slack: @alice, Phone: +1-555-0100)
- **On-Call SRE:** [See PagerDuty schedule]
- **Engineering Manager:** Bob Smith (Slack: @bob, Phone: +1-555-0200)

## Recent Incidents
- [2025-01-20] Database connection pool exhaustion (Postmortem: LINK)
- [2024-12-15] Redis cache eviction storm (Postmortem: LINK)
```

---

## Optional: AI/Automation (Incident Triage)

Use only after core alerting hygiene is in place (good SLOs, deduping, and actionable alerts). Treat automation output as a suggestion, not an authority.

**Traditional Alerting (Noisy):**
```
[14:32] Alert: High CPU on pod-1
[14:33] Alert: High CPU on pod-2
[14:33] Alert: High CPU on pod-3
[14:34] Alert: High memory on pod-1
[14:34] Alert: Database slow queries
[14:35] Alert: API latency >2s
[14:36] Alert: Error rate >10%
... (20 more alerts) ...
```

**AIOps Correlation (Signal from Noise):**
```
[14:32] Incident Detected: Database Performance Degradation
  ├─ Root Cause: Database connection pool exhaustion
  ├─ Symptoms:
  │   ├─ High CPU across 10 pods (connection retry loops)
  │   ├─ Slow queries (waiting for connections)
  │   └─ API latency and errors (timeouts)
  ├─ Affected Services: payment-api, user-service, order-service
  ├─ Impact: 15,000 users (~23% of active users)
  ├─ Suggested Runbook: "Database Connection Pool Exhaustion"
  └─ Recommended Action: Increase pool size or restart connections
```

**Benefits (when correctly configured):**
- Faster incident summarization and paging context
- Better clustering of related alerts into a single incident candidate
- Suggested runbook links and likely dependency focus areas

**Popular tools (examples):**
- Datadog event correlation / anomaly detection
- PagerDuty event intelligence / incident workflows
- BigPanda incident intelligence

### Bounded Claims

- Automation can cluster the wrong alerts together (or split one incident into many).
- Never auto-execute remediation from a summary without explicit human approval.
- Treat predicted root cause as a hypothesis; validate with telemetry and recent changes.

---

## Edge Cases & Fallbacks

**Scenario:** PagerDuty/Opsgenie is down during incident
- **Fallback:** Phone tree escalation (call on-call's mobile directly)
- **Prevention:** Backup alerting via SMS and Slack
- **Test:** Quarterly DR drill to verify phone tree works

**Scenario:** Incident commander unavailable
- **Fallback:** Next person in escalation ladder assumes IC role
- **Prevention:** Cross-train multiple engineers as IC

**Scenario:** Runbook is outdated or doesn't match current system
- **Immediate Action:** Troubleshoot manually, document steps
- **Post-incident:** Update runbook based on actual troubleshooting
- **Prevention:** Review runbooks quarterly

**Scenario:** Fix makes incident worse
- **Immediate Action:** Rollback change immediately
- **Communication:** Update stakeholders that issue is ongoing
- **Prevention:** Test fixes in staging before prod, enable feature flags

---

*This guide focuses on operational, production-ready incident management patterns. All practices are actionable and based on SRE best practices from Google, Netflix, and modern DevOps teams.*
