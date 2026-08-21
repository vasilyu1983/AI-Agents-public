---
name: foundations-information-theory
description: Information-theory primitives for AI systems, entropy, mutual information, KL, compression, channel limits, MDL, bottlenecks, and signal quality. Use when quantifying information.
compatibility: Portable core only.
version: "1.2"
last_validated: 2026-08-14
---

# Information Theory Foundations


## When to Apply

**Apply information-theory when:**
- Compressing prompts, retrieval contexts, logs, or feature sets
- Drift detection — distribution shift from baseline (KL, JS divergence)
- Feature selection by mutual information with target
- Retrieval re-ranking, MMR, or diversity-aware candidate selection
- Prompt-quality diagnosis via output-conditional entropy / Fano bound
- Hallucination / abstention gating via semantic entropy over meaning-clustered samples (#1)
- RL post-training diagnostics — policy-entropy collapse is the dominant failure mode in RLVR (#1)
- Agent-to-agent message budgets and KV-cache handoff sizing, framed as a bottleneck/rate problem (#6, #8)

**Skip and use simpler alternatives when:**
- Question is about *causation*, not *information* — use foundations-causal-inference
- Single-feature linear correlation is sufficient — Pearson r is cheaper than MI for monotonic continuous data
- Streaming data with hard latency budget — full MI/KL is too slow; use sketches or sampled approximations
- N samples too small for stable entropy estimate (rule of thumb n > 5 × #bins per variable)
- Problem is system-stability or feedback control — use foundations-control-theory
- Bits/nats unit doesn't map to a business decision — risk of treating it as decoration, not signal

---

11 applied information-theory primitives for quantifying uncertainty, signal, and compression, backed by a formal theory map. Each primitive solves a specific measurement problem. Primitives are domain-agnostic: the same entropy calculation that budgets a context window also bounds a lossless compressor; mutual information that scores retrieval also measures feature relevance in ML.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Anti-Patterns](#anti-patterns)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Practitioner Judgment](#practitioner-judgment)
- [Navigation](#navigation)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Core Formula | Use When |
|---|-----------|-------------|----------|
| 1 | [Shannon Entropy](#1-shannon-entropy) | H(X) = −Σ p log p | Measuring uncertainty, budgeting bits. Two high-value LLM specializations: *semantic* entropy — cluster sampled generations by meaning (NLI equivalence), take entropy over clusters, not tokens (Farquhar et al., *Nature* 630, 2024) — for hallucination detection; and *policy* entropy for RLVR collapse diagnosis. |
| 2 | [Mutual Information](#2-mutual-information) | I(X;Y) = H(X) − H(X\|Y) | Scoring relevance, detecting dependence |
| 3 | [KL Divergence](#3-kl-divergence) | D_KL(P‖Q) = Σ p log(p/q) | Comparing distributions, training objectives |
| 4 | [Cross-Entropy](#4-cross-entropy) | H(P,Q) = −Σ p log q | Loss functions, perplexity, model evaluation |
| 5 | [Channel Capacity](#5-channel-capacity) | C = max_{p(x)} I(X;Y) | Theoretical throughput ceilings |
| 6 | [Rate-Distortion](#6-rate-distortion) | R(D) = min_{p(x̂\|x)} I(X;X̂) | Lossy compression tradeoffs. When the reconstruction must also *look real* (generative models, image compression), apply the rate-distortion-perception (RDP) extension: high perceptual fidelity requires strictly higher rate than distortion alone predicts (Niu et al., *Entropy* 2025; Lei et al., NeurIPS 2025). |
| 7 | [MDL Principle](#7-mdl-principle) | MDL = L(M) + L(D\|M) | Model selection, Occam complexity |
| 8 | [Information Bottleneck](#8-information-bottleneck) | min I(X;T) − βI(T;Y) | Representation compression, deep learning |
| 9 | [Fano's Inequality](#9-fanos-inequality) | P_e ≥ (H(X\|Y) − 1) / log\|X\| | Error lower bound from residual uncertainty |
| 10 | [Typical Sets / AEP](#10-typical-sets--aep) | \|A_ε^(n)\| ≈ 2^{nH(X)} | Source coding theorem, block length planning |
| 11 | [Redundancy & Compression](#11-redundancy--compression) | R = H_max − H(X) | Compression budget, Huffman / LZ framing |

---

## Primitive Index

Each primitive is summarized here, expanded in [`references/primitives-overview.md`](references/primitives-overview.md), and covered by standalone playbooks under [`assets/templates/information-theory/`](assets/templates/information-theory/). Use [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs theorem assumptions or derivation boundaries.

| # | Mechanism | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | Shannon Entropy | Treating all tokens/states as equally uncertain; unquantified information budget |
| 2 | Mutual Information | Correlation-based relevance scoring that ignores non-linear dependence |
| 3 | KL Divergence | Symmetric distance assumptions on asymmetric divergences; division-by-zero on Q=0 |
| 4 | Cross-Entropy | Conflating cross-entropy loss with distribution similarity |
| 5 | Channel Capacity | Over-estimating throughput without accounting for noise |
| 6 | Rate-Distortion | Assuming lossless compression is achievable when distortion is acceptable |
| 7 | MDL Principle | Overfitting via models that describe noise rather than signal |
| 8 | Information Bottleneck | Feature extractors that retain task-irrelevant variance |
| 9 | Fano's Inequality | Optimism about classifiers when residual entropy is high |
| 10 | Typical Sets / AEP | Designing block codes shorter than entropy lower bound |
| 11 | Redundancy & Compression | Compressing without knowing the redundancy budget; picking the wrong code family |

---

## Formal Supporting Theory

| Theory Area | Use When | Applied Primitives It Grounds |
|---|---|---|
| Measure-theoretic foundations | Need discrete vs continuous entropy, differential entropy caveats, or invariance boundaries | #1, #2, #3 |
| Source coding | Need lossless compression limits, AEP, entropy rate, or universal coding | #1, #10, #11 |
| Channel coding | Need noisy-channel throughput limits and finite-blocklength caveats | #5, #9 |
| Rate-distortion theory | Need lossy compression tradeoffs and distortion measure assumptions | #6 |
| Statistical divergence | Need KL, JS, f-divergences, cross-entropy, or variational objectives | #3, #4 |
| Model selection | Need MDL, stochastic complexity, Bayesian code-length analogies | #7 |
| Representation learning | Need IB, sufficient statistics, compression vs prediction tradeoffs | #2, #8 |
| Estimation theory | Need finite-sample MI/entropy estimator bias and confidence intervals | #1, #2 |

---

## Anti-Patterns

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Using KL divergence as a symmetric distance metric | D_KL(P‖Q) ≠ D_KL(Q‖P); treating it like Euclidean distance produces asymmetric results and can cause infinite penalty when Q assigns zero probability to events P can produce | Use Jensen-Shannon divergence (symmetric, bounded [0,1]) or explicitly select the forward/reverse direction based on the cost asymmetry you intend (#3) |
| Estimating mutual information in high dimensions from finite samples | Sample estimators of MI are positively biased and scale with dimension; reported MI values can be inflated several-fold on small datasets | Apply NSB or JVHW correction for discrete MI; use MINE or NWJ estimators for continuous variables; always report confidence intervals alongside MI estimates (#2). New (2025): use the Abdelaleem-Martini-Nemenman protocol (arXiv:2506.00330) — confidence intervals + consistency checks before trusting any neural MI estimate; estimators are reliable only when dependence lies in a low-dimensional latent subspace. For continuous high-dimensional data, consider normalizing-flow-based difference-of-entropies estimators (Ni & Lotz, arXiv:2502.13085) as an alternative to MINE. |
| Treating cross-entropy as a distribution similarity score | H(P,Q) = H(P) + D_KL(P‖Q); a low cross-entropy loss does not imply the model distribution is close to the data distribution when H(P) is large | Decompose cross-entropy into entropy + KL divergence; use JS divergence or Wasserstein distance for direct distribution comparison (#4) |
| Comparing perplexity scores across tokenizers | Perplexity is exp(H(P,Q)) conditioned on a vocabulary; different tokenizers produce different sequence lengths for the same text, making cross-tokenizer perplexity incomparable | Normalize by bits-per-character (BPC) or bits-per-byte (BPB) for vocabulary-neutral comparison (#4) |
| Ignoring the continuous-discrete entropy distinction | Differential entropy (continuous) can be negative; it lacks the absolute probability interpretation of discrete entropy and is not invariant under invertible transforms | Explicitly state which entropy definition is in use; for continuous random variables, use mutual information (which is transform-invariant) rather than raw differential entropy (#1) |
| Applying the Huffman/LZ code directly without checking entropy rate | Huffman codes are optimal only for known i.i.d. distributions; they are suboptimal for correlated sources where the entropy rate H(X_n | X_{n-1},...,X_1) < H(X_1) | Model source correlations first (estimate entropy rate); apply arithmetic coding or LZ-family codes that exploit sequential dependencies (#11) |
| Assuming the information bottleneck β controls compression monotonically | The IB curve is non-convex for finite-sample or discrete cases; solutions can jump discontinuously as β changes | Sweep β densely and validate the I(T;X)/I(T;Y) tradeoff curve empirically; confirm phase transitions match the task (#8) |
| Using InfoNCE/NWJ as an unconstrained MI estimator in contrastive learning | InfoNCE is bounded above by log(K) where K = number of negative samples; severely underestimates MI when true MI >> log(K), which is common in SSL pretraining; gradients become misleading at high MI regimes | Apply f-DIME estimators (Letizia, Novello & Tonello, NeurIPS 2024; code: github.com/tonellolab/fDIME) which use derangement architecture to remove the upper-bound artefact; or use the Abdelaleem-Martini-Nemenman confidence-interval protocol (#2) to detect estimator failure before trusting MI values |
| Claiming "LLMs are optimal compressors" without a Kolmogorov benchmark | Current models (GPT-4o, Llama-3.1-405B) fail the KoLMogorov Test — producing the *shortest* program for a data sequence is distinct from next-token prediction; synthetic gains do not transfer to real sequences | Split the claim in two, because the evidence points opposite ways. *Average-case* compression does track capability: BPC on a held-out corpus correlates near-linearly with benchmark scores, Pearson ≈ −0.95 across 30 models and 12 benchmarks (Huang et al., COLM 2024, arXiv:2404.09937) — which makes BPC a cheap, contamination-resistant evaluation proxy. *Worst-case* compression does not: producing the shortest program for a sequence is a different problem, and frontier models score poorly on the KoLMogorov Test (ICLR 2025), with synthetic gains failing to transfer to real sequences. Use BPC to rank models; do not upgrade that correlation into a Kolmogorov-optimality claim (#11) |
| Using classical R(D) to bound generative model compression | Classical R(D) does not account for perceptual quality; the RDP tradeoff proves that matching the source *distribution* (not just minimising distortion) requires additional rate | Apply the three-way RDP function; use KL, TV, or Wasserstein as the perception constraint divergence measure (#3, #6) |
| Ignoring R(D) theory when choosing LLM weight quantization scheme | Scalar quantization is suboptimal; block-coding (vector quantization) yields strictly lower distortion at the same bitrate per classical R(D) results — Radio (ICML 2025) directly applies R(D)-optimal stochastic quantization to LLM weights and outperforms standard PTQ | Frame LLM quantization as a rate-distortion optimization; prefer vector/lattice quantizers over scalar; use Blahut-Arimoto to find the optimal bit allocation per layer (#6, #7) |
| Using token-level entropy or sequence log-prob to detect hallucination | Token entropy is high whenever *phrasing* is free, which is almost always; the same fact stated five ways scores as maximum uncertainty. It measures lexical, not epistemic, uncertainty, so it fires on paraphrase and misses confident falsehoods | Compute entropy over meaning-equivalence clusters, not tokens: sample N generations, cluster by bidirectional NLI entailment, take entropy of the cluster distribution (Farquhar et al., *Nature* 630:625–630, 2024). For single-generation latency budgets, semantic entropy probes read the estimate off hidden states (Kossen et al., arXiv:2406.15927). Semantic entropy detects confabulation — arbitrary, sampling-unstable answers — not consistently-wrong beliefs, which are invisible to any sampling-based estimator (#1) |
| Treating falling policy entropy during RL post-training as convergence | In RLVR the empirical fit R = −a·e^H + b holds: downstream reward is *bought* with policy entropy, so a collapsed-entropy policy has spent its exploration budget and has hit a ceiling, not found an optimum. Over 95% of the entropy drop and most of the gain occur early, then a plateau (Cui et al., arXiv:2505.22617) | Log policy entropy as a first-class training metric and fit the R/H curve to predict the ceiling before spending the compute. Collapse is driven by tokens with high covariance between log-prob and advantage — restrict updates on those via Clip-Cov or KL-Cov rather than adding a blanket entropy bonus, which trades away the signal indiscriminately (#1) |
| Sizing agent-to-agent messages by token count instead of task-relevant information | Multi-agent handoffs are a rate-constrained channel; a message budget set by token count optimizes the wrong quantity and drops task-critical bits while preserving fluent filler | Frame the handoff as an IB problem — minimize I(X;M) subject to I(M;task) — and quantize the message rather than truncating it. Farooq & Iqbal (IEEE ICRA 2026, arXiv:2602.02035) combine IB with vector quantization and a gating mechanism for 71.4% bandwidth reduction; the same framing applies to KV-cache handoffs and summary passing between LLM agents (#6, #8) |
| Applying standard IB directly to multimodal (image-text) representations | Standard IB's randomness and hyperparameter dependency cause failure in multimodal settings; the IB curve is not interpretable for CLIP-type architectures | Use NIBT (ICLR 2025, code: github.com/LMBTough/NIB) which satisfies attribution axioms and eliminates these pathologies (#8) |

---

## Misuse Boundaries

| Misuse | Why It Is Wrong | Required Correction |
|---|---|---|
| Comparing perplexity across tokenizers | Perplexity depends on tokenization | Use bits-per-byte or bits-per-character |
| Treating differential entropy like discrete entropy | Differential entropy can be negative and coordinate-dependent | Use mutual information or specify units/transform |
| Using KL as a metric | KL is asymmetric and can be infinite | Use JS, Wasserstein, or explicit forward/reverse KL |
| Reporting MI from small high-dimensional samples | MI estimators are biased and unstable | Add estimator choice, confidence intervals, and permutation baselines |
| Treating IB as settled DNN theory for either unimodal DNNs (compression phase is activation-dependent, Saxe et al. 2018) or multimodal models. The 2025 exception: in multimodal (CLIP-type) settings, the Narrowing IB Theory (NIBT, ICLR 2025) and CIBR (ICANN 2025) provide peer-reviewed working applications of IB to representation interpretability and generalization — but only with the NIBT reformulation, not standard IB. For unimodal DNNs with ReLU activations, the Generalized IB (GIB, Westphal et al. arXiv:2509.26327, preprint 2025/2026) reformulates IB via synergistic information and recovers compression phases where standard IB fails; note GIB is unreviewed — treat as promising candidate, not established practice. | Compression claims are activation/estimator dependent; multimodal IB requires NIBT reformulation; ReLU unimodal IB failure has a candidate fix in GIB | Cite both IB and rebuttal evidence; for multimodal settings use NIBT (code: github.com/LMBTough/NIB); for ReLU unimodal architectures, evaluate GIB once peer-reviewed |
| Equating LLM perplexity with Kolmogorov-complexity-optimal compression | Cross-entropy/perplexity measures average-case prediction, not worst-case shortest-program compression | Use KoLMogorov Test benchmark to bound the gap; flag "compression = intelligence" claims as unverified (#11, #7) |
| Calling content “high information” because it is long | Length is not entropy or relevance | Estimate novelty, redundancy, and query MI |
| Ignoring finite-blocklength effects | Asymptotic theorems do not guarantee short-block performance | Check finite-blocklength bounds |

---

## Decision Checklist

- [ ] **Uncertainty measurement**: Need to quantify how many bits a distribution contains? → Shannon entropy (#1)
- [ ] **Relevance scoring**: Need to measure how much knowing X reduces uncertainty about Y? → mutual information (#2)
- [ ] **Distribution comparison (asymmetric)**: Comparing a learned distribution to a reference where direction matters (e.g., RLHF KL penalty)? → KL divergence (#3)
- [ ] **Distribution comparison (symmetric)**: Need a proper metric between distributions? → JS divergence via KL (#3)
- [ ] **Training objective / model evaluation**: Computing a loss between predicted and true distribution? → cross-entropy (#4)
- [ ] **Model comparison across tokenizers**: Need tokenizer-neutral perplexity? → bits-per-byte normalization (#4)
- [ ] **Throughput ceiling**: Need the theoretical limit on reliable transmission over a noisy channel? → channel capacity (#5)
- [ ] **Compression with acceptable loss**: Need to find the minimum bitrate for a target distortion? → rate-distortion (#6)
- [ ] **Model selection / Occam's razor**: Choosing between models of different complexity? → MDL (#7)
- [ ] **Feature / representation compression**: Building a compressed representation that retains task-relevant information? → information bottleneck (#8)
- [ ] **Error lower bound**: Need the minimum achievable classification error given residual uncertainty? → Fano's inequality (#9)
- [ ] **Block code length planning**: Determining how many samples are needed for near-optimal source coding? → AEP / typical sets (#10)
- [ ] **Compression efficiency audit**: Measuring how much redundancy remains in a source relative to its entropy? → redundancy / compression (#11)

---

## Composition Recipes

### Context-Window Budget

**Problem**: A retrieval or summarization pipeline fills a context window but needs to prioritize content under a token budget.

**Stack**:
1. Estimate entropy of each candidate segment (#1) — higher entropy segments carry more novel information.
2. Compute I(segment; query) (#2) — rank by relevance, using mutual information as the relevance signal.
3. Apply MDL penalty (#7) — prune segments whose description cost (length) exceeds the information gain they add.

**Output**: A ranked, pruned set of segments that maximizes information per token.

**LLM app note**: This maps directly to KV-cache pruning and gist-token compression in LLM inference: high-surprisal tokens (H(token | context) large) carry more information and should be retained; low-surprisal tokens are candidates for KV eviction or soft merging. First-token surprisal (ICML 2025) operationalizes this for CoT step pruning.

**Inputs:** Candidate segments S₁…Sₙ, query Q, token budget B, per-segment length len(Sᵢ).
**Rules:** Score each segment as I(Sᵢ; Q) / len(Sᵢ); compute MDL penalty = L(Sᵢ) + L(data | Sᵢ); drop segments where len(Sᵢ) > information gain relative to budget B; rank remaining by MI-per-token descending.
**Outputs:** Ordered list of segments with entropy H(Sᵢ), MI(Sᵢ; Q), and MDL cost; retain/drop decision for each candidate.

### Retrieval Reranking

**Problem**: A dense retrieval system returns k candidates; a reranker must select the top-m without redundancy.

**Stack**:
1. Compute MI(query, doc_i) for each candidate (#2) — score individual relevance.
2. Compute pairwise redundancy using conditional entropy H(doc_i | doc_j) (#1) — penalize near-duplicate content.
3. Use redundancy budget (#11) — select the set of m documents that maximizes total information after subtracting pairwise overlap.

**Output**: A diverse, high-relevance set with no redundant documents.

**Inputs:** k candidate documents doc₁…docₖ, query Q, target set size m, feature distribution P(X), baseline distribution P_baseline, current distribution P_today.
**Rules:** Score relevance as MI(Q; docᵢ); penalise redundancy using H(docᵢ | docⱼ) for each pair; keep features where MI(X;Y) / H(Y) > 10%; alert on drift when KL(P_today ‖ P_baseline) > 0.05 nats sustained 3 days; greedily select m documents maximising Σ MI(Q; docᵢ) − Σ overlap penalty.
**Outputs:** Top-m document set with per-document MI(Q; docᵢ), pairwise redundancy scores H(docᵢ | docⱼ), drift flag (KL value, days sustained, severity level).

**Worked example:** Feature selection for a churn model. Feature X = "support tickets last 30 days", target Y = churn. P(Y=1) = 0.1, so H(Y) = −0.1·log₂0.1 − 0.9·log₂0.9 ≈ 0.469 bits. Bin X into [0 tickets, 1–2, 3+] with conditional distributions giving H(Y|X) ≈ 0.31 bits → MI(X;Y) = 0.469 − 0.31 = 0.16 bits = 34% of H(Y). Threshold: keep features with MI/H(Y) > 10%; X qualifies. For drift detection, compute KL(P_today ‖ P_baseline) weekly on the feature distribution; alert when KL > 0.05 nats sustained 3 days. Reference: KL = 0 means identical distributions; KL ≈ 0.69 nats ≈ 2× odds shift on a binary feature.

### Prompt Complexity Diagnosis

**Problem**: A prompt produces high-variance outputs; unclear whether the source is prompt ambiguity, model uncertainty, or stochastic decoding.

**Stack**:
1. Estimate H(output | prompt) empirically across N samples (#1) — measures residual output entropy under fixed prompt.
2. Apply Fano's inequality (#9) — derive a lower bound on the classification/decision error implied by that residual entropy.
3. Use cross-entropy and perplexity (#4) — decompose the model's token-level uncertainty to locate which prompt spans drive variance.
4. If variance is high, apply IB framing (#8) — determine whether the prompt is transmitting task-relevant information or noise.

**Output**: A diagnosis separating prompt ambiguity from model uncertainty, with actionable edits targeted to high-entropy spans.

**Inputs:** Prompt P, N sampled outputs O₁…Oₙ, token-level log-probabilities from the model, task label set Y.
**Rules:** Estimate H(output | prompt) = −(1/N) Σ log p(Oᵢ | P) across N samples; derive error lower bound P_e ≥ (H(X|Y) − 1) / log|X| via Fano's inequality; decompose token-level cross-entropy H(P,Q) = H(P) + D_KL(P‖Q) to isolate high-variance spans; apply IB framing if H(output | prompt) > threshold — check whether prompt spans carry I(span; task) > 0.
**Outputs:** Per-prompt H(output | prompt) score, Fano error bound P_e, ranked list of high-entropy prompt spans with I(span; task) scores, diagnosis label (prompt ambiguity / model uncertainty / decoding noise), and recommended prompt edits.

---

## Workflow

1. Identify the measurement problem (uncertainty quantification, distribution comparison, compression bound, model selection, representation learning).
2. Use the [Decision Checklist](#decision-checklist) to map the problem to a primitive.
3. Open [`references/primitives-overview.md`](references/primitives-overview.md) for definitions, failure modes, and source anchors.
4. For multi-step pipelines, use the [Composition Recipes](#composition-recipes) to stack primitives.
5. Check [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before applying to production — KL asymmetry, MI estimation bias, tokenizer effects, and finite-blocklength gaps are common failure modes.

---

## ASCII Flow

```text
Uncertainty, channel, or representation question
  -> Define random variables, distributions, code, channel, or embedding
  -> Select measure: entropy, KL, MI, capacity, MDL, bottleneck, or coding bound
  -> Verify estimator and finite-sample assumptions
     +-- estimator biased or data thin -> bound uncertainty or collect more data
     +-- assumptions acceptable -> compute metric
  -> Interpret directionality, units, and production limits
```

---

## Practitioner Judgment

The formulas are the easy part. What separates a top-tier application of this skill from a decorative one is knowing when the framing is load-bearing, when an MI number can be trusted, and where the metaphor stops.

### When Information-Theoretic Framing Helps vs. When It Decorates

**Helps** — the framing changes a concrete decision:
- A hard numeric budget exists (token limit, storage quota, wire bandwidth) and the question is "how many bits does this actually need" — entropy/rate-distortion bound the answer before you guess at a truncation heuristic.
- Two things must be compared on a common footing that raw scores hide — bits-per-byte across tokenizers, forward vs. reverse KL direction in an RLHF penalty, NCD instead of a hand-built similarity feature.
- A claim of "the model/feature/prompt has enough signal" can be falsified before spending compute — Fano's bound on a fixed feature set, or MI(feature; target) before adding a feature to a pipeline.
- Non-linear dependence matters and correlation would systematically miss it (MI as a first-pass relevance or leakage check, followed by a causal study if intervention claims are needed).

**Decorates** — the vocabulary is doing rhetorical work instead of analytical work:
- "Entropy" or "information content" is asserted with no distribution, alphabet, or estimator named. If you cannot write down p(x) and X, you have an analogy, not a measurement — say so explicitly rather than borrowing Shannon's authority.
- A result already reached by simpler means gets relabeled ("we picked the shorter prompt" becomes "we minimized MDL") without an actual two-part code or comparison — this adds jargon, not falsifiable content.
- Channel capacity, entropy, or IB is invoked as a one-line justification for a business or design decision with no channel model, noise process, or β sweep behind it.
- Rule of thumb: if the number would not change if you used a different but equally defensible estimator, it was never really an information-theoretic claim.

### MI Estimation Is the Load-Bearing Risk — Treat the Estimator as Part of the Result

Every MI number in production is `estimator(data, hyperparameters)`, not `I(X;Y)`. The single most common way this skill gets misused is quoting an MI value as if it were estimator-free. Before trusting one:
- State which estimator produced it (plug-in/discrete, KSG k-NN, MINE/NWJ, InfoNCE, f-DIME) — each has a different bias/variance profile and, for InfoNCE-family estimators, a hard upper bound of log(K) that silently caps the reported value regardless of true MI.
- Report a confidence interval or a permutation-null baseline, not a point estimate — the Abdelaleem-Martini-Nemenman protocol (arXiv:2506.00330) is the current (2026) reference for when a neural MI estimate can be trusted at all: mainly when the true dependence lives in a low-dimensional latent subspace and N is large relative to that subspace's complexity, not the ambient dimension.
- Treat any MI-driven go/no-go decision (drop this feature, prune this KV cache entry, gate this token) as provisional until the estimator has been sanity-checked on a shuffled-label or synthetic-independence baseline that should read ≈0.
- A high-dimensional MI estimate that looks "too clean" (smooth curve, no variance across seeds) is a warning sign, not a reassurance — bias in finite-sample estimators is directional (usually inflates dependence), so noise-free-looking output often means the estimator is confidently wrong rather than precisely right.

### Entropy Intuitions for Logging, Observability, and Feature Design

- A log field with H(field) ≈ 0 under normal operation (it almost always takes the same value) is not carrying information about normal operation — its entire value is in the rare cases where it deviates. Prioritize instrumenting fields with high *conditional* entropy given an incident (status codes, error classes, latency buckets) over fields that are merely present ("function entered" trace lines contribute ceremony, not bits).
- Cardinality blowups in metrics backends are usually an entropy/aggregation mismatch, not a tooling bug: a near-maximum-entropy field (user ID, request ID, raw timestamp) is being used as a group-by dimension meant for low-entropy categorical fields. Recognizing this as "someone is aggregating on a high-H(X) field" reframes a recurring on-call complaint as a design fix (bucket or hash the field) rather than a scaling problem to throw hardware at.
- In feature design, high entropy is necessary but nowhere near sufficient for value: a raw unique ID has maximum H(X) = log(N) and typically MI(X; target) ≈ 0 absent leakage. Always evaluate MI(feature; target), not H(feature) alone — a feature engineer who reports "this field has high entropy" without also reporting its MI with the label has described the feature's cost, not its worth.

### Channel-Capacity Thinking for Org and Team Communication (Explicit Analogy, Not a Measurement)

This is a structural metaphor for reasoning about communication design, not a literal application of the noisy-channel coding theorem — there is no rigorously defined p(x,y) for a Slack channel, and computing a fake numeric "capacity" for a team is exactly the decorative misuse this section warns against above. Used as a checklist, the structure still transfers usefully:
- A communication chain's effective throughput is bounded by its noisiest, lowest-bandwidth hop (the one skim-read doc, the meeting half the team missed) — matching capacity-as-a-bound-set-by-the-worst-conditioned-link, not a sum of nominal channel widths.
- Redundancy (the same decision restated in a doc, a Slack post, and a meeting) is not waste; it is the same design tradeoff error-correcting codes make — accepting a lower effective rate in exchange for surviving dropped attention, partial reads, and turnover.
- Compressing a message below what the receiver's shared context can decode does not degrade understanding proportionally — it produces a cliff, the same shape as attempting a rate above capacity: below some density threshold a terse Slack message or cryptic PR title is not "a bit less clear," it is misread entirely.
- Use this framing to generate questions ("what's the noisiest hop in this rollout communication, is there redundancy built in, is this message denser than the reader's available context can decode right now") — not to produce a number. If a number is demanded, that is the signal to say the analogy has been pushed past where it is honest.

---

## Navigation

- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Per-primitive playbooks: [`assets/templates/information-theory/README.md`](assets/templates/information-theory/README.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

_(No cross-links at this time. Consumer skills — ai-prompt-engineering, ai-context-layer, dev-context-engineering, data-analytics-engineering, marketing-content-strategy, qa-observability — will receive applied-recipe files in a later wave.)_

---

## Fact-Checking

- All formulas and theorems are sourced to Cover & Thomas (2006) 2nd ed. and MacKay (2003) as primary references; verify equation numbers and chapter numbers before using in citations — do not assume a plausible-sounding chapter attribution is correct. A 2026-07-11 audit found and corrected two real instances of this failure mode in this skill's own files: `primitives-overview.md` had misattributed MacKay Ch.28 ("Model Comparison and Occam's Razor") to information bottleneck when it actually grounds MDL (#7), and `09-fano-inequality.md` cited MacKay Ch.8 for Fano's inequality when MacKay's book never derives Fano's inequality at all. Treat every textbook chapter citation in this skill (and any you add) as needing independent verification, not just author/year/title.
- Numeric results (compression ratios, capacity values) are task- and channel-specific; do not transfer benchmarks across domains without re-deriving.
- Semantic entropy (Farquhar et al., *Nature* 630:625–630, 2024) is peer-reviewed and reproducible, but its scope is narrower than "hallucination detection" implies: it flags *confabulations* — answers that vary arbitrarily across samples — and is blind to errors the model states consistently. Do not present it as a general factuality check.
- The RLVR entropy law R = −a·e^H + b (Cui et al., arXiv:2505.22617) is an empirical fit across the model families tested, not a theorem. The qualitative claim (performance is traded from entropy; collapse caps gains) replicates widely; the fitted constants a and b do not transfer across setups — refit rather than reusing published values.
- The information bottleneck claims (IB = DNN compression) remain contested as of August 2026; see Saxe et al. (2018) rebuttal before asserting IB explains deep learning generalization, and treat the 2025/2026 reconciliation attempts (NIBT, CIBR, GIB) as partial and estimator-dependent, not a settled resolution — GIB in particular is an unreviewed preprint.
- If web access is unavailable, mark runtime-specific MI estimation results as unverified.
- Source links and verified dates in each per-primitive file are the canonical evidence tier.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
