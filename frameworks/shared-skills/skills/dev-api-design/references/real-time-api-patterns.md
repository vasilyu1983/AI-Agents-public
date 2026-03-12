# Real-Time API Patterns

> Operational reference for choosing, implementing, and scaling real-time communication — WebSockets, Server-Sent Events, long polling, and GraphQL subscriptions. Covers connection lifecycle, load balancing, security, and production scaling.

**Freshness anchor:** January 2026 — aligned with WebSocket API (RFC 6455), EventSource API, GraphQL over WebSocket Protocol (graphql-ws), and Socket.IO v4.x.

---

## Quick Decision: Choosing a Real-Time Pattern

| Factor | WebSocket | SSE | Long Polling | GraphQL Subscriptions |
|---|---|---|---|---|
| Direction | Bidirectional | Server → Client | Server → Client | Server → Client |
| Protocol | ws:// / wss:// | HTTP/2 (text/event-stream) | HTTP | ws:// via graphql-ws |
| Browser support | All modern | All modern (no IE) | Universal | Requires client library |
| Reconnection | Manual (implement yourself) | Built-in (EventSource) | Built-in (next request) | Library-managed |
| Binary data | Yes | No (text only) | Yes (base64) | No (JSON) |
| Max connections | OS/server limits | 6 per domain (HTTP/1.1), unlimited (HTTP/2) | Standard HTTP limits | Same as WebSocket |
| Load balancer | Sticky sessions or Redis pub/sub | Standard HTTP | Standard HTTP | Sticky sessions or Redis pub/sub |
| Use when | Chat, gaming, collaborative editing | Notifications, feeds, dashboards | Legacy clients, simplest fallback | Already using GraphQL |

### Decision Tree

```
Does the client need to SEND data in real-time?
├── YES → WebSocket
│   ├── High-frequency messages (gaming, collaboration) → Raw WebSocket
│   └── Need rooms/namespaces/fallback → Socket.IO
└── NO (server push only)
    ├── Already using GraphQL? → GraphQL Subscriptions
    ├── Need broad browser support including old proxies? → Long Polling
    └── Modern stack, text data → SSE
        ├── HTTP/2 available? → SSE (no connection limit issues)
        └── HTTP/1.1 only? → SSE with domain sharding or WebSocket
```

---

## WebSocket Patterns

### Connection Lifecycle

```
Client                          Server
  │                               │
  ├── HTTP Upgrade Request ──────>│
  │   (Upgrade: websocket)        │
  │<──── 101 Switching Protocols ─┤
  │                               │
  │<════ Full duplex channel ════>│
  │                               │
  ├── Ping ──────────────────────>│  (heartbeat)
  │<──────────────────── Pong ────┤
  │                               │
  ├── Message ───────────────────>│
  │<──────────────── Message ─────┤
  │                               │
  ├── Close (1000, "normal") ────>│
  │<──── Close acknowledgment ────┤
  │                               │
```

### Heartbeat / Keep-Alive Implementation

```javascript
// Server-side (Node.js with ws library)
const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

const HEARTBEAT_INTERVAL = 30000; // 30 seconds
const HEARTBEAT_TIMEOUT = 10000;  // 10 seconds to respond

wss.on("connection", (ws) => {
  ws.isAlive = true;

  ws.on("pong", () => {
    ws.isAlive = true;
  });
});

const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!ws.isAlive) {
      return ws.terminate(); // Dead connection
    }
    ws.isAlive = false;
    ws.ping();
  });
}, HEARTBEAT_INTERVAL);

wss.on("close", () => clearInterval(interval));
```

### Client Reconnection Strategy

```javascript
class ReconnectingWebSocket {
  constructor(url) {
    this.url = url;
    this.reconnectDelay = 1000;
    this.maxDelay = 30000;
    this.attempts = 0;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.reconnectDelay = 1000; // Reset on success
      this.attempts = 0;
    };

    this.ws.onclose = (event) => {
      if (event.code !== 1000) { // Not a clean close
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      this.ws.close();
    };
  }

  scheduleReconnect() {
    const jitter = Math.random() * 1000;
    const delay = Math.min(this.reconnectDelay + jitter, this.maxDelay);
    this.reconnectDelay *= 2;
    this.attempts++;
    setTimeout(() => this.connect(), delay);
  }
}
```

