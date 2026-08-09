# Primitive 1: Shannon Entropy

## Definition

**Discrete entropy** of a random variable X with probability mass function p(x):

```
H(X) = − Σ_{x ∈ X} p(x) log₂ p(x)        [bits, base-2 log]
H(X) = − Σ_{x ∈ X} p(x) ln p(x)           [nats, natural log]
```

Convention: 0 log 0 = 0 (entropy contribution of impossible events is zero).

**Joint entropy**:  H(X,Y) = − Σ_{x,y} p(x,y) log p(x,y)

**Conditional entropy**:  H(X|Y) = H(X,Y) − H(Y)  =  Σ_y p(y) H(X|Y=y)

**Differential entropy** (continuous X with density f):

```
h(X) = − ∫ f(x) log f(x) dx
```

Differential entropy can be negative and is not invariant under invertible reparametrizations.

**Chain rule**:  H(X₁, ..., Xₙ) = Σ_i H(Xᵢ | X₁, ..., Xᵢ₋₁)

**Bounds**:
- 0 ≤ H(X) ≤ log |X|  (discrete)
- H(X) = log |X| iff X is uniform
- H(X) = 0 iff X is deterministic

---

## When to Use

- Measuring the information content of a source (how many bits per symbol on average).
- Quantifying uncertainty before and after an observation (H(X) vs. H(X|Y)).
- Budgeting bits for compression or transmission.
- Comparing segment informativeness when filling a context window.
- Estimating the theoretical minimum description length for a lossless code.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Distribution p(x) | PMF or empirical frequency table | Probability or count over alphabet X |
| Alphabet X | Finite set | All possible values x can take |
| Log base | 2 (bits) or e (nats) | Choice is consistent within a calculation |

---

## Outputs

| Output | Type | Interpretation |
|--------|------|----------------|
| H(X) | Non-negative real | Average bits (or nats) per symbol |
| H(X|Y) | Non-negative real | Residual uncertainty in X after observing Y |
| H(X,Y) | Non-negative real | Total joint uncertainty |

---

## Failure Modes

1. **Estimating entropy from small samples**: Plug-in (MLE) entropy estimators are negatively biased. For n samples over k bins, bias ≈ (k−1)/(2n). Use Miller-Madow correction or a Bayesian estimator (NSB) when n is small relative to |X|.
2. **Applying discrete entropy to continuous variables**: Differential entropy h(X) does not share the non-negativity and absolute-probability properties of H(X). Never compare H(discrete) directly to h(continuous).
3. **Assuming base-2 for all downstream formulas**: Some ML papers use nats; Shannon's original paper uses bits. Mixing bases produces silent factor-of-ln(2) errors.
4. **Zero-count bins**: If p(x)=0 for some x, that bin contributes 0 to entropy (convention). However, if an empirical count is zero due to sampling, the true contribution is unknown — do not assume it is zero.

---

## Worked Example

**Context-window segment ranking**

Four candidate paragraphs for a RAG context window. Token counts and empirical token frequency histograms yield the following entropy estimates:

| Segment | Tokens | H(segment) [bits/token] | H(segment) × tokens [total bits] |
|---------|--------|------------------------|----------------------------------|
| A       | 200    | 9.1                    | 1,820 |
| B       | 200    | 4.3                    | 860   |
| C       | 150    | 11.2                   | 1,680 |
| D       | 150    | 3.8                    | 570   |

Budget: 400 tokens. Greedy by token count picks A+B (400 tokens, 2,680 bits). Entropy-first picks A+C (350 tokens, 3,500 bits) — 31% more information for fewer tokens. Add redundancy check (see primitive #11) to confirm C is not a near-duplicate of A.

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 2. Wiley. Canonical reference.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 2. Cambridge. Free at inference.org.uk/mackay/itila/.
- Miller, G. A. (1955). Note on the bias of information estimates. *Information Theory in Psychology*, 2, 95–100. (Miller-Madow correction.)
- Nemenman, I., Shafee, F. & Bialek, W. (2002). Entropy and inference, revisited. *NIPS 2002*. (NSB estimator.)
