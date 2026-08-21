---
description: Domain-agnostic overview of 11 information-theory primitives. Covers entropy, mutual information, KL/JS divergence, cross-entropy, channel capacity, rate-distortion, MDL, information bottleneck, Fano's inequality, AEP, and redundancy/compression.
last_verified: 2026-08-14
status: stable
---

# Information Theory Primitives Overview

## Table of Contents

- [Why Information Theory Matters](#why-information-theory-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Information Theory Matters

Every system that processes, transmits, stores, or compresses data is governed by information-theoretic limits. Without explicit measurement:

| Failure Mode | Information-Theory Diagnosis | What Goes Wrong |
|-------------|------------------------------|-----------------|
| Context window filled with redundant content | Entropy not measured; redundancy budget ignored | Token budget wasted; relevant signal crowded out |
| Retrieval returns high-scoring but near-duplicate documents | Pairwise mutual information not computed | Top-k contains little additional information |
| KL penalty applied symmetrically in RLHF | Asymmetry of D_KL(P‖Q) ignored | Incorrect regularization direction; optimization instability |
| Perplexity compared across models with different tokenizers | Vocabulary dependence not normalized | Invalid model comparison |
| Feature extractor retains task-irrelevant variance | Information bottleneck not applied | Overfitting; brittle representations |
| Compression code applied to correlated source | Entropy rate not estimated; i.i.d. assumption violated | Suboptimal compression ratio |

Each primitive in the index below addresses a specific failure mode.

---

## Primitive Index

11 primitives. This overview is the operational reference; use [`formal-theory-map.md`](formal-theory-map.md) for theorem assumptions, [`patterns-scenarios-traps.md`](patterns-scenarios-traps.md) for production failure modes, and [`../assets/templates/information-theory/README.md`](../assets/templates/information-theory/README.md) for standalone primitive playbooks.

| # | Primitive | Failure Mode | Primary Domains |
|---|-----------|-------------|-----------------|
| 1 | Shannon Entropy | Unquantified uncertainty; equal-probability assumptions | Context budgeting, source coding, model evaluation, hallucination gating (semantic entropy), RLVR training health (policy entropy) |
| 2 | Mutual Information | Linear-only dependence detection; biased finite-sample estimates | Retrieval scoring, feature selection, causal analysis |
| 3 | KL Divergence | Symmetric distance misuse; zero-probability singularities | RLHF regularization, VAE loss, hypothesis testing |
| 4 | Cross-Entropy | CE-as-similarity confusion; tokenizer-dependent perplexity | Loss functions, model comparison, perplexity |
| 5 | Channel Capacity | Throughput overestimation without noise accounting | Communication system design, retrieval pipeline design |
| 6 | Rate-Distortion | Lossless-only thinking when lossy is sufficient | Summarization, image/audio compression, token pruning |
| 7 | MDL Principle | Overfitting; model complexity not penalized | Model selection, hyperparameter tuning, Bayesian compression |
| 8 | Information Bottleneck | Representation retains task-irrelevant information | Deep learning, prompt compression, embedding design |
| 9 | Fano's Inequality | Optimistic error estimates when residual entropy is high | Classifier evaluation, retrieval accuracy bounds |
| 10 | Typical Sets / AEP | Block codes shorter than entropy lower bound | Source coding, block length planning, dataset size estimation |
| 11 | Redundancy & Compression | Compression without redundancy budget; wrong code family | Lossless compression, token budget optimization |

---

## Anti-Patterns by Domain

### Retrieval and Context Management

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Ranking documents by embedding cosine similarity only | Cosine similarity is a linear dot-product; MI captures non-linear dependence between query and document | Augment ranking with MI(query, doc) estimate (#2) |
| Filling context window greedily by relevance score | Pairwise redundancy between documents not measured | Penalize by H(doc_i \| doc_j) to maximize marginal information gain (#1, #11) |
| Truncating prompts by character count | Entropy per character varies; high-entropy content discarded disproportionately | Estimate segment entropy (#1) and prioritize high-entropy, high-MI segments (#2) |

### Model Training and Evaluation

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Treating cross-entropy loss as distribution proximity | H(P,Q) = H(P) + D_KL(P‖Q); low loss is ambiguous when H(P) is large | Decompose CE into entropy + KL divergence (#3, #4) |
| Comparing models by perplexity across vocabularies | Perplexity is vocabulary-dependent | Normalize to bits-per-byte for vocabulary-neutral comparison (#4) |
| Using KL divergence as symmetric penalty | D_KL is asymmetric; mode-seeking vs. mean-seeking behavior depends on direction | Select forward or reverse KL by cost structure; use JS divergence for symmetric needs (#3) |

### Compression and Encoding

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Huffman code on correlated source | Huffman assumes i.i.d.; correlated sources have entropy rate H_rate < H(X_1) | Estimate entropy rate; use arithmetic coding or LZ-family (#11) |
| Targeting zero distortion when lossy is acceptable | Lossless rate is always ≥ H(X); lossy can be far below | Apply rate-distortion to find optimal bitrate at target distortion (#6) |
| MDL not applied to model selection | Model complexity not traded against data fit | Compute two-part MDL: L(model) + L(data\|model) (#7) |

### LLM Uncertainty and Post-Training

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Token-level entropy or sequence log-prob used as a hallucination signal | Measures lexical freedom, not epistemic uncertainty; fires on paraphrase, silent on confident falsehoods | Cluster N sampled generations by NLI meaning-equivalence and take entropy over clusters (#1); use hidden-state probes when single-generation latency is required |
| Semantic entropy presented as a general factuality check | It detects confabulation (sampling instability), not consistently-held false beliefs | Pair with retrieval grounding or a knowledge check for stable-but-wrong outputs (#1) |
| Falling policy entropy in RLVR read as convergence | Reward is traded from entropy (R = −a·e^H + b); collapse marks a ceiling, not an optimum | Log policy entropy as a training metric; constrain updates on high log-prob/advantage-covariance tokens rather than adding a blanket entropy bonus (#1) |
| Agent handoff budgets set by token count | Optimizes message length, not task-relevant bits | Formulate as IB — minimize I(X;M) subject to I(M;task) — and quantize instead of truncating (#6, #8) |

### Feature and Representation Learning

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Feature extractors evaluated only on accuracy | Task-irrelevant variance retained; brittle under distribution shift | Apply IB: minimize I(X;T) subject to I(T;Y) ≥ threshold (#8) |
| Optimism about classifier lower bounds | Residual entropy H(Y\|features) positive but ignored | Apply Fano's inequality to derive minimum achievable error (#9) |

---

## Decision Checklist

- [ ] **Uncertainty quantification**: How many bits does a source produce? → entropy (#1)
- [ ] **Dependence / relevance**: How much does one variable inform another? → mutual information (#2)
- [ ] **Distribution comparison (directional)**: Measuring fit of approximate to true distribution? → KL divergence (#3)
- [ ] **Distribution comparison (symmetric)**: Need a proper metric? → JS divergence (symmetric form from #3)
- [ ] **Training loss / model fit**: Penalizing mismatch between predicted and true distribution? → cross-entropy (#4)
- [ ] **Cross-tokenizer model comparison**: Vocabulary-neutral perplexity needed? → bits-per-byte (#4)
- [ ] **Transmission limit**: Maximum reliable rate over noisy channel? → channel capacity (#5)
- [ ] **Lossy compression tradeoff**: Minimum bits for acceptable distortion? → rate-distortion (#6)
- [ ] **Model complexity penalty**: Selecting between models of different complexity? → MDL (#7)
- [ ] **Compressed representation**: Bottleneck that retains task relevance? → information bottleneck (#8)
- [ ] **Error lower bound**: Minimum error implied by residual uncertainty? → Fano's inequality (#9)
- [ ] **Block code design**: How long must blocks be for near-entropy-rate codes? → AEP (#10)
- [ ] **Compression efficiency**: How much redundancy remains exploitable? → redundancy / compression (#11)

---

## Sources

Use primary papers and textbooks as the strongest evidence tier. Practitioner posts are useful for templates and worked examples, not for claiming numeric thresholds transfer across settings.

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed. Wiley. Primary reference for all primitives.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*. Cambridge. Free at [inference.org.uk/mackay/itila/](https://www.inference.org.uk/mackay/itila/). Entropy/probability (Ch.2–3), source coding (Ch.4–6), channel capacity (Ch.9–11), model comparison / Occam's razor — MDL-adjacent, not IB (Ch.28). Corrected 2026-07-11: earlier drafts of this skill mislabeled Ch.28 as "IB-adjacent material"; MacKay's book predates the information bottleneck's ML popularization and does not treat IB. Ch.28 grounds primitive #7 (MDL), not #8 (IB).
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379–423.
- Tishby, N., Pereira, F. C., & Bialek, W. (2000). The information bottleneck method. *arXiv:physics/0004057*.
- Rissanen, J. (1978). Modeling by shortest data description. *Automatica*, 14(5), 465–471. MDL origin.
- Grünwald, P. (2007). *The Minimum Description Length Principle*. MIT Press.
- Saxe, A. M. et al. (2018). On the information bottleneck theory of deep learning. *ICLR 2019*. IB rebuttal.
- Tishby, N. & Schwartz-Ziv, R. (2017). Opening the black box of deep neural networks via information. *arXiv:1703.00810*.
- Belghazi, M. I. et al. (2018). MINE: Mutual information neural estimation. *ICML 2018*.
- Paninski, L. (2003). Estimation of entropy and mutual information. *Neural Computation*, 15(6), 1191–1253. Bias correction.
- Valiant, G. & Valiant, P. (2011). Estimating the unseen. *STOC 2011 / JVHW estimator*. Finite-sample MI correction.
- Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature*, 630, 625–630. Entropy over meaning-equivalence clusters; primitive #1 applied to confabulation detection.
- Kossen, J. et al. (2024). Semantic entropy probes: robust and cheap hallucination detection in LLMs. *arXiv:2406.15927*. Single-generation approximation of semantic entropy from hidden states.
- Cui, G. et al. (2025). The entropy mechanism of reinforcement learning for reasoning language models. *arXiv:2505.22617*. Empirical R = −a·e^H + b law; Clip-Cov and KL-Cov mitigations for entropy collapse.
- Huang, Y. et al. (2024). Compression represents intelligence linearly. *COLM 2024, arXiv:2404.09937*. BPC vs. benchmark score correlation ≈ −0.95 across 30 models; supports BPC as an evaluation proxy (#11).
- Farooq, A. & Iqbal, K. (2026). Bandwidth-efficient multi-agent communication through information bottleneck and vector quantization. *IEEE ICRA 2026, arXiv:2602.02035*. IB + VQ + gating for message compression (#6, #8).
