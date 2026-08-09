# Budget and Loop Hooks

Use this reference when you need **hook-enforced budgets** for autonomous agents, long-running loops, and 24/7 bot servers. Hooks fire in the runtime around tool calls and iterations — the right place to enforce budgets because the agent cannot opt out.

This guide applies to:

- **Shape A** triggered runs — enforce per-event cost cap
- **Shape B** always-on bots — enforce per-session and per-tenant cost caps
- **Shape C** autonomous loops — enforce per-iteration and per-run budgets (the canonical use case)

Pair with [`hook-patterns.md`](hook-patterns.md) for the runtime hook model and [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) for the loop-driver context.

## Table of Contents

- [Why Budgets Belong in Hooks](#why-budgets-belong-in-hooks)
- [Hook Lifecycle Surfaces](#hook-lifecycle-surfaces)
- [Budget Dimensions](#budget-dimensions)
- [Per-Iteration Budget Hook](#per-iteration-budget-hook)
- [Per-Run / Per-Session Budget Hook](#per-run--per-session-budget-hook)
- [Per-Tenant Budget Hook](#per-tenant-budget-hook)
- [Iteration Cap Hook](#iteration-cap-hook)
- [Stagnation Detector Hook](#stagnation-detector-hook)
- [External Kill-Switch Hook](#external-kill-switch-hook)
- [Provider Rate-Limit Hook](#provider-rate-limit-hook)
- [Escalation and Alerting](#escalation-and-alerting)
- [Hook Composition Order](#hook-composition-order)
- [Testing Budget Hooks](#testing-budget-hooks)
- [Common Failure Modes](#common-failure-modes)
- [Cross-References](#cross-references)

## Why Budgets Belong in Hooks

Three reasons:

1. **The agent cannot bypass them.** A budget check inside the agent's prompt is advisory. A hook is enforced by the runtime.
2. **They centralize the "fail loud" path.** When a budget breaches, the same hook code emits the alert, writes the halt event, and stops the agent.
3. **They survive context truncation.** As conversation context grows, instructions decay. Hook code does not decay.

Coding Behavior Rule 6 says budgets are not advisory — hooks are the mechanism.

## Hook Lifecycle Surfaces

Hook firing points vary by runtime; the universal lifecycle is:

```text
SessionStart
  └─ runtime / config preflight
PreToolUse  (every tool call)
  └─ tool input inspected; can deny
PostToolUse  (every tool call return)
  └─ tool output inspected; can transform; cumulative cost recorded
PreCompact / Compact  (context truncation)
PostIteration  (only some runtimes — Claude Agent SDK, custom loop drivers)
  └─ check budget, stagnation, kill-switch
Stop  (session ends)
  └─ final accounting
```

Claude Code surfaces `SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `UserPromptSubmit`, `PreCompact`, `Stop`, `SubagentStart`, `SubagentStop`, `TeammateIdle`, and others (see SKILL.md Event Surface table for the full list). Codex exposes notification hooks. Custom loop drivers add their own `PostIteration` surface.

If your runtime lacks `PostIteration`, build it: wrap each iteration call in a function that fires the hook explicitly.

## Budget Dimensions

Track these per agent run:

| Dimension | Unit | Where to count |
|---|---|---|
| Input tokens | count | PostToolUse + provider responses |
| Output tokens | count | PostToolUse + provider responses |
| Cost USD | money | derived from tokens × model price |
| Tool calls | count | PostToolUse |
| Iterations | count | PostIteration |
| Wall clock | seconds | SessionStart → now |
| Distinct tools used | set | PreToolUse |
| External-write tools used | count | PreToolUse with classification |

Costs (verified 2026-07-11 against `claude.com/pricing` and `platform.claude.com/docs/en/about-claude/models/overview`; OpenAI side against `developers.openai.com/api/docs/pricing` — re-verify before deploying, these move fast):

| Model | Input $/M tok | Output $/M tok |
|---|---|---|
| Claude Fable 5 (most capable widely-released model, GA 2026-06-09) | 10 | 50 |
| Claude Opus 4.8 (for complex agentic coding/enterprise work — not the top-capability model since Fable 5 shipped) | 5 | 25 |
| Claude Sonnet 5 (introductory, through 2026-08-31) | 2 | 10 |
| Claude Sonnet 5 (standard, after 2026-08-31) | 3 | 15 |
| Claude Haiku 4.5 | 1 | 5 |
| Claude Opus 4.7 (legacy, still served) | 5 | 25 |
| GPT-5.5 (OpenAI flagship-tier, replaced GPT-5 in Apr 2026) | 5 | 30 |
| GPT-5.4 Mini | 0.75 | 4.50 |

`GPT-5` / `GPT-5 Mini` were retired from OpenAI's pricing page by mid-2026 in favor of the `GPT-5.4`/`GPT-5.5` family, and a newer `GPT-5.6` family (sol/terra/luna tiers) now exists alongside them — if you see a budget config still pointed at the old names, treat it as a signal the config hasn't been touched since early 2026 and re-check the model ID against the live pricing page, not just the price.

Embed prices in a config file, not in the hook code, so updates don't need redeploys.

## Per-Iteration Budget Hook

The most common autonomous-loop guardrail. Caps cost per iteration; halts if breached.

```python
# .claude/hooks/post_iteration_budget.py
import json, sys, os
from pathlib import Path

STATE_FILE = Path(os.environ["LOOP_STATE_PATH"])
MAX_TOKENS_PER_ITER = int(os.environ.get("MAX_TOKENS_PER_ITER", "200000"))
MAX_COST_PER_ITER_USD = float(os.environ.get("MAX_COST_PER_ITER_USD", "5.0"))

def main():
    event = json.loads(sys.stdin.read())
    state = json.loads(STATE_FILE.read_text())
    iter_tokens = event["usage"]["input_tokens"] + event["usage"]["output_tokens"]
    iter_cost = compute_cost(event["usage"], event["model"])

    state["last_iter_tokens"] = iter_tokens
    state["last_iter_cost"] = iter_cost
    state["cumulative_tokens"] += iter_tokens
    state["cumulative_cost"] += iter_cost
    state["iterations"] += 1
    STATE_FILE.write_text(json.dumps(state))

    breaches = []
    if iter_tokens > MAX_TOKENS_PER_ITER:
        breaches.append(f"iter tokens {iter_tokens} > {MAX_TOKENS_PER_ITER}")
    if iter_cost > MAX_COST_PER_ITER_USD:
        breaches.append(f"iter cost ${iter_cost:.2f} > ${MAX_COST_PER_ITER_USD}")

    if breaches:
        halt(state, "per_iteration_budget", breaches)
    print(json.dumps({"continue": True, "iter_summary": state}))

def halt(state: dict, reason: str, details: list):
    event = {
        "event": "loop_halt", "reason": reason, "details": details,
        "iterations": state["iterations"], "cumulative_cost": state["cumulative_cost"],
    }
    print(json.dumps(event), file=sys.stderr)
    Path("/tmp/loop_halt.json").write_text(json.dumps(event))
    sys.exit(2)  # non-zero exit halts the loop

if __name__ == "__main__":
    main()
```

Wired in the runtime config to fire after each iteration (custom loop driver) or after `Stop` for one-shot sessions.

## Per-Run / Per-Session Budget Hook

Caps cumulative cost across all iterations of a single run (Shape C) or all turns of a single session (Shape B).

```python
MAX_RUN_COST_USD = float(os.environ.get("MAX_RUN_COST_USD", "200.0"))
MAX_RUN_TOKENS = int(os.environ.get("MAX_RUN_TOKENS", "8000000"))
MAX_RUN_WALL_HOURS = float(os.environ.get("MAX_RUN_WALL_HOURS", "12"))

def check_run_budget(state: dict) -> tuple[bool, str]:
    if state["cumulative_cost"] >= MAX_RUN_COST_USD:
        return False, f"cumulative cost ${state['cumulative_cost']:.2f} >= ${MAX_RUN_COST_USD}"
    if state["cumulative_tokens"] >= MAX_RUN_TOKENS:
        return False, f"cumulative tokens {state['cumulative_tokens']} >= {MAX_RUN_TOKENS}"
    hours = (time.time() - state["started_at"]) / 3600
    if hours >= MAX_RUN_WALL_HOURS:
        return False, f"wall hours {hours:.1f} >= {MAX_RUN_WALL_HOURS}"
    return True, ""
```

Run budget should be 10–50x per-iteration budget. If the math doesn't allow that, the loop is too tight to be safe.

## Per-Tenant Budget Hook

For multi-tenant bots (Shape B), prevent one tenant from exhausting shared provider quota or blowing the bill.

```python
import redis
r = redis.Redis()

def check_tenant_budget(tenant_id: str, iter_cost: float, daily_cap_usd: float) -> tuple[bool, str]:
    day_key = f"tenant_cost:{tenant_id}:{date.today().isoformat()}"
    new_total = r.incrbyfloat(day_key, iter_cost)
    r.expire(day_key, 86400 * 7)  # keep history a week
    if new_total >= daily_cap_usd:
        return False, f"tenant {tenant_id} daily cap ${daily_cap_usd} reached"
    return True, ""
```

When the cap is hit:

- Return a polite message to the user ("I'm at my daily allowance for your workspace — please try again tomorrow or contact support").
- Alert the tenant admin.
- Do not silently degrade — that produces angry support tickets.

## Iteration Cap Hook

```python
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "50"))

def check_iteration_cap(state: dict) -> tuple[bool, str]:
    if state["iterations"] >= MAX_ITERATIONS:
        return False, f"iteration cap {MAX_ITERATIONS} reached"
    return True, ""
```

Combine with stagnation detector below — iteration cap alone is a blunt instrument.

## Stagnation Detector Hook

Stops the loop when iterations no longer make progress toward the acceptance criterion.

```python
NO_PROGRESS_STREAK_LIMIT = int(os.environ.get("NO_PROGRESS_STREAK", "3"))

def check_stagnation(state: dict, made_progress: bool) -> tuple[bool, str]:
    if made_progress:
        state["no_progress_streak"] = 0
    else:
        state["no_progress_streak"] += 1
    if state["no_progress_streak"] >= NO_PROGRESS_STREAK_LIMIT:
        return False, f"no progress for {NO_PROGRESS_STREAK_LIMIT} iterations"
    return True, ""
```

`made_progress` is loop-specific. Define it in the PRD ("Definition of Progress") and compute outside the hook. Examples:

- Migration loop: `rows_remaining` decreased
- Test-fixing loop: `failing_tests` count decreased
- Refactor loop: file diff non-empty

## External Kill-Switch Hook

Lets an operator halt a running agent from outside without process access.

```python
import requests, os
KILL_SWITCH_URL = os.environ.get("KILL_SWITCH_URL")  # e.g., a config-store flag
KILL_SWITCH_FILE = os.environ.get("KILL_SWITCH_FILE", "/var/run/agent/KILL")

def kill_switch_active() -> bool:
    if Path(KILL_SWITCH_FILE).exists():
        return True
    if KILL_SWITCH_URL:
        try:
            r = requests.get(KILL_SWITCH_URL, timeout=2)
            return r.json().get("kill", False)
        except Exception:
            return False  # never block on transient errors
    return False
```

Check on:

- Every iteration (PostIteration)
- Every PreToolUse (catches mid-iteration kills before more spend)

The kill switch must be:

- Operator-flippable from a phone (Slack command, simple HTTP endpoint with auth)
- Tested monthly
- Logged when flipped (audit trail)

## Provider Rate-Limit Hook

Pre-check before tool call to avoid 429s consuming session.

```python
def pre_tool_use_rate_limit(event: dict) -> dict:
    provider = infer_provider(event["tool_name"])
    if not acquire_provider_slot(provider, MAX_CONCURRENT[provider]):
        # Either queue or fail fast
        return {"continue": False, "reason": "rate_limit"}
    return {"continue": True}
```

In autonomous loops, rate-limit should pause the iteration with backoff rather than halt. In always-on bots, surface a polite "I'm busy, please try again" message.

## Escalation and Alerting

Every budget breach must fire an event to a human-facing channel.

```python
def alert_breach(reason: str, state: dict):
    payload = {
        "event": "budget_breach",
        "reason": reason,
        "run_id": state.get("run_id"),
        "tenant": state.get("tenant"),
        "cumulative_cost_usd": state["cumulative_cost"],
        "iterations": state["iterations"],
        "timestamp": time.time(),
    }
    # Slack
    requests.post(SLACK_WEBHOOK, json={"text": f"🛑 Agent budget breach: {reason}", "attachments": [{"text": json.dumps(payload)}]})
    # PagerDuty for production-critical loops
    if state.get("environment") == "production":
        requests.post(PD_EVENTS_API, json={"event_action": "trigger", "payload": payload})
    # Observability backend
    log_event(payload)
```

Routing rules:

- Per-iteration breach → Slack only (informational)
- Per-run breach → Slack + ticketing system
- Stagnation halt → Slack
- Kill-switch flipped → Slack + audit log
- Per-tenant cap → Slack + email to tenant admin
- Repeated breaches (3+ in a day) → page on-call

## Hook Composition Order

When multiple hooks run on the same event, order matters.

PreToolUse order (each can deny):

1. Kill-switch check (fastest, denies immediately)
2. Provider rate-limit slot
3. Tool allow-list check (security)
4. Per-tenant budget check
5. Cost projection check (skip if predicted cost > remaining budget)

PostToolUse / PostIteration order:

1. Update cumulative counters
2. Per-iteration budget
3. Per-run budget
4. Per-tenant budget
5. Stagnation detector (only if iteration ended)
6. Iteration cap
7. Alert if any breach

Early hooks should be cheap; expensive hooks should run last (or only after a cheap pre-check passes).

## Testing Budget Hooks

Tests must include:

1. **Budget breach test** — synthetic state hitting each cap; assert the hook halts with the right reason.
2. **Restart-after-halt test** — start a run, halt at iteration 5, restart from checkpoint, verify budget state restored.
3. **Concurrent-tenant test** — two tenants hitting the same hook concurrently; verify isolation.
4. **Provider-outage test** — kill-switch URL returns 500; verify hook does not block (fail open for the kill-switch check).
5. **Alert delivery test** — mock Slack/PagerDuty; verify payload shape.

Run these tests in CI on every change to the hook code.

## Common Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Budget check inside prompt** | Agent ignores and keeps spending | Move to hook |
| **Hook does not halt on breach** | Loop continues despite alert | Exit code 2 + sys.exit() |
| **Cumulative counter not persisted** | Restart resets budget | Atomic write to state file |
| **Kill-switch silent** | Operator flip has no effect | Test monthly; integration test in CI |
| **Alert spam** | Slack drowns operators | Dedupe by reason within 5-min window |
| **Wrong provider price** | Cost numbers off by 5x | Config file with version + change log |
| **Tenant counter race** | Two iterations both pass cap check | Atomic INCRBY in Redis |
| **Halt with exit 0** | Pipeline thinks run succeeded | Use exit code 2 for budget halts |
| **Stagnation false positive** | Halts despite real progress | Tune progress definition; require N consecutive misses |

## Cross-References

- [`hook-patterns.md`](hook-patterns.md) — base hook model
- [`hook-security.md`](hook-security.md) — securing hook scripts
- [`hook-templates.md`](hook-templates.md) — copy-paste hook starters
- [`runtime-preflight-hooks.md`](runtime-preflight-hooks.md) — SessionStart preflight checks
- [`../../ai-agents/references/autonomous-loop-patterns.md`](../../ai-agents/references/autonomous-loop-patterns.md) — Shape C loop context
- [`../../ai-agents/references/guardrails-implementation.md`](../../ai-agents/references/guardrails-implementation.md) — input/output guardrails
- [`../../ai-agents/references/24-7-operating-model.md`](../../ai-agents/references/24-7-operating-model.md) — SLOs and oncall
- [`../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md`](../../ai-coding-agents-tasks/references/webhook-and-queue-triggers.md) — per-event budgets
- [`../../ai-mlops/references/cost-management-finops.md`](../../ai-mlops/references/cost-management-finops.md) — broader cost governance
