# Ranking Pipeline Guide

Operational patterns for building multi-stage ranking systems.

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
