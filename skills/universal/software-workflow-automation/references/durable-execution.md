# Durable Execution Landscape

> Version-sensitive content. Check platform release notes before making version-specific recommendations.

Platform choices, breaking changes, and production traps for durable workflow runtimes.

## Table of Contents

- [Temporal v1.x Patterns](#temporal-v1x-patterns)
- [Trigger.dev v4 (v3 Retired)](#triggerdev-v4-v3-retired)
- [n8n 2.x Breaking Connectors](#n8n-2x-breaking-connectors)
- [LangGraph and Langflow](#langgraph-and-langflow)
- [Known Production Traps — Verify Before Advising](#known-production-traps--verify-before-advising)

---

## Temporal v1.x Patterns

Read the installed Server and SDK versions and their compatibility/release notes before upgrading.

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

  const received = await condition(() => approved, '7d'); // illustrative approval window
  if (!received) return { orderId, status: 'pending_escalation' };
  return { orderId, status: 'approved', approver };
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

- Split task queues by workload and use [Worker Versioning](https://docs.temporal.io/worker-versioning) for compatible deployment routing; separate queue names per version are not mandatory. Replay-test histories before rolling out incompatible workflow changes
- Use Schedules instead of cron workflows; schedules survive server restarts without open instances

---

## Trigger.dev v4 (v3 Retired)

Trigger.dev v3 is retired — v4 is the supported line; there is no fallback path to v3 infrastructure. The v4 migration builds on the v3 execution model, but APIs and self-hosting components changed; read the migration guide before upgrading.

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

**Self-hosted:** see [platform-state.md](platform-state.md) for the v4 self-host topology. Migrating v3→v4 can change Trigger.dev's outbound static IPs — update any IP allowlists before or immediately after cutover.

---

## n8n 2.x Breaking Connectors

Resolve the supported stable release from vendor release notes before advising. Version, database and licensing detail lives in [platform-state.md](platform-state.md).

**2.0 breaking changes that affect existing workflows:**

| Area | Change | Fix |
|------|--------|-----|
| Task runners | Code node executions now run in isolated task-runner processes by default | Confirm custom Code node logic does not depend on same-process access to the main n8n runtime |
| Environment variables | Code nodes can no longer read `process.env` by default | Explicitly allow required variables, or pass values in via node parameters instead |
| SQLite driver | The pooled SQLite driver (`sqlite-pooled`) becomes the default; `DB_SQLITE_POOL_SIZE` controls pool size | SQLite is still supported (pooled driver only); Postgres is recommended for production; MySQL/MariaDB support was removed in 2.0 |
| Binary data mode | The in-memory default binary-data mode is removed | Explicitly set `filesystem` (regular mode) or `database` (queue mode) for `N8N_DEFAULT_BINARY_DATA_MODE` |
| `--tunnel` CLI flag | Removed | Use ngrok, localtunnel, or Cloudflare Tunnel for local webhook testing |
| Migration tooling | A Migration Report tool flags workflow- and instance-level issues before upgrade | Run it before any 1.x → 2.x upgrade |

**Legacy 1.x-era traps (relevant only to instances not yet upgraded):** the Function node was removed in favor of the Code node at the 1.0 launch; Slack node v2 required a channel ID instead of a channel name; webhook response mode defaulted to `Response Node` instead of `Last Node`. Confirm the target instance's major version before applying 1.x-specific fixes.

**Community nodes security note:** [Community nodes can access the host and workflow data](https://docs.n8n.io/integrations/community-nodes/risks/); they are not sandboxed merely because Code nodes use task runners. Review code, pin versions and restrict installation on internet-facing instances.

---

## LangGraph and Langflow

LangGraph internals (graph API, checkpointers, interrupt/resume) are covered in [../../ai-agents/references/framework-landscape.md](../../ai-agents/references/framework-landscape.md). For workflow use: run LangGraph with a durable checkpointer (for example `PostgresSaver`), never the in-process `MemorySaver`, whenever runs must survive restarts.

### Langflow

- **Model:** Visual drag-and-drop flow builder; LangChain components as blocks; FastAPI + React, self-hostable via Docker
- **Primary use:** Rapid LLM pipeline prototyping, non-engineer-facing AI tool builders
- **Hosting:** Check [Langflow deployment options](https://docs.langflow.org/deployment-overview) for managed service availability and support before recommending a host.

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

- **Temporal Nexus:** verify Server/SDK support and feature status for cross-namespace calls; test its error handling separately from activities.
- **Trigger.dev startup latency:** compare cold and warm task starts on the chosen hosting/runtime configuration; do not quote a generic latency range.
- **n8n execution log retention:** Default retention is time- and count-bounded; exceeded logs are silently deleted. Set `EXECUTIONS_DATA_MAX_AGE` (and related pruning variables) explicitly regardless of major version.
- **Langflow API run endpoint:** `POST /api/v1/run/{flow_id}` uses `input_value` (not `inputs`) as the text-input key as of the 1.2-era schema. Re-verify the request schema against the currently installed Langflow version before integrating — self-hosted and any managed offering can diverge.
