---
name: ops-incident-response
description: "Guides incident response from detection through postmortem. Use when designing on-call runbooks, triaging production incidents, writing status updates, or improving MTTD and MTTR."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Incident Response

## Quick Reference

| Need | Go to |
|------|-------|
| Classify the incident severity | `## Severity Classification` |
| Run the end-to-end response loop | `## Workflow` |
| Coordinate as incident commander | `## Incident Commander Checklist` |
| Send status or stakeholder updates | `## Communication Templates` |
| Use templates and runbooks | `## Navigation` |

## Scope

| Use For | Do NOT Use For |
|---------|----------------|
| Severity classification and escalation | Infrastructure provisioning or CI/CD |
| On-call runbook design and review | Application resilience patterns (retries, circuit breakers) |
| Incident commander workflows | Monitoring/alerting tool setup |
| Status page and stakeholder communication | Root cause analysis of code bugs |
| Blameless postmortem facilitation | Performance benchmarking |
| MTTD/MTTR measurement and improvement | Security incident forensics (use software-security-appsec) |

## Severity Classification

Read the service's paging policy and runbook before assigning severity, acknowledgement deadlines, or update cadence. If unavailable, mark the following as an illustrative starting policy and assign an owner to confirm it.

| Level | Criteria | Response time | Who is paged |
|-------|----------|---------------|-------------|
| **SEV1** | Revenue-impacting, data loss, full outage | Immediate | On-call + incident commander + leadership |
| **SEV2** | Degraded service, partial outage, SLO breach | 15 min | On-call + incident commander |
| **SEV3** | Minor degradation, workaround available | 1 hour | On-call |
| **SEV4** | Cosmetic, no user impact, internal tooling | Next business day | Ticket owner |

## Workflow

```text
1) DETECT — Alert fires or user report received
   - Acknowledge the alert within SLA
   - Open an incident channel (Slack/Teams)
   - Assign incident commander if SEV1/SEV2

   DECLARE-AND-MOBILIZE (T+0, SEV1/SEV2):
   - Auto-create or manually open a dedicated #inc-YYYYMMDD-[short-name] channel
   - Assign roles at declaration: IC, comms lead, scribe — do not wait for volunteers
   - Assign the first status update and its deadline using the service's communication policy
   - Trigger postmortem document creation at incident close (template auto-populated
     with title, severity, IC, timeline start — not at the writing stage)
   - Use the team's configured incident tooling; confirm its working escalation path

2) TRIAGE — Assess impact and classify severity
   - Confirm affected systems, user segments, blast radius
   - Check recent deployments, config changes, dependency status
   - Update status page with initial assessment
   - If SLO/error-budget tracking is active: post current budget consumed in channel

3) MITIGATE — Stop the bleeding
   - Prioritize mitigation over root cause
   - Rollback, feature-flag off, scale up, redirect traffic
   - Communicate ETA or "investigating" to stakeholders

4) RESOLVE — Confirm recovery
   - Verify the primary user outcome, service SLI, dependency health, and queued or delayed work remain within bounds for at least one meaningful traffic or processing cycle
   - Check data integrity separately when writes, ordering, or retries were affected
   - Record the observation window and residual degradation; a deploy success, pod health, falling error rate, or quiet alert stream alone is not recovery
   - Update status page to "resolved"
   - Close the incident channel
   - Note total error-budget consumed in the postmortem summary line

5) LEARN — Blameless postmortem
   - Write timeline (what happened, when, who did what)
   - Identify contributing factors (not "root cause")
   - Define action items with owners and deadlines
   - Share postmortem with the team
   - For SEV1/SEV2: use the Howie structured-interview approach before group debrief
     (see references/postmortem-facilitation.md)
   - When every component worked as designed but the interaction failed: CAST
     (see ../foundations-safety-engineering/references/cast-incident-analysis.md)
```

## Incident Commander Checklist

