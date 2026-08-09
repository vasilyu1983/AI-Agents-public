# RAG Evaluation Template

Use this template to separate retrieval quality from answer quality.

---

## 1. Retrieval Mode Under Test

- Baseline:
- Variant:
- Authority source: docs / tools / SQL / graph / hybrid
- Corpus slice: text / code / PDF / table / multilingual / high-stakes

## 2. Dataset

- Query count:
- Query types:
- Unanswerable cases included: yes / no
- Expected evidence IDs recorded: yes / no

## 3. Retrieval Metrics

- Recall@k
- MRR
- nDCG
- Empty-result rate
- P50 / P95 latency

## 4. Answer Metrics

- Correctness
- Groundedness / faithfulness
- Citation validity
- Refusal correctness
- Cost per request

## 5. Slices To Compare

- Baseline hybrid vs variant
- With vs without reranking
- With vs without query rewriting
- Text-only vs multimodal
- Static corpus vs fresh data path

## 6. Output Record

```json
{
  "query": "",
  "query_type": "",
  "expected_evidence_ids": [],
  "retrieved_evidence_ids": [],
  "answer": "",
  "citations": [],
  "retrieval_metrics": {
    "recall_at_k": 0.0,
    "mrr": 0.0,
    "ndcg": 0.0
  },
  "answer_metrics": {
    "grounded": true,
    "citation_valid": true,
    "correct": true,
    "refusal_correct": null
  }
}
```

## 7. Gate

- [ ] Retrieval metrics non-regressing
- [ ] Citation validity checked
- [ ] Unsupported-answer rate acceptable
- [ ] Operational cost acceptable
