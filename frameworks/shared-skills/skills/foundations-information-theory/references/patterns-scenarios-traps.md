---
description: Applied patterns, scenarios, anti-patterns, and known traps for information-theory foundations.
last_verified: 2026-05-02
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

## Scenarios

| Scenario | First Question | Correct Primitive |
|---|---|---|
| Two retrievers return similar documents | How much new information does each doc add? | Conditional entropy and redundancy |
| RLHF policy collapses under KL penalty | Which KL direction is being optimized? | KL divergence |
| Perplexity improves after tokenizer change | Is the comparison vocabulary-neutral? | Cross-entropy normalized to bits-per-byte |
| Compression ratio disappoints | Is the source correlated or non-stationary? | Entropy rate and redundancy |
| Classifier hits a ceiling | How much label uncertainty remains after features? | Fano's inequality |
| Summaries are short but lossy | What distortion is acceptable? | Rate-distortion |

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

## Exit Checklist

- [ ] Variables and distributions are defined.
- [ ] Units are explicit: bits, nats, bits/token, bits/byte, or code length.
- [ ] Estimator and sample size are stated for empirical entropy/MI.
- [ ] KL direction and support assumptions are explicit.
- [ ] Tokenizer effects are normalized when comparing language models.
- [ ] Asymptotic theorem use is separated from implementation claim.
