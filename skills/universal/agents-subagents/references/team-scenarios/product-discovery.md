---
description: Product Discovery — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Product Discovery

**Typical scenario**

You need to choose between several product bets and want a view grounded in user evidence, competition, and analytics.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "product-discovery"`.

Scenario: Decide whether the next quarter should prioritize a team-collaboration feature, a reporting redesign, or onboarding improvements.

Required context:
- current user complaints and product goals
- business constraint: one major initiative this quarter
- optional evidence: analytics, research notes, competitor examples

Instructions:
- product-manager frames the decision and sequencing logic
- product-user-researcher interprets user evidence and usability pain
- startup-competitive-analyst assesses external pressure and differentiation
- marketing-product-analytics-lead assesses measurement and likely outcome signal
- Run in parallel, then synthesize one prioritization recommendation
- Include what evidence is still missing if confidence is weak
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn product_manager, user_researcher, competitive_analyst, and product_analytics_lead in parallel.

Task: choose between collaboration, reporting redesign, and onboarding improvements for next quarter.

Return:
- recommended priority
- strongest evidence for it
- main counterargument
- next evidence to gather if confidence is still low
```

**Debate-first variant**

Use when user pain, competitive pressure, and analytics each point to a different priority.
