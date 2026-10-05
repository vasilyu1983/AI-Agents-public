# Primitive 11: Redundancy and Compression

## Definition

Redundancy R = log M − H(X) (relative R/log M). Entropy rate H_rate = lim H(Xₙ | X_{n−1}..X₁) captures sequential structure as well.
Prefix codes satisfy Kraft Σ 2^{−lᵢ} ≤ 1, and an optimal one has H ≤ L < H + 1. Huffman is optimal among prefix codes for its supplied symbol or block PMF; arithmetic coding approaches the model's code length; LZ77/LZ78 approach the entropy rate of stationary ergodic sources asymptotically.
Model mismatch costs D_KL(P‖Q) extra bits per symbol (H(P,Q) = H(P) + KL).
NCD(x,y) = [C(xy) − min(C(x),C(y))]/max(C(x),C(y)) with a real compressor C.

## Traps

1. **Marginal Huffman on correlated sources** misses sequential redundancy; model the source (entropy rate) first, then use conditional/block codes, arithmetic coding or LZ.
2. **Binary compression is not semantic preservation.** An entropy-rate estimate or an LZ code length concerns exact reconstruction of symbols. It cannot certify that a shorter natural-language rewrite preserves meaning, nor set a token-count impossibility floor.
3. **NCD depends on the compressor**, headers, order and length, and practical values can exceed [0,1]. Calibrate duplicate thresholds on held-out duplicate and non-duplicate pairs; no universal NCD cut-off exists.
4. **Redundancy can be useful.** Repeated instructions or constraints in prompts can carry robustness and salience; review task-critical content before removing it.
5. **Kolmogorov claims.** Average-case compression (BPC) tracks LLM capability; shortest-program compression does not (see [`../../../references/llm-practice.md`](../../../references/llm-practice.md) §1).

## Known answer

A 1,200-symbol prompt over a 512-symbol alphabet with marginal H = 7.2 bits has R = 9 − 7.2 = 1.8 bits/symbol (20%). If a separately estimated entropy rate is 4.5 bits/symbol, an asymptotic binary code needs about 1,200 × 4.5 = 5,400 bits. That is a lossless coding benchmark; it does not establish that a 750-token rewrite preserves meaning.

## Sources

Cover & Thomas (2006) Ch. 5 (codes) and Ch. 13 (universal coding); Huffman (1952); Ziv & Lempel (1977; 1978); Witten, Neal & Cleary (1987); Cilibrasi & Vitányi (2005). Full references: [`../../../data/sources.json`](../../../data/sources.json).