### Connection State Management

| State | Description | Client Action |
|---|---|---|
| CONNECTING | Handshake in progress | Show "connecting" indicator |
| OPEN | Connected and ready | Normal operation |
| CLOSING | Close initiated | Disable send, show status |
| CLOSED | Connection terminated | Attempt reconnection |
| RECONNECTING | Between attempts | Show "reconnecting" with attempt count |

### WebSocket Message Protocol Design

```json
{
  "type": "message",
  "channel": "room:123",
  "payload": { "text": "Hello", "sender_id": "usr_abc" },
  "id": "msg_01JKXYZ",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

**Message type conventions:**

| Type | Direction | Purpose |
|---|---|---|
| `subscribe` | Client → Server | Join a channel/topic |
| `unsubscribe` | Client → Server | Leave a channel/topic |
| `message` | Bidirectional | Application data |
| `ack` | Server → Client | Confirm receipt of client message |
| `error` | Server → Client | Error notification |
| `ping` / `pong` | Bidirectional | Application-level heartbeat |

---

## Server-Sent Events (SSE)

### Implementation

**Server (Node.js):**

```javascript
app.get("/events", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no" // Disable Nginx buffering
  });

  // Send initial connection event
  res.write(`event: connected\ndata: ${JSON.stringify({ status: "ok" })}\n\n`);

  // Send periodic updates
  const interval = setInterval(() => {
    res.write(`id: ${Date.now()}\nevent: update\ndata: ${JSON.stringify(getData())}\n\n`);
  }, 5000);

  req.on("close", () => {
    clearInterval(interval);
  });
});
```

**Client:**

```javascript
const source = new EventSource("/events");

source.addEventListener("update", (event) => {
  const data = JSON.parse(event.data);
  // Handle update
});

source.addEventListener("error", (event) => {
  if (source.readyState === EventSource.CONNECTING) {
    console.log("Reconnecting..."); // Auto-reconnect is built in
  }
});
```

### SSE vs WebSocket Checklist

- [ ] Only need server-to-client push → Use SSE
- [ ] Need binary data → Use WebSocket
- [ ] HTTP/2 available → SSE has no connection limit issues
- [ ] Need auto-reconnection with last-event-id → SSE (built-in)
- [ ] Client needs to send frequent messages → Use WebSocket
- [ ] Behind restrictive corporate proxies → SSE (standard HTTP)

---

## Long Polling

### Implementation Pattern

```javascript
// Server
app.get("/poll", async (req, res) => {
  const lastEventId = req.query.since;
  const timeout = 30000;

  try {
    const data = await waitForUpdates(lastEventId, timeout);
    res.json({ data, lastEventId: data.id });
  } catch (timeoutError) {
    res.status(204).end(); // No content, client should retry
  }
});

// Client
async function longPoll(since = null) {
  try {
    const url = since ? `/poll?since=${since}` : "/poll";
    const response = await fetch(url);

    if (response.status === 200) {
      const result = await response.json();
      handleUpdate(result.data);
      longPoll(result.lastEventId); // Immediately poll again
    } else {
      longPoll(since); // No data, retry
    }
  } catch (error) {
    setTimeout(() => longPoll(since), 5000); // Error, backoff
  }
}
```

**Use when:**

- Maximum compatibility required (works through all proxies/firewalls)
- Low-frequency updates (< 1 per second)
- Fallback when WebSocket/SSE connections fail

---

## GraphQL Subscriptions

### Setup with graphql-ws

```javascript
// Server
import { createServer } from "http";
import { WebSocketServer } from "ws";
import { useServer } from "graphql-ws/lib/use/ws";
import { schema } from "./schema";

const server = createServer(app);
const wsServer = new WebSocketServer({ server, path: "/graphql" });

useServer(
  {
    schema,
    context: async (ctx) => {
      const token = ctx.connectionParams?.authToken;
      return { user: await validateToken(token) };
    },
  },
  wsServer
);
```

```graphql
# Schema
type Subscription {
  orderUpdated(orderId: ID!): Order!
  newNotification: Notification!
}
```

**Use when:**

- Already using GraphQL for queries/mutations
- Want type-safe subscriptions with same schema
- Need fine-grained subscription filtering

---

## Scaling Real-Time Connections

### Architecture for Multiple Server Instances

```
Clients ──→ Load Balancer ──→ Server Instance A ──┐
                          ──→ Server Instance B ──├── Redis Pub/Sub
                          ──→ Server Instance C ──┘
