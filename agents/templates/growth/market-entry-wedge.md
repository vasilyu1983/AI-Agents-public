# Growth Template: Market Entry Wedge

Use when the product is live or close to live, but the first serious market, audience, and channel are unclear.

## Required Inputs

- Product and current stage
- Current user segments or intended ICP
- Existing acquisition channels and results
- Activation behavior that proves real value
- Constraints: budget, founder time, geography, platform, compliance, timeline

## Team Prompt Block

```text
Run `expert-board` with board `growth` and mode `market-penetration`.

Goal: choose one first market wedge and one primary channel for [PRODUCT] for the next 30 days.

Member lanes:
- product-strategist: exact audience, job-to-be-done, trigger event, anti-ICP, and sequencing.
- startup-growth-specialist: traction stage, loop quality, channel gates, and 30-day plan.
- marketing-product-analytics-lead: activation-quality metric, attribution limits, retention signal, and instrumentation gaps.
- startup-product-marketing-strategist: category frame, promise, proof asset, and demand-capture asset.
- startup-business-developer: buyer signal, partnership leverage, sales path, and monetization adjacency.

Debate trigger: run one round only if members disagree on product problem vs positioning problem vs channel problem vs monetization problem.

Synthesis output:
1. Chosen wedge: audience, use case, trigger event, anti-ICP.
2. Positioning promise and proof asset.
3. Primary channel and backup channel.
4. Activation-quality metric and instrumentation gap.
5. 30-day plan with weekly milestones.
6. Kill criteria and pivot trigger.
7. What not to do this month.
```

## Decision Rules

- A wedge is too broad if the first channel cannot name where the audience already gathers.
- A channel is premature if activation quality cannot be measured.
- Paid acquisition is a test amplifier, not the default discovery mechanism.
- If every member recommends a different channel, route to `channel-experiment-scorecard.md` before deciding.
