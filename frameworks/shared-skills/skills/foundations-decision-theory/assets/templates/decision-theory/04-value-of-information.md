# Primitive 04 — Value of Information (VoI, EVPI, EVSI)

## Definition

Value of information quantifies how much a decision maker should pay to obtain information before acting.

**Expected Value of Perfect Information (EVPI)** — the improvement in expected utility if the decision maker could observe the true state before choosing:

```
EVPI = E_θ[ max_a u(a, θ) ] − max_a E_θ[ u(a, θ) ]
```

EVPI is the upper bound on what any information source is worth. It equals zero when the optimal action is robust to all states (no information can improve it).

**Expected Value of Sample Information (EVSI)** — the improvement when the decision maker observes a noisy signal x from an experiment with known likelihood p(x|θ):

```
EVSI = E_x[ max_a E_{θ|x}[ u(a, θ) ] ] − max_a E_θ[ u(a, θ) ]
```

EVSI ≤ EVPI always. The decision to run an experiment is worthwhile only if EVSI > experiment cost.

## When to Use

- Before approving a study, pilot, A/B test, or survey.
- When the decision is already robust (optimal action same under all scenarios): EVPI = 0; skip the study.
- When sizing a study: compute EVSI as a function of sample size to find the cost-optimal stopping point.
- When comparing two information sources (e.g., focus group vs. survey): compute EVSI for each.

## Inputs

| Input | Description |
|-------|-------------|
| Current prior p(θ) | Belief over states before any experiment |
| Payoff function u(a, θ) | Utility of each action under each state |
| Action set {aᵢ} | Available choices |
| Study design (for EVSI) | Sample size, measurement noise, likelihood p(x|θ) |
| Study cost | Monetary or time cost of obtaining the information |

## Outputs

| Output | Description |
|--------|-------------|
| EVPI | Maximum value any information can provide |
| EVSI | Expected value of the specific proposed study |
| Decision to study | Run study iff EVSI > study cost |
| Optimal sample size | n* where marginal EVSI gain equals marginal cost |

## Failure Modes

- **EVPI not computed before study approval**: Any positive-cost study may be worthless if EVPI = 0.
- **EVSI conflated with EVPI**: Assuming the study provides perfect information overstates its value. Real studies are noisy.
- **Decision horizon ignored**: EVSI only counts if the information arrives before the decision must be made. Delayed information has zero value.
- **Prior too diffuse**: Very flat priors can inflate EVPI by treating all states as equally likely; a sharper prior based on historical data may reduce EVPI substantially.
- **Multiple decision makers**: EVPI is agent-specific. If stakeholders have different utilities, compute separate EVPIs.

## Worked Example

A team is deciding whether to launch Feature F now or run a 4-week user test first (cost: £20K).

States: θ₁ = high adoption (p = 0.35), θ₂ = low adoption (p = 0.65).

Payoffs (EU, £K):

| Action | θ₁ (p=0.35) | θ₂ (p=0.65) | E[u] |
|--------|-------------|-------------|------|
| Launch now (a₁) | 300 | -80 | 0.35×300 + 0.65×(−80) = 53 |
| Hold (a₂) | 0 | 0 | 0 |

Optimal action without information: a₁ (EU = 53).

EVPI = E_θ[max_a u(a, θ)] − 53:
- In θ₁: max(300, 0) = 300; in θ₂: max(-80, 0) = 0.
- E_θ[max] = 0.35×300 + 0.65×0 = 105.
- EVPI = 105 − 53 = £52K.

The user test costs £20K < EVPI = £52K → the test is potentially worth running. Next: compute EVSI using the test's signal quality (false positive/negative rates for adoption prediction) to confirm net value.

## Decision-Focused Learning (2025–2026)

When the decision problem has a *predict-then-optimize* structure (a model predicts cost parameters, a solver uses them), VoI framing generalizes to *decision loss* — the gap between the decision made with predicted vs. true parameters. Training predictors to directly minimize decision loss rather than prediction accuracy (DFL / Smart Predict-then-Optimize) is now proven to work in *online* dynamic settings. See Capitaine et al. (ICLR 2026) for online DFL with regret bounds; Rodriguez-Diaz et al. (NeurIPS 2025) for scalable DFL via dual surrogates. Practical: applies wherever the skill's VoI primitive feeds into an optimization downstream.

