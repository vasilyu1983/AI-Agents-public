# Ranking Pipeline Template

A complete architecture for a multi-stage ranking pipeline.

---

## 1. Pipeline Structure

query → candidate_generation (ACL/tenant + hard filters inside each leg) → fusion → reranking → final_output

Never add a filtering stage after fusion or reranking for ACL/tenant scope: it
must be part of each leg's index query (see ../../SKILL.md, ACL invariant).

---

## 2. Candidate Generation Config

candidate_generation:
methods:

- "bm25"
- "vector"
top_k: 200
acl_scope: "<caller scope; missing scope = deny all>"

---

## 3. Filters Applied Inside Candidate Generation

filters_in_index_query:
required_metadata:

- "language"
- "visibility"
allowed_types:
- "article"
- "faq"

---

## 4. Fusion Strategy

fusion:
method: "rrf"   # switch to a tuned convex combination once a judged set exists
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
- [ ] ACL/tenant and hard filters applied inside candidate generation, none after fusion or reranking  
- [ ] Reranker improves relevance  
- [ ] Latency acceptable
