# Basic RAG Template

*Purpose: Provide a minimal, production-ready template for implementing a simple Retrieval-Augmented Generation pipeline.*

---

## When to Use

Use this template when:

- You need a lightweight RAG pipeline.  
- Retrieval requirements are simple.  
- You want a fast, minimal baseline.  
- Advanced features (HyDE, routing, enrichment) are not required.  

---

# TEMPLATE STARTS HERE

## 1. RAG Overview

**RAG Purpose:**  
[Describe what the RAG pipeline retrieves and why.]

**Sources / Indexes:**  

- [Index name 1]  
- [Index name 2]  

**Constraints:**  

- Only use retrieved evidence for factual claims.  
- No external internet unless explicitly allowed.  

---

## 2. RAG Rules (Minimal)

- Always retrieve before answering fact-based questions.  
- Never answer without evidence.  
- Remove irrelevant or duplicate chunks.  
- Keep injected evidence ≤ 500 tokens.  
- Use reranking on retrieved results.  

---

## 3. Retrieval Pipeline

```text
query → rewrite (if needed) → embed → retrieve → rerank → filter → inject → answer
```

### 3.1 Query Rewrite (Optional)

```text
rewrite(query) → improved_query
```

### 3.2 Embedding

- Use embedding model: [model_name]  
- Use vector store: [db_name]

### 3.3 Retrieval

Parameters:

- Top-k retrieved: [5–20]

### 3.4 Reranking

- Apply cross-encoder or reranker model.  
- Keep top 3–7 chunks.  

### 3.5 Filtering Rules

- Remove chunks with low relevance.  
- Remove stale/conflicting content.  
- Remove duplicates.  

---

## 4. Evidence Injection

### Injection Format

```text
<retrieved>
[chunk_1]
[chunk_2]
...
</retrieved>
```

### Chunk Requirements

- 150–350 tokens each.  
- Single-topic per chunk.  
- Include metadata (source, page).

---

## 5. Answer Generation

### Answer Rules

- Use only retrieved evidence.  
- Cite chunks directly.  
- No hallucinated facts allowed.  
- No claims outside of injected context.  

### Example Format

```markdown
### Answer

[Short, grounded answer here.]

### Evidence

- [chunk_1_source]
- [chunk_2_source]
```

---

## 6. Validation

### Checklist

- [ ] Query rewritten (if ambiguous).  
- [ ] Embeddings computed with correct model.  
- [ ] Retrieval executed with correct k.  
- [ ] Reranking applied.  
- [ ] All chunks relevant.  
- [ ] Evidence injected before reasoning.  
- [ ] Final answer grounded in retrieved text.  

### Anti-Patterns

- AVOID: Answering without retrieval  
- AVOID: Ignoring reranking  
- AVOID: Using more than 500–700 tokens of context  
- AVOID: Mixing unsupported external knowledge  
- AVOID: Summaries not aligned with evidence  

---

# COMPLETE EXAMPLE (Optional)

## Retrieval Pipeline (Example)

**Top-k:** 10  
**Rerank to:** 3  

```text
<retrieved>
[Policy 4.1: Password Requirements]
[Policy 7.2: MFA Procedures]
</retrieved>
```

**Answer (Example)**

```markdown
Your password must meet all requirements listed in Section 4.1, including minimum length and rotation (see evidence above).
```

---

# End of Template
