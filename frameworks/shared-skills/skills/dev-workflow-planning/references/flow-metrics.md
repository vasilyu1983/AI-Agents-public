# Flow Metrics Reference

Delivery performance metrics, WIP limits, and flow optimization patterns.

---

## DORA Metrics (5 Keys - 2025 Update)

DORA metrics measure software delivery performance. In 2025, **Reliability** was added as the 5th metric.

### The Five Metrics

| Metric | Definition | Elite Benchmark (2025) |
|--------|------------|------------------------|
| **Deployment Frequency** | How often you deploy to production | Multiple times per day (elite) |
| **Lead Time for Changes** | Time from commit to production | Under 1 hour (elite) |
| **Change Failure Rate** | % of deployments causing incidents | < 5% |
| **Time to Recover (MTTR)** | Time to restore service after incident | Under 1 hour |
| **Reliability** | Meeting SLOs for availability/performance | Consistently meets targets |

Source: [DORA 5 Metrics](https://cd.foundation/blog/2025/10/16/dora-5-metrics/), [DORA.dev](https://dora.dev/guides/dora-metrics-four-keys/)

### Using DORA Metrics

```text
BEST PRACTICES:
1. Measure all 5 metrics together (not in isolation)
2. Use for improvement, not punishment
3. Reduce batch size to improve all metrics
4. Set clear benchmarks against industry standards
5. Cross-functional team ownership of metrics

ANTI-PATTERNS:
- High deployment frequency + high change failure rate
- Low lead time + no reliability monitoring
- Gaming metrics instead of improving process
```

---

## WIP Limits

Work in Progress limits restrict concurrent items in workflow stages.

### Why WIP Limits Work

- **Makes blockers visible** - Can't hide behind "busy"
- **Reduces context switching** - Focus on completion
- **Improves throughput** - Encourages finishing before starting
- **Shortens cycle time** - Items flow faster through the system

### Recommended WIP Limits

| Level | Limit | Formula |
|-------|-------|---------|
| Individual tasks | 2-3 | Cognitive limit |
| Team stories | Team size + 1 | Allow pairing |
| In Progress column | 3-5 | Force completion |
| Code Review | 2-3 | Prevent bottleneck |
| Testing | 3-5 | Match capacity |

### Setting and Adjusting

```text
INITIAL SETUP:
1. Start with team size + 1
2. Monitor for 2-4 weeks
3. Track where items get stuck

ADJUSTMENT RULES:
- Limits never reached -> Lower them
- Constantly blocked -> Investigate root cause (don't raise limit)
- Frequent exceptions -> Limit too low or process issue

WHEN TO VIOLATE:
- Emergency production fix
- Unblocking critical path
- Always document and review in retro
```

Source: [Atlassian WIP Limits](https://www.atlassian.com/agile/kanban/wip-limits)

---

## Cycle Time vs Lead Time

```text
LEAD TIME
Request -> Backlog -> In Progress -> Done
   |                      |
   +-- WAIT TIME ---------+-- CYCLE TIME
          Work actively started
```

| Metric | Measures | Use For |
|--------|----------|---------|
| **Lead Time** | Request to delivery | Customer perspective |
| **Cycle Time** | Work started to done | Team efficiency |
| **Wait Time** | Request to work started | Backlog health |

### Flow Efficiency

```text
Flow Efficiency = (Active Work Time / Total Lead Time) * 100

BENCHMARKS:
- < 15% - Significant waste, lots of waiting
- 15-40% - Typical for most teams
- > 40% - High-performing team

IMPROVEMENT:
1. Reduce WIP to decrease wait time
2. Remove handoff delays
3. Automate repetitive steps
4. Co-locate dependent work
```

---

## Scrumban Hybrid

Combines Scrum's structured planning with Kanban's continuous flow.

### When to Use Scrumban

- Mixed work types (features, bugs, urgent requests)
- Need sprint structure but flexible priorities
- Transitioning from Scrum to more flow-based approach

### Key Practices

| Practice | Description |
|----------|-------------|
| **Planning Triggers** | Plan when ready queue < 5-10 items (not fixed sprint) |
| **WIP Limits** | Per-column limits on Kanban board |
| **Daily Standups** | Keep from Scrum |
| **Retrospectives** | Keep from Scrum |
| **No Sprint Commitment** | Pull work as capacity allows |

Source: [Monday Scrumban Guide](https://monday.com/blog/rnd/scrumban/)

---

## Throughput and Predictability

### Measuring Throughput

```text
Throughput = Items completed / Time period

TRACKING:
- Stories per sprint
- Bugs fixed per week
- Features shipped per month

USE FOR:
- Forecasting delivery dates
- Capacity planning
- Identifying trends
```

### Monte Carlo Forecasting

Use historical throughput data to predict completion dates:

```text
INPUTS:
- Last 10-20 sprints of throughput data
- Number of items remaining

OUTPUT:
- Probability distribution of completion dates
- "85% confidence: Done by March 15"

BETTER THAN:
- Single-point estimates
- "Gut feel" predictions
```

---

## Quick Reference

### DORA Quick Check

Answer these for your team:

1. How often do you deploy? ___
2. How long from commit to production? ___
3. What % of deploys cause incidents? ___
4. How long to recover from incidents? ___
5. Do you consistently meet SLOs? ___

Compare to [DORA benchmarks](https://dora.dev/quickcheck/).

### WIP Limit Checklist

- [ ] WIP limits defined for each column
- [ ] Limits visible on board
- [ ] Team agrees on violation policy
- [ ] Blockers escalated immediately
- [ ] Reviewed in retrospectives

### Flow Health Indicators

| Indicator | Healthy | Unhealthy |
|-----------|---------|-----------|
| WIP | Within limits | Constantly at/over limit |
| Blockers | Resolved in < 1 day | Aging > 3 days |
| Cycle Time | Stable week-over-week | Increasing trend |
| Queue Size | < 2 sprints of work | Growing backlog |

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Planning Templates](planning-templates.md)
- [Session Patterns](session-patterns.md)

---

**Last Updated**: January 2026
