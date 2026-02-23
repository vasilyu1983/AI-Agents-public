---
name: startup-customer-success
description: "Use when building early customer success and retention systems: onboarding, activation/time-to-value, support triage, health scoring, churn prevention, renewals, and expansion motions."
---

# Startup Customer Success

Retention and expansion systems for early-stage B2B products: turn “closed won” into realized value, keep customers, and expand based on outcomes.

## When to Use

- Designing onboarding and activation flows (time-to-value)
- Building a support triage and escalation system
- Creating customer health scoring and churn prevention playbooks
- Renewals and expansion motions (with clear triggers and value proof)
- Creating a Voice of Customer loop that feeds product and GTM

## When NOT to Use

- Help center information architecture and documentation taxonomy -> [help-center-design](../help-center-design/)
- Closing and negotiation -> [startup-sales-execution](../startup-sales-execution/)

---

## Quick Start (Inputs)

- Customer type: self-serve vs high-touch; contract size band
- "First value" moment: what success looks like in 7/30/90 days
- Product dependencies: integrations, data onboarding, admin setup
- Current issues: churn reasons, support volume, activation drop-offs

---

## Benchmarks (B2B SaaS 2025)

| Metric | Average | Top Quartile |
|--------|---------|--------------|
| Annual retention rate | 74% | 90%+ |
| Net Revenue Retention | 100-105% | 120%+ |
| Onboarding dropout (week 1) | 30-50% | <20% |
| Time-to-value (median) | 14-30 days | <7 days |
| Expansion revenue share | 20-30% | 50%+ of new ARR |

---

## Workflow

1) Define success outcomes and time-to-value
- For each ICP, define: success metric, activation events, and typical blockers.

2) Build onboarding in two layers
- Self-serve: checklists, in-product guidance, fast support.
- Assisted: kickoff call, MAP, implementation plan.

3) Install support triage and escalation
- Severity levels, response targets, and ownership.
- Prevent “support as chaos” by tagging and routing.

4) Create a customer health score (simple first)
- Use `assets/customer-health-score.md`.
- Combine: product usage, outcomes, support signals, and stakeholder engagement.

5) Run churn prevention and renewal playbooks
- Use `assets/churn-postmortem.md` for every churned customer.
- Start renewal conversations early for larger contracts.

6) Expand based on outcomes and triggers
- Expansion triggers: additional team adoption, usage growth, new compliance needs.
- Expansion proof: outcomes achieved and next outcomes enabled.

7) Close the loop to product and GTM
- Monthly: top 5 customer problems, top 5 objections, and “what we should build/say.”

---

## Metrics (Minimum Viable CS Analytics)

- Time-to-value (median and p90)
- Activation rate (by segment)
- Support volume and time-to-first-response
- Logo churn and revenue churn (if applicable)
- Renewal rate (contracted customers)
- Expansion rate (seat/usage/team growth)

---

## AI and Automation in CS

- Automated health score updates from product usage data
- Triggered outreach: low usage, support escalation, renewal approaching
- AI-assisted support triage (sentiment, urgency classification)
- Predictive churn models using engagement signals

---

## Anti-Patterns (Avoid)

- **Reactive-only CS**: Waiting for customers to complain instead of proactive health monitoring
- **Manual health scoring**: Quarterly spreadsheet updates instead of real-time signals
- **One-size-fits-all onboarding**: Same flow for $500/mo and $50,000/mo customers
- **Individual-only activation**: Tracking user activation without account-level view
- **Renewal surprise**: First renewal conversation 30 days before expiration

---

## Resources

| Resource | Purpose |
|----------|---------|
| [onboarding-design.md](references/onboarding-design.md) | Onboarding patterns and time-to-value design |
| [support-triage.md](references/support-triage.md) | Support workflow and escalation |
| [cs-metrics.md](references/cs-metrics.md) | CS metrics definitions and early benchmarks |
| [health-scoring-guide.md](references/health-scoring-guide.md) | Health score design, signals, models, and calibration |
| [churn-prevention-playbook.md](references/churn-prevention-playbook.md) | Proactive churn prevention and save offer frameworks |
| [expansion-playbook.md](references/expansion-playbook.md) | Expansion triggers, motions, and pipeline management |
| [renewal-management.md](references/renewal-management.md) | Renewal process, pricing strategy, and negotiation |
| [voice-of-customer-program.md](references/voice-of-customer-program.md) | VoC program design, feedback collection, synthesis, and product loop |
| [customer-segmentation-tiering.md](references/customer-segmentation-tiering.md) | CS touch model segmentation, tier design, and resource allocation |

## Templates

| Template | Purpose |
|----------|---------|
| [onboarding-checklist.md](assets/onboarding-checklist.md) | Self-serve onboarding checklist |
| [customer-health-score.md](assets/customer-health-score.md) | Health scoring starter |
| [churn-postmortem.md](assets/churn-postmortem.md) | Churn analysis template |
| [qbr-outline.md](assets/qbr-outline.md) | QBR outline (for higher-touch accounts) |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Customer success references |

---

## Related Skills

| Skill | Use For |
|-------|---------|
| [startup-growth-playbooks](../startup-growth-playbooks/) | Retention-driven growth evidence and case studies |

---

## What Good Looks Like

- You can state the “first value” moment and measure time-to-value for new customers.
- Support issues feed product decisions through a visible loop (tags -> priorities).
- Renewal risk is visible early through health signals, not discovered at cancellation.
