# Recipe: Resumable Streams with Sequence Numbers

A step-by-step implementation recipe for reconnect-safe remote sessions using sequence-numbered messages. Implements the "sequence-aware resume" pattern described in `transport-selection.md` and `bridge-transport-and-permission-bridging.md`.

## Table of Contents

- [Goal](#goal)
- [Components](#components)
- [Step 1 — Assign sequence numbers server-side](#step-1--assign-sequence-numbers-server-side)
- [Step 2 — Retain messages with a bounded ring buffer](#step-2--retain-messages-with-a-bounded-ring-buffer)
- [Step 3 — Handle the resume handshake](#step-3--handle-the-resume-handshake)
- [Step 4 — Client reconnect loop](#step-4--client-reconnect-loop)
- [Step 5 — Edge cases to handle](#step-5--edge-cases-to-handle)
- [Step 6 — ACP stdio variant](#step-6--acp-stdio-variant)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## Goal

After any network drop, the client reconnects and the server delivers exactly the messages the client missed — no duplicates, no gaps, no full-replay cost.

Success criteria: a client that disconnects mid-turn and reconnects within the retention window sees all missed transcript and control events in order, with no agent-side side effects.

## Components

| Component | Responsibility |
|-----------|---------------|
| `SeqStore` | Server-side ring buffer of recent messages keyed by `(session_id, seq)` |
| `seq` field | Monotonically increasing integer on every server-pushed message |
| `resume` handshake | First message from client on reconnect; carries `last_seq` |
| `RetentionPolicy` | How long / how many messages to keep for reconnect eligibility |
| `ReconnectState` | Client-side enum: `Connected | Reconnecting(attempt, last_seq) | Disconnected` |

## Step 1 — Assign sequence numbers server-side

Every message the server pushes gets a `seq` before transmission:

```python
# Pseudocode — adapt to your language/framework
class SessionSender:
    def __init__(self, session_id: str, seq_store: SeqStore):
        self._session_id = session_id
        self._seq_store = seq_store
        self._next_seq = 0

    def send(self, ws, message: dict) -> None:
        message["seq"] = self._next_seq
        self._seq_store.put(self._session_id, self._next_seq, message)
        ws.send_json(message)
        self._next_seq += 1
```

Key rules:
- `seq` is per-session, not global.
- Sequence numbers are never reused, even after partial reconnect.
- Control messages (permission prompts, cancellations) get `seq` like any other message.

## Step 2 — Retain messages with a bounded ring buffer

```python
class SeqStore:
    """
    Bounded in-memory ring buffer. Replace with Redis ZSET or DB for multi-process.
    """
    MAX_RETAIN = 2000  # messages

    def __init__(self):
        self._store: dict[str, list[tuple[int, dict]]] = {}

    def put(self, session_id: str, seq: int, message: dict) -> None:
        buf = self._store.setdefault(session_id, [])
        buf.append((seq, message))
        if len(buf) > self.MAX_RETAIN:
            buf.pop(0)

    def since(self, session_id: str, last_seq: int) -> list[dict]:
        buf = self._store.get(session_id, [])
        return [msg for (seq, msg) in buf if seq > last_seq]

    def evict(self, session_id: str) -> None:
        self._store.pop(session_id, None)
```

Tune `MAX_RETAIN` for your session message volume. A 10-minute session at 3 messages/second uses ~1800 messages.

## Step 3 — Handle the resume handshake

On new WebSocket connection, the server reads the first message before routing transcript traffic:

```python
async def on_connect(ws, session_manager, seq_store):
    first = await ws.receive_json()

    if first["type"] == "resume":
        session_id = first["session_id"]
        last_seq = first["last_seq"]

        session = session_manager.get(session_id)
        if session is None:
            await ws.send_json({"type": "error", "code": "session_not_found"})
            await ws.close()
            return

        missed = seq_store.since(session_id, last_seq)
        for msg in missed:
            await ws.send_json(msg)

        # Re-attach the live sender to this new WebSocket
        session.attach_sender(ws)

    elif first["type"] == "new_session":
        session = session_manager.create()
        await ws.send_json({"type": "session_created", "session_id": session.id, "seq": -1})
        session.attach_sender(ws)

    else:
        await ws.send_json({"type": "error", "code": "unexpected_handshake"})
        await ws.close()
```

## Step 4 — Client reconnect loop

```typescript
// TypeScript pseudocode
type ReconnectState =
  | { kind: "connected" }
  | { kind: "reconnecting"; attempt: number; lastSeq: number }
  | { kind: "disconnected"; reason: string };

class ReconnectingSession {
  private state: ReconnectState = { kind: "connected" };
  private lastSeq = -1;
  private ws: WebSocket | null = null;
  private readonly MAX_ATTEMPTS = 8;
  private readonly BASE_DELAY_MS = 250;

  onMessage(msg: ServerMessage) {
    this.lastSeq = msg.seq;
    // dispatch to UI / transcript store
  }

  onDisconnect() {
    if (this.state.kind !== "connected") return;
    this.state = { kind: "reconnecting", attempt: 0, lastSeq: this.lastSeq };
    this.scheduleReconnect();
  }

  private scheduleReconnect() {
    if (this.state.kind !== "reconnecting") return;
    const { attempt, lastSeq } = this.state;
    if (attempt >= this.MAX_ATTEMPTS) {
      this.state = { kind: "disconnected", reason: "max_attempts_exceeded" };
      return;
    }
    const delay = Math.min(this.BASE_DELAY_MS * 2 ** attempt, 30_000);
    setTimeout(() => this.connect(lastSeq), delay);
  }

  private connect(lastSeq: number) {
    this.ws = new WebSocket(SESSION_WS_URL);
    this.ws.onopen = () => {
      this.ws!.send(JSON.stringify({
        type: "resume",
        session_id: SESSION_ID,
        last_seq: lastSeq,
      }));
    };
    this.ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      this.state = { kind: "connected" };
      this.onMessage(msg);
    };
    this.ws.onclose = () => {
      if (this.state.kind === "reconnecting") {
        this.state = {
          ...this.state,
          attempt: this.state.attempt + 1,
        };
        this.scheduleReconnect();
      }
    };
  }
}
```

## Step 5 — Edge cases to handle

| Case | Handling |
|------|---------|
| `last_seq` outside retention window | Server replies `{type: "error", code: "seq_expired"}`. Client falls back to full-transcript reload or shows "session too old to resume" |
| `session_id` not found | Server replies `{type: "error", code: "session_not_found"}`. Client clears local state, starts new session |
| Duplicate reconnect (two clients resume same session) | Server detaches old WebSocket, attaches new one; old client gets `{type: "displaced"}` |
| Server restart (no in-memory seq store) | Use Redis ZSET or DB-backed store. Recovery is same as `seq_expired` fallback |
| Viewer-only mode | Resume handshake carries `role: "viewer"`. Server skips control-message delivery for viewers |

## Step 6 — ACP stdio variant

For ACP (editor ↔ agent stdio), sequence-number resume works the same way but over stdin/stdout line-delimited JSON:

```
# Client (editor) reconnect message
{"jsonrpc": "2.0", "method": "session/resume", "params": {"session_id": "...", "last_seq": 42}}

# Server (agent) catch-up replay
{"jsonrpc": "2.0", "method": "session/message", "params": {..., "seq": 43}}
{"jsonrpc": "2.0", "method": "session/message", "params": {..., "seq": 44}}
```

Session state is held by the agent process (or daemon), not the editor. ACP reconnect is process re-attach, not full restart.

## Anti-patterns

- Using wall-clock timestamps instead of sequence numbers for "resume from here." Clocks drift; sequence numbers do not.
- Storing seq-store in the WebSocket connection object. The store must outlive the connection.
- Re-assigning `seq = 0` on every reconnect. New messages will collide with retained messages in the store.
- Delivering duplicate messages on reconnect because the server did not check `seq > last_seq` strictly.

## Related

- [`transport-selection.md`](transport-selection.md) — When to use WebSocket vs SSE vs HTTP POST vs ACP stdio
- [`bridge-transport-and-permission-bridging.md`](bridge-transport-and-permission-bridging.md) — Control-message schema and permission bridging
