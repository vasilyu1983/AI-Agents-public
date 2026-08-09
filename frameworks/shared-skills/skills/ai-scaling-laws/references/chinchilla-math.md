## Table of Contents

- [Overview](#overview)
- [The L(N,D) Loss Form](#the-lnd-loss-form)
- [The 20:1 Ratio — Derivation Intuition](#the-201-ratio--derivation-intuition)
- [Worked Numbers from Hoffmann et al.](#worked-numbers-from-hoffmann-et-al)
- [Comparison: Kaplan vs Chinchilla](#comparison-kaplan-vs-chinchilla)
- [Caveats and Limitations](#caveats-and-limitations)
- [Canonical Source](#canonical-source)

---

## Overview

Hoffmann et al. (2022) — colloquially "Chinchilla" — established that for a fixed compute budget the optimal strategy is to scale model size and training tokens *equally*, with roughly 20 training tokens per model parameter. This reference explains the mathematical form of that result and how to apply it numerically.

## The L(N,D) Loss Form

Hoffmann et al. fit a parametric loss function of the form:

```
L(N, D) = E + A / N^α + B / D^β
```

Where:
- `L` is the expected validation cross-entropy loss (nats)
- `N` is the number of non-embedding model parameters
- `D` is the number of training tokens
- `E` is the irreducible loss (entropy of the data distribution; approximately 1.69 nats for the Chinchilla corpus)
- `A`, `B`, `α`, `β` are fitted constants

**Fitted constants as published (Hoffmann et al. Table 3, Approach 3):**
```
A ≈ 406.4
B ≈ 410.7
α ≈ 0.336
β ≈ 0.283
E ≈ 1.69
```

> **Correction (Besiroglu et al. 2024 — read before quoting these as fact).** A replication of Approach 3 found Hoffmann et al.'s published parametric fit is **inconsistent with their own first two estimation methods**, fails to fit the extracted data, and reports confidence intervals far too narrow to be plausible (intervals that narrow would require ~600,000 experiments; they ran fewer than ~500). Two causes: the optimizer stopped before convergence due to a poor loss-scale choice, and the body-text constants are rounded enough to bias predictions. The corrected re-fit yields **α ≈ 0.35 and β ≈ 0.37** (closer to equal, i.e. α ≈ β), which is consistent with Approaches 1–2 and pushes the optimal token/param ratio modestly higher. **Use the corrected exponents for any serious projection; treat the published constants above as the historical, biased fit.** Source: arXiv 2404.10102.

These constants are fit on a specific corpus (MassiveText) and a specific architecture family. They do not transfer exactly to other corpora or architectures without re-fitting — and, per the correction above, the *original published* fit itself should not be treated as ground truth.

## The 20:1 Ratio — Derivation Intuition

To find the compute-optimal (N*, D*) pair for a fixed budget C, minimize L(N, D) subject to the constraint C = 6 N D.

Substituting the constraint (D = C / 6N) into L(N, D) and taking the derivative with respect to N, then setting to zero gives:

```
α × A / N*^(α+1)  =  β × B / D*^(β+1)
```

Solving this optimality condition with the fitted constants yields the approximate relationship:

```
N* ∝ C^0.50,   D* ∝ C^0.50
```

Both scale as C^{0.5}, meaning **both model size and training tokens should double when compute doubles**. This is the Chinchilla finding, in contrast to Kaplan et al. who found N ∝ C^{0.73} (scale model much faster than data).

The 20:1 heuristic (D* ≈ 20 × N*) comes from evaluating the optimality condition numerically at the constants above. Across the range of compute budgets studied (roughly 10^19 to 10^24 FLOPs), the optimal ratio D*/N* is approximately 20.

**Important:** The exact coefficient varies. Some analyses suggest 15–25 depending on corpus quality and architecture. 20 is a practical working estimate, not a physical constant.

## Worked Numbers from Hoffmann et al.

Selected optimal (N*, D*) pairs from the paper (Table A3, Approach 3):

| Compute C (FLOPs) | N* (params) | D* (tokens) | D*/N* |
|-------------------|-------------|-------------|-------|
| 1e19              | 400M        | 8B          | 20    |
| 1e20              | 1B          | 25B         | 25    |
| 1e21              | 4B          | 80B         | 20    |
| 1e22              | 13B         | 260B        | 20    |
| 1e23              | 40B         | 850B        | ~21   |
| 1e24              | 130B        | 2.7T        | ~21   |

**Chinchilla itself:** 70B parameters, 1.4T tokens. This is approximately 20:1 and was trained at roughly the same compute as GPT-3 (175B, ~300B tokens). Chinchilla outperforms GPT-3 on most benchmarks despite being 2.5× smaller.

**GPT-3 comparison:** At 175B params and 300B tokens, GPT-3 has a ratio of ~1.7:1 — massively under-trained by Chinchilla standards. The Chinchilla-optimal model at GPT-3's compute would be approximately 67B params trained on ~1.3T tokens.

## Comparison: Kaplan vs Chinchilla

| Property | Kaplan et al. (2020) | Chinchilla (2022) |
|----------|---------------------|-------------------|
| Optimal N scaling | N* ∝ C^{0.73} | N* ∝ C^{0.50} |
| Optimal D scaling | D* ∝ C^{0.27} | D* ∝ C^{0.50} |
| Implied D/N at 10^{23} FLOPs | ~2 | ~20 |
| GPT-3 verdict | Near-optimal | Severely under-trained |
| Dominant constraint in practice (2020 view) | Model size | Model size + data jointly |

Kaplan et al.'s finding was influenced by: not fully optimizing learning rate schedules at each model size, and not training models to full convergence. When Hoffmann et al. controlled for both, the optimal ratio shifted dramatically toward more data.

**The modern (2024) reconciliation — Kaplan was not simply "wrong."** Two 2024 papers (Pearce & Song, *Reconciling Kaplan and Chinchilla Scaling Laws*, arXiv 2406.12907; Porian et al., *Resolving Discrepancies in Compute-Optimal Scaling*, arXiv 2406.19146) show the disagreement is almost entirely **methodological**, attributable to three factors:
1. **Parameter counting** — Kaplan counted *non-embedding* params and ran at small scale, where the embedding/head FLOPs are a large fraction of the total; counting *all* FLOPs (head + embedding) is required for an unbiased coefficient.
2. **Warmup duration** — a fixed (non-scaled) warmup over-penalizes small models, skewing the power law.
3. **Scale-dependent optimizer tuning** — per-model LR/optimizer tuning is needed; reusing one config across sizes biases the exponent.

Correct all three and Kaplan's setup reproduces Chinchilla's N* ∝ C^0.50. Treat the Kaplan/Chinchilla split as "two correct-given-their-method results," not "old wrong vs new right." Note the tension with the scaling-law convention of fitting `L(N,D)` on non-embedding `N`: the convention is fine *inside a fixed fit*, but mixing conventions across the compute-optimal coefficient debate is exactly what produced the historical confusion.

## Caveats and Limitations

1. All constants are fit on MassiveText (a web-text-heavy corpus). Different corpora will yield different effective constants. Code-heavy or domain-specific corpora typically have lower irreducible entropy and different curvature.

2. The power-law form L = E + A/N^α + B/D^β is an approximation. It fits well in the 10^19 – 10^24 FLOP range but its extrapolation behavior at very large or very small compute is unknown.

3. The formula uses non-embedding parameters. Including embedding parameters in N will give incorrect results.

4. More recent empirical fits (e.g., Epoch AI, 2023) suggest the D/N optimum may be slightly higher than 20 for current-quality filtered corpora, possibly 25–35. Use 20 as a conservative lower bound.

## Canonical Source

Hoffmann, J., Borgeaud, S., Mensch, A., et al. (2022). "Training Compute-Optimal Large Language Models." arXiv:2203.15556. https://arxiv.org/abs/2203.15556
