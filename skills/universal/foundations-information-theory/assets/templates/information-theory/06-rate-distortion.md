# Primitive 6: Rate-Distortion

## Definition

R(D) = min over p(x̂|x) with E[d(X,X̂)] ≤ D of I(X;X̂): minimum bits per source symbol for expected distortion ≤ D under a named distortion d.
Non-increasing and convex in D; R(D) = 0 for D ≥ D_max. For a finite discrete source where zero distortion means exact reconstruction, R(0) = H(X); continuous sources under MSE need infinite rate at D = 0.
Gaussian source, variance σ², MSE: R(D) = ½ log₂(σ²/D) for D ≤ σ², else 0.
Blahut–Arimoto solves R(D) for supplied finite source and reconstruction alphabets and a distortion matrix.

## Traps

1. **Distortion must be the real criterion.** R(D) under MSE says nothing about ROUGE, semantic loss or task accuracy. State source, reconstruction alphabet, distortion and coding convention and their assumptions before quoting a rate.
2. **Bits are not tokens.** Code bits cannot be divided by a lexical entropy to certify a summary length. For summaries, measure quality at actual token budgets.
3. **Asymptotic.** Rates near R(D) are approachable as block length grows; a particular codec has overhead and finite-block loss.
4. **Wrong source model.** Gaussian R(D) on heavy-tailed data mispredicts. Discretizing a continuous source for Blahut–Arimoto is an approximation; report support, truncation and resolution.
5. **Model quantization.** R(D) framing is a design lens; the shipping evidence is an empirical task-loss vs bits curve ([`../../../references/llm-practice.md`](../../../references/llm-practice.md) §5). Generative codecs that must also look real need the rate-distortion-perception extension, which requires additional rate.

## Known answers

iid Gaussian, σ² = 1, MSE: D = 0.2 gives R = ½ log₂ 5 = 1.161 bits/sample; D = 0.1 gives ½ log₂ 10 = 1.661 bits/sample.
This bound concerns reconstruction of that scalar source under MSE. It cannot certify that a 193-token summary preserves meaning: ROUGE is not MSE, an embedding coordinate is not a token, and the distortion assumptions do not hold.

## Sources

Shannon (1959); Cover & Thomas (2006) Ch. 10; Blahut (1972). Full references: [`../../../data/sources.json`](../../../data/sources.json).
