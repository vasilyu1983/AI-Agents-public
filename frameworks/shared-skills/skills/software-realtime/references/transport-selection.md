# Transport Selection

Use this file when the request is deciding between SSE, WebSocket, WebTransport, WebRTC, or a managed transport.

_Last verified: 2026-07-11._

## Default

- Start with SSE for server-to-client updates.
- Use WebSocket when client-to-server interaction is frequent or stateful.
- Use WebTransport only when the workload specifically benefits from unreliable/unordered delivery or independent multiplexed streams (see decision gate below) — it is a real option now, not a fallback bet.
- Use WebRTC (data channels or media) only for peer-to-peer audio/video/data that must not round-trip a server.
- Use managed real-time platforms when presence, fan-out, and collaboration speed matter more than infrastructure control.

## Selection Signals

| Need | Default |
|---|---|
| Notifications, dashboards, feeds | SSE |
| Chat, cursor sync, multiplayer interaction | WebSocket |
| Live game state, telemetry where a stale/dropped frame beats waiting for one | WebTransport (datagrams) — verify client and infra HTTP/3 support first |
| Video/audio calls, screen share, direct browser-to-browser transfer | WebRTC media tracks or data channels |
| Rich collaboration with presence and storage | Managed real-time platform or CRDT stack |

## WebSocket vs SSE vs WebTransport Decision Gate

1. **Does the client ever need to send data back on the same connection?**
   No → SSE. HTTP/1.1-compatible, browser-native reconnect via `Last-Event-ID`, no upgrade handshake, works through virtually every proxy and load balancer without special configuration.
2. **Yes, bidirectional is required — does the app need strict in-order, reliable delivery of every message?**
   Yes → WebSocket. This is still the correct default for chat, collaborative cursors, and most interactive apps in mid-2026.
3. **Does the app need unreliable delivery (drop old data rather than block) or several independent streams that must not head-of-line-block each other?**
   Yes → WebTransport. It runs over HTTP/3/QUIC and, as of March 2026, is Baseline (Safari 26.4 shipped support alongside Chrome/Firefox/Edge) — treat it as production-viable for new builds, not experimental. It still requires: (a) a server stack with mature QUIC/HTTP-3 support, (b) confirmation that the deployment's CDN/load balancer/corporate-proxy path actually passes UDP/QUIC (many enterprise networks still block or downgrade it), and (c) a fallback story, since WebTransport's own spec allows falling back to HTTP/2+TCP when QUIC is unavailable — verify your library surfaces that fallback rather than just failing.
4. **Does the interaction never touch a server — two browsers exchanging media or data directly?**
   Yes → WebRTC. Media tracks for audio/video; data channels for arbitrary low-latency P2P data. Needs STUN for NAT traversal and a TURN relay fallback for the ~15-20% of network paths where direct P2P fails (symmetric NAT, restrictive corporate firewalls) — do not ship WebRTC without a TURN fallback budgeted in, TURN relay bandwidth is the single most volatile cost line in a WebRTC deployment.
5. **Mesh vs SFU for multi-party WebRTC:** peer-to-peer mesh only works up to about 4-6 participants — each additional peer multiplies every existing peer's upload bandwidth (N-way mesh is O(N²) total streams). Beyond that, route media through a Selective Forwarding Unit (SFU) so each client uploads once and the SFU fans out; this is the standard architecture for any group call product beyond a small huddle.

## HTTP/3 and QUIC Adoption Context (verify current before treating as durable fact)

As of July 2026, W3Techs reports roughly 40% of websites serving HTTP/3, with real-world adoption plateaus reported by some CDN operators (traffic share estimates range roughly 20-40% depending on measurement method — sites supporting it vs. actual page loads served over it). Treat this as "widely but not universally deployed": WebTransport and other QUIC-dependent transports are safe bets for new products but still need a fallback or graceful degradation path for networks that block or throttle UDP.

## Fan-Out and Broker Choice

Transport choice determines the client-facing protocol; broker choice determines how the server side distributes one event to many subscribers across nodes. Re-derive the arithmetic per system:

- **Redis Pub/Sub**: push-based, fire-and-forget, sub-millisecond in the common case. No persistence — a disconnected subscriber loses messages sent while it was down. Right choice for ephemeral fan-out (presence, cursors, live counters) where a missed update self-heals on the next tick.
- **Redis Streams**: adds a persisted log with consumer groups and acknowledgment, closer to Kafka semantics at much lower operational cost. Right choice when you need replay-on-reconnect or at-least-once delivery but don't yet need multi-datacenter retention or huge partition counts.
- **Kafka**: partitioned, horizontally scalable, strong ordering per partition, long retention and replay across many independent consumer groups. Right choice once fan-out volume or retention needs exceed what a single Redis node's CPU/network can sustain, or when multiple independent downstream systems (not just WebSocket fan-out) need the same event stream.
- **NATS / NATS JetStream**: worth evaluating when the priority is low-latency request-reply plus pub/sub in one lightweight binary, especially in Go/embedded-systems shops already running NATS for service mesh messaging.

Do the math before picking: N connected clients at M messages/s means the fan-out tier sustains roughly N × M outbound sends/s (plus framing/serialization/TLS overhead) — measure your actual broker's sustained ops/s at your message size before assuming a documented benchmark number transfers to your workload.

## Serverless / Managed WebSocket Options (verify current pricing and limits)

- **Cloudflare Durable Objects (WebSocket Hibernation API)**: up to 32,768 WebSocket connections per Durable Object; hibernation lets a DO go idle without holding the connection's compute allocation, but only when the DO is the WebSocket *server* — outbound WebSockets from a DO do not hibernate and keep it billed alive.
- **AWS API Gateway WebSocket APIs**: fully serverless, pay-per-message and per-connection-minute; good fit for infrequent bidirectional traffic, less cost-efficient than a persistent process for high-frequency low-latency workloads.
- **Azure Web PubSub**: fully managed pub/sub over WebSocket, published capacity around 100,000 concurrent connections per unit at time of writing (verify current) — reasonable default when the stack is already Azure-centric.
- **Ably / Pusher**: managed connection + presence + fan-out with SLA-backed delivery guarantees; the right trade when a small team wants to buy away connection-layer ops entirely and can accept per-connection or per-MAU pricing.

## Operational Guardrails

- Design reconnect behavior before production rollout.
- Keep messages idempotent.
- Bound queue growth for disconnected clients.
- Confirm the load balancer supports connection draining before every rolling deploy — without it, in-flight connections are hard-killed instead of allowed to finish and reconnect.
