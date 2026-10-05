# Reranker Configuration Template

Config for applying cross-encoder or LLM reranking to candidate documents.

---

## 1. Reranker Settings

reranker:
model: "<model_id>"
top_k_candidates: 50
final_top_n: 10
batch_size: 8

---

## 2. Scoring Logic

Pairs each query with each candidate document:

score = reranker.predict(query, doc_text)

Then sorts descending by score.

---

## 3. Output Schema

{
"reranked": [
{
"doc_id": "<id>",
"score": <score>
}
]
}

---

## 4. Checklist

- [ ] Reranker latency measured  
- [ ] Improves nDCG@10  
- [ ] Scores stable across evaluation set  
