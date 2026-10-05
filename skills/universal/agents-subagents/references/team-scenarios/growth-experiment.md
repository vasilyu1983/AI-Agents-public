---
description: Growth Experiment — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Growth Experiment

**Typical scenario**

You want a team to diagnose funnel friction and prioritize the next experiment.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "growth-experiments"`.

Scenario: Trial signup is strong, but activation into first successful workflow is weak. We need the next best experiment.

Required context:
- Funnel stage and target metric
- Optional context: analytics event map, landing pages, paid channel performance

Instructions:
- startup-growth-specialist identifies the biggest leverage point in the funnel
- marketing-product-analytics-lead checks instrumentation quality and metric interpretation risk
- marketing-paid-acquisition-strategist checks whether acquisition quality is causing the apparent activation issue
- marketing-strategist checks message mismatch between acquisition promise and in-product experience
- Work in parallel first
- startup-growth-specialist synthesizes the top 3 experiments with expected impact and confidence
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn growth_specialist, product_analytics_lead, paid_acquisition_strategist, and marketing_strategist in parallel.

Problem:
- trial signup is healthy
- activation into the first successful workflow is weak
- goal is to choose the next best experiment

Rules:
- analytics lead should validate whether the metric is trustworthy before others overfit to it
- each agent returns one hypothesis, one experiment idea, and one major caveat
- wait for all outputs
- then synthesize a ranked experiment list with expected impact, confidence, and required instrumentation
```

**Debate-first variant**

Use debate when the disagreement is "fix acquisition quality first" versus "fix onboarding/activation first."
