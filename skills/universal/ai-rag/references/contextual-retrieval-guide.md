# Chunk Context Augmentation (Contextual Retrieval) — Decision Only

**Implementation detail (prompt template, storage, prompt caching, migration) lives in `ai-vector-brain`** — [`../../ai-vector-brain/references/contextual-retrieval.md`](../../ai-vector-brain/references/contextual-retrieval.md). This file keeps only the retrieval-design decision; do not duplicate the build detail here.

Source: Anthropic, "Contextual Retrieval" (2024-09, https://www.anthropic.com/news/contextual-retrieval). Reported top-20 retrieval-failure reductions of ~35% (contextual embeddings alone, 5.7%→3.7%), ~49% (contextual embeddings + contextual BM25), and ~67% (combined with reranking, 5.7%→1.9%), at a one-time cost of ~$1.02 per million document tokens using prompt caching. See the vector-brain reference for the prompt template and build steps.

## When to Use

- Multi-entity corpora where chunks frequently omit the subject (company/product/user).
- Documents with temporal structure (quarters, versions, dates) where chunk-local text is ambiguous.
- Large reports/manuals where headings carry meaning that chunks lose.

## When to Skip

- Your corpus already has strong structure-aware metadata (titles, headings, section paths) and retrieval is already good.
- You cannot validate the impact with an evaluation set — this technique adds ingest-time LLM cost and must be justified by a measured recall/nDCG gain, not applied by default.

## Validation Protocol (required before adopting)

Hold out a retrieval test set (queries + expected sources) and compare baseline vs. contextualized: recall@k / nDCG, empty-result rate, latency and index-size changes. If you also rerank, test both baseline+rerank and contextualized+rerank — the combined lift is not purely additive.

## Failure Modes (Avoid)

- Hallucinated context that introduces incorrect entities or time periods.
- Context that carries sensitive data that should not be indexed or cached.
- Overly long context that bloats embeddings and increases latency and cost.

Mitigations: strict prompts with output length caps; reject empty or non-compliant outputs; keep the raw chunk for citations and display; log and sample augmented chunks for review.
