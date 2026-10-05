# Aggregation Rule (Primitive #11) and the Multi-Agent Evidence Layer

These aggregation mechanisms (voting, debate, routing, Shapley credit assignment, coalition topology) were previously indexed under `foundations-game-theory`. They are **shared-payoff** aggregation problems — every participant wants the synthesis to be correct, nobody is strategically misreporting — which makes them team-theory's regime, not game theory's. If a participant can gain by lying about its claim or vote, that is a mechanism-design problem; see `foundations-game-theory` (#7 partial, #14 partial peer-prediction layer).

## When multi-agent pays (read this before reaching for any row below)

| Question | Evidence | Rule of thumb |
|---|---|---|
| Does the task structure favor multi-agent at all? | Kim et al., arXiv:2512.08296: relative gain over a single-agent baseline ranges from +80.8% on decomposable tasks to -70.0% on sequential/interdependent planning, plus a capability-saturation effect. | Decomposable, parallel-verifiable subtasks → candidate for multi-agent. Sequential/interdependent → default to one strong agent. |
| Should I debate or vote? | Choi, Zhu & Li, arXiv:2508.17536 (NeurIPS 2025 Spotlight): "Majority Voting alone accounts for most of the performance gains typically attributed to MAD"; debate is a martingale over beliefs and "does not improve expected correctness" by itself. | Run a matched-token-budget majority-vote/self-consistency baseline first. Debate only if it beats that baseline, uses targeted interventions, or the audit trail is itself the product. |
| Is my equal-budget comparison real? | Tran & Kiela, arXiv:2604.02460: API-based budget controls "distort effective computation." | Count all tokens including retries/verification; watch for budget-control artifacts. |
| Pool or route to the strongest? | Pappu et al., arXiv:2602.01011: expertise dilution and team-size effects measurably hold experts back on expert-relevant tasks. | Route/weight to an identifiably stronger participant rather than pooling equally when one exists. |

## Aggregation rows

Full playbooks: [`../assets/templates/team-theory/`](../assets/templates/team-theory/).

| Row | Mechanism | Use when | Scope limit |
|---|---|---|---|
| Belief-driven lane assignment (ECON-inspired) | [`01-econ-belief-driven.md`](../assets/templates/team-theory/01-econ-belief-driven.md) | Members read the same context and pool into duplicate analysis | The +11.2%/-21.4% figures belong to ECON's RL-trained belief/mixing networks (arXiv:2506.08292), not this prompt-only proxy. Treat the recipe as untested until measured on your task. |
| Heterogeneous debate | [`02-adversarial-debate.md`](../assets/templates/team-theory/02-adversarial-debate.md) | Only after a matched-budget vote/self-consistency baseline has been beaten | Majority vote is the baseline to beat, not the anti-pattern (Choi et al.). "Cap at 2 rounds" is an engineering default, not sourced. |
| Courtroom-style debate (PROClaim) | [`08-courtroom-proclaim.md`](../assets/templates/team-theory/08-courtroom-proclaim.md) | High-stakes go/no-go needing an evidential audit trail | +10pp gain is confirmed but scoped to zero-shot Check-COVID; do not generalize the magnitude. |
| Confidence weighting / staking | [`11-prediction-market.md`](../assets/templates/team-theory/11-prediction-market.md) | Verbose or loud outputs must not dominate synthesis | The self-critique calibration step is CritiCal-*inspired*, not CritiCal (a training method, arXiv:2510.24505); no verified magnitude for the prompt-only version. |
| Reasoning-tree audit | [`13-reasoning-tree-audit.md`](../assets/templates/team-theory/13-reasoning-tree-audit.md) | Confident-but-wrong majority consensus | "Up to 5%" over majority vote (AgentAuditor), reported with an ACPO-trained adjudicator; no confirmed "+3pp vs LLM-as-judge" figure. |
| Meta-debate role routing | [`16-meta-debate-routing.md`](../assets/templates/team-theory/16-meta-debate-routing.md) | Static role assignment picks the wrong specialist for plaintiff/defense/judge | — |
| Beyond Majority Voting (BMV) | [`18-beyond-majority-voting.md`](../assets/templates/team-theory/18-beyond-majority-voting.md) | Best-of-N discrete answer where majority vote would erase a minority-correct candidate | This is the recommended aggregation weighting; folds into the "pool vs route" row above when one candidate is from an identifiably stronger source. |
| Radial Consensus Score (RCS) | [`19-radial-consensus-score.md`](../assets/templates/team-theory/19-radial-consensus-score.md) | Best-of-N open-ended generation, semantically clustered but lexically diverse | — |
| Conformal social choice (act/escalate) | [`20-conformal-social-choice.md`](../assets/templates/team-theory/20-conformal-social-choice.md) | Calibrated selection gating an irreversible action | A singleton is a selection result, not proof of correctness — validate independently before acting. |
| Shapley contribution scoring (#4) | [`04-shapley-contribution.md`](../assets/templates/team-theory/04-shapley-contribution.md) | Post-run credit assignment: which member added how much to the shared result | Exact cost is 2^N coalition evaluations; approximate for larger teams. Credit only, no incentive guarantee. The hand-checked worked example and self-test stay in `foundations-game-theory` (`references/verified-artifacts.md`, `scripts/game_artifacts.py`). |
| Online Shapley prompt evolution (#17) | [`17-online-shapley-prompt-evolution.md`](../assets/templates/team-theory/17-online-shapley-prompt-evolution.md) | Live, high-frequency workflow where contribution-weighted prompts must drift per run | Depends on #4 (same folder). HiveMind figures are abstract-level and not re-verified; treat the loop as untested until measured. |
| Coalition formation routing (#22) | [`22-coalition-formation-routing.md`](../assets/templates/team-theory/22-coalition-formation-routing.md) | Large team where one flat panel causes overload or duplicated work | A fit-based topology recipe with no stability guarantee; its source (arXiv:2604.14386) frames the problem with hedonic games. |

## Kept in `foundations-game-theory` (strategic kernel)

These have a genuine incentive/strategic kernel, so their templates live in game theory. Use the rows above for the non-strategic aggregation part:

- **#7 Mechanism design for synthesis** — affine-maximizer (weighted VCG) payments for multi-principal settings; no incentive guarantee without a payment scheme. See `foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md`.
- **#14 Per-claim credibility scoring** — the per-claim scoring recipe is an aggregation step (treat it like the rows above), but the peer-prediction layer (BNE truthfulness guarantee, arXiv:2509.25184) is strategic; both live in `foundations-game-theory/assets/templates/game-theory/14-credibility-scoring.md`.
- **Coalition stability theory** — the #22 recipe moved here (row above); the hedonic-game / Nash-stable-partition theory behind it stays in `foundations-game-theory` (formal-theory map).

## Not team theory — route elsewhere

- **#9 Pareto-Nash multi-objective** — single-decision-maker MCDA; use `foundations-decision-theory` for the decision logic. The template is still in `foundations-game-theory`.
- **#10 Evolutionary coordination search** — black-box optimization with no strategic or team content; for prompt search and evaluation use `ai-prompt-engineering` / `ai-evals`. The template is still in `foundations-game-theory`; it is the offline counterpart of #17 here.

## Sources

Choi, Zhu & Li, *Debate or Vote*, arXiv:2508.17536, NeurIPS 2025 Spotlight. Kim et al., arXiv:2512.08296 (abstract-level figures). Tran & Kiela, arXiv:2604.02460. Pappu et al., arXiv:2602.01011 (see team-theory SKILL.md Fact-Checking for the exact, non-transferable figures).
