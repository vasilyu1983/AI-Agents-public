# Retrieval Patterns

Use these as baseline patterns before adding complex orchestration.

## 1. Hybrid Baseline

```text
query
  -> optional normalization
  -> BM25 or lexical retrieval
  -> dense retrieval
  -> fuse results
  -> apply filters
  -> rerank top candidates
  -> return final evidence set
```

Use this for most document-retrieval systems.

## 2. Tool-First Retrieval

Use when the question is really a record lookup, status check, aggregation, or workflow query. Route to tools or APIs first and only use semantic retrieval for explanatory prose.

## 3. Late Interaction / Multivector Retrieval

Use when single-vector retrieval misses subtle relevance, field-specific meaning, or page-level structure. Treat it as a precision upgrade after a hybrid baseline is measured.

## 4. Multimodal Retrieval

Use when page layout, diagrams, tables, forms, or charts matter. Keep text extraction and page/image retrieval connected by stable page IDs.

## 5. Graph + Vector Retrieval

Use when entity traversal or relationship questions matter and unstructured text still provides needed support or quotations.

## 6. Retrieval Debugging Loop

1. Confirm expected evidence exists in the corpus.
2. Test lexical-only and dense-only retrieval separately.
3. Check filters and ACLs before tuning embeddings.
4. Measure reranker value independently.
5. Escalate to multivectors, multimodal retrieval, or agentic loops only if the baseline still fails.

## Anti-Patterns

- Increasing top-k without measuring added noise
- Adding query rewriting before checking metadata and filters
- Using retrieval retries with no evidence-quality signal
- Returning snippets without stable evidence IDs
