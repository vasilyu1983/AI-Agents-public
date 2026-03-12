# Advanced RAG Template

*Purpose: Provide a full production-grade template for complex Retrieval-Augmented Generation, including routing, HyDE, multi-index retrieval, hierarchical search, enrichment, and advanced filtering.*

---

## When to Use

Use this template when:

- Retrieval spans multiple domains or indexes  
- Queries are complex, ambiguous, or sparse  
- Strict grounding and accuracy are required  
- You need hierarchical, hybrid, or enriched retrieval  
- You must enforce domain-based filtering  
- You require structured outputs  

---

# TEMPLATE STARTS HERE

## 1. RAG Overview (Advanced)

**Goal:**  
[Describe precise retrieval goals]

**Sources / Indexes:**  

| Index | Domain | Chunk Size | Reranker | Notes |
|--------|---------|-----------:|----------|-------|
| [index_1] | [...] | [...] | [...] | [...] |
| [index_2] | [...] | [...] | [...] | [...] |

**Core Requirements:**  

- Multi-step retrieval  
- Multi-domain routing  
- Heavy reranking  
- Strict evidence-only generation  
- No hallucinations  

---

## 2. Advanced RAG Pipeline

```
query
→ detect_domain
→ route_to_index
→ rewrite (optional)
→ embed
→ retrieve (semantic + keyword)
→ rerank
→ hierarchical_refine
→ context_enrich
→ filter (domain + relevance)
→ inject
→ answer
```

---

## 3. Domain Detection & Routing

### 3.1 Classification Pattern

```
domain = classify(query)
index = route(domain)
```

### 3.2 Routing Table

| Domain | Index | Notes |
|--------|--------|--------|
| Legal | legal_idx | strict citations |
| Finance | finance_idx | numbers only from evidence |
| Code | code_idx | avoid hallucinated API names |
| Technical | docs_idx | tie-breaker by relevance |

### 3.3 Routing Rules

- Reject multi-domain queries → request clarification  
- Use fallback index only if domain = “unknown”  

---

## 4. Query Rewrite (Advanced)

### Rewrite Logic

- Expand acronyms  
- Add domain-specific terminology  
- Convert vague queries → explicit format  
- Split multi-intent queries into subqueries  

**Rewrite Template**

```text
rewrite(query) → domain-specific, explicit, unambiguous query.
```

---

## 5. Embedding & Retrieval

### 5.1 Embedding

- Use consistent embedding model  
- Use deterministic pre-processing  

### 5.2 Hybrid Retrieval

```
semantic_top_k = [20–50]
keyword_top_k = [10–20]
combine → dedupe → rerank
```

### 5.3 Retrieval Rules

- Never rely on raw top-k  
- Deduplicate before reranking  
- Resolve conflicts using domain priority  

---

## 6. HyDE (Hypothetical Document Embedding)

### When to Use

- Sparse queries  
- Retrieval fails or low hit rate  
- Queries with abstract terms  

### Pattern

```
hyde_doc = generate_hypothetical_doc(query)
embed(hyde_doc)
retrieve_using_hyde()
```

### HyDE Rules

- hyde_doc ≤ 150 tokens  
- Must reflect domain constraints  
- Must not include fabricated details  

---

## 7. Hierarchical Retrieval

### Pattern

```
retrieve(topic-level)
→ retrieve(section-level)
→ retrieve(paragraph-level)
```

### Rules

- Use hierarchical steps only when needed  
- Limit final extraction to 3–7 chunks  
- Collapse similar content into summaries  

---

## 8. Context Enrichment

### Pattern

```
add(metadata)
add(linked_entities)
add_relevant_history()
```

### Use Cases

- Entity-based tasks  
- Multi-turn workflows  
- Cross-document synthesis  

### Allowed Metadata

- IDs  
- Dates  
- Sections  
- Entity names  
- Structured fields  

---

## 9. Filtering (Advanced)

### Filters

- Domain match  
- Relevance threshold  
- Recency filter (if applicable)  
- Deduplication  
- Conflict resolution  

### Conflict Resolution Rules

- Prefer more recent content  
- Prefer domain-specific over generic  
- Prefer higher reranker score  

---

## 10. Evidence Injection

### Injection Format

```text
<retrieved>
[chunk_1]
[chunk_2]
[chunk_3]
...
</retrieved>
```

### Requirements

- Max injected length: 500–700 tokens  
- Chunks must be topic-pure  
- Include metadata (source, page, hash)  

---

## 11. Answer Generation (Strict)

### Answer Rules

- Use ONLY injected evidence  
- Cite exact chunks  
- No external world knowledge  
- No hallucinated claims  
- When evidence is missing → “insufficient data”  

### Answer Format

```markdown
## Answer
[Short grounded answer]

## Evidence
- [chunk_1_source]
- [chunk_2_source]
```

---

## 12. Validation Pipeline

### Checklist

- [ ] Domain classified accurately  
- [ ] Routed to correct index  
- [ ] Query rewritten properly  
- [ ] Hybrid retrieval used  
- [ ] Reranking applied  
- [ ] HyDE applied (if needed)  
- [ ] Hierarchical retrieval validated  
- [ ] Enrichment consistent  
- [ ] All chunks relevant  
- [ ] No duplicates  
- [ ] Answer grounded & cited  

---

## 13. Anti-Patterns (Advanced)

- AVOID: Skipping reranking  
- AVOID: Injecting > 700 tokens  
- AVOID: Mixing domain-chunks  
- AVOID: Summaries with fabricated content  
- AVOID: Relying solely on semantic search  
- AVOID: Using HyDE without domain consistency  
- AVOID: Answering from memory instead of evidence  
- AVOID: Citation mismatch  

---

## 14. Complete Example (Optional)

### Example Retrieval Summary

```text
Domain: Legal
Index: legal_idx
Rewrite: "Summarize the obligations in Section 12 of Contract A."
Hybrid Retrieval: semantic_k=30, keyword_k=10
Rerank: cross-encoder-legal
Final Chunks: 3
```

### Example Injection

```text
<retrieved>
[Contract A - Section 12: Obligations]
[Contract A - Section 12.1: Deliverables]
[Contract A - Section 12.3: Compliance Requirements]
</retrieved>
```

### Example Answer

```markdown
Section 12 requires the vendor to deliver the agreed-upon services, comply with listed requirements, and maintain proper documentation (see evidence above).
```

---

# End of Template
