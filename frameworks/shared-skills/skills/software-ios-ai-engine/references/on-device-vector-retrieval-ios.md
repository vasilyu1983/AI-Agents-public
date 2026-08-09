# On-Device Vector Retrieval on iOS

Use this reference when an iOS app needs local semantic search, local retrieval for Foundation Models tools, or an offline vector-like index over user/app content.

## Table of Contents

- [Decision Matrix](#decision-matrix)
- [Index Contract](#index-contract)
- [Retrieval Shapes](#retrieval-shapes)
- [When to Route to ai-vector-brain](#when-to-route-to-ai-vector-brain)
- [Proof Gates](#proof-gates)

## Decision Matrix

| Corpus | Default | Notes |
|---|---|---|
| App help, short built-in knowledge, settings, small note set | Natural Language embeddings or lexical + metadata search | Lowest operational cost |
| User notes/documents, hundreds to low thousands of chunks | Local table with stored vectors + Accelerate/simd scoring | Version embeddings and corpus |
| Bundled read-only knowledge | Precomputed chunks + vectors shipped in app bundle | Rebuild on release |
| Shared/public corpus, millions of chunks, team search | Server vector brain | Route to `ai-vector-brain` |
| Regulated or citation-heavy retrieval | Upstream RAG/vector system with evals | Local mirror only if citations and ACLs remain exact |

Apple Natural Language can provide word and sentence embeddings. Contextual embeddings can produce token vectors when assets are available. For scoring arbitrary local vectors, use Accelerate/simd-style vector math or a small embedded vector library if the project standardizes on one.

## Index Contract

Every local retrieval unit needs:

- stable `id`
- `content`
- optional `title`
- `sourceURI` or local route
- `contentHash`
- `corpusVersion`
- `embeddingModel`
- `locale`
- access scope
- timestamp or release marker

Do not store anonymous vectors without source anchors. Retrieval without provenance cannot safely ground Foundation Models output.

## Retrieval Shapes

### Lexical First

Use for identifiers, settings, exact names, commands, and small corpora. Prefer this before embedding when exact match is enough.

### Natural Language Embedding

Use for semantic similarity where Apple-provided language support fits the corpus. Gate assets and language support.

### Local Vector Table

Use when the app owns embeddings from a local model, bundled model, or upstream build step. Store vectors with corpus version and model ID.

### Foundation Models Tool

Expose retrieval as a tool only when the model genuinely needs to decide when to search. If retrieval is always required, run it before the model call and include the compact result in the prompt.

## When to Route to ai-vector-brain

Route to `ai-vector-brain` when:

- corpus size or update rate exceeds device-local search
- many users share the same corpus
- ACLs are server-owned
- hybrid lexical/vector/rerank is required
- evals, ingest ledgers, query logs, tombstones, or migrations are central
- the app needs pgvector, Qdrant, Weaviate, Pinecone, OpenSearch, or other server backends

For iOS, `ai-vector-brain` can still build the upstream corpus, chunks, manifests, eval seeds, and bundle artifacts. Runtime on-device retrieval remains owned here.

## Proof Gates

1. Retrieval eval set with query -> expected evidence IDs.
2. Locale/language support check for embedding path.
3. Corpus version invalidation test.
4. Top-k latency budget on target device class.
5. Privacy check: user-private chunks never cross accounts or profiles.
6. Foundation Models output validator confirms retrieved anchors are the only facts used.
