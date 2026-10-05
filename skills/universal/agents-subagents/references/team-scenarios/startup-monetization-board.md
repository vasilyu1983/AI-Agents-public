---
description: Startup Monetization Board — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Startup Monetization Board

**Typical scenario**

The product gets attention and some usage, but revenue is not following. The team needs a safer diagnosis than “just raise prices.”

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "monetization"`.

Scenario: A startup has healthy signups and okay activation, but free-to-paid conversion is weak and upgrades are rare.

Required context:
- Current pricing: free, pro, and team plan with feature-based boundaries
- Target customer: startup operators and small teams
- Current signs: signups and active users exist, but paid conversion is weak

Instructions:
- startup-pricing-advisor diagnoses the main monetization constraint and synthesizes
- marketing-product-analytics-lead checks whether the monetization read is trustworthy
- marketing-strategist checks value communication and pricing-page clarity
- startup-operating-system-reviewer checks downside risk and revenue quality
- startup-business-developer checks willingness-to-pay and commercial fit
- Run independently first
- Then debate whether the next move should be packaging, value communication, paywall timing, or price level
- Return only experiments that can be measured safely
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for pricing, product analytics, marketing, startup operations, and business development in parallel.

Task: Diagnose weak monetization and recommend the safest useful experiments.

Context:
- free, pro, and team plans exist
- signups and active users are healthy enough
- paid conversion and upgrades are weak

Rules:
- each agent returns an independent memo first
- then run a debate on packaging vs value communication vs paywall timing vs price level
- synthesize a final monetization memo with 3 experiments, risks, and measurement requirements
```

**Debate-first variant**

Use when the core disagreement is "the price is wrong" versus "the value is not obvious enough yet."
