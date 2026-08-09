# Reranking Template

Use a cross-encoder or LLM to refine retrieved candidates.

---

## 1. Reranker Config

reranker:
model: "<cross_encoder_model>"
top_k_candidates: 50
final_top_n: 5

---

## 2. Reranking Workflow

1. Input: K candidates from ANN/BM25  
2. Score each candidate with cross-encoder/LLM  
3. Sort by descending score  
4. Select top N  

---

## 3. Output Schema

{
"reranked": [
{
"chunk_id": "<id>",
"score": <score>,
"text": "<text>",
"metadata": { ... }
}
]
}

---

## 4. Reranking Checklist

- [ ] Latency acceptable  
- [ ] Improves nDCG@10  
- [ ] No regressions on keyword queries  
