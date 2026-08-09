# Durable Execution Landscape

> Last verified: 2026-07-11. Re-verify platform release notes before making version-specific recommendations.

Platform choices, breaking changes, and production traps for durable workflow runtimes.

## Table of Contents

- [Temporal v1.x Patterns](#temporal-v1x-patterns)
- [Trigger.dev v4 (v3 Fully Shut Down)](#triggerdev-v4-v3-fully-shut-down)
- [n8n 2.x Breaking Connectors](#n8n-2x-breaking-connectors)
- [LangGraph vs Langflow Divergence](#langgraph-vs-langflow-divergence)
- [Known Production Traps — Verify Before Advising](#april-2026-production-traps)

---

## Temporal v1.x Patterns

Temporal Server v1.26+ (latest stable at last verification). TypeScript SDK v1.10+, Go SDK v1.28+.

### Core durable-execution patterns

**Activity with retry policy:**

```ts
// workflow.ts
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { sendEmail, chargeCard } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30s',
  retry: {
    maximumAttempts: 5,
    initialInterval: '1s',
    backoffCoefficient: 2,
    maximumInterval: '30s',
    nonRetryableErrorTypes: ['PaymentDeclinedError'],
  },
});
```

**Signal + query pattern (human-in-the-loop):**

```ts
import { defineSignal, defineQuery, setHandler, condition } from '@temporalio/workflow';

const approveSignal = defineSignal<[{ approvedBy: string }]>('approve');
const statusQuery  = defineQuery<string>('status');

export async function approvalWorkflow(orderId: string) {
  let approved = false;
  let approver = '';

  setHandler(approveSignal, ({ approvedBy }) => { approved = true; approver = approvedBy; });
  setHandler(statusQuery,   () => approved ? `approved by ${approver}` : 'pending');

  await condition(() => approved, '7d');  // timeout after 7 days
  return { orderId, approver };
}
```

**Versioning (patching):**

```ts
import { patched } from '@temporalio/workflow';

// Safe deploy of new logic without breaking running instances
if (patched('add-fraud-check-v2')) {
  await runFraudCheck();
}
```

### Namespace and task-queue hygiene

- One task queue per worker fleet version; never share a task queue across breaking SDK versions
- Use `schedules` (GA in v1.21+) instead of cron workflows; schedules survive server restarts without open instances

---

## Trigger.dev v4 (v3 Fully Shut Down)

Trigger.dev v3 stopped accepting new deploys 2026-04-01 and was fully shut down 2026-07-01 — v4 is the only supported line; there is no fallback path to v3 infrastructure. v4 is GA and layers on top of the v3 execution model rather than rewriting it (unlike the v2→v3 rewrite), so most migrations complete in minutes, but several APIs changed shape.

**v3 → v4 migration required changes:**

| v3 pattern | v4 pattern |
|------------|------------|
| `import { task } from '@trigger.dev/sdk/v3'` | `import { task } from '@trigger.dev/sdk'` (the `/v3` path still resolves but is deprecated and slated for removal) |
| `myTask.trigger(data, { queue: { name, concurrencyLimit } })` (queue created on demand) | `const q = queue({ name, concurrencyLimit }); myTask.trigger(data, { queue: 'name' })` — queues must be predefined, not created inline |
| `onSuccess: (payload, output, { ctx }) => {}` | `onSuccess: ({ payload, ctx, task, output }) => {}` — hook params are unified into one destructurable object |
| `ctx.attempt.id` / `ctx.attempt.status` | `ctx.attempt.number` (the former fields were removed) |
| `batchTrigger()` returning runs directly | `const handle = await tasks.batchTrigger(...); const batch = await batch.retrieve(handle.batchId)` |

**v4 task definition:**

```ts
import { task, queue } from '@trigger.dev/sdk';

const orderQueue = queue({ name: 'orders', concurrencyLimit: 10 });

export const processOrder = task({
  id: 'process-order',
  queue: orderQueue,
  maxDuration: 300,  // seconds
  retry: { maxAttempts: 3 },
  run: async (payload: { orderId: string }) => {
    // idempotent work here
    return { processed: true };
  },
});
```

**Self-hosted:** v4 self-hosting collapsed the v3 provider + coordinator + `trigger-worker` split into a single supervisor process. The reference Docker Compose stack bundles Postgres, Redis, ElectricSQL, ClickHouse, a container registry, and MinIO object storage — `docker compose up` with no separate startup scripts. Confirm current infra requirements against the v4 self-hosting docs before provisioning; the compose file is a starting point, not a production-hardened deployment on its own. Migrating v3→v4 can change Trigger.dev's outbound static IPs — update any IP allowlists (databases, third-party APIs) before or immediately after cutover.

---

## n8n 2.x Breaking Connectors

n8n reached 2.0 in 2026 (verify the exact date and current minor before advising — n8n ships new minors most weeks). n8n's self-hosted Community Edition runs under the fair-code **Sustainable Use License**: free for internal business use and modification, but restricted once the commercial value offered to a third party derives substantially from n8n itself (e.g., hosting a multi-tenant instance and charging others for access, or white-labeling it as your own product). Verify current license text before recommending a resale or managed-hosting model.

**2.0 breaking changes that affect existing workflows:**

| Area | Change | Fix |
|------|--------|-----|
| Task runners | Code node executions now run in isolated task-runner processes by default | Confirm custom Code node logic does not depend on same-process access to the main n8n runtime |
| Environment variables | Code nodes can no longer read `process.env` by default | Explicitly allow required variables, or pass values in via node parameters instead |
| SQLite driver | The pooled SQLite driver (`sqlite-pooled`) becomes the default; `DB_SQLITE_POOL_SIZE` controls pool size | Self-hosted docs still recommend Postgres for any production instance — SQLite remains on a deprecation path for production use |
| Binary data mode | The in-memory default binary-data mode is removed | Explicitly set `filesystem` (regular mode) or `database` (queue mode) for `N8N_DEFAULT_BINARY_DATA_MODE` |
| `--tunnel` CLI flag | Removed | Use ngrok, localtunnel, or Cloudflare Tunnel for local webhook testing |
| Migration tooling | A Migration Report tool flags workflow- and instance-level issues before upgrade | Run it before any 1.x → 2.x upgrade |

**Legacy 1.x-era traps (relevant only to instances not yet upgraded):** the Function node was removed in favor of the Code node at the 1.0 launch; Slack node v2 required a channel ID instead of a channel name; webhook response mode defaulted to `Response Node` instead of `Last Node`. Confirm the target instance's major version before applying 1.x-specific fixes.

**Community nodes security note:** n8n flags community nodes that have not been verified against its security policy and runs them in a sandboxed process by default. Running unverified community nodes on internet-facing instances is a supply-chain risk — pin versions in `package.json` and review changelogs regardless of major version.

---

## LangGraph vs Langflow Divergence

Both tools address AI workflow composition but have diverged significantly since 2024, and LangGraph reached a 1.0 milestone in 2026.

### LangGraph (LangChain ecosystem)

- **Model:** Code-first state graph; nodes are Python/JS functions; edges are conditional transitions
- **Primary use:** Multi-agent orchestration, long-running agent loops, checkpointed state
- **Persistence:** Built-in `checkpointer` (Postgres, SQLite, Redis) for interrupt/resume
- **Release cadence:** LangGraph 1.0 shipped alongside LangChain 1.0 in 2026 and is marked Production/Stable; it has continued on a 1.x line since (multiple minors shipping monthly) — verify the current minor before pinning code samples to a specific version
- **When to choose:** Complex agent graphs, human-in-the-loop approval steps, replay debugging

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

builder = StateGraph(MyState)
builder.add_node("agent", call_agent)
builder.add_node("tools", call_tools)
builder.add_conditional_edges("agent", route_fn, {"tools": "tools", "end": END})
builder.set_entry_point("agent")

checkpointer = SqliteSaver.from_conn_string(":memory:")
graph = builder.compile(checkpointer=checkpointer)
```

### Langflow

- **Model:** Visual drag-and-drop flow builder; LangChain components as blocks
- **Primary use:** Rapid LLM pipeline prototyping, non-engineer-facing AI tool builders
- **Ownership change:** DataStax acquired Langflow in 2024; IBM's acquisition of DataStax closed in 2025–2026. The DataStax-hosted managed Langflow product was deprecated (2026-03-09) and shut down (2026-04-09) — do not recommend it as a current managed option. The open-source `langflow-ai/langflow` repo continues to be maintained, now under IBM's stewardship.
- **Backend:** FastAPI + React; self-hostable via Docker
- **When to choose:** Visual authoring speed matters; flows are model-centric and change frequently; prototyping before LangGraph migration; verify current managed-hosting options before assuming DataStax Astra still offers one

### Decision matrix

| Factor | LangGraph | Langflow |
|--------|-----------|----------|
| Code review / git diff | Native (Python/JS files) | Export JSON; hard to diff |
| Checkpointing / replay | Built-in | Not available |
| Non-engineer authoring | Minimal | Strong |
| Production SLOs | Suitable | Not recommended for critical paths |
| LangChain version lock | Yes | Yes |

---

## Known Production Traps — Verify Before Advising

- **Temporal Nexus is GA for the Python SDK; public preview for TypeScript and .NET SDKs.** Cross-namespace service calls via Nexus endpoints are production-usable on Go, Java, and Python; treat TS/.NET Nexus usage as preview-grade and re-check SDK-specific GA status before committing production workflows to it.
- **Trigger.dev v4 warm starts vs. v3 cold starts:** v4 reuses a warm machine for the next run of the same task version instead of always cold-booting, cutting most starts to roughly 100-300ms; this is a meaningful latency change from v3 and should be re-verified against current benchmarks rather than assumed.
- **n8n execution log retention:** Default retention is time- and count-bounded; exceeded logs are silently deleted. Set `EXECUTIONS_DATA_MAX_AGE` (and related pruning variables) explicitly regardless of major version.
- **LangGraph `interrupt` primitive:** The `interrupt()` function is the current human-in-the-loop primitive, replacing the older `NodeInterrupt` exception pattern. Verify the exact primitive name and signature against the installed LangGraph 1.x minor before writing code samples — the API has continued to evolve across 1.x releases.
- **Langflow API run endpoint:** `POST /api/v1/run/{flow_id}` uses `input_value` (not `inputs`) as the text-input key as of the 1.2-era schema. Re-verify the request schema against the currently installed Langflow version before integrating — self-hosted and any managed offering can diverge.
