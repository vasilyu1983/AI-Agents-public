# Debugging Checklist Template

Copy-paste checklist for systematic debugging workflows.

---

## Universal Debugging Checklist

### Phase 1: Information Gathering

```
[ ] Can you reproduce the issue consistently?
    - Reproduction rate: ___%
    - Required conditions: _______________

[ ] What is the exact error message?
    Error: _______________
    Location: _______________

[ ] When did the issue start?
    Date/Time: _______________
    Version: _______________

[ ] What changed recently?
    [ ] Code deployment
    [ ] Configuration change
    [ ] Data migration
    [ ] Infrastructure update
    [ ] External service change

[ ] What is the expected behavior?
    _______________

[ ] What is the actual behavior?
    _______________

[ ] What environment(s) are affected?
    [ ] Production
    [ ] Staging
    [ ] Development
    [ ] Local
```

---

### Phase 2: Hypothesis Formation

```
[ ] Form 2-3 hypotheses about root cause

Hypothesis 1: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low

Hypothesis 2: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low

Hypothesis 3: _______________
Evidence: _______________
Likelihood: [ ] High [ ] Medium [ ] Low

[ ] Rank hypotheses by probability
[ ] Identify test for each hypothesis
```

---

### Phase 3: Investigation

```
[ ] Gather evidence

LOGS:
[ ] Check application logs
[ ] Filter by time window: _______________
[ ] Filter by request ID: _______________
[ ] Filter by user ID: _______________
    Key findings: _______________

METRICS:
[ ] Check error rate
[ ] Check latency (P50/P95/P99)
[ ] Check resource usage (CPU/memory/disk)
[ ] Check request rate
    Key findings: _______________

TRACES:
[ ] Find affected request trace
    Trace ID: _______________
[ ] Identify bottleneck service/component
[ ] Review full request path
    Key findings: _______________

DATABASE:
[ ] Check query performance (EXPLAIN ANALYZE)
[ ] Check connection pool stats
[ ] Check for long-running queries
[ ] Check for lock contention
    Key findings: _______________

EXTERNAL SERVICES:
[ ] Check third-party API status pages
[ ] Check network connectivity
[ ] Check timeout configurations
[ ] Review API error responses
    Key findings: _______________
```

---

### Phase 4: Testing Hypothesis

```
[ ] Design minimal test case
    Test: _______________
    Expected result if hypothesis correct: _______________

[ ] Execute test
    [ ] In local environment
    [ ] In staging environment
    [ ] In isolated production environment

[ ] Record actual result
    Result: _______________

[ ] Does result match prediction?
    [ ] Yes -> Hypothesis confirmed, proceed to fix
    [ ] No -> Hypothesis rejected, form new hypothesis
```

---

### Phase 5: Fix Implementation

```
[ ] Implement fix
    Change: _______________

[ ] Test fix locally
    [ ] Unit tests pass
    [ ] Integration tests pass
    [ ] Manual testing complete

[ ] Deploy to staging
    [ ] Smoke tests pass
    [ ] Regression tests pass
    [ ] Performance tests pass

[ ] Deploy to production
    [ ] Canary deployment (10%)
    [ ] Monitor for 30 minutes
    [ ] Increase to 50%
    [ ] Monitor for 1 hour
    [ ] Full deployment (100%)

[ ] Verify fix resolves issue
    [ ] Error rate returned to normal
    [ ] Latency returned to baseline
    [ ] No new errors introduced
    [ ] User confirmed resolution
```

---

### Phase 6: Prevention

```
[ ] Add regression test
    Test file: _______________

[ ] Update documentation
    [ ] Runbook updated
    [ ] README updated
    [ ] Architecture docs updated

[ ] Share learnings
    [ ] Team notification sent
    [ ] Postmortem conducted (if incident)
    [ ] Wiki/knowledge base updated

[ ] Implement preventive measures
    [ ] Add monitoring/alerting
    [ ] Add validation checks
    [ ] Improve error messages
    [ ] Add defensive coding
```

---

## Specialized Checklists

### Performance Issue Checklist

```
[ ] Profile CPU usage
    Tool: _______________
    Hot functions: _______________

[ ] Profile memory usage
    Tool: _______________
    Memory leaks detected: [ ] Yes [ ] No

[ ] Analyze database queries
    [ ] Run EXPLAIN ANALYZE on slow queries
    [ ] Check for missing indexes
    [ ] Check for N+1 query problems
    Findings: _______________

[ ] Check network latency
    [ ] External API calls
    [ ] Database connections
    [ ] Inter-service communication
    Findings: _______________

[ ] Review algorithmic complexity
    [ ] Identify O(n^2) or worse loops
    [ ] Check for redundant operations
    Findings: _______________

[ ] Test with production-like data
    [ ] Volume testing complete
    [ ] Load testing complete
    Findings: _______________
```