- [ ] Open dedicated incident channel
- [ ] Assign roles: IC, comms lead, subject matter experts
- [ ] Set a timer for the service's agreed status-update cadence
- [ ] Keep a running timeline in the channel
- [ ] Delegate investigation — IC coordinates, does not debug
- [ ] Post status page updates at each phase transition
- [ ] Apply the recovery checks in Workflow before calling "resolved"
- [ ] Schedule postmortem using the team's review deadline

## Incident Commander Decisions

- **Ambiguous severity:** declare when plausible user harm from delayed coordination exceeds the disruption of mobilizing responders; de-escalate after bounding impact. The cost comparison in [decision-theory-applied.md P2](references/decision-theory-applied.md#p2--minimax-regret-for-ambiguous-severity) is illustrative, not proof that escalation always wins.
- **Communication:** send material changes immediately and retain the promised next-update time even when nothing changed. Keep raw investigation detail in the responder channel; send impact, progress, and next update to stakeholders.
- **Conflicting mitigations:** name one action owner and surface incompatible proposals before execution. If investigation stops producing updates, request the hypothesis, evidence, and next checkpoint.
- **Blameless review:** preserve factual actions and timestamps, then explain the information and constraints available to responders. Rewriting every action as “the system allowed” can erase evidence. Track action closure separately from postmortem publication and assign owners to each contributing factor.

## Communication Templates

### Status Page — Investigating

```text
[Service Name] — Investigating
We are aware of [brief description of impact].
Our team is investigating and will provide updates every [interval].
Started: [timestamp UTC]
```

### Status Page — Resolved

```text
[Service Name] — Resolved
The issue affecting [brief description] has been resolved.
Duration: [start] to [end] ([total minutes])
[If approved for this audience: postmortem publication date or next follow-up.]
```

### Stakeholder Update (SEV1/2)

```text
Subject: [SEV-N] [Service] incident update — [status]

Impact: [who is affected, what they see]
Current status: [mitigating / investigating / resolved]
Next update: [time UTC]
Actions taken: [bulleted list]
Incident lead: [name]
```

## Metrics

Targets below are example starting points; set real targets from your own incident baseline.

| Metric | What it measures | Example target |
|--------|-----------------|--------|
| **MTTD** (Mean Time to Detect) | Impact starts → confirmed detection (alert or user report) | < 5 min for SEV1 |
| **MTTA** (Mean Time to Acknowledge) | Alert fires → responder acknowledges | < 15 min for SEV1 |
| **MTTM** (Mean Time to Mitigate) | Acknowledge → user impact stops | < 30 min for SEV1 |
| **MTTR** (Mean Time to Resolve) | Impact starts → full recovery (local definition) | < 1 hour for SEV1 |
| **Postmortem completion rate** | Incidents with published postmortems | 100% for SEV1/2 |
| **Action item close rate** | Postmortem actions completed on time | > 80% within deadline |

**Distributional caveat:** [Davidovič's report](https://sre.google/resources/practices-and-processes/incident-metrics-in-sre/) finds that sparse, variable incident samples can make means, medians, and tail percentiles unreliable for detecting improvements. Define timestamps consistently, show cohort size, and measure the response step a change targets. See [incident-metrics-guide.md](references/incident-metrics-guide.md) when designing the measurement.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Blaming individuals in postmortems | Focus on systems, processes, and contributing factors |
| Reviewing only full outages | Apply the team's review criteria; include near misses or repeated incidents when they expose a failure pattern |
| IC also debugging | IC coordinates and communicates; SMEs debug |
| "Root cause" singular thinking | Most incidents have multiple contributing factors |
| Silent status pages during incidents | Update even if the update is "still investigating" |
| Action items without owners or deadlines | Every action item gets a name and a date |
| Blameless language over a blame-shaped narrative | Keep factual actions and explain responder context — see Incident Commander Decisions |
| Action items logged but never revisited ("action-item graveyard") | Track action-item close rate as its own metric, separate from postmortem completion rate |

## Regulatory Reporting Overlays

During triage, send plausible regulatory exposure to legal/compliance and record awareness, classification, materiality determination, and submission timestamps separately. This skill supplies the operational timeline; counsel confirms scope and filing deadlines.

| Regime | Trigger to record | Lookup before calculating a deadline |
|--------|-------------------|------------------------------------|
| EU DORA | Awareness of the ICT incident and classification as major | [RTS 2025/301 Article 5](https://eur-lex.europa.eu/eli/reg_del/2025/301/oj): initial deadline uses both awareness and classification, with a separate rule for classification after the awareness window. Intermediate timing runs from initial submission; final timing from the intermediate or latest updated intermediate report. Check entity-specific holiday rules and competent-authority instructions. [ITS 2025/302](https://eur-lex.europa.eu/eli/reg_impl/2025/302/oj) supplies incident forms/templates; ITS 2024/2956 concerns the third-party register. |
| EU NIS2 | Awareness of a significant incident | [Directive 2022/2555 Article 23](https://eur-lex.europa.eu/eli/dir/2022/2555/oj): early warning without undue delay and within 24 hours of awareness; incident notification without undue delay and within 72 hours of awareness; final report within 1 month after submitting the incident notification. Check national implementing law and the competent CSIRT's instructions, trust-service-provider notification exceptions, and the ongoing-incident progress/final-report sequence. |
| SEC Form 8-K Item 1.05 | Domestic registrant's materiality determination | [SEC disclosure guidance](https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/cybersecurity-risk-management-strategy-governance-incident-disclosure) and the applicable form: file within 4 business days after determining the incident is material; make that determination without unreasonable delay. Discovery is a separate timestamp. Foreign private issuers use the Form 6-K framework. Counsel confirms permitted delays and issuer scope. |

## Navigation

### References

- [runbook-design-guide.md](references/runbook-design-guide.md) — How to write effective on-call runbooks
- [on-call-practices.md](references/on-call-practices.md) — On-call rotation, escalation, and fatigue management
- [postmortem-facilitation.md](references/postmortem-facilitation.md) — Running blameless postmortems (includes Howie standard for SEV1/SEV2)
- [incident-metrics-guide.md](references/incident-metrics-guide.md) — Load when defining duration metrics or evaluating response improvements; covers timestamp definitions and sample uncertainty
- [slo-incident-triggering.md](references/slo-incident-triggering.md) — Error-budget burn rate as incident trigger; burn rate → severity mapping; postmortem prioritization by budget remaining
- [references/control-theory-applied.md](references/control-theory-applied.md) — Control-theory applied recipes for incident response: stable autoscaler retune, cascading-failure containment, recovery throttling.
- [references/decision-theory-applied.md](references/decision-theory-applied.md) — Decision-theory applied recipes for incident response: paging thresholds via EU, rollback as real option, MAB runbook ordering.

### Assets

Use these as copy-paste starters; fill placeholders before sharing with stakeholders.

- [incident-channel-template.md](assets/incident-channel-template.md) — Use at **T+0** when opening a SEV1/SEV2 incident channel; post as the first pinned message to assign roles and set next-update time.
- [postmortem-template.md](assets/postmortem-template.md) — Use at **incident close** to create the postmortem document; populate title, severity, IC, and timeline start immediately (do not wait until the writing session).
- [runbook-template.md](assets/runbook-template.md) — Use when **authoring or reviewing** a service runbook; also reference during triage to confirm runbook coverage gaps as action items.

### Related Skills

| Skill | Relationship |
|-------|--------------|
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | Infrastructure, CI/CD, deployment automation |
| [qa-resilience](../qa-resilience/SKILL.md) | Application-level fault tolerance patterns |
| [qa-observability](../qa-observability/SKILL.md) | Monitoring, alerting, SLI/SLO setup |
| [qa-debugging](../qa-debugging/SKILL.md) | Systematic debugging during incidents |
| [software-security-appsec](../software-security-appsec/SKILL.md) | Security incident handling |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
