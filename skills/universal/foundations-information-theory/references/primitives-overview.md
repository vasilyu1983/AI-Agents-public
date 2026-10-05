---
description: Anti-patterns by domain for the 11 information-theory primitives (retrieval and context, training and evaluation, compression, LLM uncertainty, representations), plus core sources. The primitive table lives in SKILL.md.
status: stable
---

# Information Theory Primitives Overview

## Table of Contents

- [Why Information Theory Matters](#why-information-theory-matters)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
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

The primitive table and playbook links live in [`../SKILL.md`](../SKILL.md#quick-reference).

---

## Anti-Patterns by Domain

### Retrieval and Context Management

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Ranking documents by embedding cosine similarity only | Cosine similarity is a linear dot-product; MI captures non-linear dependence between query and document | Augment ranking with MI(query, doc) estimate (#2) |
| Filling context window greedily by relevance score | Pairwise redundancy between documents not measured | Reward task-relevant conditional information; low H(doc_i \| doc_j) indicates predictability, not high novelty. Calibrate any lexical/document proxy against the task (#1, #11) |
| Truncating prompts by character count | Character count ignores which content the task needs; truncation can drop instructions, negations and constraints | Preserve essential constraints first, then choose content by task-validated relevance at several budgets against an unpruned baseline. High entropy is not value: random text has high entropy and is useless, while a predictable negation can be essential (#1, #2) |

### Model Training and Evaluation

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Treating cross-entropy loss as distribution proximity | H(P,Q) = H(P) + D_KL(P‖Q); low loss is ambiguous when H(P) is large | Decompose CE into entropy + KL divergence (#3, #4) |
| Comparing models by perplexity across vocabularies | Perplexity is vocabulary-dependent | Normalize to bits-per-byte for vocabulary-neutral comparison (#4) |
| Using KL divergence as symmetric penalty | D_KL is asymmetric; mode-seeking vs. mean-seeking behavior depends on direction | Select forward or reverse KL by cost structure; use JS divergence for symmetric needs (#3) |

### Compression and Encoding

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Huffman code on correlated source | Symbol-wise Huffman uses a marginal PMF; correlated sources can have lower entropy rate. Block/conditional codes can also use Huffman coding | Estimate entropy rate; use arithmetic coding or LZ-family (#11) |
| Targeting zero distortion when lossy is acceptable | Lossless rate is always ≥ H(X); lossy can be far below | Apply rate-distortion to find optimal bitrate at target distortion (#6) |
| MDL not applied to model selection | Model complexity not traded against data fit | Compute two-part MDL: L(model) + L(data\|model) (#7) |

### LLM Uncertainty and Post-Training

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Token-level entropy or sequence log-prob used as a hallucination signal | Measures lexical freedom, not epistemic uncertainty; fires on paraphrase, silent on confident falsehoods | Cluster N sampled generations by NLI meaning-equivalence and take entropy over clusters (#1); use hidden-state probes when single-generation latency is required |
| Semantic entropy presented as a general factuality check | It detects confabulation (sampling instability), not consistently-held false beliefs | Pair with retrieval grounding or a knowledge check for stable-but-wrong outputs (#1) |
| Falling policy entropy in RLVR read as convergence | Reward is traded from entropy (R = −a·e^H + b); collapse marks a ceiling, not an optimum | Log policy entropy as a training metric; constrain updates on high log-prob/advantage-covariance tokens rather than adding a blanket entropy bonus (#1) |
| Agent handoff budgets set by token count | Optimizes message length, not task-relevant bits | Formulate as IB — minimize I(X;M) subject to I(M;task). Quantizing rather than truncating is a hypothesis for LLM handoffs: the supporting result (Farooq & Iqbal, ICRA 2026) is one synthetic robotics MARL domain, untested on LLM summaries or KV caches (#6, #8) |

### Feature and Representation Learning

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Feature extractors evaluated only on accuracy | Task-irrelevant variance retained; brittle under distribution shift | Apply IB: minimize I(X;T) subject to I(T;Y) ≥ threshold (#8) |
| Optimism about classifier lower bounds | Residual entropy H(Y\|features) positive but ignored | Apply Fano's inequality to derive minimum achievable error (#9) |

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
- Jiao, J., Venkat, K., Han, Y., & Weissman, T. (2015). Minimax estimation of functionals of discrete distributions. IEEE Transactions on Information Theory 61(5), 2835–2885. JVHW entropy/MI estimators.
- Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature*, 630, 625–630. Entropy over meaning-equivalence clusters; primitive #1 applied to confabulation detection.
- Kossen, J. et al. (2024). Semantic entropy probes: robust and cheap hallucination detection in LLMs. *arXiv:2406.15927*. Single-generation approximation of semantic entropy from hidden states.
- Cui, G. et al. (2025). The entropy mechanism of reinforcement learning for reasoning language models. *arXiv:2505.22617*. Empirical R = −a·e^H + b law; Clip-Cov and KL-Cov mitigations for entropy collapse.
- Huang, Y. et al. (2024). Compression represents intelligence linearly. *COLM 2024, arXiv:2404.09937*. BPC vs. benchmark score: 31 models, 12 benchmarks, ρ = −0.93 overall, −0.935 to −0.953 per domain; supports BPC as an evaluation proxy (#11).
- Farooq, A. & Iqbal, K. (2026). Bandwidth-efficient multi-agent communication through information bottleneck and vector quantization. *IEEE ICRA 2026, arXiv:2602.02035*. IB + VQ + gating for message compression in one synthetic robotics MARL domain; LLM transfer untested (#6, #8).