---

### Memory Leak Checklist

```
[ ] Monitor memory over time
    Initial: ___ MB
    After 1 hour: ___ MB
    After 4 hours: ___ MB
    Growth rate: ___ MB/hour

[ ] Take heap snapshots
    [ ] Snapshot at start
    [ ] Snapshot after operations
    [ ] Compare snapshots
    Retained objects: _______________

[ ] Check for common causes
    [ ] Global variables accumulating data
    [ ] Event listeners not removed
    [ ] Timers (setInterval) not cleared
    [ ] Circular references
    [ ] Large objects in closures
    [ ] Cache without eviction
    [ ] Unclosed connections
    [ ] File handles not closed

[ ] Verify fix
    [ ] Memory usage stable over 24 hours
    [ ] No growth trend observed
    [ ] Garbage collection working normally
```

---

### Distributed System Debugging Checklist

```
[ ] Trace request across services
    Request ID: _______________

[ ] Map service dependencies
    Entry point: _______________
    Services involved: _______________

[ ] Check each service health
    [ ] Service A: [ ] Healthy [ ] Degraded [ ] Down
    [ ] Service B: [ ] Healthy [ ] Degraded [ ] Down
    [ ] Service C: [ ] Healthy [ ] Degraded [ ] Down

[ ] Review service-to-service communication
    [ ] Check network connectivity
    [ ] Verify service discovery
    [ ] Check circuit breaker status
    [ ] Review timeout configurations

[ ] Analyze distributed trace
    [ ] Identify slowest span
    [ ] Check for failed requests
    [ ] Review retry attempts
    Bottleneck: _______________

[ ] Check infrastructure
    [ ] Load balancer health
    [ ] DNS resolution
    [ ] Network policies
    [ ] Resource limits
```

---

### Production Incident Checklist

```
DETECTION:
[ ] Incident detected
    Time: _______________
    Source: [ ] Alert [ ] User report [ ] Monitoring

[ ] Severity assessed
    [ ] P0 - Critical (system down)
    [ ] P1 - High (major feature broken)
    [ ] P2 - Medium (degraded performance)
    [ ] P3 - Low (minor issue)

RESPONSE:
[ ] Create incident ticket
    Ticket #: _______________

[ ] Assemble response team
    Incident Commander: _______________
    Technical Lead: _______________
    Communications Lead: _______________

[ ] Establish communication channel
    Channel: _______________

[ ] Notify stakeholders
    [ ] Engineering team
    [ ] Product team
    [ ] Customer support
    [ ] External customers (if needed)

INVESTIGATION:
[ ] Check monitoring dashboards
[ ] Review recent deployments
[ ] Analyze logs and traces
[ ] Form hypothesis

MITIGATION:
[ ] Implement immediate fix
    OR
[ ] Rollback to last known good version

[ ] Verify mitigation
    [ ] Error rate returned to normal
    [ ] Functionality restored

RESOLUTION:
[ ] Implement permanent fix
[ ] Test in staging
[ ] Deploy to production
[ ] Monitor for 24 hours

POSTMORTEM:
[ ] Document timeline
[ ] Identify root cause
[ ] List action items
[ ] Share learnings
[ ] Schedule follow-up
```

---

## Common Anti-Patterns to Avoid

```
[FAIL] Making random code changes without hypothesis
[FAIL] Skipping reproduction steps
[FAIL] Debugging without logs/observability
[FAIL] Fixing symptoms instead of root cause
[FAIL] Not adding regression tests
[FAIL] Deploying fixes without testing
[FAIL] Debugging directly in production
[FAIL] Ignoring stack traces
[FAIL] Not documenting findings
[FAIL] Restarting services without understanding issue
```

---

## Tips for Effective Debugging

```
[OK] Use the scientific method
[OK] Form testable hypotheses
[OK] Make one change at a time
[OK] Document everything
[OK] Use version control
[OK] Take breaks when stuck
[OK] Explain problem to someone else (rubber duck)
[OK] Add instrumentation proactively
[OK] Read error messages carefully
[OK] Follow the data
```

---

## Time-Boxed Debugging

If stuck after:

```
30 minutes: Take a break, explain problem to someone
1 hour: Try different approach or tool
2 hours: Escalate or ask for help
4 hours: Reassess strategy, consult senior engineer
```

Remember: Getting help is not failure, it's efficiency.

---

> **Pro Tip**: Copy this checklist into your incident ticket or debugging session notes. Check off items as you go to maintain systematic approach.
