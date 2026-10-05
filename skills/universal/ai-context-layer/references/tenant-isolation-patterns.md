# Tenant Isolation Patterns

Tenant leakage — serving one tenant's context to another — is a P0 failure in any multi-tenant context layer. This reference covers isolation patterns across every layer of the context architecture.

## Isolation Principle

Every context record (entity profile, learned memory, retrieval result, graph edge, assembled bundle) must carry an `owner_scope` field that identifies which tenant owns it. Apply the scope filter at candidate generation — inside the vector, keyword or graph query, before fusion, reranking, truncation or any cache — never on an already-retrieved top-k (the ACL invariant in [ai-rag](../../ai-rag/SKILL.md)). The assembly-time `owner_scope` check below is an assertion that catches a missed filter, not the filter itself.

## Isolation Patterns by Storage Type

### Vector Stores

- **Namespace-per-tenant**: each tenant gets a separate namespace or collection. Queries are scoped to the tenant's namespace. This is the strongest isolation — no filter logic needed, no risk of filter bypass.
- **Filter-level isolation**: all tenants share one index with a `tenant_id` metadata field. Allowed only when the tenant key is a mandatory pre-filter applied inside the ANN query by a server-side layer the caller cannot skip, and a cross-tenant canary runs on every assembly, cache-key or filter change. A filter added by each caller is A10/A30 (see reference-architectures RA3/RA10), not isolation.
- **Tradeoff**: namespace-per-tenant is safer but costs more at scale (each namespace has its own index). Filter-level is cheaper but requires rigorous enforcement. Default to namespace-per-tenant for compliance-sensitive apps.

### SQL / Relational Databases

- **Row-Level Security (RLS)**: database-enforced policies that filter rows by tenant_id on every query. The application sets the tenant context at connection time. RLS is the strongest SQL isolation pattern for application code, but it is not unconditional: superusers and roles with `BYPASSRLS` always bypass it, and table owners bypass it unless the table has `ALTER TABLE ... FORCE ROW LEVEL SECURITY` (PostgreSQL docs, ddl-rowsecurity). Connect as a non-owner role that is neither superuser nor `BYPASSRLS`, set FORCE RLS, and reset the tenant context on every pooled-connection checkout; a leaked `SET` on a pooled connection defeats RLS as surely as a missing WHERE clause.
- **Schema-per-tenant**: each tenant gets a separate schema. Strongest isolation but expensive to manage at scale.
- **Application-level filtering**: WHERE tenant_id = ? on every query. Fragile — a single missing filter leaks data. Use RLS instead when possible.

### Memory Stores (Redis, Key-Value)

- **Partition keys**: prefix all keys with `tenant:{id}:`. Use key-pattern ACLs to prevent cross-tenant access.
- **Separate instances**: strongest isolation, highest cost. Reserve for regulated workloads (finance, healthcare).

### Graph Stores

- **Tenant-scoped subgraphs**: partition graph nodes and edges by tenant. Traversals must not cross tenant boundaries unless explicitly authorized (e.g., shared reference data).
- **Edge-level ACLs**: every edge carries an owner_scope. Traversal queries filter by scope.

## Validation and Testing

- **Cross-tenant retrieval smoke tests**: for each tenant, issue a retrieval query that should return results, and verify no results from other tenants appear. Run these in CI.
- **Cross-tenant canary test**: seed a unique canary string (e.g. `CANARY-<uuid>`) into tenant A's memory, retrieval index and any response or semantic cache. Assemble a bundle as tenant B for the same intent and entity id, then assert the canary is absent from both the bundle and the generated answer. Run it on every change to assembly, cache keys or scope filters, and keep a negative control (a store with the scope filter removed) that must fail. A prose review or a single-tenant fixture proves nothing about isolation. Offline version: `builds/evals/suites/smoke/test_tenant_canary.py`.
- **Runtime assertions**: assert `owner_scope` matches the requesting actor's scope before including any record in a context bundle. Fail loud — throw an error, do not silently filter.
- **Audit logging**: log every context assembly request with actor_id, owner_scope, and the tenant_ids of all records included in the bundle. Alert on mismatches.

## Recipe: support / CRM memory

A support agent serves end customers on behalf of an operator tenant. Scenario defaults are in [memory-scenario-playbooks](memory-scenario-playbooks.md#2-customer-support--crm-multi-tenant); the isolation rules are here.

- **Scope key**: `(operator_tenant, customer_id)` derived from the authenticated session (the operator's API credential plus the verified customer identity), never from the ticket text, a tool argument, or the model. Memory about a customer belongs to that customer's scope, not to the human or AI agent who wrote it. A per-agent scope holds only the agent's own working notes and style preferences, and never customer facts; otherwise a customer's history fragments across agents and leaks to whoever handled them last.
- **CRM is the system of record (P1).** Plan, entitlements, balance, and contact details are read live from the CRM on every turn that needs them. Memory holds interaction summaries, stated preferences, and resolutions, each keyed to the CRM record and ticket ID it came from, and is invalidated when that record changes.
- **Human handoff note.** On escalation, write a typed note into the customer scope (issue, steps tried, open question, customer-stated constraints as attributed claims, ticket ID) and show it to the human agent. The human's resolution comes back as an episode with the human as source; it outranks the AI's summary.
- **Filter inside the index, not after it.** Apply `(operator_tenant, customer_id)` inside the ANN query (partition, partial index, tenant-aware payload index, or iterative scan), not on the top-k it returns. pgvector's own documentation shows that with HNSW a selective filter applied after the scan returns far fewer rows than requested, so a customer with a short history silently gets almost none of it back while a larger neighbour's rows dominate the candidate set.
- **Similar-ticket search** across customers stays inside the operator tenant and returns resolutions, not other customers' messages; strip customer identifiers from anything served across the customer boundary.
- **No shared semantic or response cache** across customers; the cache key includes both scope fields.
- **Tests**: the cross-tenant canary below, run at both levels (operator A vs operator B, and customer 1 vs customer 2 inside one operator); a stale-state probe (plan changed after the note was written); a handoff round-trip. Slice design and scoring for these probes live in [retrieval-and-memory-eval](../../ai-evals/references/retrieval-and-memory-eval.md).

## Shared vs. Tenant-Specific Context

Some context is legitimately shared across tenants (public documentation, product catalogs, reference data). Isolate shared context in a dedicated scope (e.g., `owner_scope: "global"`) and explicitly allowlist it in context assembly rules. Never mix shared and tenant-specific data in the same storage partition without clear scoping.

## Embedding Model Considerations

- **Shared embedding model**: most common. One model serves all tenants. Safe as long as embeddings are not stored or cached across tenant boundaries.
- **Per-tenant fine-tuned models**: rare. Use only when tenants have domain-specific vocabularies that materially affect retrieval quality. The cost and complexity are high.
