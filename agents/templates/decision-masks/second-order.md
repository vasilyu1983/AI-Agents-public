# Mask: Second-Order Thinking

## Purpose

Force 2-3 levels of consequence before committing to a decision. First-order thinking answers "what happens?" Second-order thinking answers "and then what? And then what?" Howard Marks's formulation in his Oaktree memos (2010s), though the underlying pattern is older (game theory, military strategy, chess).

## When To Apply

- Strategic decisions with cascading consequences (pricing changes, hiring senior roles, platform architecture)
- Competitive responses ("if we ship this, what does the competitor do, and then what do we do?")
- Incident response rollback calls ("and then what if the rollback itself fails?")
- Policy decisions that change incentives (comp, org design, access control)
- Platform changes that affect downstream teams
- Any decision where the team is celebrating the first-order win without asking what comes next

## Reasoning Rewrite

The mask rewrites the analysis by chaining consequences:

| First-order (stops at 1) | Second-order (chains to 2-3) |
|---|---|
| "Raising prices increases revenue per customer" | "Raising prices increases revenue per customer. And then some customers churn. And then our NPS drops. And then word-of-mouth acquisition slows. And then CAC rises to compensate. And then the revenue gain is partially or fully offset." |
| "Hiring a VP of Sales accelerates growth" | "Hiring a VP of Sales adds sales capacity. And then we need more SDRs to feed them. And then our product needs to handle enterprise-shaped deals. And then our engineering roadmap shifts toward enterprise features. And then our SMB experience gets worse. Can we afford that tradeoff?" |
| "Moving to microservices improves team autonomy" | "Microservices improve team autonomy. And then each team owns a service. And then cross-service changes need coordination. And then simple changes that used to be one PR become 5 PRs across 5 teams. And then our velocity on cross-cutting features drops. Do we have the coordination infrastructure to handle that?" |
| "Rolling back the deploy fixes the incident" | "Rolling back fixes the immediate issue. And then we're on the old code with the original bug that the deploy was meant to fix. And then if that bug is customer-impacting, we need to push a new fix fast. And then we're deploying under pressure. And then we risk a worse incident. Is rollback actually the right move?" |

The key: **stop at level 2 or 3, not level 1**. First-order thinking says "this works." Second-order thinking says "this works, then X happens, then Y happens, and by level 3 the original win may be neutralized."

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the Second-Order mask:

```text
MASK: Second-Order Thinking

For each significant claim or recommendation in your analysis, chain the
consequences:

LEVEL 1 (first-order): What happens immediately when this decision is made?
LEVEL 2 (second-order): And then what? What does the environment or the other
  stakeholders do in response?
LEVEL 3 (third-order): And then what? How does the situation look 2-3 moves
  later?

Write out at least 2 complete chains for the decision. A chain looks like:

"We do X. This causes Y. Y causes the [competitor / customers / team / regulators]
to respond with Z. Z causes us to need to do W. By the time we reach W, the
original benefit of X is [still valid / partially offset / fully offset /
reversed into a net loss]."

Rules for chains:
1. Do not stop at level 1. If your analysis is "we do X and it works," you are
   not applying the mask. Keep going.
2. The chain must be specific, not generic. Not "and then the market changes"
   but "and then specific competitor A responds with specific move B because
   they have specific incentive C."
3. Name the feedback loop if there is one. Second-order effects often loop
   back to the original decision.
4. Identify which level the benefit is preserved at. If the benefit survives
   through level 3, it's a robust decision. If it's neutralized by level 2,
   you need a different approach.

Return your analysis in two parts:
1. Forward analysis (your normal stakeholder-role read)
2. Consequence chains (at least 2 complete chains, each going to level 3)
```

## Worked Example

**Decision**: Should we add a premium tier at 3× the current price?

**First-order analysis**: Premium tier captures higher willingness-to-pay. Revenue increases from power users. Good move.

**Second-order chains**:

*Chain 1: Positioning*
- Level 1: We add a premium tier at 3× current price
- Level 2: Existing customers who don't upgrade feel "demoted" — their current plan becomes the "basic" plan instead of the "main" plan
- Level 3: Some of those customers start shopping for alternatives because they resent being in the "lower" segment. NPS drops. Churn increases on the existing tier.
- Benefit preserved? Partially. The premium tier adds revenue, but existing-tier churn offsets some of it. Net depends on what % upgrades vs churns.

*Chain 2: Roadmap*
- Level 1: Premium tier exists with premium features
- Level 2: Our roadmap now needs to produce features that justify the 3× price — otherwise the premium tier feels empty
- Level 3: Roadmap priorities shift toward "features that signal premium value" rather than "features that deliver broad user value." SMB customers who don't pay premium see their requested features deprioritized.
- Benefit preserved? Partially. Premium revenue up, but SMB dissatisfaction grows and the product starts feeling split.

*Chain 3: Competitive*
- Level 1: We charge 3× for premium
- Level 2: A competitor notices our premium pricing and ships their own premium tier at 2×
- Level 3: Our premium tier looks overpriced. Prospects price-compare. Our premium conversion slows. We either cut the premium price (signal: rushed pricing) or hold and lose deals.
- Benefit preserved? Depends on differentiation. If premium features are genuinely unique, we hold. If they're easily copied, the premium tier becomes a price floor we can't defend.

**Synthesis from the mask**: The premium tier idea survives if (a) ≥30% of existing customers upgrade without the remainder churning, (b) the premium features are hard to copy, and (c) the roadmap can legitimately deliver 3× value — not just "3× features." Without those preconditions, the first-order benefit is offset by second-order effects.

## Common Mistakes

- **Stopping at level 1**: the most common failure. First-order thinking feels satisfying and complete. Force the chain forward.
- **Vague chains**: "and then the market reacts" is not second-order thinking; it's hand-waving. Name specific actors and specific moves.
- **Ignoring feedback loops**: second-order effects often loop back. If customer X churns because of decision Y, that churn affects metric Z, which affects the original decision's ROI.
- **Applying it to everything**: second-order thinking is expensive. Use it for strategic decisions, not routine execution. Chaining consequences on "should we fix this typo?" is wasted effort.
- **Confusing second-order with pessimism**: second-order thinking can surface positive cascades too. "We ship feature X. And then power users love it. And then they tell their networks. And then CAC drops." This is still second-order thinking — it's just optimistic.

## Evidence

- Howard Marks, Oaktree Capital memos (publicly available at oaktreecapital.com) — "Second-Level Thinking" is Marks's most-cited concept in *The Most Important Thing* (2011).
- Game theory literature — second-order thinking is a common name for "thinking two moves ahead" in competitive environments (chess, poker, negotiation).
- Chuck Prince's 2007 "as long as the music is playing, you've got to get up and dance" quote (Citigroup CEO just before the 2008 crisis) is the canonical example of first-order thinking at senior executive level — the second-order consequences were fully predictable but got ignored because first-order incentives were strong.
