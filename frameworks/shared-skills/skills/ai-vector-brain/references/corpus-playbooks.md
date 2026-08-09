# Corpus Playbooks

V1 supports three playbooks. Choose one before writing schema, scripts, or evals.

## Table of Contents

- [Repo / Codebase Brain](#repo--codebase-brain)
- [Docs Hub Brain](#docs-hub-brain)
- [Compliance / Policy Brain](#compliance--policy-brain)
- [Corpus Flow Summary](#corpus-flow-summary)

## Repo / Codebase Brain

Use when the corpus is a software repository or repo portfolio.

Primary questions:

- where is this behavior implemented?
- what files, modules, APIs, migrations, or tests matter?
- what is the blast radius?
- what docs explain this subsystem?

Chunking:

- Markdown: heading-anchored chunks.
- Code: function/class/module boundaries when parser support exists; otherwise file sections with stable line anchors.
- Config and manifests: keep logical objects atomic.
- Retrieval unit: usually source chunk or symbol record, not distilled Q&A. Preserve exact path, line, symbol, and commit.

Required metadata:

- `source_repo`
- `source_path`
- `source_commit_sha`
- `language`
- `symbol_name` when known
- `artifact_type`: `code`, `test`, `config`, `docs`, `migration`, `api_contract`
- `content_hash`

Eval focus:

- symbol/path exact-match recall@5
- file recall@10
- stale-commit detection
- negative queries that should refuse or ask for more context

Anti-patterns:

- embedding generated/vendor/build output
- summarizing code without preserving path and commit
- treating generated summaries as primary source
- chunking code by arbitrary character count

Flow:

```text
repo files
  -> inventory source paths and commit SHAs
  -> split by symbol, heading, or logical file section
  -> attach path, symbol_name, artifact_type, commit, content_hash
  -> embed source chunks or symbol records
  -> retrieve by lexical + vector + path/symbol filters
  -> answer with file path, symbol, and commit evidence
```

## Docs Hub Brain

Use when the corpus is a curated documentation hub, handbook, product docs, architecture docs, or generated context folder.

Primary questions:

- where is the canonical explanation?
- what page or section should I read?
- how do related docs connect?
- what changed since the last verified snapshot?

Chunking:

- heading-aware Markdown chunks
- keep tables and code blocks atomic
- preserve backlinks, navigation hierarchy, and freshness metadata
- treat generated JSON/graphs as metadata or edge inputs unless users need raw lookup
- For duplicate or near-duplicate docs, add a canonicalization pass before embedding so top-k does not return five versions of the same paragraph.
- For user-question-heavy hubs, consider typed knowledge packets: one question, answer, source anchor, status, and owner. Keep generated packets rebuildable from source docs.

Recommended staging:

- `raw/`: copied/imported source material, exports, transcripts, screenshots with OCR, and unorganized notes
- `compiled/` or `wiki/`: generated canonical pages and cross-links; rebuild from `raw/`
- `outputs/`: answers, briefings, and research artifacts; only promote to `compiled/` after review

Required metadata:

- `source_path`
- `section_path`
- `last_verified`
- `review_cadence`
- `doc_owner`
- `doc_status`: `canonical`, `generated`, `draft`, `archive`, `report`
- `content_hash`

Eval focus:

- recall@10
- answer faithfulness
- citation coverage
- canonical-source selection over duplicate reports

Anti-patterns:

- indexing archives as canonical
- mixing generated reports with source docs without labels
- feeding generated outputs back into the brain as canonical truth without review
- missing freshness fields on critical docs
- returning prose without source links

Flow:

```text
raw/
  -> normalize into documents with owner/status/freshness metadata
  -> heading-aware chunks; keep tables/code blocks atomic
  -> canonicalize near-duplicate docs before embedding
  -> optional compiled/wiki pages after review
  -> hybrid retrieval favors canonical docs over generated reports
  -> answer with source path, section path, and freshness status
```

## Compliance / Policy Brain

Use when the corpus contains policies, regulations, standards, controls, runbooks, regulator letters, or audit evidence.

Primary questions:

- what rule applies?
- which version was effective at a date?
- what policy implements which regulation or control?
- can this answer be cited safely?

Document sources and ingestion (pick what matches the corpus):

- self-hosted document store: **paperless-ngx** — pull via REST API (`GET /api/documents/`, text via `/api/documents/{id}/content/`, binary via `/api/documents/{id}/download/`) or watch the consume folder. Documents arrive already OCR'd (paperless runs Tesseract on ingest), so no separate OCR pass is needed. Map paperless fields to required metadata: `correspondent`/`document_type` -> `authority`, `created` -> `effective_from`, `tags` -> `owner`/review state, `id` -> `source_uri`.
- mixed/variable documents not already OCR'd: **Amazon Bedrock Data Automation (BDA)** is the AWS-recommended default for intelligent document processing — one API classifies + extracts via foundation models, flat per-document pricing. As of the March 2026 unification, **Textract is the OCR layer inside BDA's "Bedrock Pipeline" mode** for complex docs.
- scanned, high-volume, or compliance-grade standardized PDFs (regulator letters, signed policies, 50k+/mo receipts): **AWS Textract** standalone (`StartDocumentTextDetection` async batch; `AnalyzeDocument` for forms/tables/signatures) — deterministic, ~75% cheaper per doc than BDA for standardized formats, 95%+ accuracy. Assemble Textract blocks into clause-ordered text/Markdown *before* clause-aware chunking — preserve section headings so `clause_id` survives.
- plain filesystem of text/Markdown: feed directly to the chunker.

Embedding model on AWS: **Amazon Nova 2 Multimodal Embeddings** is the AWS-native default for Bedrock pipelines (supersedes Titan Text/Multimodal Embeddings); Matryoshka-tunable to 3072/1024/384/256 dims, 8,192-token context, 200 languages. Pair with S3 Vectors or Aurora pgvector. Layer **Amazon Bedrock Rerank** (Cohere Rerank 3.5 / Amazon Rerank) on the candidate list — reranking is the largest accuracy lever for citation-precision-critical compliance corpora. Verify the current model id and dimension in the Bedrock console before pinning a manifest.

Chunking:

- clause-aware chunks
- preserve numbered sections, schedules, appendices, and footnotes
- do not split obligations across chunks
- use parent-child chunks for long clauses or procedures
- Consider obligation packets only after clause-aware chunks exist: one obligation, applicability condition, effective date, source clause, authority, and review status.
- Deduplicate copied obligations across policies by canonical obligation ID, while preserving each implementing document as evidence.

Required metadata:

- `doc_id`
- `version`
- `clause_id`
- `authority`: `regulation`, `policy`, `standard`, `procedure`, `runbook`, `guideline`
- `effective_from`
- `effective_to`
- `owner`
- `reviewer_approved_at`
- `source_uri`
- `citation_anchor`

Eval focus:

- citation precision
- refusal correctness when no evidence exists
- effective-time correctness
- conflict detection
- authority ranking over semantic similarity

Generation-time governance (AWS): layer **Amazon Bedrock Guardrails** on the generate step — the **contextual grounding check** scores each answer for grounding against retrieved chunks and relevance to the query, blocking ungrounded responses (the runtime enforcement of "refusal correctness" above); **Automated Reasoning** adds mathematically verifiable policy checks; **PII redaction** (built-in entities + custom regex) protects restricted material at output. Apply the same guardrail across models via the standalone `ApplyGuardrail` API so the gate is model-independent.

Anti-patterns:

- quoting a guideline when a regulation conflicts
- losing effective dates during ingest
- citing document titles without clause anchors
- allowing stale or unapproved policy chunks to answer without warnings
- letting deprecated and current versions compete in top-k without version filters

Flow:

```text
policy/regulation/runbook sources
  -> normalize doc_id, version, authority, effective dates
  -> clause-aware chunks; preserve clause_id and citation_anchor
  -> optional obligation packets after clause chunks exist
  -> filter by authority, ACL, as_of, and unit_type before fusion
  -> rank regulation > policy > procedure > runbook > guideline
  -> answer or refuse with paragraph-precise citations
```

## Corpus Flow Summary

```text
repo brain:       source path + symbol + commit      -> exact evidence recall
docs hub brain:   canonical page + section + status  -> navigable grounded answers
policy brain:     authority + effective date + cite  -> safe answer or refusal
```

### Deferred extension: graph-bounded retrieval

Graph-bounded retrieval (`graph_bounded_hybrid_rrf`) is a future extension for compliance brains where the corpus has explicit obligation graphs (regulation → policy → procedure → control → evidence). The idea: constrain the candidate pool to a subgraph (e.g. "all implementations of clause X under authority Y at date Z") *before* hybrid RRF runs, instead of relying on metadata filters alone.

V1 does not ship this. The `policy-brain.manifest.json` example uses plain `hybrid_rrf` with required `authority` and `as_of` filters. When v1.x adds graph-bounded retrieval, it will compose with the same `hybrid_retrieve_context` function via an additional `p_clause_graph_root` filter parameter — additive, not breaking.

If you need graph-bounded retrieval before it ships, build it as an app-layer pre-filter: resolve the obligation subgraph in your application, pass the resulting `chunk_id` set as a candidate constraint, then call hybrid retrieval against that pool.
