---
name: startup-sales-execution
description: "Use when running founder-led sales, BD/partnership deal execution, or building an early sales motion: discovery calls, qualification, pipeline stages, proposals, negotiation, closing, expansion, BD outreach, partner deal structures, co-selling coordination, and sales metrics/cadence."
---

# Startup Sales Execution

Practical playbooks to turn interest into revenue: run discovery, qualify deals, close cleanly, and drive expansion without breaking trust or economics.

## When to Use

- You need a founder-led sales motion that actually closes (not just "leads")
- Discovery calls, qualification, objection handling, or pricing conversations
- Building a pipeline with stages, exit criteria, and weekly deal review cadence
- Proposals, mutual action plans, procurement/security handling
- Renewals/expansion motion (especially in B2B SaaS)
- BD outreach, partner deal negotiation, co-selling execution

## When NOT to Use

- Lead capture, demand gen, meeting booking -> [marketing-leads-generation](../marketing-leads-generation/)
- Pricing model design, unit economics -> [startup-business-models](../startup-business-models/)
- GTM strategy and channel selection -> [startup-go-to-market](../startup-go-to-market/)
- Onboarding/support systems -> [startup-customer-success](../startup-customer-success/)

---

## Quick Start (Inputs)

Ask for the minimum set of inputs that makes sales advice concrete:

- Product: what it does, setup time, and “first value” moment
- ICP: buyer, champion, typical deal size (ACV/ARPA), sales cycle expectations
- Motion: PLG, sales-led, hybrid (who does what, when)
- Current state: current pipeline, win/loss notes, objections heard, pricing page link (if any)
- Constraints: legal/security requirements, procurement friction, implementation/services required

If inputs are missing, proceed with explicit assumptions and ask for 1 example deal (won/lost) to anchor.

---

## Workflow

1) Define the sales motion and handoffs
- Who qualifies (founder/SDR), who closes (founder/AE), who onboards (CS/product).
- Decide the primary close path: demo-first, trial-first, or audit/assessment-first.

2) Set pipeline stages with exit criteria
- Use `assets/pipeline-stages.md` to define stages and “done means done” criteria.
- Keep stages few and behavioral (what the buyer did), not internal hope.

3) Run discovery that produces a decision
- Use `references/discovery-playbook.md` and `assets/discovery-call-script.md`.
- Output: a clear problem statement, impact, stakeholders, and next step.

4) Qualify with one framework (and actually use it)
- Use `references/qualification-and-deal-review.md`.
- Output: a deal summary that predicts close probability and exposes gaps early.

5) Price and propose with guardrails
- Use `assets/proposal-outline.md`.
- Keep discounting rules explicit (who can approve, for what, and why).

6) Handle procurement and negotiation without “random concessions”
- Use `references/negotiation-and-procurement.md`.
- Default posture: trade concessions for commitment (term length, volume, case study, prepay).

7) Close with a mutual action plan (MAP)
- Use `assets/mutual-action-plan.md`.
- MAP turns “sounds good” into calendar-bound steps with owners.

8) Drive expansion with usage + outcomes (not pressure)
- Define expansion triggers (seats, usage, additional teams, compliance).
- Coordinate with [startup-customer-success](../startup-customer-success/) for retention-first expansion.

9) Run BD outreach and partner deals (when applicable)
- BD discovery differs from direct sales: focus on mutual value and long-term alignment, not pain selling.
- Qualify partners with `assets/partner-deal-scorecard.md`: audience fit, technical compatibility, incentive alignment, champion access.
- Structure deals explicitly: rev share, referral fees, integration commitments, co-sell SLAs, exit terms.
- BD negotiation is relationship-first: trade exclusivity for commitment, volume for better terms, co-marketing for access.
- Maintain a separate BD pipeline from direct sales (different stages, longer cycles, different success metrics).
- For partner strategy and program design: see [startup-go-to-market](../startup-go-to-market/).
- For detailed BD execution patterns: see `references/bd-execution-playbook.md`.

10) Install a weekly operating cadence
- Pipeline review (30 min): stage hygiene + next steps.
- Deal review (30 min): top 3 deals + one stuck deal (diagnose gap).
- Win/loss (30 min): one deal, one lesson, one change to the playbook.

---

## Metrics (Minimum Viable Sales Analytics)

- Pipeline created per week (by channel)
- Stage conversion rates and time-in-stage
- Win rate by segment (ICP) and by deal size band
- Median sales cycle length
- Discount rate and reasons
- Expansion rate (if applicable)

---

## Resources

| Resource | Purpose |
|----------|---------|
| [discovery-playbook.md](references/discovery-playbook.md) | How to run discovery and produce a next-step decision |
| [qualification-and-deal-review.md](references/qualification-and-deal-review.md) | Qualification frameworks and deal review templates |
| [objection-handling.md](references/objection-handling.md) | Objection patterns by stage, price objections, competitor responses |
| [negotiation-and-procurement.md](references/negotiation-and-procurement.md) | Procurement, security, negotiation, and redline handling |
| [bd-execution-playbook.md](references/bd-execution-playbook.md) | BD outreach, partner deal terms, co-selling coordination, BD pipeline |
| [sales-metrics-and-forecasting.md](references/sales-metrics-and-forecasting.md) | Pipeline metrics, velocity formula, forecasting methods, board reporting |
| [sales-enablement-content.md](references/sales-enablement-content.md) | Sales collateral, battlecards, case studies, demo scripts, content tracking |
| [crm-pipeline-setup.md](references/crm-pipeline-setup.md) | CRM selection, pipeline stages, fields, automation, reporting dashboards |
| [demo-methodology.md](references/demo-methodology.md) | Demo types, 3-story framework, multi-stakeholder demos, metrics |

## Templates

| Template | Purpose |
|----------|---------|
| [pipeline-stages.md](assets/pipeline-stages.md) | Stages, exit criteria, and definitions |
| [discovery-call-script.md](assets/discovery-call-script.md) | Talk track + question flow |
| [proposal-outline.md](assets/proposal-outline.md) | Proposal structure and pricing terms |
| [mutual-action-plan.md](assets/mutual-action-plan.md) | MAP for closing and onboarding handoff |
| [partner-deal-scorecard.md](assets/partner-deal-scorecard.md) | Partner qualification and deal evaluation |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Sales references |

---

## What Good Looks Like

- You can explain “why buy, why now, why us” in one paragraph per deal.
- Each pipeline stage has a buyer action and a next step scheduled.
- Negotiation trades are explicit (concession for commitment), not reactive discounts.
- You know your bottleneck (top-of-funnel vs close vs onboarding friction) from numbers, not vibes.
