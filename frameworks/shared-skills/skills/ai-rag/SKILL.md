---
name: ai-rag
description: "Designs retrieval-augmented generation and search systems. Use when choosing retrieval, chunking, hybrid search, grounding, or RAG evaluation patterns."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# RAG & Retrieval Engineering

Build retrieval systems that are grounded, observable, and explicit about tradeoffs.

This skill covers:

- Retrieval architecture choice: long-context vs hosted file search vs tool-first/MCP vs SQL/graph vs classic vector RAG
- Corpus preparation: parsing, metadata, chunking, ACLs, freshness, invalidation
- Retrieval quality: sparse, dense, hybrid, late interaction, reranking, multimodal retrieval
- Answer quality: grounding, citation coverage, refusal on missing evidence, regression testing

**July 2026 posture**

- Choose the retrieval mode before tuning chunk size. A vector index is not the default answer to every knowledge problem.
- Separate retrieval quality from answer quality and evaluate both.
- Treat retrieved text, tool responses, and MCP resources as untrusted input.
- Prefer primary sources for vendor or framework recommendations; volatile facts must be verified live.
- Treat OpenTelemetry GenAI semantic conventions as useful but still evolving.
- **Context-budget note (Opus 4.7 tokenizer):** The Claude Opus 4.7 tokenizer encodes ~1.0–1.35× more tokens than the pre-2026 tokenizer for the same text. Chunk-size and token-budget heuristics from earlier than 2026 are invalid — re-measure on your own corpus with the current tokenizer before setting chunk sizes or context-window budgets.
- **Managed retrieval is a real option:** Anthropic's `web_search_20260209` (and `web_search_20250305`) server tools and OpenAI's file-search are API-native retrieval surfaces — evaluate them before building a self-hosted RAG stack. See [references/managed-retrieval-vs-self-hosted.md](references/managed-retrieval-vs-self-hosted.md).
- **Retrieval may not be the right answer at all:** if the corpus is small and stable, CAG / long-context / fine-tune may be cheaper and more reliable than RAG. Run the decision rubric in [`../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md`](../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md) before building a RAG pipeline.

**Scope note**: For generation-prompt structure and output contracts after retrieval, use [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md).

**Implementation note**: This skill owns retrieval theory and evaluation concepts. For vector-brain builds with paste-ready SQL, pgvector assets, manifests, ingest scripts, and agent retrieval tool contracts, use [ai-vector-brain](../ai-vector-brain/SKILL.md).

## ASCII Flow

```text
knowledge need
  |
  v
retrieval mode decision
  long context | hosted retrieval | tool/API | SQL/graph | hybrid search
  |
  v
corpus contract
  source truth + parsing + metadata + ACL + freshness + deletion path
  |
  v
retrieval quality loop
  baseline -> sparse/dense/hybrid -> rerank/filter/query rewrite -> eval
  |
  v
answer quality loop
  context pack + citation checks + refusal behavior + faithfulness eval
```

## Workflow

1. **Pin the authority source and freshness budget first.** Before touching a chunker or embedder, decide whether truth lives in documents, live tools, or a structured store, and how stale an answer is allowed to be. This decision, not chunk size, determines the architecture.
2. **Run the retrieval mode decision** (see Retrieval Choice Framework below) and default to the simplest mode that meets freshness, traceability, and latency — long-context, hosted file search, tool-first/MCP, and SQL/graph all beat a custom vector stack when they fit.
3. **Write the corpus contract before indexing anything**: parsing strategy, metadata schema (tenant, ACL, source, timestamp, section), freshness/invalidation rule, and a deletion path that actually propagates.
4. **Build the dumbest possible baseline first**: exact/lexical search plus a golden eval set (`scripts/exact_search_baseline.py`, `scripts/retrieval_eval.py`). Measure recall@k, MRR, nDCG before adding embeddings, hybrid fusion, or a reranker — an expert never tunes a component the eval hasn't proven necessary.
5. **Add retrieval-quality layers only when the baseline eval shows a measured gap**: hybrid (sparse+dense), reranking, query rewriting, late interaction/multivector, or multimodal retrieval, in that order of operational cost.
6. **Keep retrieval eval and answer eval as two separate gates.** A retrieval pipeline that hits recall@10 = 0.9 can still produce ungrounded answers; faithfulness, citation coverage, and abstention behavior need their own test set and their own pass/fail bar.
7. **Instrument before you scale**: evidence IDs, retrieval-mode traces, and confidence scores must exist end to end so a bad answer can be traced back to a specific retrieval decision (see observability-tracing-contract.md).
8. **Treat the eval set as a regression gate, not a one-time report.** Re-run it before every chunker, embedder, index, or reranker change, and before any vendor swap (embedding model, reranker, vector DB) — silent regressions are the most common way "working" RAG systems degrade.

