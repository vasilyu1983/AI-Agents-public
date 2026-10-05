---
description: Applied patterns, scenarios, anti-patterns, and known traps for information-theory foundations.
status: stable
---

# Information Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Context budget | Context, RAG, or summarization must fit a hard budget | Preserve constraints -> task-validated relevance and redundancy proxies -> task-loss/budget curve vs unpruned baseline |
| Distribution drift diagnosis | Model outputs or event distributions shift | KL/JS -> cross-entropy decomposition -> support check |
| Compression feasibility | Need to know whether shorter representation is possible | Entropy rate -> redundancy -> code family selection |
| Noisy channel planning | Pipeline has lossy handoff or unreliable transmission | Channel model -> capacity -> finite-blocklength margin |
| Representation audit | Embedding retains too much irrelevant variation | Mutual information -> bottleneck objective -> downstream metric |
| Model selection | Larger model fits better but may overfit | MDL -> validation loss -> sensitivity to model class |
| Hallucination gating | Need to abstain when a generation is unreliable | Sample N generations -> cluster by NLI meaning equivalence -> entropy over clusters -> abstain above threshold |
| RL post-training health check | Reward plateaus during RLVR and it is unclear whether the run is done | Log policy entropy per step -> fit R vs. H -> inspect log-prob/advantage covariance on the collapsing tokens |
| Agent message budgeting | Handoffs between agents exceed a bandwidth or token budget | Define the message as the bottleneck variable -> minimize I(X;M) at fixed I(M;task) -> benchmark quantized vs truncated messages on task loss (quantize-over-truncate is an untested hypothesis for LLM handoffs) |

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

## Anti-Patterns and Traps

The anti-pattern table lives in [SKILL.md](../SKILL.md#anti-patterns), and per-primitive traps live in each playbook's Traps section ([index](../assets/templates/information-theory/README.md)). This file does not repeat them. Four traps that the SKILL table does not carry:

- MI is dependence, not an intervention effect; route causal claims to causal inference ([02](../assets/templates/information-theory/02-mutual-information.md)).
- MDL can favor any model under an arbitrary code; declare the code ([07](../assets/templates/information-theory/07-mdl-principle.md)).
- KL/JS drift values depend on binning, support, sample size and log base; no universal alert level ([03](../assets/templates/information-theory/03-kl-divergence.md)).
- Removing prompt redundancy can remove robustness or instruction salience ([11](../assets/templates/information-theory/11-redundancy-compression.md)).

## Exit Checklist

- [ ] Variables and distributions are defined.
- [ ] Units are explicit: bits, nats, bits/token, bits/byte, or code length.
- [ ] Estimator and sample size are stated for empirical entropy/MI.
- [ ] KL direction and support assumptions are explicit.
- [ ] Tokenizer effects are normalized when comparing language models.
- [ ] Asymptotic theorem use is separated from implementation claim.
