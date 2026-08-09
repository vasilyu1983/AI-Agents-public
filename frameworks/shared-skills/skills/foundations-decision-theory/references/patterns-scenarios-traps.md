---
description: Applied patterns, scenarios, anti-patterns, and known traps for decision-theory foundations.
last_verified: 2026-05-02
status: stable
---

# Decision Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Launch gate | Need go/no-go under uncertainty | EU -> risk aversion -> VoI |
| Research approval | Team wants an experiment first | EVPI -> EVSI -> study cost |
| Roadmap ranking | Multiple criteria compete | MCDA -> sensitivity -> real options |
| Ambiguous market bet | Probabilities are disputed | Minimax regret -> scenario analysis |
| Adaptive allocation | Options reveal performance over time | Bandit -> guardrails -> dominance check |
| Deep uncertainty | Probabilities unknowable; large or high-dimensional scenario space | RDM (Lempert 2003) → scenario discovery (PRIM) → strategy robustness check |
| Multi-stage adaptive planning | Long-horizon decisions with observable threshold-crossings across > 2 stages | DAPP (Haasnoot 2013) → pathway map → tipping-point triggers |

## Known Traps

- Expected value is not expected utility.
- EVPI is an upper bound; most real studies have lower EVSI.
- MCDA rankings can reverse under small weight changes.
- Real options require uncertainty to resolve before the option expires.
- Bandits optimize measured reward, not necessarily product quality or fairness.
- Stochastic dominance avoids specifying utility only under the relevant dominance order.
- **Minimax regret requires a finite, enumerable state space.** For high-dimensional deep uncertainty where the scenario space cannot be fully enumerated, use the RDM scenario-discovery approach (Lempert et al. 2003) instead of a regret matrix.
- **Info-gap note:** When no reference distribution and no enumerable state space exist (severe uncertainty), info-gap theory (Ben-Haim 2006) seeks the action that maximises robustness to uncertainty while meeting a satisficing threshold. Note: the framework has been critiqued as a variant of maximin (Sniedovich 2010/2011); evaluate carefully before use.
- **Ergodicity note:** For repeated or leveraged bets (returns, survival, compounding debt), the ensemble-average EU calculation and the time-average growth rate diverge whenever a ruin state exists (Peters 2019). Check for an absorbing floor before trusting a positive-EV recommendation; see the "When Expected-Value Reasoning Breaks Down" section in `SKILL.md` and the Kelly-criterion addition in `assets/templates/decision-theory/06-risk-aversion.md`.

## Exit Checklist

- [ ] Action set and state space are explicit.
- [ ] Probability source is named.
- [ ] Utility/loss function is stated.
- [ ] Experiment value is compared with experiment cost.
- [ ] MCDA weights have sensitivity analysis.
- [ ] Sequential policies have guardrails and stopping rules.
