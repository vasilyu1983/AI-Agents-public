# AWS Bedrock Knowledge Bases (Managed RAG)

Amazon Bedrock Knowledge Bases is AWS's fully-managed RAG service: ingestion → chunking → embedding → vector store → retrieval → citation, with session context and source attribution built in. It is the AWS peer to Anthropic's `web_search` server tool and OpenAI's file-search.

Use it when you want a production RAG path without building the pipeline yourself, and AWS is your platform.

---

## Table of Contents

- [When Bedrock KB is the right answer](#when-bedrock-kb-is-the-right-answer)
- [What the service does end-to-end](#what-the-service-does-end-to-end)
- [Guardrails](#guardrails)
- [Vector store decision matrix](#vector-store-decision-matrix)
- [Chunking modes](#chunking-modes)
- [Multimodal + structured-data retrieval](#multimodal--structured-data-retrieval)
- [Bedrock KB vs self-hosted RAG](#bedrock-kb-vs-self-hosted-rag)
- [Composition with AgentCore and Bedrock Agents](#composition-with-agentcore-and-bedrock-agents)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

---

## When Bedrock KB is the right answer

ALL of these:

1. **AWS is the platform.** You are deploying on AWS or have data residency constraints favoring AWS regions.
2. **You want the pipeline managed.** You'd rather configure than build chunking, embedding, vector storage, retrieval, and citation yourself.
3. **The vector-store options fit.** At least one of S3 Vectors / Aurora pgvector / OpenSearch Serverless / Neptune Analytics / Pinecone / MongoDB / Redis is acceptable.
4. **You can live with the chunking modes available.** Semantic, hierarchical, or fixed-size. Custom chunking is possible but moves you toward self-hosted.

If you need code-aware chunking, custom rerankers not in the AWS catalog, or cross-cloud portability — self-host with `ai-rag` patterns and `ai-vector-brain`.

---

## What the service does end-to-end

```text
DATA SOURCES (S3, Confluence, SharePoint, Salesforce, web crawl, custom)
   ↓ ingest (automatic)
NORMALIZATION + CHUNKING (semantic / hierarchical / fixed)
   ↓
EMBEDDING (Amazon Nova 2 Multimodal Embeddings [AWS-native default, 2026], Cohere, Titan [legacy], other Bedrock-hosted models)
   ↓
VECTOR STORE (S3 Vectors / Aurora / OpenSearch / Neptune / Pinecone / Mongo / Redis)
   ↓
RETRIEVE (RetrieveAPI) or RetrieveAndGenerate (with Bedrock LLM)
   ↓
CITATIONS (source attribution + chunk lineage)
```

You configure each stage. AWS runs it. Amazon Nova 2 Multimodal Embeddings is the AWS-native default embedder for new KB builds; Titan Embeddings is legacy. Nova 2 supports Matryoshka dimensions (3072/1024/384/256), 8192-token context, and 200 languages. For scanned or form-heavy S3 documents, **Bedrock Data Automation (BDA)** is the AWS-recommended intelligent document processing front door (one API classifies + extracts via foundation models, flat per-doc pricing, Textract as its OCR layer for complex docs in "Bedrock Pipeline" mode); standalone Amazon Textract (forms/tables, multi-page structure) remains best for high-volume standardized document formats (~75% cheaper per doc on standardized formats, ~95%+ compliance accuracy).

---

## Managed retriever: Amazon Kendra GenAI Index

Amazon Kendra GenAI Index is a managed retriever offering hybrid keyword + vector search, semantic ranking, and a built-in reranker. It can be indexed once and reused across **both** Amazon Bedrock Knowledge Bases and Amazon Q Business — Bedrock KB can be configured to sit on top of it instead of a raw vector store. This is AWS's production enterprise-RAG stack: **Kendra GenAI Index + Retriever API + Bedrock FM**.

Use Kendra GenAI Index when:

- You need one retriever shared between agent (Bedrock KB) and enterprise-search (Q Business) surfaces.
- The corpus requires built-in semantic reranking without managing a separate reranker.
- Cross-department access controls (IAM, SAML) need to be enforced at the retriever layer.

Use a plain vector store (S3 Vectors, OpenSearch, etc.) when cost matters most and you don't need Q Business sharing or built-in reranking.

## Native reranking (Bedrock Rerank API)

**Amazon Bedrock Rerank API** (June 2026) wires reranking directly into KB retrieval without a separate service. Available models: **Cohere Rerank 3.5** and **Amazon Rerank**. This replaces the need to call an external reranker after `Retrieve`. Note: Cohere Command R/R+ are now legacy; the active Cohere surface in Bedrock is Embed v3/v4 + Rerank 3.5.

Use Bedrock Rerank when:

- You are already on Bedrock KB and want reranking without adding a self-hosted or third-party reranker.
- You need a single AWS API surface (retrieve + rerank in one call).

If you need a custom reranker or a non-AWS reranker (Jina, Zerank, Voyage), self-host or use the external API and skip the Bedrock Rerank API.

---

## Guardrails

Amazon Bedrock Guardrails is the AWS-native safety and governance layer. It integrates natively with the `RetrieveAndGenerate` API and is also callable model-independently via the standalone `ApplyGuardrail` API.

Six safeguards:

| Safeguard | What it does |
|---|---|
| **Content moderation** | Blocks harmful or off-policy output categories |
| **Prompt-attack detection** | Detects and blocks prompt injection attempts |
| **Denied-topics policy** | Refuses responses on explicitly prohibited topics |
| **PII redaction** | Redacts or anonymizes built-in entity types + custom regex at input or output |
| **Contextual grounding check** | Scores each response for grounding against retrieved chunks and relevance to the query; responses below either threshold are blocked (see below) |
| **Automated Reasoning** | Mathematically verifiable claim checking; catches hallucinations that LLM judges miss |

**Contextual grounding check — the RAG-critical safeguard.** It scores two dimensions independently: (a) grounding — how well the response is supported by the retrieved reference chunks, and (b) relevance — how well the response addresses the query. Each dimension has its own threshold; a response is blocked if either score falls below its threshold. This is the AWS-managed hallucination/faithfulness gate for RAG pipelines — critical for legal, financial, and compliance KBs where ungrounded answers cause direct harm. Wire it at the `RetrieveAndGenerate` layer; it fires after generation, before the response is returned.

**PII redaction** applies at the output layer — strip or anonymize sensitive entities before the response reaches the caller. Useful when the corpus contains personal data and the retrieval surface is multi-tenant.

**ApplyGuardrail API** lets you apply the same guardrail to any model output, not just Bedrock-hosted calls — useful for consistency when the generation model is self-hosted or cross-cloud.

For self-hosted equivalents: [`grounding-checklists.md`](grounding-checklists.md) (faithfulness enforcement patterns), [`confidence-scoring.md`](confidence-scoring.md) (scoring), [`abstention-recipe.md`](abstention-recipe.md) (abstain when grounding score is low). On AWS, Guardrails contextual grounding check is the managed enforcement layer for these patterns.

---

## Vector store decision matrix

| Backend | Best for | Cost shape | Latency | When to pick |
|---|---|---|---|---|
| **S3 Vectors** | Cost-optimized RAG at scale; cold or rarely-queried corpora | ~**90% cheaper** than alternatives | ~100ms warm, sub-second cold | Default for new builds. Trillions of vectors. Pick first; upgrade only if latency-bound |
| **Aurora pgvector** | Transactional data + vectors together; existing Postgres estate | Aurora pricing | Low | Already on Aurora; co-locate vectors with relational |
| **OpenSearch Serverless** | Low-ops managed search + vector | Pay-per-OCU | Low–medium | Hybrid BM25 + vector workloads, full-text + vector co-resident |
| **OpenSearch Managed Cluster** | Full control over OpenSearch tuning | Cluster instance pricing | Tunable | Need cluster-level knobs (custom plugins, replicas, sharding) |
| **Neptune Analytics** | Graph + vector co-resident — GraphRAG patterns | Neptune pricing | Low | H4 (GraphRAG) workloads, relationship reasoning |
| **Pinecone** | Existing Pinecone investment; multi-cloud | Pinecone SaaS pricing | Low | Cross-cloud team using Pinecone elsewhere |
| **MongoDB Atlas** | Existing MongoDB; document model + vectors | Atlas pricing | Low–medium | Already on MongoDB; want one store |
| **Redis Enterprise Cloud** | Low-latency tier-1 retrieval | Redis pricing | Very low | Sub-50ms p99 is mandatory |

**Default recommendation 2026:** start with **S3 Vectors**. The ~90% cost reduction is large enough that you should explicitly justify any other choice. Move up the matrix only if latency or co-location demands it. Detail in [`../../ai-vector-brain/references/s3-vectors-backend.md`](../../ai-vector-brain/references/s3-vectors-backend.md).

---

## Chunking modes

| Mode | What it does | When to pick |
|---|---|---|
| **Fixed-size** | Token-count slices with overlap | Uniform prose corpora; baseline |
| **Hierarchical** | Parent–child chunks; embed children, return parents | Long documents where context matters at multiple scales (regulations, contracts) |
| **Semantic** | Boundary detection by embedding similarity | Heterogeneous corpora; clean paragraph breaks |
| **Custom** | Lambda-based chunking before ingest | Code, structured data, anything the modes above can't handle |

Cross-references: [`chunking-strategies.md`](chunking-strategies.md), [`chunking-patterns.md`](chunking-patterns.md), [`markdown-chunking-patterns.md`](../../ai-context-layer/references/markdown-chunking-patterns.md).

For code corpora (H1 scenarios), custom chunking is almost always required — fixed-size and semantic both produce sub-symbol fragments. Use a Lambda pre-processor or self-host.

---

## Multimodal + structured-data retrieval

Two newer capabilities worth knowing:

- **Multimodal KBs** — embed and retrieve images alongside text. Useful for H5 (multimodal RAG) when corpus has figures, charts, diagrams co-located with text.
- **Structured-data retrieval** — query tabular data (CSV, database tables) with natural language, returning rows with citations. Useful for finance, ops, and analytics surfaces where the answer is a row not a paragraph.

Both are still maturing in mid-2026 — verify limits against the corpus you have before committing.

---

## Bedrock KB vs self-hosted RAG

| Decision | Bedrock KB | Self-hosted (`ai-rag` + `ai-vector-brain`) |
|---|---|---|
| Time-to-production | Days | Weeks |
| Customization | Limited (chunking modes, AWS-cataloged embedding/rerankers) | Full |
| Code-aware chunking | Needs custom Lambda | Direct (`dev-context-code-graph`) |
| Cross-cloud portability | None | Full |
| Cost | Per-token retrieve + per-query + storage | Storage + compute (often cheaper at scale, more ops) |
| Confidence scoring | Built-in source attribution + score | DIY ([`confidence-scoring.md`](confidence-scoring.md)) |
| Abstention | Not first-class; build in prompt | First-class ([`abstention-recipe.md`](abstention-recipe.md)) |
| Evaluations | Pair with AgentCore Evaluations (13 evaluators) | DIY ([`rag-evaluation-guide.md`](rag-evaluation-guide.md)) |
| Eval set discipline | Still needed | Still needed |

Rule of thumb: **start with Bedrock KB** for the first AWS RAG, **graduate to self-hosted** when you hit a customization wall. The most common walls are: code-aware chunking, custom reranker, cross-cloud, or aggressive cost optimization at very high query volume.

---

## Composition with AgentCore and Bedrock Agents

| Pairing | Pattern |
|---|---|
| **AgentCore + Bedrock KB** | Agent calls `Retrieve` on KB inside a Runtime session; result enters context. Memory layer (per-user state) separate from KB (corpus retrieval). |
| **Bedrock Agents (classic) + Bedrock KB** | Configuration-only: bind KB to the classic agent. Fastest path; least flexible. |
| **AgentCore + Bedrock KB + S3 Vectors** | Cost-minimal AWS-native production RAG agent. |
| **AgentCore + Bedrock KB + Neptune Analytics** | GraphRAG (H4) on AWS. Graph + vector co-resident, agent traverses. |
| **AgentCore Gateway + Bedrock KB** | Expose KB retrieve as an MCP tool callable by non-Bedrock agents (Claude, GPT, Copilot via MCP). |

The H scenarios in `router-engineering/references/engineering-scenarios.md` are platform-agnostic. Bedrock KB is the AWS implementation:

- H2 (Company-Wiki RAG) → Bedrock KB on S3 Vectors or OpenSearch
- H4 (GraphRAG) → Bedrock KB on Neptune Analytics
- H5 (Multimodal RAG) → Bedrock KB multimodal mode + S3 Vectors
- H6 (Compliance RAG) → Bedrock KB on hierarchical chunking + Aurora + AgentCore Policy

---

## Anti-patterns

- **A-BKB-1 — Pick Bedrock KB before checking if RAG is the right answer at all.** Run [`../../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md`](../../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md) first. For a 50K-token stable corpus, CAG (I1) is simpler and cheaper.
- **A-BKB-2 — Default to OpenSearch Serverless or Pinecone "because that's what we know."** S3 Vectors is ~90% cheaper at comparable latency for most workloads. Justify the upgrade, don't assume.
- **A-BKB-3 — Skip evals because "it's managed."** Managed pipeline doesn't mean managed correctness. Build the eval set ([`rag-evaluation-guide.md`](rag-evaluation-guide.md)) and gate corpus refreshes on it.
- **A-BKB-4 — Use the fixed-size chunking default on a regulation/contract corpus.** Use hierarchical. Otherwise you lose clause hierarchy and your citations are useless for audit.
- **A-BKB-5 — Build code RAG on stock Bedrock KB chunking.** Code needs symbol-aware chunking. Use a custom Lambda chunker or self-host.
- **A-BKB-6 — Mix Bedrock KB sources without authority discipline.** Multiple data sources merged into one KB without per-source authority weights makes the loudest source win. Run multiple KBs scoped by authority, or self-host where you control the weights ([`confidence-scoring.md`](confidence-scoring.md)).
- **A-BKB-7 — Treat AgentCore Memory and Bedrock KB as interchangeable.** Memory = per-user state. KB = corpus retrieval. They are different patterns.

---

## Related

- [managed-retrieval-vs-self-hosted.md](managed-retrieval-vs-self-hosted.md) — broader comparison: Bedrock KB vs Anthropic web_search vs OpenAI file-search vs self-hosted
- [`../../ai-vector-brain/references/s3-vectors-backend.md`](../../ai-vector-brain/references/s3-vectors-backend.md) — Default vector backend on AWS in 2026
- [`../../software-paas-hosting/references/aws-bedrock-agentcore.md`](../../software-paas-hosting/references/aws-bedrock-agentcore.md) — Agent platform that composes with KB
- [graph-rag-patterns.md](graph-rag-patterns.md) — Neptune Analytics as GraphRAG backend
- [confidence-scoring.md](confidence-scoring.md), [abstention-recipe.md](abstention-recipe.md) — Quality gates KB does not provide first-class
- [`../../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md`](../../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md) — Decision before picking KB at all
- AWS docs: [Knowledge Bases overview](https://aws.amazon.com/bedrock/knowledge-bases/), [How it works](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-it-works.html), [S3 Vectors integration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html), [OpenSearch Managed Cluster support](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-amazon-opensearch-service-managed-cluster-as-vector-store/), [Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
