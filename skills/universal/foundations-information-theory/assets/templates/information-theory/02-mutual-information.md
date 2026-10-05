# Primitive 2: Mutual Information

## Definition

I(X;Y) = H(X) − H(X|Y) = H(X) + H(Y) − H(X,Y) = D_KL(p(x,y) ‖ p(x)p(y)). I ≥ 0, and I = 0 iff independent.
Conditional MI: I(X;Y|Z) = H(X|Z) − H(X|Y,Z). Chain rule: I(X₁..Xₙ;Y) = Σ I(Xᵢ;Y | X₁..Xᵢ₋₁).
Continuous MI is invariant under invertible transforms of X or Y, unlike differential entropy.
Normalizations (NMI by geometric mean, by min entropy) rank differently: always state which one.

## Traps

1. **Plug-in MI is biased upward.** For an m×n full-support table under independence and iid multinomial sampling, the leading null bias in log base b is (m−1)(n−1)/(2N ln b). For 2×2 and N = 100: 0.005 nats ≈ 0.0072 bits. Away from independence, with sparse counts or unknown support, this is not a universal correction.
2. **Estimator is part of the result.** Plug-in, KSG k-NN, MINE/NWJ, InfoNCE (capped at log K negatives) and f-DIME have different bias profiles. Report a CI and a shuffled-label baseline that should read ≈ 0. Treat MI from more than about 20 dimensions with suspicion.
3. **MI is not causation.** Common causes create MI; conditional MI helps only if the conditioning set is right. Route effect claims to foundations-causal-inference.
4. **Binning continuous data** adds bias; prefer k-NN or kernel estimators and report the choice.
5. **Relevance minus redundancy is a heuristic.** I(q;d) − I(d;selected) is not the exact marginal gain. The exact target is the conditional MI I(q;d|selected), which needs a joint distribution over query, candidate and selected set.

## Known answer

Hypothetical retrieval scores (not measured): relevance I(q;dᵢ) = 3.2, 2.9, 3.5, 2.4, 1.8 bits for d₁..d₅; pairwise I(dᵢ;d₃) = 0.1, 0.2, —, 2.1, 0.4. Pick d₃ first; the heuristic gains are then 3.1, 2.7, —, 0.3, 1.4, so the top 3 are d₃, d₁, d₂ and near-duplicate d₄ drops. Validate any such heuristic on held-out task success before reporting its values as bits.

## Sources

Cover & Thomas (2006) Ch. 2; Jiao, Venkat, Han & Weissman (2015), *IEEE Trans. Inf. Theory* 61(5), arXiv:1406.6959 (JVHW); Kraskov, Stögbauer & Grassberger (2004) (KSG); Belghazi et al. (2018) (MINE); Paninski (2003). Full references: [`../../../data/sources.json`](../../../data/sources.json).
