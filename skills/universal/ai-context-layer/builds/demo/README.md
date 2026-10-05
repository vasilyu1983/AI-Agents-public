# Demo

End-to-end walkthrough of the reference app: ingest → recall → assemble → sub-agent.

## Run with no infra (default)

```bash
PYTHONPATH=builds:builds/reference_app python builds/demo/end_to_end.py
```

Uses the in-memory fakes from `evals/fakes.py`. Prints a `ContextBundle` shape
plus the validated sub-agent response.

## Run the pointer-first multimodal demo

```bash
PYTHONPATH=builds:builds/reference_app python builds/demo/jit_multimodal.py
```

Shows P12-style runtime refs (`ContextRef` / `ArtifactRef`) resolving into
typed multimodal projections without stuffing raw payloads into the bundle.

## Run against real Postgres + pgvector

1. Apply the schema:
   ```bash
   psql "$POSTGRES_DSN" -f builds/reference_app/adapters/migrations/0001_initial.sql
   ```
2. Run with `USE_POSTGRES=1`:
   ```bash
   USE_POSTGRES=1 POSTGRES_DSN=postgresql://... \
     python builds/demo/end_to_end.py
   ```

The demo currently uses a stub embedder so you don't need an embedding-API key
to test the schema. Wire your real embedder (OpenAI, Voyage, Cohere) in
`build_stack()` before relying on retrieval quality.

## What this demonstrates

| Step | What it shows |
|------|---------------|
| `episodes.append` | A13 — every memory traces back to a logged episode |
| `write(fact)` | A4 — ingest-time contradiction detection runs |
| `retrieval.index` | A8 — knowledge stays separate from memory |
| `assemble(...)` | The six runtime verbs composed correctly |
| `isolate(...)` | F1 defense — fabricated evidence_ids get rejected |
| `jit_multimodal.py` | P12 — pointer-first loading for multimodal artifacts |
