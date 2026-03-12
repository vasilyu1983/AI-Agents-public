```markdown
# Incident Response Template (DevOps)

*Purpose: A production-ready template for managing incidents from detection through resolution, including communications, triage, mitigation, escalation, and post-incident review.*

---

# 1. Incident Metadata

**Incident ID:**  
[IR-YYYYMMDD-001]

**Title:**  
[Short description: “Checkout API 500 errors”, “K8s cluster degraded”, etc.]

**Severity:**  
- [ ] SEV0 — Critical outage  
- [ ] SEV1 — Major degradation  
- [ ] SEV2 — Partial impairment  
- [ ] SEV3 — Minor operational issue  

**Start Time:**  
[UTC timestamp]

**Current Status:**  
- [ ] Investigating  
- [ ] Mitigating  
- [ ] Monitoring  
- [ ] Resolved  

**Reported By:**  
[Source: alert, user, SRE, etc.]

**Affected Systems:**  
[List services, clusters, DBs, regions]

---

# 2. Roles & Assignments

**Incident Commander (IC):**  
[Name]

**Communications Lead:**  
[Name]

**Technical Lead(s):**  
[Service/K8s/infra/DX/etc.]

**Scribe (Documentation):**  
[Name]

**Other SMEs:**  
[DBA, Network Eng, App Dev, SRE, etc.]

Checklist:
- [ ] IC assigned within 2 minutes  
- [ ] Comms channel opened (#incident-<id>)  
- [ ] Scribe logging major events  
- [ ] Escalation tree loaded  

---

# 3. Incident Summary (Live Updating)

**What is happening?**  
[Describe symptoms]

**Impact:**  
- [ ] Outage  
- [ ] High latency  
- [ ] Increased error rate  
- [ ] Partial regional effects  
- [ ] Data inconsistency  
- [ ] Degraded throughput  

**User Impact:**  
[What does a real user experience?]

---

# 4. Initial Triage

## 4.1 Is it real?

- [ ] False alert?  
- [ ] Partial outage or localized?  
- [ ] Monitoring gap?  

## 4.2 Immediate Observability Checks

### Metrics  
- Traffic  
- Latency (p95/p99)  
- Error rate  
- Saturation (CPU/mem)  

### Logs  
- Error spikes  
- Deployment events  
- Repeated exceptions  

### Traces  
- Slow spans  
- Failed downstream calls  

## 4.3 Quick Triage Checklist

- [ ] Check dashboards (Golden Signals)  
- [ ] Check last deploy  
- [ ] Check dependencies (DB/cache/queue)  
- [ ] Check resource exhaustion  
- [ ] Check infrastructure events (K8s/node/cloud)  

---

# 5. Mitigation Plan

**Current Hypothesis:**  
[Suspected root cause]

**Immediate Mitigation Actions:**  
(Choose those relevant)

- [ ] Rollback latest deployment  
- [ ] Scale pods/services  
- [ ] Recreate pods or nodes  
- [ ] Failover DB or region  
- [ ] Reduce traffic / enforce rate limiting  
- [ ] Disable heavy background jobs  
- [ ] Revert feature flag  
- [ ] Increase service quotas  
- [ ] Restart unhealthy workloads  

```

Mitigation Step:
Reason:
Command(s):
Expected Outcome:

```

---

# 6. Communication

Announce updates every 10–15 minutes.

### Communication Template
```

[Time UTC]
Status:
Root cause hypothesis:
Mitigation in progress:
Next update in XX min.

```

Channels:
- #incident-<id>  
- Status page  
- Email to key stakeholders  

Checklist:
- [ ] Stakeholders notified  
- [ ] Customer-facing updates posted if required  
- [ ] No speculation  
- [ ] Clear next steps  

---

# 7. Investigative Actions

**Data Collected So Far:**
- Metrics snapshots  
- Logs with timestamps  
- Traces (long spans)  
- K8s events  
- DB metrics  
- Cloud provider alerts  

### Investigative Questions
- When did it start?  
- What changed (deploy, config, dependency)?  
- Which region(s) affected?  
- Can problem be reproduced?  
- Is it cascading from another service?  

### Safe Experiments

- [ ] Test rollback  
- [ ] Test endpoint with dev traffic  
- [ ] Disable/enable specific replica  
- [ ] Temporarily reroute traffic  

Never perform:
- Destructive K8s operations in prod  
- Full cluster/node delete  
- Unvalidated DB migrations  
- Forced failover without IC approval  

---

# 8. Resolution

**Resolution Time:**  
[Timestamp]

**Resolution Summary:**  
[What fixed the issue?]

```

Commands/steps executed:

- ...
- ...

```

Checklist:
- [ ] Systems stable for 30 min  
- [ ] Error budget updated  
- [ ] All rollbacks applied  
- [ ] Alerts firing as expected  
- [ ] Cluster/database fully healthy  

---

# 9. Recovery Actions

**After mitigation, apply:**

- [ ] Backfill dropped traffic if required  
- [ ] Sync caches or replicas  
- [ ] Re-enable paused jobs  
- [ ] Re-enable autoscaling  
- [ ] Re-deploy artifact if rollback used  
- [ ] Validate metrics for 1–2 hours  

---

# 10. Post-Incident Review (PIR)

Must be completed within 24–48 hours.

### PIR Template

```

Incident ID:
Severity:
Start / End Time:
Duration:
Services Impacted:
User Impact:

Root Cause:
Contributing Factors:
Timeline:
  [time] event
  [time] event
Mitigation:
What Went Well:
What Went Poorly:
Where We Got Lucky:
Action Items (with owners and due dates):
Long-Term Fixes:

```

Checklist:
- [ ] No blame language  
- [ ] One action item per contributing factor  
- [ ] Business owner included  
- [ ] Regression tests added  

---

# 11. Severity Levels (Standard)

| Sev | Description | Response Time | Criteria |
|-----|-------------|----------------|----------|
| SEV0 | Full outage | Immediate | 100% down / major data loss |
| SEV1 | Major impact | < 15 min | Critical path degraded |
| SEV2 | Partial impact | < 1 hr | Non-critical slowdowns |
| SEV3 | Minor issue | < 1 day | No user-visible outage |

---

# 12. Incident Runbook Snippets

### Restart Pod Safely (K8s)

```

kubectl delete pod <pod> --grace-period=30
kubectl rollout status deployment/<app>

```

### Rollback Deployment

```

kubectl rollout undo deployment/<app>

```

### Restart Service (Systemd)

```

sudo systemctl restart <service>

```

### Rolling Restart

```

kubectl rollout restart deployment/<app>

```

### Verify Health

```

kubectl get pods
kubectl logs <pod>
curl -f https://<service>/healthz

```

---

# 13. Final Incident Checklist

### Before Declaring Resolved

- [ ] Systems stable 30+ minutes  
- [ ] No alert flapping  
- [ ] SLOs green  
- [ ] Runbooks updated if missing steps  
- [ ] Monitoring dashboards corrected  
- [ ] Root cause validated  
- [ ] Action items logged  

---

# 14. Completed Example

**Incident ID:** IR-20250310-001  
**Title:** Prod Checkout API 500 Spike  
**Severity:** SEV1  
**Impact:** Users unable to complete purchases  

**Cause:** A canary deployment introduced a latency regression → cascading DB saturation.

**Mitigation:**  
- Rolled back deployment  
- Added rate limiting  
- Increased DB read replicas  

**Resolution:** 17 minutes  
**Action Items:**  
- Add load tests to pipeline  
- Add DB connection pool alert  
- Strengthen canary gating  

---

# END
```
