# Agentic RAG Patterns

**Stance: May 2026**

Agentic RAG is a conditional pattern, not the default baseline.

Use it when fixed retrieval pipelines fail because the task needs decomposition, adaptive retrieval, verification, or tool orchestration.

**Multi-hop qualifier:** Evidence for agentic/iterative retrieval superiority is query-distribution-dependent. The strongest published finding (arXiv 2601.19827, chemistry domain) shows gains of up to +25.6pp on multi-hop questions in that domain. Transfer to general-domain QA is not confirmed. Measure on your own multi-hop eval set before committing to the agentic loop overhead — do not assert a blanket win over single-shot retrieval.

## Table of Contents

- [When Agentic RAG Is Worth It](#when-agentic-rag-is-worth-it)
- [When A Simpler Pipeline Is Better](#when-a-simpler-pipeline-is-better)
- [Iterative Retrieval Beats Oracle Context on Multi-Hop Questions (grade B, preprint, narrow domain)](#iterative-retrieval-beats-oracle-context-on-multi-hop-questions-grade-b-preprint-narrow-domain)
- [Retrieve → Reason → Re-Retrieve Loop](#retrieve--reason--re-retrieve-loop)
- [Query Planning](#query-planning)
- [Patterns](#patterns)
- [Agentic RAG Evaluation](#agentic-rag-evaluation)
- [Guardrails](#guardrails)
- [Cross-References](#cross-references)

## When Agentic RAG Is Worth It

- Ambiguous queries that need clarification or reformulation
- Multi-hop or comparative questions that require several retrieval passes
- High-stakes answers that need a verification loop before final output
- Workflows that must combine retrieval with tools, APIs, or graph traversal

## When A Simpler Pipeline Is Better

- Straightforward FAQ or policy lookup
- Low-latency chat experiences
- Corpora with high-quality metadata and stable retrieval performance
- Cases where BM25 + dense + rerank already meets eval targets

## Iterative Retrieval Beats Oracle Context on Multi-Hop Questions (grade B, preprint, narrow domain)

**Evidence grade B** — arXiv 2601.19827 (Jan 2026, preprint). Study used 11 LLMs on ChemKGMultiHopQA (chemistry knowledge graph), so results are domain-specific; treat as directional, not universal.

Key finding: iterative retrieve-and-refine (agentic loop) outperformed providing the full gold/oracle context in a single pass:

- Non-reasoning models: up to **+25.6 percentage points** improvement
- Reasoning models: up to **~+9.7 percentage points** improvement

**Implication for "when is agentic RAG worth it":**

| Query type | Recommendation |
|---|---|
| Multi-hop (≥2 retrieval steps required) | Iterative agentic loop — evidence supports clear gains |
| Single-hop / simple lookup | Fixed pipeline — agentic overhead not justified |
| Long-context packing of all candidates | See long-context hard-negative degradation note in retrieval-choice-framework.md |

Do not generalize these gains beyond multi-hop without domain-specific evaluation. The chemistry-domain setting means transfer to general QA is not confirmed.

## Retrieve → Reason → Re-Retrieve Loop

The core agentic RAG cycle. Unlike single-shot retrieve-then-read, the agent interleaves retrieval and reasoning — using intermediate model outputs to refine subsequent queries.

```text
Query
  -> query planning (decompose if multi-hop; classify intent)
  -> retrieve (keyword / semantic / tool)
  -> reason over evidence
  -> evaluate: is evidence sufficient?
      yes -> generate with citations -> verify -> answer
      no  -> reformulate sub-query (backtrack if depth limit reached)
           -> re-retrieve (new query or different retrieval mode)
           -> merge evidence with provenance tracking
  -> repeat up to depth limit
  -> fallback: refuse or surface uncertainty if depth exhausted
```

**Depth and budget limits are mandatory.** An unbounded re-retrieve loop will spiral in latency and token cost without converging on a better answer.

## Query Planning

Query planning is the step where the agent decides, before first retrieval, whether and how to decompose the incoming question.

| Query type | Planning action |
|---|---|
| Simple factual lookup | No decomposition — single retrieval |
| Comparative ("A vs B") | Decompose into two independent retrievals; merge |
| Multi-hop (answer to Q1 is input to Q2) | Sequential sub-questions; pass intermediate answer as context |
| Aggregation (count, summarize across docs) | Retrieve all candidates first; aggregate after |
| Ambiguous intent | Clarify or generate candidate interpretations before retrieval |

**A-RAG approach (arXiv 2602.03442, verified):** Provides the model with multiple retrieval tools at different granularities (keyword search, semantic search, chunk reading) rather than a single retrieve-all call. This allows the agent to choose the right retrieval surface per sub-question and adaptively decide what information to retrieve and at what level of detail. The paper reports improvements on open-domain QA benchmarks while using comparable or fewer retrieved tokens than fixed-pipeline approaches.

## Patterns

### 1. Adaptive Retrieval

Choose between direct answer, retrieval, tool call, or clarification based on intent and freshness needs.

### 2. Self-Correcting Retrieval

Run a second retrieval attempt only when evidence quality is measurably poor. Do not retry blindly.

### 3. Multi-Hop Decomposition

Break a complex query into sub-questions, retrieve independently, then merge evidence with explicit provenance.

### 4. Verification Loop

After generation, check that every important claim maps to a retrieved or tool-derived evidence object.

### 5. Query-Planning-First

Before any retrieval: classify intent, decompose if multi-hop, select retrieval mode per sub-question. Emit the plan before executing it — enables interruption and logging.

### 6. Adaptive RAG

The standard 2026 production deployment pattern in LlamaIndex and LangGraph stacks. A query classifier routes each incoming question to the cheapest retrieval tier that can answer it correctly:

| Query tier | Routing decision | Retrieval action |
|---|---|---|
| Trivial / self-contained | No retrieval needed | Direct answer from model |
| Single-hop factual | Plain vector retrieval | Single-pass dense + rerank |
| Multi-hop / compositional | Iterative agentic loop | Decompose, retrieve per sub-question, merge |
| Ambiguous intent | Clarify first | Prompt user before retrieving |

**Why it matters:** routing every query through the same pipeline wastes latency and tokens on simple questions while underserving multi-hop ones. The classifier (a lightweight LLM call or a fine-tuned classifier) amortizes cheaply across the full query distribution.

This pattern is consistent with the "measure on your distribution" framing throughout this file: the classifier is trained or prompted on your actual query mix, not a benchmark. Do not hard-code the routing thresholds — observe the distribution and adjust. In LlamaIndex, `RouterQueryEngine` with a `LLMSingleSelector` is the canonical implementation surface. In LangGraph, a conditional edge from a `classify_query` node implements the same routing.

## RAFT: Retrieval-Augmented Fine-Tuning

RAFT fine-tunes a model on (question, distractor documents, gold document, chain-of-thought answer) tuples so it learns to reason over retrieved content and ignore distractors — combining RAG freshness with fine-tune precision.

**When to use:**

- Domain-specific QA where the model consistently fails to reason over retrieved documents
- Corpus is stable enough to justify fine-tuning compute; corpus does not change weekly
- You can afford labeled (or synthetic) training data generation over the target domain
- Distractors in retrieval are a known failure mode and standard reranking is insufficient

**When not to use:**

- Corpus changes frequently — retraining would be required to keep the model current
- General-domain QA where RAG + reranking already meets eval targets
- Low-resource setting with no labeling budget or GPU access
- Off-the-shelf instruct model already handles retrieval reasoning at acceptable quality

## Corrective RAG (CRAG)

**Paper:** arXiv 2401.15884

CRAG adds a retrieval evaluator that scores retrieved documents after each retrieval step. When confidence is low, the system automatically re-queries or falls back to web search before passing context to the generator.

**Decision checklist:**

- [ ] Retrieval quality varies significantly across query types or sub-topics
- [ ] Web search fallback is permissible (data residency and trust model allow it)
- [ ] A lightweight retrieval evaluator (classifier or LLM-judge) is available and cost-acceptable
- [ ] Latency budget accommodates a second retrieval pass on low-confidence cases
- [ ] Fallback source trust boundary is defined (web content is untrusted; normalize before packing)
- [ ] Retry limit is bounded to prevent infinite re-query loops

## Guardrails

- Bound retries and traversal depth
- Log each reformulation and retrieval decision
- Keep a deterministic fallback path
- Treat tool outputs and retrieved text as untrusted
- Verify citations before final answer
- Track token spend per loop iteration; surface budget breach explicitly

## Decision Checklist

- [ ] Baseline non-agentic pipeline measured first on your query distribution
- [ ] Multi-hop gains confirmed on your own eval set (not assumed from domain-specific papers)
- [ ] Agent loop exists for a real failure mode, not for novelty
- [ ] Retry count bounded
- [ ] Verification stage defined
- [ ] Latency budget still acceptable
- [ ] Token budget per loop iteration tracked
