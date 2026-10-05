# Hybrid Fusion Patterns (BM25 + Vector Search)

These patterns combine lexical and dense retrieval for maximum recall and relevance.

## Table of Contents

- [1. Why Use Hybrid Search](#1-why-use-hybrid-search)
- [2. Fusion Strategies](#2-fusion-strategies)
- [3. Hybrid Workflow Template](#3-hybrid-workflow-template)
- [4. Fusion Tuning Guidelines](#4-fusion-tuning-guidelines)
- [5. Hybrid Quality Checklist](#5-hybrid-quality-checklist)

---

## 1. Why Use Hybrid Search

Use hybrid retrieval when:

- Queries vary between keyword and semantic  
- Data includes structured + narrative content  
- Domain terms or abbreviations affect relevance  
- BM25 or vector alone is insufficient  

---

## 2. Fusion Strategies

This file owns the fusion decision (RRF vs convex combination, `k`, weights,
normalization) for every skill; product-search engine syntax lives in
[software-search hybrid-search-and-reranking.md](../../software-search/references/hybrid-search-and-reranking.md).

**Default rule:** use RRF until you have relevance labels; once you have a small
judged-query set, switch to a tuned convex combination of normalized scores.

### A. Reciprocal Rank Fusion (RRF) — the default without labels

score = Σ (1 / (k + rank_i))
Characteristics:

- Stable
- One parameter, `k` (RRF is rank-based and has no α; do not conflate it with
  the convex-combination weight below)
- Order-based, not score-based — needs no score normalization

**Default:** `k = 60`, from Cormack, Clarke & Büttcher (SIGIR 2009). The paper
says `k = 60` "was fixed during a pilot investigation" and was "near-optimal,
but … the choice was not critical"; its own pilot table shows k = 70 and k = 80
marginally higher. Treat 60 as a safe starting point, not an empirically best
constant. `scripts/hybrid_rrf_demo.py` uses it (`--rrf-k 60`).

**Worked example (k=60), two ranked lists fused by RRF:**

| Candidate | BM25 rank | Vector rank | RRF score | Calculation |
|---|---|---|---|---|
| Doc A | 1 | 1 | 0.0328 | 1/(60+1) + 1/(60+1) = 2/61 |
| Doc B | 2 | — (not retrieved) | 0.0161 | 1/(60+2) = 1/62 |
| Doc C | 5 | 5 | 0.0308 | 1/(60+5) + 1/(60+5) = 2/65 |

Doc C, ranked 5th by both rankers, scores *higher* than Doc B, ranked 2nd by
only one ranker (0.0308 vs 0.0161) — RRF rewards cross-ranker consensus over a
single ranker's top pick. Doc A, ranked 1st by both, still wins overall.
Lower `k` sharpens the advantage of a top rank; higher `k` flattens it toward
uniform weighting across the candidate list.

---

### B. Convex Combination of Normalized Scores — once you have labels

score = w · norm(lexical) + (1 − w) · norm(dense),  0 ≤ w ≤ 1

Normalize each leg first (min-max, or z-score): BM25 scores, cosine similarity,
recency, and popularity do not share a natural scale.

Bruch, Gai & Ingber, "An Analysis of Fusion Functions for Hybrid Retrieval"
(arXiv 2210.11934), find that:

- RRF is sensitive to its parameters;
- a tuned convex combination outperforms RRF both in-domain and out-of-domain;
- the convex combination is largely agnostic to the choice of normalization;
- it is sample-efficient: one parameter, tunable on a small training set.

Tune `w` on a held-out judged-query set (nDCG@10). Without labels there is
nothing to tune `w` against, which is why RRF stays the default until then.

### Default fusion ladder, simplest first

| Property | Unweighted RRF | Weighted RRF | Normalized linear (convex combination) |
|---|---|---|---|
| Requires score normalization | No | No | Yes (min-max, L2, or z-score) |
| Stable across query types | Yes | Yes | Fragile until calibrated |
| Parameter surface | `k` | `k` + one weight per retriever | Normalizer + one weight per retriever |
| Sensitive to BM25 score scale changes | No | No | Yes |

1. Start with unweighted RRF.
2. Add per-retriever weights when the judged set shows one leg dominates a
   query class (for example, SKU or exact-name queries where the lexical leg
   should win) and you need to stay rank-based.
3. Move to normalized linear fusion (the convex combination) once a held-out
   judged set exists to calibrate the weight.

Before coding any of these, check what the engine supports natively (RRF,
per-leg weights, normalizers, licence tier); the lookup matrix is in
[software-search hybrid-search-and-reranking.md](../../software-search/references/hybrid-search-and-reranking.md).

---

### C. Two-Stage Fusion

1. BM25 retrieves top K (ACL/tenant pre-filtered)  
2. Dense retrieves top K (ACL/tenant pre-filtered)  
3. Reranker fuses + scores  

---

## 3. Hybrid Workflow Template

1. Preprocess & embed text  
2. Run BM25 ranker with the caller's ACL/tenant filter in the query  
3. Run vector search with the same ACL/tenant filter in the query  
4. Combine lists (fusion)  
5. Rerank using cross-encoder  
6. Output top N results  

Never apply ACL or tenant scope after step 4 or 5; see the ACL invariant in
[`../SKILL.md`](../SKILL.md#core-concepts).

### Query Preprocessing Guardrail

Stop-word removal can improve short keyword queries, but it can also destroy
intent in semantic search:

- preserve quoted phrases, negation, product names, legal clauses, code
  symbols, and domain terms before removing anything
- run preprocessing before both query embedding and lexical retrieval only when
  evals show improvement
- log the raw query, cleaned query, and preprocessing version for search
  debugging
- keep a no-preprocessing fallback for low-confidence transformations

---

## 4. Fusion Tuning Guidelines

- Tune `w` (convex combination) or `k` (RRF) using nDCG@10 — they are separate parameters for separate fusion methods
- Test RRF for stability across query types  
- Use BM25 to cover keyword-heavy queries  
- Use vectors to cover paraphrases and synonyms  

---

## 5. Hybrid Quality Checklist

- [ ] Both rankers tuned  
- [ ] Fusion method selected & validated  
- [ ] Recall@k improves vs baseline  
- [ ] No quality loss on keyword queries  
