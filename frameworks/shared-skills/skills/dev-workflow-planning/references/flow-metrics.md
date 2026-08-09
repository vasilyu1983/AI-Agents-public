# Flow Metrics Reference

Delivery performance metrics, WIP limits, and predictability patterns for planning and execution.

---
## Table of Contents

- [DORA Metrics](#dora-metrics)
- [Current DORA Set](#current-dora-set)
- [Good Usage](#good-usage)
- [Bad Usage](#bad-usage)
- [Reliability vs DORA](#reliability-vs-dora)
- [WIP Limits](#wip-limits)
- [Cycle Time, Lead Time, Queue Time](#cycle-time-lead-time-queue-time)
- [Predictability](#predictability)
- [Hybrid Planning](#hybrid-planning)
- [Quick Check](#quick-check)
- [Navigation](#navigation)


## DORA Metrics

Use DORA as a planning and improvement lens, not as a target to game.

### Current DORA Set

| Metric | What it measures | Planning use |
|--------|------------------|--------------|
| Change lead time | Time from code change to production value | Batch size, approval friction, queueing |
| Deployment frequency | How often value ships | Release cadence and batch discipline |
| Change failure rate | Share of deployments that cause user-visible failure | Risk, test coverage, rollout quality |
| Failed deployment recovery time | Time to restore service after a bad deployment | Rollback, incident readiness, observability |
| Deployment rework rate | Share of deployed work that must be revised or redone | Requirement quality, plan quality, feedback loop strength |

Use the official DORA guide and quick check for definitions and discussion, then compare against your own historical baseline before comparing against external teams.

### Good Usage

- measure the full set together
- improve systems, not individual performance reviews
- reduce batch size and queue time before adding more process
- pair DORA with reliability and user-impact metrics that matter to your product

### Bad Usage

- quoting unsupported "elite" thresholds without the official report context
- using one metric in isolation
- treating DORA as a leaderboard

---

## Reliability vs DORA

Reliability still matters, but keep it separate from the DORA core definitions unless you explicitly define the metric set your team uses.

Examples:

- SLO attainment
- incident rate
- rollback rate
- latency and error-budget burn

Use these alongside DORA when planning production work and release gates.

---

## WIP Limits

WIP limits reduce context switching and surface blockers early.

| Level | Starting limit | Why |
|-------|----------------|-----|
| Individual | 2-3 active tasks | Protect focus |
| Team stories | Team size + 1 | Allow pairing without overload |
| In-progress column | 3-5 items | Force completion before new starts |
| Code review | 2-3 PRs per reviewer | Prevent review backlog |

Adjustment rules:

1. Start conservative.
2. Review every 2-4 weeks.
3. If limits are never hit, lower them.
4. If work keeps getting blocked, fix the bottleneck instead of raising the limit automatically.

---

## Cycle Time, Lead Time, Queue Time

| Metric | Measures | Why it matters |
|--------|----------|----------------|
| Lead time | Request to delivered value | Customer view |
| Cycle time | Work start to completion | Team execution efficiency |
| Queue time | Waiting before work starts | Planning and prioritization health |

Flow efficiency improves when waiting and handoff time shrink, not when people simply appear busier.

---

## Predictability

Use historical throughput for forecasting rather than a single-point estimate.

Good signals:

- items completed per week or sprint
- cycle-time distribution
- blocker aging
- rework rate

Monte Carlo forecasting is useful when you have stable historical throughput and need a confidence range rather than a promise.

---

## Hybrid Planning

Mixed feature, bug, and urgent-support teams often benefit from a hybrid model:

- planning cadence from Scrum
- pull discipline and WIP limits from Kanban
- explicit expedite lane for true emergencies

Do not add more ceremony than the current variability requires.

---

## Quick Check

- Are batches small enough to recover quickly?
- Are blockers visible within a day?
- Is rework tracked separately from new delivery?
- Are review and deployment queues stable?
- Does the team know the current next bottleneck?

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Planning Templates](planning-templates.md)
- [Operational Checklists](operational-checklists.md)
