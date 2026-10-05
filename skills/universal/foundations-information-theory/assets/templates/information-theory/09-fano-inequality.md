# Primitive 9: Fano's Inequality

## Definition

For any estimator X̂ = f(Y) of X over a finite alphabet, with P_e = Pr[X̂ ≠ X]:
H(X|Y) ≤ H_b(P_e) + P_e log(|X| − 1).
Simplified lower bound (bits): P_e ≥ (H(X|Y) − 1) / log₂ |X|.
It is the key step in the converse of the channel coding theorem.

## Traps

1. **A nonpositive simplified bound is inconclusive.** It does not establish feature sufficiency, and it does not rule out irreducible error; it only fails to give a floor.
2. **Tightness needs more than MAP.** Equality additionally requires the error indicator to be independent of the observation and, conditional on an error and the observation, the true class to be uniform over the remaining |X| − 1 classes. MAP decoding with averaged uniform wrong-class frequencies is not enough; real errors concentrate on confusable pairs.
3. **Not an achievability result.** Infinite training data does not make a particular bound achievable; achievability needs a separate theorem and assumptions.
4. **Estimated H(X|Y).** Plug-in conditional entropy is biased downward on small samples, which makes the floor too optimistic.
5. **Binary case.** With |X| = 2, log(|X| − 1) = 0, so H(X|Y) ≤ H_b(P_e); still an inequality.
6. **Average, not worst case.** Per-instance error can be far higher.
7. **Uninformative Y.** If H(X|Y) = log₂|X|, the simplified bound gives 1 − 1/log₂|X|, which is not the exact random-guess error 1 − 1/|X|.

## Known answers

|X| = 50, H(X|features) = 2.1 bits: P_e ≥ (2.1 − 1)/log₂ 50 = 1.1/5.644 = 0.195. No model trained on these features can beat 19.5% error under this distribution.
After adding embeddings, H(X|embeddings) = 0.6 bits: (0.6 − 1)/5.644 = −0.071, so the bound is vacuous (P_e ≥ 0). That is inconclusive, not proof that the features now suffice.

## Sources

Fano (1961); Cover & Thomas (2006) Theorem 2.10.1. MacKay (2003) does not derive Fano's inequality; do not cite it for this bound. Full references: [`../../../data/sources.json`](../../../data/sources.json).
