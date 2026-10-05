---
description: Information-theory decision rules for LLM evaluation and serving - compression as prediction, bits-per-byte comparability, proper scoring rules, speculative-decoding acceptance, and when not to trust quantization or KV-cache compression claims.
status: stable
---

# Information Theory in LLM Practice

Read this when an LLM evaluation or serving decision rests on an information quantity. Each section gives the rule, the check, and when not to use it. Serving implementation lives in ai-llm-inference; calibration methodology lives in foundations-statistical-inference.

## 1. Compression equals prediction

**Rule.** A model q plus arithmetic coding compresses a sequence x to about −log₂ q(x) bits (within a small constant per sequence). So total NLL in bits *is* a code length, and a better predictor is a better compressor on that data.

**Evidence.** Delétang et al., "Language Modeling Is Compression" (ICLR 2024, arXiv:2309.10668), [abstract and Table 1](https://arxiv.org/html/2309.10668v2): Chinchilla 70B compresses ImageNet patches to “43.4%” and LibriSpeech samples to “16.4%” of raw size, against PNG “58.5%” and FLAC “30.3%” (quoted raw compression rates; model parameters excluded).

**When not to use it.**
- Raw rates ignore the model's own size. The same paper reports that once parameters are counted (adjusted compression rate), large models are poor compressors of 1 GB of data. Do not claim a practical compressor from raw NLL.
- Their experiments chunk data into 2,048-byte sequences because of context limits; classical compressors see longer context. Compare at matched context.
- Average-case compression tracking capability (Huang et al., COLM 2024: 31 models, 12 benchmarks, ρ = −0.93 overall, −0.935 to −0.953 per domain) is not Kolmogorov optimality; frontier models score poorly on the KoLMogorov Test (ICLR 2025).

## 2. Perplexity, BPB and BPC comparability

**Rule.** Perplexity is exp of mean NLL *per token*. Two tokenizers split the same text into different token counts, so their perplexities are not comparable. Convert to a byte- or character-level rate on identical text:

`BPB = Σ_tokens (−log₂ q(token | prefix)) / bytes = token_count × log₂(perplexity) / bytes` (perplexity defined with natural-log NLL; the log₂ converts).

**Checks before comparing.** Same bytes (encoding, normalization, special tokens), same context length and document boundaries, same treatment of BOS/EOS, and NLL summed over the whole text, not averaged per document then averaged again. Report whether the figure is BPB (bytes) or BPC (characters); multibyte scripts make them differ.

**When not to use it.** BPB ranks predictors on one corpus; it does not rank instruction-following or tool use, and contamination of the eval corpus lowers BPB without new capability. Worked known answer: [`04-cross-entropy.md`](../assets/templates/information-theory/04-cross-entropy.md).

## 3. Proper scoring rules for confidence and calibration

**Rule.** Score probabilistic outputs (abstention gates, verbalized confidence, judge probabilities) with a strictly proper scoring rule, so that reporting the true belief is the unique optimum (Gneiting & Raftery, JASA 102(477):359–378, 2007). Log loss is the information-theoretic choice: its expectation is cross-entropy, so it decomposes into the outcome's entropy plus KL from the truth. Brier score is also strictly proper and bounded, so a single confident miss does not dominate it the way it dominates log loss.

**Decision.**
- Log loss when tail confidence matters (a confident wrong "safe" is expensive) and probabilities are never exactly 0 or 1 (clip, and state the clip).
- Brier when outliers should not dominate and a bounded, decomposable score is easier to explain.
- Accuracy, AUROC and selective risk/coverage are not proper scores; use them alongside, not instead.
- Method (reliability diagrams, bin choice, uncertainty): foundations-statistical-inference `references/predictive-calibration.md`.

**When not to use it.** A proper score compares forecasters on the same outcomes; it does not tell you where to put an abstention threshold. That is a cost decision (foundations-decision-theory).

## 4. Speculative decoding acceptance is a distribution match

**Rule.** With target distribution p and draft q at a position, the standard accept/reject scheme accepts a draft token with probability β = Σ_x min(p(x), q(x)) = 1 − TV(p, q). The expected acceptance rate is α = E[β] over prefixes, and with γ draft tokens per step the expected tokens produced per target call is (1 − α^{γ+1}) / (1 − α) (Leviathan, Kalman & Matias, ICML 2023, arXiv:2211.17192, Lemma 3.3, Corollary 3.6, Eq. 1). Output distribution is unchanged, so the gain is pure latency.

**Decision.** Choose the draft model and γ by measured α on production-like prompts **at the serving temperature and sampling settings**. The paper's own table shows α changes with temperature (for one T5 pair, 0.75 at argmax vs 0.62 at temperature 1).

**When not to use it.** α is not KL: a draft with small KL can still have lower acceptance than expected on the high-traffic prefixes, and KL is undefined where q has no support. Measure α directly. Wall-clock speed-up also depends on draft cost and batching, which α alone does not capture; hand off to ai-llm-inference.

## 5. Quantization and KV-cache compression: when not to trust the claim

**Rule.** Treat weight quantization and KV-cache compression as an empirical rate-distortion curve: x-axis bits per element (or cache bytes per token), y-axis **task** loss on the workloads you serve. Look for the knee; do not pick a point from a formula.

**Checks.**
- Perplexity and multiple-choice accuracy are not enough. Dutta et al. (NeurIPS 2024, arXiv:2407.09141) report "flips": answers change from correct to incorrect and back while aggregate accuracy stays similar, and compressed models do worse on generative evaluation. They recommend KL divergence to the baseline and flip rate as additional metrics.
- Long context is where cache compression breaks. Yuan et al. (arXiv:2407.01527) benchmark KV-cache quantization, token dropping, prompt compression and other long-context efficiency methods across seven task categories; test your own retrieval and multi-hop cases at the context lengths you serve rather than trusting a short-context average.
- Calibration-set sensitivity: re-measure when the calibration data differs from production traffic (language, domain, format).
- Classical R(D) needs a named source, reconstruction alphabet and distortion. It bounds nothing about task loss unless the distortion *is* task loss.

**When not to use it.** Do not accept "no perplexity change" or a single benchmark delta as a shipping gate. Do not treat surprisal or attention score as proof that an evicted token was unimportant; that is a proxy to benchmark (see SKILL.md Context-Window Budget).

## Sources

- Delétang, G. et al. (2024). Language Modeling Is Compression. ICLR 2024. https://arxiv.org/abs/2309.10668
- Leviathan, Y., Kalman, M. & Matias, Y. (2023). Fast Inference from Transformers via Speculative Decoding. ICML 2023. https://arxiv.org/abs/2211.17192
- Gneiting, T. & Raftery, A. E. (2007). Strictly Proper Scoring Rules, Prediction, and Estimation. JASA 102(477), 359–378. https://doi.org/10.1198/016214506000001437
- Dutta, A., Krishnan, S., Kwatra, N. & Ramjee, R. (2024). Accuracy is Not All You Need. NeurIPS 2024. https://arxiv.org/abs/2407.09141
- Yuan, J. et al. (2024). KV Cache Compression, But What Must We Give in Return? A Comprehensive Benchmark of Long Context Capable Approaches. arXiv:2407.01527. https://arxiv.org/abs/2407.01527
- Huang, Y. et al. (2024). Compression Represents Intelligence Linearly. COLM 2024. https://arxiv.org/abs/2404.09937
