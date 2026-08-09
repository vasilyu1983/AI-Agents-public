# Primitive 9: Fano's Inequality

## Definition

**Fano's inequality** — a lower bound on the probability of error P_e for estimating X from an observation Y:

```
H(X|Y) ≤ H_b(P_e) + P_e · log(|X| − 1)
```

where:
- H(X|Y) = conditional entropy of X given Y (residual uncertainty)
- H_b(P_e) = binary entropy of the error probability = −P_e log P_e − (1−P_e) log(1−P_e)
- |X| = alphabet size of X
- P_e = Pr[X̂ ≠ X] for any estimator X̂ = f(Y)

**Simplified lower bound** (looser but easy to compute):

```
P_e ≥ (H(X|Y) − 1) / log|X|
```

This form is widely used in practice. It says: if the residual entropy H(X|Y) is large relative to log|X|, then no estimator can achieve low error.

**Converse to the channel coding theorem**: Fano's inequality is the key step in proving that rates above capacity have error bounded away from zero.

**Interpretation**: H(X|Y) ≤ 1 + P_e log|X|.
- If H(X|Y) → 0 (Y fully determines X), then P_e → 0: perfect prediction is possible.
- If H(X|Y) = log|X| (Y tells us nothing about X), then P_e ≥ (log|X|−1)/log|X| → 1 − 1/|X|: barely above random guessing.

---

## When to Use

- **Classifier evaluation**: given the conditional entropy H(Y|features), lower-bound the achievable classification error before building or evaluating a model.
- **Retrieval accuracy ceiling**: given MI(query, document), bound the minimum precision@k that any retrieval algorithm can achieve.
- **Feature sufficiency check**: if Fano's bound implies P_e ≥ 0.4 with a proposed feature set, adding model capacity will not help — the features do not carry enough information.
- **Proving impossibility**: demonstrating that a task cannot be solved below some error rate given available information.
- **Information-theoretic sanity check**: before training, estimate H(Y|X) on training data to detect fundamental ambiguity.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| H(X\|Y) | Non-negative real (bits) | Residual uncertainty in X after observing Y |
| \|X\| | Positive integer | Number of possible classes/values |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| P_e lower bound | Real | [0, 1] | Minimum achievable error probability for any estimator |

---

## Failure Modes

1. **Confusing Fano bound tightness**: The bound is tight when X̂ is the MAP estimator and the error is spread uniformly across wrong classes. In practice, errors concentrate on confusable pairs and the true P_e can be close to the bound or much lower.
2. **Applying Fano when |X| = 2 (binary case)**: For binary classification, H_b(P_e) = H(P_e) and the bound simplifies to H(X|Y) ≤ H_b(P_e) + P_e. This is exact when the two classes are equally likely. Verify class balance before interpreting the bound.
3. **Using H(X|Y) estimated from small samples**: Fano's bound is only as accurate as the entropy estimate. For small n, plug-in H(X|Y) is negatively biased → the P_e bound is overly optimistic. Apply bias correction.
4. **Treating the bound as achievable with finite data**: Fano's bound is achievable in the limit of infinite data and optimal codes. At finite sample sizes, the bound gives a floor that may not be reachable.
5. **Ignoring that P_e is an average**: Fano gives an average (expected) error bound. Worst-case per-instance error can be much higher. For safety-critical systems, use per-instance Fano variants or concentration inequalities.

---

## Worked Example

**Feature sufficiency check for intent classification**

An intent classifier maps user utterances to one of |X| = 50 intent classes. Estimated H(X) = 5.3 bits (near-uniform). Estimated H(X|features) = 2.1 bits (after conditioning on TF-IDF feature vector of 1,000 terms).

Fano lower bound:

```
P_e ≥ (H(X|features) − 1) / log₂|X|
    = (2.1 − 1) / log₂(50)
    = 1.1 / 5.64
    = 0.195
```

Even with perfect learning, the error rate is at least 19.5% given these features. The features do not carry enough information about the intent. Adding model capacity (deeper network, transformers) will not overcome this floor. Corrective actions: add more discriminative features, improve utterance preprocessing, or reduce intent granularity.

After adding contextual embeddings: H(X|embeddings) = 0.6 bits.

```
P_e ≥ (0.6 − 1) / 5.64 = −0.07  → bound is 0 (non-negative)
```

The bound is now vacuous (P_e ≥ 0) — the embeddings contain more than enough information; error is limited by model and data quality, not information.

---

## Sources

- Fano, R. M. (1961). *Transmission of Information*. MIT Press. (Original derivation.)
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Theorem 2.10.1. Wiley.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423. (Channel converse.)
- Correction (2026-07-11): MacKay's *Information Theory, Inference, and Learning Algorithms* was previously cited here (as "Ch. 8") as a source for Fano's inequality. Verified against the book's treatment of coding theorems: MacKay does not derive or name Fano's inequality anywhere in the text — Ch.8 ("Dependent Random Variables" as of the 3rd printing; "Correlated Random Variables" in earlier printings) covers joint/conditional entropy but not this bound. Cover & Thomas Theorem 2.10.1 and Fano (1961) remain the correct primary sources; do not re-add MacKay as a Fano citation without a page-verified quote.
