# HNSW Index Configuration Template

> **Operational HNSW configuration is owned by the `ai-vector-brain` skill.**
> This template previously held a paste-ready YAML with backend-specific
> defaults. That content drifts as pgvector versions, halfvec support, and
> iterative-scan semantics evolve, so the canonical template now lives next to
> the SQL it configures.

For paste-ready HNSW DDL, per-session tuning knobs (`hnsw.ef_search`,
`hnsw.iterative_scan`, `hnsw.max_scan_tuples`), `halfvec` guidance for
>2000-dim models, and the escalation path to pgvectorscale, see:

- `frameworks/shared-skills/skills/ai-vector-brain/assets/sql/002_indexes_hnsw.sql`
- `frameworks/shared-skills/skills/ai-vector-brain/references/postgres-pgvector-default.md`
- `frameworks/shared-skills/skills/ai-vector-brain/references/backend-selection.md`

## What stays in `ai-rag`

The conceptual side of HNSW — what `M`, `ef_construction`, and `ef_search`
each control, the recall/latency tradeoff curve, and when HNSW is the wrong
choice — lives in `references/vector-search-patterns.md` (Pattern 3).

## Boundary reminder

| Concern | Owned by |
|---|---|
| Why HNSW, what M and ef_search mean, recall/latency theory | `ai-rag` |
| HNSW DDL, parameter defaults, per-session knobs, version-specific features | `ai-vector-brain` |
| Backend selection (HNSW vs pgvectorscale vs Qdrant vs Vespa) | `ai-vector-brain/references/backend-selection.md` |
