# Vector Brain Framework

This is the portable contract for a repeatable vector brain. Backends can vary; the artifact model should not.

## Table of Contents

- [Core Pipeline](#core-pipeline)
- [ASCII Flow](#ascii-flow)
- [Required Objects](#required-objects)
- [Brain And Source Routing](#brain-and-source-routing)
- [Implementation Lifecycle](#implementation-lifecycle)
- [Brain Manifest](#brain-manifest)
- [Design Rules](#design-rules)

## Core Pipeline

```text
Source
  -> Document
  -> Chunk
  -> RetrievalUnit
  -> Embedding
  -> Index
  -> RetrievalResult
  -> ContextBundle or agent tool result
```

## ASCII Flow

```text
[Source roots]
    |
    v
[inventory_corpus.py]
    |
    v
[prepare_documents.py] ---> documents(source_uri, source_path, content_hash)
    |
    v
[chunk_markdown.py] -----> chunks(anchor, citation_anchor, unit_type)
    |                         |  unit_type = chunk | parent | knowledge_packet | compiled_page
    |                         |  parent_child mode emits parent rows plus child chunk rows
    v                         v
[embedder] --------------> embeddings(chunk_id, model_id, embedding)
    |
    v
[hybrid_retrieve_context()]
    |
    +--> lexical candidates from chunks.fts_vector
    +--> vector candidates from embeddings
    +--> filters before fusion: doc_type, authority, language, ACL, as_of, unit_type
    |
    v
[RRF fusion] -> [optional rerank] -> [retrieve_context result] -> [grounded answer]
```

## Required Objects

### Source

The origin of truth.

Required fields:

- `source_id`
- `source_type`: `repo`, `docs_hub`, `policy`, `guide`, `support_kb`, `note_vault`, `generated_graph`, `web`, `pdf`
- `source_uri`
- `owner`
- `acl_scope`
- `freshness_policy`
- `ingest_mode`: `snapshot`, `git_diff`, `webhook`, `manual_upload`, `scheduled_pull`

## Brain And Source Routing

For multi-corpus deployments, keep two routing axes separate:

- **Brain:** the database, deployment, or trust boundary. Change brains when the
  data owner, tenant boundary, retention policy, or access model changes.
- **Source:** a repo, docs hub, vault, team folder, import stream, or generated
  context hub inside one brain. Change sources when the owner stays the same but
  the corpus changes.

`source_id` is not just display metadata. It is part of every document, chunk,
retrieval unit, query log, and citation. A result from a multi-source brain must
be citeable as `brain_id:source_id:source_path#anchor` or an equivalent stable
contract.

Default routing:

| User intent | Route |
|---|---|
| Query current repo/docs hub | Current brain + current source. |
| Query several repos owned by the same team | Same brain, explicit source fan-out. |
| Query another team/customer/personal corpus | Different brain; do not rely on filters inside the current brain. |
| Write new extracted facts or compiled pages | Brain/source that owns the raw signal. |
| Federate across brains | Agent orchestrates multiple queries and cites each boundary explicitly. |

This mirrors the operational-brain pattern in
[`../../ai-context-layer/references/operational-brain-pattern.md`](../../ai-context-layer/references/operational-brain-pattern.md)
and prevents the common failure where a single global vector index hides
ownership, residency, or freshness boundaries.

### Document

The normalized source file or page before chunking.

Required fields:

- `document_id`
- `source_id`
- `source_uri`
- `source_path`
- `title`
- `doc_type`
- `version_or_commit`
- `content_hash`
- `language`
- `metadata`

Recommended fields:

- `effective_from`
- `effective_to`
- `authority`
- `review_status`
- `sensitivity`

### Chunk

The anchored source slice. A chunk can be the retrieval unit for code and navigation-heavy docs, but it is not always the best unit for policy, support, or repeated business knowledge.

Required fields:

- `chunk_id`
- `document_id`
- `chunk_index`
- `content`
- `anchor`
- `section_path`
- `token_count`
- `content_hash`

Recommended fields:

- `parent_chunk_id`
- `contextual_summary`
- `citation_anchor`
- `symbol_name`
- `clause_id`
- `authority`

### RetrievalUnit

The object that is embedded and searched. Use the simplest unit that preserves the answer boundary:

- `chunk`: an anchored source slice
- `parent`: larger parent context row used by child chunks
- `knowledge_packet`: one typed claim, decision, obligation, or question-answer pair
- `compiled_page`: generated wiki page rebuilt from raw sources

Required fields:

- `unit_id`
- `unit_type`
- `source_chunk_ids`
- `embed_text`
- `display_text`
- `citation_anchor`
- `content_hash`

Recommended fields:

- `canonical_unit_id`
- `question`
- `answer`
- `claim_type`: `fact`, `procedure`, `obligation`, `decision`, `definition`, `exception`
- `version_state`: `current`, `draft`, `deprecated`, `superseded`
- `acl_scope`
- `review_status`
- `dedupe_cluster_id`

Rules:

- Embed `embed_text`; show `display_text`; cite the original source anchors.
- Keep the source chunk IDs so every packet can be audited back to documents.
- Do not use LLM-generated packets as source truth; they are projections over source truth.
- Prefer knowledge packets only when they improve evals. Code lookup often needs symbol and file exactness more than distilled Q&A.

### Embedding

The model-specific projection.

Required fields:

- `embedding_id`
- `chunk_id`
- `model_id`
- `embedding`
- `created_at`

Rules:

- Store `model_id` from day one.
- Keep embeddings separate from chunks so model migration is additive.
- Use the same normalized text for indexing and eval reproduction.

### RetrievalResult

The object returned by search before final answer generation.

Required fields:

- `chunk_id`
- `content`
- `source_uri`
- `section_path`
- `score`
- `retrieval_method`
- `freshness`
- `citation_anchor`

Optional fields:

- `rrf_score`
- `vector_score`
- `lexical_score`
- `rerank_score`
- `authority`
- `staleness_warning`
- `conflict_warning`

## Implementation Lifecycle

Use this as the build sequence for a concrete vector brain:

1. **Extract** source documents from the system of record; never make the
   vector index the source of truth.
2. **Normalize** documents into stable `Document` rows with source URI, content
   hash, ACL scope, version, language, and freshness policy.
3. **Chunk or packetize** into retrieval units that preserve the answer boundary.
4. **Embed** with a pinned model ID and dimension; store embeddings separately
   from source chunks.
5. **Baseline exact search** on a small corpus before building ANN indexes.
6. **Index** only after the exact baseline proves the units and model are viable.
7. **Expose an API/tool contract** that validates input, bounds `k`, enforces
   ACLs, and returns source anchors plus scores.
8. **Observe and evaluate** query logs, zero-hit/low-confidence cases,
   recall@k, citation coverage, latency, and corpus-version invalidation.

Compatibility checks before indexing:

- embedding dimension matches the index definition
- query and document embeddings use the same model and preprocessing version
- metadata filters are applied before or during retrieval, not after unsafe
  cross-tenant candidate generation
- normalized embeddings are used when the metric assumes cosine/dot-product
  equivalence
- model, chunker, and preprocessing changes create a new eval cohort

## Brain Manifest

Every brain should have a manifest.

```json
{
  "brain_id": "example-docs-brain",
  "backend": "postgres_pgvector",
  "corpus_type": "docs_hub",
  "embedding_model": "provider/model@dimension",
  "source_roots": ["docs/"],
  "chunking": {"strategy": "heading", "target_tokens": 500},
  "retrieval_unit": {"type": "chunk", "dedupe": "content_hash"},
  "retrieval": {"mode": "hybrid_rrf", "candidate_k": 50, "return_k": 10},
  "freshness": {"mode": "git_diff", "max_staleness_hours": 24},
  "eval": {"dataset": "evals/retrieval.jsonl", "primary_metric": "recall@10"}
}
```

## Design Rules

- The manifest is the build contract, not a README paragraph.
- Source documents are auditable truth; chunks and embeddings are projections.
- Retrieval units are a design choice. Do not assume arbitrary chunks are facts.
- Treat retrieval units like an approximation domain: if units are too large,
  mixed, or poorly anchored, similarity smooths away the local evidence the
  answer needs.
- Distilled packets need source anchors, version state, access scope, and review status.
- Generated graphs can guide retrieval but should remain rebuildable from sources.
- Context bundles should carry evidence, not just text.
- Corpus-specific evals decide whether a tuning change is safe.
