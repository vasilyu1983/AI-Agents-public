# Managed Memory Boundaries

## Table of Contents

- [Keep these app-owned](#keep-these-app-owned)
- [Managed services can own](#managed-services-can-own)
- [Decision test](#decision-test)
- [Runtime rules](#runtime-rules)
- [Good fit](#good-fit)
- [Failure checks](#failure-checks)
- [Case studies](#case-studies)
- [How the case studies map to P13 sub-rules](#how-the-case-studies-map-to-p13-sub-rules)
- [Erasure across derived stores](#erasure-across-derived-stores)
- [Cost and performance crossover](#cost-and-performance-crossover)

P13 is the boundary pattern for using hosted memory or retrieval without
turning a vendor service into the canonical product database by accident.

## Keep these app-owned

- User, org, billing, entitlement, and account state
- Audit logs for invalidation, DSAR/delete, and reviewer actions
- Scope derivation (`owner_scope`, tenant, user, org)
- Export/rebuild path from source systems

## Managed services can own

- Fast recall over learned memories
- Hosted retrieval indexes and chunk storage
- Convenience extraction and ranking
- Session-local or provider-local caches

## Decision test

If the answer to "what plan is this customer on?" or "should this user have
access?" comes from hosted memory, the boundary is broken.

## Runtime rules

- Scope is attached before the provider call, not after results return.
- Invalidation and delete semantics are mapped in app code and recorded locally.
- Provider outages degrade recall, not product truth.
- Model or provider migrations have a replay/rebuild path.

## Good fit

- Managed retrieval for fast time-to-value
- Hosted memory for user-scoped personalization where app truth still lives in
  product systems
- LangGraph / agent runtime stacks that want namespaced memory without hiding
  source-of-truth boundaries

## Failure checks

- A28 blocked: hosted memory does not become canonical truth
- A30 blocked: scope is enforced before retrieval/memory expansion
- A2 blocked: structured account-state questions still hit tools or SQL

## Case studies

The boundary call is clearest on concrete services. These services pull on
P13 from different directions; each forces a different boundary call.

### Case 1 — MongoDB Atlas `autoEmbed` (in-DB embedding)

**What it does.** Configure the vector index with `autoEmbed: { sourcePath,
model, credentials }` and Atlas generates embeddings server-side using Voyage
models when documents are inserted or updated. No app-side embedding pipeline.

**Boundary risk.** The embedding model becomes a property of the index, not of
your code. Switching models means dropping the index and re-embedding the
corpus. The vendor controls the model registry — adding or deprecating Voyage
versions is on Atlas's roadmap, not yours.

**Rule.** Allowed for derived chunk retrieval where the model is a tunable.
**Not allowed** for memory rows where embeddings are part of an audit chain.
For memory, generate embeddings in your app, store as raw arrays, and use a
non-`autoEmbed` vector index.

**Migration plan to document before adoption:**

1. Source text is the durable artifact, not the embedding. Keep the field that
   feeds `sourcePath`.
2. Re-embed cost is "drop index → recreate with new model → wait for backfill."
   Estimate this in time and cost on a representative collection before
   committing.
3. Voyage credentials encrypted in Atlas are not exportable. To leave the
   platform, you re-embed in your own pipeline.

### Case 2 — Anthropic Memory Tool (client-side `/memories` directory)

**What it does.** Claude calls a memory tool that the SDK routes to a virtual
`/memories` directory. The commands are `view`, `create`, `str_replace`,
`insert`, `delete`, and `rename` (platform docs, memory-tool page). **The model never stores anything itself** — your handler
implements the directory against your own backend (filesystem, S3, Postgres,
MongoDB, Redis, anything).

**Boundary characteristic.** This is the rare hosted memory affordance that
*deliberately* keeps storage in your infra. The boundary is enforced by design:
Anthropic ships the tool interface, you ship the storage and retention.

**Rule.** Allowed for long-running agents (research, coding, multi-day tasks).
The `/memories` directory pattern composes naturally with P10 (filesystem-as-memory)
and is the cleanest path to durable agent memory on Claude. Wire it into your
existing storage layer rather than treating it as a new tier.

**Implementation guardrails:**

1. Path normalization is on you. Reject `..`, absolute paths, symlinks.
2. Tenant scope is on you — the model has no concept of `owner_scope` unless
   you encode it in path prefixes (`/memories/tenant_<id>/...`) and validate on
   every call.
3. Retention and DSAR/delete are on you. Maintain audit logs for every
   create/update/delete the model emits.
4. The model's view of memory is deliberately small — full-corpus search is
   out of scope. Layer P8 retrieval over `/memory/` separately when you need
   semantic recall across the full directory.

**Managed Agents memory stores and dreams (hosted surface).** Claude Managed
Agents mount memory stores into the agent's filesystem, with read-only mounts
enforced at the filesystem and a store per user as the isolation unit. A
dream is a background pass over prior sessions and a store; it writes a new,
reorganised store and never modifies its input, so you can diff the output
and adopt or discard it. Stores keep immutable versions for a fixed window
(see `data/sources.json`) and expose a redact operation, which matters for
erasure. The docs warn that a successful prompt injection can write content
that later sessions read as trusted memory, so treat writable mounts as a
write path that needs P17 controls. Apps that use the client-side memory tool
directly get none of this and run their own P14 job.

### Case 3 — OpenAI: ChatGPT memory and Agents SDK sessions

**ChatGPT memory** is a consumer feature that saves memories across a user's
chats. No developer API for it was found (unverified), so treat it as out of
scope for app architecture; deleting a chat reportedly does not delete a
memory saved from it (unverified).

**Agents SDK sessions** are transcript memory: the runner reads the session's
items before a run and appends new ones after it. A session is keyed by a
session ID string and exposes `get_items`, `add_items`, `pop_item`, and
`clear_session`. Backends include SQLite, Redis, SQLAlchemy, MongoDB, Dapr
(with TTL), a server-managed backend on the Conversations API, a compaction
wrapper that clears and rewrites the session history, and an encrypted
wrapper with TTL.

**Boundary characteristic.** Sessions store what was said, not extracted
facts, and they carry no authorisation. The SDK docs say the session ID
does not authenticate a user or authorise access to that history, and the
SQLite backend does not authenticate stored rows or detect external edits,
deletions, reordering, or replay. The encrypted wrapper does not verify
completeness or order either.

**Rule.**

1. Derive the session ID server-side from the authenticated principal and
   tenant (`tenant:user:thread`), never from a client-supplied value (T4).
2. Long-term facts are a separate store you build (P2 or P6) and pass at
   request time in the `ContextBundle`.
3. Compaction rewrites history in place; keep the raw items elsewhere if you
   need audit or rebuild (A47).
4. Erasure means `clear_session` plus every copy the backend keeps: Redis
   persistence, database backups, and server-side conversation objects. Read
   the Conversations API's state and retention docs before relying on it.

### Case 4 — AWS Bedrock AgentCore Memory

**What it does.** AgentCore Memory is a managed service in the [Bedrock AgentCore](../../software-paas-hosting/references/aws-bedrock-agentcore.md) family. The app writes immutable events (`CreateEvent`) keyed by `actorId` and `sessionId` (short-term memory). Asynchronous strategies (semantic facts, summaries, preferences, and episodes with reflection) extract long-term records into hierarchical namespaces. Strategies can be overridden or self-managed, and conversations can branch.

**Boundary characteristic.** AWS owns storage and the default extraction prompts; the app owns the IDs, the namespaces, and deletion. IAM condition keys on the namespace path can restrict a role to its own prefix. End every namespace with a trailing slash; the docs say this prevents prefix collisions between tenants. Event expiry covers short-term events only. Long-term records persist until deleted explicitly (`DeleteMemoryRecord`, `BatchDeleteMemoryRecords`). Extraction is asynchronous, so a fact from the last few turns may not be retrievable yet.

Check region availability and the feature list before committing a data-residency plan.

**Rule.**

1. Use it for per-user and per-session state inside AgentCore-hosted agents.
2. Do not use it for corpus retrieval; that is [Bedrock Knowledge Bases](../../ai-rag/references/aws-bedrock-knowledge-bases.md).
3. Derive `actorId` and the namespace from the authenticated tenant and user, and pin the IAM namespace condition to them.
4. Keep raw events recoverable as long as policy allows: if the extraction prompts change, records can drift in shape, and the events are your rebuild path.
5. An erasure runbook must delete long-term records by namespace, not rely on event expiry.
6. AWS-controlled extraction makes the interpretation of conversations opaque. For compliance-sensitive memory, prefer an app-owned P2 store or a self-managed strategy.

### Case 5 — OpenMemory MCP (P10 + P13 Hybrid)

**What it does.** OpenMemory MCP is Mem0's local-first MCP memory server. It
runs on your own machine or self-hosted infra and exposes the Mem0 extraction
and recall interface as a standard MCP server. Compatible with Claude Desktop,
Cursor, and VS Code. Memory data never leaves your infrastructure.

**Boundary characteristic.** P10 + P13 hybrid: storage is local (you own the
bytes and the storage backend), MCP is purely the delivery layer. Mem0
extraction runs locally against a locally-configured LLM or embedding provider.
This is the same boundary shape as the Anthropic Memory Tool (Case 2) — the
vendor ships the interface; you own the storage and retention.

**Rule.** Allowed for multi-tool memory sharing across MCP-compatible clients
(Claude Desktop, IDE agents, terminal agents) when cloud-hosted memory is ruled
out by privacy or compliance constraints. Apply the same guardrails as Case 2:

1. Path or namespace isolation per tenant/user is your responsibility.
2. Scope enforcement (what each MCP caller can access) must be validated at the
   server boundary in your handler, not assumed from client identity.
3. Operational truth (billing, entitlements, account state) must not flow
   through OpenMemory MCP — route those calls to tools or SQL (P1).
4. Retain DSAR/delete audit logs locally; the server does not manage them.

### Case 6 — Vertex AI Memory Bank

**What it does.** Memory Bank extracts memories from conversation events, or
accepts direct creates and updates, under a scope dictionary (for example
`{"user_id": ...}`) that must match exactly on retrieval. Consolidation
merges on write: each generation reports memories created, updated, or
deleted, and a contradicted memory is deleted. Memories can carry a TTL;
each change keeps an immutable revision that can be rolled back, and the
revisions have their own retention (see `data/sources.json`). IAM
conditions can restrict access by scope.

**Boundary characteristic.** Vertex owns extraction and the merge decision;
the app owns the scope. The docs advise assuming that some sensitive or
personal information may still be stored, so configure what to extract and
keep a sensitivity filter on the write path (P24).

**Rule.** Derive the scope dict server-side. Log the created, updated, and
deleted results so you can reconstruct why a memory changed. Erasure must
cover revisions as well as the live memory; check the revision retention
before you promise an erasure deadline.

## How the case studies map to P13 sub-rules

| Service | Storage owner | Embedding owner | Scope owner | Forget owner | Verdict |
|---------|---------------|-----------------|-------------|--------------|---------|
| MongoDB autoEmbed | App (Atlas cluster) | **Atlas (vendor model)** | App | App | OK for chunks; not for audit-bound memory |
| Anthropic Memory Tool | **App (any backend)** | App (if you embed) | App | App | OK; cleanest boundary on Claude |
| Claude Managed Agents memory stores | Anthropic | n/a (files) | App (store per user, mounts) | App (delete, redact) plus version retention | OK; diff dream output before adopting it |
| OpenAI ChatGPT memory | OpenAI | OpenAI | OpenAI | User | No developer API found; out of scope |
| OpenAI Agents SDK sessions | App backend, or OpenAI for the Conversations backend | n/a (transcript) | App (derive the session ID) | App (`clear_session` plus backups) | OK for transcript memory; the ID is not authorisation |
| Google Vertex Memory Bank | Vertex | Vertex | App (exact-match scope dict) | App via API; revisions retained separately | OK with your own log of merge results; erasure must reach revisions |
| OpenAI Retrieval | OpenAI | OpenAI | App-attached | Manual | OK for grounding only |
| AWS AgentCore Memory | AWS | **AWS (vendor extraction)** | App (actor, session, namespace) | App (explicit record deletes; expiry covers events only) | OK for per-user state on AWS; not for audit-bound memory |
| OpenMemory MCP (Mem0) | **App (local/self-hosted)** | App (local provider) | App | App | OK; P10 + P13 hybrid; scope and DSAR are fully app-owned |

The pattern: P13 is healthier when **at least scope and forget are app-owned**,
and the rebuild path from primary sources is documented before adoption.

## Cost and performance crossover

When does a fact-based memory store beat long-context inference on cost?
arXiv 2603.04814 (preprint) reports, in the authors' setup, that fact memory
becomes cheaper than re-sending a long context after a modest number of
turns, and sooner as the context grows. On accuracy it reports the
long-context baseline ahead on LongMemEval and LoCoMo, where the full
transcript matters, and fact memory competitive (not superior) where answers
rest on stable attributes.

**Use it as a method, not a constant.** The break-even moves with the model
and the price sheet; re-derive it from your own turn length, context size,
and the provider's pricing page. The direction supports the P13 rule: design
app-owned memory for long-session economics, not per-call cost, and keep
the full-context baseline in every evaluation
([agent-memory-benchmarks](agent-memory-benchmarks.md#rules-before-you-trust-a-memory-number)).

## Erasure across derived stores

Deleting the row a fact came from is not erasure. One personal fact written
once can end up in a dozen places, and most of them survive a row delete.

| Store | Why the fact survives a delete | What erases it |
|---|---|---|
| Source rows and episode logs | Soft-delete flags; "invalidate, never delete" engines (P4) keep the old fact by design | Physical delete; a tombstone that holds no content |
| Vector indexes | Graph indexes (HNSW) often mark deletions and keep the vector until compaction; arXiv 2606.18497 (abstract) reports soft-deleted vectors as recoverable | Hard delete, then compaction, vacuum, or rebuild; confirm the engine's delete is physical |
| Full-text indexes | SQLite FTS5 keeps deleted entries in the index until segments merge unless its `secure-delete` option is on; freed database pages keep old bytes unless `PRAGMA secure_delete` is on (both off by default). Postgres keeps dead tuples until vacuum | Enable secure delete before deleting, then merge or rebuild; vacuum |
| Graph nodes and edges | An entity node aggregates facts from many episodes; deleting the episode leaves edges extracted from it | Delete edges whose only source is the erased episode; re-derive edges with mixed sources |
| Consolidated summaries, profiles, observations | The fact was rewritten into prose with no pointer back | Delete by lineage (P21); without lineage, regenerate from the remaining episodes or search and redact |
| Caches | Semantic caches, rendered context bundles, prompt caches | Purge by subject on erasure, or keep TTLs shorter than the erasure deadline |
| Revisions, versions, backups | Memory Bank revisions, memory-store versions, dataset versions, point-in-time recovery, database backups | Redact where an endpoint exists; crypto-shredding for backups; otherwise document the retention window as the erasure deadline |
| Vendor-held memory | Hosted engines and async extraction queues hold their own copies | Delete through the vendor API per record or namespace after the queue drains; get derived-store deletion in the contract |
| Telemetry, traces, eval sets | Prompts and retrieved context are logged; eval fixtures get built from production | Retention limits, scrubbing at capture, fixtures from synthetic data |

**Order of operations.**

1. Suppress re-admission: record a content-free suppression key so the fact
   is not re-extracted from a source that still holds it.
2. Let async extraction finish, or cancel queued jobs for the subject.
3. Delete the source episodes.
4. Delete derived records by lineage: facts, edges, summaries, observations.
5. Compact or rebuild vector and full-text indexes.
6. Purge caches.
7. Destroy the subject's key (backups) and call vendor deletes.
8. Write an audit row that records the request and the stores cleared, with
   no personal content.

**Crypto-shredding for backups.** Rewriting every backup to remove one
person is rarely possible. Encrypt each subject's content under a
per-subject data key (envelope encryption in a KMS); backups then hold only
ciphertext, and destroying the key makes every copy unreadable without
touching the backups. Limits: live indexes cannot search ciphertext, so
embeddings and full-text entries still need the physical deletes above;
plaintext that leaked into logs is not covered; and a restored backup must
not be able to fetch the destroyed key. The technique is on a widely read
technology radar at "Trial"; whether a given regulator accepts key
destruction as erasure was not confirmed, so get legal sign-off.
arXiv 2606.18497 proposes rotating keys by epoch for vector stores.

**Acceptance test: the sentinel.**

1. Plant a synthetic personal fact containing a unique token for a test
   subject, plus a neighbour fact for the same subject and one for another
   subject.
2. Positive control: wait for async extraction, then confirm every probe
   below finds the sentinel. A probe that cannot find it before erasure
   proves nothing after.
3. Erase through the production path.
4. Probe every store (exact-token search over rows, full-text indexes, graph
   properties, summaries, caches, vendor APIs, logs) and every retrieval path
   (vector search with paraphrases, nearest neighbours of the sentinel's old
   embedding, keyword search, graph traversal, the agent's own answer). Run
   the same probes on a restore of the latest backup in an isolated
   environment.
5. Pass means zero recoveries anywhere, both neighbour facts still
   retrievable, a content-free audit row present, and re-ingesting the
   original source not bringing the sentinel back.

Run it in CI on fixtures and on a schedule against staging; rerun after any
change to indexes, consolidation, caching, or vendors.

**Regulatory anchor (hedged).** The EDPB's Opinion 28/2024 addresses AI
models, not memory stores. A German state regulator's discussion paper
attaches data-subject rights to the input and output of an AI system and
names retrieval-augmented systems. No regulator text found classifies
embeddings as personal data in terms; the safe inference is that an
embedding of personal text, retrievable by that person's name, gets the same
erasure treatment as the text.

## Primary sources

- `data/sources.json` → Google Agent Engine Memory Bank
- `data/sources.json` → OpenAI Retrieval
- `data/sources.json` → OpenAI Memory FAQ (consumer)
- `data/sources.json` → LangChain Long-Term Memory
- `data/sources.json` → MongoDB autoEmbed (vector search)
- `data/sources.json` → Anthropic Memory Tool (Claude API)
- `data/sources.json` → Claude Managed Agents memory stores
- `data/sources.json` → OpenAI Agents SDK sessions
- `data/sources.json` → AWS Bedrock AgentCore Memory
- `data/sources.json` → SQLite FTS5 and secure_delete
- `data/sources.json` → crypto-shredding (technology radar)
- arXiv 2603.04814 (cost crossover); arXiv 2606.18497 (soft-deleted vectors)

Thank you to arXiv for use of its open access interoperability.
