# Retrieval Debugging Runbook

Use this runbook when retrieval quality, grounding, or search relevance drops.
It separates source, retrieval, ranking, context assembly, and generation failures.

## Contents

- [Fast Triage](#fast-triage)
- [Failure Matrix](#failure-matrix)
- [Debug Sequence](#debug-sequence)
- [Rollback Rules](#rollback-rules)

## Fast Triage

```text
bad answer
  -> evidence missing?
       yes -> retrieval path
       no  -> answer/citation path
  -> exact baseline good?
       no  -> source, chunk, embedder, preprocessing
       yes -> ANN, filters, fusion, rerank
  -> retrieved evidence correct but answer wrong?
       yes -> context assembly or generation prompt
  -> only production bad?
       yes -> drift, freshness, ACL, cache, latency fallback
```

## Failure Matrix

| Symptom | Likely Cause | Check | Fix |
|---|---|---|---|
| Exact baseline misses expected evidence | Bad source selection, chunking, preprocessing, or embedder | `exact_search_baseline.py` on golden cases | Fix corpus or model before tuning ANN |
| Exact baseline passes but ANN misses | Index params, quantization, filtered ANN, stale index | Compare exact vs indexed prediction files | Raise recall budget, rebuild index, fix filter path |
| Hybrid loses exact keyword queries | Dense leg over-weighted or stop words damaged identifiers | Slice evals by `lexical_required` | Use RRF or stronger lexical leg |
| Good retrieval, bad answer | Context assembly or generation issue | Citation check and unsupported claims | Reformat bundle, add refusal/citation checks |
| Correct source, wrong version | Freshness or authority failure | Effective-time and supersession cases | Filter by `as_of`, authority, and tombstones before scoring |
| Cross-tenant hit appears | ACL filtered after fusion/rerank instead of at candidate generation | Security red-team cases, `acl_filtered_after_rerank` eval case | Move the ACL/tenant filter to candidate generation (pre-fusion, pre-rerank) — see SKILL.md ACL invariant |
| Quality slowly drops | Corpus drift or embedding-model drift | Quarterly golden eval and score distributions | Re-embed, dual-index, or adapter migration |
| Latency spikes with low recall | Over-filtered ANN or rerank too deep | Trace candidate counts and filter selectivity | Use iterative scans, prefilter indexes, or staged rerank |
| Irrelevant top results, no obvious retrieval bug | Weak embedding model, poor chunking, or missing domain vocabulary | Spot-check embeddings on known-good/known-bad pairs | Try a domain-tuned embedding model, add synonyms/query rewriting |
| Duplicate or near-duplicate results | Duplicate source docs, chunk overlap too high, or chunk explosion | Inspect chunk IDs and source doc IDs for the same query | Deduplicate source documents, reduce overlap, add chunk hashing |
| Hallucinated answer despite retrieval passing | Prompt allows speculation, or chunks are topically close but not actually supporting | Run `check_citation_support.py` | Add grounding constraints and enforce a citation requirement |

## Debug Sequence

1. Reproduce with a single query and record expected evidence ID.
2. Run exact-search baseline against the same corpus snapshot.
3. Run the production retriever with tracing enabled.
4. Compare candidate lists at each stage: lexical, vector, fusion, rerank,
   hydrate, final context bundle.
5. Check corpus version, chunker version, embedding model, and preprocessing
   version.
6. Check freshness and ACL filters before scoring.
7. Run citation-support checks on the generated answer.
8. Add the failure as a golden eval case before shipping the fix.

## Rollback Rules

- Roll back a chunker, embedder, index, or reranker change if it regresses any
  critical slice: ACL, policy effective-time, unanswerable, or citation support.
- Do not roll forward by adding prompt instructions when retrieval is missing
  evidence. Fix retrieval first.
- Do not accept a reranker improvement that improves average nDCG but harms
  exact identifier, policy, or security slices.

## Logging Requirements

Log at minimum, per query: query text, requested K, candidate sets from each
stage (lexical, vector, fusion, rerank), scores at each stage, index version,
embedding-model version, and chunk/evidence IDs returned. Without per-stage
candidate logging, the Debug Sequence above cannot isolate which stage caused
a failure.

## Final Checklist

- [ ] Retrieval validated against the exact-search baseline
- [ ] Chunking and embeddings verified against golden cases
- [ ] ACL/tenant filter confirmed at candidate generation, not after rerank
- [ ] Fusion method (RRF/weighted) tested for stability across query types
- [ ] Reranker improves precision without harming exact-identifier or security slices
- [ ] Grounding constraints respected; hallucinations mitigated
- [ ] Failure added as a golden eval case before shipping the fix

## Gotchas From Regulated Multi-Entity Corpora

- **Stale index fingerprint, silent fallback.** Editing query code can change the index fingerprint; an eval or server then falls back to a weaker in-memory path and still reports numbers. Fail loud on a fingerprint mismatch and record the retrieval path in every eval row.
- **Scope per document, not per section.** One entity's addendum (for example a gift limit) was served for another entity because scope was tagged on the document. Tag scope on the section or chunk and filter at candidate generation.
- **Abstain gate over the whole document.** Coverage computed over the whole top document makes confident-wrong answers likely on large frameworks. Compute coverage over the retrieved section, and see [abstention-recipe.md](abstention-recipe.md).
- **Temporal state.** Withhold superseded, expired and tombstoned documents at serve time, and propagate tombstones to the graph and index. Answer as-of queries with `effective_from <= t < effective_to`. Check for `superseded_by` self-pointers.
- **Own-eval inflation.** Score on an independent held-out set with hard negatives and report a confident-wrong rate; the builders' own set overstated the answer rate by a wide margin in one build (about 60% held-out vs about 90% own, one observed build).

End-to-end lifecycle checklist (admission, encoding, persistence, maintenance, retrieval, post-retrieval, materialisation): [memory-responsibilities-audit.md](../../ai-context-layer/references/memory-responsibilities-audit.md).
