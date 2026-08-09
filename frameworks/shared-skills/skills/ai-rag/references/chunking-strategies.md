# Chunking Strategy Selection

Decision page. Pick a baseline here, then jump to
[`chunking-patterns.md`](chunking-patterns.md) for the actual procedure
(token budgets, overlap, metadata, quality checks).

Chunking is a tuning lever, not the first architecture decision. Decide
whether the system should retrieve documents at all *before* picking a
chunking strategy.

## Pick by content type

| Content type | Baseline | Procedure in `chunking-patterns.md` |
|--------------|----------|-------------------------------------|
| Long-form prose (blogs, articles, docs) | Sliding window | §2 Standard Sliding-Window |
| Structured docs (manuals, legal, papers) | Hierarchical | §3 Hierarchical Chunking |
| Source code | Syntax-aware blocks | §4 Code Chunking |
| Tables | Row-wise with header pairing | §5 Table Chunking |
| PDFs / scans | Layout-reconstructed | §6 PDF/Scanned Document |
| Markdown policies, ADRs, runbooks, git-anchored docs | Heading-aware + frontmatter | see `ai-context-layer/references/markdown-chunking-patterns.md` |
| Chat / email threads | Message-aware | metadata: thread id, author, timestamp |

## Pick by failure mode

| Failure | Strategy |
|---------|----------|
| Topic boundaries fuzzy, fixed-size cuts split meaning | **Semantic chunking** |
| Cross-section context strongly affects meaning, ingestion budget available | **Late chunking** |
| Want better per-chunk context without redesigning the embedding stack | **Contextual retrieval** (prepend compact context summaries) |
| Citations break across versions of the same doc | **Anchor-stable chunking** (heading path as stable id; see markdown-chunking-patterns) |

## Practical default

Start with structure-aware chunking when structure exists. Use fixed-size
with overlap only as a baseline for unstructured text. Move to semantic
or late chunking when evals show a real gap.

## Validation loop (only thing not in `chunking-patterns.md`)

1. Freeze embedder, retriever, reranker.
2. Change *only* the chunking strategy.
3. Re-run retrieval evals on the same slice set.
4. Compare recall@k, MRR, nDCG, latency, and citation validity.

A change that improves recall but degrades citation validity is not a
win — chunk boundaries that don't survive into the citation are a
silent regression.

## 2026 Benchmark Findings

Two papers published in 2026 benchmark chunking strategies at scale:

- **arXiv 2504.19754** — broad chunking strategy comparison across corpus types.
- **arXiv 2603.25333 (Adaptive Chunking)** — evaluates adaptive chunking against fixed-size and semantic baselines.

**Key Feb 2026 finding:** On a 50-paper academic corpus, recursive 512-token splitting scored 69% accuracy vs 54% for semantic chunking. Simple recursive chunking remains a strong default; let evals on your own corpus decide whether the added complexity of semantic or adaptive methods is justified.

## Cross-references

- Procedures, token budgets, metadata: [`chunking-patterns.md`](chunking-patterns.md)
- Markdown / policy / ADR shapes: [`../../ai-context-layer/references/markdown-chunking-patterns.md`](../../ai-context-layer/references/markdown-chunking-patterns.md)
- Git-anchored bi-temporal ingestion: [`../../ai-context-layer/references/git-anchored-ingestion.md`](../../ai-context-layer/references/git-anchored-ingestion.md)
