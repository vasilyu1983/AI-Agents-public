---
description: Expert-board growth mode — extracted scenario for progressive disclosure.
last_verified: 2026-09-16
status: stable
---

## Expert-board Growth Mode

**Typical scenario**

Your company is growing, but the team disagrees on whether growth is healthy and what to improve next across product, funnel, and GTM.

**Claude prompt**

```text
Run the saved `expert-board` workflow with board `growth`.

Scenario: We are a B2B SaaS company with rising top-of-funnel traffic but uneven activation and unclear expansion signal.

Required context:
- Stage: early post-PMF with first meaningful inbound demand
- Target customer: startups and scale-up operators
- Current signs: visits and signups are up, activation is flat, retention is uneven

Instructions:
- product-strategist: challenge whether the current product direction is still the right wedge
- startup-growth-specialist: challenge whether the active loops and experiments are actually compounding
- marketing-product-analytics-lead: challenge whether the metric read is trustworthy or misleading
- startup-product-marketing-strategist: challenge positioning, category frame, launch narrative, proof assets, and demand capture
- startup-business-developer: challenge monetization, buyer signal, and partnership leverage
- Let each member produce an independent read first
- Then have them explicitly argue over whether the next improvement should be product, distribution, or pricing
- product-strategist synthesizes a final founder memo with the strongest recommendation and strongest dissent
- Clean up the team when done
```

**Codex prompt**

```text
Run `expert-board` with board `growth`. Its manifest dispatches product-strategist, growth-specialist, product-analytics-lead, product-marketing-strategist, and business-developer role briefs in parallel.

Task: Evaluate whether the company is growing in a healthy way and decide what to improve next.

Context:
- top-of-funnel traffic and signups are up
- activation is flat
- retention is uneven
- product serves startups and scale-up operators

Rules:
- each agent returns an independent memo first
- then run a debate round on product vs distribution vs pricing as the next priority
- synthesize a final founder memo with agreement, disagreement, and the single next operating focus
```

**Debate-first variant**

Use when the core disagreement is "we need a product change" versus "we need better distribution and demand capture."

**Typical scenario (variant: market penetration / first serious users)**

You have already built the app or product, but growth is not deliberate. The question is which market wedge and channel to focus on now, not whether another feature can be built.

Use the [market-penetration workflow contract](../workflow-contracts.md#market-penetration-review). The required output is a 30-day plan with one primary channel, one backup channel, activation-quality metric, instrumentation gaps, and a named execution team.

**Codex prompt**

```text
Run `expert-board` with board `growth` and mode `market-penetration`. Its manifest dispatches the five growth lenses in parallel.

Task: Decide the first or next market-entry wedge for this built product and produce a 30-day growth plan.

Context:
- product is live or close to live
- current channel focus is unclear
- founder needs serious users, not generic traffic
- activation / retention / monetization data may be incomplete

Rules:
- each member returns an independent memo first
- debate product problem vs positioning problem vs channel problem vs monetization problem
- synthesize exactly one primary market wedge and one primary channel
- include what not to do for the next 30 days
```
