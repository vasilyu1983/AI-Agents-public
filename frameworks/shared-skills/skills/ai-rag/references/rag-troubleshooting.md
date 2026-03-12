# RAG Troubleshooting Guide

A structured triage tool for diagnosing retrieval, relevance, hallucination, and context issues.

---

## 1. Symptom → Cause → Fix Matrix

### 1.1 Irrelevant Results

**Causes**

- Poor chunking  
- Weak embedding model  
- Low K  
- Bad index parameters  

**Fixes**

- Increase chunk size or overlap  
- Switch to stronger embeddings  
- Tune ef_search / nprobe  
- Use hybrid retrieval  
- Add reranking  

---

### 1.2 Missing Essential Information

**Causes**

- K too small  
- Metadata filters too strict  
- Incorrect query formulation  

**Fixes**

- Increase K  
- Loosen filters  
- Add query rewriting  

---

### 1.3 Hallucinations

**Causes**

- Context not strong enough  
- Prompt allows speculation  
- Chunks irrelevant  

**Fixes**

- Add grounding constraints  
- Enforce citation requirement  
- Improve chunk quality  

---

### 1.4 Slow Retrieval

**Causes**

- Large index without tuning  
- High-dimensional embeddings  
- Disk-based index not cached  

**Fixes**

- Reduce embedding size  
- Use HNSW  
- Optimize ANN parameters  
- Cache vectors in RAM  

---

### 1.5 Repeated Content or Duplicates

**Causes**

- Duplicate documents  
- Chunk explosion  
- Overlap too high  

**Fixes**

- Deduplicate source documents  
- Reduce overlap  
- Add chunk hashing  

---

## 2. Debugging Workflow

1. Inspect retrieved chunks manually  
2. Log embeddings & similarity scores  
3. Test with simpler queries  
4. Compare BM25 vs vector vs hybrid  
5. Evaluate reranker performance  

---

## 3. Logging Requirements

Log:

- Query text  
- Retrieval K  
- Index version  
- Chunk IDs returned  
- Similarity scores  
- Reranker scores  

---

## 4. Troubleshooting Checklist

- [ ] Retrieval validated  
- [ ] Chunking validated  
- [ ] Grounding constraints respected  
- [ ] Hallucinations mitigated  
- [ ] Reranker improves precision  
