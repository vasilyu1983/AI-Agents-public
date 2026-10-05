# Reference App — RA1

Working implementation of Reference Architecture 1 (P1 + P2 + P5 + P8): a SaaS
app with operational truth behind tools, typed memory with lifecycle verbs, and
evidence-bearing retrieval, assembled per surface with explicit budgets.

## Layout

```
reference_app/
  contracts/        # Canonical contracts as Python dataclasses
  adapters/         # Adapter Protocols + Postgres reference impl + 5 vendor adapters + Anthropic LLM + runtime-ref helpers
  runtime/          # The six runtime verbs (write/select/compress/isolate/order/format) + resolve() + UnionMemoryStore
  pyproject.toml    # Package metadata + extras: postgres / anthropic / langgraph / http / dev
```

## Status

All six phases shipped. Highlights by phase:

- **Phase 1:** contracts as code, adapter interfaces, runtime verb signatures, smoke tests
- **Phase 2:** Postgres + pgvector adapters, working ingest/retrieval/assembly, end-to-end demo
- **Phase 3:** 5 vendor adapters (Mem0, Letta, Cognee, LangGraph Store, Supermemory) with cookbooks
- **Phase 4:** Anthropic LLM adapter, context-rot suite (5 token tiers), mode-collapse suite, metrics + reports
- **Phase 5:** `UnionMemoryStore` composition + ops cookbooks (latency/cost, ops runbook, traps)
- **Phase 6:** pointer-first runtime refs (`ContextRef`, `ArtifactRef`, `LoadedArtifact`), optional resolver/loader protocols, JIT multimodal demo, and per-vendor smoke suites

## Design choices

- **Dataclasses over Pydantic for contracts.** Zero runtime dependencies for the contract layer; validation is the adapter's job. Add Pydantic at the API boundary if you need it.
- **`Protocol` over ABC for adapters.** Structural typing means a Postgres adapter, a Mem0 adapter, and a fake-in-memory test adapter all satisfy the same `MemoryStore` interface without inheritance.
- **Runtime verbs as free functions, not methods.** `write(store, fact)` composes better than `store.write(fact)` when you want to wrap one verb (e.g., add provenance) without subclassing the store.
- **No framework lock-in.** Works with raw provider SDKs, LangGraph, LlamaIndex, or your own orchestrator. The kit owns *contracts and verbs*, not *orchestration*.
- **Pointer-first by default for heavy artifacts.** Large files and multimodal payloads should travel as refs until a surface explicitly resolves them.

## Quick mental model

```
ingest:    raw_episode → extract → write(memory_store, fact) → index(retrieval_store, doc)
recall:    surface_request → select(memory) + select(retrieval) → resolve(refs) → format → order → compress → bundle
feedback:  reaction → update_confidence(memory_store) | enqueue_contradiction(review_queue)
```

Each arrow is one runtime verb plus one adapter call. That's the whole shape.
