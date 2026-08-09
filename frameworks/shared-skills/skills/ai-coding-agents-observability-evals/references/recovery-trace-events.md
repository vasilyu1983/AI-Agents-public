# Recovery Trace Events

Concrete examples of the trace events emitted during agent recovery, reconnect, and cancellation scenarios. Use these as the reference when building trace parsers, eval harnesses, or observability dashboards.

## Table of Contents

- [Event Envelope](#event-envelope)
- [Event Catalog](#event-catalog)
- [Using Recovery Events in Evals](#using-recovery-events-in-evals)

---

## Event Envelope

All events share this envelope. Fields marked `*` are required.

```jsonc
{
  "event":      "string*",          // event name (see catalog below)
  "session_id": "string*",          // stable ID for the session
  "task_id":    "string | null",    // task the event belongs to; null for session-level events
  "turn":       "integer | null",   // agent turn number when event fired; null for async events
  "ts":         "string*",          // ISO-8601 timestamp with milliseconds
  "data":       "object"            // event-specific payload (see per-event schema below)
}
```

---

## Event Catalog

### 1. `agent.recovery.started`

Fired when the agent detects a recoverable error (tool failure, partial tool output, unexpected model stop) and enters the recovery branch.

```json
{
  "event": "agent.recovery.started",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": "task_review_pr_42",
  "turn": 7,
  "ts": "2026-04-27T14:22:01.304Z",
  "data": {
    "trigger": "tool_error",
    "tool_name": "Bash",
    "error_code": "ETIMEDOUT",
    "error_message": "Command timed out after 30s: npm test",
    "recovery_strategy": "retry_with_timeout_increase",
    "attempt": 1,
    "max_attempts": 3
  }
}
```

**Fields:**

| Field | Type | Meaning |
|-------|------|---------|
| `trigger` | string | What caused recovery: `tool_error`, `partial_output`, `model_stop`, `context_overflow` |
| `tool_name` | string | Tool that failed (if `trigger = tool_error`) |
| `error_code` | string | Machine-readable error code |
| `recovery_strategy` | string | Strategy selected: `retry_with_timeout_increase`, `fallback_tool`, `replan`, `abort` |
| `attempt` | integer | Current attempt number (1-based) |
| `max_attempts` | integer | Maximum attempts before the strategy escalates to `abort` |

---

### 2. `agent.recovery.succeeded`

Fired when the recovery attempt produced an acceptable result and the agent resumes normal execution.

```json
{
  "event": "agent.recovery.succeeded",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": "task_review_pr_42",
  "turn": 8,
  "ts": "2026-04-27T14:22:14.817Z",
  "data": {
    "recovery_strategy": "retry_with_timeout_increase",
    "attempt": 2,
    "elapsed_ms": 13513,
    "resumed_from_turn": 7
  }
}
```

---

### 3. `agent.recovery.failed`

Fired when all recovery attempts are exhausted and the task is being escalated or aborted.

```json
{
  "event": "agent.recovery.failed",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": "task_review_pr_42",
  "turn": 9,
  "ts": "2026-04-27T14:22:45.001Z",
  "data": {
    "trigger": "tool_error",
    "recovery_strategy": "retry_with_timeout_increase",
    "total_attempts": 3,
    "total_elapsed_ms": 43697,
    "escalation": "task_abort",
    "reason": "npm test consistently times out; environment likely unhealthy"
  }
}
```

---

### 4. `session.reconnect.initiated`

Fired when the transport layer detects a dropped connection and begins reconnection. Common in remote-runtime configurations (WebSocket or SSE streams).

```json
{
  "event": "session.reconnect.initiated",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": null,
  "turn": null,
  "ts": "2026-04-27T14:35:08.112Z",
  "data": {
    "transport": "websocket",
    "disconnect_reason": "network_timeout",
    "reconnect_attempt": 1,
    "backoff_ms": 1000,
    "last_ack_turn": 12,
    "resume_token": "tok_8xkq3p2"
  }
}
```

**Fields:**

| Field | Type | Meaning |
|-------|------|---------|
| `transport` | string | `websocket`, `sse`, `grpc`, `http_polling` |
| `disconnect_reason` | string | `network_timeout`, `server_closed`, `client_closed`, `auth_expired` |
| `last_ack_turn` | integer | Last turn the server acknowledged; replay starts from `last_ack_turn + 1` |
| `resume_token` | string | Opaque token used to resume the session without full re-auth |

---

### 5. `session.reconnect.succeeded`

```json
{
  "event": "session.reconnect.succeeded",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": null,
  "turn": null,
  "ts": "2026-04-27T14:35:09.344Z",
  "data": {
    "transport": "websocket",
    "reconnect_attempt": 1,
    "replay_turns": 0,
    "session_state": "running"
  }
}
```

`replay_turns`: number of turns replayed to re-sync the agent state after reconnect. Zero means the server held state and no replay was needed.

---

### 6. `session.reconnect.failed`

```json
{
  "event": "session.reconnect.failed",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": null,
  "turn": null,
  "ts": "2026-04-27T14:35:59.002Z",
  "data": {
    "transport": "websocket",
    "total_attempts": 5,
    "total_elapsed_ms": 50890,
    "final_reason": "auth_expired",
    "session_state": "dead",
    "recovery_hint": "Re-authenticate and create a new session; this session cannot be resumed."
  }
}
```

---

### 7. `task.cancelled`

Fired when the user or orchestrator explicitly cancels a running task.

```json
{
  "event": "task.cancelled",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": "task_refactor_auth",
  "turn": 15,
  "ts": "2026-04-27T14:41:33.780Z",
  "data": {
    "cancelled_by": "user",
    "reason": "User pressed Ctrl+C",
    "last_completed_turn": 14,
    "partial_artifacts": [
      { "path": "src/auth/token.ts", "status": "modified_uncommitted" }
    ],
    "rollback_action": "none"
  }
}
```

**Fields:**

| Field | Type | Meaning |
|-------|------|---------|
| `cancelled_by` | string | `user`, `orchestrator`, `timeout`, `budget_exceeded` |
| `partial_artifacts` | array | Files that were modified but not yet committed when cancellation fired |
| `rollback_action` | string | `none`, `git_restore`, `snapshot_restore` — what the runtime did with partial artifacts |

---

### 8. `task.cancellation.completed`

Fired after the cancellation handshake is fully resolved (partial artifacts handled, cleanup done).

```json
{
  "event": "task.cancellation.completed",
  "session_id": "sess_01j9kx2fvg3b4h7r",
  "task_id": "task_refactor_auth",
  "turn": null,
  "ts": "2026-04-27T14:41:33.952Z",
  "data": {
    "rollback_status": "skipped",
    "artifacts_left_on_disk": true,
    "cleanup_ms": 172
  }
}
```

---

## Using Recovery Events in Evals

1. **Recovery ratio**: `agent.recovery.succeeded` / (`agent.recovery.succeeded` + `agent.recovery.failed`) — measures how often the agent self-heals.
2. **Mean recovery time**: `elapsed_ms` from `agent.recovery.started` to `agent.recovery.succeeded` per strategy.
3. **Reconnect rate**: `session.reconnect.initiated` count per session-hour — a spike indicates transport instability.
4. **Cancellation cleanliness**: `rollback_action != "none"` rate — partial artifacts left on disk should trend toward zero.
5. **Partial-artifact rate after cancel**: tasks where `partial_artifacts` is non-empty at `task.cancelled` — high values suggest the agent is not checkpointing frequently enough.
