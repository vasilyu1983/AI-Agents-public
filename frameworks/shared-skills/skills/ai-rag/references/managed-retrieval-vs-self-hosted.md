# Managed Retrieval vs Self-Hosted RAG

**Stance: July 2026 (re-verified)**

Before building a self-hosted retrieval stack, evaluate provider-managed retrieval surfaces. They cover the majority of standard docs/Q&A and web-grounding use cases with no infrastructure to operate.

## Table of Contents

- [Decision Node](#decision-node)
- [Anthropic Web Search Tool](#anthropic-web-search-tool)
- [Hosted File Search (OpenAI and Equivalents)](#hosted-file-search-openai-and-equivalents)
- [AWS Bedrock Knowledge Bases](#aws-bedrock-knowledge-bases)
- [Self-Hosted RAG - When It Is the Right Call](#self-hosted-rag--when-it-is-the-right-call)
- [Anti-Patterns](#anti-patterns)
- [Verification Before Choosing Managed](#verification-before-choosing-managed)

## Decision Node

```text
Do you need retrieval?
  |
  ├─ Fresh web data, citations, real-time grounding?
  │   └─ Anthropic web search tool (see below) — managed, no corpus to maintain
  │
  ├─ Retrieval over your own documents (PDFs, support docs, knowledge base)?
  │   ├─ Standard ranking acceptable, low infra appetite?
  │   │   └─ Hosted file search (OpenAI file-search or equivalent) — managed vector store
  │   └─ Custom ranking, residency controls, strict ACL, corpus isolation?
  │       └─ Self-hosted RAG — hybrid sparse+dense + reranker
  │
  └─ You need both fresh web data AND retrieval over your own docs?
      └─ Combine: web search tool for live data + hosted/self-hosted for corpus
```

## Anthropic Web Search Tool

**Current versions (re-verified July 2026, source: platform.claude.com/docs):**

| Tool type string | Status | Capability |
|---|---|---|
| `web_search_20260209` | Current, recommended | Dynamic filtering: model writes and executes code to filter search results before they enter context; reduces token cost and improves precision. Requires code execution tool. |
| `web_search_20250305` | Available, no dynamic filtering | Basic web search with `max_uses`, `allowed_domains`, `blocked_domains`, `user_location` |

**Supported models for `web_search_20260209`:** Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 4.6, Claude Mythos Preview.

**Platform availability:** Claude API, Claude Platform on AWS, Microsoft Foundry. Not on Amazon Bedrock. Vertex AI supports `web_search_20250305` only (no dynamic filtering).

**Pricing:** $10 per 1,000 searches plus standard token costs for search-generated content. Search result content counts as input tokens.

**RAG use case:** Use when the knowledge source is the live web — news, current documentation, real-time prices, regulatory updates. Citations are automatic. Not suitable for retrieval over a private corpus.

**Relevant configuration parameters:**
- `max_uses` — cap searches per request to control cost
- `allowed_domains` / `blocked_domains` — restrict retrieval surface
- `user_location` — localize results

## Hosted File Search (OpenAI and Equivalents)

> **Deprecation notice (April 2026):** The OpenAI Assistants API — which previously hosted the file-search tool — is deprecated as of April 2026 with shutdown scheduled for **August 26, 2026**. New work must use the **Responses API + Vector Store API** for hosted file search. If you are on the Assistants API today, migrate before the shutdown date. Canonical docs: [platform.openai.com/docs/guides/file-search](https://platform.openai.com/docs/guides/file-search) (Responses API).

Use when:
- Documents are your own (PDFs, markdown, support articles)
- Standard retrieval quality is acceptable
- You want to skip embedding pipeline, index management, and vector DB operations
- Citation granularity at the chunk level is sufficient

Tradeoffs vs self-hosted:

| Dimension | Managed | Self-hosted |
|---|---|---|
| Ranking control | Provider defaults | Full — custom reranker, RRF weights |
| Corpus residency | Provider-controlled | Your infrastructure |
| Freshness latency | Depends on provider update SLA | You control index refresh |
| ACL and multi-tenancy | Provider scheme | Custom RLS and filter enforcement |
| Citation fidelity | Provider citation format | Custom evidence-ID scheme |
| Cold start | Hours not days | Days to weeks for full stack |
| Cost model | Per-request or per-storage | Infrastructure + embedding + serving |

## AWS Bedrock Knowledge Bases

Use when:
- AWS is the platform (deployment, data residency, IAM integration)
- You want managed RAG with a choice of vector store: S3 Vectors (cost-optimized default), Aurora pgvector, OpenSearch Serverless/Managed, Neptune Analytics (graph+vector), Pinecone, MongoDB, Redis
- Multimodal (image+text) or structured-data (tabular) retrieval is in scope
- You'll pair with AgentCore or Bedrock Agents (classic) for the agent side

Tradeoffs vs self-hosted:

| Dimension | Bedrock KB | Self-hosted |
|---|---|---|
| Vector store choice | 7 backends (incl. **S3 Vectors** at ~90% cost reduction) | Any backend |
| Chunking modes | Semantic / hierarchical / fixed (custom via Lambda) | Full control (incl. code-aware) |
| Citation surface | Source attribution + score, KB-managed | DIY (`grounding-checklists.md`) |
| Confidence + abstention | Not first-class; build into prompt | First-class (`confidence-scoring.md`, `abstention-recipe.md`) |
| Cross-cloud | AWS-only | Portable |
| Co-locate with agent | Native with AgentCore + Bedrock Agents | Via API |
| Cold start | Hours | Days–weeks |

**Default 2026 AWS recipe:** Bedrock KB on S3 Vectors. Upgrade vector store only when latency or co-location demands.

Deep dive: [aws-bedrock-knowledge-bases.md](aws-bedrock-knowledge-bases.md) for the full vector-store decision matrix; [`../../ai-vector-brain/references/s3-vectors-backend.md`](../../ai-vector-brain/references/s3-vectors-backend.md) for S3 Vectors specifically.

## Self-Hosted RAG — When It Is the Right Call

Choose self-hosted when:
- Residency or data-sovereignty requirements preclude provider ingestion
- You need custom ranking (domain-specific reranker, BM25 tuning, RRF weight sweep)
- Multi-tenant ACL with row-level isolation across sensitivity classes
- Deep retrieval tuning is justified by eval failure on managed baseline
- Corpus poisoning risk requires hybrid retrieval (BM25+dense) as an architectural defense (see security-red-team-cases.md)
- Evidence IDs must be stable and traceable to your own provenance model

## Anti-Patterns

- Building a self-hosted vector stack for a use case where the Anthropic web search tool would have shipped in a day
- Using managed retrieval for private regulated corpora without verifying residency guarantees
- Mixing managed web search results and self-hosted corpus chunks without normalizing provenance trust levels
- Assuming managed retrieval handles ACL, deletion, and freshness automatically — verify provider guarantees explicitly

## Verification Before Choosing Managed

- [ ] Confirm the provider's data residency and retention policy matches your requirements
- [ ] Verify deletion propagation (tombstones, right-to-be-forgotten)
- [ ] Test citation fidelity against your expected source types
- [ ] Confirm ACL and multi-tenant isolation meets your threat model
- [ ] Check domain availability: web search is not available on all platforms (Bedrock excluded as of July 2026)