```

### Scaling Checklist

- [ ] Redis Pub/Sub or NATS for cross-instance message broadcasting
- [ ] Sticky sessions OR shared state for WebSocket connections
- [ ] Connection count monitoring per instance (alert at 80% capacity)
- [ ] Graceful shutdown: drain connections before instance termination
- [ ] Horizontal scaling: add instances based on connection count, not CPU

### Load Balancer Configuration

| Load Balancer | WebSocket Support | Key Config |
|---|---|---|
| Nginx | Yes | `proxy_set_header Upgrade $http_upgrade;` |
| ALB (AWS) | Yes | Idle timeout up to 4000s |
| Cloudflare | Yes | 100s idle timeout (configurable on enterprise) |
| HAProxy | Yes | `option http-server-close` disable |

**Nginx WebSocket proxy:**

```nginx
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
```

### Connection Limits Reference

| Resource | Typical Limit | Tuning |
|---|---|---|
| OS file descriptors | 1024 default | `ulimit -n 65535` |
| Node.js per-process | ~10K-50K concurrent | Cluster mode or multiple processes |
| Nginx | 512 per worker | `worker_connections 10240;` |
| Redis Pub/Sub | 10K subscribers/channel | Shard channels by topic prefix |

---

## Security Considerations

### WebSocket Security Checklist

- [ ] Use `wss://` (TLS) in production — never `ws://`
- [ ] Validate Origin header on upgrade request
- [ ] Authenticate during handshake (token in query param or first message)
- [ ] Rate limit messages per connection (prevent flooding)
- [ ] Validate and sanitize all incoming message payloads
- [ ] Set maximum message size (`maxPayload` in ws library)
- [ ] Implement per-IP connection limits
- [ ] Close connections that fail authentication within 5 seconds

### SSE Security Checklist

- [ ] CORS headers configured for allowed origins
- [ ] Authentication via cookies or query token (no custom headers with EventSource)
- [ ] Rate limit connection attempts per IP
- [ ] Validate `Last-Event-ID` header to prevent injection

### Authentication Patterns for WebSocket

| Pattern | Pros | Cons |
|---|---|---|
| Token in query string | Simple, works everywhere | Token in URL logs |
| Token in first message | Clean URL | Unauthenticated window |
| Cookie-based | Automatic, secure | CORS complexity |
| Connection params (graphql-ws) | Clean, typed | Library-specific |

**Recommended:** Token in connection params or first message, with a 5-second auth timeout.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| No heartbeat/ping-pong | Zombie connections accumulate | Implement 30s ping, terminate on missed pong |
| No reconnection logic | Client disconnects permanently | Exponential backoff with jitter |
| Sending large payloads over WebSocket | Memory pressure, slow parsing | Paginate large data; use REST for bulk |
| Using WebSocket for request-response | Adds complexity over HTTP | Use REST/GraphQL for request-response; WS for push |
| No message size limits | DoS via oversized messages | Set `maxPayload` (e.g., 1MB) |
| Broadcasting to all connections | Does not scale, wasted bandwidth | Use channels/topics, send only relevant updates |
| Storing session state in-process only | Breaks with multiple instances | Use Redis or external store for connection state |
| SSE without `X-Accel-Buffering: no` | Nginx buffers events, appears broken | Disable proxy buffering for SSE endpoints |
| No graceful degradation | Complete failure if WS unavailable | Fallback to SSE → long polling |
| Authentication only at connection time | Long-lived connections bypass token expiry | Periodic re-authentication or token refresh |

---

## Cross-References

- `dev-api-design/references/webhook-patterns.md` — async push alternative to real-time connections
- `dev-api-design/references/api-testing-patterns.md` — testing WebSocket and SSE endpoints
- `software-architecture-design/references/api-gateway-service-mesh.md` — gateway configuration for WebSocket routing
- `software-frontend/references/state-management-patterns.md` — managing real-time data in frontend state
- `qa-resilience/references/load-shedding-backpressure.md` — handling connection overload
