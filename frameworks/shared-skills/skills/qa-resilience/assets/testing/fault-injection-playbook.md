# Fault Injection Playbook

Use this to plan and execute a single fault injection test.

- **Scenario:** e.g., dependency latency +2s, 500 errors, network drop, AZ outage  
- **Hypothesis:** What should happen? (timeouts respected, circuit opens, fallback serves stale data)  
- **Blast Radius:** Scope (service, namespace, AZ), guardrails, auto-revert time  
- **Pre-Checks:** SLO burn rate, alerts healthy, dashboards bookmarked, rollback commands verified  
- **Execution Steps:** Ordered commands/scripts with expected signals per step  
- **Success Signals:** Error budget burn stays <X, latency <Y, no 5xx beyond Z%, no queue overload  
- **Rollback Criteria:** Thresholds that trigger immediate stop; rollback steps and owner  
- **Post-Test Actions:** Findings, gaps, new alerts, runbook updates, follow-up owners + due dates  
