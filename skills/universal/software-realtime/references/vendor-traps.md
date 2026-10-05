# Real-Time Vendor Traps

Vendor versions, limits and prices change often. Each trap names what to check; read the linked vendor docs for current values before quoting them.

## Table of Contents

- [PartyKit (Cloudflare)](#partykit-cloudflare)
- [Liveblocks](#liveblocks)
- [Supabase Realtime](#supabase-realtime)
- [Socket.IO v4 Adapter Changes](#socketio-v4-adapter-changes)
- [Cloudflare Durable Objects + WebSockets](#cloudflare-durable-objects--websockets)
- [Phoenix / LiveView](#phoenix--liveview)
- [CRDT Options: Yjs, Automerge 3, Loro](#crdt-options-yjs-automerge-3-loro)
- [Cross-Vendor Decision Table](#cross-vendor-decision-table)
- [Anti-Patterns](#anti-patterns)

---

## PartyKit (Cloudflare)

PartyKit runs on Cloudflare Durable Objects. It is a strong, low-friction path to a globally distributed WebSocket room with shared state, but it inherits all Durable Object constraints.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Hot room execution | A room maps to one DO, so its message path can saturate that object. JavaScript runs on one thread, but `await` on external I/O permits interleaving; use storage operations or transactions for atomic state changes. Measure before sharding. [Cloudflare input-gate guidance](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/) |
| Storage value size | Backends have different key/value and total-storage limits. Check the [current DO limits](https://developers.cloudflare.com/durable-objects/platform/limits/) before choosing inline snapshots or R2. |
| Cold-start latency | Durable Objects evict after inactivity, and a hibernated DO re-runs its constructor when an event arrives. Cloudflare publishes no cold-start figure — measure first-frame latency, keep constructors light, and design reconnect UI to tolerate the delay. |
| WebSocket hibernation API | Check whether the selected PartyKit or PartyServer path accepts sockets through the [Hibernation API](https://developers.cloudflare.com/durable-objects/best-practices/websockets/); do not infer billing from use of a broadcast helper. |
| No multi-region active-active | A DO instance lives in one region at a time. Cloudflare routes to it, but two clients on opposite sides of the world both pay cross-region latency to reach that single instance. For latency-sensitive multiplayer, measure actual round-trips before committing. |
| Package upgrades | Read the selected package's changelog and lock the tested dependency set. |

---

## Liveblocks

Check npm for the current Liveblocks major and follow the official upgrade guides major by major rather than jumping versions.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Client throttle | The client WebSocket `throttle` applies to all client updates, not only presence. Check its default and allowed range in the client API reference, lower it deliberately for cursor-heavy UIs, and measure the message-volume cost. |
| Yjs integration via `@liveblocks/yjs` | The `@liveblocks/yjs` provider replaces y-websocket. Subdocument support was limited at initial release — check the current docs before relying on subdocuments. |
| Major-version upgrades | Webhook payloads, connection-status values and pricing have changed across majors; this file does not pin them. Read the upgrade guide and pricing page for your target version. |

---

## Supabase Realtime

Supabase Realtime uses Phoenix Channels under the hood. The managed service imposes connection, channel and message limits that differ between plans (supabase.com/docs/guides/realtime/limits).

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Connection and channel limits | Plans cap concurrent **connections** per project and, separately, **channels per connection** — read the limits page for current values and do not confuse the two. Load-test against the connection limit, and check how your client surfaces a rejected join. |
| Broadcast vs Postgres changes | Broadcast messages are ephemeral — no durability guarantee. Postgres Changes are driven by database changes. Mixing both in one subscription creates confusion about delivery semantics. |
| Postgres Changes throughput | Changes are processed on a single thread and each change runs one authorization check per subscriber, so cost scales with subscribers × change rate. The docs name a subscriber count above which to use Broadcast instead; check it before designing a high-fan-out feed on Postgres Changes. |
| Register handlers before `subscribe()` | `RealtimeChannel.subscribe()` returns the `RealtimeChannel` (realtime-js source). Attach `.on(...)` handlers before calling `.subscribe()`, and use the subscribe status callback to detect join failures. |
| Presence clock drift | Do not compare presence timestamps to local `Date.now()`; client clocks drift, so measure the offset rather than assuming a figure. |
| Authorization on Broadcast/Presence | Private channels are authorized by RLS policies on `realtime.messages` (Realtime Authorization); public channels are not authorized at all. Treating a public Broadcast channel as authenticated is a security misconfiguration. |

---

## Socket.IO v4 Adapter Changes

Socket.IO v4 is stable; adapter choice matters more than the minor version (socket.io/docs/v4/redis-adapter).

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Redis adapter client and sharding | `@socket.io/redis-adapter` works with both the `redis` and `ioredis` clients. The docs warn that `redis` has had problems restoring subscriptions after reconnection — test reconnect or use `ioredis`. For new work on Redis 7+, the docs recommend the sharded adapter (`createShardedAdapter`, sharded Pub/Sub). |
| Cluster adapter scope | `@socket.io/cluster-adapter` targets the Node.js cluster module on one machine; it does not span hosts. |
| Postgres adapter `pg` peer dependency | Check `@socket.io/postgres-adapter`'s declared `pg` peer range before deploying. |
| Sticky sessions still required | Socket.IO HTTP long-polling requires sticky sessions on the load balancer. WebSocket-only mode avoids that requirement, but loses polling fallback. Configure `transports: ['websocket']` on both client and server when stickiness is unavailable; verify current [Socket.IO deployment guidance](https://socket.io/docs/v4/using-multiple-nodes/). |
| `maxHttpBufferSize` | Default is 1 MB (`1e6`) per the server-options docs. Messages larger than this close the connection; set it explicitly for large binary frames (images, audio chunks), and keep it low on public endpoints to limit memory DoS. |

---

## Cloudflare Durable Objects + WebSockets

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| Hibernation API is opt-in | Without `ctx.acceptWebSocket()` (Hibernation API), each open WebSocket keeps the DO in memory and billing duration. The cost difference depends on idle ratio — model it rather than assume a multiple. |
| Request rate per DO | Each DO has a *soft* per-object requests-per-second limit (see the DO limits page). At high CCU, shard hot rooms across DOs rather than relying on one object. |
| Alarms vs WebSocket ping | Use DO alarms to drive periodic state flushes, not server-side WebSocket ping/pong. With hibernation, configure `setWebSocketAutoResponse` for keepalives so pings do not wake the DO. |
| `--remote` dev flag cost | Running `wrangler dev --remote` against production DOs during development is billed. Use `--local` for development and verify the hibernation code path with an integration test. |
| Storage consistency | DO transactional storage provides serializable isolation per DO but not across DOs. Applications that shard rooms across multiple DOs and need cross-shard consistency must implement their own coordination layer. |

---

## Phoenix / LiveView

Phoenix Channels are battle-tested but LiveView introduced stateful server-side components that interact with channels in non-obvious ways.

**Version-pinned gotchas (verify current)**

| Trap | Detail |
|------|--------|
| LiveView `handle_info` blocking assigns | `handle_info/2` is synchronous per LiveView process. Long-running operations in `handle_info` block all state updates for that connected client. Offload to `Task.async` and handle the result via `send`. |
| PubSub fan-out at scale | `Phoenix.PubSub`'s default adapter is `Phoenix.PubSub.PG2`. Very hot topics can create mailbox pressure; benchmark and shard hot topics. |
| LiveView dead render vs live render | Pages that rely on LiveView for initial render do not receive JavaScript hook events until the live socket connects. Avoid putting critical interactive behavior in hooks that depend on immediate socket availability. |
| Cluster node isolation | Check the chosen PubSub adapter and cluster discovery setup; exercise node loss and rejoin before relying on cross-node fan-out. |

---

## CRDT Options: Yjs, Automerge 3, Loro

### Yjs

The dominant CRDT library for collaborative editing. Mature, well-integrated, but has known scaling constraints.

| Trap | Detail |
|------|--------|
| Document size growth | `Y.Doc` garbage-collects deleted content by default (`gc: true`; [Yjs docs](https://docs.yjs.dev/api/y.doc)). Measure encoded size on real long-lived documents, especially when `gc: false` is needed for history; do not promise that re-encoding compacts all metadata. |
| Subdocument support | Subdocuments work but are sparsely documented. Providers (y-websocket, y-webrtc) handle subdocuments inconsistently. Test load and sync of subdocuments explicitly. |
| Awareness is not in the Y.Doc | Awareness state (cursors, selection) lives in a separate `Awareness` object that is not persisted by default. Applications that persist `Y.Doc` state but not awareness state lose cursor positions on reload — this is intentional but surprises new users. |
| `@liveblocks/yjs` subdocument gap | As noted above, the Liveblocks Yjs provider did not support subdocuments at initial release (verify current). |

### Automerge 3

Automerge (`@automerge/automerge`) is a Rust core compiled to WASM. Automerge 3.0 cut memory use by over 10x versus 2.x (automerge.org/blog/automerge-3), so older "Automerge is too heavy" verdicts need re-measuring.

| Trap | Detail |
|------|--------|
| WASM bundle size | The WASM binary is a real cold-start cost for mobile web or edge workers — measure it for your build (a specific size figure is not pinned here). |
| `automerge-repo` is a separate package | `@automerge/automerge-repo` provides sync, storage, and network adapters. The core `@automerge/automerge` package alone does not handle network sync. Do not conflate the two in architecture documentation. |
| No operational transform compatibility | Automerge and Yjs documents are not interchangeable. A system that starts with Yjs cannot migrate existing documents to Automerge without a full re-encode. |
| Major-version API changes | Text and document APIs changed between Automerge 1, 2 and 3. Follow the migration notes for each major; do not mix examples written for different majors. |

### Loro

Loro is a CRDT library (Rust/WASM, with Swift and Python bindings) with a focus on rich text and version history as first-class features. It is post-1.0 (`loro-crdt` 1.x), so the API-instability objection from the pre-1.0 era no longer holds, but ecosystem gaps remain.

| Trap | Detail |
|------|--------|
| Young sync ecosystem | Loro now has first-party sync pieces — the Loro Protocol (`loro-protocol`), `loro-websocket` (client + simple server) and `loro-adaptors` — but they are 0.x and far less battle-tested than Yjs providers (y-websocket, y-webrtc, y-partykit, y-indexeddb) or automerge-repo. Budget for hardening the transport, not just the CRDT integration. |
| Version history storage overhead | Benchmark encoded documents and history retention under your edit pattern; do not assume Loro or Yjs is smaller across workloads. |
| Rich text maturity | Loro's rich text support is a primary differentiator and has stabilized considerably post-1.0, but has materially less production track record than Yjs + ProseMirror/TipTap. For a team with zero CRDT experience shipping today, that track-record gap — not API stability — is the real risk to weigh. |
| Post-1.0 does not mean "same maturity as Yjs" | Passing 1.0 fixes the API-churn risk, not the ecosystem/production-track-record gap. Choosing Loro over Yjs is a legitimate call when snapshot size or version-history features are the priority — just don't justify it on "Loro is stable now" alone. |

---

## Cross-Vendor Decision Table

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| Managed collaborative whiteboard | Liveblocks | Storage and presence in one API surface; check per-room limits |
| Edge-first multiplayer | PartyKit or PartyServer on Cloudflare | DO-native room model; shard at measured room limits |
| Existing Supabase Postgres backend, add presence | Supabase Realtime Broadcast/Presence on private channels | No extra infra; watch the connection limit and Realtime Authorization policies |
| Self-hosted Node.js multi-node chat | Socket.IO v4 + Redis adapter (sharded on Redis 7+) | Mature, well-understood adapter model |
| Elixir stack | Phoenix Channels | Native process model; benchmark PubSub on the target workload |
| Collaborative rich text, open-source | Yjs + y-websocket | Largest provider ecosystem; monitor document growth |
| Collaborative rich text, version history / time-travel a priority | Loro | Post-1.0 API; sync via the young (0.x) Loro Protocol / `loro-websocket` — budget for hardening it |

---

## Anti-Patterns

**Using managed realtime for server-to-client only feeds.** SSE or simple HTTP long-polling is cheaper and simpler when there is no client-to-server messaging requirement. Paying for WebSocket connection infrastructure for a dashboard that only needs push updates is unnecessary.

**Treating plan limits as soft.** Supabase and Liveblocks both enforce connection limits at plan tiers. Load test against plan limits before launch and verify how your client surfaces a rejected join.

**Mixing CRDT awareness with document state.** Yjs awareness (cursors, typing indicators) is ephemeral. Persisting awareness state alongside Y.Doc updates causes stale cursor positions to rehydrate on reload and confuses conflict resolution.

**Not monitoring long-lived Yjs document size.** GC is on by default; measure encoded size and alert on outliers instead of assuming a compaction job fixes every growth pattern.

**Choosing a CRDT library based on GitHub stars alone.** Loro's rise in stars reflects novelty. Yjs has more production integrations, more providers, and more documented edge cases. Evaluate on integration surface, not popularity.
