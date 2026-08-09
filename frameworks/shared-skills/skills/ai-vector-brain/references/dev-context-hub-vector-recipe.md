# Dev-Context Hub → Vector Brain Recipe

Turn a `dev-context-multi-repo` (or `dev-context-engineering`) compiled hub into a retrievable vector brain, using only existing scripts. This is the "Vector hub" output mode. The corpus can include markdown hub pages plus repo/context artifacts such as `profiles/*.json`, `graphs/*.json`, manifests, schemas, SQL, and selected source files.

## Table of Contents

- [When to use](#when-to-use)
- [One-command build](#one-command-build-infra-free-artifacts)
- [Architecture](#architecture-2026-graph-bounded-hybrid)
- [End-to-end commands](#end-to-end-commands)
- [Freshness](#freshness-git-anchored-incremental)
- [Manifest example](#manifest-example)
- [Production rigor](#production-rigor-inherit-from-the-skill-do-not-re-derive)
- [Anti-patterns](#anti-patterns)

## When to use

The compiled hub or repo artifact set already exists and agents need *retrieval* over it (find/answer/cite), not just to read markdown. If readers only browse the hub, stay on markdown/HTML — a vector index is not free.

## Two Options

### Option A: Files And Graphs

Stop at the normal dev-context outputs: Markdown pages plus JSON profiles, system edges, knowledge graphs, code graphs, and freshness reports. Use direct reads, `rg`, index pages, `query_graph.py`, `query_code_graph.py`, PPR, and community summaries. This is the canonical, Git-reviewable context hub.

### Option B: Vector DB

Build a vector DB projection from Option A when retrieval needs to be served through an API or tool. Index citable leaves such as Markdown sections, repo profiles, module reports, manifests, schemas, SQL, and selected source lines. Keep graph JSON as the bounding and routing layer, not as one embedded document.

## One-command build (infra-free artifacts)

To make the vector hub as easy to produce as the markdown hub, run:

```bash
bash ../scripts/build_vector_hub.sh <hub_root> <out_dir> [source_id] [corpus_type]
```

This runs steps 1–3 below and emits a validated `brain-manifest.json` — producing
`inventory.jsonl`, `documents.jsonl`, `chunks.jsonl`, `brain-manifest.json` in
`<out_dir>`. It fails loudly if `<hub_root>` has no indexable context files. It deliberately
stops before embed/load (that needs Postgres+pgvector and a provider key) and
prints the exact `embed_and_load.py` command to run next. The manual steps below
explain what the wrapper does and how to wire retrieval and freshness.

## Architecture (2026 graph-bounded hybrid)

```text
compiled hub + repo artifacts  --inventory_corpus.py-->  inventory.jsonl
  --prepare_documents.py --corpus-type repo|docs-->       documents.jsonl   (provenance metadata preserved)
  --chunk_corpus_files.py-->                              chunks.jsonl
  --embed_and_load.py-->                          pgvector (documents + chunks + embeddings)

retrieve time:
  query_graph.py --ppr --seed <node>  ->  bounded node set  ->  source paths
  retrieve.py --query Q --source-path-prefix <p> ...  (lexical + vector + RRF + rerank, filtered to the bounded paths)
```

The knowledge/code graph is **not embedded as one giant graph blob**. It is the retrieve-time bounding layer: graph gives depth (multi-hop, relationships), vectors give breadth (semantic recall). If you index graph-adjacent artifacts, index bounded, human-citable leaves such as repo profiles, module reports, query outputs, manifests, schemas, or selected source files with path/line anchors. For simple semantic lookup over a small hub, skip the graph step — it is overhead without benefit.

## End-to-end commands

All scripts are in `ai-vector-brain/scripts/`. `provider`/`model`/`dim` are deployment choices (e.g. `openai text-embedding-3-large 3072`), not defaults.

```bash
# 1. catalog the hub or repo artifact root (provenance lands in the documents table)
python3 inventory_corpus.py <hub_root> --source-id hub > inventory.jsonl
python3 prepare_documents.py inventory.jsonl --corpus-type repo > documents.jsonl
#    documents.jsonl rows carry metadata (source_path, and any source_repo/
#    source_commit_sha set on inventory rows) — preserved by prepare_documents.

# 2. chunk the corpus files themselves.
#    Markdown gets heading-aware parent-child chunks; JSON/YAML/code/SQL/text
#    get line-bounded chunks with path#line anchors. The graph remains a
#    bounding layer, while citable source and report leaves become retrieval rows.
python3 chunk_corpus_files.py <hub_root> --unit parent_child --max-tokens 512 > chunks.jsonl

# 3. apply DDL then load — see references/postgres-pgvector-default.md for the SQL
python3 embed_and_load.py chunks.jsonl \
  --provider <provider> --model <model> --dim <dim> \
  --source-id hub --doc-type repo

# 4. retrieve, graph-bounded
python3 ../../dev-context-multi-repo/scripts/query_graph.py <knowledge-graph.json> \
  --ppr --seed <node-id> --format json --output bound.json
#    take the node source paths from bound.json, pass each as --source-path-prefix
python3 retrieve.py --query "<question>" \
  --provider <provider> --model <model> --dim <dim> \
  --source-path-prefix <path1> --source-path-prefix <path2>
```

Per-repo instead of portfolio: use `../../dev-context-code-graph/scripts/query_code_graph.py <code-graph.json> --ppr --seed <symbol>` for the bounding step. The deeper graph-at-scale patterns (PPR seeding, community summaries, candidate-region bounding) are in [graph-theory-at-scale.md](graph-theory-at-scale.md).

## Freshness (git-anchored incremental)

Do not re-embed the world on a schedule. Re-embed only files whose git content changed: content-hash idempotency on `documents`, tombstone-on-delete, diff-driven ingestion. Full mechanics and the ingest ledger contract: [../../ai-context-layer/references/git-anchored-ingestion.md](../../ai-context-layer/references/git-anchored-ingestion.md) (RA10) and `assets/sql/004_ingest_ledger.sql`.

## Manifest example

Passes `python3 ../scripts/check_brain_manifest.py`:

```json
{
  "brain_id": "dev-context-hub",
  "backend": "postgres_pgvector",
  "corpus_type": "repo",
  "embedding_model": "openai:text-embedding-3-large:3072",
  "source_roots": ["<hub_root>"],
  "chunking": {"unit": "mixed_parent_child_line_bounded", "max_tokens": 512, "token_unit": "word_estimate", "context": "markdown parent-child; structured/code/sql/text line-bounded"},
  "retrieval": {"mode": "graph_bounded_hybrid", "top_k": 10, "candidates": 50, "rerank": true},
  "freshness": {"strategy": "git_anchored_incremental", "idempotency": "content_hash", "on_delete": "tombstone"},
  "eval": {"seed": "build_eval_seed.py", "gates": ["path_recall@10", "stale_commit_detection"]}
}
```

## Production rigor (inherit from the skill, do not re-derive)

This recipe is the *path*; production readiness comes from the skill's existing machinery. Before calling a hub brain done:

- **Eval gate is not optional.** Seed a golden set with [`../scripts/build_eval_seed.py`](../scripts/build_eval_seed.py), hand-label expected evidence, and gate `path_recall@10` + `stale_commit_detection` in CI before tuning chunking or embeddings. Per-corpus gates: [eval-by-corpus-type.md](eval-by-corpus-type.md).
- **Lift recall with contextual retrieval** when retrieval-failure rate is the bottleneck — contextualize at index time, keep the original chunk for citation: [contextual-retrieval.md](contextual-retrieval.md).
- **Plan for model + corpus drift** — pin `embedding_model` per row, monitor similarity drift, prefer Drift-Adapter over full re-embedding: [embedding-drift-mitigation.md](embedding-drift-mitigation.md).

## Anti-patterns

- Embedding the knowledge/code graph itself as a giant JSON blob — it is the bounding layer, not the corpus.
- Indexing only generated Markdown when the real question needs repo artifacts, manifests, schemas, code profiles, or selected source lines.
- Vector-only retrieval over a hub that already has a graph (loses multi-hop accuracy).
- Full re-index when a git diff identifies the changed files.
- Dropping `source_path` / `source_commit_sha` — citations and stale detection need them.
- Treating generated hub summaries as primary source instead of the cited repo content.
