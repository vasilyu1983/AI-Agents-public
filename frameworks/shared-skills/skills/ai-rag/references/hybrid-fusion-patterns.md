# Hybrid Fusion Patterns (BM25 + Vector Search)

These patterns combine lexical and dense retrieval for maximum recall and relevance.

---

## 1. Why Use Hybrid Search

Use hybrid retrieval when:

- Queries vary between keyword and semantic  
- Data includes structured + narrative content  
- Domain terms or abbreviations affect relevance  
- BM25 or vector alone is insufficient  

---

## 2. Fusion Strategies

### A. Weighted Sum Fusion

score = α *bm25 + β* similarity
Typical weights:

- α = 0.3–0.6  
- β = 0.4–0.7  

---

### B. Reciprocal Rank Fusion (RRF)

score = Σ (1 / (k + rank_i))
Characteristics:

- Stable  
- Easy to tune  
- Order-based, not score-based  

---

### C. Two-Stage Fusion

1. BM25 retrieves top K  
2. Dense retrieves top K  
3. Reranker fuses + scores  

---

## 3. Hybrid Workflow Template

1. Preprocess & embed text  
2. Run BM25 ranker  
3. Run vector search  
4. Combine lists  
5. Rerank using cross-encoder  
6. Output top N results  

---

## 4. Fusion Tuning Guidelines

- Tune α/β using nDCG@10  
- Test RRF for stability across query types  
- Use BM25 to cover keyword-heavy queries  
- Use vectors to cover paraphrases and synonyms  

---

## 5. Hybrid Quality Checklist

- [ ] Both rankers tuned  
- [ ] Fusion method selected & validated  
- [ ] Recall@k improves vs baseline  
- [ ] No quality loss on keyword queries  
