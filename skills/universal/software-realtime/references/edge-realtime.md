# Edge Real-Time Landscape

Platform choices, limits, and production traps for real-time collaborative systems running at the edge.

Vendor limits, prices and versions change often. This file names which limits matter and why; read the linked vendor page for current values before sizing or quoting.

## Table of Contents

- [PartyKit and Cloudflare Durable Objects](#partykit-and-cloudflare-durable-objects)
- [Liveblocks](#liveblocks)
- [Supabase Realtime Channel Limits](#supabase-realtime-channel-limits)
- [Socket.IO v4 Adapter Notes](#socketio-v4-adapter-notes)
- [CRDT Picks: Yjs vs Loro](#crdt-picks-yjs-vs-loro)
- [Production Traps](#production-traps)

---

## PartyKit and Cloudflare Durable Objects

**PartyKit** (acquired by Cloudflare, 2024) wraps Durable Objects (DOs) with a higher-level party/room abstraction. Current behavior:

For a Workers-native project, also evaluate [PartyServer](https://github.com/cloudflare/partykit/blob/main/packages/partyserver/README.md) and its [y-partyserver](https://github.com/cloudflare/partykit/blob/main/packages/y-partyserver/README.md) Yjs addon. Check the maintained package and migration docs before choosing between PartyKit and PartyServer.

- Each `PartyServer` instance maps 1:1 to a Cloudflare Durable Object
- Each DO has strongly consistent storage and a single JavaScript thread. `await` on external I/O can still interleave requests; use storage operations or transactions for atomic counters, and recheck state after external calls. See Cloudflare's [input-gate guidance](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/).
- **WebSocket Hibernation API** (`ctx.acceptWebSocket(ws)` instead of `ws.accept()`) lets the DO be evicted from memory while clients stay connected, so idle connections do not bill duration. `ctx.waitUntil` is unrelated — it is not the hibernation API. Only server-side (accepted) WebSockets hibernate; outbound WebSockets opened by a DO do not
- A single room's hot message path can bottleneck on its DO; measure it before sharding.

**Limits to look up before sizing** (developers.cloudflare.com/durable-objects/platform/limits/ and the DO State API `acceptWebSocket` section):

| Limit | Why it matters |
|-------|----------------|
| WebSocket connections per DO (Hibernation API) | Caps CCU per room instance; beyond it, shard the room |
| Storage per object and per account — differs by backend (SQLite-backed vs legacy KV-backed) | Decides whether snapshots live in DO storage or R2 |
| Key/value size — differs by backend | Inline document snapshots can exceed it; chunk or offload |
| CPU per request (CPU time, not wall time; configurable via `cpu_ms`) | Long merges or snapshot encodes must fit the budget |
| Requests per second per object (a *soft* limit) | Hot rooms need application-level sharding |

Alarm timing granularity is not a published limit — measure it rather than design around a number.

**PartyKit-specific:**

```ts
// server.ts
import type * as Party from 'partykit/server';

export default class Room implements Party.Server {
  constructor(readonly room: Party.Room) {}

  onConnect(conn: Party.Connection) {
    // broadcast to all except sender
    this.room.broadcast(`${conn.id} joined`, [conn.id]);
  }

  onMessage(message: string, sender: Party.Connection) {
    this.room.broadcast(message, [sender.id]);
  }
}
```

---

## Liveblocks

Check npm and the Liveblocks upgrade guides for the current major before writing code; follow upgrades major by major. The SDK is split into separate packages:

```bash
npm install @liveblocks/client @liveblocks/react @liveblocks/node
```

**Notes (verify against the Liveblocks upgrade guides for your version):**

- Hooks such as `useRoom`, `useMyPresence`, `useOthers`, `useStorage` are current API (`useRoom` returns the Room of the nearest `RoomProvider`)
- Yjs integration is the `@liveblocks/yjs` package
- The client WebSocket `throttle` setting applies to all client updates, not just presence; check its default and allowed range in the client API reference before tuning cursor-heavy UIs

**Connection limits and pricing:** plan limits (connections per room, MAU caps, prices) change often and third-party summaries disagree. Read liveblocks.io/pricing before quoting any number; the skill does not pin them. The number that matters for CCU-per-document sizing is the per-room simultaneous-connection limit.

---

## Supabase Realtime Channel Limits

Supabase Realtime uses Phoenix Channels over WebSocket. Relevant limits (read supabase.com/docs/guides/realtime/limits and supabase.com/docs/guides/realtime/pricing for current values):

- Limits are per plan and come in two separate dimensions: concurrent **connections** per project and **channels per connection**. Do not read a connection cap as a channel cap.
- Billing is on peak connections and message volume; read the pricing page for current rates.
- Postgres Changes are processed on a single thread with one authorization check per subscriber, so cost scales with subscribers × change rate. The docs name a subscriber count above which to use Broadcast instead — check it before designing a high-fan-out feed on Postgres Changes.

Peak-connection billing is measured as the single highest concurrent-connection count during the billing cycle per project, not an average — a short spike sets the bill for the whole period. Message cost is billed separately from connection cost, so a low-connection-count, high-message-rate broadcast channel (e.g., a hot presence channel) can cost more than the connection count alone suggests.

**Presence payload size limit:** each client's presence state has a size cap (see the limits page); large user metadata commonly exceeds it, so keep presence to IDs and cursor state and fetch profiles separately.

**Channel naming:** Prefix with a namespace to avoid cross-tenant leakage in multi-tenant apps:

```ts
const channel = supabase.channel(`tenant:${tenantId}:room:${roomId}`);
```

**RLS on Realtime:** Postgres Changes respect table RLS. Broadcast and Presence are authorized through **Realtime Authorization**: RLS policies on the `realtime.messages` table gate *private* channels (disable "Allow public access" in Realtime settings). Public channels have no authorization — do not treat them as authenticated (supabase.com/docs/guides/realtime/authorization).

---

## Socket.IO v4 Adapter Notes

Socket.IO v4 (check npm for the current release) requires explicit adapter choice for multi-node deployments:

| Adapter | Package | Use case |
|---------|---------|----------|
| Redis | `@socket.io/redis-adapter` | Standard multi-node; uses Pub/Sub; works with the `redis` or `ioredis` client. For new work on Redis 7+, the docs recommend the sharded adapter (`createShardedAdapter`, sharded Pub/Sub). The docs warn the `redis` package has had problems restoring subscriptions after reconnection — test reconnect, or use `ioredis` |
| Redis Streams | `@socket.io/redis-streams-adapter` | Delivery guarantees, message history |
| Postgres | `@socket.io/postgres-adapter` | When Redis is unavailable |
| Cluster | `@socket.io/cluster-adapter` | Single machine multi-process only |

```ts
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);
io.adapter(createAdapter(pubClient, subClient));
```

**v4 breaking changes from v3:**

- `socket.rooms` is now a `Set<string>` (was `object`)
- Namespace middleware no longer receives `next` with error argument; throw instead
- `socket.request.headers` is undefined if `allowRequest` rejects before upgrade

---

## CRDT Picks: Yjs vs Loro

### Yjs

- **Language:** JavaScript/TypeScript (WASM ports for other runtimes)
- **Model:** YATA algorithm; shared types (`Y.Text`, `Y.Map`, `Y.Array`)
- **Maturity:** Production-proven, with the largest provider and editor-binding ecosystem
- **Providers:** `y-websocket`, `y-webrtc`, `y-partykit`, `y-supabase`
- **Bundle size:** small; measure it with your bundler
- **GC:** `Y.Doc` garbage-collects deleted content by default (`gc: true`); set `gc: false` only when you need snapshots/version history

```ts
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const doc = new Y.Doc();
const provider = new WebsocketProvider('wss://y.example.com', 'room-id', doc);
const text = doc.getText('content');
text.insert(0, 'Hello');
```

### Loro

- **Language:** Rust core, WASM + JS bindings (`loro-crdt` npm package), also published for Swift and Python
- **Model:** Peritext-inspired; richer undo/redo semantics; time-travel to any version
- **Maturity:** Post-1.0 (`loro-crdt` 1.x) — the API is no longer pre-1.0-unstable. Sync now has first-party pieces: the Loro Protocol (`loro-protocol`), `loro-websocket` (WebSocket client + simple server) and `loro-adaptors`. These are young (0.x) compared with `y-websocket`/`y-partykit`, so budget for integration and hardening
- **Differentiation:** Compact encoded snapshots (benchmark on your own documents before relying on a size advantage); fractional indexing built-in
- **Use when:** You need version snapshots, time-travel, or smaller wire size, and the team can own hardening a young (0.x) sync layer

**Pick Yjs** when ecosystem compatibility (hosted providers, editor bindings, prior production track record) matters more than raw feature set.
**Pick Loro** when snapshot size, time-travel/version history, or Rust-native integration are primary requirements — the API-stability objection from the pre-1.0 era no longer holds, and the sync gap has narrowed to "young 0.x provider" rather than "no provider".

**Automerge 3** (`@automerge/automerge` 3.x) cut memory use by over 10x versus Automerge 2 (automerge.org/blog/automerge-3), which weakens the old "Automerge is heavy" objection; sync lives in `@automerge/automerge-repo`.

---

## Production Traps

- **PartyKit / DO cold-start latency:** an evicted DO pays a cold start on the next request, and a hibernated DO re-runs its constructor on wake. Cloudflare publishes no cold-start figure — measure first-frame latency and design the reconnect UI to tolerate it.
- **Liveblocks `@liveblocks/yjs` conflict resolution:** Yjs updates are applied optimistically on the client; server canonical state reconciles asynchronously. Do not read `doc.toJSON()` immediately after a remote update — subscribe to `doc.on('update', ...)`.
- **Supabase Realtime limit errors:** read the current [limits](https://supabase.com/docs/guides/realtime/limits/) and distinguish connections, channels per connection, and message throughput before changing channel topology.
- **Socket.IO sticky sessions:** Without sticky sessions (IP hash or cookie) on a load balancer, HTTP long-polling fallback breaks. Always configure sticky sessions or disable `polling` transport.
- **Yjs provider ordering:** Connecting multiple providers to the same `Y.Doc` without awareness sync (`y-protocols/awareness`) causes presence state collisions.
