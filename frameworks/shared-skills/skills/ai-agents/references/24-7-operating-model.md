# 24/7 Operating Model for Agents

Use this reference when an agent system moves from "demo that works" to "production thing customers depend on at 3am". This guide defines SLOs, on-call structure, runbook contracts, post-mortem expectations, and the operating cadence that keeps agent systems healthy over months.

Applies across Shape A (triggered), Shape B (always-on bot/voice), and Shape C (autonomous loop). Each shape has different SLO targets but shares the same operating-model spine.

## Table of Contents

- [What "Production" Means for Agents](#what-production-means-for-agents)
- [SLO Catalogue by Shape](#slo-catalogue-by-shape)
- [Error Budgets](#error-budgets)
- [On-Call Structure](#on-call-structure)
- [Agent-Specific Alert Catalog](#agent-specific-alert-catalog)
- [Runbook Contract](#runbook-contract)
- [Incident Severity Levels](#incident-severity-levels)
- [The Standard Runbooks](#the-standard-runbooks)
- [Post-Mortem Template](#post-mortem-template)
- [Operating Cadence](#operating-cadence)
- [Change Management](#change-management)
- [Capacity Planning](#capacity-planning)
- [Cost Governance](#cost-governance)
- [Compliance Hooks](#compliance-hooks)
- [Readiness Checklist Before First 24/7 Day](#readiness-checklist-before-first-247-day)
- [Cross-References](#cross-references)

## What "Production" Means for Agents

Production for an agent system is not the same as production for a regular web service. Differences:

| Dimension | Regular service | Agent system |
|---|---|---|
| Failure mode that matters most | 5xx errors | Silent quality degradation |
| Bill scaling | Linear with traffic | Can be quadratic with prompt growth |
| Eval substrate | Tests + monitoring | Tests + monitoring + online evals |
| Change risk | Code change | Code change + model change + prompt change + tool change |
| Rollback unit | Service version | Service + prompt + tool + model versions |
| Oncall pages | Errors and latency | Errors, latency, cost spikes, eval regressions, safety trips |

The 24/7 operating model is built around these differences.

## SLO Catalogue by Shape

Pick the targets that match your product; tighten over time.

### Shape A — Triggered runs

| SLO | Target | Window |
|---|---|---|
| Trigger receipt → agent start | p99 < 30s | 28 days |
| Agent run success rate | ≥ 99% | 28 days |
| DLQ rate | ≤ 1% | 28 days |
| Duplicate rate (after dedup) | ≤ 0.1% | 28 days |
| End-to-end p99 | ≤ 5 min (or product-specific) | 28 days |
| Cost per event vs forecast | within 1.5x | 28 days |

### Shape B — Always-on bot/voice

| SLO | Target | Window |
|---|---|---|
| Availability | 99.9% | 28 days |
| Turn latency p50 | < 1.5s text, < 600ms voice | 28 days |
| Turn latency p99 | < 5s text, < 1.5s voice | 28 days |
| Session completion rate | ≥ 90% | 28 days |
| Escalation rate (delta from baseline) | within 1.5x | 7 days |
| Tool-call success rate | ≥ 99% | 28 days |
| Safety filter trip rate | tracked, alert on 2x baseline | 7 days |

### Shape C — Autonomous loops

| SLO | Target | Window |
|---|---|---|
| Loop completion rate (acceptance met) | ≥ 80% | rolling |
| Stagnation halts | ≤ 10% | rolling |
| Budget breach halts | ≤ 5% | rolling |
| Drift detections | tracked, page if any | per-run |
| Cost per completion vs forecast | within 1.5x | rolling |

Loops with completion rates below 80% are usually mis-scoped — the acceptance criterion is too tight for the agent's capability. Treat low completion as a product problem, not an ops problem.

## Error Budgets

Error budget = (1 − SLO target) × time window.

For 99.9% availability over 28 days: 0.001 × 28 × 24 × 60 ≈ 40 minutes downtime budget.

Burn rate alerts (page when):

- 2% of budget consumed in 1 hour (very fast burn)
- 5% of budget consumed in 6 hours (fast burn)
- 10% of budget consumed in 24 hours (sustained burn)

When the budget is exhausted: stop shipping risky changes until budget is replenished. This is the discipline mechanism — without it, SLOs are decorative.

## On-Call Structure

Minimum viable on-call for an agent system:

- **Primary on-call**: 1 engineer, 1-week rotation, pages first.
- **Secondary on-call**: 1 engineer, fallback at 15 min unacked.
- **Subject-matter on-call** (optional): 1 person familiar with prompts/evals, weekday hours only.

Rotation rules:

- Minimum team size 4 (otherwise burnout). With fewer than 4, accept business-hours-only coverage.
- Hand off Mondays, not Fridays.
- 24 hours of compensatory time per primary week.
- On-call shadow rotation for new hires (4 weeks).

On-call equipment baseline:

- Phone with paging app
- Laptop with VPN and prod access
- Bookmarked runbook hub
- Kill-switch documented
- Provider status pages bookmarked
- A way to silence runaway alerts

## Agent-Specific Alert Catalog

Standard service alerts (5xx, latency, saturation) plus these agent-specific ones:

| Alert | Trigger | Severity | First action |
|---|---|---|---|
| Budget breach | Per-run cost > threshold | P2 | Kill-switch run, investigate |
| Loop stagnation | 3+ iterations no progress | P3 | Review iteration outputs |
| Safety trip rate spike | 2x baseline in 1h | P1 | Pause new sessions, investigate |
| Eval regression | online eval score drops > 10% | P2 | Rollback or pin to prior version |
| Provider outage (LLM) | provider 5xx rate > 5% | P1 | Switch to fallback provider |
| Provider outage (STT/TTS) | provider 5xx rate > 5% | P1 | Switch to fallback (voice only) |
| Cost forecast breach | day-of-month cost > forecast × 1.3 | P2 | Check for runaway loop or attack |
| DLQ depth growth | DLQ > 100 items | P2 | Triage DLQ |
| Recording compliance miss | recording success < 99% | P1 | Halt regulated calls (voice only) |
| Tool error spike | tool error rate > 2x baseline | P2 | Investigate tool backend |
| Memory leak | resident memory growing without bound | P2 | Investigate, restart with caution |
| Hot tenant | one tenant > 50% of LLM spend | P3 | Reach out to tenant, throttle |
| Webhook signature failures | > 1% in 1h | P2 | Possible attack or rotated secret |

Tune thresholds to your baselines. Alert fatigue kills oncall faster than the underlying failures.

## Runbook Contract

Every alert must point to a runbook. Every runbook must answer:

1. **What does this alert mean?** (one paragraph)
2. **How urgent is it?** (severity, time-to-respond)
3. **What's the first thing to check?** (dashboard URL, log query)
4. **What's the most likely cause?** (top 3 historical causes)
5. **What's the kill-switch / mitigation?** (link to action)
6. **Who owns this in normal hours?** (team / Slack channel)
7. **When was this runbook last tested?** (date — older than 90 days = stale)

Runbooks live in the same repo as the agent code, not in a wiki nobody updates.

## Incident Severity Levels

| Sev | Definition | Response | Customer comms |
|---|---|---|---|
| **SEV1** | Outage; customers cannot use product | All hands; war room | Status page; proactive comms |
| **SEV2** | Significant degradation; some flows broken | Primary + secondary | Status page if customer-visible |
| **SEV3** | Edge-case failure or quality regression | Primary | Internal only unless escalates |
| **SEV4** | Cost or efficiency degradation | Triage in business hours | None |

Promote ruthlessly. A SEV3 that's been open 4 hours is a SEV2.

## The Standard Runbooks

Every agent system needs these runbooks before first 24/7 day:

1. **LLM provider outage** — switch to fallback, communicate degradation
2. **Runaway loop / cost spike** — find the loop, kill it, refund affected tenants if needed
3. **Safety filter trip storm** — pause new sessions, investigate input source, file model-provider report if needed
4. **Eval regression** — identify the change, rollback, post-mortem
5. **DLQ saturation** — triage classification, decide drop vs replay vs fix
6. **Hot tenant** — throttle, reach out, possibly migrate to dedicated capacity
7. **Stale checkpoint / state corruption** — restore from backup, identify root cause
8. **Recording compliance gap** (voice only) — assess regulatory exposure, file SAR/breach notice if required
9. **Carrier outage** (voice only) — failover, update status page
10. **Agent context window saturation** — reduce context, summarize history, restart loop with smaller scope

Each should be runnable by the on-call without escalation.

## Post-Mortem Template

```markdown
# Post-Mortem: {{title}}

- **Date**: {{date}}
- **Authors**: {{authors}}
- **Status**: {{draft|review|published}}
- **Severity**: SEV{{1|2|3|4}}
- **Duration**: {{start}} → {{end}} ({{minutes}} min)
- **User impact**: {{description}}

## Timeline
- HH:MM — {{event}}
- HH:MM — {{event}}

## Root cause
{{single sentence, then a paragraph}}

## What went well
- ...

## What went badly
- ...

## Where we got lucky
- ...

## Action items
| Action | Owner | Due | Linked ticket |
|---|---|---|---|
| ... | ... | ... | ... |

## Related material
- Dashboards, logs, prior incidents
```

Rules:

- Blameless. Names attach to actions, not faults.
- Published within 5 business days for SEV1/2.
- Action items have owners and due dates; track in your normal issue tracker.
- One person reads each post-mortem aloud at the next ops review — surfaces gaps you cannot read through.

## Operating Cadence

Weekly:

- 30 min ops review: prior week alerts, SLO burn, top tenants by cost
- DLQ triage pass
- Eval suite run; investigate any regression > 5%

Monthly:

- Runbook freshness audit (any > 90 days untested gets re-tested)
- Cost trend review against forecast
- Kill-switch test (literally flip it and verify the agent stops)
- On-call rotation health (burnout, alert volume per shift)

Quarterly:

- Capacity planning against expected growth
- Provider contract review (volume tiers, fallback SLAs)
- Game day: simulate provider outage, runaway loop, mass-call drop
- Threat model refresh
- Compliance audit prep

## Change Management

Production changes that need review:

| Change | Reviewer | Pre-prod step |
|---|---|---|
| Code change | Standard PR review | Eval suite green |
| Prompt change | Eval-suite gate + 1 reviewer | Canary cohort |
| Model change (e.g., Opus 4.6 → 4.7) | Eval-suite gate + ops sign-off | Canary + cost forecast |
| Tool addition | Security review + 1 reviewer | Sandboxed test |
| Tool removal | Customer-impact review | Deprecation notice |
| Budget cap change | Ops sign-off | Forecast update |
| Hook change (esp. budget hooks) | 2 reviewers | Hook unit tests + integration |

Changes outside business hours: only SEV1/2 mitigation. No feature work, no eval changes, no prompt changes after 6pm local time.

## Capacity Planning

Forecast each substrate:

- LLM provider TPM / concurrent quota
- STT/TTS provider quotas (voice)
- Compute (CPU, memory, pod count)
- Storage (recordings, checkpoints, eval data)
- Telephony carrier capacity (voice)
- Webhook gateway throughput (triggered)

Plan to peak × 2 with at least 14 days of lead time on any quota increase request.

## Cost Governance

Daily:

- Cost dashboard by tenant, by model, by purpose
- Anomaly alerts (any tenant > 3x 7-day average)

Weekly:

- Tenant top-10 review (any new entrant?)
- Cost-per-call / cost-per-event tracked vs forecast

Monthly:

- Provider invoice reconciliation against internal meter
- Budget cap effectiveness (how many runs hit the cap?)

The single most common production fire in May 2026 agent systems is a runaway loop or compromised webhook causing 10x cost overnight. Daily cost alerts catch this before the bill.

## Compliance Hooks

If your agent system is regulated (financial, health, government):

- All actions producing customer impact must be logged with: user, action, agent version, timestamp, agent reasoning summary.
- Audit log retention per regulation (5y for FCA, 7y for HIPAA, 6y for GDPR records of processing).
- Right-to-erasure flows must reach training data and embedding stores, not just the customer-visible database.
- Recordings (voice) with consent records, retention-policy enforced.
- DPIA on file before launch.
- Model card / system card with limitations and known failure modes.

See:

- Project-specific EMI / GDPR skills for client deployments — keep project references out of this portable domain skill
- [`../../ai-mlops/references/governance-checklists.md`](../../ai-mlops/references/governance-checklists.md) — MLOps governance
- `legal-emi-region-uk` — UK regulatory triage

## Readiness Checklist Before First 24/7 Day

- [ ] SLOs documented per shape, with dashboards
- [ ] Error budget defined, burn alerts wired
- [ ] On-call rotation set with at least 4 people
- [ ] Pages route to primary, escalate to secondary at 15 min
- [ ] All 10 standard runbooks written and tested in last 90 days
- [ ] Kill-switch operable from phone
- [ ] Cost dashboards live, anomaly alerts firing
- [ ] DLQ has owner; depth alert wired
- [ ] Eval suite runs nightly with regression alerts
- [ ] Online evals running (Shape B and C)
- [ ] Provider fallback chains configured
- [ ] Audit log meets regulatory retention
- [ ] Post-mortem template available; first one written for a prior near-miss
- [ ] Status page exists; status comms drafted
- [ ] Game day completed in last 90 days
- [ ] Change-management process documented
- [ ] Capacity headroom > 30%
- [ ] Compliance sign-off (if regulated)

## Cross-References

- [`autonomous-loop-patterns.md`](autonomous-loop-patterns.md) — Shape C deep dive
- [`agent-operations-best-practices.md`](agent-operations-best-practices.md) — broader ops patterns
- [`deployment-ci-cd-and-safety.md`](deployment-ci-cd-and-safety.md) — release patterns
- [`evaluation-and-observability.md`](evaluation-and-observability.md) — telemetry stack
- [`guardrails-implementation.md`](guardrails-implementation.md) — guardrails
- [`escalation-patterns.md`](escalation-patterns.md) — escalation flow
- [`../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) — Shape A patterns
- [`../../ai-coding-agents-tasks/references/durable-trigger-integration.md`](../../ai-coding-agents-tasks/references/durable-trigger-integration.md) — durable orchestration
- [`../../ai-bot-builder/references/production-deployment.md`](../../ai-bot-builder/references/production-deployment.md) — Shape B text bot
- [`../../ai-bot-builder/references/stateful-rollout-and-blue-green.md`](../../ai-bot-builder/references/stateful-rollout-and-blue-green.md) — bot rollouts
- [`../../ai-voice-bots/references/production-deployment.md`](../../ai-voice-bots/references/production-deployment.md) — Shape B voice
- [`../../agents-hooks/references/budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md) — budget enforcement
- [`../../ops-incident-response/SKILL.md`](../../ops-incident-response/SKILL.md) — general incident response
- [`../../ai-mlops/references/incident-response-playbooks.md`](../../ai-mlops/references/incident-response-playbooks.md) — ML/AI incident playbooks
- [`../../qa-observability/SKILL.md`](../../qa-observability/SKILL.md) — observability foundations
- [`../../qa-resilience/SKILL.md`](../../qa-resilience/SKILL.md) — resilience review
