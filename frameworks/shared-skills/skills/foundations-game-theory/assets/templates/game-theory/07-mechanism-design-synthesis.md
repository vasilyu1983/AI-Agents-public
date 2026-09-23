# Mechanism: Mechanism Design for Synthesis

## Domain Applications

- **Policy aggregation**: government or product decision combines multiple stakeholder inputs; structured evidence review reduces loud-voice bias; no truthful-revelation guarantee; dissent section captures minority positions.
- **Investment committee decisions**: analysts submit finding + evidence + confidence; synthesis ranks by evidence density, not seniority or verbosity; contradicted findings go to debate.
- **A/B test result synthesis**: multiple experiment results with conflicting signals; mechanism-design synthesis classifies agreed vs. contradicted results and surfaces dissent before acting.
- **Agent team synthesis**: the primary agent-team use case; synthesis owner applies experimental evidence-synthesis protocol to integrate member outputs without majority-vote pathologies.

## The Synthesis Problem

Synthesis is the highest-value step — and the most prone to game-theoretic failure. The synthesis owner must integrate diverse perspectives without:

- Defaulting to the loudest/longest member output
- Averaging away genuine disagreements
- Ignoring minority positions that may be correct

## Evidence-Synthesis Protocol (No Incentive Guarantee)

```
Step 1: Each member submits: finding + evidence + confidence + uniqueness flag
  (uniqueness flag = "only I could produce this insight")

Step 2: Synthesis owner classifies each finding:
  - Agreed (>1 member converged) → inspect common source/model errors; confidence follows independently checked evidence and calibration, not vote count
  - Unique (one member) → independently verify; sender confidence/uniqueness is a hypothesis, not calibrated evidence
  - Contradicted (members disagree) → reasoning tree audit → include with dissent noted
  - Redundant (same finding from 2+ members) → include once, credit originator

Step 3: Final output includes:
  - Decision/recommendation
  - Evidence strength for each element
  - Dissenting views (not suppressed)
  - Confidence calibration
  - Gaps identified
```

## Reporting Norms for Synthesis

Encourage honest assessment and preserve evidence, uncertainty and dissent. These process norms do not prove any strategic best response. To claim incentive compatibility, specify players, private information, utility, allocation/transfer rules, feasible deviations, enforcement and an incentive inequality for the actual mechanism.

**Implementation**: The synthesis owner commits to valuing:

1. Surprising findings with evidence over confirmatory findings
2. Honest uncertainty over confident guesses
3. Specific disagreements with reasoning over generic agreement
4. "I found nothing noteworthy" over manufactured insights

## Misreport Hazard (Multi-Principal Setting)

When multiple principals share a fine-tuning or synthesis objective, the cited fine-tuning paper finds truthful reporting sub-optimal under most circumstances for its specified social-welfare-maximization rules. This does not imply strict dominance or a misreport incentive for ordinary prompted synthesis. Its affine-maximizer payment result assumes the paper's utility, information and transfer model; verify these before applying DSIC/IR claims.

**When this applies**: multiple stakeholders each contribute a reward signal or preference weight to a shared training or synthesis objective (e.g., multi-team LLM fine-tuning, multi-department synthesis).

**Fix**: design an affine maximizer payment scheme (a weighted VCG extension) so each stakeholder's best response is honest preference reporting. If transferable/enforceable utility assumptions fail, report that the proposed DSIC argument is unavailable; relabelling the task single-principal does not establish truthfulness.

Source: MechDesignFinetune — arXiv 2405.16276, NeurIPS 2024 (confirmed `neurips.cc/virtual/2024/99033`). IJCAI 2025 extended abstract corroborates.

## Claim-Level Truthfulness (Peer-Prediction)

For synthesis tasks with multiple sources, truthfulness at the claim level requires more than Vickrey design at the output level. Sources can strategically shape which claims they surface.

**Recipe**: Decompose the draft synthesis into atomic claims → elicit each agent's stance on each claim → apply peer-prediction scoring (reward informative agreement among sources) → filter manipulated sources before re-synthesis. Any BNE claim is restricted to the paper's actual scoring rule, information/prior and payoff assumptions; this shorthand recipe alone specifies no mechanism or equilibrium proof. Report evidence quality separately from strategic truthfulness.

**Boundary condition**: peer-prediction degrades when sources share the same training data or are semantically near-identical (correlated stances nullify the informative-agreement signal). Run a source diversity check before deploying — if sources are near-identical, the signal collapses.

Source: TTS-PeerPrediction — arXiv 2509.25184, ICLR 2026.

## Related

- [`02-adversarial-debate.md`](02-adversarial-debate.md) — reasoning-tree audit replaces majority voting
- [`11-prediction-market.md`](11-prediction-market.md) — confidence weighting at synthesis step
- [`09-pareto-nash.md`](09-pareto-nash.md) — multi-objective synthesis when tradeoffs are genuine
