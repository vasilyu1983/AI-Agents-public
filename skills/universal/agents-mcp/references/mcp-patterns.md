# MCP Tool Result Patterns

Worked shapes for the rules in [`../SKILL.md`](../SKILL.md#tool-result-contract), the tool result contract. The shapes are wire-level JSON so they hold across SDKs. The handler sketches use TypeScript-like pseudocode: translate them to your SDK's high-level API after the SDK lane lookup in [mcp-custom.md](mcp-custom.md#sdk-lane-lookup).

## Table of Contents

- [Tool Result Contract](#tool-result-contract)
- [Handler Sketch: Choosing the Error Channel](#handler-sketch-choosing-the-error-channel)
- [Pagination and Truncation](#pagination-and-truncation)
- [Idempotent Writes](#idempotent-writes)
- [Upstream REST Calls with Retry](#upstream-rest-calls-with-retry)
- [Where Other Patterns Live](#where-other-patterns-live)

## Tool Result Contract

**Success.** Return a text rendering for the model and, when a caller parses the result, `structuredContent` that conforms to the tool's declared `outputSchema`:

```json
{
  "content": [{ "type": "text", "text": "Order 4821 (Jane Doe): shipped on 12 Mar via DHL." }],
  "structuredContent": { "orderId": "4821", "customer": "Jane Doe", "status": "shipped" }
}
```

**Tool execution error (the model can act on it).** Use a normal result with `isError: true`. The text names the failed input, the reason, and the next call:

```json
{
  "isError": true,
  "content": [{
    "type": "text",
    "text": "No order with id \"4812\". Did you mean 4821? List recent orders with list_orders(customer_email=..., limit=5)."
  }]
}
```

Use this channel for: not found, permission denied on a resource, upstream 4xx/5xx after retries, rate limits (say when to retry), business-rule rejections, and arguments the model can correct.

**Protocol error (the request itself is unusable).** A JSON-RPC `error` response is for an unknown tool name, a malformed request, or a server fault the model cannot route around. Clients may show these to the user instead of the model, so a recoverable failure sent here takes away the model's chance to self-correct. The spec's tools page for your target revision defines where argument-validation failures belong; check it and do not guess.

## Handler Sketch: Choosing the Error Channel

```typescript
// Pseudocode: map domain failures to isError results; let only true faults escape.
async function handleGetOrder({ orderId }) {
  try {
    const order = await orders.get(orderId);
    if (!order) {
      return toolError(`No order with id "${orderId}". Find ids with list_orders(customer_email=...).`);
    }
    return {
      content: [{ type: "text", text: `Order ${order.id}: ${order.status}` }],
      structuredContent: { orderId: order.id, status: order.status },
    };
  } catch (err) {
    if (err.code === "EACCES" || err.status === 403) {
      return toolError(`Access to order "${orderId}" is denied for this user. Ask the user to confirm the account.`);
    }
    if (err.status === 429) {
      return toolError("Order service is rate-limited. Retry in about 30 seconds or narrow the query.");
    }
    throw err; // genuine server fault: let the SDK turn it into a protocol error
  }
}

const toolError = (text) => ({ isError: true, content: [{ type: "text", text }] });
```

Anti-pattern this replaces: throwing `InvalidParams` protocol errors for `ENOENT`/`EACCES`. That hides a fixable situation from the model.

## Pagination and Truncation

Accept `limit` and `cursor`, apply a small default, cap the maximum at the server, and say plainly when there is more:

```json
{
  "content": [{ "type": "text", "text": "50 of 1,240 tickets shown (newest first). More: call list_tickets(cursor=\"t_8812\")." }],
  "structuredContent": { "items": ["…"], "nextCursor": "t_8812", "hasMore": true }
}
```

Rules:

- Fetch `limit + 1` rows to learn `hasMore` without a count query.
- Use an opaque cursor (last seen key), not an offset, for data that changes between calls.
- Truncate long text fields at the server and mark the truncation. Never rely on the client's output cap; clients cut silently or warn only at their own thresholds.
- For large blobs (files, reports), return a `resource_link` the client can fetch instead of inlining the payload.

## Idempotent Writes

Let the caller pass an idempotency key on every write that appends, sends, or charges, and return the stored result on a replay:

```typescript
// Pseudocode. Keep keys in durable storage for real writes; an in-memory map
// only protects a single process lifetime.
async function handleCreateTicket({ idempotencyKey, ...fields }) {
  const prior = await idempotencyStore.get(idempotencyKey);
  if (prior) return prior;                     // replay: same result, no second ticket
  const result = await createTicket(fields);
  await idempotencyStore.put(idempotencyKey, result, { ttlHours: 24 });
  return result;
}
```

Declare `idempotentHint: true` only for tools whose repeat call really has no further effect (see [mcp-custom.md](mcp-custom.md#tool-annotation-hints)).

## Upstream REST Calls with Retry

- Call a fixed, server-owned endpoint per tool. Never let the model supply a base URL, path, or method. Tool names like `api_call(endpoint, method)` are a generic wrapper that bypasses every scope decision.
- Retry only when a retry is safe: network errors, 429, and 5xx on idempotent requests (or writes that carry an idempotency key).
- Honour `Retry-After`. Otherwise use capped exponential backoff with jitter, and put a total time budget below the client's tool timeout.
- After the last attempt, return an `isError` result that states what failed and when to retry. Do not throw a protocol error.

```typescript
async function fetchWithRetry(url, init, { maxRetries = 3, baseMs = 500, capMs = 8000 } = {}) {
  for (let attempt = 0; ; attempt++) {
    let res;
    try {
      res = await fetch(url, { ...init, signal: AbortSignal.timeout(10_000) });
    } catch (err) {
      if (attempt >= maxRetries) throw err;           // caller maps to an isError result
    }
    if (res && res.status !== 429 && res.status < 500) return res;
    if (res && attempt >= maxRetries) return res;     // caller maps status to an isError result
    const retryAfter = Number(res?.headers.get("retry-after"));
    const backoff = Math.min(capMs, baseMs * 2 ** attempt) * (0.5 + Math.random() / 2);
    await sleep(Number.isFinite(retryAfter) && retryAfter > 0 ? retryAfter * 1000 : backoff);
  }
}
```

## Where Other Patterns Live

This file used to carry more patterns. They moved or were dropped:

| Former section | Now |
|---|---|
| Database pooling, multi-database | [mcp-for-dwh.md](mcp-for-dwh.md): server shapes, enforcement layers, audit log |
| Scoped filesystem access | [mcp-security.md](mcp-security.md#safe-filesystem-checklist) |
| Resources and prompt templates | [mcp-custom.md](mcp-custom.md) (capability selection; v1 examples under Old patterns) |
| Zero-trust checklist | [mcp-security.md](mcp-security.md#safe-http-checklist) |
| Multi-agent orchestration across MCP servers | [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md) and [`../../ai-agents/SKILL.md`](../../ai-agents/SKILL.md) |
| GraphQL integration, operational knowledge loop | Dropped: generic client code, and the note-vault pattern is covered by scenario S6 in `../SKILL.md` |

## Related

- [mcp-security.md](mcp-security.md): security hardening guide
- [mcp-servers.md](mcp-servers.md): discovery and adoption
- [`../../ai-agents/references/tool-design-specs.md`](../../ai-agents/references/tool-design-specs.md): generic tool schema and selection design
