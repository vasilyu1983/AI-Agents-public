# Advanced RAG Pipeline Template

*Purpose: Deploy a robust, high-recall RAG system for production or high-value use cases (large corpora, mixed formats, high accuracy/faithfulness demands).*

---

## When to Use

Use this template when:

- Your knowledge base is large, diverse, or multi-format (e.g., >50k docs, mixed PDF/web/Markdown)
- Retrieval precision, faithfulness, or latency is critical
- You need hybrid retrieval (dense + keyword/BM25), reranking, or automated context compression
- The LLM must reliably ground answers in external, up-to-date, or compliance-sensitive data

---

## Structure

This template has 6 sections:

1. **Advanced Chunking** – structure-aware, semantic windowing, deduplication
2. **Hybrid Retrieval** – dense + keyword search, metadata filtering
3. **Post-Retrieval Reranking** – LLM/cross-encoder or custom rankers
4. **Context Compression** – select/summarize to fit context window
5. **Prompt Assembly** – structured, citation-required, with fallback
6. **Evaluation & Monitoring** – log, validate, and monitor recall, latency, faithfulness

---

# TEMPLATE STARTS HERE

## 1. Advanced Chunking

- Parse docs by structure (headings, sections, tables)
- Use semantic chunkers if possible (not just token windows)
- Chunk size: 300–800 tokens (adjust per doc type)
- Deduplicate near-duplicate chunks (hash or similarity match)
- Track metadata: doc/source, section, timestamp, tags

## 2. Hybrid Retrieval

- At query:  
  - **Dense retrieval:** Embed question, search vector DB (e.g., BGE, ada-002, E5, etc)
  - **Keyword/BM25 retrieval:** Run keyword search, e.g. with Elastic or built-in
  - Combine results, remove duplicates
  - Filter by metadata if needed (date, type, tags)

## 3. Post-Retrieval Reranking

- Pass candidate chunks to reranker:
  - LLM-based: e.g., “Does this chunk answer the question? Y/N”
  - Cross-encoder model or BERT re-ranker
- Select top-N (usually 2–6) for final prompt

## 4. Context Compression

- If context window exceeded:
  - Summarize lower-priority chunks, or
  - Select most relevant sentences within chunk
  - Hard truncate only as last resort

## 5. Prompt Assembly

**Prompt Template:**

```
Answer ONLY using the context. If context is insufficient, say "Not found."
Cite sources (e.g., [doc1], [doc2]) for every claim.

Context:
{ranked_context_with_sources}

Question: {user_question}

Answer:
```

## 6. Evaluation & Monitoring

- Log retrievals, LLM generations, user feedback
- Periodically re-benchmark retrieval recall, faithfulness, latency, cost
- Trigger alert/rollback if key metrics degrade

---

# COMPLETE EXAMPLE

**Python (LangChain/Hybrid/LLM rerank pseudo-code):**

```python
# 1. Chunking
docs = load_docs("corpus/")
chunks = semantic_chunk(docs)
chunks = deduplicate_chunks(chunks)
store_chunks(chunks, metadata=["doc", "section", "date"])

# 2. Hybrid Retrieval
def hybrid_search(query):
    dense_hits = vector_search(query, top_k=12)
    keyword_hits = bm25_search(query, top_k=12)
    hits = merge_dedup(dense_hits, keyword_hits)
    return hits

# 3. Reranking
reranked = llm_rerank(query, hits, top_n=4)

# 4. Context Compression
context = compress_context(reranked, max_tokens=1800)

# 5. Prompt Assembly
sources = "\n\n".join([f"[{c['doc']}] {c['content']}" for c in context])
prompt = f"""
Answer ONLY using the context. If context is insufficient, say "Not found."
Cite sources (e.g., [doc1], [doc2]) for every claim.

Context:
{sources}

Question: {query}

Answer:
"""
answer = call_llm(prompt)
print(answer)
```

---

## Quality Checklist

Before finalizing:

- [ ] Semantic or structure-aware chunking, dedup complete
- [ ] Hybrid retrieval (dense + keyword) implemented, tuned
- [ ] Reranker (LLM/cross-encoder) validated for precision
- [ ] Context fits LLM input window (with compression)
- [ ] Prompt requires citations, fallback "Not found"
- [ ] Retrieval recall, latency, faithfulness monitored, alerts configured

---

*For minimal use cases, see [template-basic-rag.md]. For multi-agent or multimodal, see [agentic-workflows/]. For eval, see [references/eval-patterns.md].*
