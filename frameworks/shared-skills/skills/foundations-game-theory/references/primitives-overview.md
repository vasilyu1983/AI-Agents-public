---
description: Domain-agnostic overview of 22 game-theory primitives. For the agent-team applied recipe layer, see agents-subagents/references/game-theory-agent-teams.md.
last_verified: 2026-05-08
status: stable
---

# Game-Theory Primitives Overview

## Table of Contents

- [Why Mechanism Design Matters](#why-mechanism-design-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Mechanism Design Matters

Strategic decisions are games. Each participant optimizes for their own objective, but system outcomes depend on the combination of all participants' actions. Without intentional mechanism design:

| Failure Mode | Game Theory Diagnosis | What Goes Wrong |
|-------------|----------------------|-----------------|
| Attribution defaults to seniority or loudness | No marginal-contribution tracking — free-riding equilibrium | Poor performers retained; top performers under-credited |
| Synthesis averages diverse inputs | No incentive to produce a distinctive position | Decisions reflect no one's evidence well |
| Majority vote passes correlated errors | Shared biases — participants agree on wrong answers | Hallucinations and false claims survive aggregation |
| One voice dominates negotiation | Unequal information or authority asymmetry | ZOPA is never found; value is left on the table |
| Trust is applied uniformly | Track record differences ignored | High-risk participants get the same autonomy as proven ones |

Each primitive in the index below addresses a specific failure mode.

---

## Primitive Index

22 primitives, each in its own playbook under [`../assets/templates/game-theory/`](../assets/templates/game-theory/). The table includes primary domain applications — each primitive applies across all listed domains, not just agent teams.

| # | Primitive | Failure Mode | Primary Domains |
|---|-----------|-------------|-----------------|
| 1 | [Belief-Driven Coordination (ECON)](../assets/templates/game-theory/01-econ-belief-driven.md) | Pooling equilibrium — overlapping analysis from shared context | Multi-party teams, distributed analysis, agent teams |
| 2 | [Adversarial Debate](../assets/templates/game-theory/02-adversarial-debate.md) | Confabulation consensus, correlated bias | Content moderation, risk review, audit, agent teams |
| 3 | [Auction-Based Routing](../assets/templates/game-theory/03-auction-task-routing.md) | Static routing, ambiguous selection | Ad bidding, task delegation, resource allocation |
| 4 | [Shapley Contribution](../assets/templates/game-theory/04-shapley-contribution.md) | Free-riding, unverifiable attribution | Revenue sharing, team composition, ad attribution |
| 5 | [Reputation-Gated Autonomy](../assets/templates/game-theory/05-reputation-gating.md) | Uniform trust regardless of track record | Supplier qualification, fraud gating, agent oversight |
| 6 | [Cooperation and Defection](../assets/templates/game-theory/06-cooperation-defection.md) | Shallow output, scope dumping, echo chambers | Partnership design, incentive alignment, compliance |
| 7 | [Mechanism Design for Synthesis](../assets/templates/game-theory/07-mechanism-design-synthesis.md) | Loudest-wins aggregation, suppressed dissent | Decision aggregation, policy-making, any synthesis step |
| 8 | [Courtroom-Style Debate](../assets/templates/game-theory/08-courtroom-proclaim.md) | Evidence stagnation, position-anchored reasoning | Legal review, risk go/no-go, security claim verification |
| 9 | [Pareto-Nash Multi-Objective](../assets/templates/game-theory/09-pareto-nash.md) | Single-objective optimization on multi-objective problems | Product tradeoffs, regulatory vs growth, pricing |
| 10 | [Evolutionary Coordination Search](../assets/templates/game-theory/10-alphaevolve.md) | Hand-tuned rules sub-optimal vs. measured fitness | Algorithm selection, prompt tuning, rule optimization |
| 11 | [Prediction Market / Confidence Betting](../assets/templates/game-theory/11-prediction-market.md) | Verbose output dominates synthesis | Forecasting, risk calibration, ensemble weighting |
| 12 | [Negotiation Protocol (ZOPA/BATNA)](../assets/templates/game-theory/12-negotiation-zopa-batna.md) | Adversarial framing on genuine compromises | Pricing negotiation, partnership terms, resource contention |
| 13 | [Reasoning-Tree Audit](../assets/templates/game-theory/13-reasoning-tree-audit.md) | Confident-but-wrong consensus; majority vote unsafe | High-stakes synthesis, compliance review, claim checking |
| 14 | [Per-Claim Credibility Scoring](../assets/templates/game-theory/14-credibility-scoring.md) | Single-claim failure modes reputation gating misses | Misinformation detection, adversarial content, security |
| 15 | [Generative Social Choice](../assets/templates/game-theory/15-generative-social-choice.md) | Multi-stakeholder buy-in; averaging erases minority evidence | Multi-stakeholder policy, diverse-user product decisions |
| 16 | [Meta-Debate Role Routing](../assets/templates/game-theory/16-meta-debate-routing.md) | Wrong-specialist gets wrong debate role | Debate setup, agent teams, jury / panel selection |
| 17 | [Online Shapley Prompt Evolution](../assets/templates/game-theory/17-online-shapley-prompt-evolution.md) | Weak members never improve; static prompts | High-frequency teams, prompt tuning |
| 18 | [Beyond Majority Voting (BMV)](../assets/templates/game-theory/18-beyond-majority-voting.md) | Majority vote on best-of-N erases minority-correct answers | Best-of-N (discrete), ensemble selection, agent teams |
| 19 | [Radial Consensus Score (RCS)](../assets/templates/game-theory/19-radial-consensus-score.md) | Lexical-overlap voting fails on semantically clustered answers | Best-of-N (open-ended), self-consistency |
| 20 | [Conformal Social Choice](../assets/templates/game-theory/20-conformal-social-choice.md) | Wrong consensus turns into irreversible action | High-stakes debate, release gates, legal/payments/security |
| 21 | [Attested Delegation Contracts](../assets/templates/game-theory/21-attested-delegation-contracts.md) | Self-claimed quality corrupts routing | Cross-trust subagents, tools, plugins, external services |
| 22 | [Coalition Formation Routing](../assets/templates/game-theory/22-coalition-formation-routing.md) | Large flat panels duplicate work and overload synthesis | Departments, incident boards, large audits, multi-workstream teams |

---

## Anti-Patterns by Domain

### Pricing and Monetization

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Single price point tested without tradeoff mapping | Single-objective optimization | Pareto-Nash (#9) maps revenue × retention frontier |
| Negotiation as adversarial debate | Positions harden; ZOPA never found | BATNA/ZOPA protocol (#12) with interests, not positions |
| Synthesis averages price scenarios | Minority-correct low-price signal erased | Generative social choice (#15) preserves outlier signal |

### Ad Bidding and Attribution

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Last-touch attribution | Free-riding by mid-funnel channels | Shapley marginal-contribution (#4) across the funnel |
| Static routing to top bidder | True fit not measured | Cost-effectiveness auction (#3) scores value per cost |
| Flat confidence on forecasts | Overconfident models dominate ensemble | Prediction market confidence betting (#11) with CritiCal calibration |

### Security and Adversarial Contexts

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Reputation gating per-participant only | Injected claims from trusted participant pass | Per-claim credibility scoring (#14) independent of sender |
| Majority vote on adversarial inputs | Coordinated false claims achieve plurality | Reasoning-tree audit (#13) traces each claim to primary evidence |
| Single evaluator on high-stakes decisions | No adversarial challenge | Courtroom protocol (#8) with explicit plaintiff and defense |
| Agreement treated as authorization | Wrong consensus acts without a safety valve | Conformal social choice (#20) converts uncertainty into escalation |
| Delegate claims capability cheaply | Router selects inflated or unverified quality | Attested delegation contracts (#21) require verified identity/capability |

### Partnerships and Cooperation

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Flat trust assumed for new partners | Track record not collected | Reputation-gated tiers (#5) start all partners on probationary |
| Cooperation assumed without incentive alignment | Defection is rational if undetected | Iterated PD payoff-scale test (#6) surfaces tendency early |
| Attribution of joint outcomes unclear | Partners dispute share post-hoc | Shapley split (#4) agreed pre-launch |
| Large partner group forced into one panel | Coalitions form implicitly and destabilize synthesis | Coalition formation routing (#22) makes subgroups explicit |

---

## Decision Checklist

This checklist applies to any strategic decision system — pricing, bidding, partnerships, agent teams, or policy.

- [ ] **Routing problem**: Multiple options with measurable fit? → auction (#3)
- [ ] **Attribution problem**: Multiple contributors to a shared outcome? → Shapley (#4)
- [ ] **Synthesis problem**: Claims with varying quality or confidence? → reasoning-tree audit (#13) + mechanism-design synthesis (#7)
- [ ] **Trust heterogeneity**: Participants with different track records? → reputation gating (#5)
- [ ] **Multi-objective tradeoff**: Incommensurable objectives? → Pareto-Nash (#9) or negotiation (#12)
- [ ] **High-stakes binary decision**: Needs audit trail? → courtroom debate (#8)
- [ ] **Adversarial context**: Claims may be injected or manipulated? → per-claim credibility scoring (#14)
- [ ] **Multi-stakeholder output**: Multiple user types with different needs? → generative social choice (#15)
- [ ] **Confidence calibration needed**: Forecast or probabilistic claim? → prediction market (#11)
- [ ] **Long-running repeatable system**: Measurable quality signal over many runs? → evolutionary search (#10)
- [ ] **Cooperation incentives unclear**: Will defection be rational? → cooperation-defection payoff structure (#6)
- [ ] **Dissent suppressed in aggregation**: Minority-correct risk? → mechanism-design synthesis (#7) with required dissent section
- [ ] **Multi-party context-sharing risk**: Members may produce overlapping analysis from same context? → belief-driven coordination (#1) with explicit belief briefs
- [ ] **Best-of-N synthesis (discrete)**: Need to recover minority-correct answers? → BMV (#18)
- [ ] **Best-of-N synthesis (open-ended)**: Lexically diverse but semantically clustered candidates? → RCS (#19)
- [ ] **High-frequency team (50+ runs)**: Want to evolve prompts using Shapley signal? → online Shapley prompt evolution (#17)
- [ ] **Debate role assignment ambiguous**: Best plaintiff/defense not the obvious specialist? → meta-debate role routing (#16)
- [ ] **High-stakes act/escalate**: Consensus cannot be trusted as authorization? → conformal social choice (#20)
- [ ] **Cross-trust delegation**: Delegate can self-claim quality, authority, or identity? → attested delegation contracts (#21)
- [ ] **Large team / department**: Work naturally splits into coalitions? → coalition formation routing (#22)

---

## Sources

Use primary papers and official docs as the strongest evidence tier. Practitioner posts and secondary summaries are useful for templates, not for claiming numeric thresholds transfer across domains.

- ECON (referenced for context): Bayesian Nash equilibrium for multi-LLM coordination (ICML 2025). [arxiv.org/abs/2506.08292](https://arxiv.org/abs/2506.08292)
- A-HMAD: Adaptive heterogeneous multi-agent debate. +4-6% accuracy, -30% factual errors. [doi.org/10.1007/s44443-025-00353-3](https://link.springer.com/article/10.1007/s44443-025-00353-3)
- AgentAuditor: Reasoning tree audit replacing majority voting. [arxiv.org/html/2602.09341](https://arxiv.org/html/2602.09341)
- ShapleyFlow: Cooperative game theory for agentic workflow analysis. [arxiv.org/abs/2502.00510](https://arxiv.org/abs/2502.00510)
- RedDebate: Multi-agent debate + red-teaming with long-term memory. [arxiv.org/abs/2506.11083](https://arxiv.org/abs/2506.11083)
- AlphaEvolve baseline: evolutionary coding-agent search. [arxiv.org/abs/2506.13131](https://arxiv.org/abs/2506.13131)
- AlphaEvolve applied to game-theoretic MARL: VAD-CFR and SHOR-PSRO variants. [arxiv.org/abs/2602.16928](https://arxiv.org/abs/2602.16928)
- PROClaim: Courtroom-style multi-agent debate with progressive RAG and role-switching (March 2026). [arxiv.org/html/2603.28488](https://arxiv.org/html/2603.28488v1)
- Pareto-Nash Equilibrium: Multi-objective game theory for agent teams. [arxiv.org/abs/2412.20523](https://arxiv.org/abs/2412.20523)
- IJCAI-25: "Game Theory Meets Large Language Models" — pro-social bias and tacit collusion in LLM agents
- DeepMind: Game-theory insights into asymmetric multi-agent games. [deepmind.google/blog/game-theory-insights](https://deepmind.google/blog/game-theory-insights-into-asymmetric-multi-agent-games/)
- Wisdom of the Silicon Crowd: LLM ensemble prediction. Science Advances 2025. [science.org/doi/10.1126/sciadv.adp1528](https://www.science.org/doi/10.1126/sciadv.adp1528)
- AI Negotiation: practitioner dataset; useful for value-framing heuristics, not a universal benchmark. [medium.com/@fabioherle](https://medium.com/@fabioherle/building-autonomous-negotiations-that-actually-work-lessons-from-180-098-ai-negotiations-805a2f8798a4)
- HiveMind: Contribution-Guided Online Prompt Optimization of LLM Multi-Agent Systems. arXiv 2512.06432 (Dec 2025). [arxiv.org/abs/2512.06432](https://arxiv.org/abs/2512.06432)
- FAIRGAME framework: payoff-scaled iterated PD + Public Goods Games for measuring defection tendency. [arxiv.org/abs/2601.15047](https://arxiv.org/abs/2601.15047)
- Dynamic Role Assignment: meta-debate for capability-aware role routing. [arxiv.org/abs/2601.17152](https://arxiv.org/abs/2601.17152)
- Beyond Majority Voting: OW and ISP aggregation. [arxiv.org/abs/2510.01499](https://arxiv.org/abs/2510.01499)
- Radial Consensus Score: embedding-geometry best-of-N selection. [arxiv.org/abs/2604.12196](https://arxiv.org/abs/2604.12196)
- Conformal Social Choice: calibrated act/escalate for multi-agent debate. [arxiv.org/abs/2604.07667](https://arxiv.org/abs/2604.07667)
- Provenance Paradox: attested identity and delegation contracts for multi-agent routing. [arxiv.org/abs/2603.18043](https://arxiv.org/abs/2603.18043)
- Coalition Formation in LLM Agent Networks: hedonic-game stable partitions for LLM agents. [arxiv.org/abs/2604.14386](https://arxiv.org/abs/2604.14386)
- Mapping human anti-collusion mechanisms to multi-agent AI systems. Knowledge-Based Systems 2026.
- Credibility scoring for adversary-resistant multi-agent systems. [arxiv.org/abs/2505.24239](https://arxiv.org/abs/2505.24239)
- Shapley-Coop: Credit assignment for emergent cooperation. OpenReview 2025. [openreview.net/pdf?id=HnJ1UkuJXS](https://openreview.net/pdf?id=HnJ1UkuJXS)
- MAST taxonomy: Why Do Multi-Agent LLM Systems Fail? NeurIPS 2025. [arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
- Talk Isn't Always Cheap: Failure Modes in Multi-Agent Debate. arXiv 2509.05396 (2025). [arxiv.org/abs/2509.05396](https://arxiv.org/abs/2509.05396)
- Persuasion-driven adversarial influence in multi-agent LLM debate. Nature Sci Reports 2026. [nature.com/articles/s41598-026-42705-7](https://www.nature.com/articles/s41598-026-42705-7)
- Adaptive stability detection (Beta-Binomial + KS test) for multi-agent debate convergence. OpenReview 2026. [openreview.net/forum?id=Vusd1Hw2D9](https://openreview.net/forum?id=Vusd1Hw2D9)
- Hierarchical MAS taxonomy (holonic + nested-summary patterns). arXiv 2508.12683. [arxiv.org/abs/2508.12683](https://arxiv.org/abs/2508.12683)
