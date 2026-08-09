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
| Cross-tenant hit appears | ACL applied after retrieval | Security red-team cases | Enforce tenant scope in retrieval function/index namespace |
| Quality slowly drops | Corpus drift or embedding-model drift | Quarterly golden eval and score distributions | Re-embed, dual-index, or adapter migration |
| Latency spikes with low recall | Over-filtered ANN or rerank too deep | Trace candidate counts and filter selectivity | Use iterative scans, prefilter indexes, or staged rerank |

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
