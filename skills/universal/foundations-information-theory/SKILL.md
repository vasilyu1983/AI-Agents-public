---
name: foundations-information-theory
description: Measures entropy, mutual information, KL/JS, bits-per-byte. Use when picking KL direction, comparing cross-tokenizer perplexity, trusting MI estimates, or semantic-entropy gating.
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-08-14
---

# Information Theory Foundations

## When to Apply

**Apply when a decision depends on a defined distribution:**
- Distribution shift or model-update comparison (KL direction, JS with a stated log base)
- Feature relevance or leakage screening by mutual information, with an estimator and a null baseline
- Model comparison across tokenizers (bits-per-byte or bits-per-character, not perplexity)
- Hallucination or abstention gating via semantic entropy over meaning clusters
- RL post-training health: policy-entropy collapse in RLVR
- Context, prompt, KV-cache or agent-handoff compression framed as a measured rate/task-loss tradeoff
- Error floors (Fano), coding limits (entropy, capacity, rate-distortion), model selection (MDL)
- LLM-serving questions: speculative-decoding acceptance, quantization or KV-cache compression claims, log loss vs Brier for calibration ([references/llm-practice.md](references/llm-practice.md))

**Skip or hand off when:**
- The question is causal, not dependence: foundations-causal-inference
- Linear or monotonic dependence is enough: Pearson or rank correlation
- The task is significance, error bars or calibration methodology: foundations-statistical-inference
- The task is feedback stability: foundations-control-theory
- Team or human communication design: foundations-team-theory or foundations-grounding-communication (channel capacity is not a measurement there)
- No random variable, sampling frame or estimator can be written down: call the score a proxy and evaluate it on task outcomes

## Quick Reference

| # | Primitive | Core formula | Use when | Playbook |
|---|---|---|---|---|
| 1 | Shannon entropy | H(X) = −Σ p log p | Uncertainty of a defined PMF; semantic entropy over meaning clusters; RLVR policy entropy | [01](assets/templates/information-theory/01-shannon-entropy.md) |
| 2 | Mutual information | I(X;Y) = H(X) − H(X\|Y) | Non-linear dependence, relevance, leakage | [02](assets/templates/information-theory/02-mutual-information.md) |
| 3 | KL / JS divergence | D_KL(P‖Q) = Σ p log(p/q) | Directional distribution comparison; JS for symmetric | [03](assets/templates/information-theory/03-kl-divergence.md) |
| 4 | Cross-entropy | H(P,Q) = H(P) + D_KL(P‖Q) | Loss, perplexity, bits-per-byte | [04](assets/templates/information-theory/04-cross-entropy.md) |
| 5 | Channel capacity | C = max_{p(x)} I(X;Y) | Noisy-channel throughput ceilings with a named transition law | [05](assets/templates/information-theory/05-channel-capacity.md) |
| 6 | Rate-distortion | R(D) = min I(X;X̂) s.t. E d ≤ D | Lossy compression under a named distortion | [06](assets/templates/information-theory/06-rate-distortion.md) |
| 7 | MDL | L(M) + L(D\|M) | Model selection with an explicit code | [07](assets/templates/information-theory/07-mdl-principle.md) |
| 8 | Information bottleneck | min I(X;T) − β I(T;Y) | Representation compression with a defined target | [08](assets/templates/information-theory/08-information-bottleneck.md) |
| 9 | Fano's inequality | H(X\|Y) ≤ H_b(P_e) + P_e log(\|X\|−1) | Error floor from residual uncertainty | [09](assets/templates/information-theory/09-fano-inequality.md) |
| 10 | Typical sets / AEP | −(1/n) log p(Xⁿ) → H | Source-coding limits, block-length reasoning | [10](assets/templates/information-theory/10-typical-sets-aep.md) |
| 11 | Redundancy & compression | R = log M − H(X); entropy rate | Code-family choice, NCD, redundancy audits | [11](assets/templates/information-theory/11-redundancy-compression.md) |

Theorem assumptions: [references/formal-theory-map.md](references/formal-theory-map.md). Domain anti-patterns: [references/primitives-overview.md](references/primitives-overview.md).

## Measurement Contract (apply before any number)

Write the random variables, sampling frame, support, log base (bits or nats), estimator, sample size and a null or permutation baseline. Token variety, label cardinality, embedding spread and model confidence are not Shannon entropy or MI unless probabilities and outcomes are defined. Label such scores as proxies and validate them against the decision they feed. Full contract and known-answer controls: [references/practical-contract.md](references/practical-contract.md); runnable: `python3 scripts/discrete_information.py`. The RLVR law R = −a·e^H + b is an empirical fit; a and b do not transfer across setups. Numeric compression or bandwidth results are setup-specific; do not transfer across domains without re-measuring.

