# Hybrid Retrieval Template

*Purpose: Provide a structured template for implementing hybrid retrieval (semantic + keyword) with reranking, domain filtering, metadata scoring, and conflict resolution.*

---

## When to Use

Use this template when:

- Retrieval requires both semantic similarity **and** exact matching.  
- Data includes technical, legal, financial, or code-heavy content.  
- Users ask for factual, numeric, or terminology-sensitive answers.  
- You need higher precision than semantic-only retrieval.  

---

# TEMPLATE STARTS HERE

## 1. Hybrid Retrieval Overview

**Goal:**  
[Describe what the hybrid retrieval solves or enhances.]

**Sources / Indexes:**  

- [Semantic index]  
- [Keyword index]  
- [Optional rule-based index]  
- [Optional metadata index]

**Constraints:**  

- All chunks must be relevant.  
- Keyword hits have priority for factual accuracy.  
- Semantic matches fill conceptual context.  

---

## 2. Retrieval Pipeline (Hybrid)

```
query
→ optional_rewrite
→ embed
→ semantic_retrieve(top_k_semantic)
→ keyword_retrieve(top_k_keyword)
→ merge_and_dedupe
→ rerank
→ filter
→ inject
→ answer
```

---

## 3. Parameters

### Semantic Retrieval

- **top_k_semantic:** [20–50]  
- Embedding model: [model_name]  

### Keyword Retrieval

- **top_k_keyword:** [10–20]  
- Engine: [BM25 / keyword index]  

### Reranking

- Model: [cross-encoder / domain reranker]  
- Keep: top 3–7  

### Filtering

- Domain check  
- Term match  
- Conflict resolution  
- Metadata validation  

---

## 4. Merge & Deduplication

### Rule Set

- Deduplicate by chunk hash or paragraph ID.  
- Prefer keyword hits for exact terms.  
- Merge based on semantic similarity threshold (e.g., 0.8).  

### Example Pseudocode

```
results = semantic_results + keyword_results
results = dedupe(results)
results = rerank(results)
```

---

## 5. Filtering (Hybrid-Specific)

### Required Filters

- Domain alignment  
- Relevance threshold  
- Term consistency  
- Metadata validity  

### Domain Enforcement Example

```
if chunk.domain != expected_domain:
    discard
```

### Term Check Example

```
if query contains exact_term:
    ensure keyword_result contains exact_term
```

---

## 6. Evidence Injection

### Injection Format

```text
<retrieved>
[chunk_1]
[chunk_2]
[chunk_3]
</retrieved>
```

### Injection Rules

- Max tokens: 500–700  
- Keep only highly relevant chunks  
- Include metadata: source, page, section, timestamp  

---

## 7. Answer Generation Rules

- Use *only* injected evidence.  
- Cite chunk metadata.  
- Avoid mixing external world knowledge.  
- If evidence contradicts: surface conflict explicitly.  

### Answer Template

```markdown
## Answer
[Short grounded answer]

## Evidence
- [chunk_1_source]
- [chunk_2_source]
```

---

## 8. Validation

### Checklist

- [ ] Query rewritten (if needed)  
- [ ] Semantic retrieval executed  
- [ ] Keyword retrieval executed  
- [ ] Results merged correctly  
- [ ] Reranking applied  
- [ ] All chunks relevant  
- [ ] No duplicates  
- [ ] Evidence injected properly  
- [ ] Final answer grounded  

### Anti-Patterns

- AVOID: Using semantic-only for fact-heavy queries  
- AVOID: Injecting irrelevant keyword hits  
- AVOID: Overweighting semantic similarity  
- AVOID: Using >700 tokens as context  
- AVOID: Responding without citations  
- AVOID: Mixing multi-domain results  

---

## 9. Complete Example (Optional)

### Pipeline Summary

```
Rewrite: enabled
Semantic top_k: 30
Keyword top_k: 15
Rerank: cross-encoder-finance
Final Chunks: 3
```

### Injection Example

```text
<retrieved>
[Annual Report 2023 - Section 4.2: Revenue Breakdown]
[Annual Report 2023 - Section 4.3: Cost of Goods Sold]
[Annual Report 2023 - Appendix A: Terminology]
</retrieved>
```

### Answer Example

```markdown
Revenue increased due to higher unit sales and expanded distribution channels (see Section 4.2).
```

---

# End of Template
