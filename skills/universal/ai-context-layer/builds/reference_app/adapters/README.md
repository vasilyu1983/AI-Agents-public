# Adapters

Adapter `Protocol`s for memory, retrieval, episode log, operational tools,
embedding, LLM, plus optional runtime-ref helpers (`ReferenceResolver`,
`ArtifactLoader`). Concrete implementations satisfy these structurally — no
inheritance required.

## How to add a new adapter

1. Pick the Protocol(s) your vendor naturally maps to (most often `MemoryStore`
   and/or `RetrievalStore`; P12 surfaces may also need `ReferenceResolver` and
   `ArtifactLoader`).
2. Implement every method with the exact signature. Use `runtime_checkable` at
   import time in your tests to fail fast on signature drift.
3. Keep the adapter dumb — no business logic, no cross-cutting concerns. The
   runtime verbs handle compression, ordering, and projection; the adapter
   only handles I/O.
4. Add a fake/in-memory adapter in your tests so eval suites can run without
   the vendor.
5. When ready, contribute the cookbook entry to `../../cookbooks/` with: when
   to pick this vendor, schema mapping, gotchas, and a runnable smoke test.

## Phase 2 ships

- `postgres_memory.py` — bi-temporal `LearnedMemory` table with `supersedes_id`
- `postgres_retrieval.py` — pgvector index with reranker hook
- `postgres_episodes.py` — append-only episode log
- `fake_*.py` — in-memory test doubles used by the eval harness

## Phase 3 vendor adapters (shipped)

Each adapter has a paired cookbook in `../../cookbooks/` and an env-gated
smoke suite under `../../evals/suites/<vendor>/`.

- `mem0_adapter.py` — Mem0 / Mem0g (cookbook: `mem0.md`)
- `letta_adapter.py` — Letta / MemGPT (cookbook: `letta.md`)
- `cognee_adapter.py` — Cognee retrieval + thin memory shim (cookbook: `cognee.md`)
- `langgraph_store_adapter.py` — LangGraph Store (cookbook: `langgraph_store.md`)
- `supermemory_adapter.py` — Supermemory REST API (cookbook: `supermemory.md`)
- `anthropic_llm.py` — Anthropic LLM adapter (Phase 4) for `compress`/`isolate`

## Phase 6 runtime-ref helpers (shipped)

- `ReferenceResolver` — turns `ContextRef` into typed evidence, live facts,
  relationship context, and `ArtifactRef`s
- `ArtifactLoader` — loads `ArtifactRef` into `LoadedArtifact` only after
  selection

## Anti-patterns the adapter layer must block

| ID | Where it gets blocked |
|----|----------------------|
| A2 | Adapters never expose entity state — only `LearnedMemory` and `RetrievalResult` |
| A3 | `MemoryStore.forget` is non-destructive; no `delete` method exists |
| A7 | Same as A3 — invalidation, not deletion |
| A10 | Every read takes `owner_scope`; no scope-less query exists in the Protocol |
| A11 | Lifecycle verbs are first-class methods, not optional helpers |
| A13 | `LearnedMemory.source_episode_id` is non-optional in the contract |
| A14 | `LearnedMemory.confidence` is non-optional and `improve` exists |
| A18 | `RetrievalStore.retrieve` returns post-rerank `RetrievalResult`, never raw hits |
