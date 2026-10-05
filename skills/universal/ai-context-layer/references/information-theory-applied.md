# Information theory applied to context design

Load [information theory](../../foundations-information-theory/SKILL.md) only when a defined probability model, compression experiment, or distribution comparison helps resolve a concrete context failure. Skip formal information quantities for routine retrieval, prompt edits, or small context assembly; use relevance, provenance, and task tests directly.

## Context budget and compression

A token limit is a resource constraint. Token-frequency entropy measures a chosen symbol distribution; it does not measure novel semantic signal or answer usefulness. Embedding variance and answer-quality loss are not compatible inputs to the Gaussian squared-error rate-distortion formula. Do not convert these quantities into a guaranteed token budget.

Compare full context, selected excerpts, and summaries at several token budgets on held-out representative tasks. Record source coverage, correctness, omissions, latency, and tokens using the actual target tokenizer. Protect mandatory instructions, authoritative facts, citations, and unresolved constraints before pruning. Select a measured quality/cost tradeoff rather than a universal score cutoff. Keep uncertainty and worst-case omissions visible.

**Return artifact:** budget table, mandatory evidence list, per-task losses, chosen compression setting, and recovery path to original sources. The [rate-distortion template](../../foundations-information-theory/assets/templates/information-theory/06-rate-distortion.md) is useful only with a defined source distribution and compatible distortion; it does not supply a semantic budget guarantee.

## Retrieval relevance and redundancy

For a fixed question, relevance concerns the answer variable conditional on that question, not entropy of the query text. Formal information gain is I(A; D | Q) under a specified joint model. A reranker score, cosine similarity, attention weight, or log-likelihood on one answer is not an MI estimate in bits. MINE requires an explicit sampling model and estimator validation; it is unnecessary for ordinary retrieval.

Use a calibrated relevance score and separately named similarity penalty for MMR-style selection:

```
selection_score = relevance(query, candidate) - weight * max_similarity(candidate, selected)
```

Tune weight on held-out answer quality and required-fact coverage; label it a heuristic. Pairwise similarity does not capture all complementary evidence. Never define NMI as cosine squared times token entropy. Deduplicating authoritative passages must preserve differing dates, qualifiers, and contradictions.

**Return artifact:** selected source IDs, relevance and duplicate flags, token count, uncovered requirements, and held-out comparison against the original retrieval baseline.

## Summarization and information bottleneck

The [information-bottleneck template](../../foundations-information-theory/assets/templates/information-theory/08-information-bottleneck.md) requires defined C (context), T (representation), and Y (target variable). Summary length is not I(C;T); answer F1 is not I(T;Y). Use an empirical tokens-versus-task-quality curve, not invented bit values or a claimed phase transition. Compare paired tasks and preserve facts needed by likely follow-ups. A task-specific quality cliff does not establish a theoretical IB boundary.

## Distribution drift and coverage

Use the same fixed topic bins, support, log base, and sampling window for both distributions. KL can be infinite when reference support is zero; disclose smoothing and its sensitivity. Base-2 JSD lies in [0,1] bits; natural-log JSD lies in [0,ln(2)] nats. Choose alert thresholds from observed false alerts and confirmed failures, not universal constants. A topic shift may reflect a legitimate user instruction; it is not proof of poisoning or authorization to discard history.

Corpus topic entropy describes concentration, not query answerability. Equal entropy can hide entirely different topics. Typical-set cardinality is not a count of documents required by a retrieval corpus. Compare query-weighted required-fact coverage and unanswered tasks per topic; ingest verified missing evidence rather than maximizing corpus entropy.

**Return artifact:** distributions and units, support/smoothing policy, drift diagnostic, missing facts, and validated refresh action.

## Cache decisions

Separate semantic document caches from KV caches: KV reuse depends on exact prefix/runtime semantics and cannot be governed by document similarity alone. For document caches, compare LRU/LFU with a query-weighted relevance heuristic. Protect unique required evidence, freshness, access boundaries, and invalidation rules.

A possible retention heuristic is relevance minus redundancy; evict the lowest retention score. Adding redundancy to a score that is minimized would incorrectly protect duplicates. Normalize query counts by actual observed count, handle an empty window, and use zero redundancy for a singleton cache. Score scales and weights must be calibrated. Do not call weighted cosine predicted MI or promise optimal eviction.

**Return artifact:** policy definition, protected entries, hit/miss and task-quality comparison, freshness violations, and rollback trigger.

## Finite classification bounds

[Fano's inequality](../../foundations-information-theory/assets/templates/information-theory/09-fano-inequality.md) applies to a specified finite label variable and population joint distribution. With M >= 2 labels and entropy in bits, a loose bound is max(0,(H(A|T)-1)/log2(M)). Document identity classification is not automatically answer correctness or retrieval recall. Without a defensible conditional entropy estimate and uncertainty, omit the numeric bound. A weak bound does not identify corpus replacement as the remedy.

**Return artifact when applicable:** label space, estimator and uncertainty, bound with assumptions, and empirical classification errors. Otherwise return measured retrieval/answer omissions.

## Composition and sources

Start with required evidence and held-out tasks, then test retrieval selection, compression, drift, and caching only where the diagnosed failure justifies them. Keep the applied owner responsible for context assembly. Use the foundation's [discrete information contract](../../foundations-information-theory/references/practical-contract.md) for executable finite-distribution checks; theoretical assumptions remain distinct from measured application performance.

Primary definitions and source links are maintained in [foundations-information-theory](../../foundations-information-theory/SKILL.md). This pack supplies application contracts rather than additional claimed research effects.
