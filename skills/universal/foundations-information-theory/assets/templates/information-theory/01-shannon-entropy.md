# Primitive 1: Shannon Entropy

## Definition

H(X) = −Σ p(x) log p(x): bits with log₂, nats with ln (1 nat = 1/ln 2 ≈ 1.4427 bits). Convention 0 log 0 = 0.
Joint H(X,Y); conditional H(X|Y) = H(X,Y) − H(Y); chain rule H(X₁..Xₙ) = Σ H(Xᵢ | X₁..Xᵢ₋₁).
Bounds: 0 ≤ H(X) ≤ log |X|; equality at uniform (upper) and deterministic (lower).
Differential entropy h(X) = −∫ f log f can be negative and changes under invertible reparametrization.

## Traps

1. **Plug-in (MLE) entropy is biased downward.** For n iid samples on k fixed, full-support categories, the leading bias in log base b is −(k−1)/(2n ln b); Miller–Madow **adds** that magnitude. In nats ln b = 1; in bits divide by ln 2. It fails with sparse counts or unseen support; it is not a universal small-sample remedy. Report support assumptions and uncertainty; consider NSB where justified.
2. **Discrete vs differential.** Never compare H(discrete) with h(continuous); use MI, which is transform-invariant.
3. **Mixed bases.** Mixing bits and nats gives silent factor-of-ln 2 errors.
4. **Zero-count bins.** A true zero contributes 0; an empirical zero from sampling does not mean the probability is zero.
5. **Entropy is not value, and token entropy is not epistemic uncertainty.** High entropy means unpredictability, not relevance. For context selection, semantic entropy and RLVR policy entropy, see the SKILL.md anti-patterns and Context-Window Budget recipe.

## Known answers (base 2)

Fair binary source: 1 bit/symbol. Deterministic source: 0. Uniform over four symbols: 2 bits.
An empirical histogram from N observations has at most N distinct outcomes, so H ≤ log₂ N: 200 tokens give at most 7.644 bits and 150 tokens at most 7.229 (≈ 7.23) bits. A claimed 11.2 bits from 150 tokens exceeds the maximum and is impossible for that histogram. These bounds concern lexical histograms, not semantic relevance; summing marginal token entropy ignores sequence dependence and cannot certify a context-selection improvement.

## Sources

Cover & Thomas (2006) Ch. 2; Shannon (1948); Paninski (2003). Not in sources.json: Miller, G. A. (1955), Note on the bias of information estimates, *Information Theory in Psychology* 2, 95–100; Nemenman, I., Shafee, F. & Bialek, W. (2002), Entropy and inference, revisited, *NIPS 2002* (NSB). Full references: [`../../../data/sources.json`](../../../data/sources.json).
