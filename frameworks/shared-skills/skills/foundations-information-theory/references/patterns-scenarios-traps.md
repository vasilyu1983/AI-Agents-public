---
description: Applied patterns, scenarios, anti-patterns, and known traps for information-theory foundations.
last_verified: 2026-08-14
status: stable
---

# Information Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Information-per-token budget | Context, RAG, or summarization must fit a hard budget | Entropy -> mutual information -> redundancy penalty |
| Distribution drift diagnosis | Model outputs or event distributions shift | KL/JS -> cross-entropy decomposition -> support check |
| Compression feasibility | Need to know whether shorter representation is possible | Entropy rate -> redundancy -> code family selection |
| Noisy channel planning | Pipeline has lossy handoff or unreliable transmission | Channel model -> capacity -> finite-blocklength margin |
| Representation audit | Embedding retains too much irrelevant variation | Mutual information -> bottleneck objective -> downstream metric |
| Model selection | Larger model fits better but may overfit | MDL -> validation loss -> sensitivity to model class |
| Hallucination gating | Need to abstain when a generation is unreliable | Sample N generations -> cluster by NLI meaning equivalence -> entropy over clusters -> abstain above threshold |
| RL post-training health check | Reward plateaus during RLVR and it is unclear whether the run is done | Log policy entropy per step -> fit R vs. H -> inspect log-prob/advantage covariance on the collapsing tokens |
| Agent message budgeting | Handoffs between agents exceed a bandwidth or token budget | Define the message as the bottleneck variable -> minimize I(X;M) at fixed I(M;task) -> quantize rather than truncate |

## Scenarios

| Scenario | First Question | Correct Primitive |
|---|---|---|
| Two retrievers return similar documents | How much new information does each doc add? | Conditional entropy and redundancy |
| RLHF policy collapses under KL penalty | Which KL direction is being optimized? | KL divergence |
| Perplexity improves after tokenizer change | Is the comparison vocabulary-neutral? | Cross-entropy normalized to bits-per-byte |
| Compression ratio disappoints | Is the source correlated or non-stationary? | Entropy rate and redundancy |
| Classifier hits a ceiling | How much label uncertainty remains after features? | Fano's inequality |
| Summaries are short but lossy | What distortion is acceptable? | Rate-distortion |
| Model states a fluent falsehood | Does the answer vary across resamples, or is it stably wrong? | Semantic entropy over meaning clusters |
| RLVR reward stops improving | Has policy entropy already collapsed? | Entropy of the policy distribution |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Safer Move |
|---|---|---|
| "More text means more information" | Length measures cost, not uncertainty or relevance | Estimate novelty and query mutual information |
| "KL is distance" | KL is asymmetric and can be infinite | Use JS or state the KL direction |
| "Low cross-entropy means distributions match" | Cross-entropy includes source entropy | Decompose into entropy plus KL |
| "MI proves causality" | MI is dependence, not intervention effect | Route causal claims to causal inference |
| "The theorem says this compressor is optimal" | Theorems are asymptotic and model-dependent | Check finite-blocklength and source assumptions |
| "IB explains this deep net" | IB evidence depends on activation and estimator | Treat IB as design lens, not settled explanation |

## Known Traps

- Differential entropy can be negative and coordinate-dependent.
- MI estimates in high dimensions are often biased upward without correction.
- JS divergence is bounded, but its scale is still distribution- and log-base-dependent.
- AEP does not guarantee short-block behavior.
- MDL can reward the wrong model if the coding scheme encodes the wrong inductive bias.
- Compression of prompts can remove redundancy that was useful for robustness or instruction salience.
- Token-level entropy is lexical, not epistemic: it rises on free paraphrase and stays low on confident falsehoods. Cluster by meaning before taking entropy.
- Semantic entropy is blind to consistent errors. Any sampling-based uncertainty measure detects instability, not wrongness.
- Falling policy entropy in RL post-training is a spent exploration budget, not convergence. Treat it as a ceiling signal.
- Entropy bonuses applied uniformly trade away useful signal; collapse is concentrated in high log-prob/advantage-covariance tokens.

## Exit Checklist

- [ ] Variables and distributions are defined.
- [ ] Units are explicit: bits, nats, bits/token, bits/byte, or code length.
- [ ] Estimator and sample size are stated for empirical entropy/MI.
- [ ] KL direction and support assumptions are explicit.
- [ ] Tokenizer effects are normalized when comparing language models.
- [ ] Asymptotic theorem use is separated from implementation claim.
