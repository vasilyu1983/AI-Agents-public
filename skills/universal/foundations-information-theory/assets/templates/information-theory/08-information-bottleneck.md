# Primitive 8: Information Bottleneck

## Definition

Find a representation T of X (with T ← X → Y, so T carries no Y information beyond X) that solves min over p(t|x) of I(X;T) − β I(T;Y), β > 0 (Tishby, Pereira & Bialek 2000). Small β favors compression; large β favors relevance. By the data-processing inequality, I(T;Y) ≤ I(X;Y).
IB curve: frontier of achievable (I(T;X), I(T;Y)); state axes before reading a plot.
Discrete self-consistent solution: p(t|x) ∝ p(t) exp(−β D_KL(p(y|x) ‖ p(y|t))), iterated like Blahut–Arimoto.

**Variational IB** (Alemi et al., ICLR 2017) maximizes I(Z;Y) − β I(Z;X) via the surrogate: minimize E[−log q(y|z)] + β KL(q(z|x) ‖ r(z)), i.e. the negative log-likelihood of the target plus β times a KL rate term. Here β multiplies the compression term, the opposite convention from the Lagrangian above; VIB β does not equal IB β.

## Traps

1. **No Y, no IB.** Unsupervised compression is rate-distortion (#6) or MDL (#7).
2. **β is not a monotone knob.** Finite or discrete problems show phase transitions and jumps; sweep β densely and check solver assumptions.
3. **IB is not settled DNN theory.** Saxe et al. (2018) showed compression phases depend on activation and MI estimator. Newer reformulations are contested; treat IB as a design lens.
4. **Estimator noise** in high-dimensional I(X;T), I(T;Y) produces misleading curves; report estimator and seeds.
5. **Plug-in limits.** A histogram over N samples cannot estimate more than log₂ N bits of MI; 1,000 pairs cap at about 9.97 bits.
6. **Agent handoffs.** "Quantize rather than truncate" rests on one synthetic robotics MARL study (Farooq & Iqbal, ICRA 2026); it is an untested hypothesis for LLM summaries or KV caches.

## Known answer (hypothetical values)

Prompt compression with a predeclared requirement of at least 88% retention, where retention = I(T;R)/I(P;R) and I(P;R) = 4.1 bits:

| Tokens in T | I(T;R) bits | Retention |
|---|---|---|
| 300 | 3.9 | 3.9/4.1 = 0.951220 |
| 150 | 3.6 | 3.6/4.1 = 0.878049 |

150 tokens fails the threshold (87.805% < 88%); do not round a failure into a pass. 300 tokens (95.122%) is the smallest listed size that qualifies. These are illustrative values, not measured results, and do not prove a Pareto frontier; choose by validated downstream utility and cost.

## Sources

Tishby, Pereira & Bialek (2000), arXiv:physics/0004057; Alemi et al. (2017), arXiv:1612.00410; Saxe et al. (2018), arXiv:1805.05815; Tishby & Schwartz-Ziv (2017), arXiv:1703.00810. Full references: [`../../../data/sources.json`](../../../data/sources.json).
