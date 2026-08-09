# Game-Theory Primitives — Composition Guide

22 domain-agnostic game-theory primitives. Each file is a standalone playbook (problem, solution, how-it-works, domain applications, launch-prompt template, citations). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

For the agent-team applied recipe layer (team.yaml manifest fields, agent-team anti-patterns, decision checklist for team launches), see [`../../../../agents-subagents/references/game-theory-agent-teams.md`](../../../../agents-subagents/references/game-theory-agent-teams.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-econ-belief-driven.md](01-econ-belief-driven.md) | Pooling equilibrium — members read same context, produce overlapping analysis |
| 2 | [02-adversarial-debate.md](02-adversarial-debate.md) | Confabulation consensus, correlated bias |
| 3 | [03-auction-task-routing.md](03-auction-task-routing.md) | Static routing, ambiguous selection |
| 4 | [04-shapley-contribution.md](04-shapley-contribution.md) | Free-riding, unverifiable attribution |
| 5 | [05-reputation-gating.md](05-reputation-gating.md) | Uniform trust regardless of track record |
| 6 | [06-cooperation-defection.md](06-cooperation-defection.md) | Shallow output, scope dumping, echo chambers |
| 7 | [07-mechanism-design-synthesis.md](07-mechanism-design-synthesis.md) | Loudest-wins aggregation, suppressed dissent |
| 8 | [08-courtroom-proclaim.md](08-courtroom-proclaim.md) | Evidence stagnation, position-anchored reasoning |
| 9 | [09-pareto-nash.md](09-pareto-nash.md) | Single-objective optimization on multi-objective problems |
| 10 | [10-alphaevolve.md](10-alphaevolve.md) | Hand-tuned rules sub-optimal vs. measured fitness |
| 11 | [11-prediction-market.md](11-prediction-market.md) | Verbose output dominates synthesis |
| 12 | [12-negotiation-zopa-batna.md](12-negotiation-zopa-batna.md) | Adversarial framing on genuine compromises |
| 13 | [13-reasoning-tree-audit.md](13-reasoning-tree-audit.md) | Confident-but-wrong consensus; majority vote unsafe |
| 14 | [14-credibility-scoring.md](14-credibility-scoring.md) | Single-claim failure modes reputation gating misses |
| 15 | [15-generative-social-choice.md](15-generative-social-choice.md) | Multi-stakeholder buy-in; averaging erases minority evidence |
| 16 | [16-meta-debate-routing.md](16-meta-debate-routing.md) | Wrong-specialist gets wrong debate role; static role assignment |
| 17 | [17-online-shapley-prompt-evolution.md](17-online-shapley-prompt-evolution.md) | Weak team members never improve; static prompts under-utilize Shapley signal |
| 18 | [18-beyond-majority-voting.md](18-beyond-majority-voting.md) | Majority vote on best-of-N erases minority-correct answers |
| 19 | [19-radial-consensus-score.md](19-radial-consensus-score.md) | Lexical-overlap voting fails on semantically clustered open-ended answers |
| 20 | [20-conformal-social-choice.md](20-conformal-social-choice.md) | Wrong consensus turns into irreversible action |
| 21 | [21-attested-delegation-contracts.md](21-attested-delegation-contracts.md) | Self-claimed delegate quality corrupts routing |
| 22 | [22-coalition-formation-routing.md](22-coalition-formation-routing.md) | Large flat panels duplicate work and destabilize synthesis |

---

## Domain Scenario Stacks

### Pricing / Mechanism Design

- **Objective**: set pricing that maximizes revenue while preserving retention and remaining competitive
- **Stack**: #9 (Pareto-Nash — map efficient frontier across revenue × retention × competitive positioning) + #12 (BATNA/ZOPA — identify negotiation range for enterprise deals) + #7 (mechanism-design synthesis — dissent required in pricing committee output)
- **Add if adversarial**: #14 (per-claim credibility on market data inputs)

### Ad Auctions and Bidding

- **Objective**: route ad placements to maximize value-per-cost; attribute conversion credit fairly
- **Stack**: #3 (auction-based routing — truthful sealed-bid for placement selection) + #4 (Shapley attribution — marginal credit across touchpoints) + #11 (prediction market — confidence-weighted CTR/conversion forecasts)
- **Add for ensemble forecasting**: #13 (reasoning-tree audit at the ensemble synthesis step)

