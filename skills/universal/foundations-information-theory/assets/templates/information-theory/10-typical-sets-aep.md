# Primitive 10: Typical Sets and the AEP

## Definition

For iid X₁..Xₙ ~ p: −(1/n) log p(X₁..Xₙ) → H(X) in probability.
Typical set A_ε^(n): sequences whose sample entropy is within ε of H. P(A_ε^(n)) → 1; |A_ε^(n)| ≤ 2^{n(H+ε)} and ≥ (1−δ) 2^{n(H−ε)} for large n.
Source coding theorem: about nH bits suffice for n symbols with vanishing error, and fewer do not. For stationary ergodic sources, replace H by the entropy rate (Shannon–McMillan–Breiman).

## Traps

1. **Text is not iid.** Use the entropy rate, not marginal H(X₁); marginal entropy overstates the rate of a correlated source.
2. **Asymptotic.** AEP supplies no universal finite-length gap; derive a bound for the stated source, error tolerance and code class. Channel-coding finite-blocklength results do not transfer unchanged.
3. **Typical is not most probable.** The single most probable sequence may lie outside the typical set.
4. **Typical-set size is not a sample-complexity theorem** for language models, and not a Huffman code-length guarantee.
5. **Non-ergodic sources** (regime switches) may have no well-defined rate.

## Known answer

Chebyshev concentration for the sample mean of iid variables with finite variance σ² = 3: P(|mean − μ| ≥ ε) ≤ σ²/(n ε²). For ε = 0.1 and δ = 0.05, n ≥ 3/(0.01 × 0.05) = 6000. This needs independence and the stated variance; the variance is an assumption for the example, not a universal constant for text, and dependent text needs a different argument.

## Sources

Shannon (1948); Cover & Thomas (2006) Ch. 3 (AEP) and Ch. 4 (entropy rates); McMillan (1953). Full references: [`../../../data/sources.json`](../../../data/sources.json).
