# Primitive 5: Channel Capacity

## Definition

**Channel capacity** C of a discrete memoryless channel (DMC) with input X and output Y:

```
C = max_{p(x)} I(X;Y)       [bits per channel use]
```

Capacity is the maximum mutual information over all possible input distributions p(x).

**Binary Symmetric Channel (BSC)** with crossover probability p:

```
C_BSC = 1 − H_b(p) = 1 − [−p log p − (1−p) log(1−p)]
```

At p=0 or p=1: C=1 (perfect channel or perfectly predictable errors). At p=0.5: C=0 (pure noise, no information transmitted).

**Additive White Gaussian Noise (AWGN) channel** — Shannon-Hartley theorem:

```
C = B · log₂(1 + S/N)       [bits per second]
```

where B = bandwidth (Hz), S/N = signal-to-noise ratio (linear scale, not dB).

**Shannon's Channel Coding Theorem** (1948):
- For any rate R < C, there exist codes with arbitrarily small error probability.
- For any rate R > C, error probability is bounded away from zero regardless of code.

The theorem is an existence result — it does not specify how to construct capacity-achieving codes. Turbo codes, LDPC, and polar codes approach capacity in practice.

**Multi-access and broadcast channels** generalize C to multiple transmitters / receivers; capacity becomes a region, not a scalar.

---

## When to Use

- Establishing the theoretical maximum throughput for a communication link before designing the encoding scheme.
- Analyzing a retrieval pipeline only when named discrete intent/output alphabets and measured transition probabilities justify a channel model. Report observed mutual information separately from capacity; precision@k does not supply either.
- Analyzing a supplied communication model; summary token budgets require an explicit source/reconstruction/distortion model and task validation (see primitive #6), not a capacity inferred from token count alone.
- Understanding why increasing bandwidth has diminishing returns at high S/N (log relationship).

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Channel transition matrix p(y\|x) | Matrix | For DMC; specifies output probability for each input |
| Crossover probability p | Real [0, 0.5] | For BSC |
| Bandwidth B, SNR S/N | Real > 0 | For AWGN channels |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| C | Non-negative real | [0, log\|X\|] | Maximum mutual information; bits per channel use |
| C_AWGN | Non-negative real | [0, ∞) | Bits per second at given bandwidth and SNR |

---

## Failure Modes

1. **Ignoring channel memory**: The supplied DMC formulas assume memorylessness. Channels with memory (wireless multipath, bursty links) require a stated state/dependence model and the appropriate capacity analysis; memory does not universally decrease capacity relative to a marginal DMC approximation.
2. **Treating capacity as a guaranteed rate**: For noisy channels, capacity is an asymptotic vanishing-error limit; finite-blocklength achievable rates depend on blocklength, target error, channel model and coding constraints (Polyanskiy-Poor-Verdú 2010), and are not guaranteed by C alone. Strictly lower rate is not universal: a noiseless binary channel reaches C=1 bit/use at blocklength one with zero error.
3. **Applying AWGN formula to non-Gaussian noise**: The log₂(1+SNR) formula is optimal only for Gaussian input on AWGN channels. For non-Gaussian noise, capacity requires solving the max-MI optimization numerically.
4. **SNR in dB vs. linear**: The Shannon-Hartley formula requires S/N as a linear ratio. Converting from dB: S/N_linear = 10^(S/N_dB / 10). Common error is plugging dB directly.
5. **Equating bandwidth with bitrate**: Bandwidth (Hz) and bitrate (bits/second) are related by capacity but not equal. Capacity maps bandwidth × log(1+SNR) → bitrate; extra bandwidth has diminishing returns.

---

## Worked Example

**Fully specified hypothetical binary channel**

Let X,Y each have alphabet {0,1}, with independent errors across uses and transition matrix rows p(Y|X=0)=(0.77,0.23), p(Y|X=1)=(0.23,0.77). This is a BSC with crossover p=0.23. Base-2 entropy gives H_b(0.23)≈0.778011 and C≈0.221989 bits per channel use. Uniform inputs attain this single-use mutual information; capacity is a coding limit, not observed retrieval throughput. A separately specified BSC(0.10) has C≈0.531004 bits/use.

Aggregate retrieval precision or fraction of incorrect documents does **not** identify p(Y|X), binary symmetry, or bits per query. Counterexample: P(X=0)=0.77 and Y always equals 0 gives 77% accuracy, but identical transition rows and capacity zero. Before applying a channel model to retrieval, name the input/output alphabets, measure the conditional transition probabilities, test memory assumptions, and compute actual I(X;Y) for the observed input distribution. A retrieved document set is not automatically one transmitted bit; no retrieval efficiency multiplier follows from the hypothetical BSC comparison.

---

## Sources

- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 7 (Channel Capacity), Ch. 9 (Gaussian Channel, i.e. the AWGN / Shannon-Hartley result). Wiley. (Ch.8, Differential Entropy, is prerequisite background, not the capacity result itself — corrected 2026-07-11 from an earlier "Ch. 7–8" citation.)
- Hartley, R. V. L. (1928). Transmission of information. *Bell System Technical Journal*, 7(3), 535–563.
- Polyanskiy, Y., Poor, H. V. & Verdú, S. (2010). Channel coding rate in the finite blocklength regime. *IEEE Transactions on Information Theory*, 56(5), 2307–2359.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 9–11. Cambridge.
