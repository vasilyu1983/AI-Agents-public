# Primitive 10 — Multi-Armed Bandit (Exploration–Exploitation)

## Definition

The multi-armed bandit (MAB) problem formalizes sequential decision making under uncertainty: a decision maker chooses at each time step t which arm (option) to pull from K arms, each with an unknown reward distribution. The usual goal is to maximize cumulative reward (equivalently, minimize cumulative regret). A different goal — committing to the best arm after the test (best-arm identification, pure exploration) — needs different algorithms and stopping rules; see [thresholds-stopping-and-ope.md §3–4](../../../references/thresholds-stopping-and-ope.md#3-best-arm-identification-vs-regret).

**Regret**: The difference between the reward of always pulling the optimal arm and the actual reward accumulated:
```
Regret(T) = T · μ* − Σₜ μ_{aₜ}
```
where μ* = max_i μᵢ is the optimal arm's mean reward and μ_{aₜ} is the mean of the pulled arm at time t.

Key policies:

**Upper Confidence Bound (UCB1)** — frequentist. Pull arm i with highest:
```
UCB_i(t) = x̄ᵢ + √(2 ln t / nᵢ)
```
where x̄ᵢ is the empirical mean and nᵢ is the number of pulls. Guarantees logarithmic regret O(log T).

**Thompson Sampling (TS)** — Bayesian. Maintain a posterior Beta(αᵢ, βᵢ) for each arm; sample θᵢ from each posterior; pull the arm with the highest sample. Achieves near-optimal Bayesian regret; often outperforms UCB in practice.

**ε-Greedy** — Explore uniformly at random with probability ε; exploit the current best arm with probability 1−ε. Simple but suboptimal (linear regret unless ε decays).

## When to Use

- Allocating traffic across ad variants, product features, or recommendation strategies where performance is unknown.
- Sequential experiment slot allocation.
- Any repeated choice problem where pulling an arm provides noisy feedback about its true quality.
- Balancing learning (exploration) and performance (exploitation) explicitly.

## When NOT to Use

- You need an unbiased effect size, the decision metric is long-horizon or a guardrail, or rewards are delayed: use a fixed-allocation randomised test. Adaptive allocation biases naive per-arm means (Hadad et al. 2021).
- You will pick one winner and stop: that is best-arm identification, not regret minimisation.

## Inputs

| Input | Description |
|-------|-------------|
| K arms | Options to evaluate; assumed stationary reward distributions |
| Reward signal | Observed outcome after each pull (binary, continuous, or count) |
| Time horizon T | Number of rounds available |
| Prior (for TS) | Beta(α₀, β₀) per arm for Thompson sampling initialization |

## Outputs

| Output | Description |
|--------|-------------|
| Arm allocation policy | Which arm to pull at each step |
| Cumulative regret | Running measure of learning cost vs. optimal |
| Posterior belief | Updated distribution over each arm's true mean (TS) |
| Confidence bounds | UCB for each arm (UCB1) |

## Failure Modes

- **Non-stationary rewards**: UCB and basic TS assume stationary distributions. Sliding-window or discounted variants are needed when reward means drift over time.
- **Contextual structure ignored**: If arm performance depends on observable covariates (user features, time of day), contextual bandits (LinUCB, contextual TS) should replace stationary MAB.
- **Early exploitation before arm identification**: Greedy early commits to the wrong arm; UCB and TS maintain uncertainty pressure.
- **EVPI bound not checked**: Before investing in a bandit experiment, compute EVPI (#4). If even perfect knowledge of the best arm is worth less than the opportunity cost of exploration, skip the learning and commit on the prior. EVPI above that cost does not by itself justify the experiment.
- **Comparing arms only at first pull**: First-pull outcomes have very high variance. Thompson sampling needs sufficient pulls per arm to produce reliable posteriors.

## Worked Example

An email subject-line test across three variants (K = 3). Metric: click rate (binary reward).

Prior: Beta(1, 1) (uniform) for each arm.

After 50 rounds of Thompson sampling:

| Arm | Clicks | Sends | Empirical CTR | Posterior |
|-----|--------|-------|---------------|-----------|
| A | 8 | 20 | 40% | Beta(9, 13) |
| B | 4 | 18 | 22% | Beta(5, 15) |
| C | 3 | 12 | 25% | Beta(4, 10) |

Thompson sampling at round 51: sample θ_A, θ_B, θ_C from their posteriors. Estimate the posterior probability that each arm is best by reproducible integration or seeded Monte Carlo.

Posterior estimates (numerical integration over the three Beta posteriors; a seeded 400k-draw Monte Carlo agrees to about ±0.002): P(best) = 0.716 / 0.094 / 0.190 for A / B / C; expected loss of choosing each = 0.026 / 0.185 / 0.15 CTR.

Stopping rule: declare a threshold of caring ε before the test and ship the arm with the smallest expected loss once that loss is below ε. With ε = 0.005 CTR, keep testing; with ε = 0.03, ship A now even though P(A best) is only 0.72. A "P(best) > 0.99" rule ignores magnitude and can run forever on near-ties.

## Constrained Bandits: Best-of-Both-Worlds (ICML 2025)

When exploration must respect general long-term resource budgets, weakly adaptive primal-dual regret minimization (Bernasconi et al., ICML 2025) achieves sublinear regret in the stochastic regime and a ρ/(1+ρ) competitive ratio in the adversarial regime, with sublinear constraint violations in both.

**Kill criteria:** Drop if your bandit arms face no long-term resource constraints and inputs are always stochastic — vanilla UCB/Thompson remains optimal in that case.

## LLM Agents and PSRL (ICLR 2026)

When the bandit or MDP environment is described in natural language and the agent is an LLM, standard exploration policies (UCB, ε-greedy) are absent by default. Arumugam & Griffiths (ICLR 2026) show LLMs can *explicitly implement* Posterior Sampling for RL (PSRL) by delegating three atomic roles to distinct LLM calls: (1) approximate posterior update from trajectory, (2) posterior sample (hypothesis about the world), (3) optimal policy for that hypothesis. This provides empirical evidence of better exploration in the studied natural-language tasks. Approximate LLM posterior updates, samples and policies do not automatically inherit the exact algorithm's regret guarantees; theorem conditions require separate justification. Practical: the model underlying the PSRL implementation matters — replacing GPT-4o with o1-mini turned linear into sublinear regret in some experiments, but o1-mini also degraded to linear regret on the length-4 RiverSwim task.

**Kill criteria:** Drop if the environment is not partially observable or the action space is small enough that tabular PSRL or UCB applies directly. Drop if LLM inference cost per step exceeds the value of improved exploration.

## Sources

- Robbins, H. (1952). "Some Aspects of the Sequential Design of Experiments." Bulletin of the AMS 58.
- Auer, P., Cesa-Bianchi, N., and Fischer, P. (2002). "Finite-time Analysis of the Multiarmed Bandit Problem." Machine Learning 47.
- Thompson, W. R. (1933). "On the Likelihood that One Unknown Probability Exceeds Another in Drawing from It." Biometrika 25(3–4).
- Russo, D. J., Van Roy, B., Kazerouni, A., Osband, I., and Wen, Z. (2018). "A Tutorial on Thompson Sampling." Foundations and Trends in Machine Learning 11(1).
- Lattimore, T. and Szepesvári, C. (2020). Bandit Algorithms. Cambridge University Press.
- Bernasconi, M., Castiglioni, M., and Celli, A. (2025). "No-Regret is not enough! Bandits with General Constraints through Adaptive Regret Minimization." ICML 2025, PMLR 267:3877–3898.
- Audibert, J.-Y., Bubeck, S., and Munos, R. (2010). "Best Arm Identification in Multi-Armed Bandits." COLT 2010.
- Russo, D. (2016). "Simple Bayesian Algorithms for Best Arm Identification." arXiv:1602.08448.
- Hadad, V., Hirshberg, D. A., Zhan, R., Wager, S., and Athey, S. (2021). "Confidence Intervals for Policy Evaluation in Adaptive Experiments." arXiv:1911.02768.
- Arumugam, D. and Griffiths, T. L. (2026). "Toward Efficient Exploration by Large Language Model Agents." ICLR 2026. arXiv:2504.20997.
