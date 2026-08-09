# Hybrid Search Template (BM25 + Vector Search)

A unified configuration for combining lexical and semantic retrieval.

---

## 1. Hybrid Mode

hybrid:
enabled: true
methods:

- bm25
- vector

---

## 2. BM25 Stage

bm25:
top_k: 20
field_boosts:
title: 3
body: 1

---

## 3. Vector Stage

vector:
top_k: 20
index_type: "hnsw"
ef_search: 128

---

## 4. Fusion

fusion:
type: "weighted_sum"
alpha: 0.4
beta: 0.6

or use:

fusion:
type: "rrf"
k: 60

---

## 5. Checklist

- [ ] BM25 tuned  
- [ ] Vector search tuned  
- [ ] Fusion validated  
- [ ] Recall@k increased vs single method
