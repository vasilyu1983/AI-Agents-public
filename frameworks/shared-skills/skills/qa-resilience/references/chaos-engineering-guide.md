# Chaos Engineering Quick Guide

Use this guide to design safe, high-signal reliability experiments.

## Planning
- Define objective and success criteria (SLO impact, user impact)
- Pick hypothesis tied to a specific failure mode (e.g., dependency timeout)
- Limit blast radius (namespace, AZ, service subset) and set auto-revert
- Notify stakeholders and set a clear stop condition

## Common Experiments
- Kill or drain a pod/instance; verify rescheduling and traffic rebalancing
- Increase latency or error rate for a dependency; verify timeouts and fallbacks
- Drop network packets or DNS for a dependency; verify circuit breakers open
- Exhaust a resource (CPU, memory, file descriptors); verify autoscaling or load shedding
- Zonal outage simulation; verify multi-AZ failover and data replication

## Execution Steps
1. Baseline metrics and SLO burn rate
2. Run the experiment with live monitoring
3. Observe user impact (error budgets, latency, conversion)
4. Roll back if thresholds hit; otherwise finish after the planned window
5. Record findings, gaps, and actions

## Debrief Checklist
- [ ] New failure modes discovered and documented
- [ ] SLO/SLA coverage validated or updated
- [ ] Runbooks updated with verified steps
- [ ] Automation opportunities captured (alerts, auto-remediation)
- [ ] Follow-up owners and due dates assigned
