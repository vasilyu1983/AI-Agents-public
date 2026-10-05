# RAG Patterns — Agent-Side Pointers

*Purpose: the retrieval decisions that belong to an agent design. Pipeline mechanics (chunking, embeddings, hybrid fusion, reranking, filtering, HyDE, routing, evaluation) are owned by the [`ai-rag`](../../ai-rag/SKILL.md) skill; do not duplicate them here.*

## Table of Contents

- [Where the Depth Lives](#where-the-depth-lives)
- [Agentic RAG: Static vs Iterative Retrieval](#agentic-rag-static-vs-iterative-retrieval)
- [Agent-Side Rules](#agent-side-rules)

## Where the Depth Lives

| Need | Read |
|---|---|
| Pipeline shape, chunking, embeddings, index choice | [`../../ai-rag/references/pipeline-architecture.md`](../../ai-rag/references/pipeline-architecture.md), [`../../ai-rag/references/chunking-strategies.md`](../../ai-rag/references/chunking-strategies.md), [`../../ai-rag/references/index-selection-guide.md`](../../ai-rag/references/index-selection-guide.md) |
| Hybrid (semantic + keyword) fusion and reranking | [`../../ai-rag/references/hybrid-fusion-patterns.md`](../../ai-rag/references/hybrid-fusion-patterns.md), [`../../ai-rag/references/ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md) |
| Query rewriting, HyDE, routing, hierarchical retrieval | [`../../ai-rag/references/query-rewriting-patterns.md`](../../ai-rag/references/query-rewriting-patterns.md), [`../../ai-rag/references/advanced-rag-patterns.md`](../../ai-rag/references/advanced-rag-patterns.md) |
| Contextual retrieval (chunk context augmentation) and its validation | [`../../ai-rag/references/contextual-retrieval-guide.md`](../../ai-rag/references/contextual-retrieval-guide.md) |
| Agentic RAG loop mechanics | [`../../ai-rag/references/agentic-rag-patterns.md`](../../ai-rag/references/agentic-rag-patterns.md) |
| Grounding, abstention, evaluation | [`../../ai-rag/references/grounding-checklists.md`](../../ai-rag/references/grounding-checklists.md), [`../../ai-rag/references/abstention-recipe.md`](../../ai-rag/references/abstention-recipe.md), [`../../ai-rag/references/rag-evaluation-guide.md`](../../ai-rag/references/rag-evaluation-guide.md) |
| Copy-paste templates (basic, advanced, hybrid) | `ai-rag/assets/` (chunking, context packing, grounding, eval templates) |
| Multi-agent retrieval worker | [`multi-agent-patterns.md` § 10](multi-agent-patterns.md#10-multi-agent-rag-pattern) |
| Knowledge-base layout for an agent | [`../assets/knowledge-base/kb-architecture.md`](../assets/knowledge-base/kb-architecture.md) |

## Agentic RAG: Static vs Iterative Retrieval

```text
Static:   query → embed → retrieve top-k → inject → generate
Agentic:  query → plan retrieval → multi-step search → adapt → rerank → cite → generate
```

Default to static retrieval. Move to agentic retrieval only when the query is multi-domain, needs several sources, benefits from iterative refinement, or has a high-accuracy bar (legal, medical, technical), because each extra retrieval round adds latency, tokens, and a new place for the loop to drift. Bound the loop the same way as any planner loop: step cap, budget, and an escalation path ([`agent-debugging-patterns.md`](agent-debugging-patterns.md)).

Reference shape (Anthropic's research system): a lead agent plans, spawns parallel search agents, each summarizes into external memory, and the lead retrieves those summaries for synthesis with citations.

## Agent-Side Rules

- Retrieval precedes reasoning; every factual claim in the answer cites retrieved text, and the agent refuses or degrades when evidence is missing ([`agent-operations-best-practices.md` § 3](agent-operations-best-practices.md#3-retrieval--grounding)).
- Treat retrieved chunks as untrusted input: they never carry instructions, and an exfiltration-capable tool never shares a context with them (see Production Defaults in [`../SKILL.md`](../SKILL.md)).
- Route by domain before retrieving when the corpus mixes domains; a wrong-domain hit is a silent failure the reranker will not catch.
- Validate any retrieval change (contextual chunks, hybrid fusion, reranker swap) on a held-out set with recall@k, nDCG or MRR, and empty-result rate, plus end-to-end groundedness; do not adopt a technique on a vendor's reported lift.
