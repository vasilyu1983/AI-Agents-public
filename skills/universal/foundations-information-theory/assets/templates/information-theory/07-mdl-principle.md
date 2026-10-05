# Primitive 7: Minimum Description Length

## Definition

Choose M minimizing L(M) + L(D|M) in bits, where both codes are explicit.
Two-part (crude) MDL encodes the model then the data. Refined MDL uses universal codes: normalized maximum likelihood (minimax regret) or prequential (online) codes.
BIC ≈ −2 log L(D|θ̂) + k log n is a large-n approximation to two-part MDL for regular models.

## Traps

1. **The code decides the answer.** An arbitrary L(M) can make MDL favor any model. State the coding convention (parameter precision, integer codes) or use NML or prequential codes.
2. **BIC is not MDL** for small n or non-regular models (mixtures, neural networks).
3. **Free parameters** (L(M) = 0) reduce MDL to maximum likelihood and overfit.
4. **Relabelling is not MDL.** "We picked the shorter prompt" is not MDL without a code for prompts and a data-given-prompt code in compatible bit units. Never compare raw token length with bits of information gain.
5. **Sequential data** suits prequential coding, which accumulates cost as data arrives.
6. **Kolmogorov complexity** is uncomputable; LLM perplexity is average-case prediction, not shortest-program length.

## Known answer

Toy two-part comparison on the same data, with a declared code of 13 bits per parameter (an assumption, not a property of 32-bit floats): model A with 10,000 parameters costs 130,000 model bits plus 52,000 data bits = 182,000; model B with 100,000 parameters costs 1,300,000 + 41,000 = 1,341,000. A wins under this code. Changing the per-parameter cost changes the answer, which is the point of trap 1.

## Sources

Rissanen (1978; 1996); Grünwald (2007); MacKay (2003) Ch. 28 (model comparison and Occam's razor). Not in sources.json: Schwarz, G. (1978), Estimating the dimension of a model, *Ann. Stat.* 6(2), 461–464. Full references: [`../../../data/sources.json`](../../../data/sources.json).
