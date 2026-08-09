# Webhook and Queue Triggers

Use this reference when the agent is **Shape A — Hosted / event-triggered**: a fresh agent session is spawned by an external event (webhook delivery, queue message, schedule firing) and runs to completion. The trigger substrate lives outside the agent runtime.

May 2026 baseline: every serious autonomy deployment routes through an idempotent trigger layer. Naked HTTP-to-agent endpoints fail under retries, duplicate webhooks, and cron drift.

## Table of Contents

- [Trigger Topology](#trigger-topology)
- [Trigger Sources Compared (May 2026)](#trigger-sources-compared-may-2026)
- [Idempotency Contract](#idempotency-contract)
- [Deduplication Window](#deduplication-window)
- [Webhook Triggers](#webhook-triggers)
- [Queue Triggers (SQS / Redis Streams / Kafka)](#queue-triggers-sqs--redis-streams--kafka)
- [Schedule Triggers](#schedule-triggers)
- [Dead Letter Queues](#dead-letter-queues)
- [Backpressure and Concurrency](#backpressure-and-concurrency)
- [Trigger Payload Schema](#trigger-payload-schema)
- [Approval Gates Inside the Trigger](#approval-gates-inside-the-trigger)
- [Observability for Triggers](#observability-for-triggers)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## Trigger Topology

```text
  External event                Trigger substrate                Agent runtime
  ┌──────────────┐    HTTP    ┌────────────────────────┐        ┌─────────────────┐
  │  Webhook     │  ────────▶ │  Idempotency layer     │        │  Agent session  │
  │  (Stripe,    │            │  (key → payload hash)  │  ────▶ │  (fresh ctx)    │
  │   GitHub,    │            │  └─ dedup window       │        │                 │
  │   etc.)      │            └──────────┬─────────────┘        │  Loads PRD,     │
  └──────────────┘                       │                      │  skills, MCP    │
                                         ▼                      │  servers        │
  ┌──────────────┐  put     ┌────────────────────────┐          │                 │
  │  Producer    │ ───────▶ │  Queue (SQS/Streams/   │          │  Reports result │
  └──────────────┘          │   Kafka)               │  ────▶   │                 │
                            │  └─ visibility timeout │          └────────┬────────┘
                            └────────────────────────┘                   │
                                                                         ▼
  ┌──────────────┐  cron    ┌────────────────────────┐          ┌─────────────────┐
  │  Scheduler   │ ───────▶ │  Schedule firing       │  ────▶   │  Result sink    │
  │  (cron/EB/   │          │  (with jitter)         │          │  (DB, Slack,    │
  │   /fire)     │          └────────────────────────┘          │  next queue)    │
  └──────────────┘                                              └─────────────────┘
```

Three substrates, one universal trigger contract: every event must carry an idempotency key, schema-validated payload, and replay-safe semantics.

## Trigger Sources Compared (May 2026)

| Source | Delivery | Native Idempotency | Best For | Caution |
|---|---|---|---|---|
| **Anthropic `/fire` + schedule** | At-most-once | No (build yourself) | Schedule-driven agent runs inside Claude Code | Beta header; cap-drop behavior |
| **OpenAI scheduled tasks** | At-most-once | No | Codex scheduled runs | GA but trigger payload is opaque |
| **AWS EventBridge → Lambda → agent** | At-least-once | EventBridge idempotency token | Production-grade scheduling | Lambda 15-min cap forces long agent runs into Step Functions or Temporal |
| **AWS Bedrock AgentCore** | At-most-once for schedules, at-least-once for events | Yes (action-group level) | AWS-native agent stacks | Vendor-locked; payload schema is Bedrock-specific |
| **GitHub Actions (workflow_dispatch / webhooks)** | At-least-once | No | CI-triggered agent runs, PR review agents | Concurrency limits per repo |
| **Webhook gateway (Svix, Hookdeck)** | At-least-once with retry | Yes (idempotency key passthrough) | Multi-source webhook fan-in | Cost scales with volume |
| **SQS standard** | At-least-once | No | High-throughput async work | Duplicates expected; dedup layer required |
| **SQS FIFO** | Exactly-once within 5-min window | Yes (MessageDeduplicationId) | Order-sensitive agent runs | Lower throughput than standard |
| **Redis Streams** | At-least-once | No | Low-latency, single-region | Consumer-group offset tracking needed |
| **Kafka** | At-least-once (configurable) | No | High-volume multi-consumer | Operational complexity high |
| **Inngest / Trigger.dev / Temporal** | Exactly-once (durable) | Yes | Multi-step agent workflows | Covered in [`durable-trigger-integration.md`](durable-trigger-integration.md) |

Choose by failure tolerance, not by familiarity. Most agent products land on either Temporal/Inngest (for orchestration) or SQS+Lambda (for fan-out), with webhooks gated through Svix or Hookdeck.

## Idempotency Contract

Every trigger event has an **idempotency key**. The agent runtime stores `(key → first_result, expires_at)` in a fast KV (Redis, DynamoDB). On duplicate delivery, the stored result is returned without invoking the agent.

```python
import redis, hashlib, json
from datetime import timedelta

r = redis.Redis()
IDEMP_TTL = timedelta(hours=24)

def idempotency_key(event: dict) -> str:
    # Prefer the source's native key; fall back to payload hash.
    return event.get("idempotency_key") or hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()

def try_acquire(key: str) -> tuple[bool, dict | None]:
    pipe = r.pipeline()
    pipe.set(f"idemp:{key}:lock", "1", nx=True, ex=int(IDEMP_TTL.total_seconds()))
    pipe.get(f"idemp:{key}:result")
    acquired, prior = pipe.execute()
    if not acquired and prior:
        return False, json.loads(prior)
    return True, None

def record_result(key: str, result: dict) -> None:
    r.set(f"idemp:{key}:result", json.dumps(result), ex=int(IDEMP_TTL.total_seconds()))
```

Rules:

1. The agent invocation is wrapped in `try_acquire` / `record_result`.
2. The key TTL must exceed the maximum upstream retry window (24h is safe for most webhook providers).
3. If `try_acquire` returns `(False, None)` the request is in flight — return 409 and let the upstream retry later.
4. The result stored must be deterministic enough to replay (typically: the structured response payload, not the full agent transcript).

## Deduplication Window

Idempotency keys catch exact replays. Dedup windows catch near-duplicates: same logical event, different timestamps or trace IDs.

Pattern: derive a content-based dedup key (e.g., `(user_id, action_type, target_id)`) and reject anything seen in the last N minutes.

```python
def is_duplicate(dedup_key: str, window_seconds: int = 300) -> bool:
    return r.set(f"dedup:{dedup_key}", "1", nx=True, ex=window_seconds) is None
```

Use 5 minutes for user-action triggers, 1 hour for periodic recompute triggers, 24h for cron-driven catch-up runs.

## Webhook Triggers

Stripe, GitHub, Linear, Slack, Intercom — all webhook providers retry on non-2xx. Build for retries from day one.

Minimum handler:

```python
from fastapi import FastAPI, Request, Header, HTTPException
import hmac, hashlib

app = FastAPI()
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]

def verify_signature(body: bytes, signature: str) -> bool:
    expected = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(...)):
    body = await request.body()
    if not verify_signature(body, stripe_signature):
        raise HTTPException(401, "bad signature")
    event = json.loads(body)
    key = event["id"]  # Stripe sends a unique event id
    acquired, prior = try_acquire(key)
    if not acquired:
        return prior or {"status": "in_flight"}
    # Hand off to agent
    result = await invoke_agent(event)
    record_result(key, result)
    return result
```

Critical: **always return 2xx within the provider's timeout** (Stripe: 30s, GitHub: 10s, most others: <10s). If the agent run is longer, enqueue to a worker queue and return immediately.

```python
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(...)):
    body = await request.body()
    if not verify_signature(body, stripe_signature):
        raise HTTPException(401, "bad signature")
    event = json.loads(body)
    await sqs.send_message(QueueUrl=QUEUE, MessageBody=json.dumps(event),
                           MessageDeduplicationId=event["id"],
                           MessageGroupId=event["account"])
    return {"status": "queued"}
```

## Queue Triggers (SQS / Redis Streams / Kafka)

SQS-driven Lambda is the path of least resistance for agent fan-out. Up to 1000 concurrent agent invocations, automatic retries, native DLQ.

```python
# Lambda handler
def handler(event, context):
    for record in event["Records"]:
        msg = json.loads(record["body"])
        key = msg.get("idempotency_key") or record["messageId"]
        acquired, prior = try_acquire(key)
        if not acquired:
            continue
        try:
            result = run_agent_sync(msg)
            record_result(key, result)
        except RetryableError as e:
            raise  # SQS will retry; release the lock first
        except FatalError as e:
            send_to_dlq(record, str(e))
```

Visibility timeout = max agent run time + buffer. If agents take 5 minutes, set visibility timeout to 6 minutes minimum. If they exceed, SQS will redeliver and you'll run twice — idempotency key catches this, but it costs you tokens.

**Kafka pattern** (for very high volume):

```python
from confluent_kafka import Consumer
consumer = Consumer({
    "bootstrap.servers": "...",
    "group.id": "agent-workers",
    "enable.auto.commit": False,  # commit only after successful agent run
})
consumer.subscribe(["agent-triggers"])

while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None or msg.error():
        continue
    event = json.loads(msg.value())
    key = event["idempotency_key"]
    acquired, prior = try_acquire(key)
    if acquired:
        try:
            result = run_agent_sync(event)
            record_result(key, result)
            consumer.commit(msg)
        except Exception:
            # Do not commit — Kafka redelivers on next poll
            log_failure(event)
    else:
        consumer.commit(msg)  # already handled, advance offset
```

## Schedule Triggers

Use schedules for: periodic reconciliation, daily digests, hourly polling of external systems, time-of-day announcements.

| Substrate | Cron support | Drift tolerance | Notes |
|---|---|---|---|
| Anthropic `/fire` schedules | Yes | ~minute | Beta; see [`claude-code-routines.md`](claude-code-routines.md) |
| AWS EventBridge Scheduler | Yes, timezone-aware | <1 second | Default for AWS stacks |
| GCP Cloud Scheduler | Yes | <1 second | Default for GCP stacks |
| Temporal cron workflows | Yes | <1 second | Best for multi-step scheduled work |
| GitHub Actions `schedule:` | Yes (UTC only) | 5–30 min (often delayed) | Free but unreliable for precise timing |

**Always add jitter** to schedules that hit shared resources:

```python
import random
def cron_with_jitter(base_cron: str, max_jitter_seconds: int = 60):
    return f"sleep {random.randint(0, max_jitter_seconds)} && {base_cron}"
```

Without jitter, 100 agents on the same `0 * * * *` schedule will hammer the LLM provider at the same instant.

## Dead Letter Queues

A DLQ is mandatory. Any agent run that fails N times (default 3) must land in the DLQ with full context so a human can triage.

DLQ payload schema:

```json
{
  "original_event": { ... },
  "attempts": 3,
  "errors": [
    {"attempt": 1, "ts": "2026-05-20T10:00:00Z", "error": "..."},
    {"attempt": 2, "ts": "2026-05-20T10:01:00Z", "error": "..."},
    {"attempt": 3, "ts": "2026-05-20T10:02:00Z", "error": "..."}
  ],
  "first_seen": "2026-05-20T10:00:00Z",
  "triage_url": "https://..."
}
```

DLQ items must alert. A DLQ no one watches is a silent failure mode (Coding Behavior Rule 12).

## Backpressure and Concurrency

LLM providers have per-minute and per-day rate limits. The trigger layer is the right place to enforce them, not the agent.

```python
from redis import Redis
r = Redis()

def acquire_provider_slot(provider: str, max_concurrent: int) -> bool:
    current = r.incr(f"slots:{provider}")
    if current > max_concurrent:
        r.decr(f"slots:{provider}")
        return False
    return True

def release_provider_slot(provider: str) -> None:
    r.decr(f"slots:{provider}")
```

If acquisition fails, requeue with exponential backoff. Do **not** burst into 429s — the cooldown periods kill throughput more than throttled-but-paced traffic.

Provider tier limits (May 2026, indicative):

| Provider | Tier | Concurrent | TPM (input) |
|---|---|---|---|
| Anthropic Tier 4 | Production | ~50–100 | 400k |
| OpenAI Tier 5 | Production | ~500 | 2M |
| AWS Bedrock | Region-dependent | Quota-managed | Region-dependent |

Always check live quotas before sizing concurrency.

## Trigger Payload Schema

Every trigger payload must conform to a versioned schema. Validate before invoking the agent. Garbage-in produces garbage-out at LLM prices.

```python
from pydantic import BaseModel, Field
from typing import Literal

class AgentTriggerV1(BaseModel):
    schema_version: Literal["v1"]
    idempotency_key: str
    source: str  # "webhook:stripe", "queue:sqs:invoices", "schedule:daily-recon"
    occurred_at: str  # ISO 8601
    payload: dict  # source-specific
    metadata: dict = Field(default_factory=dict)
    approval_required: bool = False
    cost_budget_usd: float | None = None
    max_duration_seconds: int = 300
```

Validation failures route to a separate DLQ ("malformed input") so they don't contaminate retry counts.

## Approval Gates Inside the Trigger

For high-risk actions, the trigger does not invoke the agent directly. It creates an approval task and waits.

```python
async def trigger_with_approval(event: AgentTriggerV1) -> dict:
    if event.approval_required or is_high_risk(event):
        task_id = await create_approval_task(event)
        await notify_approvers(task_id)
        return {"status": "pending_approval", "task_id": task_id}
    return await invoke_agent(event)
```

Approval flows belong here, not inside the agent, because: (1) approvers cannot review what the agent has already done; (2) the trigger layer is auditable in a way the agent's reasoning is not.

## Observability for Triggers

Per-event signals:

- `trigger.received` — source, schema_version, payload_size
- `trigger.deduplicated` — when idempotency or dedup kicked in
- `trigger.queued` — when handed to async worker
- `trigger.agent_invoked` — start of agent run
- `trigger.completed` — duration, tokens, cost, result_size
- `trigger.failed` — error class, attempt number
- `trigger.dlq` — when an item lands in DLQ

Per-source metrics:

- arrival rate
- p50 / p99 end-to-end latency (trigger receipt → agent completion)
- duplicate rate
- DLQ rate
- approval rate (for high-risk sources)

Dashboard rule: a healthy trigger system has dedup-rate < 5%, DLQ-rate < 1%, and p99 latency within SLO.

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Duplicate agent runs** | Same work done twice, double-billing | Idempotency key + dedup window |
| **Webhook timeout** | Provider retries, agent runs twice | Return 2xx fast; enqueue async |
| **Visibility timeout < agent runtime** | SQS redelivers mid-run | Set timeout = max_runtime + 20% |
| **Bursty schedule fan-out** | LLM provider 429s | Cron jitter + provider slot accounting |
| **Silent DLQ** | Failures pile up uninspected | Alert on DLQ depth > 0 |
| **Schema drift** | Trigger fields change, agent breaks | Versioned schema + reject unknown versions |
| **Missing signature verification** | Spoofed webhook drains budget | Always verify HMAC before any work |
| **Synchronous webhook → long agent** | Provider disables the webhook endpoint | Decouple via queue |

## Cross-References

- [`durable-trigger-integration.md`](durable-trigger-integration.md) — when the trigger needs Temporal/Inngest semantics
- [`claude-code-routines.md`](claude-code-routines.md) — Anthropic-hosted schedule and `/fire` specifics
- [`task-types-and-lifecycle.md`](task-types-and-lifecycle.md) — task model the trigger feeds into
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C consumes Shape A triggers
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs, oncall, runbooks
- [`../../agents-hooks/references/budget-and-loop-hooks.md`](../../agents-hooks/references/budget-and-loop-hooks.md) — enforcing budgets per trigger
- [`../../software-workflow-automation/SKILL.md`](../../software-workflow-automation/SKILL.md) — workflow substrates
- [`../../ai-mlops/references/incident-response-playbooks.md`](../../ai-mlops/references/incident-response-playbooks.md) — incident response for trigger systems
