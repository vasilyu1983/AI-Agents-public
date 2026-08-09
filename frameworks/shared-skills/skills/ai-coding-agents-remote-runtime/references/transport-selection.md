# Transport Selection Decision Tree

## Table of Contents

- [Decision Tree](#decision-tree)
- [Transport Comparison](#transport-comparison)
- [Criteria](#criteria)
- [Hybrid patterns](#hybrid-patterns)
- [No-inbound-ports relay (outbound-poll mirroring)](#no-inbound-ports-relay-outbound-poll-mirroring)
- [Anti-patterns](#anti-patterns)
- [Sequence number conventions (WebSocket resume)](#sequence-number-conventions-websocket-resume)
- [Related](#related)

Use this reference when choosing between WebSocket, SSE, HTTP POST, and ACP stdio for a remote coding-agent session. Decide per direction (read vs. write) and per session mode before coding.

## Decision Tree

```
Start: What does this channel carry?
│
├── Control traffic (permission prompts, cancellations, interrupt signals)
│   └── Bidirectional, low-latency required?
│       ├── YES → WebSocket control channel
│       └── NO  → HTTP POST (write-side) + SSE or polling (read-side)
│
├── Transcript / streaming agent output (read-heavy)
│   └── Does the client need to push anything back on the same connection?
│       ├── YES → WebSocket (multiplex reads and acks on one pipe)
│       └── NO  → SSE (simpler, HTTP/2 compatible, survives load-balancer restarts better)
│
├── Single-shot writes (user message submission, approve/deny response)
│   └── HTTP POST — never upgrade to WebSocket just because the reads are streaming
│
└── Editor integration (Zed, JetBrains, VS Code fork, IntelliJ)
    └── ACP stdio — line-delimited JSON over spawned subprocess;
        session-ID re-attach on reconnect, not replay
```

## Transport Comparison

| Transport | Direction | Latency | Reconnect model | When to prefer |
|-----------|-----------|---------|-----------------|----------------|
| **WebSocket** | Bidirectional | Low | Client reconnects; server re-delivers in-flight on seq number match | Control channels; mixed read+write streams that must stay ordered |
| **SSE** | Server → client only | Low | Browser/HTTP layer reconnects automatically with `Last-Event-ID` | Pure streaming output; simpler infrastructure; HTTP/2 environments |
| **HTTP POST** | Client → server only | Medium | Stateless; idempotent with request ID | Single-shot writes: submitting a message, answering a prompt |
| **ACP stdio** | Bidirectional | Lowest (IPC) | Session-ID re-attach on new stdin pipe; process may restart | Editor integrations; local daemon ↔ editor; never crosses the internet |

## Criteria

### Use WebSocket when

- The channel carries both control messages and transcript events on one pipe
- The server must push control events (cancellations, reconnect notifications) to the client unprompted
- Ordered delivery with sequence numbers matters for reconnect-resume correctness
- The client needs to ack or respond to server-pushed events within the same stream

### Use SSE when

- The session is read-heavy: the client consumes a stream of agent turns and renders them
- Writes are infrequent and well-suited to separate HTTP POST calls
- You want automatic HTTP-layer reconnect (`Last-Event-ID` + `EventSource`)
- You are behind an HTTP/2 load balancer and want to avoid WebSocket upgrade complexity

### Use HTTP POST when

- The write is a discrete user action: submitting a prompt, approving a tool call, cancelling a task
- The response can come back synchronously in the HTTP reply or asynchronously on the read channel
- Idempotency is straightforward to implement (use a stable `request_id` in the body)

### Use ACP stdio when

- The consumer is an editor that spawns the agent as a child process
- You need the lowest possible latency and no network hop
- Session-ID re-attach on new `stdin` FD is acceptable (the process may restart between editor sessions)
- You want to codegen method dispatch from the ACP schema rather than hand-write WebSocket handlers

## Hybrid patterns

**Split read/write transport** is the most common robust pattern for internet-facing sessions:

```
Client reads:  SSE or WebSocket (server → client)
Client writes: HTTP POST (client → server)
```

This decouples reconnect semantics. If the read channel drops, the client reconnects SSE/WebSocket from the last event ID. Writes in-flight already have HTTP-level retries. The two channels never confuse each other's ordering.

**Downgrade path:** start with HTTP polling as a fallback if SSE or WebSocket is blocked by a proxy. Never expose polling as the default; it adds unnecessary latency and load.

## No-inbound-ports relay (outbound-poll mirroring)

A fifth transport shape that the decision tree above omits, and that a non-expert will not think to ask for: when the "remote" party is actually a client mirroring into a session that must keep running on an untrusted or NAT'd machine (a laptop, not a data-center host), do not open an inbound port on that machine at all.

Verified production example (`code.claude.com/docs/en/remote-control`, checked 2026-07-11): Claude Code's cross-device session steering makes **outbound HTTPS requests only** from the local machine and never opens an inbound port. The local process registers with a cloud API and polls for work; the remote browser/mobile client also talks to the cloud API; the cloud side relays between them over a streaming connection. Credentials are multiple short-lived tokens, each scoped to a single purpose and expiring independently — not one long-lived session secret shared across both legs.

Use this shape when:

- the executing machine is a laptop/workstation that sleeps, roams networks, and sits behind NAT or a firewall you do not control
- you cannot assume the remote viewer and the executing machine can ever open a direct connection to each other
- you want the executing machine to be able to revoke a compromised viewer credential without also invalidating its own connection to the relay

Do not use this shape as a substitute for the SSH-stdio-devbox pattern (see `local-ui-remote-execution-model.md`) — the point of the SSH pattern is that *execution* moves to the remote host; the point of the no-inbound-ports relay is that execution stays put and only *steering* moves.

Anti-pattern: building a bespoke WebSocket-to-the-laptop bridge that requires the laptop to accept inbound connections (via port-forwarding, ngrok-style tunnels, or a static IP). That reintroduces exactly the NAT/firewall/security-review problem the relay pattern exists to avoid.

## Anti-patterns

- Upgrading every channel to WebSocket because "it's faster." HTTP POST writes are simpler to reason about, retry, and audit.
- Mixing control messages and transcript output on one untyped WebSocket pipe with no schema. Control events become invisible in the stream.
- Using ACP stdio for internet-facing remote sessions. ACP is a local IPC protocol; it has no auth, no TLS, and no rate-limiting layer.
- Reusing the SSE `Last-Event-ID` as a session-resume token. That is a client-side hint, not a durable server-side checkpoint.

## Sequence number conventions (WebSocket resume)

When using WebSocket with sequence-aware resume, assign a monotonically increasing `seq` to every server-pushed message. On reconnect:

1. Client sends `{type: "resume", session_id: "...", last_seq: N}`
2. Server delivers messages from `N+1` onward
3. Messages with `seq ≤ N` are discarded server-side after a configurable retention window

For recipes, see [`recipe-reconnect-with-sequence.md`](recipe-reconnect-with-sequence.md).

## Related

- [`bridge-transport-and-permission-bridging.md`](bridge-transport-and-permission-bridging.md) — WebSocket control messages, permission routing, reconnect
- [`recipe-reconnect-with-sequence.md`](recipe-reconnect-with-sequence.md) — Resumable stream implementation
- [`../ai-coding-agents-sessions/references/resume-path-decision-tree.md`](../../ai-coding-agents-sessions/references/resume-path-decision-tree.md) — When to use session ID vs picker vs ACP re-attach
