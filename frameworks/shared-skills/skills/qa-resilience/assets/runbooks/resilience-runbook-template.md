# Resilience Runbook Template

Fill this template when documenting a service's resilience strategy.

- **Service:**  
- **Owner / Pager:**  
- **SLOs:** Availability %, latency targets, error budget burn alerts  
- **Dependencies (ranked):** Service → dependency, timeout, retry policy, circuit breaker config, fallback  
- **Failure Modes:** What can go wrong? (timeout, error spike, thundering herd, saturation)  
- **Protection:** Bulkheads, backpressure, rate limits, load shedding rules  
- **Observability:** Key dashboards, alerts, traces, logging fields (correlation IDs)  
- **Graceful Degradation:** What to show users when degraded; data freshness guarantees  
- **Failover/DR:** Region/AZ strategy, replication lag budget, RPO/RTO, failover test cadence  
- **Run Steps:** Verification checklist before/after change; rollback triggers and commands  
- **Validation:** Chaos experiment IDs, last test date, next scheduled game day  
