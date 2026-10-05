# Primitive 4: Cross-Entropy, Perplexity and Bits-per-Byte

## Definition

H(P,Q) = −Σ p(x) log q(x) = H(P) + D_KL(P‖Q). With P fixed, minimizing cross-entropy over Q minimizes D_KL(P‖Q).
Perplexity = exp of mean token NLL (natural log) = 2^(mean bits per token).
BPB = Σ_tokens (−log₂ q(token|prefix)) / bytes = token_count × log₂(perplexity) / bytes. It is tokenizer-neutral on identical bytes.

## Traps

1. **CE as similarity.** Low loss can coexist with large H(P); compare distributions with KL/JSD.
2. **Perplexity across tokenizers.** Different token counts for the same text make perplexities incomparable; use BPB or BPC on the same corpus, encoding, special-token handling and context protocol.
3. **Marginal vs conditional decomposition.** For classification, loss = H(Y|X) + expected conditional KL, not H(Y) + KL. Balanced deterministic labels can have H(Y) = 1 bit and H(Y|X) = 0, so label frequencies cannot diagnose irreducible loss.
4. **Length bias.** Sum NLL over the whole text before dividing; do not average per document and then average again.
5. **Perplexity is not quality.** Low perplexity does not imply calibration, factuality or instruction following. For compressed models see [`../../../references/llm-practice.md`](../../../references/llm-practice.md).

## Known answer

Same 10,000,000-byte corpus. Model A: 2.4M tokens, perplexity 12.3. Model B: 3.1M tokens, perplexity 18.7 (both natural-log token NLL).
BPB_A = 2.4e6 × log₂ 12.3 / 1e7 = 0.869. BPB_B = 3.1e6 × log₂ 18.7 / 1e7 = 1.310. A is better on this corpus; normalization makes the comparison valid, it does not reverse the ranking here.

## Sources

Cover & Thomas (2006) Ch. 2 and 5; Huang et al. (2024), arXiv:2404.09937 (BPC used because tokenizers differ); Delétang et al. (2024), arXiv:2309.10668; Müller et al. (2019), arXiv:1906.02629. Full references: [`../../../data/sources.json`](../../../data/sources.json).
