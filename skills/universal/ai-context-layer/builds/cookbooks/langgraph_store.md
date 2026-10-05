# Cookbook: LangGraph Store

Adapter file: `reference_app/adapters/langgraph_store_adapter.py`.
Works with any `langgraph.store.base.BaseStore` implementation —
`InMemoryStore` (testing), `PostgresStore` (durable), or your own.

## When to pick LangGraph Store

- You are already on **LangGraph** for orchestration and want one
  storage layer for graph checkpoints + agent memory.
- You want **namespaced KV** semantics — your memory access pattern is
  "give me everything under `(org, user, "memory")`" rather than
  "find similar memories."
- You want **swappable backends** without rewriting application code:
  swap `InMemoryStore` for `PostgresStore` for tests-vs-prod.

## When to pick something else

- You need rich **vector search** without rolling your own embeddings —
  `BaseStore.search` supports vector indexing in newer versions but the
  ergonomics lag pgvector and Mem0.
- You need **bi-temporal** queries — none of the BaseStore impls model
  fact time vs system time.
- You aren't using LangGraph for orchestration — there's no reason to
  pull in the dep just for storage.

## Schema mapping

| Contract field | LangGraph Store location | Notes |
|---|---|---|
| Namespace | `(*sorted(owner_scope.values()), entity_id, "memory")` | Structural A10 |
| Key | `LearnedMemory.id` | Caller-provided UUID |
| Value | JSON-shaped payload of the full record | `_to_payload(fact)` |
| `invalidated_at` | `value.invalidated_at` | Soft-delete pattern |

## Lifecycle support

| Verb | Native? | Cost of emulation |
|------|---------|-------------------|
| `remember` | Yes (`put`) | None |
| `recall` | Yes (`search`) | One round-trip; filtering happens client-side |
| `forget` | **No** non-destructive option | We patch the payload's `invalidated_at`; recall filter skips them. The row stays for audit |
| `improve` | **No** atomic update | Read-modify-write — race on concurrent feedback. Acceptable at low volume |
| `find_contradictions` | Emulated via search | Over-fetch the namespace + filter client-side. Adequate for ≤10K memories per entity |

## Tenant isolation

`_namespace` builds a tuple by sorting `owner_scope` keys and appending
the entity. Cross-tenant queries are structurally impossible — to read
a different scope's memory you must build a different tuple, which means
the calling code has the scope explicitly.

```python
{"organization_id": "org_42"} + entity "usr_5"
  → namespace ("org_42", "usr_5", "memory")
```

If you need hierarchical scopes (org > workspace > project), encode them
all in the tuple: `("org_42", "wsp_1", "prj_7", "usr_5", "memory")`.
LangGraph's `search(namespace_prefix=...)` then lets you scope reads
broader or narrower as needed.

## Gotchas

1. **`list_namespaces()` is not on every BaseStore impl.** Required by
   `_find_namespace` for forget/improve. The adapter falls back to a
   no-op when missing — for production, maintain a side index of
   `id → namespace` to avoid the scan.
2. **`InMemoryStore` is process-local.** Tests pass; production fails
   silently if you forget to swap it. Add a startup assertion that
   rejects `InMemoryStore` outside test envs.
3. **`search` returns Item objects in newer SDKs, dicts in older ones.**
   The adapter handles both shapes. If your linter complains about the
   ambiguous types, pin a single SDK version and tighten the adapter.
4. **Vector search is opt-in and extra-config.** Just calling `search`
   gives you list-by-namespace. To get semantic ranking, configure an
   index at store-construction time and pass `query=` to `search`.
5. **Namespace cardinality is your problem.** A naive multi-tenant
   deployment can produce millions of namespaces. Some BaseStore impls
   (e.g. PostgresStore) handle this fine; others (in-memory) blow up.

## Smoke test

```bash
PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/langgraph_store -v
```

The InMemoryStore variant requires no env var; PostgresStore variant
gates on `POSTGRES_DSN`.

## Pairing with LangGraph orchestration

The adapter is most useful when LangGraph already runs your agent loop:

```python
from langgraph.store.postgres import PostgresStore
from reference_app.adapters import LangGraphStoreMemoryStore
from reference_app.runtime import assemble

store = PostgresStore.from_conn_string(DSN)
memory = LangGraphStoreMemoryStore(store)

# Inside your LangGraph node:
def my_node(state, config, store):
    bundle = assemble(
        request=state["request"],
        memory_store=memory,
        ...,
    )
    return {"bundle": bundle}
```

The `store` argument is the same `BaseStore` instance LangGraph uses
for checkpoints — one connection, one schema migration, one ops story.
