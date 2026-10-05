# Mask: Anchoring Reset

## Purpose

Force the agent to **discard the stated anchor** (price, budget, baseline number, prior estimate, competitor reference) and re-derive the value range from primitives, *then* compare against the anchor as a final reconciliation step. Direct response to the documented LLM anchoring effect: stated numbers in the prompt or retrieved context bias the model's output disproportionately, even when the agent has independent knowledge that contradicts the anchor.

## Source

- Echterhoff et al., *Cognitive Bias in Decision-Making with LLMs* ([arxiv 2403.00811](https://arxiv.org/abs/2403.00811), updated 2024–2025; aclanthology [2024.findings-emnlp.739](https://aclanthology.org/2024.findings-emnlp.739/)). Documents anchoring as one of the most reliable LLM cognitive biases. BiasBuster's "ignoring anchor hints" strategy is the operational fix.
- *LLMs Show Amplified Cognitive Biases in Moral Decisions* ([PNAS 2412015122](https://www.pnas.org/doi/10.1073/pnas.2412015122)). Confirms that LLM anchoring is *amplified* over human baselines in some domains.

## When To Apply

- Pricing decisions where a competitor price, current price, or a "starting point" was named in the brief
- Budget reviews where a previously-quoted figure dominates the discussion
- Estimation tasks (effort, latency, traffic) where an early number was floated in chat
- Negotiation analysis where the counterparty's opening offer is in the context
- Performance review where last quarter's numbers are loaded into the prompt
- Any decision where the stated baseline is suspected to be wrong, stale, or strategically planted

## Reasoning Rewrite

The mask changes the *order of reasoning*, not just the question:

| Forward thinking | Anchoring-reset thinking |
|---|---|
| The current price is $49 — should we raise it to $59? | Ignore current pricing for now. From willingness-to-pay, value metric, and competitor median, what is the defensible price range? *Then* compare to $49. |
| Customer offered $200K, we asked $250K. What's the gap? | Discard both numbers. From the deal's strategic value, opportunity cost, and our pricing principle, what range would we accept absent these offers? *Then* place $200K and $250K in that range. |
| Last sprint estimated 20 points; this looks similar — 25? | Re-estimate from work breakdown without referencing 20. Then check whether your independent estimate is suspiciously close to 20 (anchoring leaked through). |
| Competitor raised $40M — should we target $30-50M? | Discard the $40M. From burn rate, milestones to next stage, and dilution targets, what is the right raise size? *Then* check whether market comps support it. |

The mask runs the analysis **twice**: once with the anchor erased, once with it as a reconciliation check. The reconciliation matters — sometimes the anchor was right.

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the Anchoring Reset mask:

```text
MASK: Anchoring Reset

The brief contains one or more numeric anchors (prices, budgets, estimates,
baselines). Anchors bias reasoning even when irrelevant — work the problem
without them, then compare.

Step 1 — Identify the anchors. List every specific number in the brief that
could bias your value estimate.

Step 2 — Derive without anchors. Re-derive the value range from primitives
ONLY. Do not reference the listed anchors during this step. Show your
reasoning chain — the chain must not include the anchor numbers.

Step 3 — Reconcile. Compare your independent derivation to the anchors.
For each anchor, classify:
  - Anchor was correct (within your derived range, anchor is well-calibrated)
  - Anchor was off (outside your range — name the gap and which side)
  - Cannot tell (your derivation is too uncertain to discriminate)

Step 4 — Decision. Recommend based on your INDEPENDENT range, with the
anchor reconciliation as evidence of how confident the recommendation is.

If your independent derivation accidentally lands within ±5% of an anchor,
add a sentence flagging the possibility that the anchor leaked into your
reasoning despite the discipline.
```

## Worked Example

**Decision**: A B2B SaaS team is reviewing whether to raise pricing from **$49/seat to $59/seat**. The brief names both numbers.

**Forward analysis** (standard, anchored): Move from $49 to $59 is a 20% bump. Competitor charges $55. Sounds reasonable.

**Anchoring-reset analysis**:

1. **Anchors identified**: $49 current, $59 proposed, $55 competitor.
2. **Independent derivation**:
   - Value metric is "active seats" — a customer with 50 seats getting full value should pay enough to make the relationship economic.
   - Median deal is 25 seats, average ROI claim from sales calls is $200/seat/month in productivity gains.
   - At 5% value capture (conservative SaaS rule), defensible price is ~$10/seat. At 25% (aggressive but supportable for ROI-led products), defensible is ~$50/seat.
   - Competitor median across 3 alternatives (not just the named one) is $48-72/seat.
   - **Independent range**: $50-75/seat is defensible.
3. **Reconciliation**:
   - $49 anchor → at the floor of the defensible range; under-pricing.
   - $59 proposed → mid-range; supportable but not aggressive.
   - $55 competitor → does not constrain — multiple competitors price higher.
4. **Decision**: $59 is fine but conservative. Independent analysis suggests $65-69 is the right ceiling. The original framing of "$49 → $59" was anchoring on the existing price; the real question was always "what does the value capture support."

The mask surfaced that the team was anchoring on the current price as the baseline, which made $59 feel like a meaningful jump when the value-capture analysis says it isn't.

## Common Mistakes

- **Identifying the anchor and then using it anyway**: the discipline is to *re-derive without it*. Listing the anchor in step 1 doesn't excuse referencing it in step 2.
- **Vague independent derivation**: "based on industry standards" is not a derivation. Name the value metric, the comp set, the rule of thumb.
- **Treating the anchor as the answer when uncertain**: if your independent derivation is too uncertain, the answer is "we don't know," not "default to the anchor."
- **Skipping the leak check**: when the independent derivation lands suspiciously close to the anchor, anchoring may have leaked through. Re-run with a colleague's framing or a different reasoning chain.

## Composes With

- **First Principles** (sibling mask): first-principles asks "from primitives, what's true?" Anchoring Reset is the price/value/estimate-specific operationalization. Layer them when both convention and a numeric anchor are present.
- **Inversion** (sibling mask): inversion asks "what would guarantee failure?" Anchoring Reset asks "what's the defensible range?" Different jobs.
- **Pre-Mortem** (debate method): pre-mortem identifies failure modes; Anchoring Reset disarms the most common one (we under-priced because we anchored on existing price).
- **Generative Social Choice** (game-theory 15): when synthesis must reconcile multiple anchored estimates, run Anchoring Reset on each member's input before maximin selection.
