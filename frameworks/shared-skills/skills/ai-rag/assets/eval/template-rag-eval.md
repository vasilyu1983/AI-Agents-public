# RAG Evaluation Template

A reproducible structure for evaluating retrieval quality and grounded generation.

---

## 1. Evaluation Tasks

- Closed-book QA  
- Grounded QA  
- Multi-hop reasoning  
- Summarization with citations  
- Fact extraction  

---

## 2. Metrics

### Retrieval Metrics

- Recall@k  
- Precision@k  
- nDCG  

### Generation Metrics

- Correctness  
- Groundedness  
- Hallucination rate  
- Citation validity  

---

## 3. Evaluation Protocol

1. Build 20–200 sample queries  
2. Define gold answers  
3. Run:  
   - BM25  
   - Vector-only  
   - Hybrid  
   - Reranked  
4. Evaluate grounded answers  
5. Score with rubric  

---

## 4. Output Template

{
"query": "<query>",
"retrieved_chunks": ["<id1>", "<id2>", ...],
"generated_answer": "<answer>",
"gold_answer": "<gold>",
"metrics": {
"recall@k": <value>,
"groundedness": <value>,
"hallucination_rate": <value>
}
}

---

## 5. Checklist

- [ ] All retrieval stages evaluated  
- [ ] Grounding validated  
- [ ] Scores stored with version  
