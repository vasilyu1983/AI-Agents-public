# Ranking Pipeline Guide

Operational patterns for building multi-stage ranking systems.

## Table of Contents

- [1. Standard Ranking Pipeline](#1-standard-ranking-pipeline)
- [2. Candidate Generation](#2-candidate-generation)
- [3. Filtering Stage](#3-filtering-stage)
- [4. Scoring Stage](#4-scoring-stage)
- [5. Reranking Stage](#5-reranking-stage)
- [6. Logging for Ranking Pipeline](#6-logging-for-ranking-pipeline)
- [7. Ranking Final Checklist](#7-ranking-final-checklist)

---

## 1. Standard Ranking Pipeline

1. Candidate generation (BM25, ANN, or hybrid)  
2. Filtering (metadata, type, permissions)  
3. Scoring  
4. Reranking (cross-encoder / LLM reranker)  
5. Fusion / final ordering  

---

## 2. Candidate Generation

### Guidelines

- Retrieve more than you need (K = 20–200)  
- Keep metadata for filtering  
- Ensure high recall  

---

## 3. Filtering Stage

Filter by:

- Document type  
- Language  
- Date range  
- Permission / ACLs  

---

## 4. Scoring Stage

Options:

- BM25 score  
- Cosine similarity  
- RRF  
- Weighted fusion  

---

## 5. Reranking Stage

### Recommended models

- Cross-encoder (ms-marco variants)  
- MonoT5  
- LLM reranker  

Rerank top K candidates (20–100).  
Output 5–20 best items.

### Amazon Bedrock Rerank API (AWS-managed, June 2026)

For AWS stacks using Bedrock Knowledge Bases, the **Bedrock Rerank API** provides managed reranking without a separate service call. Available models: **Cohere Rerank 3.5** and **Amazon Rerank**. Wires directly into KB retrieval; note Cohere Command R/R+ are now legacy — the active Cohere surface in Bedrock is Embed v3/v4 + Rerank 3.5.

Use when: already on Bedrock KB and want reranking in a single AWS API surface. Skip when: you need a custom or non-AWS reranker (Jina, Zerank, Voyage), or cross-cloud portability is required.

### Jina reranker-v3 — current open-weight SOTA at <1B params (grade B, preprint + HF corroboration)

**Evidence grade B** (arXiv 2509.25085, preprint; corroborated by Hugging Face community benchmarks).

`jinaai/jina-reranker-v3` (~0.6B parameters, built on Qwen3-0.6B) uses a "last-but-not-late" listwise causal architecture, applying causal attention between the query and all candidate documents in one context window (up to ~64 documents) rather than pair-by-pair scoring.

**Benchmark results:**

| Benchmark | Score |
|-----------|-------|
| BEIR nDCG@10 | 61.94 |
| MIRACL (18 languages) | 66.83 |
| CoIR (code retrieval) | 70.64 |

It reaches this BEIR score while **outperforming Qwen3-Reranker-4B at ~6× smaller size** — which is why it, not the larger Qwen3-Reranker, is the open-weight default under 1B. As of June 2026 this remains the highest published open-weight reranker score under 1B parameters.

**License caveat — verify before production:** the published weights are **CC BY-NC 4.0 (non-commercial)**. It is the default open-weight reranker for research, evaluation, and non-commercial pipelines; for commercial deployment, confirm the current license/terms (or a commercial grant) before shipping, or fall back to a permissively-licensed cross-encoder (e.g. an Apache-2.0/MIT reranker). Do not adopt it as a production default on benchmark score alone.

- **HuggingFace:** [huggingface.co/jinaai/jina-reranker-v3](https://huggingface.co/jinaai/jina-reranker-v3)
- **Paper:** arXiv 2509.25085

> Thank you to arXiv for use of its open access interoperability.

---

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
- [ ] Filtering correct  
- [ ] Logs available  
- [ ] Latency acceptable  
