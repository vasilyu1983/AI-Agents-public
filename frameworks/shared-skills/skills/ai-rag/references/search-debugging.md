# Search Debugging Guide

A structured approach to diagnosing low relevance, poor recall, index issues, or slow search.

---

## 1. Symptom → Root Cause → Fix

### A. Irrelevant Results

**Causes**

- Weak embeddings  
- Poor chunking  
- Missing domain vocabulary  

**Fixes**

- Use domain embeddings  
- Add synonyms or query rewriting  
- Improve metadata quality  

---

### B. Low Recall

**Causes**

- K too small  
- Overly strict filters  
- Bad ANN parameters  

**Fixes**

- Increase K (20–100)  
- Relax filters  
- Tune ef_search or nprobe  

---

### C. High Latency

**Causes**

- Large vectors  
- Disk-backed index  
- Insufficient caching  

**Fixes**

- Use HNSW  
- Reduce embedding dim  
- Add warm cache on startup  

---

### D. Duplicate or Noisy Results

**Causes**

- Repetitive docs  
- Chunking explosion  
- Bad deduping logic  

**Fixes**

- Deduplicate source docs  
- Reduce overlap during chunking  

---

## 2. Debugging Workflow

1. Inspect top-K results manually  
2. Check metadata completeness  
3. Compare BM25-only vs vector-only  
4. RRF fusion test  
5. Reranker performance test  
6. Embedding drift check  

---

## 3. Logging Requirements

Log:

- Query text  
- Candidate sets from each stage  
- Scores  
- Index version  
- Embedding model version  

---

## 4. Debugging Checklist

- [ ] Retrieval validated  
- [ ] Embeddings verified  
- [ ] Index tuned  
- [ ] Fusion method tested  
- [ ] Reranker stable  