## Quick Reference

| Need | Recommended path | Use when | Avoid when |
|------|------------------|----------|------------|
| Small corpus fits in context | Long-context prompt or lightweight search | Low update rate, low audit burden | Corpus is large, fast-changing, or citation-critical |
| Provider-managed retrieval | Anthropic web search tool (`web_search_20260209`) or hosted file search | Fresh web data with citations, fast start, no infra to operate | You need residency controls, custom ranking internals, or corpus isolation beyond provider defaults |
| Provider-managed file/doc retrieval | OpenAI file-search (Responses API) | Standard docs/Q&A, limited infra appetite | You need custom ranking, strict residency controls, or deep retrieval tuning |
| Provider-managed doc retrieval on AWS | AWS Bedrock Knowledge Bases | AWS-native, want managed ingestion + embedding + retrieval with IAM/residency controls | You need cross-cloud portability or custom ranking internals → references/aws-bedrock-knowledge-bases.md |
| Source of truth is tools/APIs | Tool-first or MCP retrieval | Data lives in SQL, CRM, ticketing, SaaS APIs, or internal tools | You actually need semantic retrieval over large prose corpora |
| Website or research ingestion | Crawl/extract first, then index | The source starts as websites, reports, or broad web research | You only need one-off browsing instead of a maintained retrieval system |
| Exact joins or aggregations | SQL/graph retrieval | Questions need filters, joins, counts, or relationship traversal | Natural-language corpus lookup is the main problem |
| Standard knowledge retrieval | Hybrid search + rerank | Mixed lexical + semantic queries, high recall, controllable latency | A simpler hosted or tool-first option already solves the problem |
| Generated repo/context hub corpus | Graph-bounded hybrid (graph scopes, vector recalls, rerank) | A compiled multi-repo/context hub with an existing knowledge/code graph | The corpus has no graph, or simple semantic lookup already passes eval |
| High-precision retrieval | Late interaction / multivector retrieval | Near-duplicate docs, subtle wording differences, PDF pages, multilingual precision | Latency budget is tight and BM25+dense+rering is already sufficient |
| PDFs, tables, diagrams | Multimodal document retrieval | OCR loses structure or layout meaning matters | Plain text extraction is already high quality |
| Production readiness proof | Golden eval + exact baseline + traces | You need to prove quality, not just describe architecture | One-off exploratory research with no durable corpus |

## Retrieval Choice Framework

```text
Need external knowledge?
  ├─ No -> Use direct prompting / standard prompt engineering
  └─ Yes
      ├─ Data already lives behind tools, APIs, SQL, or SaaS?
      │   └─ Start with tool-first or MCP retrieval
      │
      ├─ Corpus fits comfortably in model context and changes slowly?
      │   └─ Try long-context or hosted file search before custom indexing
      │
      ├─ Need joins, counts, or relationship traversal?
      │   └─ Use SQL, graph, or graph+vector hybrid retrieval
      │       (paradigm choice: see ../software-database-design/SKILL.md#storage-paradigm-matrix-relational-vs-graph-vs-vector)
      │
      ├─ Need fresh web data or provider-managed file search without self-hosting?
      │   └─ Evaluate managed retrieval first: Anthropic web_search_20260209 / web_search_20250305,
      │      OpenAI file-search, or other provider-native tools before building a custom stack
      │      (see references/managed-retrieval-vs-self-hosted.md for decision criteria)
      │
      ├─ Need retrieval over prose or mixed documents?
      │   └─ Use sparse+dense hybrid as the default baseline
      │
      ├─ Retrieval misses subtle matches or page-level structure?
      │   └─ Add late interaction, multivector, or multimodal retrieval
      │
      ├─ Precision still poor?
      │   └─ Add reranking, filters, query rewriting, and stronger evals
      │
      └─ Same queries keep re-running synthesis? Need a reviewable knowledge asset?
          └─ Switch from retrieval to knowledge compilation (P7 in ai-context-layer)
              Route to ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md
              Blocks A15 (RAG re-run per turn instead of compiled knowledge)
```

