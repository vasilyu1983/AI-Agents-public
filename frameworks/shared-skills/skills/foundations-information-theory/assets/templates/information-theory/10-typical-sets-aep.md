# Primitive 10: Typical Sets and the AEP

## Definition

**Asymptotic Equipartition Property (AEP)**: for i.i.d. random variables X₁, X₂, ..., Xₙ ~ p(x), the sample entropy converges in probability to H(X):

```
−(1/n) log p(X₁, X₂, ..., Xₙ) → H(X)   (in probability, as n → ∞)
```

**Typical set** A_ε^(n): the set of sequences (x₁,...,xₙ) whose sample entropy is within ε of H(X):

```
A_ε^(n) = { (x₁,...,xₙ) : | −(1/n) log p(x₁,...,xₙ) − H(X) | ≤ ε }
```

**Key properties of the typical set**:
1. **Probability**: P(A_ε^(n)) → 1 as n → ∞ (almost all sequences are typical)
2. **Size**: |A_ε^(n)| ≤ 2^{n(H(X)+ε)}  (upper bound)
3. **Size**: |A_ε^(n)| ≥ (1−δ) · 2^{n(H(X)−ε)} for large enough n  (lower bound)
4. **Equipartition**: all typical sequences have approximately equal probability ≈ 2^{−nH(X)}

**Source coding theorem** (Shannon 1948): it is possible to compress n i.i.d. symbols to nH(X) bits with arbitrarily low error probability (for large n), and impossible to compress to fewer than nH(X) bits without increasing error.

**Block code interpretation**: to represent a source losslessly, assign codes to typical sequences only. The codebook requires approximately 2^{nH(X)} entries → n·H(X) bits per block of n symbols.

**Non-i.i.d. sources**: the AEP generalizes via the entropy rate:

```
H_rate = lim_{n→∞} H(X₁,...,Xₙ)/n   (if the limit exists)
```

For stationary ergodic sources, |A_ε^(n)| ≈ 2^{n·H_rate} and the source coding theorem applies with H replaced by H_rate.

---

## When to Use

- Determining the minimum block length n for a source code to be near-optimal (approach entropy rate within ε).
- Sizing dataset complexity: the number of distinct sequences a source can produce scales as 2^{n·H_rate}.
- Explaining why language model training requires large corpora: linguistic text has high entropy rate; covering the typical set requires exponentially many examples.
- Justifying compression standards: the existence of near-entropy-rate codes (Huffman, arithmetic) follows from the AEP.
- Finite block length tradeoffs: for short blocks, the achievable rate is above H(X) + ε; the gap scales as O(√(log n / n)) (channel coding finite block length theory, Polyanskiy et al. 2010).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| H(X) or H_rate | Non-negative real (bits) | Entropy or entropy rate of the source |
| Block length n | Positive integer | Number of symbols per block |
| Tolerance ε | Small positive real | Acceptable deviation from entropy rate |

---

## Outputs

| Output | Type | Interpretation |
|--------|------|----------------|
| \|A_ε^(n)\| | ≈ 2^{nH(X)} | Number of typical sequences (effective codebook size) |
| Code length | n·H(X) bits per block | Minimum bits per block for near-lossless coding |
| Required n | Integer | Minimum block length for a given ε, δ guarantee |

---

## Failure Modes

1. **AEP requires i.i.d. (or ergodic stationary)**: Natural text, speech, and code are not i.i.d. The AEP for such sources requires estimating H_rate (the entropy rate), not H(X₁). Plug-in entropy of marginals overestimates H_rate for correlated sources.
2. **Convergence speed**: The AEP convergence rate is O(1/√n) for the LLN guarantee. For small n, the typical set may not contain most probability mass. Do not apply AEP-based bounds for n < 100 without checking sample sizes.
3. **Non-ergodic sources**: For non-ergodic processes (e.g., sources with regime switches), H_rate may not be well-defined or may be path-dependent. AEP breaks down.
4. **Conflating typical probability with typical events**: The typical set contains sequences of approximately equal probability, not the most probable sequences. The single most probable sequence (mode) may not be in the typical set for highly skewed distributions.
5. **Using typical-set size as exact codebook size**: 2^{nH(X)} is an approximation. The actual typical set size oscillates; for finite n, add ε-slack and use floor/ceiling carefully in implementation.

---

## Worked Example

**Training dataset size estimation**

A text source has an estimated entropy rate H_rate = 1.3 bits/character (English text approximation). We want to estimate the number of distinct 100-character sequences we should expect in a training corpus.

```
|A_ε^(100)| ≈ 2^{100 × 1.3} = 2^{130} ≈ 1.36 × 10^{39}
```

The typical set contains ≈ 10^{39} sequences — far beyond any corpus size. This explains why language models cannot memorize typical sequences; they must generalize. Sampling 10^{12} tokens covers only 10^{12}/10^{39} = 10^{−27} of the typical set.

**Source code block length**

We want a Huffman code for a source with H(X) = 4.7 bits/symbol that achieves within ε=0.1 bits/symbol of entropy with probability ≥ 0.95. By AEP, we need n large enough that the LLN concentration holds. Using Chebyshev:

```
n ≥ Var[−log p(X)] / (ε² · (1−δ))
```

For typical text sources, Var[−log p(X)] ≈ 2–4 bits². With ε=0.1, δ=0.05:

```
n ≥ 3 / (0.01 × 0.95) ≈ 316 symbols per block
```

A block length of 320 characters is sufficient to achieve within 0.1 bits/symbol of entropy rate with 95% probability.

---

## Sources

- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423. (Source coding theorem.)
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 3. Wiley. (AEP and typical sets.)
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 5. Cambridge.
- McMillan, B. (1953). The basic theorems of information theory. *Annals of Mathematical Statistics*, 24(2), 196–219. (AEP for stationary ergodic processes.)
- Polyanskiy, Y., Poor, H. V. & Verdú, S. (2010). Channel coding rate in the finite blocklength regime. *IEEE Transactions on Information Theory*, 56(5), 2307–2359.
