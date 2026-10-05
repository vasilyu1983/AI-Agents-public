# RAG Observability And Tracing Contract

Use this contract for any retrieval, vector search, or RAG system that must be
debuggable after deployment. It is backend-neutral and compatible with OpenTelemetry
GenAI semantic conventions; verify current attribute names against the official
OpenTelemetry docs before hard-coding them.

## Contents

- [Trace Shape](#trace-shape)
- [Required Attributes](#required-attributes)
- [Redaction Rules](#redaction-rules)
- [Dashboards](#dashboards)
- [Acceptance Gate](#acceptance-gate)

## Trace Shape

Create one parent trace per user request or agent tool call.

```text
request
  -> context_assembly
  -> retrieve
       -> query_preprocess
       -> embed_query
       -> sparse_search
       -> vector_search
       -> fusion
       -> rerank
       -> hydrate
  -> generate_or_tool_response
  -> citation_check
```

Skip spans that do not exist in the implementation, but never collapse
retrieval and generation into one opaque span.

## Required Attributes

Record these attributes or equivalent names:

- `corpus_id`
- `corpus_version`
- `chunker_version`
- `embedding_model`
- `embedding_dimension`
- `retrieval_mode`: `lexical`, `vector`, `hybrid_rrf`, `hybrid_rerank`,
  `late_interaction`, `tool_first`, `hosted`
- `candidate_k`
- `return_k`
- `filters_applied`
- `acl_scope_hash`
- `query_preprocess_version`
- `reranker_model`
- `top_evidence_ids`
- `empty_result`
- `latency_ms`
- `token_count_in`
- `token_count_out`
- `citation_check_status`

For answer-generation spans, also record:

- `evidence_count`
- `unsupported_claim_count`
- `refusal_expected`
- `refusal_observed`
- `model_id`

## Redaction Rules

- Hash actor, tenant, and ACL values when raw values are sensitive.
- Never log raw private documents, full user prompts, secrets, credentials, or
  unredacted PII by default.
- Log evidence IDs and source anchors instead of full chunks.
- Store full traces only in a controlled debug mode with explicit retention.
- Keep trace retention shorter than corpus retention unless compliance requires
  the opposite.

## Dashboards

Minimum production dashboard:

- retrieval latency P50/P95/P99 by retrieval mode
- empty-result rate by corpus and query tag
- recall@k and nDCG on the golden eval suite
- citation-check failures
- unsupported-claim rate
- top stale or tombstoned evidence returned
- cross-tenant or denied-filter attempts
- embedder and reranker error rate
- cache hit rate with corpus-version invalidation rate

## Acceptance Gate

A retrieval system is not production-ready until:

- every response can be traced to evidence IDs or a no-evidence refusal
- retrieval metrics and answer metrics are reported separately
- traces include corpus and model versions
- sensitive data is redacted before traces leave the trust boundary
- there is a documented debug path from a bad answer to the specific retrieval
  stage that failed

## Sources

- OpenTelemetry Semantic Conventions for Generative AI systems:
  https://opentelemetry.io/docs/specs/semconv/gen-ai/
