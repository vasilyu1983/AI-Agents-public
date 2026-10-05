# Hybrid Search Configuration Template

Combine lexical and vector retrieval results for improved relevance.

---

## 1. Hybrid Mode

hybrid:
enabled: true
components:

- "bm25"
- "vector"

---

## 2. BM25 Component

bm25:
top_k: 20
k1: 1.4
b: 0.65
field_boosts:
title: 3
body: 1

---

## 3. Vector Component

vector:
top_k: 20
index_type: "hnsw"
ef_search: 128

---

## 4. Fusion Method

Weighted sum:

fusion:
method: "weighted"
alpha: 0.4
beta: 0.6

or RRF:

fusion:
method: "rrf"
k: 60

---

## 5. Validation Checklist

- [ ] Hybrid improves recall  
- [ ] Fusion tuned  
- [ ] Keyword queries preserved  
- [ ] Long-tail semantic queries improved  
