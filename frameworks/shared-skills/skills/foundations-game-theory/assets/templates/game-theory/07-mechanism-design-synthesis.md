# Mechanism: Mechanism Design for Synthesis

## Domain Applications

- **Policy aggregation**: government or product decision combines multiple stakeholder inputs; truthful-revelation step prevents loud voices from dominating; dissent section captures minority positions.
- **Investment committee decisions**: analysts submit finding + evidence + confidence; synthesis ranks by evidence density, not seniority or verbosity; contradicted findings go to debate.
- **A/B test result synthesis**: multiple experiment results with conflicting signals; mechanism-design synthesis classifies agreed vs. contradicted results and surfaces dissent before acting.
- **Agent team synthesis**: the primary agent-team use case; synthesis owner applies incentive-compatible protocol to integrate member outputs without majority-vote pathologies.

## The Synthesis Problem

Synthesis is the highest-value step — and the most prone to game-theoretic failure. The synthesis owner must integrate diverse perspectives without:

- Defaulting to the loudest/longest member output
- Averaging away genuine disagreements
- Ignoring minority positions that may be correct

## Incentive-Compatible Synthesis Protocol

```
Step 1: Each member submits: finding + evidence + confidence + uniqueness flag
  (uniqueness flag = "only I could produce this insight")

Step 2: Synthesis owner classifies each finding:
  - Agreed (>1 member converged) → include with high confidence
  - Unique (only one member, flagged as unique) → include with member's confidence
  - Contradicted (members disagree) → reasoning tree audit → include with dissent noted
  - Redundant (same finding from 2+ members) → include once, credit originator

Step 3: Final output includes:
  - Decision/recommendation
  - Evidence strength for each element
  - Dissenting views (not suppressed)
  - Confidence calibration
  - Gaps identified
```

## Vickrey Principle for Synthesis

Apply the truthful revelation principle: design the synthesis process so that each member's best strategy is to report their **honest assessment** rather than what they think the synthesis owner wants to hear.

**Implementation**: The synthesis owner commits to valuing:

1. Surprising findings with evidence over confirmatory findings
2. Honest uncertainty over confident guesses
3. Specific disagreements with reasoning over generic agreement
4. "I found nothing noteworthy" over manufactured insights

## Misreport Hazard (Multi-Principal Setting)

When multiple principals share a fine-tuning or synthesis objective, agents have a dominant incentive to misreport preferences without payment incentives — truthful reporting is strictly dominated. Affine maximizer (weighted VCG) payment restores Dominant-Strategy Incentive Compatibility (DSIC) and Individual Rationality (IR).

**When this applies**: multiple stakeholders each contribute a reward signal or preference weight to a shared training or synthesis objective (e.g., multi-team LLM fine-tuning, multi-department synthesis).

**Fix**: design an affine maximizer payment scheme (a weighted VCG extension) so each stakeholder's best response is honest preference reporting. If payments are non-monetary or utility is non-transferable, explicitly scope the mechanism to a single-principal setting and state that DSIC is not guaranteed.

Source: MechDesignFinetune — arXiv 2405.16276, NeurIPS 2024 (confirmed `neurips.cc/virtual/2024/99033`). IJCAI 2025 extended abstract corroborates.

## Claim-Level Truthfulness (Peer-Prediction)

For synthesis tasks with multiple sources, truthfulness at the claim level requires more than Vickrey design at the output level. Sources can strategically shape which claims they surface.

**Recipe**: Decompose the draft synthesis into atomic claims → elicit each agent's stance on each claim → apply peer-prediction scoring (reward informative agreement among sources) → filter manipulated sources before re-synthesis. Formal BNE guarantee: honest reporting is a Bayesian Nash Equilibrium under this mechanism.

**Boundary condition**: peer-prediction degrades when sources share the same training data or are semantically near-identical (correlated stances nullify the informative-agreement signal). Run a source diversity check before deploying — if sources are near-identical, the signal collapses.

Source: TTS-PeerPrediction — arXiv 2509.25184, ICLR 2026.

## Related

- [`02-adversarial-debate.md`](02-adversarial-debate.md) — reasoning-tree audit replaces majority voting
- [`11-prediction-market.md`](11-prediction-market.md) — confidence weighting at synthesis step
- [`09-pareto-nash.md`](09-pareto-nash.md) — multi-objective synthesis when tradeoffs are genuine
