# Managed Retrieval vs Self-Hosted RAG

**Stance:** evaluate managed retrieval first; re-check the vendor docs before citing any row below.

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

**Look up before citing (platform.claude.com/docs, tool-use reference).** Tool type strings are dated and versioned, and model support, platform parity, and pricing change often, so this file pins none of them. Check:

| Question | Why it matters |
|---|---|
| Which versioned web-search tool type is current, and which older versions still work? | Code pinned to a retired version fails at request time |
| Does the current version support dynamic filtering (the model filters results with code before they enter context)? | Filtering cuts token cost and raises precision |
| Which models and which platforms (Claude API, cloud marketplaces) support it? | Platform parity lags; some clouds offer basic search only or none |
| Per-search price and how result content is billed | Search results count as input tokens on top of the per-search fee |

**RAG use case:** Use when the knowledge source is the live web — news, current documentation, real-time prices, regulatory updates. Citations are automatic. Not suitable for retrieval over a private corpus.

**Relevant configuration parameters:**
- `max_uses` — cap searches per request to control cost
- `allowed_domains` / `blocked_domains` — restrict retrieval surface
- `user_location` — localize results

## Hosted File Search (OpenAI and Equivalents)

> **Target the Responses API + Vector Store API for hosted file search, not the Assistants API.** The Assistants API that used to host the file-search tool is deprecated; check the OpenAI deprecations page for its status and migrate any code that still targets it. Canonical docs: [platform.openai.com/docs/guides/file-search](https://platform.openai.com/docs/guides/file-search) (Responses API).

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
| Vector store choice | Several managed backends, incl. the cost-optimized **S3 Vectors** (check current backend list and pricing) | Any backend |
| Chunking modes | Semantic / hierarchical / fixed (custom via Lambda) | Full control (incl. code-aware) |
| Citation surface | Source attribution + score, KB-managed | DIY (`grounding-checklists.md`) |
| Confidence + abstention | Not first-class; build into prompt | First-class (`confidence-scoring.md`, `abstention-recipe.md`) |
| Cross-cloud | AWS-only | Portable |
| Co-locate with agent | Native with AgentCore + Bedrock Agents | Via API |
| Cold start | Hours | Days–weeks |

**Default AWS recipe:** Bedrock KB on S3 Vectors. Upgrade vector store only when latency or co-location demands.

Deep dive: [aws-bedrock-knowledge-bases.md](aws-bedrock-knowledge-bases.md) for the full vector-store decision matrix; [`../../ai-vector-brain/references/s3-vectors-backend.md`](../../ai-vector-brain/references/s3-vectors-backend.md) for S3 Vectors specifically.

## Self-Hosted RAG — When It Is the Right Call

Choose self-hosted when:
- Residency or data-sovereignty requirements preclude provider ingestion
- You need custom ranking (domain-specific reranker, BM25 tuning, RRF weight sweep)
- Multi-tenant ACL with row-level isolation across sensitivity classes
- Deep retrieval tuning is justified by eval failure on managed baseline
- Corpus poisoning risk calls for hybrid retrieval (BM25+dense), which raises attack cost but is not a complete defense (see security-red-team-cases.md)
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
- [ ] Check platform availability: web search is not offered on every cloud platform; verify current platform support before citing
