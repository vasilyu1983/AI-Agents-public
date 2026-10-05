# Stateful Rollout and Blue-Green Deployment

Use this reference for **Shape B — Always-on bot server** when you need to deploy a new bot version without dropping in-flight conversations, leaking budget, or corrupting state.

Stateful bots cannot use the same rollout playbook as stateless web services. A user mid-conversation has expectations the new version may not match. Checkpoints written by v1 may not be readable by v2. Schemas drift. Tool contracts change. May 2026 baseline: bot rollouts are cohort-based, not percentage-based, and assume checkpoint migration is a first-class concern.

Pair with [`production-deployment.md`](production-deployment.md) for the serving stack and [`state-checkpoints-and-hitl.md`](state-checkpoints-and-hitl.md) for the checkpoint model itself.

## Table of Contents

- [Why Stateful Rollouts Are Different](#why-stateful-rollouts-are-different)
- [Rollout Models Compared](#rollout-models-compared)
- [Session Cohorts, Not Traffic Percentages](#session-cohorts-not-traffic-percentages)
- [Checkpoint Schema Migration](#checkpoint-schema-migration)
- [Graceful Drain](#graceful-drain)
- [Blue-Green for Bots](#blue-green-for-bots)
- [Canary by Cohort](#canary-by-cohort)
- [Tool Contract Changes](#tool-contract-changes)
- [Prompt Changes Without Drift](#prompt-changes-without-drift)
- [Rollback Strategy](#rollback-strategy)
- [Pre-Rollout Checklist](#pre-rollout-checklist)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## Why Stateful Rollouts Are Different

A bot session has memory: prior turns, slot values, escalation flags, partial workflows. A naive rolling deploy will:

- Drop sessions mid-conversation when a pod terminates.
- Route turn N+1 to a new pod that cannot deserialize state from turn N.
- Apply a new system prompt mid-conversation, producing jarring tone or behavior shifts.
- Break tool calls in flight if a tool schema changed.
- Lose the LangGraph checkpoint if the new graph topology removed a node.

The general principle: **a session, once started on version X, should finish on version X unless explicitly migrated**.

## Rollout Models Compared

| Model | Stateful-bot fit | Notes |
|---|---|---|
| **Rolling update (k8s default)** | Poor | Terminates pods holding active sessions |
| **Blue-green (full swap)** | Good | Both versions run; cut over after drain |
| **Cohort canary** | Best | New sessions go to v2; existing sessions finish on v1 |
| **Percentage canary (traffic split)** | Poor | A user can be routed across versions across turns |
| **Shadow** | Useful for evals | Run v2 in parallel without serving its responses |

The default for production bots: **cohort canary**, with blue-green as the underlying infra.

## Session Cohorts, Not Traffic Percentages

Tag every session with the version that started it. The load balancer routes by tag, not by percentage.

```python
class SessionRouter:
    def route(self, session_id: str, message: dict) -> str:
        state = redis.get(f"session:{session_id}")
        if state:
            return json.loads(state)["bot_version"]  # sticky to version
        # New session: assign by cohort policy
        return self.choose_version_for_new_session(message)

    def choose_version_for_new_session(self, message: dict) -> str:
        # 10% of new sessions go to v2; rest go to v1
        if hash(message.get("user_id", "")) % 100 < 10:
            return "v2"
        return "v1"
```

Why this matters:

- A user mid-conversation never sees a version change.
- The cohort ramp (1% → 5% → 25% → 100%) is by *new sessions*, so existing sessions are never disrupted.
- Rollback only affects new sessions; in-flight sessions on the bad version finish naturally or are explicitly drained.

## Checkpoint Schema Migration

Every checkpoint write should include a schema version. Every read should handle older versions or fail loudly.

```python
class CheckpointV2(BaseModel):
    schema_version: Literal["v2"]
    session_id: str
    turns: list[Turn]
    slots: dict
    escalation_flags: list[str]
    bot_version: str
    created_at: str
    last_updated: str

def load_checkpoint(session_id: str) -> CheckpointV2:
    raw = redis.get(f"checkpoint:{session_id}")
    if raw is None:
        return None
    data = json.loads(raw)
    sv = data.get("schema_version", "v1")
    if sv == "v2":
        return CheckpointV2(**data)
    if sv == "v1":
        return migrate_v1_to_v2(data)
    raise UnknownCheckpointSchema(sv)
```

Migration rules:

1. **Never destructively migrate.** Write v2 as a copy; keep v1 until drain.
2. **Migrate on read, not on deploy.** A bulk migration that touches all keys during deploy is the highest-risk path.
3. **Forward-only migrations.** If you cannot migrate v1 → v2, the v1 sessions stay on v1 until they expire.
4. **TTL the old format.** Once all active v1 sessions complete (typically 1–7 days), the v1 reader can be removed.

LangGraph specifics:

- Use `langgraph.checkpoint.postgres.PostgresSaver` for production; SQLite is fine for dev only.
- LangGraph checkpoints include the graph topology (node names). Renaming a node breaks resumption — add a node migration step or version your graph names.

## Graceful Drain

When draining a v1 pod:

```python
class GracefulShutdown:
    def __init__(self, drain_timeout_seconds: int = 600):
        self.draining = False
        self.active_sessions: set[str] = set()
        self.drain_timeout = drain_timeout_seconds

    def session_started(self, sid: str):
        if self.draining:
            raise PodDraining("Reject new sessions")
        self.active_sessions.add(sid)

    def session_ended(self, sid: str):
        self.active_sessions.discard(sid)

    async def begin_drain(self):
        self.draining = True
        start = time.time()
        while self.active_sessions and time.time() - start < self.drain_timeout:
            await asyncio.sleep(5)
        if self.active_sessions:
            # Force checkpoint and let other pods pick up
            for sid in self.active_sessions:
                await force_persist_checkpoint(sid)
```

Wire to k8s `preStop` hook. Set `terminationGracePeriodSeconds` to `drain_timeout + 60`.

```yaml
lifecycle:
  preStop:
    exec:
      command: ["python", "-m", "bot.drain"]
terminationGracePeriodSeconds: 660
```

If a session cannot finish in the drain window, the bot must explicitly tell the user ("Hold on — I'm reconnecting") and resume from checkpoint on another pod. This is a worse outcome than a clean finish but better than silent state loss.

## Blue-Green for Bots

Two full deployments (blue and green) run concurrently. The load balancer routes by session affinity, not by deployment.

```text
                      ┌──────────────────────────┐
                      │   Load Balancer          │
                      │   routes by session tag  │
                      └────────────┬─────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                                     │
        ┌───────▼──────────┐               ┌──────────▼─────────┐
        │  Blue (v1)       │               │  Green (v2)        │
        │  serves existing │               │  serves new        │
        │  sessions until  │               │  sessions only     │
        │  drain           │               │  during canary     │
        └──────────────────┘               └────────────────────┘
                │                                     │
                └──────────────┬──────────────────────┘
                               ▼
                ┌──────────────────────────────┐
                │  Shared state (Redis,        │
                │  Postgres, vector store)     │
                │  with versioned checkpoints  │
                └──────────────────────────────┘
```

Lifecycle:

1. Green is deployed alongside blue at 0% new-session traffic.
2. Smoke tests run against green.
3. Cohort ramp: 1% → 5% → 25% → 100% of *new* sessions to green.
4. Blue continues serving existing sessions until they all finish or drain timeout.
5. Blue is shut down.

Critical: shared state (Redis, DB) must be backward-compatible across both versions during the rollout. Forward-incompatible schema changes need a separate migration step before rollout.

## Canary by Cohort

Choose cohorts by *who is least affected by a bad rollout*:

| Cohort | Risk | Use For |
|---|---|---|
| Internal employees | Lowest | Day-1 smoke test |
| Beta opt-in users | Low | Feature validation |
| Specific tenant / org | Medium | B2B rollout |
| Geography | Medium-high | Geo-specific changes |
| 1% random users | Higher | Final pre-100% gate |

Always include at least one internal-only cohort step. Always allow tenants to opt out of canary (paying customers do not want to be unwilling testers).

```python
def assign_cohort(user_id: str, tenant_id: str) -> str:
    if is_employee(user_id):
        return "v2"  # internal always on latest
    if tenant_id in CANARY_TENANTS:
        return "v2"
    if hash(user_id) % 100 < canary_percentage():
        return "v2"
    return "v1"
```

`canary_percentage()` reads from a config store (LaunchDarkly, ConfigCat, Redis) so you can change the ramp without redeploying.

## Tool Contract Changes

If v2 changes a tool's signature, in-flight v1 sessions calling the old tool will break.

Options, in preference order:

1. **Additive only**: add new fields, never remove. New v1 calls ignore new fields. Best path.
2. **Versioned tool names**: keep `search_v1` and `search_v2` both available; v1 bot calls v1, v2 bot calls v2.
3. **Adapter layer**: tool gateway translates v1 calls into v2 backend automatically.
4. **Forbidden during canary**: schedule the breaking tool change between rollouts, not during.

Document tool versions in the bot prompt so the LLM emits the right shape:

```text
Available tools:
- search_v2(query: str, filters: dict, top_k: int = 5) → list[Result]
  (replaces search_v1 — same semantics, stricter filter validation)
```

## Prompt Changes Without Drift

A new system prompt mid-conversation jolts the bot's behavior. Treat the prompt as part of the session state.

```python
class SessionState:
    prompt_version: str
    prompt_text: str  # frozen at session start

def start_session(user_id: str) -> SessionState:
    return SessionState(
        prompt_version=current_prompt_version(),
        prompt_text=load_prompt(current_prompt_version()),
    )

def resume_session(session_id: str) -> SessionState:
    state = load_state(session_id)
    # Even if v2 is the current version, this session keeps v1's prompt
    return state
```

Session-pinned prompts mean the bot's tone, capabilities, and guardrails are stable across the lifetime of a conversation. Pair with cohort routing — both versions run, each with their own prompt.

When a prompt change must propagate immediately (legal, safety), use a **safety overlay**: an additional layer on top of the pinned prompt that injects the new constraint. Overlays are versionless and apply to every session in real time.

## Rollback Strategy

Rollback contract:

1. Stop routing new sessions to v2 (set canary_percentage to 0).
2. Allow in-flight v2 sessions to finish.
3. Investigate.
4. Patch and re-canary, or remove v2 deployment.

Do **not** force-migrate v2 sessions back to v1 unless v2 is actively harmful. Forcing migration risks worse state corruption than letting them finish.

Rollback signals to watch:

- error rate on v2 > 2x v1 baseline
- latency p99 on v2 > 1.5x v1
- escalation rate on v2 > 1.5x v1
- user-reported bug rate spike
- safety filter trips on v2 > v1

Automate at least one of these as a kill-switch that flips canary_percentage to 0.

## Pre-Rollout Checklist

- [ ] Checkpoint schema is backward-compatible OR migration path tested
- [ ] Tool changes are additive OR versioned tool names in place
- [ ] Prompt changes are session-pinned (no mid-conversation swap)
- [ ] Cohort routing implemented and tested with a fake-user load test
- [ ] Drain handler verified — kill a pod with active sessions and confirm clean shutdown
- [ ] Canary ramp documented (e.g., 1% → 5% → 25% → 50% → 100% over 24h)
- [ ] Kill-switch wired (config-store flag flips canary_percentage to 0)
- [ ] Rollback rehearsed within the last 30 days
- [ ] Eval suite passes on v2 with no regressions
- [ ] Observability dashboard split by bot version
- [ ] Alerts split by bot version (v2 spikes paged separately)
- [ ] On-call briefed on the change

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Mid-conversation version jump** | User sees tone/behavior change | Session-pinned version |
| **Checkpoint deserialization error** | New pod cannot resume old session | Schema versioning + migrate-on-read |
| **Forced rolling deploy drops sessions** | Active sessions vanish | Cohort routing + drain handler |
| **Tool schema break** | LLM emits invalid tool call | Additive-only or versioned tools |
| **Prompt change mid-session** | Inconsistent behavior across turns | Pin prompt at session start |
| **Shared state schema drift** | One version corrupts the other's reads | Pre-rollout migration; both versions tested against the new schema |
| **Silent kill-switch** | Bad v2 keeps serving | Automated rollback signals |
| **Drain timeout too short** | Sessions truncated | Set drain timeout to p99 session length |

## Cross-References

- [`production-deployment.md`](production-deployment.md) — base serving stack
- [`state-checkpoints-and-hitl.md`](state-checkpoints-and-hitl.md) — checkpoint model
- [`graph-design-patterns.md`](graph-design-patterns.md) — LangGraph topology
- [`secret-rotation-and-model-fallback.md`](secret-rotation-and-model-fallback.md) — provider failover during rollout
- [`testing-and-production.md`](testing-and-production.md) — eval gates before rollout
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../ai-agents/references/deployment-ci-cd-and-safety.md`](../../ai-agents/references/deployment-ci-cd-and-safety.md) — general release patterns
- [`../../ai-mlops/references/deployment-patterns.md`](../../ai-mlops/references/deployment-patterns.md) — model deployment patterns
