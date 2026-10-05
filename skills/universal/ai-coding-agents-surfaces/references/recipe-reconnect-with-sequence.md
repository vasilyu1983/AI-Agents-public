# Recipe: Resumable Streams with Sequence Numbers

A step-by-step implementation recipe for reconnect-safe remote sessions using sequence-numbered messages. Implements the "sequence-aware resume" pattern described in `transport-selection.md` and `bridge-transport-and-permission-bridging.md`.

## Table of Contents

- [Goal](#goal)
- [Components](#components)
- [Step 1 — Assign sequence numbers server-side](#step-1--assign-sequence-numbers-server-side)
- [Step 2 — Retain messages in a bounded buffer that reports expiry](#step-2--retain-messages-in-a-bounded-buffer-that-reports-expiry)
- [Step 3 — Handle the resume handshake](#step-3--handle-the-resume-handshake)
- [Step 4 — Client reconnect loop](#step-4--client-reconnect-loop)
- [Step 5 — Edge cases to handle](#step-5--edge-cases-to-handle)
- [Step 6 — ACP stdio variant](#step-6--acp-stdio-variant)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## Goal

After any network drop, the client reconnects and the server delivers exactly the messages the client missed — no duplicates, no gaps, no full-replay cost. When the missed range is no longer retained, the server says so and the client falls back to a full reload instead of silently skipping messages.

Success criteria: a client that disconnects mid-turn and reconnects within the retention window sees all missed transcript and control events in order, with no agent-side side effects. Outside the window, it sees an explicit `seq_expired` and reloads.

**Default:** resume from `last_seq`; on `seq_expired`, reload the full transcript out of band and resume from the reloaded position. Use "live only" (no replay) only for viewers that do not need history.

## Components

| Component | Responsibility |
|-----------|---------------|
| `SeqStore` | Server-side bounded buffer of recent messages per session; reports when a requested range has been evicted |
| `seq` field | Monotonically increasing integer on every server-pushed transcript or control message |
| Handshake frames | `resume` (client → server, carries `last_seq`); `resumed{from,to}`, `seq_expired{oldest,next}`, `error{code}`, `displaced` (server → client). Handshake frames carry **no** `seq` |
| Per-session lock | Serializes live sends against attach + snapshot + replay, so nothing is sent between the snapshot and the attach |
| `ReconnectState` | Client-side state: `connecting(attempt) | connected | disconnected(reason)` |

## Step 1 — Assign sequence numbers server-side

Every message the server pushes gets a `seq`, is retained, and is sent under the session lock. `send` is `async` because the socket write is awaited.

```python
# Runnable sketch (asyncio); adapt to your framework.
import asyncio
from collections import deque


class Session:
    def __init__(self, session_id: str, store: "SeqStore"):
        self.id = session_id
        self._store = store
        self._next_seq = 0
        self._ws = None                  # the attached controller socket, or None
        self.lock = asyncio.Lock()       # one lock per session

    async def send(self, message: dict) -> None:
        async with self.lock:
            message = {**message, "seq": self._next_seq}
            self._store.put(self.id, self._next_seq, message)   # retain before sending
            self._next_seq += 1
            ws = self._ws
            if ws is not None:
                try:
                    await ws.send_json(message)
                except ConnectionError:
                    self._ws = None      # message is retained; the client resumes it
```

Key rules:
- `seq` is per-session, not global.
- Sequence numbers are never reused, even after partial reconnect.
- Control messages (permission prompts, cancellations) get `seq` like any other message.
- Retain before sending: a message that fails to send must still be replayable.

## Step 2 — Retain messages in a bounded buffer that reports expiry

```python
class SeqExpired(Exception):
    def __init__(self, oldest: int):
        self.oldest = oldest


class SeqStore:
    """Bounded in-memory buffer. Use a Redis ZSET or a DB table for multi-process servers."""

    def __init__(self, max_retain: int = 2000):
        self._max = max_retain
        self._bufs: dict[str, deque] = {}

    def put(self, session_id: str, seq: int, message: dict) -> None:
        # deque(maxlen=...) evicts the oldest entry in O(1); list.pop(0) is O(n).
        self._bufs.setdefault(session_id, deque(maxlen=self._max)).append((seq, message))

    def since(self, session_id: str, last_seq: int, next_seq: int) -> list[dict]:
        """Messages with seq > last_seq. Raises SeqExpired instead of truncating silently."""
        if last_seq == next_seq - 1:
            return []                                   # client is fully caught up
        buf = self._bufs.get(session_id) or deque()
        oldest = buf[0][0] if buf else next_seq
        if last_seq > next_seq - 1 or last_seq + 1 < oldest:
            # Client is ahead of the server (server restarted) or the gap was evicted.
            raise SeqExpired(oldest)
        return [msg for (seq, msg) in buf if seq > last_seq]

    def evict(self, session_id: str) -> None:
        self._bufs.pop(session_id, None)
```

Tune `max_retain` for your session message volume. A 10-minute session at 3 messages/second uses ~1800 messages.

## Step 3 — Handle the resume handshake

On a new WebSocket connection, the server reads handshake frames before any transcript traffic. Under the session lock it attaches the new socket, snapshots the missed range, acknowledges, then replays. Because live `send` calls wait on the same lock, no message can be sent to the old socket after the snapshot, and live messages arrive after the replay in `seq` order.

```python
async def resume(session: Session, ws, last_seq: int) -> bool:
    async with session.lock:
        try:
            missed = session._store.since(session.id, last_seq, session._next_seq)
        except SeqExpired as e:
            # Answer before replaying anything; do not attach.
            await ws.send_json({"type": "seq_expired", "oldest": e.oldest,
                                "next": session._next_seq})
            return False
        old, session._ws = session._ws, ws          # attach first ...
        if old is not None and old is not ws:
            await old.send_json({"type": "displaced"})
            await old.close()
        await ws.send_json({"type": "resumed", "from": last_seq + 1,
                            "to": session._next_seq - 1})
        for msg in missed:                           # ... then replay, still under the lock
            await ws.send_json(msg)
    return True


async def on_connect(ws, session_manager) -> None:
    while True:                                      # a client may retry after seq_expired
        first = await ws.receive_json()
        if first.get("type") != "resume":
            await ws.send_json({"type": "error", "code": "unexpected_handshake"})
            await ws.close()
            return
        session = session_manager.get(first["session_id"])
        if session is None:
            await ws.send_json({"type": "error", "code": "session_not_found"})
            await ws.close()
            return
        if await resume(session, ws, int(first["last_seq"])):
            return                                   # attached; live traffic flows via send()
```

Session creation is a separate call (for example `POST /sessions`) that returns the `session_id`; a brand-new client then resumes with `last_seq: -1`.

## Step 4 — Client reconnect loop

```typescript
// TypeScript sketch
type ReconnectState =
  | { kind: "connecting"; attempt: number }
  | { kind: "connected" }
  | { kind: "disconnected"; reason: string };

class ReconnectingSession {
  private state: ReconnectState = { kind: "connecting", attempt: 0 };
  private lastSeq = -1;
  private ws: WebSocket | null = null;
  private readonly MAX_ATTEMPTS = 8;
  private readonly BASE_DELAY_MS = 250;
  private readonly MAX_DELAY_MS = 30_000;

  constructor(
    private readonly url: string,
    private readonly sessionId: string,
    private readonly dispatch: (msg: { seq: number }) => void,
    private readonly reloadTranscript: () => Promise<number>, // returns the snapshot's last seq
  ) {}

  start() { this.connect(); }

  private sendResume(ws: WebSocket) {
    ws.send(JSON.stringify({ type: "resume", session_id: this.sessionId, last_seq: this.lastSeq }));
  }

  private connect() {
    const ws = new WebSocket(this.url);
    this.ws = ws;
    ws.onopen = () => this.sendResume(ws);
    ws.onmessage = (e: MessageEvent) => {
      if (ws !== this.ws) return;                      // ignore frames from a superseded socket
      const msg = JSON.parse(e.data as string);
      // 1. Handshake and error frames carry no seq: route them first.
      switch (msg.type) {
        case "resumed":                                // connected on the ack, even if nothing was missed
          this.state = { kind: "connected" };
          return;
        case "seq_expired":                            // range evicted: reload, then resume again
          this.reloadTranscript().then(
            (snapshotSeq) => { this.lastSeq = snapshotSeq; this.sendResume(ws); },
            () => this.fail("reload_failed"),
          );
          return;
        case "error":                                  // never marks the session connected
        case "displaced":
          this.fail(msg.type === "error" ? msg.code : "displaced");
          return;
      }
      // 2. Sequenced traffic: drop duplicates, reconnect on a gap.
      if (this.state.kind !== "connected" || typeof msg.seq !== "number") return;
      if (msg.seq <= this.lastSeq) return;
      if (msg.seq !== this.lastSeq + 1) { ws.close(); return; } // gap: resume from lastSeq
      this.lastSeq = msg.seq;
      this.dispatch(msg);
    };
    ws.onclose = () => {                               // wired on every socket, in every state
      if (ws !== this.ws) return;
      this.ws = null;
      if (this.state.kind === "disconnected") return;
      const attempt = this.state.kind === "connecting" ? this.state.attempt + 1 : 0;
      this.scheduleReconnect(attempt);
    };
  }

  private scheduleReconnect(attempt: number) {
    if (attempt >= this.MAX_ATTEMPTS) { this.fail("max_attempts_exceeded"); return; }
    this.state = { kind: "connecting", attempt };
    const cap = Math.min(this.MAX_DELAY_MS, this.BASE_DELAY_MS * 2 ** attempt);
    setTimeout(() => this.connect(), Math.random() * cap); // full jitter
  }

  private fail(reason: string) {
    this.state = { kind: "disconnected", reason };
    const ws = this.ws;
    this.ws = null;
    ws?.close();
  }
}
```

What this loop guarantees:
- `connected` is set only by the server's `resumed` acknowledgement, so an idle resume with nothing missed still completes, and an error frame never looks like a healthy connection.
- `onclose` is wired on every socket, so a drop after a successful reconnect starts a new reconnect cycle.
- Messages with `seq <= lastSeq` are dropped; a gap forces a resume instead of silently skipping.
- Full-jitter backoff keeps many clients from reconnecting in lockstep after a server restart.

## Step 5 — Edge cases to handle

| Case | Handling |
|------|---------|
| `last_seq` outside the retained range | Server replies `{type: "seq_expired", oldest, next}` before replaying anything and does not attach. Client reloads the full transcript out of band, sets `lastSeq` to the snapshot position, and resumes again. Show "session too old to resume" only if the reload fails |
| `session_id` not found | Server replies `{type: "error", code: "session_not_found"}` and closes. Client clears local state and starts a new session |
| Duplicate reconnect (two clients resume the same session as controller) | Server attaches the new socket; the old one gets `{type: "displaced"}` and is closed |
| Server restart (in-memory store lost) | Use a Redis ZSET or DB-backed store. Without one, the client's `last_seq` is ahead of the server's counter, so `since` raises and recovery is the `seq_expired` path |
| Viewer-only mode | Resume handshake carries `role: "viewer"`. Viewers are attached as read-only listeners and never receive control prompts they could answer |
| Out-of-order or missing `seq` on the client | Close and resume from `lastSeq`; never advance `lastSeq` past a gap |

## Step 6 — ACP stdio variant

Do not bolt a custom `last_seq` method onto ACP. ACP defines its own session methods: `session/load` replays the conversation to the client, and `session/resume` re-attaches without replay. Check the ACP protocol schema for the version you target, and the capabilities the agent advertises, before relying on either.

Session state is held by the agent process (or daemon), not the editor. ACP reconnect is process re-attach, not full restart.

## Anti-patterns

- Using wall-clock timestamps instead of sequence numbers for "resume from here." Clocks drift; sequence numbers do not.
- Storing the seq store in the WebSocket connection object. The store must outlive the connection.
- Re-assigning `seq = 0` on every reconnect. New messages will collide with retained messages in the store.
- Snapshotting the missed range and attaching the new socket as separate, unlocked steps. Messages sent in between go to the dead socket and are missing from the snapshot.
- Truncating the buffer silently. Evicting old messages is fine; answering a resume for an evicted range as if it succeeded is not.
- Treating any inbound frame as proof of a healthy connection. Only the resume acknowledgement is.

## Related

- [`transport-selection.md`](transport-selection.md) — When to use WebSocket vs SSE vs HTTP POST vs ACP stdio
- [`bridge-transport-and-permission-bridging.md`](bridge-transport-and-permission-bridging.md) — Control-message schema and permission bridging
