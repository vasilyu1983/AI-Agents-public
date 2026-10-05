# Cookbook: OpenAI Retrieval (Managed Boundary)

Use this when you want hosted retrieval speed and developer ergonomics, but you
still keep product truth, scope derivation, and deletion/audit semantics in the
app layer.

## Good fit

- Corpus grounding for docs, notes, and uploaded files
- OpenAI-native response/runtime stacks
- Teams that want managed indexing but app-owned truth

## Keep app-owned

- Billing, entitlement, profile, and org truth
- `owner_scope` derivation
- invalidation / delete / export policy
- evals for wrong-scope and stale-source behavior

## Wiring pattern

1. Build `ContextRef` / `ArtifactRef` handles in app code.
2. Call hosted retrieval with explicit scope metadata.
3. Convert results into `RetrievalResult` with stable `evidence_id`.
4. Keep raw provider payloads out of the bundle; project only the typed fields
   the surface needs.

## Gotchas

- Hosted retrieval is not a profile store.
- Re-index and delete semantics still need local audit.
- Provider ranking quality is not answer quality; keep evals separate.
