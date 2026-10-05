# Cookbooks

Per-vendor adapter recipes, latency/cost worked examples, ops runbooks, and
the traps appendix.

## Phase status

- [x] Phase 3 — Vendor adapters
  - [x] `pgvector.md` — Postgres + pgvector (default reference adapter, Phase 2)
  - [x] `mem0.md` — Mem0 / Mem0g
  - [x] `letta.md` — Letta / MemGPT
  - [x] `cognee.md` — Cognee (retrieval primary + thin memory shim)
  - [x] `langgraph_store.md` — LangGraph Store
  - [x] `supermemory.md` — Supermemory
- [x] Phase 5 — Operational
  - [x] `latency_cost.md` — five levers, per-surface token budgets, KV-cache layout, cost worksheet, latency-budget anatomy, embedding-cost ceiling
  - [x] `ops_runbook.md` — pre-launch checklist, zero-downtime migrations, backfill recipe, A/B adapter switching, kill switch, observability + alerts, 2 incident playbooks (F1 in prod, adapter outage), backups
  - [x] `traps.md` — 10 production traps with symptom/cause/fix (Anthropic streaming truncation, JSON-mode drift, embedding migration, MCP injection, mode-collapse at scale, contradiction-flooding, cost trap, sub-agent fabrication, model deprecation, GDPR deletion)
- [x] Phase 6 — Runtime refs + managed boundaries
  - [x] `jit_context_loading.md` — pointer-first loading with refs and typed artifact projections
  - [x] `multimodal_assembly.md` — modality-aware bundle shaping and artifact budgets
  - [x] `openai_retrieval_managed.md` — OpenAI hosted retrieval with app-owned truth boundaries
  - [x] `vertex_memory_bank.md` — Vertex managed memory boundary guidance
- [x] Phase 7 — Converged + multi-repo
  - [x] `mongodb_atlas.md` — converged datastore with autoEmbed, P13 boundary mitigations (RA9)
  - [x] `git_repo_ingest.md` — git-anchored multi-repo ingestion: schema, chunk emitter, diff-based runs, DSAR purge, webhook + freshness loop (RA10)

## Vendor smoke suites

Each vendor adapter ships a behavioral smoke test under
`evals/suites/<vendor>/`. The suites are env-gated and skip cleanly when
the SDK or credentials are missing:

| Suite | Gate |
|-------|------|
| `langgraph_store/` | `langgraph` package importable (uses `InMemoryStore`) |
| `mem0/` | `mem0` package + `MEM0_API_KEY` |
| `letta/` | `letta_client` package + `LETTA_BASE_URL` + `LETTA_AGENT_ID` |
| `cognee/` | `cognee` package + `COGNEE_LLM_API_KEY` (or `OPENAI_API_KEY`) |
| `supermemory/` | `httpx` + `SUPERMEMORY_API_KEY` |

Run any suite with the credentials in env: `pytest evals/suites/<vendor>/`.

## Each vendor cookbook follows this template

1. **When to pick this vendor** (one paragraph, honest tradeoffs)
2. **Schema mapping** — `LearnedMemory` ↔ vendor's data model
3. **Adapter implementation** — full Python file satisfying `MemoryStore`
   and/or `RetrievalStore`
4. **Lifecycle support** — which of `remember`/`recall`/`forget`/`improve`
   are native vs emulated; cost of emulation
5. **Tenant isolation** — how the vendor scopes per `owner_scope`
6. **Gotchas** — at least three things the docs don't tell you
7. **Smoke test** — a runnable test against the live vendor (with env-var
   gate so CI without credentials still passes)
