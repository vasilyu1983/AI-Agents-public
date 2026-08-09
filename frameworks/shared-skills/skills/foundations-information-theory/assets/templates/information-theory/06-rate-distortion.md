# Primitive 6: Rate-Distortion

## Definition

**Rate-distortion function** R(D): the minimum bitrate required to represent source X with expected distortion ≤ D under distortion measure d(x, x̂):

```
R(D) = min_{p(x̂|x): E[d(X,X̂)] ≤ D} I(X; X̂)
```

The minimization is over all conditional distributions p(x̂|x) (reconstruction distributions) that satisfy the distortion constraint.

**Key properties**:
- R(0) = H(X) (lossless coding; zero distortion requires entropy-rate bits)
- R(D) is monotone non-increasing and convex in D
- R(D) = 0 for D ≥ D_max (some distortion level makes the source redundant to transmit)

**Gaussian source, squared-error distortion** (MSE = D):

```
R(D) = ½ log₂(σ² / D)       [bits per sample, D ≤ σ²]
R(D) = 0                     [D > σ²]
```

For a Gaussian source with variance σ², the minimum bitrate to achieve MSE = D is ½ log₂(σ²/D).

**Distortion-rate function** D(R): the inverse of R(D) — minimum achievable distortion at bitrate R.

**Parametric (Blahut-Arimoto) form**:

```
R(D) solved iteratively via Blahut-Arimoto algorithm:
  p(x̂|x) ∝ q(x̂) · exp(−β · d(x, x̂))
  q(x̂) = Σ_x p(x) · p(x̂|x)
```

where β is the Lagrange multiplier trading rate against distortion (analogous to temperature in IB, primitive #8).

---

## When to Use

- Finding the theoretical minimum bitrate for a lossy compression task at an acceptable quality level.
- Deciding whether to invest in lossless vs. lossy coding: if D_acceptable > 0, lossy can save significant bits.
- Sizing summarization compression: the "distortion" is semantic loss; R(D) bounds the minimum prompt/summary length.
- Quantization design: mapping a continuous source to discrete levels under MSE or perceptual distortion.
- Benchmarking learned compression codecs against the theoretical limit.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Source distribution p(x) | PMF or density | Statistical model of the source to compress |
| Distortion measure d(x, x̂) | Function → ℝ≥0 | Hamming, squared-error, perceptual, BLEU, etc. |
| Target distortion D | Real ≥ 0 | Maximum acceptable expected distortion |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| R(D) | Non-negative real | [0, H(X)] | Minimum bits/symbol at distortion D |
| D(R) | Non-negative real | [0, D_max] | Minimum distortion at bitrate R |
| R-D curve | Monotone convex curve | — | Tradeoff frontier between bitrate and quality |

---

## Failure Modes

1. **Assuming lossless is required when lossy is acceptable**: Any D>0 reduces R(D) below H(X). For a Gaussian source with σ²=1, accepting D=0.1 (10% MSE) drops the required rate from ∞ (impossible lossless) to ½log₂(10) ≈ 1.66 bits — a dramatic saving.
2. **Wrong distortion measure**: R(D) is defined for a specific d(x,x̂). Computing R(D) under MSE then applying a perceptual distortion budget is invalid. Choose d(x,x̂) aligned with the actual downstream quality criterion.
3. **Confusing R(D) with achievable codec rate**: R(D) is a lower bound achievable only with infinite block length. Real codecs operate above R(D); the gap is implementation overhead, not a violation of theory.
4. **Ignoring source statistics**: Applying the Gaussian R(D) formula to a non-Gaussian source (e.g., heavy-tailed text token distributions) produces incorrect rate predictions. Compute R(D) numerically via Blahut-Arimoto for non-Gaussian sources.
5. **Not checking R(D)=0 regime**: Below some maximum distortion D_max, no information needs to be transmitted. If the task tolerance is above D_max, compression is trivially free — always check before designing a codec.

---

## Worked Example

**Summarization bitrate bound**

A source document has estimated entropy H(X) = 12 bits/token (rich technical text). A downstream QA system tolerates up to D = 0.2 semantic distortion (measured by 1 − ROUGE-L). Model the source as approximately Gaussian in embedding space with σ² = 1 (normalized).

```
R(D=0.2) = ½ log₂(1/0.2) = ½ log₂(5) ≈ 1.16 bits/token
```

Original document: 2,000 tokens × 12 bits = 24,000 bits of content.
At D=0.2: minimum representation needs only 2,000 × 1.16 = 2,320 bits → approximately 193 tokens.

A 10× compression is theoretically achievable at 20% semantic distortion. A summary longer than ~200 tokens at this distortion level is transmitting redundant information. Use this bound to set summarization length targets rather than arbitrary word-count rules.

---

## Sources

- Shannon, C. E. (1959). Coding theorems for a discrete source with a fidelity criterion. *IRE National Convention Record*, part 4, 142–163.
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 10. Wiley.
- Blahut, R. E. (1972). Computation of channel capacity and rate-distortion functions. *IEEE Transactions on Information Theory*, 18(4), 460–473.
- Arimoto, S. (1972). An algorithm for computing the capacity of arbitrary discrete memoryless channels. *IEEE Transactions on Information Theory*, 18(1), 14–20.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 34. Cambridge.
