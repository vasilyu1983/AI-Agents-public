# Edge Real-Time Landscape

Platform choices, limits, and production traps for real-time collaborative systems running at the edge.

_Last verified: 2026-07-11._

## Table of Contents

- [PartyKit and Cloudflare Durable Objects](#partykit-and-cloudflare-durable-objects)
- [Liveblocks v2](#liveblocks-v2)
- [Supabase Realtime Channel Limits](#supabase-realtime-channel-limits)
- [Socket.IO v4 Adapter Notes](#socketio-v4-adapter-notes)
- [CRDT Picks: Yjs vs Loro](#crdt-picks-yjs-vs-loro)
- [Production Traps](#production-traps)

---

## PartyKit and Cloudflare Durable Objects

**PartyKit** (acquired by Cloudflare, 2024) wraps Durable Objects (DOs) with a higher-level party/room abstraction. Current behavior:

- Each `PartyServer` instance maps 1:1 to a Cloudflare Durable Object
- DOs provide **strongly consistent single-threaded execution** — safe for presence counters without locks
- **Hibernation API** (`this.ctx.waitUntil`) keeps DOs alive for async work without billing idle compute
- WebSocket messages enter the DO serially; no need for mutex but beware blocking the event loop

**Hard limits (Cloudflare, verify current):**

| Limit | Value |
|-------|-------|
| Max WebSocket connections per DO | 32,768 |
| Max storage per DO | 128 GB |
| CPU time per request | 30 s (wall), unlimited with hibernation |
| DO alarm granularity | 500 ms |

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

## Liveblocks v2

Liveblocks v2 (GA January 2025) restructured the SDK into separate packages:

```bash
npm install @liveblocks/client @liveblocks/react @liveblocks/node
```

**Breaking changes from v1:**

- `createClient` moved to `@liveblocks/client`; v1 root import no longer works
- `useRoom` hook removed; use `useMyPresence`, `useOthers`, `useStorage` directly
- Yjs integration is now a first-class `@liveblocks/yjs` package (replaces manual binding)
- REST API v2 endpoints: `/v2/rooms/{roomId}/storage` (v1 path `/v1/...` still active but deprecated)

**Connection limits (Liveblocks, verify current — pricing pages change often and third-party summaries disagree; confirm at liveblocks.io/pricing before quoting a number):**

| Plan | Monthly price (annual/monthly) | Max simultaneous connections *per room* | Anonymous connections/month |
|------|-------------------------------|------------------------------------------|------------------------------|
| Free | $0 | 10 | shared cap across plan |
| Pro | $25 / $30 | 20 | 3,000 (shared cap, verify current) |
| Team | $500-3,125 / $600-3,750 | 50 | 3,000 (shared cap, verify current) |
| Enterprise | Custom | 100 (custom above) | Custom |

Per-project simultaneous connections are effectively unlimited on every tier — the binding constraint is connections *within a single room*, which is the number that matters for CCU-per-document sizing. Liveblocks bills primarily on MAU, not raw connection count, so high connection-churn/low-MAU apps (e.g., short-lived anonymous sessions) are cheaper than the room-connection ceiling alone suggests.

---

## Supabase Realtime Channel Limits

Supabase Realtime uses Phoenix Channels over WebSocket. Relevant limits (verify current at supabase.com/docs/guides/realtime/limits and supabase.com/docs/guides/realtime/pricing — Supabase moved to peak-connection and message-volume billing rather than flat per-tier connection caps):

| Tier | Included concurrent connections | Overage pricing |
|------|----------------------------------|------------------|
| Free | 200 | not available; upgrade required |
| Pro | 500 | $10 per 1,000 additional peak connections; $2.50 per 1M additional messages |
| Team / Enterprise | Custom | Custom |

Peak-connection billing is measured as the single highest concurrent-connection count during the billing cycle per project, not an average — a short spike sets the bill for the whole period. Message cost is billed separately from connection cost, so a low-connection-count, high-message-rate broadcast channel (e.g., a hot presence channel) can cost more than the connection count alone suggests.

**Presence payload size limit:** 10 KB per client state object — exceeded commonly with large user metadata (verify current).

**Channel naming:** Prefix with a namespace to avoid cross-tenant leakage in multi-tenant apps:

```ts
const channel = supabase.channel(`tenant:${tenantId}:room:${roomId}`);
```

**RLS on Realtime:** Row-Level Security is enforced for Postgres Changes subscriptions (`INSERT/UPDATE/DELETE`) but **not** for Broadcast or Presence. Add application-level auth checks for those.

---

## Socket.IO v4 Adapter Notes

Socket.IO v4 is current LTS (v4.8.3 as of late 2025/mid-2026, verify current) and requires explicit adapter choice for multi-node deployments:

| Adapter | Package | Use case |
|---------|---------|----------|
| Redis | `@socket.io/redis-adapter` | Standard multi-node; uses Pub/Sub |
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
- **Maturity:** Production-proven; used by Notion, Figma (historically), Linear
- **Providers:** `y-websocket`, `y-webrtc`, `y-partykit`, `y-supabase`
- **Bundle size:** ~24 KB gzip

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
- **Maturity:** Passed 1.0 in 2025 and is now iterating past v1.13.x (as of mid-2026) — the API itself is no longer pre-1.0-unstable, but the ecosystem is still thin: no ready-made hosted sync provider comparable to `y-websocket`/`y-partykit`, so teams write their own transport integration (verify current before treating this gap as closed)
- **Differentiation:** Smaller encoded snapshot size (~30–50% vs Yjs for rich documents); fractional indexing built-in
- **Use when:** You need version snapshots, time-travel, or smaller wire size, and the team can own the sync-transport layer itself

**Pick Yjs** when ecosystem compatibility (hosted providers, editor bindings, prior production track record) matters more than raw feature set.
**Pick Loro** when snapshot size, time-travel/version history, or Rust-native integration are primary requirements and the team is comfortable building its own sync transport — the API-stability objection that applied pre-2025 no longer holds, but the "no off-the-shelf provider" gap still does.

---

## Production Traps

- **PartyKit cold-start latency:** DOs start cold in ~100 ms (edge) but first WebSocket frame can take 300–500 ms if Hibernation wakes from storage. Pre-warm critical rooms with a scheduled alarm.
- **Liveblocks v2 `@liveblocks/yjs` conflict resolution:** Yjs updates are applied optimistically on the client; server canonical state reconciles asynchronously. Do not read `doc.toJSON()` immediately after a remote update — subscribe to `doc.on('update', ...)`.
- **Supabase Realtime `429` on Free tier:** Broadcast `rate_limit` is per-channel, not per-connection. A single high-frequency channel from many senders saturates the limit; shard across channels or upgrade.
- **Socket.IO sticky sessions:** Without sticky sessions (IP hash or cookie) on a load balancer, HTTP long-polling fallback breaks. Always configure sticky sessions or disable `polling` transport.
- **Yjs provider ordering:** Connecting multiple providers to the same `Y.Doc` without awareness sync (`y-protocols/awareness`) causes presence state collisions.
