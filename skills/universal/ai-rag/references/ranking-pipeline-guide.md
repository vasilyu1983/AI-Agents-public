# Ranking Pipeline Guide

Operational patterns for building multi-stage ranking systems.

## Table of Contents

- [1. Standard Ranking Pipeline](#1-standard-ranking-pipeline)
- [2. Candidate Generation](#2-candidate-generation)
- [3. Filters at Candidate Generation](#3-filters-at-candidate-generation)
- [4. Fusion Stage](#4-fusion-stage)
- [5. Reranking Stage](#5-reranking-stage)
- [6. Logging for Ranking Pipeline](#6-logging-for-ranking-pipeline)
- [7. Ranking Final Checklist](#7-ranking-final-checklist)

---

## 1. Standard Ranking Pipeline

1. Candidate generation (BM25, ANN, or hybrid legs), with the caller's ACL/tenant scope and other hard filters applied inside each leg's index query  
2. Fusion of the candidate lists (RRF or a tuned convex combination)  
3. Reranking (cross-encoder / LLM reranker) over the fused top-N  
4. Final ordering (business rules, dedup, truncation to the result size)  

Permissions are never a later stage. Filtering after fusion, after the reranker,
or after truncation sends unauthorized text through the reranker and any cache,
and it silently shrinks recall because top-k was chosen without the scope — see
the ACL invariant in [`../SKILL.md`](../SKILL.md#core-concepts).

---

## 2. Candidate Generation

### Guidelines

- Retrieve more than you need (K = 20–200)  
- Apply the ACL/tenant pre-filter in every leg's query (see §3); never over-fetch and drop unauthorized rows afterwards  
- Keep metadata for filtering and logging  
- Ensure high recall within the caller's scope  

---

## 3. Filters at Candidate Generation

Push these predicates into the index query of every retrieval leg, before any
fusion, reranking, caching, or truncation:

- Permission / ACLs and tenant scope (mandatory, fail closed when the scope is missing)  
- Document type  
- Language  
- Date range  

If the engine cannot filter a leg natively, that leg is not safe for scoped data
until it can; do not compensate with a post-retrieval filter for ACL or tenant
predicates.

---

## 4. Fusion Stage

Merge the per-leg candidate lists into one ranked list. Options:

- RRF (rank-based; the default until you have relevance labels)  
- Convex combination of normalized scores (once a judged set exists to tune the weight)  

Method choice, `k`, weights, and normalization are owned by
[hybrid-fusion-patterns.md](hybrid-fusion-patterns.md).

---

## 5. Reranking Stage

### Reranker classes

- Cross-encoder (ms-marco variants and domain fine-tunes)  
- MonoT5  
- Listwise LLM reranker (scores many candidates in one context window instead of pair by pair)  
- Reasoning reranker (test-time compute) — see below  

Rerank top K candidates (20–100).  
Output 5–20 best items.

### Choosing a reranker

Model rosters, benchmark leads, and managed-API model lists change release to
release, so this guide names none as a default. Decide on these criteria, then
check the current leaderboard (BEIR, MIRACL for multilingual, CoIR for code) and
the vendor docs at use time:

| Criterion | What to check |
|---|---|
| Measured gain on your judged set | Rerank the same fused candidates with and without the model; keep it only if nDCG/precision improves at your cut-off |
| Latency at your N | p95 for reranking N candidates on your hardware or the vendor API, inside the latency budget |
| License | Many open-weight rerankers ship non-commercial weights (for example CC BY-NC); confirm commercial terms before shipping |
| Deployment surface | Managed API inside your cloud (for example a cloud provider's rerank API next to its knowledge-base retrieval) vs self-hosted; data residency and whether scoped text may leave your boundary |
| Domain and language fit | Leaderboard scores on general benchmarks do not transfer to your domain; verify on your own queries |
| Vendor stability | Reranker vendors consolidate; confirm the model's support roadmap before building reindex-heavy dependencies |

Listwise causal rerankers are one architecture to test against a cross-encoder
(for example Jina reranker-v3, arXiv 2509.25085, which attends across the query
and all candidates in one window); check the current weights' license before
production use.

> Thank you to arXiv for use of its open access interoperability.

---

### Reasoning rerankers — when a score alone is not enough

Rank1 (Weller et al., arXiv 2502.18418) distils reasoning-model traces into a reranker that "thinks" before scoring, returning an explainable chain alongside the relevance judgement. Treat it as a fourth tier above cross-encoder and listwise LLM reranking: it earns its latency (an order of magnitude above a cross-encoder — measure on your hardware) only on queries where relevance depends on multi-step inference, negation, or instruction-following, and where the reasoning trace itself is a product feature (audit, citation justification). Do not put it on the hot path for lookup-style queries; gate it behind a query classifier or use it offline to label training data for a cheaper reranker.

## 6. Logging for Ranking Pipeline

Log:

- Query  
- Top-K candidates  
- Scores (bm25, vector, reranker)  
- Pipeline version  
- User segments  

---

## 7. Ranking Final Checklist

- [ ] Generator recall ≥ target  
- [ ] Reranker improves relevance  
- [ ] ACL/tenant filter applied inside candidate generation, with no post-retrieval ACL filter  
- [ ] Logs available  
- [ ] Latency acceptable  
