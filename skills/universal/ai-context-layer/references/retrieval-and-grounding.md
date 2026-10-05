# Retrieval And Grounding

Use [ai-rag](../../ai-rag/SKILL.md) for depth. This file defines the context-layer boundary.

## Retrieval Belongs Here When

- The source is prose or documents.
- The app needs citations or evidence.
- The corpus changes independently of the operational database.
- The answer should be grounded in external or derived content.

## Retrieval Does Not Belong Here When

- The answer depends on live billing, entitlement, profile, or org state.
- The source of truth already lives in SQL or tools.
- The question is mainly aggregate or transactional.

## Grounding Requirements

Every retrieval result should carry:

- source identifier
- chunk or page identifier
- freshness timestamp
- ACL scope
- confidence or ranking score
- stable citation handle

## SQL Backed RAG Rollout

When the retrieval store is Postgres/Supabase, do not make vector search or
full-text search the first blocking migration. Ship retrieval in layers:

1. Source/chunk tables, RLS, and evidence metadata.
2. Minimal lexical retrieval RPC with tenant/tier/ACL filters.
3. Content seed as DML only.
4. Ranking tuning with stopwords, intent boosts, and deterministic ordering.
5. Retrieval evals for expected chunks/modules and leakage checks.
6. Optional indexed retrieval after the target database proves extension support.

Capability probes should precede migrations that depend on `pgvector`,
generated search columns, text-search configurations, trigram indexes, HNSW,
IVFFlat, or provider-specific search behavior. Keep DDL, function changes, and
large content seeds separate so a failed search feature does not block safe
content rollout.

Keep lexical retrieval as-is when the corpus is small, tier/ACL probes pass,
and retrieval evals show expected top chunks. Defer retrieval logs retention,
editor lifecycle metadata, localization, corpus versioning, miss tracking,
embeddings, and dedicated search until a concrete trigger exists: traffic,
corpus growth, frequent content edits, locale quality gaps, audit needs, failed
evals, or measured latency.

## Episode Provenance Chain

Citations should chain back to a raw **episode** (conversation turn, document, event, ingest batch), not stop at the chunk.

- **Why**: chunks are a transient artifact of whatever chunker ran at index time. Re-chunk with a different strategy and the chunk IDs disappear, breaking every citation that pointed at them. Episode IDs — the ID of the raw input the fact was derived from — survive re-chunking, re-embedding, and re-extraction.
- **Pattern**: keep `source_episode_id` on `LearnedMemory` and on retrieval results. When a user asks "why do you think this?", the answer is "derived from episode E-2026-04-10-0312, which was `[conversation turn | email | document | tool result]`." The episode store holds the raw input verbatim; derived layers point at it.
- **Check**: if you cannot reconstruct *why* a fact is in derived memory after re-running the pipeline, the provenance chain is broken. Fix by persisting episode IDs at write time, not regenerating them.
- **Interaction with bi-temporal invalidation**: the episode is also what you re-read when a contradiction is reported — the raw episode is ground truth, the extracted fact is derived and can be wrong.

<!-- Source: github.com/getzep/graphiti@98d8344d531aa74160f2e33b8db84c5bdc9954ba (Apache-2.0), extracted 2026-04-15 -->


## Agentic Retrieval

Retrieval is increasingly agent-orchestrated rather than pipeline-driven:

- **Agent-decides-what-to-retrieve**: the agent inspects the query, decides which retrieval sources to call, and may issue multiple retrieval rounds with refined queries. This replaces static retrieve-then-generate pipelines.
- **Multi-step retrieval**: the agent retrieves, inspects results, identifies gaps, and re-queries with different terms or sources. This is standard in Azure AI Search agentic retrieval and LangChain/LlamaIndex tool-use patterns.
- **Intent-based routing**: classify the query intent first, then route to the appropriate retrieval source (tool/API for live state, vector index for prose, graph for relationships). The agent or a lightweight classifier makes this decision.
- **Self-RAG**: the agent evaluates whether retrieved context is actually relevant before using it. Irrelevant retrievals are discarded rather than stuffed into the prompt.

See [ai-rag](../../ai-rag/SKILL.md) for depth on retrieval pipeline design, chunking, reranking, and evaluation. For the markdown-chunking interface this skill expects, see [markdown-chunking-patterns.md](markdown-chunking-patterns.md). For git-anchored multi-repo ingestion (RA10), see [git-anchored-ingestion.md](git-anchored-ingestion.md). For multi-repo catalog and freshness tooling, see partner skill [dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md).

## Recommended Defaults

- Start with hybrid retrieval for prose corpora.
- Add reranking before adding more index complexity.
- Keep retrieval and answer evaluation separate.
- Refuse or downgrade when evidence is missing or contradictory.
- Treat retrieved text and tool output as untrusted input.
