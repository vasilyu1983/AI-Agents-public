# Finite-State Decision Calculator

Use `scripts/decision_calculator.py` when a decision can be represented by a small, explicit action-by-state utility matrix. It calculates expected utility, EVPI, exact finite-signal EVSI, and minimax regret. It does not elicit probabilities or utilities and does not claim that the supplied model is valid.

## Input contract

The JSON object requires:

- `states`: non-empty, unique, trimmed string names.
- `actions`: non-empty, unique, trimmed string names.
- `utilities`: one object per action and one finite numeric utility per state. Utilities must share one declared scale.

`prior` is optional. Supply exactly one probability for every state to calculate expected utility and EVPI. Omit it when probabilities are not defensible and use minimax regret alone.

`signal_likelihoods` is optional and requires a prior. It maps each possible signal to `p(signal | state)` for every state. For each state, likelihoods across all named signals must sum to one. An impossible signal, with marginal probability zero, is retained in output with a null posterior and makes no contribution to EVSI. `study_cost` defaults to zero and must be non-negative. State study cost in the same utility units and for the same affected population and decision horizon as the utility matrix.

Probabilities must sum exactly to one. JSON decimal literals are parsed as exact decimal values for this check, and the calculator never rescales or normalizes them. Unknown keys, duplicate JSON object keys, missing or extra matrix cells, duplicate or blank names, booleans, non-finite values, malformed mappings, invalid probabilities, and results too large or too small to remain nonzero as finite JSON numbers are errors.

## Calculation

For prior `p(s)` and utility `u(a,s)`, the current choice maximizes:

```text
EU(a) = sum_s p(s) u(a,s)
EVPI = sum_s p(s) max_a u(a,s) - max_a EU(a)
```

For explicit likelihoods `p(x|s)`, Bayes' rule gives `p(s|x)`. The program enumerates all possible signals and calculates:

```text
EVSI = sum_x p(x) max_a sum_s p(s|x) u(a,s) - max_a EU(a)
net EVSI = EVSI - study cost
```

The study recommendation is `run` only when EVSI exceeds cost, `skip` when it is lower, and `indifferent` on a tie. EVPI exceeding cost only establishes that some information could be worth buying; it does not establish that the proposed signal is valuable enough.

Without probabilities, regret in state `s` is the best utility available in that state minus an action's utility. Minimax regret selects every action tied for the smallest worst-state regret.

## Output interpretation

The calculator uses exact rational arithmetic internally and treats actions as tied only when their calculated values are equal. It converts results to finite JSON numbers at the output boundary. With a prior it reports expected utility by action, the current value and choices, and EVPI. With a signal model it also reports each signal's marginal probability, posterior, posterior expected utilities and choices, plus EVSI, cost, net EVSI, and the study recommendation. Minimax regret is always reported.

All values are conditional on the stated states, utilities, prior, and signal model. If changing scenario bounds, utility scale, or defensible probabilities could change the choice, report that sensitivity rather than treating the output as decision authority.

## Source and known answer

Heath and Baio, “Calculating the Expected Value of Sample Information using Efficient Nested Monte Carlo: A Tutorial,” [arXiv:1709.02319](https://arxiv.org/pdf/1709.02319), section 2, defines EVSI from posterior-optimal decisions averaged over possible future data. This calculator performs the corresponding exact enumeration for a finite signal space; it does not implement the paper's later Monte Carlo approximation.

The fixture `data/finite-state-decision-fixtures.json` includes the symmetric check: an action pays `+1/-1` under a `0.5/0.5` prior, an outside action pays zero, and a symmetric signal is correct with probability `0.75`. The exact results are EVPI `0.5` and EVSI `0.25`. This also shows why a percentage reduction in posterior variance cannot be multiplied by EVPI to obtain EVSI.
