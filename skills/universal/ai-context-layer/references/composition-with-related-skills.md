# Composition With Related Skills

## Table of Contents

- [Ownership map](#ownership-map)
- [End-to-end pipeline the requirements-hub-shaped case](#end-to-end-pipeline-the-requirements-hub-shaped-case)

How `ai-context-layer` composes with the other context-bearing skills in
this repo when the problem is "build an AI-agent KB over a portfolio of
git repos *and* a body of policies, runbooks, and operational docs."
This is the requirements-hub-shaped case — the load-bearing example the
RA10 + RA11 pair is designed for.

Each skill owns a slice. None replaces the others. The mistake to avoid is
duplicating ownership: e.g., letting `ai-context-layer` redefine repo
discovery, or letting `ai-rag` redefine the bundle contract.

## Ownership map

| Skill | Owns | Does not own |
|-------|------|--------------|
| **`dev-context-multi-repo`** | Repo discovery, portfolio profile extraction, hub assembly, freshness reports, drift detection across repos | Per-file chunking, vector index, agent runtime |
| **`dev-context-engineering`** | Repo-native agent context: `AGENTS.md`, `.claude/`, `.codex/`, instruction files, context-graph discipline *inside* one repo | Cross-repo composition, retrieval, agent memory |
| **`dev-context-code-graph`** | Symbol-level / import / inheritance / blast-radius graphs *per repo* | Markdown content, retrieval, runtime context bundles |
| **`ai-rag`** | Retrieval pipeline depth: chunking experiments, reranker choice, hybrid search, RAG evals | Memory lifecycle, bundle assembly, tenant isolation, ingest scheduling |
| **`ai-context-layer`** *(this skill)* | Composition: tools + memory + retrieval + graph; bundle assembly; grounding contracts; ingest patterns (RA10 / RA11); cross-corpus joins | Repo discovery, per-repo instruction files, retrieval reranker tuning |

The skills layer like this:

```
                       ┌──────────────────────────────────────────┐
   AGENT RUNTIME       │  Agents (chat / code-review / AML /     │
                       │  customer copilot) consume ContextBundle │
                       └─────────────────▲────────────────────────┘
                                         │ ContextRef + ContextBundle
   ─────────────────────────────────────  │  ─────────────────────────
                                         │
                       ┌─────────────────┴────────────────────────┐
   COMPOSITION         │  ai-context-layer                        │
                       │  RA10 (git-anchored multi-repo KB)       │
                       │  RA11 (policy / compliance / ops docs)   │
                       │  Bundle assembly + grounding contracts   │
                       └──┬──────────┬───────────────┬────────────┘
                          │          │               │
   ─────────────────────  │  ──────  │  ───────────  │  ──────────
                          │          │               │
                  ┌───────▼────┐ ┌───▼─────────┐ ┌───▼──────────────┐
   PIPELINES      │  ai-rag    │ │  policy     │ │  graph layer     │
                  │  retrieval │ │  ingest     │ │  (P5 / Neo4j /   │
                  │  reranker  │ │  adapters   │ │  Postgres edges) │
                  │  evals     │ │  (PDF/      │ │                  │
                  │            │ │  Confluence)│ │                  │
                  └────────────┘ └─────────────┘ └──────────────────┘
                          │
   ─────────────────────  │  ─────────────────────────────────────
                          │
                  ┌───────▼─────────────────────────────────┐
   CATALOG +      │  dev-context-multi-repo                 │
   PORTFOLIO      │  discover_repos / scan_portfolio /      │
                  │  build_hub_views / report_drift /       │
                  │  check_hub_freshness                    │
                  └─┬───────────────────────────┬───────────┘
                    │                           │
   ────────────  ───┼  ─────────────────  ──────┼  ──────────────
                    │                           │
          ┌─────────▼────────┐         ┌────────▼─────────────┐
   PER    │  dev-context-    │         │  dev-context-        │
   REPO   │  engineering     │         │  code-graph          │
          │  AGENTS.md /     │         │  symbols / imports / │
          │  .claude/ /      │         │  inheritance /       │
          │  context-graph   │         │  blast-radius        │
          └──────────────────┘         └──────────────────────┘
                    │                           │
   ──────────────────────────────────────────────────────────
                    │
          ┌─────────▼─────────────────────────────────┐
   SOURCES│  Git repos · Confluence · SharePoint ·    │
          │  Notion · regulator PDFs · runbooks ·     │
          │  control frameworks (ISO/NIST/PCI/PSD2)   │
          └───────────────────────────────────────────┘
```

## End-to-end pipeline (the requirements-hub-shaped case)

For a firm with N git repos, M policies/standards/runbooks across mixed
sources, and K agents consuming the layer:

### Phase 1 — Portfolio shape (`dev-context-multi-repo`)

Run once, then on a cadence:

1. `discover_repos.py` against the org → produces the repo inventory.
2. `scan_portfolio.py` → extracts per-repo profile (language, owner,
   lifecycle stage, CI shape).
3. `build_hub_views.py` → produces the coordination repo's
   `profiles/<repo>.json` (or domain × lifecycle folders, as
   `requirements-hub` already does).
4. `report_drift.py` + `check_hub_freshness.sh` → freshness SLO inputs.

**Output to `ai-context-layer`:** the portfolio catalog, consumed as
`KnowledgeSource` rows. The catalog tells RA10 ingestion which repos to
scan and what `owner_scope` to attach.

To publish that hub as a retrievable vector brain, follow
[../../ai-vector-brain/references/dev-context-hub-vector-recipe.md](../../ai-vector-brain/references/dev-context-hub-vector-recipe.md)
(graph-bounded hybrid, git-anchored freshness).

### Phase 2 — Per-repo agent context (`dev-context-engineering`)

For each repo that hosts agents *inside* itself:

1. Adopt `AGENTS.md` / `.claude/rules/` / `.codex/agents/` as the per-repo
   instruction surface.
2. Validate context-graph discipline (no mutual references, no orphan
   rules).
3. Compile per-repo `CLAUDE.md` / `AGENTS.md` if missing.

This layer is *not* ingested into the cross-repo KB. It is the per-repo
agent contract. It composes *next to* RA10, not *into* it.

### Phase 3 — Per-repo code graph (`dev-context-code-graph`)

For repos where agents need blast-radius / call-graph awareness:

1. Build per-repo code graph (symbols, imports, inheritance, test links).
2. Persist as JSON next to the repo.

**Output to `ai-context-layer`:** code-artifact nodes for the RA11
cross-reference graph. Specifically the `(:CodeArtifact)-[:ENFORCES]->
(:Standard)` edges that join code to policy.

### Phase 4 — Multi-repo KB ingest (RA10 in this skill)

Per `references/git-anchored-ingestion.md` and the
`builds/cookbooks/git_repo_ingest.md`:

1. For each repo in the catalog, diff `last_indexed_sha → current_sha`.
2. For each changed `.md` file, emit chunks (heading-aware,
   `markdown-chunking-patterns.md`).
3. Embed and upsert with `(source_repo, source_path, source_commit_sha,
   content_hash, valid_from_commit)`.
4. Tombstone deleted files / chunks via `valid_to_commit`.

**Substrate:** Postgres + pgvector with RLS for the regulated default;
MongoDB Atlas (RA9 substrate) for non-regulated converged stacks.

### Phase 5 — Policy / compliance ingest (RA11 in this skill)

Per `references/policy-and-compliance-docs.md`:

1. **Polyglot adapters** — git markdown via Phase 4; Confluence via REST +
   page-version webhooks; SharePoint `.docx` via `python-docx`; regulator
   PDFs via `unstructured.io` + Marker / Docling; Notion via API.
2. Each adapter emits `PolicyChunk(doc_id, version, clause_id,
   normative_weight, effective_from, …)`.
3. **Cross-reference graph build** — `IMPLEMENTS`, `OPERATIONALIZES`,
   `ENFORCES`, `SUPERSEDED_BY`, `MAPS_TO` edges. Substrate: Neo4j +
   Graphiti for bi-temporal graph; Postgres `policy_edge` table for
   simpler stacks.
4. **Editorial review** — new policy versions land in staging; reviewer
   cuts over `effective_from`; old version retains `effective_to`.

**Boundary:** this is *not* `ai-rag`'s job. The retrieval pipeline tuning
(reranker, hybrid weights, RAG evals) is delegated to `ai-rag`. This
skill owns the corpus shape, the schema, and the bundle contract.

### Phase 6 — Retrieval depth (`ai-rag`)

For each retrieval surface (RA10 chunks, RA11 policy chunks):

1. Pick chunking + reranker per `ai-rag/SKILL.md` decision framework.
2. Build RAG evals (recall@k, citation accuracy, refusal-on-empty).
3. Tune hybrid (BM25 + vector) weights on the substrate.

**Important:** the *bundle assembly* — picking which retrieval results to
load, applying authority re-ranking by `normative_weight`, joining to the
graph, attaching citations — stays in `ai-context-layer`. `ai-rag` tunes
the retrieval *pipeline*, not the bundle composition.

### Phase 7 — Bundle assembly + grounding (this skill)

For each agent surface (compliance copilot, code-review, AML, customer
chatbot), assemble per the `ContextBundle` contract:

1. Resolve entities → graph traversal → bounded chunk set (RA11 path).
2. Retrieval over the bounded set, re-ranked by authority weight.
3. Optional join to RA10 code artifacts via `ENFORCES` edges.
4. Citation block with `(doc_id, version, clause_id, effective_at)`.
5. Conflict warnings; staleness warnings.
6. Token-budget enforcement; pointer-first loading (P12) for any artifact
   over the inline threshold.

## Routing decisions (when in doubt, read this)

| Question the user is asking | Skill to use |
|------------------------------|--------------|
| "How do I discover and profile 100+ repos?" | `dev-context-multi-repo` |
| "How do I structure `AGENTS.md` and `.claude/rules/` in this repo?" | `dev-context-engineering` |
| "What's the blast radius of changing this function?" | `dev-context-code-graph` |
| "Should I use HNSW or IVFFlat? What chunk size? Which reranker?" | `ai-rag` |
| "How do I build an agent KB across all those repos and policies?" | `ai-context-layer` (RA10 + RA11) |
| "How do I keep the KB fresh when repos and policies update?" | `ai-context-layer` (RA10 ingest) + `dev-context-multi-repo` (catalog) |
| "How do I cite a policy clause in an agent answer?" | `ai-context-layer` (RA11 citation contract) |
| "How do I prevent the agent from answering with a superseded policy?" | `ai-context-layer` (RA11 effective-time) |
| "How do I tune RAG recall on the policy corpus?" | `ai-rag` (depth) consumed *by* `ai-context-layer` (composition) |

## Anti-patterns of the composition itself

- **Duplicating ownership.** Putting repo-discovery logic in
  `ai-context-layer` because "we ingest from repos." Wrong — call
  `dev-context-multi-repo`'s catalog and treat it as a `KnowledgeSource`
  input.
- **Skipping `ai-rag` because RA10/RA11 mention chunking.** The chunking
  *interface* lives here; the chunking *experiments and depth* live in
  `ai-rag`. Skipping the latter ships a mediocre retrieval layer.
- **Putting per-repo `AGENTS.md` content into the cross-repo vector
  index.** Per-repo agent instructions are *for that repo's agents*.
  They are not policy. Do not ingest them into RA11. They may be
  ingested into RA10 if they are part of the documented portfolio
  knowledge — but tag them as `guideline`, not `policy`.
- **One graph for everything.** Code graph (`dev-context-code-graph`) and
  policy graph (RA11) are different graphs with different shapes.
  Joining them via the `ENFORCES` edge is fine; merging the substrates
  into one Neo4j instance "for simplicity" is not.

## See also

- `reference-architectures.md` → RA10, RA11.
- `git-anchored-ingestion.md` — RA10 ingest mechanics.
- `policy-and-compliance-docs.md` — RA11 deep dive.
- `markdown-chunking-patterns.md` — chunking interface this skill expects.
- Partner skills: `dev-context-multi-repo`, `dev-context-engineering`,
  `dev-context-code-graph`, `ai-rag`.
