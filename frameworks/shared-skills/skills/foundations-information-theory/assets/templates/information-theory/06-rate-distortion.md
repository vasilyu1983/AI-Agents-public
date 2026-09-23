# Primitive 6: Rate-Distortion

## Definition

**Rate-distortion function** R(D): the minimum bitrate required to represent source X with expected distortion ≤ D under distortion measure d(x, x̂):

```
R(D) = min_{p(x̂|x): E[d(X,X̂)] ≤ D} I(X; X̂)
```

The minimization is over all conditional distributions p(x̂|x) (reconstruction distributions) that satisfy the distortion constraint.

**Key properties**:
- For a finite discrete memoryless source with zero distortion iff exact reconstruction, R(0)=H(X); continuous sources under MSE can require infinite rate at D=0
- R(D) is monotone non-increasing and convex in D
- R(D) = 0 for D ≥ D_max (some distortion level makes the source redundant to transmit)

**Gaussian source, squared-error distortion** (MSE = D):

```
R(D) = ½ log₂(σ² / D)       [bits per sample, D ≤ σ²]
R(D) = 0                     [D > σ²]
```

For a Gaussian source with variance σ², the minimum bitrate to achieve MSE = D is ½ log₂(σ²/D).

**Distortion-rate function** D(R): the inverse of R(D) — minimum achievable distortion at bitrate R.

**Finite source/reconstruction alphabet Blahut-Arimoto form**:

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
- Modeling summarization as lossy coding only after defining source/reconstruction distributions, task distortion, and a code-to-token mapping. Without that mapping, measure quality at actual token budgets; R(D) does not certify prompt/summary length.
- Quantization design: mapping a continuous source to discrete levels under MSE or perceptual distortion.
- Benchmarking learned compression codecs against the theoretical limit.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Source distribution p(x) | PMF or density | Statistical model, memory assumptions and source-symbol units |
| Reconstruction alphabet and coding convention | Set/model | Allowed reconstructions, block length, bits per source symbol; any mapping to lexical tokens |
| Distortion measure d(x, x̂) | Function → ℝ≥0 | Hamming, squared-error, perceptual, BLEU, etc. |
| Target distortion D | Real ≥ 0 | Maximum acceptable expected distortion |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| R(D) | Non-negative extended real | [0, H(X)] only for finite discrete sources allowing exact reconstruction; otherwise may be infinite | Minimum bits/source symbol under the stated coding model; differential entropy is not this upper bound |
| D(R) | Non-negative real | [0, D_max] | Minimum distortion at bitrate R |
| R-D curve | Monotone convex curve | — | Tradeoff frontier between bitrate and quality |

---

## Failure Modes

1. **Assuming lossless is required when lossy is acceptable**: A positive distortion budget may reduce required rate; strict reduction depends on source and distortion measure. For a Gaussian source with σ²=1, accepting D=0.1 (10% MSE) drops the required rate from ∞ (impossible lossless) to ½log₂(10) ≈ 1.66 bits — a dramatic saving.
2. **Wrong distortion measure**: R(D) is defined for a specific d(x,x̂). Computing R(D) under MSE then applying a perceptual distortion budget is invalid. Choose d(x,x̂) aligned with the actual downstream quality criterion.
3. **Confusing R(D) with achievable codec rate**: Under standard memoryless source-coding assumptions, rates arbitrarily close to R(D) are asymptotically approachable as block length grows. Finite-block feasibility depends on the coding criterion; special/trivial cases can achieve the bound exactly. Measure overhead and finite-block loss rather than promising attainability for a particular codec.
4. **Ignoring source statistics**: Applying the Gaussian R(D) formula to a non-Gaussian source (e.g., heavy-tailed text token distributions) produces incorrect rate predictions. Finite-alphabet Blahut-Arimoto requires a supplied finite source/reconstruction support and distortion matrix. Continuous-source discretization is an approximation whose support/truncation/resolution error must be reported; non-Gaussian does not itself make the finite algorithm exact.
5. **Not checking R(D)=0 regime**: At or above D_max, no information needs to be transmitted. If the task tolerance is above D_max, compression is trivially free — always check before designing a codec.

---

## Worked Example

**Gaussian MSE known answer**

For an iid scalar Gaussian source with variance 1 and squared-error distortion D=.2, R(D)=.5*log2(5)=1.161 bits/sample. This asymptotic bound concerns reconstruction of that scalar source under MSE. ROUGE-L semantic loss is not MSE, an embedding coordinate is not a text token, and binary code bits cannot be divided by a lexical entropy to certify a 193-token summary. For summarization, define the source/reconstruction random variables and task loss, then measure achievable quality at actual token budgets; any Gaussian analogy is a heuristic, not a summary-length theorem.

## Sources

- Shannon, C. E. (1959). Coding theorems for a discrete source with a fidelity criterion. *IRE National Convention Record*, part 4, 142–163.
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 10. Wiley.
- Blahut, R. E. (1972). Computation of channel capacity and rate-distortion functions. *IEEE Transactions on Information Theory*, 18(4), 460–473.
- Arimoto, S. (1972). An algorithm for computing the capacity of arbitrary discrete memoryless channels. *IEEE Transactions on Information Theory*, 18(1), 14–20.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 34. Cambridge.
