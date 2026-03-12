# Retrieval Pipeline Template

Defines the full retrieval → rerank → context assembly pipeline.

---

## 1. Pipeline Overview

query → preprocess → embed → search(K) → rerank(optional) → select_top_N → pack_context

---

## 2. Query Preprocessing

- Normalize whitespace  
- Strip HTML/Markdown  
- (Optional) query rewriting  

---

## 3. Retrieval Step

retrieval:
top_k: 20
embedding_model: "<model_name>"
index: "<index_type>"

---

## 4. Optional Reranking

reranking:
enabled: true
model: "<cross_encoder_or_llm>"
top_k: 50

---

## 5. Context Selection

context:
max_chunks: 5
ordering: "by_score"

---

## 6. Output Schema

{
"query": "<query>",
"results": [
{
"chunk_id": "<id>",
"score": <score>,
"text": "<text>",
"metadata": { ... }
}
]
}

---

## 7. Checklist

- [ ] Same embedding model for indexing & querying  
- [ ] K tuned for recall@k  
- [ ] Reranking improves precision  
