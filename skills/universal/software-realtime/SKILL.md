---
name: software-realtime
description: "Designs real-time and collaborative systems. Use when building chat, presence, live dashboards, collaborative editing, WebSockets, SSE, WebTransport, or local-first sync."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Real-Time Systems

Use this skill for transport choice, collaborative-state design, presence models, reconnection behavior, and multi-node real-time scaling. It owns SSE, WebSocket, CRDT, and managed real-time decisions, not generic backend APIs or frontend-only state management.

## Quick Reference

| Task | Use |
|------|-----|
| Transport selection | [references/transport-selection.md](references/transport-selection.md) |
| Collaboration, presence, and recovery | [references/collaboration-patterns.md](references/collaboration-patterns.md) |
| Vendor traps and version-pinned gotchas | [references/vendor-traps.md](references/vendor-traps.md) |
| Edge platforms, CRDT picks, channel limits | [references/edge-realtime.md](references/edge-realtime.md) | PartyKit, Liveblocks, Supabase, Socket.IO v4, Yjs/Loro/Automerge |
| WebSocket handshake, message, and second-connection checks | [scripts/check_ws_smoke.py](scripts/check_ws_smoke.py) | message checks require `websockets`; set a workload-specific timeout |
| Source map | [data/sources.json](data/sources.json) |

## When to Use This Skill

- Choose between SSE, WebSocket, managed real-time, or CRDT collaboration.
- Choose a local-first relational sync engine, or test WebTransport suitability.
- Design chat, live dashboards, notifications, presence, or collaborative editing.
- Plan reconnection, backpressure, offline queues, and connection lifecycle.
- Scale WebSocket or collaboration infrastructure across multiple nodes.

## Route Elsewhere

- Request-response APIs or background jobs: use [software-backend](../software-backend/SKILL.md).
- System-level event architecture: use [software-architecture-design](../software-architecture-design/SKILL.md).
- Frontend state-management-only questions: use [software-frontend](../software-frontend/SKILL.md).
- Mobile push-notification delivery: use [software-mobile](../software-mobile/SKILL.md).
- Streaming AI response UX: use [software-ai-integration](../software-ai-integration/SKILL.md).

## Defaults

- Default to SSE for one-way text/event streaming.
- Default to WebSocket for bidirectional interactive flows.
- Default to CRDTs for collaborative editing and keep awareness separate from document state.
- Use a Postgres-backed sync engine for relational app data when the server owns permissions and a client needs an offline partial replica; choose its auth and conflict policy explicitly.
- Treat presence as its own data model with throttling and expiry rules.
- Design reconnects, idempotency, and slow-consumer handling before worrying about horizontal scale.

## Workflow

1. Classify the real-time shape: one-way stream, bidirectional messaging, shared collaborative state, or managed service need.
2. Choose the transport or collaboration model before touching implementation detail.
3. Define connection lifecycle, Origin policy and auth handoff, retries, presence semantics, and durability.
4. Add multi-node fan-out and recovery only after the single-node model is sound.
5. Verify current library or vendor behavior before final recommendations when the choice is version-sensitive.

## Core Decisions

### Transport Choice

| Use Case | Transport | Reason |
|----------|-----------|--------|
| Dashboards, feeds, notifications | SSE | One-way, HTTP-native, browser handles reconnect |
| Chat, multiplayer, live cursors, client-originated messages | WebSocket | Bidirectional session required |
| Sub-frame media/game state where occasional loss beats head-of-line blocking | WebTransport | Unreliable + unordered datagrams over QUIC; check its current Baseline status and browser support before committing infra |
| Peer-to-peer audio/video or direct browser-to-browser data | WebRTC (media tracks or data channels) | Budget for TURN relay and consider an SFU when mesh upload grows with participants |
| Shared documents / state that must merge under concurrency | CRDT-backed collaboration | Avoids hand-rolled merge logic |
| Team owns connection infra as a core advantage | Custom WebSocket + pub/sub | Full control |
| Team wants to avoid connection layer ops | Managed pub/sub (Ably, Pusher, Supabase Realtime, PartyKit) or serverless WebSocket (AWS API Gateway WebSocket, Azure Web PubSub) | Faster path, vendor limits apply |

**WebTransport reality check:** check browser support and test the selected server, CDN, load balancer, and proxy path. If datagrams are required, verify that the negotiated mode supports unreliable delivery; a reliable-only fallback will not meet that need. Default to WebSocket unless the workload needs datagrams or independent streams, and retain a tested fallback where the required mode is unavailable.

**Relational sync vs document collaboration:** Zero syncs server-authorized queries, Electric syncs Postgres shapes, and PowerSync Sync Streams select an offline SQLite replica. These fit relational app state and partial offline reads; use a CRDT for free-form concurrent document edits. Check each engine's current query scope, permission enforcement, write/conflict path, and deployment model before choosing. See [collaboration patterns](references/collaboration-patterns.md).

