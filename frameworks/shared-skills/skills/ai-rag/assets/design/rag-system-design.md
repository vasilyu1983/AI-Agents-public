# Retrieval System Design Template

**Purpose**: choose the right retrieval mode, define evidence contracts, and plan evaluation before implementation.

---

## 1. Problem Definition

- **Use case**:
- **Primary users**:
- **Queries to support**: factual / exploratory / analytical / multi-hop / workflow-triggered
- **Authority source**: documents / files / tools / APIs / SQL / graph / hybrid
- **Latency budget**:
- **Freshness requirement**:
- **Need citations or traceability?** yes / no
- **Need tenant or document ACL enforcement?** yes / no
- **Document types**: text / code / tables / PDFs / images / mixed
- **Compliance or residency constraints**:

---

## 2. Retrieval Mode Decision

```text
Need external knowledge?
  -> No: use direct prompting
  -> Yes:
     - Source of truth already lives in tools or APIs?
       -> Tool-first or MCP retrieval
     - Needs joins, counts, or graph traversal?
       -> SQL / graph / graph+vector hybrid
     - Corpus fits in context and changes slowly?
       -> Long-context or hosted file search
     - Need semantic retrieval over prose or mixed documents?
       -> Hybrid sparse+dense baseline
     - PDFs, tables, charts, or page layout matter?
       -> Multimodal document retrieval
     - Precision still poor?
       -> Add reranking, late interaction, or multivectors
```

**Selected retrieval mode**:

- [ ] Long-context only
- [ ] Hosted file search
- [ ] Tool-first / MCP
- [ ] SQL / graph retrieval
- [ ] Hybrid sparse + dense
- [ ] Multimodal retrieval
- [ ] Late interaction / multivectors
- [ ] Hybrid of the above

**Why this mode fits better than alternatives**:

---

## 3. Corpus And Evidence Contract

### Corpus Profile

- **Corpus size**:
- **Update frequency**:
- **Deletion requirements**:
- **Average document length**:
- **Expected languages**:

### Evidence Contract

- **Stable evidence ID format**:
- **Required metadata**: source, timestamp, ACL, page/section, language, content type
- **Citation granularity**: document / page / section / chunk / table cell / tool record
- **Response must include**:
  - [ ] evidence IDs
  - [ ] source titles or paths
  - [ ] timestamps
  - [ ] page/section references
  - [ ] refusal when evidence missing

---

## 4. Retrieval Pipeline

### Ingestion

- **Parser/extractor**:
- **Chunking strategy**:
- **Chunk size / overlap**:
- **Metadata enrichments**:
- **Embedding model family**:
- **Index or storage**:

### Query Path

- **Pre-filters**:
- **Candidate generation**:
- **Candidate count**:
- **Reranker**:
- **Final context size**:
- **Fallback path if retrieval fails**:

### Freshness And Isolation

- **Invalidation trigger**:
- **Index rebuild strategy**: full / incremental / append-only
- **ACL enforcement point**:
- **Tenant isolation strategy**:

---

## 5. Evaluation Plan

### Offline Eval

- **Test set source**: human-written / synthetic scaffold / mixed
- **Slices**: easy / hard / ambiguous / unanswerable / multilingual / PDF / table / high-stakes
- **Retrieval metrics**: recall@k / MRR / nDCG / empty-result rate / latency
- **Answer metrics**: correctness / groundedness / citation validity / refusal correctness

### Online Monitoring

- **Business metrics**:
- **Operational metrics**:
- **Guardrails**:
  - [ ] prompt injection detection
  - [ ] ACL failures
  - [ ] stale-answer incidents
  - [ ] citation-support failures

---

## 6. Risks And Rollback

- **Top risks**: staleness / wrong-source retrieval / ACL leak / unsupported citations / latency spikes
- **Rollback lever 1**:
- **Rollback lever 2**:
- **Safe degraded mode**:

---

## 7. Decision Summary

| Area | Decision | Reason |
|------|----------|--------|
| Retrieval mode |  |  |
| Parsing/chunking |  |  |
| Storage/index |  |  |
| Ranking |  |  |
| Grounding policy |  |  |
| Evaluation gate |  |  |
| Freshness policy |  |  |

