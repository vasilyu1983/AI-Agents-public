# Mask: Base-Rate Reset

## Purpose

Force the agent to **start from the base rate** — the population frequency of the outcome being predicted — before incorporating salient, vivid, or recent evidence. Direct response to documented LLM availability/representativeness biases: vivid case studies and recent evidence dominate reasoning, even when base rates are known and informative.

## Source

- Tversky & Kahneman, *Judgment under Uncertainty: Heuristics and Biases* (1974) — the canonical statement of base-rate neglect.
- BiasBuster framework / *Cognitive Bias in Decision-Making with LLMs* (aclanthology [2024.findings-emnlp.739](https://aclanthology.org/2024.findings-emnlp.739/)). Documents LLM susceptibility to the conjunction fallacy and base-rate neglect; recommends "Thoughts of Principles" prompting as the operational fix.
- *A Comprehensive Evaluation of Cognitive Biases in LLMs* ([aclanthology 2025.nlp4dh-1.50](https://aclanthology.org/2025.nlp4dh-1.50.pdf)).

## When To Apply

- Forecasting and timing decisions ("when will X happen?")
- Risk assessment ("what's the probability of failure?")
- Hiring and team-fit predictions ("will this candidate succeed?")
- Project ETA estimation, especially for novel work
- Any decision where a vivid recent anecdote is being treated as evidence
- Any decision where the agent is asked "could X happen?" — the right question is usually "how often does X happen?"
- Founder, investor, and strategy decisions where survivorship bias is acute (most-cited successes are the surviving outliers)

## Reasoning Rewrite

The mask changes the *first* question asked, before evidence enters:

| Forward thinking | Base-rate reset thinking |
|---|---|
| Will this product hit $1M ARR in 18 months? | Of products in this segment with comparable launch metrics, what fraction hit $1M ARR in 18 months? *Then* adjust for what makes us different. |
| This migration will go fine — we tested it. | What fraction of database migrations of this size have shipped without rollback? *Then* assess our specific testing as evidence to update from that base rate. |
| Will this candidate be a top performer? | What fraction of senior hires from this background and stage have become top performers? *Then* update from the interview evidence. |
| Should we expect this PR to merge cleanly? | What fraction of PRs touching N files in this codebase have merged without conflict resolution? *Then* update from this PR's specifics. |
| Will this campaign hit 10K signups? | What's the median signup count from comparable campaigns in this channel? *Then* update for what's distinctive here. |
| Will this incident be back to normal in 1 hour? | What's the median time-to-recovery for incidents of this type historically? *Then* update from current signals. |

The mask runs base rate first, then specific evidence as updates — the reverse of intuitive reasoning.

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the Base-Rate Reset mask:

```text
MASK: Base-Rate Reset

You are being asked to estimate or predict an outcome. Vivid case studies
and recent events tend to dominate reasoning. Run base rate first.

Step 1 — Identify the reference class. Name the population this decision
draws from. Be specific — "B2B SaaS at $5-10M ARR raising Series B" is a
reference class; "startups" is not.

Step 2 — Estimate the base rate. State the unconditional frequency of the
outcome in the reference class. If you don't know, say so explicitly and
either name the data source you'd need OR widen the reference class until
the rate is estimable. NEVER skip this step because the rate is unknown —
record uncertainty as a wide range.

Step 3 — List the specific evidence. For this case, what evidence shifts
probability up or down from the base rate? For each piece, classify:
  - Reliable update signal (objective, large effect, well-validated)
  - Weak update signal (anecdotal, small effect, unvalidated)
  - Vividness trap (a single salient story or recent event being
    over-weighted because it's memorable, not because it's representative)

Step 4 — Apply Bayesian-style update. Adjust the base rate by the reliable
update signals. Discount weak signals. Discard vividness traps. Show your
reasoning chain.

Step 5 — Final estimate. State the posterior probability or estimate
range, ANCHORED on the base rate (so the reader sees how far you moved
from it).

If your final estimate diverges from the base rate by more than 2x,
explicitly justify the magnitude of the update. Large divergence requires
correspondingly strong evidence.
```

## Worked Example

**Decision**: An ops team is debating whether to ship a database migration on a Friday because "we tested it thoroughly and the team has done these before."

**Forward analysis** (standard, vividness-driven): Last migration went fine. The team is experienced. Shipping Friday means the weekend is the soak period.

**Base-rate-reset analysis**:

1. **Reference class**: Production database migrations of comparable scope (>50% of rows touched, >10TB) at this company over the last 24 months.
2. **Base rate**: 7 such migrations in the reference class. 3 had post-deploy issues requiring rollback or hotfix. 1 of the 3 was a Friday deploy. **Base rate of post-deploy issues ≈ 43%**; Friday deploys overrepresented in the failure set.
3. **Specific evidence**:
   - Reliable update: 2 weeks of staging soak with synthetic load — *down* from 43%
   - Weak update: "team is experienced" — minimal effect, the failed migrations also had experienced teams
   - **Vividness trap**: "last migration went fine" — n=1, last migration was simpler, this is the failure mode the mask exists to catch
4. **Bayesian update**: Start at 43%. Strong staging soak → maybe 25-30%. Friday deploy → adds back ~5-10pp because Friday increases time-to-detection and reduces remediation team size.
5. **Final estimate**: ~30-35% probability of needing a rollback or hotfix. Shipping Friday under those odds is a poor expected-value trade. Shift to Tuesday-Wednesday.

The mask surfaced that the "last migration went fine" framing was a vividness trap, and that the reference-class base rate (43%) is much higher than the team's gut estimate (~10%).

## Common Mistakes

- **Skipping base rate when the rate is unknown**: this is the worst failure mode. Wide-range uncertainty is more honest than implicit assumption.
- **Reference class too narrow or too broad**: a class of 1 is just the vivid case; a class of "all decisions" is meaningless. Aim for a class with 5-50 comparable cases.
- **Applying base rate without updating from evidence**: the mask is *anchored* on base rate, not *replaced* by it. Strong reliable evidence should move the estimate.
- **Treating "this case is special" as evidence**: every case feels special. The question is whether it is *representative-class-changing* special.
- **Letting recency leak through reference class selection**: "comparable migrations" should not silently mean "recent migrations the team remembers." Pull from data when possible.

## Composes With

- **First Principles** (sibling mask): first-principles re-derives from primitives; base-rate is the empirical complement — what does the data say happens?
- **Anchoring Reset** (sibling mask): anchoring resets the *number*; base rate resets the *probability*. Layer when both apply (e.g., "competitor raised $40M with traction T → what's the base rate of comparable raises succeeding?").
- **Pre-Mortem** (debate method): pre-mortem benefits from base-rate calibration — "X will go wrong" is more useful when paired with "this fails 30% of the time historically."
- **Prediction Market** (game-theory 11): base-rate reset is the natural input to a member's confidence stake. Stake against the base rate, not against the salient story.
