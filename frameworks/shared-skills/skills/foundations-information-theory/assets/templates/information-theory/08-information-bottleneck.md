# Primitive 8: Information Bottleneck

## Definition

**Information Bottleneck (IB)** — Tishby, Pereira & Bialek (2000): find a compressed representation T of input X that retains maximum information about a relevant variable Y, while discarding irrelevant information.

**IB objective** (Lagrangian form):

```
min_{p(t|x)} [ I(X; T) − β · I(T; Y) ]
```

where:
- I(X;T) = information retained about the input X (compression cost — minimize)
- I(T;Y) = information about the target Y preserved in T (relevance — maximize)
- β > 0 = Lagrange multiplier (tradeoff: β→0 maximizes compression; β→∞ minimizes information loss)

**IB curve**: the Pareto frontier in the I(T;X) vs. I(T;Y) plane. For horizontal I(T;X) and vertical I(T;Y), relevance above the maximal achievable frontier is unachievable; dominated achievable points below it are suboptimal. State axes before interpreting a plot.

**IB self-consistency equations** (iterative solution for discrete case):

```
p(t|x) ∝ p(t) · exp(−β · D_KL(p(y|x) ‖ p(y|t)))
p(t)   = Σ_x p(x) p(t|x)
p(y|t) = Σ_x p(y|x) p(x|t)
```

Solved by alternating minimization (analogous to EM or the Blahut-Arimoto algorithm).

**Deep learning view** — Schwartz-Ziv & Tishby (2017): internal network layers form a bottleneck that progressively compresses X while retaining I(T;Y). Phases: "fitting" (I(T;Y) grows) then "compression" (I(X;T) decreases).

**Variational IB** (Alemi et al. 2017): approximates IB for high-dimensional X,Y using variational bounds on MI, enabling gradient-based optimization:

```
Maximize: I(Z;Y) − β_vib I(Z;X)
Minimize surrogate: E[-log p(y|z)] + β_vib KL(q(z|x) ‖ p(z))
The multiplier convention differs from the compression-minus-β-relevance IB form above
```

---

## When to Use

- **Representation learning**: designing embeddings that retain task-relevant signal while discarding noise or domain shift.
- **Prompt compression**: finding the minimal prompt that preserves I(T;Y) where Y is the desired output.
- **Feature extraction for robustness**: minimizing I(X;T) reduces sensitivity to spurious correlations in X.
- **Diagnosing deep networks**: plotting the IB curve for each layer reveals whether the network is in the fitting or compression phase.
- **Privacy-utility tradeoff**: minimize I(T; sensitive_attribute) subject to I(T; useful_attribute) ≥ threshold.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Input X | Random variable | Source to be compressed |
| Target Y | Random variable | Relevant information to preserve |
| β | Real > 0 | Compression-relevance tradeoff; sweep to trace the IB curve |
| p(x,y) | Joint distribution | Empirical or known joint distribution |

---

## Outputs

| Output | Type | Interpretation |
|--------|------|----------------|
| T (representation) | Compressed variable | Bottleneck variable; I(T;X) is its complexity |
| I(T;Y) | Non-negative real | Preserved task-relevant information |
| I(T;X) | Non-negative real | Retained input information (compression cost) |
| IB curve | Pareto frontier | Achievable (I(T;X), I(T;Y)) tradeoffs |

---

## Failure Modes

1. **IB β controls compression monotonically**: Globally optimized relevance/compression tradeoffs can be monotone yet discontinuous. Finite/discrete distributions have phase transitions; local optimization and estimator noise can also distort the observed curve. Sweep β and check the objective and solver assumptions rather than equating a jump with nonmonotonicity.
2. **IB interpretation of deep learning generalization**: Saxe et al. (2018) showed the IB compression phase Schwartz-Ziv & Tishby observed depends on the choice of MI estimator and activation function. Do not assert IB explains DNN generalization without validating estimator choice and architecture.
3. **VIB β ≠ IB β**: The variational bound introduces a gap; the VIB β controlling KL penalty does not directly correspond to the IB β controlling the theoretical tradeoff. Empirical calibration of β is required.
4. **MI estimation noise in high dimensions**: IB requires estimating I(X;T) and I(T;Y) in high-dimensional embedding spaces. Bias and variance in the MI estimator can produce misleading IB curves. Use binned estimates with multiple runs to check stability.
5. **Using IB for features without a defined Y**: IB requires a supervision signal Y. Unsupervised compression does not optimize the IB objective — use rate-distortion theory (#6) or MDL (#7) instead.

---

## Worked Example

**Prompt compression via IB framing**

A 500-token prompt P is used to generate a 50-token response R. We want to compress P to T ≤ 100 tokens while preserving I(T;R).

The following hypothetical population-information values illustrate the tradeoff; they are not measured results. A 1,000-pair plug-in histogram cannot estimate 18.2 bits of mutual information because its empirical entropy is at most log2(1000). A model-based estimator would need separate validation and uncertainty reporting:

| Tokens in T | I(T;P) [bits] | I(T;R) [bits] | I(T;R)/I(P;R) [retention] |
|-------------|--------------|--------------|--------------------------|
| 500 (full)  | 18.2         | 4.1          | 100% |
| 300         | 12.4         | 3.9          | 95% |
| 150         | 7.3          | 3.6          | 87.805% |
| 100         | 5.0          | 3.1          | 76% |
| 50          | 3.1          | 1.8          | 44% |

The hypothetical values illustrate that compressing to 150 tokens retains approximately 87.805% of task-relevant information while discarding 60% of input complexity. The 100-token target hits a cliff in I(T;R) — the illustrative retention is lower. These points do not prove a Pareto frontier. If a predeclared task-quality threshold requires at least 88% retention under a validated estimator, the unrounded 3.6/4.1 = 87.805% at 150 tokens does not meet it; 300 tokens (3.9/4.1 = 95.122%) does. Never round a threshold failure into a pass; otherwise choose by actual downstream utility and cost.

---

## Sources

- Tishby, N., Pereira, F. C. & Bialek, W. (2000). The information bottleneck method. *arXiv:physics/0004057*. https://arxiv.org/abs/physics/0004057
- Tishby, N. & Schwartz-Ziv, R. (2017). Opening the black box of deep neural networks via information. *arXiv:1703.00810*. https://arxiv.org/abs/1703.00810
- Alemi, A. A. et al. (2017). Deep variational information bottleneck. *ICLR 2017*. https://arxiv.org/abs/1612.00410
- Saxe, A. M. et al. (2018). On the information bottleneck theory of deep learning. *ICLR 2019*. https://arxiv.org/abs/1805.05815 (IB rebuttal.)
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 2–3. Wiley.