### Collaboration and Presence

- Use CRDTs (Yjs, Loro) over hand-rolled merge semantics; merge bugs are subtle and rare.
- Keep awareness data (cursors, typing, online status) in a separate `provider.awareness` object, not in the durable document.
- Coalesce cursor updates to a measured rate; avoid broadcasting every pointer event.
- Plan storage, sync, and recovery as a single design decision — retrofitting recovery after storage is built is expensive.

### Connection Management

**Reconnect and resync contract.**

Give each durable update a monotonic sequence or cursor and each client operation a stable ID. On reconnect, the client sends its last applied cursor; the server returns the missing range or a fresh snapshot plus a new cursor. Define retention expiry explicitly: when the gap is no longer replayable, force snapshot resync instead of pretending the live stream is complete.

- Reconnect with jitter and a retry cap; on mass disconnects, spread admission and honor server-directed retry delay.
- Browser WebSocket APIs cannot set arbitrary request headers; the handshake still carries cookies. Prefer a short-lived, single-use ticket issued over authenticated HTTPS and redeemed at the handshake, or authenticate the first message before joining any channel. Avoid long-lived query tokens because URLs can enter logs. For cookie auth, allowlist `Origin` on every handshake to block cross-site WebSocket hijacking; Origin alone does not authenticate non-browser clients. Check authorization again on each room join and action. [OWASP guidance](https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html).
- Derive heartbeat and dead-connection timers from the shortest intermediary idle timeout.
- Slow consumers: bound per-client outbound queues. Coalesce latest-value state by key (for example cursor/price), but never drop durable operations; force resync if the replay gap expires.
- Offline queues: assign stable `op_id` to each outbound message for idempotent replay; cap queue size and surface an error if exceeded.

**Heartbeat interval budget (re-derive from your own proxy/LB idle timeout, never reuse this number):** if the tightest intermediary idle timeout in the path (LB, corporate proxy, CDN) is 60s, send heartbeats at ≤ half that (≤30s) so at least one heartbeat lands before the timeout fires even under jitter; set server-side dead-connection detection at 2–3× the heartbeat interval (60–90s here) so one dropped heartbeat frame does not trigger a false disconnect.

**Connection memory sizing:** measure socket buffers, auth/subscription state, and the bounded outbound queue under representative load. Check file descriptors and network limits separately from memory.

### Scaling

- WebSocket fleets: shared pub/sub (Redis, NATS) plus sticky-session-aware load balancing (or stateless room routing).
- Presence and room membership: must work across nodes — do not store room state only in process memory.
- Deployments: plan graceful client reconnect on rolling restarts, not just health-check wiring.
- Sticky sessions are a load-balancer contract, not a WebSocket protocol feature: pick IP-hash or cookie-based affinity, and confirm the LB supports **connection draining** (finish in-flight connections before removal) before every deploy — without it, rolling restarts hard-kill live sessions instead of letting clients reconnect gracefully.
- Broker choice for fan-out is a durability decision: Redis Pub/Sub loses messages for disconnected subscribers; Redis Streams adds consumer groups and replay; Kafka fits retained, partition-ordered streams consumed by independent systems. Keep ephemeral presence off a retained log unless another requirement needs it.

**Fan-out math:** for N subscribed clients each receiving M messages per second, budget N × M outbound sends per second before framing and TLS. Measure broker and egress capacity at your payload size; shard hot rooms when the measured ceiling approaches demand.

## Output Modes

- Transport decision memo:
  SSE, WebSocket, managed service, or CRDT with tradeoffs.
- Realtime architecture brief:
  rooms, presence, persistence, reconnect, and scale path.
- Collaboration plan:
  document model, awareness, sync transport, and recovery notes.

## Known Traps

| Trap | Consequence | Fix |
|------|-------------|-----|
| Auth only on initial handshake; reconnect path undefined | Reconnect after token expiry fails silently | Handle token refresh in reconnect loop |
| Treating presence/typing signals as durable truth | Stale cursors on reconnect; unbounded storage growth | Ephemeral TTL store; derive expiry from heartbeat interval |
| Offline queues without stable `op_id` and dedupe policy | Duplicate state on replay | Assign `op_id` before queuing; server deduplicates idempotently |
| Scaling to multi-node before single-node protocol is stable | Fan-out bugs are hard to reproduce across nodes | Validate room semantics on a single node first |
| Choosing WebSocket by habit for one-way server push | Unnecessary bidirectional session overhead | Evaluate SSE; if client never sends messages, SSE is cheaper |
| Adopting WebTransport because of browser support alone | The deployed request path may not pass the selected transport | Test on target networks and intermediaries; keep a tested fallback |
| Sizing a WebSocket fleet from a published per-connection memory or DO connection-count figure without measuring on your own runtime | Instance falls over well below the "documented" ceiling because TLS termination point, message size, and per-connection app state differ from the vendor's benchmark | Load test at target CCU with production-representative payloads before trusting any vendor capacity number |

