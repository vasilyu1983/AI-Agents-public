## Table of Contents

- [Overview](#overview)
- [The L(N,D) Loss Form](#the-lnd-loss-form)
- [The 20:1 Ratio — Derivation Intuition](#the-201-ratio--derivation-intuition)
- [Derived Optimum Table (20:1 algebra)](#derived-optimum-table-201-algebra)
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
- `N` is the number of model parameters. Hoffmann et al. count **total** parameters (embeddings included); Kaplan et al. count non-embedding parameters. Keep one convention per fit
- `D` is the number of training tokens
- `E` is the irreducible loss (entropy of the data distribution; approximately 1.69 nats for the Chinchilla corpus)
- `A`, `B`, `α`, `β` are fitted constants

**Fitted constants as published (Hoffmann et al., Approach 3 equation in the body text):**
```
A ≈ 406.4
B ≈ 410.7
α ≈ 0.34
β ≈ 0.28
E ≈ 1.69
```

> **Correction (Besiroglu et al. 2024 — read before quoting these as fact).** A replication of Approach 3 found Hoffmann et al.'s published parametric fit is **inconsistent with their own first two estimation methods**, fails to fit the extracted data, and reports confidence intervals far too narrow to be plausible (intervals that narrow would require ~600,000 experiments; they ran fewer than ~500). Two causes: the optimizer stopped before convergence due to a poor loss-scale choice, and the body-text constants are rounded enough to bias predictions. The corrected re-fit yields **α ≈ 0.35 and β ≈ 0.37** (closer to equal, i.e. α ≈ β), which is consistent with Approaches 1–2. Direction matters: the *published* constants imply a far higher optimum than 20 tok/param (≈50 at 1e21 FLOPs and ≈93 at Chinchilla's own budget of 5.76e23, by direct minimization), while the refit restores ≈20 (≈22 and ≈18 at the same budgets). **Use the corrected exponents for any serious projection; treat the published constants above as the historical, biased fit.** Source: arXiv 2404.10102.

These constants are fit on a specific corpus (MassiveText) and a specific architecture family. They do not transfer exactly to other corpora or architectures without re-fitting — and, per the correction above, the *original published* fit itself should not be treated as ground truth.

## The 20:1 Ratio — Derivation Intuition

To find the compute-optimal (N*, D*) pair for a fixed budget C, minimize L(N, D) subject to the constraint C = 6 N D.

Substituting the constraint (D = C / 6N) into L(N, D) and taking the derivative with respect to N, then setting to zero gives:

```
α × A / N*^α  =  β × B / D*^β
```

Solving it gives N* = G·(C/6)^(β/(α+β)) with G = (αA/(βB))^(1/(α+β)), and D* = C/(6N*). The exponents depend only on α and β: the published constants give N* ∝ C^0.45 and D* ∝ C^0.55, while the refit (and Approaches 1–2) give roughly equal exponents:

```
N* ∝ C^0.50,   D* ∝ C^0.50
```

Both scale as C^{0.5}, meaning **model size and training tokens grow in equal proportion**: 4× the compute buys 2× N and 2× D (doubling compute raises each by √2). This is the Chinchilla finding, in contrast to Kaplan et al. who found N ∝ C^{0.73} (scale model much faster than data).

The 20:1 heuristic (D* ≈ 20 × N*) is the working ratio consistent with Approaches 1–2 and with the refit (≈22 at 1e21 FLOPs, ≈18 at 5.76e23). It does **not** come from the published constants above, which imply ≈50–93 tok/param over the same range (see the correction). Recompute any of these with `scripts/training_math.py optimum --compute <C>`, which prints the 20:1, published-fit and refit optima side by side.

**Important:** The exact coefficient varies. Some analyses suggest 15–25 depending on corpus quality and architecture. 20 is a practical working estimate, not a physical constant.

## Derived Optimum Table (20:1 algebra)

These rows are **derived**, not copied from the paper: N* = (C/120)^0.5 and D* = 20·N*, which is C = 6ND with D = 20N. Hoffmann et al.'s three approaches disagree with each other at large C (Approach 3 implies more tokens per parameter), so use the table for order of magnitude only.

| Compute C (FLOPs) | N* (params) | D* (tokens) |
|-------------------|-------------|-------------|
| 1e19              | 0.29B       | 5.8B        |
| 1e20              | 0.91B       | 18B         |
| 1e21              | 2.9B        | 58B         |
| 1e22              | 9.1B        | 183B        |
| 1e23              | 29B         | 577B        |
| 1e24              | 91B         | 1.8T        |

**Chinchilla itself:** 70B parameters, 1.4T tokens (≈5.9e23 FLOPs), approximately 20:1. It was compute-matched to **Gopher** (280B params, 300B tokens, ≈5.0e23 FLOPs), not to GPT-3; it used about 1.9× GPT-3's compute and outperformed Gopher at a quarter of the size.

**GPT-3 comparison:** At 175B params and 300B tokens (≈3.2e23 FLOPs), GPT-3 has a ratio of ~1.7:1, under-trained by Chinchilla standards. The 20:1 optimum at GPT-3's compute is ≈51B params trained on ≈1.0T tokens.

## Comparison: Kaplan vs Chinchilla

| Property | Kaplan et al. (2020) | Chinchilla (2022) |
|----------|---------------------|-------------------|
| Optimal N scaling | N* ∝ C^{0.73} | N* ∝ C^{0.50} |
| Optimal D scaling | D* ∝ C^{0.27} | D* ∝ C^{0.50} |
| Implied D/N | Falls as C grows (D ∝ N^0.37) | ~20, roughly constant |
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

3. Keep the parameter convention fixed: Chinchilla's fit counts total parameters; plugging non-embedding N into Chinchilla constants (or the reverse) biases the answer, most at small scale.

4. The optimum moves with data quality and architecture. Refit on your own corpus (IsoFLOP curves at 3+ budgets) rather than adopting another lab's ratio.

## Canonical Source

Hoffmann, J., Borgeaud, S., Mensch, A., et al. (2022). "Training Compute-Optimal Large Language Models." arXiv:2203.15556. https://arxiv.org/abs/2203.15556