### Security / Adversarial Contexts

- **Objective**: assess threats or verify claims in adversarial or low-trust environments
- **Stack**: #14 (per-claim credibility — independent of source reputation) + #13 (reasoning-tree audit — trace claims to evidence) + #8 (courtroom debate — structured plaintiff/defense for high-stakes go/no-go)
- **Add if ongoing risk monitoring**: #5 (reputation gating — tiered trust for data sources)

### Attribution and Revenue Sharing

- **Objective**: credit contributors fairly in joint ventures, ad funnels, or multi-contributor pipelines
- **Stack**: #4 (Shapley — marginal contribution scoring) + #5 (reputation gating — tier partners by track record) + #7 (mechanism-design synthesis — dissent required in the attribution report)

### Partnership and Negotiation

- **Objective**: design incentive-aligned partnership terms and negotiate contract parameters
- **Stack**: #6 (cooperation-defection — payoff-scale test before signing) + #5 (reputation gating — initial tier assignment) + #12 (ZOPA/BATNA — locate negotiation range per item)
- **Add for complex multi-party**: #9 (Pareto-Nash — map dominant term sets across parties)

### High-Stakes Synthesis (Any Domain)

- **Objective**: aggregate diverse inputs without majority-vote pathologies
- **Stack**: #13 (reasoning-tree audit) + #7 (mechanism-design synthesis — required dissent) + #11 (confidence betting — weight by conviction, not volume)
- **Add for act/escalate**: #20 (conformal social choice — calibrated singleton acts, multi-answer set escalates)
- **Add for adversarial inputs**: #14 (per-claim credibility)
- **Add for multi-stakeholder output**: #15 (generative social choice)

### Multi-Stakeholder Policy / Product Decisions

- **Objective**: produce an output that serves multiple distinct user segments without erasing minority signal
- **Stack**: #15 (generative social choice — maximin selection across candidate outputs) + #9 (Pareto-Nash — dominant options across user-segment objectives) + #7 (mechanism-design synthesis — truthful-revelation step)

### Agent Teams (Standard)

- **Always-on baseline**: **#1 (ECON belief briefs)** + #4 (Shapley contribution) + #7 (mechanism-design synthesis with required dissent)
- **High-stakes decisions**: add #2 (adversarial debate) or #8 (courtroom) + #11 (confidence betting) + #13 (reasoning-tree audit)
- **High-stakes act/escalate**: add #20 (conformal social choice) after confidence elicitation
- **Cross-trust delegation**: add #21 (attested delegation contracts) before auction routing or reputation updates
- **Large teams / departments**: add #22 (coalition formation routing) before final synthesis
- **Adversarial / compromised context**: add #14 (per-claim credibility)
- **Multi-objective decisions**: add #9 (Pareto-Nash) or #12 (negotiation) + #15 (generative social choice)
- **Cross-domain or ambiguous routing**: #3 (auction) for membership selection; **#16 (meta-debate role routing)** for plaintiff/defense/judge selection
- **Long-running team optimization**: #5 (reputation) + #10 (evolutionary search) + **#17 (online Shapley prompt evolution)** for high-frequency teams (50+ runs)
- **Best-of-N synthesis (discrete answer)**: **#18 (BMV)** — Optimal Weight + Inverse Surprising Popularity
- **Best-of-N synthesis (open-ended)**: **#19 (RCS)** — embedding-centroid selector across 5+ candidates

For the full agent-team applied layer (team.yaml manifest, anti-patterns, checklist), see [`../../../../agents-subagents/references/game-theory-agent-teams.md`](../../../../agents-subagents/references/game-theory-agent-teams.md).

---

## Related

- [`../../../../agents-subagents/assets/templates/debate-methods/`](../../../../agents-subagents/assets/templates/debate-methods/) — debate-method overlays (Six Hats, Pre-Mortem, Devil's Advocate, etc.)
- [`../../../../agents-subagents/assets/templates/decision-masks/`](../../../../agents-subagents/assets/templates/decision-masks/) — single-agent decision-frame overlays
- [`../../../../agents-subagents/assets/templates/composition-recipes.md`](../../../../agents-subagents/assets/templates/composition-recipes.md) — full archetype-to-stack recipes for agent-team scenarios
