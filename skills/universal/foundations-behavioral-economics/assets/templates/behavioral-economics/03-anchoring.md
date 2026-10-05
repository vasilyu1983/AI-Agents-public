# Primitive: Anchoring

## Definition

Anchoring is the tendency for an initial piece of numerical information (the anchor) to disproportionately influence subsequent judgments, even when the anchor is arbitrary or irrelevant to the decision. First documented by Tversky & Kahneman (1974) in the adjustment-and-anchoring heuristic.

Mechanism: when presented with a number, people adjust from it as a starting point. Adjustment is typically insufficient — the final estimate stays too close to the anchor. The anchor biases the perceived value of anything that follows it.

Key properties:
- Arbitrary anchors work: Tversky & Kahneman's famous study showed that a spinning wheel (producing a random number) anchored subsequent estimates of African countries in the UN, even when subjects knew it was random.
- High anchors raise final estimates; low anchors lower them.
- The effect is strongest when the user has no independent estimate to start from.
- Anchors set by the interface — e.g., the highest-priced option shown first — influence willingness to pay for all subsequent options.

## When to Use

- **Pricing pages**: show a high anchor (enterprise tier, original price, competitor price comparison) before the target price.
- **Discount presentation**: show the original price alongside the discounted price to anchor perceived value.
- **Salary or contract negotiation setup**: your system is designing a negotiation flow where setting the first number matters.
- **Subscription tiers**: sequence tiers so the high-price option is the first thing seen.

## Misuse Boundary

**Ethical use**: Anchoring is ethical when the anchor is plausible, relevant, and accurately represents some real comparator — what the product or service has previously cost, what competitors charge, what the full value is.

**Manipulation**: Fabricating an anchor ("was $999, now $99!") when the product was never sold at $999; showing inflated "market rate" comparisons with no basis; using random or irrelevant numbers to inflate perceived value.

**Required condition**: (1) The anchor must be a real number — an actual price, a real competitor's price, a genuine original price. (2) The anchor must be relevant to the decision — pricing comparisons must be for comparable products. (3) In the UK, showing a "was" price requires the product to have genuinely been sold at that price for a meaningful period (ASA/CMA guidance).

## Inputs

- The target price or value you want the user to reach.
- A relevant, accurate high comparator (original price, competitor price, enterprise tier price, "per item" unpackaged cost).
- The context: is the user price-sensitive? Do they have existing reference points?

## Outputs

- An anchored presentation sequence: high anchor visible before target price.
- Copy framing that makes the comparator explicit ("compared to hiring a consultant at $150/hr").
- If discounting: original price shown struck through, with the anchor-to-discount ratio prominent.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Anchor has no effect | User already has a strong external anchor (e.g., they know competitor prices) | Surface the comparison explicitly; use a more credible anchor than the one they have |
| Anchor backfires | High anchor signals that the product is expensive/inaccessible | Pair high anchor with value justification — explain what the anchor price gets |
| Anchor damages trust | User suspects inflation; anchor is implausibly high | Use verifiable comparators (show the source or context for the anchor number) |
| Low anchor suppresses willingness to pay | Interface shows cheapest option first | Resequence: show highest-value tier first or lead with full-price enterprise option |

## Worked Example

**Scenario**: SaaS analytics product, $49/month target price.

Without anchoring: Show $49/month in isolation.

With anchoring:
- Option A (tier anchor): Show enterprise at $299/month first, then Pro at $99/month, then Starter at $49/month. Starter now anchors low by comparison.
- Option B (value anchor): "Hiring an analyst costs $5,000/month. [Product] gives you their output for $49/month."
- Option C (original price anchor): "$99/month — 50% off for the first 3 months. $49/month." (Only valid if $99 is a real price.)

**Ethical check**: Option A — the enterprise tier is a real offering. Option B — the analyst comparison is accurate and relevant. Option C — only valid if the product genuinely has a $99 list price.

## Sources

- Tversky, A. & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. _Science_, 185(4157), 1124–1131. — anchoring and adjustment heuristic.
- Ariely, D., Loewenstein, G. & Prelec, D. (2003). "Coherent arbitrariness": Stable demand curves without stable preferences. _Quarterly Journal of Economics_, 118(1), 73–106. — arbitrary coherence; anchors on willingness to pay.
- Ariely, D. (2008). _Predictably Irrational_, ch. 2. — pricing applications.
