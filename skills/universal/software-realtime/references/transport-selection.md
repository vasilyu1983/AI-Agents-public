# Transport Selection

Use this file when the request is deciding between SSE, WebSocket, WebTransport, WebRTC, or a managed transport.

Browser support and HTTP/3 deployment change over time; check current support tables before committing infrastructure.

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
   No → SSE. Browser reconnects automatically and can send `Last-Event-ID`; the server must implement replay. Check HTTP/1.1 browser connection limits and proxy buffering before rollout.
2. **Yes, bidirectional is required — does the app need strict in-order, reliable delivery of every message?**
   Yes → WebSocket. This is still the correct default for chat, collaborative cursors, and most interactive apps.
3. **Does the app need unreliable delivery (drop old data rather than block) or several independent streams that must not head-of-line-block each other?**
   Yes → WebTransport. Check current browser support and the deployed server, CDN, load balancer, and proxy path. Some implementations offer reliable-only operation; test the actual `WebTransport.reliability` result if the product needs datagrams. Provide an explicit fallback when the connection or required mode is unavailable.
4. **Does the interaction never touch a server — two browsers exchanging media or data directly?**
   Yes → WebRTC. Media tracks carry audio/video; data channels carry P2P data. Include STUN and a TURN relay fallback, then measure relay usage and bandwidth on the target network mix.
5. **Mesh vs SFU for multi-party WebRTC:** mesh upload grows with every added peer. Measure the device and network budget; use an SFU when mesh cannot meet it.

## HTTP/3 and QUIC Adoption Context

HTTP/3 adoption figures differ by measurement method (sites that support it vs. page loads actually served over it); look up a current survey (for example W3Techs or a CDN operator's report) and name the method before quoting a figure. Treat HTTP/3 as widely but not universally deployed: WebTransport and other QUIC-dependent transports are safe bets for new products but still need a fallback or graceful degradation path for networks that block or throttle UDP.

## Fan-Out and Broker Choice

Transport choice determines the client-facing protocol; broker choice determines how the server side distributes one event to many subscribers across nodes. Re-derive the arithmetic per system:

- **Redis Pub/Sub**: push-based and fire-and-forget. A disconnected subscriber loses messages sent while it was down. Fits ephemeral fan-out where the next update repairs a miss.
- **Redis Streams**: adds a persisted log with consumer groups and acknowledgment. Evaluate when replay or at-least-once processing matters.
- **Kafka**: partitioned, horizontally scalable, strong ordering per partition, long retention and replay across many independent consumer groups. Right choice once fan-out volume or retention needs exceed what a single Redis node's CPU/network can sustain, or when multiple independent downstream systems (not just WebSocket fan-out) need the same event stream.
- **NATS / NATS JetStream**: worth evaluating when the priority is low-latency request-reply plus pub/sub in one lightweight binary, especially in Go/embedded-systems shops already running NATS for service mesh messaging.

Do the math before picking: N connected clients at M messages/s means the fan-out tier sustains roughly N × M outbound sends/s (plus framing/serialization/TLS overhead) — measure your actual broker's sustained ops/s at your message size before assuming a documented benchmark number transfers to your workload.

## Serverless / Managed WebSocket Options (verify current pricing and limits)

- **Cloudflare Durable Objects (WebSocket Hibernation API)**: hibernation lets an object go idle while accepted sockets remain connected. Check current connection and CPU limits in the [official limits](https://developers.cloudflare.com/durable-objects/platform/limits/) before room sizing; outbound sockets do not hibernate.
- **AWS API Gateway WebSocket APIs**: fully serverless, pay-per-message and per-connection-minute; good fit for infrequent bidirectional traffic, less cost-efficient than a persistent process for high-frequency low-latency workloads.
- **Azure Web PubSub**: fully managed pub/sub over WebSocket; capacity is sold in units, so check the Azure limits page for connections per unit and the maximum units per tier, and size the unit count from peak CCU — reasonable default when the stack is already Azure-centric.
- **Ably / Pusher**: managed connection, presence, and fan-out. Check current delivery semantics, limits, and pricing against the workload.

## Operational Guardrails

- Design reconnect behavior before production rollout.
- Keep messages idempotent.
- Bound queue growth for disconnected clients.
- Confirm the load balancer supports connection draining before every rolling deploy — without it, in-flight connections are hard-killed instead of allowed to finish and reconnect.
