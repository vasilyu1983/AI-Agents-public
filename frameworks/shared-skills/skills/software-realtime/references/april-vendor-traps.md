# Real-Time Vendor Traps

_Last verified: 2026-07-11._

## Table of Contents

- [PartyKit (Cloudflare)](#partykit-cloudflare)
- [Liveblocks v2](#liveblocks-v2)
- [Supabase Realtime](#supabase-realtime)
- [Socket.IO v4 Adapter Changes](#socketio-v4-adapter-changes)
- [Cloudflare Durable Objects + WebSockets](#cloudflare-durable-objects--websockets)
- [Phoenix / LiveView](#phoenix--liveview)
- [CRDT Options: Yjs, Automerge 2, Loro](#crdt-options-yjs-automerge-2-loro)
- [Cross-Vendor Decision Table](#cross-vendor-decision-table)
- [Anti-Patterns](#anti-patterns)

---

## PartyKit (Cloudflare)

PartyKit runs on Cloudflare Durable Objects. It is currently the fastest path to a globally distributed WebSocket room with shared state, but it inherits all Durable Object constraints.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Single-threaded execution per room | All messages for one room serialize through one DO instance. High-frequency cursor events can saturate it. Shard rooms at the application layer, not at the PartyKit layer. |
| Storage quota per DO | 128 KB limit on synchronous `storage.get/put` per call. Storing full document snapshots inline will silently fail or throw at runtime. Use external R2 or KV for large payloads. |
| Cold-start latency | Durable Objects evict after inactivity. First connection after eviction pays ~200 ms cold-start on v8 isolates. Design reconnect UI to tolerate this rather than treating it as an error. |
| WebSocket hibernation API | PartyKit wraps the Cloudflare WebSocket Hibernation API. If you bypass the `server.broadcast` abstraction and use raw `this.env.DO` patterns from older examples, you bypass hibernation and incur idle CPU billing. |
| No multi-region active-active | A DO instance lives in one region at a time. Cloudflare routes to it, but two clients on opposite sides of the world both pay cross-region latency to reach that single instance. For latency-sensitive multiplayer, measure actual round-trips before committing. |
| `partykit` CLI `^0.0.x` versioning | The CLI uses pre-1.0 versioning. Breaking changes appear in patch releases. Pin the CLI and the `partykit` npm package to the same patch in your lockfile. |

---

## Liveblocks v2

Liveblocks v2 introduced a storage and presence model that is not wire-compatible with v1 clients. Incremental migration from v1 to v2 within the same room is not supported.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Room schema migration | v2 rooms require explicit type-safe schema definitions. v1 `useMutation` / `useStorage` patterns compile but produce runtime type errors when mixed with v2 schema-enforced rooms. |
| Presence throttle defaults | Liveblocks throttles presence broadcasts to 60 ms by default. Applications that relied on sub-60 ms cursor sync from v1 will see visible lag without explicitly lowering the throttle on a paid plan. |
| Yjs integration via `@liveblocks/yjs` | The `@liveblocks/yjs` provider replaces y-websocket. It did not support Yjs subdocuments at initial release (verify current). Subdocument users must stay on y-websocket or pin the Liveblocks Yjs package pre-subdocument-warning. |
| Webhook event schema | v2 webhook payloads changed field names. `actor` became `userId`; `event.type` enum values were renamed. Webhook consumers written for v1 silently receive unrecognized events. |
| Connection state machine | The v2 `RoomProvider` exposes a new `lost-connection` status that v1 apps do not handle. UI code that only checks `connected` / `disconnected` will not show the correct reconnecting state. |
| Pricing per MAU | v2 pricing moved from per-connection to per-MAU. Applications with high connection churn but low active users pay less; apps with many MAUs hitting free tier limits will exceed the free plan more quickly. |

---

## Supabase Realtime

Supabase Realtime uses Phoenix Channels under the hood. The managed service imposes channel and message limits that differ between plans.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Channel limit per project | Free plan: 200 concurrent channels per project. Pro plan: 500. Exceeding the limit causes `JOIN` messages to be silently rejected with a `close` frame. There is no error surfaced to the client SDK by default. |
| Broadcast vs Postgres changes | Broadcast messages are ephemeral — no durability guarantee. Postgres Changes use the WAL replication slot. Mixing both in one subscription creates confusion about delivery semantics. |
| Replication slot exhaustion | Each Postgres Changes subscription uses a replication slot. On shared Supabase instances, slot exhaustion pauses replication globally for that project. High-cardinality row-level filters each count as a slot consumer. |
| `@supabase/realtime-js` v2.x | The v2 client changed `RealtimeChannel.subscribe()` to return `void` instead of a `RealtimeChannel`. Code that chains `.on()` after `.subscribe()` silently loses the subscription. |
| Presence clock drift | Supabase presence uses server-assigned timestamps. Clients that compare presence timestamps to local `Date.now()` will see apparent drift of 50-500 ms depending on region proximity. |
| RLS on Broadcast | Row-level security does not apply to Broadcast messages — only to Postgres Changes. Treating Broadcast as an authenticated channel is a security misconfiguration. |

---

## Socket.IO v4 Adapter Changes

Socket.IO v4 is stable, but the adapter ecosystem changed significantly between v4.5 and v4.7.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Redis adapter v8 requires ioredis v5 | `@socket.io/redis-adapter` v8 dropped support for the legacy `redis` npm package. Projects still on `redis@3` must either upgrade to `ioredis@5` or pin the adapter to v7. |
| Cluster adapter deprecation | The `@socket.io/cluster-adapter` (Node.js cluster module) was soft-deprecated in v4.6 in favor of the Redis or Postgres adapters. It still ships but is not recommended for new deployments. |
| Postgres adapter `pg` peer dependency | `@socket.io/postgres-adapter` v0.3+ requires `pg@8`. Apps on `pg@7` will get a silent peer dependency resolution and receive `undefined` on emitted events from other nodes. |
| `io.to(room).emit` vs `io.in(room).emit` | Both work but have different behavior when combined with `except()`. In v4.7, `io.to(roomA).except(socketId).emit()` correctly excludes; older patterns using `.to().to()` chaining no longer apply the exclude to the entire chain. |
| Sticky sessions still required | Socket.IO HTTP long-polling requires sticky sessions on the load balancer. WebSocket-only mode does not require stickiness, but fallback transport is still enabled by default. Disable `transports: ['polling']` explicitly if stickiness is not available. |
| Engine.IO v6 included in v4.7 | Socket.IO v4.7 upgraded to Engine.IO v6 internally. The `maxHttpBufferSize` default dropped from 1 MB to 100 KB. Applications sending large binary frames (images, audio chunks) need to set this explicitly. |

---

## Cloudflare Durable Objects + WebSockets

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Hibernation API is opt-in | Without `acceptWebSocket()` (Hibernation API), each open WebSocket connection keeps the DO active and billed. At scale, this doubles costs versus hibernation mode. |
| WebSocket rate limit per DO | Cloudflare enforces ~1000 messages per second per DO instance for inbound messages. At 10k-CCU, rooms must be sharded to stay under this limit. |
| Alarms vs WebSocket ping | DO alarms are the correct way to drive periodic state flushes. Using WebSocket ping/pong frames from the server side to drive logic is not reliable — the DO runtime can buffer pings during hibernation. |
| `--remote` dev flag cost | Running `wrangler dev --remote` against production DOs during development is billed. Use `--local` for development and verify the hibernation code path with an integration test. |
| Storage consistency | DO transactional storage provides serializable isolation per DO but not across DOs. Applications that shard rooms across multiple DOs and need cross-shard consistency must implement their own coordination layer. |

---

## Phoenix / LiveView

Phoenix Channels are battle-tested but LiveView introduced stateful server-side components that interact with channels in non-obvious ways.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| LiveView `handle_info` blocking assigns | `handle_info/2` is synchronous per LiveView process. Long-running operations in `handle_info` block all state updates for that connected client. Offload to `Task.async` and handle the result via `send`. |
| PubSub fan-out at scale | `Phoenix.PubSub` defaults to `PG2` (Process Groups). At very high subscriber counts (>10k per topic), broadcasts can generate significant message queue pressure. Consider `FastGlobal` or topic sharding for hot topics. |
| LiveView dead render vs live render | Pages that rely on LiveView for initial render do not receive JavaScript hook events until the live socket connects. Avoid putting critical interactive behavior in hooks that depend on immediate socket availability. |
| Phoenix Channels 1.7 presence diff | `Presence.list/2` now returns maps keyed by `id` rather than a list. Code relying on list order for rendering will break silently when two users share the same presence key. |
| Cluster node isolation | Phoenix PubSub distributes across nodes via `libcluster`. If a node fails and `libcluster` has not reconnected, PubSub messages for that node's subscribers are dropped silently. |

---

## CRDT Options: Yjs, Automerge 2, Loro

### Yjs

The dominant CRDT library for collaborative editing. Mature, well-integrated, but has known scaling constraints.

| Trap | Detail |
|------|--------|
| Document size growth | Yjs does not compact history automatically. A document with many deletions accumulates tombstones indefinitely. Run `Y.encodeStateAsUpdate` + re-initialize to compact. Clients that merge old state against compacted state must use state vectors correctly. |
| Subdocument support | Subdocuments work but are sparsely documented. Providers (y-websocket, y-webrtc) handle subdocuments inconsistently. Test load and sync of subdocuments explicitly. |
| Awareness is not in the Y.Doc | Awareness state (cursors, selection) lives in a separate `Awareness` object that is not persisted by default. Applications that persist `Y.Doc` state but not awareness state lose cursor positions on reload — this is intentional but surprises new users. |
| `@liveblocks/yjs` subdocument gap | As noted above, the Liveblocks Yjs provider did not support subdocuments at initial release (verify current). |

### Automerge 2

Automerge 2 (`@automerge/automerge`) is a Rust-compiled WASM port with significantly better performance than Automerge 1.

| Trap | Detail |
|------|--------|
| WASM bundle size | The WASM binary is ~500 KB before gzip. For mobile web or edge-deployed workers, this is a meaningful cold-start cost. |
| `automerge-repo` is a separate package | `@automerge/automerge-repo` provides sync, storage, and network adapters. The core `@automerge/automerge` package alone does not handle network sync. Do not conflate the two in architecture documentation. |
| No operational transform compatibility | Automerge and Yjs documents are not interchangeable. A system that starts with Yjs cannot migrate existing documents to Automerge without a full re-encode. |
| Text type API changed in 2.x | Automerge 2 text is now a native string type, not a `Text` object. Code written against Automerge 1's `getText()` / `insertAt()` API will not compile against v2. |

### Loro

Loro is a CRDT library (Rust/WASM, with Swift and Python bindings) with a focus on rich text and version history as first-class features. It passed 1.0 in 2025 and was iterating past v1.13.x by mid-2026 (verify current) — the API-instability objection from Loro's pre-1.0 era no longer holds, but ecosystem gaps remain.

| Trap | Detail |
|------|--------|
| No mature hosted-provider ecosystem | Unlike Yjs (y-websocket, y-webrtc, y-partykit, y-indexeddb) or automerge-repo, Loro still does not ship a ready-made sync provider as of mid-2026 (verify current). You write the transport integration yourself — budget for this in the estimate, not just the CRDT integration. |
| Version history storage overhead | Loro's version graph model stores more metadata than Yjs to enable true historical replay. For documents with high mutation rates, storage costs are higher than Yjs equivalents. |
| Rich text maturity | Loro's rich text support is a primary differentiator and has stabilized considerably post-1.0, but has materially less production track record than Yjs + ProseMirror/TipTap. For a team with zero CRDT experience shipping today, that track-record gap — not API stability — is the real risk to weigh. |
| Post-1.0 does not mean "same maturity as Yjs" | Passing 1.0 fixes the API-churn risk, not the ecosystem/production-track-record gap. Choosing Loro over Yjs is a legitimate call when snapshot size or version-history features are the priority — just don't justify it on "Loro is stable now" alone. |

---

## Cross-Vendor Decision Table

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| <500 CCU collaborative whiteboard, managed | Liveblocks v2 | Storage, presence, and CRDT in one API surface |
| 1k-10k CCU multiplayer, edge-first | PartyKit on Cloudflare | DO-native room model; shard above ~2k per room |
| Existing Supabase Postgres backend, add presence | Supabase Realtime Broadcast | No extra infra; watch channel and slot limits |
| Self-hosted Node.js multi-node chat | Socket.IO v4 + Redis adapter v8 | Mature, well-understood adapter model |
| Elixir stack, any scale | Phoenix Channels | Native process model; benchmark PubSub at >10k |
| Collaborative rich text, open-source | Yjs + y-websocket | Largest provider ecosystem; compact periodically |
| Collaborative rich text, version history / time-travel a priority | Loro | Past 1.0 as of mid-2026 (verify current); accept owning the sync-transport layer since no hosted provider exists yet |

---

## Anti-Patterns

**Using managed realtime for server-to-client only feeds.** SSE or simple HTTP long-polling is cheaper and simpler when there is no client-to-server messaging requirement. Paying for WebSocket connection infrastructure for a dashboard that only needs push updates is unnecessary.

**Treating channel limits as soft.** Supabase and Liveblocks both enforce hard channel or connection limits at plan tiers. Exceeding these in production causes silent JOIN rejections. Load test against plan limits before launch.

**Mixing CRDT awareness with document state.** Yjs awareness (cursors, typing indicators) is ephemeral. Persisting awareness state alongside Y.Doc updates causes stale cursor positions to rehydrate on reload and confuses conflict resolution.

**Skipping tombstone compaction on long-lived Yjs documents.** Documents used daily for months grow unboundedly without periodic compaction. Schedule compaction as a background job, not as a manual step.

**Choosing a CRDT library based on GitHub stars alone.** Loro's rise in stars reflects novelty. Yjs has more production integrations, more providers, and more documented edge cases. Evaluate on integration surface, not popularity.
