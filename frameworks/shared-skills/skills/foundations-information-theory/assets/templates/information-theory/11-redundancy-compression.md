# Primitive 11: Redundancy and Compression

## Definition

**Redundancy** of a source X with alphabet size M and entropy H(X):

```
R = log M − H(X)          [absolute redundancy, bits]
R% = (log M − H(X)) / log M   [relative redundancy, 0–1]
```

Redundancy measures the gap between the maximum possible entropy (uniform distribution) and the actual entropy. It is the exploitable structure that compression algorithms remove.

**Entropy rate** for a correlated source X₁, X₂, ...:

```
H_rate = lim_{n→∞} H(Xₙ | X_{n-1}, ..., X₁) = lim_{n→∞} H(X₁,...,Xₙ)/n
```

The total redundancy includes both marginal redundancy (R above) and sequential redundancy from conditional structure.

**Lossless compression codes**:

| Code | Optimal For | Properties |
|------|-------------|------------|
| Huffman | Known i.i.d. PMF | Optimal prefix-free code; L_avg ≤ H(X)+1 bit/symbol |
| Arithmetic | Known i.i.d. or sequential | Approaches H(X) arbitrarily closely; L_avg < H(X)+ε |
| LZ77 | Unknown distribution, sequential | Adapts online; approaches H_rate asymptotically; basis for zlib/DEFLATE |
| LZ78 / LZW | Unknown distribution, sequential | Dictionary-based; basis for GIF, early ZIP |

**Kraft inequality**: for any prefix-free code with code lengths l₁,...,lₙ:

```
Σᵢ 2^{−lᵢ} ≤ 1
```

**Coding theorem** (Shannon-Fano-Elias): there exists a prefix-free code with average length L satisfying:

```
H(X) ≤ L < H(X) + 1
```

**Normalized compression distance (NCD)**: a parameter-free measure of similarity using a compressor C:

```
NCD(x,y) = [C(xy) − min(C(x),C(y))] / max(C(x),C(y))
```

NCD ∈ [0,1]; NCD≈0 means x and y are compressible together (similar); NCD≈1 means incompressible together (dissimilar).

---

## When to Use

- **Compression efficiency audit**: measure how much redundancy a source has before choosing a codec.
- **Code family selection**: match the code to source statistics (i.i.d. vs. correlated; known vs. unknown distribution).
- **Context-window redundancy check**: estimate whether two retrieved documents carry redundant content before merging them.
- **Token budget analysis**: estimate the redundancy of a prompt to determine whether it can be shortened without information loss.
- **Similarity detection**: use NCD to detect near-duplicate documents or code plagiarism without explicit feature design.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| Source distribution p(x) or samples | PMF or corpus | Distribution or empirical data |
| Alphabet size M | Positive integer | Number of distinct symbols |
| H(X) or H_rate | Non-negative real (bits) | Entropy or entropy rate |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| R | Non-negative real (bits) | [0, log M] | Exploitable redundancy per symbol |
| R% | Real | [0, 1] | Fraction of max entropy that is redundant |
| L_avg | Non-negative real | ≥ H(X) | Average code length achieved by chosen code |
| NCD(x,y) | Real | [0, 1] | Compression-based similarity between x and y |

---

## Failure Modes

1. **Huffman on correlated sources**: Huffman is optimal for i.i.d. sources under a known PMF. For correlated sources (text, speech, code), H_rate < H(X₁); Huffman cannot exploit sequential redundancy. Use arithmetic coding or LZ-family codes instead.
2. **Not estimating H_rate before choosing a code**: The compression ratio achievable by LZ approaches H_rate, not H(X₁). If H_rate << H(X₁) (high correlation), LZ outperforms Huffman significantly; ignoring this wastes compression budget.
3. **NCD depends on compressor quality**: NCD is only as accurate as the underlying compressor. Weak compressors (e.g., run-length encoding) produce noisy NCD values. Use bzip2, zstd, or lzma for reliable NCD; test on held-out pairs.
4. **Treating redundancy as uniform across the source**: Redundancy is an average. Some segments of a document may be near-uniform (high local entropy); others may be highly predictable. Entropy per segment varies; apply local entropy estimation for selective compression.
5. **Arithmetic coding with model mismatch**: Arithmetic coding achieves H(X) only when the model used by the coder matches the true distribution. Model mismatch adds D_KL(P‖Q) extra bits per symbol (from cross-entropy decomposition: H(P,Q) = H(P) + KL).

---

## Worked Example

**Prompt redundancy budget**

A 1,200-token system prompt is being optimized for cost reduction. Estimate its compression properties:

1. **Token frequency distribution**: empirical PMF over the 512-token vocabulary shows H(X₁) = 7.2 bits/token (marginally). Alphabet size M = 512, log M = 9 bits.

```
R = 9 − 7.2 = 1.8 bits/token marginal redundancy
R% = 1.8/9 = 20%
```

2. **Sequential redundancy**: bigram entropy H(X₂|X₁) = 5.8 bits/token. LZ-family code can approach H_rate ≈ 4.5 bits/token (estimated from trigram model).

```
Additional sequential redundancy = 7.2 − 4.5 = 2.7 bits/token
Total redundancy ≈ 9 − 4.5 = 4.5 bits/token = 50%
```

3. **Compression target**: at H_rate = 4.5 bits/token, 1,200 tokens → 5,400 bits of information. To represent this at 7.2 bits/token (naive Huffman), you need 5,400/7.2 = 750 tokens. An LZ-style semantic compressor should achieve ~750 tokens; under 500 would require lossy compression (→ rate-distortion, primitive #6).

4. **NCD check for duplicate sections**: compute NCD(section_A, section_B) using zstd for each pair. Sections with NCD < 0.15 are near-duplicates and one can be removed without significant information loss.

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 5. Wiley. (Huffman, arithmetic coding theorems.)
- Huffman, D. A. (1952). A method for the construction of minimum-redundancy codes. *Proceedings of the IRE*, 40(9), 1098–1101.
- Ziv, J. & Lempel, A. (1977). A universal algorithm for sequential data compression. *IEEE Transactions on Information Theory*, 23(3), 337–343. (LZ77.)
- Ziv, J. & Lempel, A. (1978). Compression of individual sequences via variable-rate coding. *IEEE Transactions on Information Theory*, 24(5), 530–536. (LZ78.)
- Cilibrasi, R. & Vitányi, P. M. B. (2005). Clustering by compression. *IEEE Transactions on Information Theory*, 51(4), 1523–1545. (NCD.)
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 5–6. Cambridge.
- Witten, I. H., Neal, R. M. & Cleary, J. G. (1987). Arithmetic coding for data compression. *Communications of the ACM*, 30(6), 520–540.
