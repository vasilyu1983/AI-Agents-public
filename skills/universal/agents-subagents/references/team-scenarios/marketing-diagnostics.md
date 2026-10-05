---
description: Marketing Diagnostics — extracted from monolith for progressive disclosure.
last_verified: 2026-08-26
status: stable
---

## Marketing Diagnostics

**Typical scenario**

You want a debate-driven read on product metrics, SEO, and AEO to decide what to improve on the site and in the funnel next.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "marketing-diagnostics"`.

Scenario: We need to understand why organic and AI-search discovery are underperforming even though we keep publishing new pages.

Required context:
- Product metrics: signup rate is okay, activation from organic is weak
- SEO context: a few pages rank, but commercial pages underperform
- AEO context: brand rarely appears in AI answer engines for category questions

Instructions:
- marketing-product-analytics-lead: validate whether the metrics and attribution actually support the current diagnosis
- startup-growth-specialist: identify the highest-leverage funnel and conversion improvements
- marketing-seo-strategist: identify the strongest technical and content SEO gaps
- marketing-aeo-strategist: identify the strongest answer-engine and citation gaps
- Let each member work independently first
- Then force a debate on what should come first: measurement cleanup, SEO fixes, AEO content, or funnel changes
- startup-growth-specialist synthesizes a final improvement plan with ordering and expected impact
- Clean up the team when done
```

**Codex prompt**

```text
Spawn generic role-brief workers for product analytics, growth, SEO, and AEO in parallel.

Task: Diagnose product metrics, SEO, and AEO performance and decide what to improve next.

Context:
- organic traffic exists but activation is weak
- commercial landing pages underperform
- the brand is rarely cited in AI answer engines

Rules:
- each agent returns a short memo first
- then run a debate round on whether the first improvement should be analytics cleanup, SEO, AEO, or funnel conversion
- synthesize a final prioritized improvement plan with rationale and expected effect
```

**Debate-first variant**

Use when the disagreement is "fix measurement first" versus "ship discoverability improvements now."
