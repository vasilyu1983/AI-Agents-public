# Primitive 2: Mutual Information

## Definition

**Mutual information** between random variables X and Y:

```
I(X;Y) = H(X) − H(X|Y)
        = H(Y) − H(Y|X)
        = H(X) + H(Y) − H(X,Y)
        = Σ_{x,y} p(x,y) log [ p(x,y) / (p(x) p(y)) ]
```

I(X;Y) ≥ 0 always; I(X;Y) = 0 iff X and Y are independent.

**Relation to KL divergence**:

```
I(X;Y) = D_KL( p(x,y) ‖ p(x)p(y) )
```

MI measures the KL divergence between the joint distribution and the product of marginals.

**Conditional mutual information**:

```
I(X;Y|Z) = H(X|Z) − H(X|Y,Z)
```

**Chain rule for MI**:  I(X₁,...,Xₙ; Y) = Σ_i I(Xᵢ;Y | X₁,...,Xᵢ₋₁)

**Normalized variants** (for bounded scoring):

```
NMI(X;Y) = I(X;Y) / sqrt(H(X)·H(Y))         [0,1], geometric mean normalization
UMI(X;Y) = I(X;Y) / min(H(X), H(Y))          [0,1], upper-bounded by less entropic variable
```

**Continuous MI** (via differential entropy):

```
I(X;Y) = h(X) + h(Y) − h(X,Y)                [transform-invariant; can be estimated from data]
```

Continuous MI is transform-invariant under invertible maps, making it a valid dependency measure where differential entropy alone is not.

---

## When to Use

- Ranking features by relevance to a target variable (feature selection).
- Scoring retrieval candidates by how much each document reduces query uncertainty.
- Detecting non-linear statistical dependence (captures relationships that correlation misses).
- Measuring information flow between representations in a neural network (see IB, primitive #8).
- Quantifying redundancy between two information sources before merging them.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Joint distribution p(x,y) | PMF or samples | Empirical co-occurrences or known distribution |
| Marginals p(x), p(y) | Derived or known | Can be computed from joint or marginal samples |
| Sample size n | Integer | Must be large relative to |X|·|Y| for reliable estimation |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| I(X;Y) | Non-negative real | [0, min(H(X),H(Y))] | Average bits X reveals about Y |
| NMI(X;Y) | Real | [0, 1] | Normalized relevance score |
| I(X;Y\|Z) | Non-negative real | [0, ...] | Relevance of X to Y after conditioning on Z |

---

## Failure Modes

1. **Positive bias from finite samples**: Plug-in MI estimates are positively biased. For m×n contingency table with N samples, bias ≈ (m−1)(n−1)/(2N). Use JVHW or NSB correction for discrete variables; MINE or NWJ for continuous.
2. **High-dimensional curse**: In high dimensions, MI estimates from k-NN methods require exponentially more samples. Always report confidence intervals; treat raw MI values from >20 dimensions with suspicion.
3. **MI ≠ causal influence**: I(X;Y) > 0 does not imply X causes Y. Spurious MI arises from common causes. Apply conditional MI I(X;Y|Z) to partial out confounders.
4. **NMI normalization choice matters**: Geometric-mean NMI vs. min-based UMI produce different rankings. Always state which normalization is in use; min-normalization is sharper when one variable has much lower entropy.
5. **Discrete vs. continuous estimation mismatch**: Discretizing continuous variables to compute discrete MI introduces binning bias. Prefer k-NN or kernel-based estimators for continuous data.

---

## Worked Example

**Retrieval reranking with redundancy penalty**

Query q, five candidate documents d₁–d₅. Estimated I(q;dᵢ) (bits) and pairwise redundancy I(dᵢ;d₃) for the document closest to d₃:

| Doc | I(q;dᵢ) | I(dᵢ;d₃) | Marginal gain if d₃ selected |
|-----|---------|----------|------------------------------|
| d₁  | 3.2     | 0.1      | 3.1 |
| d₂  | 2.9     | 0.2      | 2.7 |
| d₃  | 3.5     | —        | 3.5 (first pick) |
| d₄  | 2.4     | 2.1      | 0.3 (near-duplicate of d₃) |
| d₅  | 1.8     | 0.4      | 1.4 |

Budget: top 3. Naive relevance-only ranking: d₃, d₁, d₂. Redundancy-penalized ranking: d₃, d₁, d₂ (same here — d₄ drops because I(d₄;d₃) = 2.1, leaving marginal gain of only 0.3 bits). d₄ would appear as top-3 with cosine-similarity scoring but carries minimal new information.

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 2. Wiley.
- Belghazi, M. I. et al. (2018). MINE: Mutual Information Neural Estimation. *ICML 2018*. https://arxiv.org/abs/1801.04062
- Paninski, L. (2003). Estimation of entropy and mutual information. *Neural Computation*, 15(6), 1191–1253.
- Valiant, G. & Valiant, P. (2011). Estimating the unseen. *STOC 2011*. (JVHW estimator.)
- Kraskov, A., Stögbauer, H. & Grassberger, P. (2004). Estimating mutual information. *Physical Review E*, 69(6). (k-NN estimator.)
