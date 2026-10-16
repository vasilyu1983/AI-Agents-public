# Dev-Context Hub → Vector Brain Recipe

Turn a `dev-context-multi-repo` (or `dev-context-engineering`) compiled hub into a retrievable vector brain, using only existing scripts. This is the "Vector hub" output mode. The corpus can include markdown hub pages plus repo/context artifacts such as `profiles/*.json`, `graphs/*.json`, manifests, schemas, SQL, and selected source files.

## Table of Contents

- [When to use](#when-to-use)
- [One-command build](#one-command-build-infra-free-artifacts)
- [Architecture](#architecture-graph-bounded-hybrid)
- [End-to-end commands](#end-to-end-commands)
- [Optional enriched entity anchors](#optional-enriched-entity-anchors)
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

## Architecture (graph-bounded hybrid)

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

## Optional enriched entity anchors

Keep the graph-first route above as the default. Try this projection only when labels and approved aliases miss paraphrased entity lookup. An anchor is a candidate entity ID, not answer evidence. Enrichment here means deterministic text generated from graph records; it is not a learned structural graph embedding or a replacement for the source graph.

Source basis: Keith Bourne, *Unlocking Data with Generative AI and RAG*, second edition, Chapter 14, PDF pages 401–411 (printed pages 362–372), demonstrates entity descriptions assembled from properties and connected entities, then semantic lookup followed by graph expansion. The controls and evaluation below are this recipe's requirements, not measured results from that example. Do not adopt its later prose-parsing step to recover relationships: retrieve the typed graph records directly.

### Build an eligible projection

1. Select an authoritative graph snapshot and an access partition. Before enrichment or embedding, require the anchor, every included neighbor, property, alias, edge and cited source leaf to be visible to that partition. A broadly visible anchor must not inherit a restricted neighbor's text. Use separate projections for different scopes; combine facts only when their permissions apply to every reader of the projection. An embedding is also a derived disclosure, so filtering its returned text afterward is insufficient.
2. Apply the requested effective time and, when supported, knowledge cutoff to all dependencies before traversal. Require a nonempty intersection of their validity intervals. Keep historical and current projections distinct. Missing ACL, validity, source identity or commit metadata makes a dependency ineligible; it does not mean unrestricted or timeless.
3. Expand only allowlisted typed, directed edges. Example budget: one hop, eight edges and 1,024 UTF-8 bytes per anchor, including its label. Sort by `(edge_type, source_id, target_id, edge_id)` before selection; deduplicate edge IDs, reject repeated nodes on longer paths, and stop on either budget. Omit whole relation lines when they do not fit. Record omitted counts and budget settings; truncation cannot imply a complete neighborhood. Raise the hop budget only for a measured query slice, preserving explicit intermediate nodes and directions.
4. Render a fixed template with canonical IDs, labels and approved aliases. Preserve subject and object order; incoming edges retain their original subject. Do not infer inverse, transitive or causal relations from adjacency. Reject unknown edge types rather than inventing a natural-language meaning. Keep each relation's edge ID, source path/line anchor, source commit, validity interval and access scope in a sidecar dependency record.
5. Store the derived text separately from source leaves. Key the projection by entity ID, graph snapshot, dependency digest, renderer version, expansion budget, time scope and access-policy revision. Key its embedding additionally by model/version. Keep the complete dependency list, including labels and aliases; IDs alone cannot detect changed content.

Synthetic example, all records authorized for partition `public-docs` and valid at the selected time:

```text
entity svc:checkout | Checkout API | aliases: payment gateway
edge e:17 | svc:checkout -[CALLS]-> svc:ledger (Ledger API)
source services/checkout/routes.py#L42 | source_commit_sha: <full-commit-sha>
```

The renderer embeds the first two lines and stores the source, validity and scope in the dependency sidecar. “Which service invokes the accounting API?” may locate `svc:checkout`; semantic similarity alone does not prove the answer. `Ledger API -[CALLS]-> Checkout API` is a different fact. An incoming `svc:web -[CALLS]-> svc:checkout` must stay in that order, even when rendered under the checkout anchor.

### Update and retrieval controls

Maintain a reverse dependency map from node, edge, source leaf and policy record to projections. An edit, deletion, tombstone, supersession, alias change, validity boundary or permission change invalidates all dependent text and embeddings. A deleted edge must invalidate its old anchors even though it no longer appears in a new traversal. Re-render affected anchors and re-embed only changed text; update provenance even when the rendered text stays identical. Publish the matching dependency manifest and index generation atomically.

At query time, first select an authorized access partition and temporal scope. Search only an index generation certified against their current policy and dependency revisions. A stale generation cannot participate in candidate ranking: it could expose restricted facts through similarity or ranking even if display filters hide the text. If freshness cannot be established before search, skip the enriched index and use authorized graph-first retrieval. Do not depend solely on delayed index deletion.

Recheck each hit against current dependency revisions, validity and permissions, then expand its canonical ID in the authoritative graph under the same scope. Fetch the actual source leaves and construct evidence from typed edge records with citations. Never parse the enriched description back into triples, use it as proof, or silently choose one of several same-label entities. Return ambiguity or abstain when IDs or supporting evidence cannot be resolved.

### Matched three-arm evaluation

Use one frozen source snapshot, access/time cohort, gold entity IDs, expected answer sets and edge/source evidence IDs. Compare:

| Arm | Candidate selection | Evidence construction |
|---|---|---|
| A: labels only | Canonical labels and the same approved aliases, embedded without relation text | Authorized graph expansion and source leaves |
| B: enriched anchors | The bounded text projection above | The same expansion and source-leaf path as A |
| C: current graph-first | Existing graph seed resolution and bounded hybrid recipe | Existing graph-first evidence path |

Hold the embedding model, candidate count, reranker, answer model/prompt and evidence-token budget fixed where applicable. Match final evidence budgets across all arms and report their actual candidate/edge counts; do not give B extra expansion or a different source corpus. Freeze tuning before running the held-out set.

Include paraphrases, approved aliases, duplicate labels requiring disambiguation, incoming versus outgoing edges, reversed-edge distractors, absent intermediate edges, and omitted neighbors beyond the expansion budget. Add fixtures with expired edges, backdated corrections, deleted sources, changed ACLs and a deliberately stale index. Expected behavior for denied or stale projections is exclusion before semantic search, with an authorized fallback or explicit abstention.

Report entity recall@k and ambiguity error rate, evidence recall/precision, exact answer-set correctness, supporting-edge direction correctness, unsupported-relationship rate, stale/unauthorized exposure counts, abstention quality and p50/p95 latency. Define unsupported-relationship rate as emitted relationship claims without eligible typed edge/path and source evidence divided by all emitted relationship claims; report counts and mark a zero denominator undefined. Record build/update time, embedded tokens, query tokens, index storage and priced cost only when actual rates are supplied; otherwise report cost as unpriced. Include invalidation and fallback latency, not only warm searches.

Predeclare quality, latency and cost thresholds; compare paired queries and report uncertainty and slice results. Retain enrichment only when measured value over labels-only anchors also justifies its maintenance cost against the current graph-first route, without stale/unauthorized exposure or unsupported-relationship regression. Until that comparison runs, enrichment's retrieval benefit is **not measured**. Deterministic renderer and invalidation checks establish control behavior only; they do not establish retrieval quality.

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
