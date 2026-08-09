# Search Evaluation Template

A reproducible evaluation structure for BM25, vector, or hybrid search systems.

---

## 1. Evaluation Settings

evaluation:
metrics:

- "ndcg@10"
- "recall@10"
- "precision@5"
slices:
- "query_length"
- "domain"

---

## 2. Test Steps

1. Load testset  
2. Run BM25  
3. Run vector search  
4. Run hybrid search  
5. Compute metrics  
6. Compare variants  
7. Log version  

---

## 3. Output Format

{
"query": "<query>",
"gold_docs": ["<id1>", "<id2>"],
"retrieved_docs": ["<idX>", "<idY>"],
"metrics": {
"ndcg@10": <float>,
"recall@10": <float>,
"precision@5": <float>
}
}

---

## 4. Evaluation Checklist

- [ ] Testset covers keyword + semantic queries  
- [ ] Baselines compared  
- [ ] Reranker evaluated  
- [ ] Version logged  