## Scenarios

Five numbered scenarios covering the most common real-time design moments. Each lists the shortest path using patterns above.

### S1 — Presence channel for online users with stale-cleanup

1. Model presence as ephemeral key-value entries keyed by `user_id`; include a `last_seen` timestamp on each heartbeat.
2. Publish presence updates at most every 5 seconds; throttle high-frequency ping loops on the client.
3. On server, derive expiry from the heartbeat interval and expected network jitter.
4. Broadcast presence diffs (join/leave/update) to room subscribers, not the full member list.
5. On reconnect, re-publish the client's own presence before subscribing to the room's current snapshot.
6. Keep presence data in a fast TTL store (Redis `SETEX`) separate from durable document state.

### S2 — Reconnect with exponential backoff + queued ops

1. On disconnect, enter a reconnect loop: initial delay 1s, double each attempt, cap at 30s, add ±20% jitter.
2. Queue outbound operations locally while offline; assign each a stable `op_id` for deduplication on replay.
3. On reconnect, re-authenticate (token refresh if needed), then replay the queue in order.
4. The server deduplicates by `op_id`; idempotent apply means safe replay without double-writes.
5. If the queue exceeds a size limit, surface an error to the user rather than dropping silently.
6. Emit connection-state events (`connecting`, `connected`, `disconnected`) so the UI can show status.

### S3 — Yjs CRDT collaborative doc sync with awareness

1. Initialize a `Y.Doc` per document; connect via a WebSocket provider (`y-websocket` or `PartyKit`).
2. Persist document updates to durable storage (Postgres, Supabase) using the binary `Y.encodeStateAsUpdate` format.
3. Keep awareness data (cursors, selection, name) in a separate `provider.awareness` object; never write it to the doc.
4. Throttle awareness broadcasts to at most 50ms; rapid cursor movement generates too many small updates.
5. On client reconnect, call `Y.applyUpdate` with the server state before broadcasting local pending updates.
6. Test concurrent edits from two clients with network partition; confirm the doc converges after reconnect.

### S4 — SSE vs WebSocket choice for a one-way live dashboard

1. Confirm the dashboard receives server-pushed updates and never sends user input back to the server.
2. Choose SSE: HTTP/1.1 compatible, reconnect handled by the browser natively, no upgrade handshake needed.
3. Implement the server endpoint as a streaming HTTP response with `Content-Type: text/event-stream`.
4. Include `id:` fields and implement replay from `Last-Event-ID`; the header alone does not restore missed events.
5. Add a server-side heartbeat comment (`: keepalive`) every 25 seconds to prevent proxy timeout.
6. Check HTTP/1.1 per-origin connection limits across tabs, proxy buffering, and compression; use HTTP/2 where available and test actual streaming latency. [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events).

### S5 — PartyKit room sharding for hot rooms

1. Verify the default single-Durable-Object-per-room limit; one room instance handles a bounded connection count.
2. Shard large rooms by assigning users to sub-rooms (e.g., `room:{id}:shard:{n}`) based on `user_id % shard_count`.
3. Broadcast cross-shard events via a coordinator object that fans out to all shard instances.
4. Keep presence and room membership aggregated at the coordinator level, not replicated per shard.
5. Test shard rebalancing behavior when a shard instance restarts; clients should reconnect to the same shard.
6. Monitor per-shard connections and request rate; adjust shard count before measured ceilings are reached.

## Navigation

- Core references: [references/transport-selection.md](references/transport-selection.md), [references/collaboration-patterns.md](references/collaboration-patterns.md), [references/vendor-traps.md](references/vendor-traps.md)
- Source map: [data/sources.json](data/sources.json)
- Script: [scripts/check_ws_smoke.py](scripts/check_ws_smoke.py). The older [ws_smoke_test.py](scripts/ws_smoke_test.py) forwards its positional CLI to this tool.
- Related skills: [software-backend](../software-backend/SKILL.md), [software-baas-platforms](../software-baas-platforms/SKILL.md), [software-frontend](../software-frontend/SKILL.md), [software-architecture-design](../software-architecture-design/SKILL.md), [software-mobile](../software-mobile/SKILL.md), [qa-resilience](../qa-resilience/SKILL.md), [software-security-appsec](../software-security-appsec/SKILL.md)
- [references/distributed-systems-applied.md](references/distributed-systems-applied.md) — CAP/PACELC, consensus, idempotency, quorums applied to real-time and collaborative systems.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