## Anti-Patterns

| Anti-pattern | Diagnosis | Fix |
|---|---|---|
| KL used as a symmetric distance | D_KL(P‖Q) ≠ D_KL(Q‖P); infinite when Q = 0 where P > 0 | Name numerator and denominator. D_KL(P‖Q) is large where Q puts little mass where P has mass; outcomes with P = 0 contribute nothing. Use JS (max 1 bit = ln 2 nats) or its square root for symmetry (#3) |
| MI reported as estimator-free | Plug-in MI is biased upward; neural estimators fail outside low-dimensional latent dependence; InfoNCE is capped at log K | State the estimator, report a CI and a shuffled-label baseline that should read ≈ 0 (#2) |
| Plug-in entropy trusted on sparse counts | Plug-in entropy is biased **downward**; Miller–Madow **adds** (k−1)/(2N) nats and fails when support is sparse or unknown | Report support and uncertainty; use an estimator justified for the regime (#1) |
| Cross-entropy read as distribution similarity | H(P,Q) = H(P) + KL ≥ H(P); comparisons across different P mix source uncertainty and model mismatch | Decompose; compare distributions with KL/JS/Wasserstein (#4) |
| Perplexity compared across tokenizers | Perplexity is per token; token counts differ | Convert total NLL to bits-per-byte or per character on the same bytes (#4) |
| Differential entropy treated like discrete entropy | Can be negative; not invariant under reparametrization | Use MI (transform-invariant) or state units and transform (#1) |
| Token entropy used as a hallucination signal | Measures lexical freedom, not epistemic uncertainty | Entropy over NLI meaning clusters of N samples (Farquhar et al., *Nature* 630, 2024); probes for single-pass (Kossen et al., arXiv:2406.15927). Detects confabulation only; blind to stable errors (#1) |
| Falling RLVR policy entropy read as convergence | Empirical fit R = −a·e^H + b: reward is bought with entropy; most of the drop happens early (Cui et al., arXiv:2505.22617) | Log policy entropy; refit a, b per setup; restrict updates on high log-prob/advantage-covariance tokens (Clip-Cov, KL-Cov) rather than a blanket bonus. Training detail: ai-post-training (#1) |
| "LLMs are optimal compressors" | Average-case prediction ≠ shortest program | BPC tracks capability: 31 models, 12 benchmarks, ρ = −0.93 overall, −0.935 to −0.953 per domain (Huang et al., COLM 2024, arXiv:2404.09937). Frontier models do poorly on the KoLMogorov Test (ICLR 2025). Use BPC to rank; do not claim Kolmogorov optimality (#4, #11) |
| High entropy or length read as "more useful" | Random text has high entropy and no value; a predictable negation can be essential | Preserve constraints first; rank by task-validated relevance, not H(segment) (#1, #2) |
| Handoff budget set by token count | Optimizes length, not task-relevant bits | Frame as a bottleneck on I(M;task). One robotics MARL study (Farooq & Iqbal, ICRA 2026, arXiv:2602.02035) reports “71.4% bandwidth reduction” (800 vs 2,800 bits/episode; §V-A) in one synthetic domain; transfer to LLM summaries or KV caches is an untested hypothesis (#6, #8) |
| Quantization or KV compression justified by R(D) or perplexity alone | R(D) needs a named source and distortion; perplexity misses answer flips | Measure task loss vs bits per element and find the knee; see [references/llm-practice.md](references/llm-practice.md) (#6) |
| IB presented as settled DNN theory | Compression phases depend on activation and estimator (Saxe et al., 2018) | Use IB as a design lens; sweep β; treat newer reformulations as contested (#8) |
| Asymptotic theorem quoted as a finite guarantee | AEP, capacity and R(D) are limits | Check finite-blocklength results and the source model (#5, #10) |

## Composition Recipes

### Context-Window Budget

**Use only when** a distribution-based compression question is defined, or to interpret a measured quality/budget tradeoff. A single segment has no Shannon entropy or MI without a random-variable model.

- **Inputs:** held-out tasks, candidate segments, the real token budget, a task-loss measure, and the instructions, permissions, negations and constraints that must survive.
- **Rules:** Preserve essential constraints first. Benchmark relevance, diversity and surprisal proxies against task outcomes at several budgets, including an unpruned baseline. With a joint distribution, marginal information is I(task;candidate|selected), not a bit value attached to one document. Density ranking is a heuristic for indivisible budgets. MDL needs an explicit code; never compare raw token length with bits of information gain.
- **Outputs:** task-loss/budget curve, chosen context, retained constraints, proxy definitions, uncertainty. KV-cache pruning and gist compression need their own task and latency benchmarks; high surprisal alone neither keeps nor evicts a token.

### Retrieval Reranking

Exact marginal information is I(task;candidate|selected); relevance minus pairwise MI is a heuristic to validate. High conditional entropy of a candidate given the selected set indicates novelty, not redundancy. Drift and feature-inclusion thresholds must be calibrated to sampling uncertainty, baseline and decision cost; no universal 0.05-nat or 10%-of-entropy gate exists.

Hypothetical feature example: H(churn) = 0.469 bits and a validated H(churn|tickets) = 0.31 give MI = 0.159 bits. This is dependence, not causation, and alone neither approves the feature nor sets an alert.

### Prompt Variability Diagnosis

- **Inputs:** fixed prompt, sampled outputs, the sampling law q (temperature, top-p), the evaluated law p, sample size, units, and a grounded finite label Y with evidence E if a bound is wanted.
- **Rules:** Mean −log p(output|prompt) over samples from q estimates cross-entropy of q relative to p; it equals sampling entropy only when q = p. Fano: for m = |Y| > 1, P_e ≥ max(0, (H(Y|E) − 1)/log₂ m) in bits; without that joint distribution, report "bound unavailable". Output variability alone cannot separate prompt ambiguity, decoding and model effects; use controlled edits and sampler changes on held-out labels.

## Workflow

1. Write the measurement contract (variables, frame, base, estimator, baseline); if you cannot, label the score a proxy.
2. Pick the primitive from the Quick Reference and open its playbook for traps and a known answer.
3. Check the Anti-Patterns table and, for LLM evaluation or serving, `references/llm-practice.md`.
4. Report value, units, uncertainty and whether the claim is a theorem, an empirical result or a heuristic.

## Practitioner Judgment

**MI is estimator(data, hyperparameters).** Name the estimator (plug-in, KSG, MINE/NWJ, InfoNCE, f-DIME), report a CI or permutation null, and treat any MI-driven go/no-go (drop a feature, evict a KV entry) as provisional until a shuffled or synthetic-independence check reads ≈ 0. A suspiciously smooth high-dimensional MI curve usually means confident bias. Neural-estimator protocol: Abdelaleem, Martini & Nemenman (arXiv:2506.00330, preprint).

**Logging and features.** Select fields by held-out diagnostic or predictive value, not entropy alone. Preserve identifiers needed to correlate traces, but keep unique IDs out of aggregate metric labels; hashing does not reduce cardinality unless mapped into bounded buckets. In an empirical table with one observed label per unique ID, H(target|ID) = 0 and plug-in MI(ID; target) = H(target), even without useful prediction on new IDs. Treat this as sample memorization; require a permutation baseline and held-out evidence before feature selection.


**Citing formulas.** Cover & Thomas (2006) and MacKay (2003) are the canonical references — verify chapter titles, not only the book: MacKay does not derive Fano's inequality, and his Ch. 28 grounds MDL, not IB. Semantic entropy flags confabulation (sampling-unstable answers), not stable false beliefs; validate thresholds on grounded labels.

## Navigation

- [references/practical-contract.md](references/practical-contract.md) — measurement contract, estimator guardrails, known-answer controls. Read before reporting any bits or nats.
- [references/llm-practice.md](references/llm-practice.md) — compression = prediction, BPB comparability, log loss vs Brier, speculative-decoding acceptance, when not to trust quantization or KV-cache compression claims. Read for LLM evaluation or serving questions.
- [references/primitives-overview.md](references/primitives-overview.md) — anti-patterns by domain and core sources.
- [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) — scenario-to-primitive map and exit checklist.
- [references/formal-theory-map.md](references/formal-theory-map.md) — theorem assumptions and boundaries.
- [assets/templates/information-theory/](assets/templates/information-theory/README.md) — one playbook per primitive, with traps and known answers.
- [`scripts/discrete_information.py`](scripts/discrete_information.py), [`scripts/test_discrete_information.py`](scripts/test_discrete_information.py) — finite-PMF known answers.
- [`data/sources.json`](data/sources.json) — sources.

## Related Skills

Applied adapters (domain decisions that use this foundation):
- [ai-prompt-engineering](../ai-prompt-engineering/references/information-theory-applied.md) — prompt variants, KL direction for regression checks
- [ai-context-layer](../ai-context-layer/references/information-theory-applied.md) — context assembly budgets
- dev-context-engineering — repo context selection and output compression
- marketing-content-strategy — content redundancy and topic coverage
- [qa-observability](../qa-observability/references/information-theory-applied.md) — log and metric signal design
- research-painpoint-scanner — theme drift and signal novelty

Handoffs: foundations-statistical-inference (`references/predictive-calibration.md` owns proper scoring and calibration); ai-post-training (RLVR entropy management); ai-llm-inference (speculative decoding, quantization); foundations-causal-inference (MI is not an effect).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
