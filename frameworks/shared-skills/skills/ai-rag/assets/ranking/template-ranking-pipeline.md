# Ranking Pipeline Template

A complete architecture for a multi-stage ranking pipeline.

---

## 1. Pipeline Structure

query → candidate_generation → filtering → scoring → reranking → final_output

---

## 2. Candidate Generation Config

candidate_generation:
methods:

- "bm25"
- "vector"
top_k: 200

---

## 3. Filtering Rules

filtering:
required_metadata:

- "language"
- "visibility"
allowed_types:
- "article"
- "faq"

---

## 4. Scoring Strategy

scoring:
method: "rrf"
k: 60

---

## 5. Reranking Stage

reranking:
enabled: true
model: "<cross_encoder_or_llm>"
top_k_candidates: 50
final_top_n: 10

---

## 6. Output Format

{
"results": [
{
"doc_id": "<id>",
"score": <score>,
"snippet": "<text>"
}
]
}

---

## 7. Ranking Checklist

- [ ] High recall from candidate generation  
- [ ] Filtering correct  
- [ ] Reranker improves relevance  
- [ ] Latency acceptable
