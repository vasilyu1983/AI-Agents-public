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
- Benchmarking retrieval pipelines: the "channel" is the pipeline; X is the query intent; Y is the retrieved document set; C bounds how much query information can be preserved.
- Sizing token budgets: the "channel" from a source document to a compressed summary has capacity bounded by the compression ratio and distortion tolerance (see primitive #6).
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

1. **Ignoring channel memory**: Shannon capacity assumes a memoryless channel. Real channels (wireless multipath, bursty internet links) have memory. Capacity is lower or requires different analysis (channels with states, ISI correction).
2. **Treating capacity as a guaranteed rate**: C is achievable only with infinite block length codes. At practical block lengths, achievable rate is lower (see finite block length converse: Polyanskiy-Poor-Verdú 2010).
3. **Applying AWGN formula to non-Gaussian noise**: The log₂(1+SNR) formula is optimal only for Gaussian input on AWGN channels. For non-Gaussian noise, capacity requires solving the max-MI optimization numerically.
4. **SNR in dB vs. linear**: The Shannon-Hartley formula requires S/N as a linear ratio. Converting from dB: S/N_linear = 10^(S/N_dB / 10). Common error is plugging dB directly.
5. **Equating bandwidth with bitrate**: Bandwidth (Hz) and bitrate (bits/second) are related by capacity but not equal. Capacity maps bandwidth × log(1+SNR) → bitrate; extra bandwidth has diminishing returns.

---

## Worked Example

**BSC capacity for a noisy retrieval channel**

Model a keyword-to-document retrieval system as a BSC. Each "bit" of query intent either passes correctly (true positive, probability 1−p) or flips to a wrong document (probability p). Empirical measurement over 1,000 queries: 23% of documents retrieved are incorrect. p = 0.23.

```
C_BSC = 1 − H_b(0.23)
H_b(0.23) = −(0.23 · log₂ 0.23) − (0.77 · log₂ 0.77)
           = −(0.23 · (−2.12)) − (0.77 · (−0.38))
           = 0.487 + 0.293 = 0.780 bits
C_BSC = 1 − 0.780 = 0.220 bits per retrieval query
```

At 0.22 bits/query, the channel is transmitting only 22% of its theoretical maximum. Improving precision from 77% to 90% (p=0.10) raises C_BSC to 0.531 bits — a 2.4× improvement in channel efficiency, before any reranking.

---

## Sources

- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 7 (Channel Capacity), Ch. 9 (Gaussian Channel, i.e. the AWGN / Shannon-Hartley result). Wiley. (Ch.8, Differential Entropy, is prerequisite background, not the capacity result itself — corrected 2026-07-11 from an earlier "Ch. 7–8" citation.)
- Hartley, R. V. L. (1928). Transmission of information. *Bell System Technical Journal*, 7(3), 535–563.
- Polyanskiy, Y., Poor, H. V. & Verdú, S. (2010). Channel coding rate in the finite blocklength regime. *IEEE Transactions on Information Theory*, 56(5), 2307–2359.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 9–11. Cambridge.