**Kill criteria:** Drop if prediction targets map 1:1 to good decisions (i.e., calibrated probabilities suffice) or if the optimization problem downstream is non-differentiable and no surrogate is feasible.

## LLM-Assisted Decision Theory (2025)

When applying this primitive with LLM agents as decision support tools, **DeLLMa** (Liu et al., ICLR 2025 Spotlight, arXiv:2402.02392) operationalises EU + utility elicitation + state probability forecasting in a single inference-time pass: (1) forecast pertinent uncertain variables in-context, (2) elicit a utility function aligned with user goals, (3) identify the expected-utility-maximising action. Benchmarked across 3 LLM families on structured decision tasks, DeLLMa achieved up to a 40% accuracy improvement over direct prompting. This is the first peer-reviewed demonstration that the VoI/EU primitives (#1, #2, #4) can be operationalised by LLMs with measurable calibration.

**Kill criteria:** Drop if the decision task has no natural-language state representation (purely numerical optimisation problem) or if a formal EVPI computation is required rather than an inference-time approximation.

## EVPI for Agent Clarification, and Its Time Decay (2025–2026)

The clarify-or-commit choice — should an agent ask the user a question or proceed on its best reading? — is EVPI applied to a question rather than to a study. Two results make it directly operational:

**Scoring.** Rank candidate questions by cost-penalized EVPI, not by the agent's felt uncertainty. A question whose every possible answer leads to the same next action has zero value no matter how uncertain the agent is. Suri et al. (arXiv:2511.08798) implement this as SAGE-Agent and cut question count 1.5–2.7x against uncertainty-threshold baselines while raising task success. Their framework separates *specification* uncertainty (about user intent — askable) from *model* uncertainty (about the agent's own correctness — not askable; needs verification or retrieval instead).

**Time decay — the departure from textbook VoI.** Classical EVPI is computed once, before acting. In a long-horizon trajectory the value of the same question falls as execution proceeds, because rework cost accumulates against a fixed information gain. Gulati et al. (arXiv:2605.07937; ~6,000 runs, 4 information dimensions, 3 benchmarks, 4 frontier models) measure this: goal-level clarification decays to baseline value after roughly the first 10% of execution, input-level clarification holds to about 50%, and clarification deferred past the midpoint performs *worse* than never asking. Frontier models do not track this optimum on their own, over-asking in 52% of sessions or suppressing questions entirely.

**Practical rule:** front-load goal questions before the first action, permit input questions through mid-trajectory, and commit after the midpoint.

**Kill criteria:** Drop if the interaction is single-turn (no trajectory over which value can decay), or if asking is free and unlimited — the cost penalty is what makes the EVPI ranking bind.

## Sources

- Raiffa, H. and Schlaifer, R. (1961). Applied Statistical Decision Theory. Harvard University Press. Chapters 4–5.
- Howard, R. A. (1966). "Information Value Theory." IEEE Transactions on Systems Science and Cybernetics 2(1).
- Pratt, J. W., Raiffa, H., and Schlaifer, R. (1995). Introduction to Statistical Decision Theory. MIT Press.
- Liu, O. et al. (2025). "DeLLMa: Decision Making Under Uncertainty with Large Language Models." ICLR 2025 Spotlight. arXiv:2402.02392. https://arxiv.org/abs/2402.02392
- Capitaine et al. (2026). "Online Decision-Focused Learning." ICLR 2026. arXiv:2505.13564.
- Rodriguez-Diaz, Bansak, Paulson (2025). "A Dual Perspective on Decision-Focused Learning: Scalable Training via Dual-Guided Surrogates." NeurIPS 2025. arXiv:2511.04909.
- Suri, M. et al. (2025/2026). "Structured Uncertainty guided Clarification for LLM Agents." arXiv:2511.08798.
- Gulati, A., Gupta, H., Lumer, E., Sen, S., and Subbiah, V. K. (2026). "Ask Early, Ask Late, Ask Right: When Does Clarification Timing Matter for Long-Horizon Agents?" arXiv:2605.07937.
