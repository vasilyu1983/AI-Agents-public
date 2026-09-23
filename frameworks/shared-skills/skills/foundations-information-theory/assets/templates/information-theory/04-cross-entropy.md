# Primitive 4: Cross-Entropy

## Definition

**Cross-entropy** of distribution Q relative to distribution P:

```
H(P, Q) = − Σ_{x} p(x) log q(x)      [discrete]
H(P, Q) = − ∫ f_P(x) log f_Q(x) dx   [continuous]
```

**Decomposition** (always holds):

```
H(P, Q) = H(P) + D_KL(P ‖ Q)
```

Cross-entropy equals the true entropy H(P) plus the KL divergence of Q from P. Minimizing H(P,Q) over Q is identical to minimizing D_KL(P‖Q) when P is fixed.

**Perplexity**:

```
PP(Q) = 2^{H(P,Q)}       [base-2]
PP(Q) = e^{H(P,Q)}       [base-e]
```

Perplexity measures how surprised a model Q is at the true distribution P on average. Lower is better.

**Cross-entropy loss** (classification, n classes):

```
L = − Σ_{i=1}^{n} y_i log ŷ_i       [y = one-hot true label, ŷ = softmax output]
```

Equivalent to NLL (negative log-likelihood) under the model's predicted distribution.

**Bits-per-byte (BPB) normalization**:

```
BPB = sum_token(-log2 q(token | prefix)) / number_of_bytes
    = mean_bits_per_token * number_of_tokens / number_of_bytes
```

BPB is vocabulary-agnostic, enabling cross-tokenizer and cross-model comparisons.

---

## When to Use

- **Training objective**: cross-entropy loss is the standard objective for classification, language modeling, and sequence labeling.
- **Model evaluation**: perplexity measures how well a language model predicts held-out text.
- **Cross-tokenizer comparison**: use BPB when comparing models with different vocabularies (e.g., GPT-2 vs. Llama tokenizer).
- **Decomposing model behavior**: decompose H(P,Q) = H(P) + KL to separate irreducible data uncertainty from model approximation error.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| True distribution P | PMF or one-hot labels | Source of ground truth probabilities |
| Model distribution Q | PMF / softmax output | Predicted probabilities over the alphabet |
| Log base | 2 (bits) or e (nats) | Must be consistent within a calculation |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| H(P,Q) | Non-negative real | [H(P), ∞) | Average code length using Q for a P-distributed source |
| PP(Q) | Real ≥ 1 | [1, ∞) | Effective branching factor; lower = better fit |
| BPB | Non-negative real | (0, 8] typical | Bits used per byte; vocabulary-neutral perplexity |

---

## Failure Modes

1. **CE-as-similarity confusion**: Low CE loss does not mean Q is "similar" to P. H(P,Q) = H(P) + D_KL(P‖Q); a low loss can result from small KL even with large H(P). For distribution similarity, use KL or JSD directly.
2. **Cross-tokenizer perplexity comparison**: Perplexity is defined over a vocabulary. A model with a 50k-token vocabulary sees shorter sequences for the same text than a model with a 32k vocabulary, producing a lower perplexity for reasons unrelated to quality. Always normalize to BPB for cross-model comparisons.
3. **Perplexity as absolute quality**: Perplexity is task-specific. A model with low perplexity on a held-out sample can still be poorly calibrated or generate factually incorrect text. Supplement with task-specific metrics.
4. **One-hot labels as ground truth**: When labels are noisy or ambiguous, one-hot encoding treats the label as P=1 for one class. Label smoothing (ε-smoothed) applies P = (1−ε)·one-hot + ε/n to acknowledge uncertainty.
5. **Summing CE over sequences of different lengths**: Summing CE over batches of different lengths without per-token averaging produces a length-biased loss. Always use mean CE per token (or per byte for cross-architecture comparison).

---

## Worked Example

**Model comparison with vocabulary mismatch**

Two language models evaluated on the same test set (10M bytes of text):

| Model | Vocab size | Sequence tokens | Perplexity | BPB |
|-------|-----------|-----------------|------------|-----|
| ModelA | 50,257 | 2.4M | 12.3 | 0.869 |
| ModelB | 32,000 | 3.1M | 18.7 | 1.310 |

Assuming each perplexity is exp(mean token NLL), BPB_A = 2.4M * log2(12.3) / 10M = 0.869 and BPB_B = 3.1M * log2(18.7) / 10M = 1.310. A is better on this same byte corpus. The example does not reverse ranking; normalization makes the comparison meaningful. Report common corpus, encoding, special-token treatment and context protocol.

**Decomposing training loss**

For conditional classification loss, the decomposition uses H(Y|X) and the expected conditional KL, not marginal entropy H(Y). A balanced deterministic-label classifier can have H(Y)=1 bit and H(Y|X)=0. Label frequencies alone therefore cannot diagnose irreducible prediction uncertainty. If a valid conditional model gives loss .41 bits, H(Y|X)=.38 and conditional KL=.03, that decomposition is illustrative; verify the conditional entropy estimate before attributing a training ceiling.

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 2. Wiley.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 2. Cambridge.
- Müller, R. et al. (2019). When does label smoothing help? *NeurIPS 2019*. https://arxiv.org/abs/1906.02629 (Label smoothing.)
- Press, O. et al. (2022). Measuring the carbon intensity of AI in cloud instances. (BPB normalization practice.) https://arxiv.org/abs/2203.00540