## Core Concepts

- **Authority source**: define whether truth comes from retrieved documents, live tools, structured databases, or a hybrid of them.
- **Trust boundary**: retrieved chunks, uploaded files, MCP resources, tool results, and web pages are untrusted until validated.
- **Freshness model**: set staleness budget, invalidation triggers, and deletion propagation rules.
- **Generated-context corpus**: a compiled multi-repo/context hub is a valid corpus; graph-bounded build path is [../ai-vector-brain/references/dev-context-hub-vector-recipe.md](../ai-vector-brain/references/dev-context-hub-vector-recipe.md).
- **Evidence contract**: return stable evidence IDs, source metadata, and enough context for later citation verification.
- **Two eval planes**: retrieval relevance and answer faithfulness are separate systems and must be measured separately.

## When NOT to Use This Skill

| Need | Route to |
|------|----------|
| Small personal knowledge base (≲100 articles / ≲400K words) where an LLM-maintained `INDEX.md` is sufficient and vector infra would be premature | [`../docs-notes-retrieval/SKILL.md`](../docs-notes-retrieval/SKILL.md) (Karpathy scale heuristic) |
| Paste-ready SQL, DDL, pgvector indexes, or backend loader scripts | [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md) |
| Building a repo/docs/compliance vector brain end to end | [`../ai-vector-brain/SKILL.md`](../ai-vector-brain/SKILL.md) |
| App context architecture, memory lifecycle, and grounding boundaries | `ai-context-layer` |
| Agent topology and tool orchestration | [`../ai-agents/SKILL.md`](../ai-agents/SKILL.md) |
| Bot UX, conversation flows, and escalation | `ai-bot-builder` |
| On-device iOS retrieval-stitch composer (Apple Foundation Models, `@Generable`, retrieval over local chunks with no-cloud guarantee) | [`../software-ios-ai-engine/SKILL.md`](../software-ios-ai-engine/SKILL.md) |
| End-to-end natural conversational iOS surface composed with this skill + `ai-context-layer` + `ai-vector-brain`, Path A (Foundation Models) and Path B (vector-DB-only) | [`../software-ios-ai-engine/references/composition-with-rag-context-vector.md`](../software-ios-ai-engine/references/composition-with-rag-context-vector.md) |
| Cross-platform natural conversation (iOS / Android / web / Telegram-Discord-WhatsApp-Slack bots / voice / backend) with or without on-device models | [`../ai-context-layer/references/conversational-surfaces-cross-platform.md`](../ai-context-layer/references/conversational-surfaces-cross-platform.md) |

## Operational Defaults

**Do**

- Start with the simplest retrieval mode that satisfies freshness, traceability, and latency.
- Keep metadata first-class: tenant, ACL, source, timestamp, page/section, language, content type.
- Probe database/search capabilities before depending on optional extensions, parser configs, generated search columns, or ANN index types in migrations.
- Stage SQL-backed RAG rollout in reversible layers: schema/RLS, minimal lexical retrieval, content seed, ranking tuning, evals, then indexed hybrid retrieval.
- Defer embeddings, ANN indexes, full-text/trigram search, and dedicated search services until an eval failure, corpus-size trigger, or measured latency problem justifies the added moving parts.
- Make retrieval deterministic where possible: fixed candidate sizes, explicit filters, bounded retries.
- Add citation coverage checks and refusal behavior when evidence is missing or conflicting.
- Keep offline eval sets versioned and run them before changing chunkers, embedders, indexes, or rerankers.

**Avoid**

- Assuming every knowledge feature needs a custom vector database.
- Hard-coding prices, benchmark rankings, or model leaderboards into durable guidance.
- Treating agentic RAG as the default for simple factual Q&A.
- Mixing tenants, corpora, or sensitivity classes without retrieval-time isolation.
- Using response caching without invalidation tied to corpus or tool freshness.

## Known Traps

