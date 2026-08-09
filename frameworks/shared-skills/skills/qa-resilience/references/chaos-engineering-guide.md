# Chaos Engineering Quick Guide

Use this guide to design safe, high-signal reliability experiments.

## When Production Chaos Testing Is Essential vs. Irresponsible

Chaos experiments only produce trustworthy signal about production behavior when they run where production behavior actually happens — staging environments routinely differ in traffic shape, data volume, dependency versions, and failure-mode coupling, so a clean staging result does not prove a system is resilient in production. That is the case *for* production testing. It is essential, not optional, when: the system has genuine redundancy to fail over into (so the experiment can only reveal a gap, not cause a real outage with no fallback); a tested rollback/abort mechanism exists and has itself been exercised; blast radius is bounded to a small traffic or infrastructure slice; and an on-call human is actively watching live dashboards for the whole experiment window, empowered to abort immediately.

Running chaos experiments in production is irresponsible — not merely risky, but the wrong call — when any of the following hold: there is no verified rollback path (an "abort button" that has never been pressed is not a rollback path); the blast radius cannot be bounded below "all users" (e.g., a single shared control-plane component with no partition); the team lacks the observability to detect user-facing harm within the experiment's own timescale; the experiment targets a system already known to be in a fragile or degraded state (chaos testing during an ongoing incident, or immediately after one, adds risk without adding signal); or the organization has not first validated the same hypothesis in a lower environment at all — production should usually be the *last* rung of a testing ladder (unit/local fault injection → staging chaos → canary/limited-production chaos → full production game day), not the first. Skipping straight to unbounded production chaos to "move fast" is the single most common way this practice damages trust in itself.

The deciding question is not "could this fail?" (something can always fail) but "if this goes wrong, can we detect it and reverse it faster than it can hurt a user?" If the honest answer is no, the experiment needs a smaller blast radius, a lower environment, or a rollback mechanism built and proven first — not cancellation of the resilience goal, but a redesign of how to reach it safely.

## Planning
- Define objective and success criteria (SLO impact, user impact)
- Pick hypothesis tied to a specific failure mode (e.g., dependency timeout) — see [reliability-theory-applied.md](reliability-theory-applied.md#p2--steady-state-hypothesis-design-for-chaos-experiments) for steady-state hypothesis discipline (define the measurable steady state *before* the experiment, not after)
- Limit blast radius (namespace, AZ, service subset) and set auto-revert — bound the blast radius to the smallest slice that can still produce a real answer; widen only after a smaller radius has produced a clean result
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
