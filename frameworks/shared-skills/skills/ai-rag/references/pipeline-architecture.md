# RAG Pipeline Architecture

Comprehensive guide to end-to-end RAG pipeline design, ingestion, and index hygiene.

## End-to-End RAG Pipeline Structure

Use when designing any retrieval-augmented system.

### Pipeline Stages

1. **Ingestion**
   - Extract text
   - Clean & normalize
   - Split into units (chunks)

2. **Embedding**
   - Use a consistent embedding model
   - Store vectors + metadata + original text

3. **Indexing**
   - Build vector index (HNSW / IVF / Flat)
   - Configure parameters (ef_search, nlist, nprobe, etc.)

4. **Retrieval**
   - KNN or hybrid (BM25 + vectors)
   - Apply filters (metadata, keywords, content type)

5. **Reranking (optional but recommended)**
   - Cross-encoder or lightweight LLM reranker
   - Improves relevance when K > 5

6. **Context Packaging**
   - Merge & order results
   - Trim to token budget
   - Prepare prompt blocks

7. **Generation**
   - Controlled prompt
   - Format-safe output
   - Grounding reminders ("Use only provided context")

### Pipeline Implementation Checklist

- [ ] Clear ingestion → embedding → indexing → retrieval → generation
- [ ] Same embedding model for indexing & querying
- [ ] Retrieval K sized based on evaluation (not guesswork)
- [ ] Reranker included for deep queries
- [ ] Context window budget defined

---

## Ingestion, Freshness, and Index Hygiene

### Data Feeds & Ingestion Patterns

- **Feeds:** Prefer CDC/log-based ingestion for changing sources; keep idempotent loaders
- **Schema evolution:** Version metadata schema; add forward/backward-compatible parsers; log index version and embedding model version
- **Backfill/compaction:** Schedule rebuilds; support hot-swap (dual index + flip); compact deletes/updates
- **Freshness/SLA:** Track lag from source → index; alert if beyond threshold; record chunk timestamp/version for provenance
- **Governance/residency:** Honor hard-delete requests (GDPR); propagate deletions to embeddings; segment indexes by residency/tenant; maintain audit trail
- **Provenance:** Store source URI, section/page, checksum; include in context to satisfy governance

### Ingestion Health Checklist

- [ ] CDC/backfill path documented and tested
- [ ] Index + embedding versions tracked
- [ ] Dual-index or hot-swap path available
- [ ] Freshness lag monitored with alerting
- [ ] Provenance stored and surfaced to model

---

## Embedding Model Selection

**Use when selecting embedding model.**

### Decision Rules

- Need **fast + cheap** → small embedding model (e.g. BERT-mini / fastembed)
- Need **domain-specific** → domain model (legal/medical/code)
- Need **high recall** → modern LLM embeddings (1000+ dims)
- Need **multilingual** → multilingual embedding model

### Embeddings Ready Checklist

- [ ] Model chosen based on domain + cost
- [ ] Dimensionality known
- [ ] Same embedding model used for query + index
- [ ] Embeddings stored with metadata + raw text

---

## Related Resources

- [Chunking Patterns](chunking-patterns.md) - Detailed chunking strategies
- [Index Selection Guide](index-selection-guide.md) - Vector database configuration
- [Retrieval Patterns](retrieval-patterns.md) - Retrieval optimization techniques
- [RAG Troubleshooting](rag-troubleshooting.md) - Debugging and fixes