- tuning chunk size, embedder, or reranker before deciding whether retrieval is even the right architecture
- using pre-2026 chunk-size or token-budget heuristics with Opus 4.7 — the tokenizer produces ~1.0–1.35× more tokens for the same text; re-measure on your own corpus
- assuming iterative/agentic multi-hop retrieval is universally superior — gains are query-distribution-dependent (strongest on chemistry-domain multi-hop; transfer to general QA is unconfirmed); measure on your own multi-hop eval set before committing to the agentic loop overhead
- shipping vector/full-text migrations before verifying the target database supports the required extensions, text-search configs, generated columns, and index operators
- mixing DDL, retrieval-function changes, and large content seeds in one migration so a search-feature failure blocks safe corpus rollout
- upgrading a small passing lexical corpus to embeddings or search infrastructure just because it is on the long-term roadmap
- reindexing synthesized reports or summaries as if they were authoritative primary evidence
- picking an embedding or reranker vendor purely off a leaderboard snapshot without checking license terms (many open-weight rerankers ship non-commercial licenses) and ownership stability (reranker/embedding vendors are consolidating via acquisition; confirm the model's roadmap and support commitment survive a vendor change before building reindex-heavy dependencies on it)
- treating retrieval recall problems and answer-faithfulness problems as one metric
- relying on hosted retrieval defaults while assuming ACL, residency, freshness, and deletion semantics are handled
- mixing tool outputs, crawled pages, uploaded files, and MCP resources without normalizing provenance and trust boundaries

## Common Anti-Patterns

See [references/quick-start-guide.md](references/quick-start-guide.md) for detailed root-cause analysis of each anti-pattern below.

- vector database first, source-of-truth model later (A2 in [`../ai-context-layer/references/anti-patterns-catalog.md`](../ai-context-layer/references/anti-patterns-catalog.md))
- agentic retrieval loops for straightforward lookup tasks
- no freshness or invalidation model for mutable corpora
- citation formatting without evidence-ID verification (A13 — provenance as optional metadata)
- cross-tenant or cross-sensitivity indexing with retrieval-time filtering bolted on later (A10)
- **RAG re-run per turn instead of compiled knowledge (A15)** — fix: switch to knowledge compilation (P7 in [`../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md`](../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md))

## Vendor Recommendation Protocol

When users ask for "best" tools, models, or frameworks:

1. Read [data/sources.json](data/sources.json) and start from sources marked `add_as_web_search: true`.
2. Verify claims against current primary docs, release notes, or official benchmarks.
3. Prefer durable guidance: retrieval mode choice, operational tradeoffs, integration constraints, evaluation and rollback plan.
4. If live browsing is unavailable, state that rankings, prices, and benchmark claims are unverified.

## Research & Ingestion Pipelines

See [references/research-and-ingestion-patterns.md](references/research-and-ingestion-patterns.md) for crawl/extract (Firecrawl-style), research loops (GPT Researcher-style), recurring data pipelines (dlt-style), and CLI evaluation workflows (simonw/llm-style). Core rule: separate crawl/extract from rank/retrieve, keep raw capture and chunks as distinct artifacts.

## Scripts

`check_sources.py` — validate sources.json · `retrieval_eval.py` — recall@k/MRR/nDCG · `check_citation_support.py` — evidence-ID verification · `generate_synthetic_rag_testset.py` — testset scaffolds · `late_interaction_eval.py` — ColBERT/ColPali offline eval (no inference runner) · `exact_search_baseline.py` — exact cosine/dot baseline · `hybrid_rrf_demo.py` — BM25-lite + vector + RRF smoke test

## When To Use This Skill

Use when the user asks about: choosing retrieval mode (file search / tools / SQL / vector RAG); designing a RAG or retrieval system; diagnosing retrieval quality; late interaction, reranking, or hybrid search; PDF, table, or diagram retrieval; grounding, citation, or faithfulness evaluation; or debugging freshness, ACL, or prompt-injection in retrieval.

## Navigation

### References (this skill)

Architecture & choice: [retrieval-choice-framework.md](references/retrieval-choice-framework.md) · [managed-retrieval-vs-self-hosted.md](references/managed-retrieval-vs-self-hosted.md) · [pipeline-architecture.md](references/pipeline-architecture.md) · [aws-bedrock-knowledge-bases.md](references/aws-bedrock-knowledge-bases.md)

Corpus & chunking: [chunking-strategies.md](references/chunking-strategies.md) · [chunking-patterns.md](references/chunking-patterns.md) · [index-selection-guide.md](references/index-selection-guide.md) · [embedding-model-guide.md](references/embedding-model-guide.md) · [research-and-ingestion-patterns.md](references/research-and-ingestion-patterns.md) · [pdf-heavy-retrieval-playbook.md](references/pdf-heavy-retrieval-playbook.md)

Retrieval patterns: [retrieval-patterns.md](references/retrieval-patterns.md) · [vector-search-patterns.md](references/vector-search-patterns.md) · [hybrid-fusion-patterns.md](references/hybrid-fusion-patterns.md) · [bm25-tuning.md](references/bm25-tuning.md) · [graph-rag-patterns.md](references/graph-rag-patterns.md) · [contextual-retrieval-guide.md](references/contextual-retrieval-guide.md) · [advanced-rag-patterns.md](references/advanced-rag-patterns.md) · [agentic-rag-patterns.md](references/agentic-rag-patterns.md)

Ranking & query: [ranking-pipeline-guide.md](references/ranking-pipeline-guide.md) · [query-rewriting-patterns.md](references/query-rewriting-patterns.md) · [backend-comparison-fixtures.md](references/backend-comparison-fixtures.md)

Grounding & eval: [grounding-checklists.md](references/grounding-checklists.md) · [confidence-scoring.md](references/confidence-scoring.md) · [abstention-recipe.md](references/abstention-recipe.md) · [rag-evaluation-guide.md](references/rag-evaluation-guide.md) · [search-evaluation-guide.md](references/search-evaluation-guide.md)

Ops & debugging: [observability-tracing-contract.md](references/observability-tracing-contract.md) · [retrieval-debugging-runbook.md](references/retrieval-debugging-runbook.md) · [rag-troubleshooting.md](references/rag-troubleshooting.md) · [search-debugging.md](references/search-debugging.md) · [rag-caching-patterns.md](references/rag-caching-patterns.md) · [distributed-search-slos.md](references/distributed-search-slos.md) · [user-feedback-learning.md](references/user-feedback-learning.md) · [multilingual-domain-patterns.md](references/multilingual-domain-patterns.md) · [security-red-team-cases.md](references/security-red-team-cases.md)

Onboarding: [quick-start-guide.md](references/quick-start-guide.md) - workflow, full template index, detailed anti-patterns · [wiki-grounded-retrieval.md](references/wiki-grounded-retrieval.md)

### Cross-Skill References

- [`../ai-context-layer/references/anti-patterns-catalog.md`](../ai-context-layer/references/anti-patterns-catalog.md) - A2, A10, A13, A15 anti-patterns referenced throughout this skill
- [`../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md`](../ai-context-layer/references/retrieve-vs-preload-vs-finetune.md) - Decision rubric: RAG vs long-context vs fine-tune
- [`../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md`](../ai-context-layer/references/knowledge-compilation-and-wiki-pattern.md) - P7 pattern for compiled knowledge (A15 fix)
- [`../ai-vector-brain/references/dev-context-hub-vector-recipe.md`](../ai-vector-brain/references/dev-context-hub-vector-recipe.md) - Graph-bounded build path for generated-context corpora
- [`../software-ios-ai-engine/references/composition-with-rag-context-vector.md`](../software-ios-ai-engine/references/composition-with-rag-context-vector.md) - iOS conversational RAG composition

### External Sources

- [data/sources.json](data/sources.json) - Primary-source catalog for live verification

## Related Skills

Gate before invoking: each foundation has a `When to Apply` / `When to Skip` section.

- **[ai-evals](../ai-evals/SKILL.md)** - LLM-judge bias control and reproducibility for faithfulness/answer evals
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Retrieval-grounded prompt contracts and structured outputs
- **[ai-agents](../ai-agents/SKILL.md)** - Agent orchestration and tool workflows
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment, monitoring, and governance
- **[ai-llm-inference](../ai-llm-inference/SKILL.md)** - Latency, batching, caching, and cost controls
- **[docs-notes-retrieval](../docs-notes-retrieval/SKILL.md)** - Local note-vault and notebook-export packaging for retrieval
- **[foundations-information-theory](../foundations-information-theory/SKILL.md)** - Entropy, mutual information, and KL divergence for chunk scoring, MMR diversity, and drift detection

## Fact-Checking

Verify bugs, framework footguns, and version-specific guidance against current primary web sources. Use web search for current vendor capabilities, prices, benchmarks, and release status. Mark unverified claims explicitly if live browsing is unavailable.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present). After applying it, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
