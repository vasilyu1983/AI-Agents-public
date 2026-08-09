# Swarm Cost Discipline

## Table of Contents

- [Why Orchestration Amplifies Cost](#why-orchestration-amplifies-cost)
- [Fan-Out Cost Patterns](#fan-out-cost-patterns)
- [Session Lifecycle Cost](#session-lifecycle-cost)
- [Orchestration Config Recommendations](#orchestration-config-recommendations)
- [Decision Heuristics](#decision-heuristics)
- [Observability](#observability)
- [Cross-References](#cross-references)

Orchestration layer cost patterns. Where [../../agents-subagents/references/cost-control.md](../../agents-subagents/references/cost-control.md) focuses on individual subagent cost, this reference focuses on **fan-out patterns, session lifecycles, and long-running orchestration** — the costs that compound across many workers or across time.

## Why Orchestration Amplifies Cost

Orchestration cost scales multiplicatively, not additively:

- **Parallel fan-out**: N workers each pay full parent-context cost = N × parent size.
- **Staged waves**: later waves inherit a larger parent context (original + earlier wave outputs).
- **Long sessions**: every wave of workers sees the accumulated context of all previous waves.
- **Loops and schedules**: unattended runs keep spawning workers until stopped.

The lead thread is usually small. The swarm is where the bill lives.

## Fan-Out Cost Patterns

### Parallel Fan-Out

When dispatching N workers in one wave:

| Pattern | Cost shape | When to use |
| --- | --- | --- |
| Same context, N workers | N × parent tokens | Genuinely parallel, short tasks |
| Fresh brief per worker (no parent transcript) | N × brief tokens | Default — smallest correct mode |
| Sequential (one at a time) | 1 × parent, serial | When workers depend on each other |

**Rule:** never pass the parent transcript to a worker. Build a **self-contained brief** (goal, required context, owned files, deliverable, verification). This collapses worker input from ~150k tokens to ~5k — often 30× cheaper per spawn. See [../SKILL.md](../SKILL.md) §Fresh Context Principle.

### Staged Waves

Each wave's workers inherit the lead's context as of that moment. If wave 1 returns large outputs that the lead reads, wave 2 workers pay for wave 1's outputs too.

**Mitigations:**

- Have the lead write wave outputs to **durable files** (`docs/`, `reports/`), then pass **file paths** to wave 2 instead of content.
- Have the lead summarize wave outputs before wave 2 spawns (a one-time cost that amortizes across all wave-2 workers).
- Use `/compact` between waves if the lead context has grown past the `autoCompactWindow` threshold.

### Retry Loops (Evaluator-Optimizer)

An evaluator-optimizer pattern can retry indefinitely without a cap. Each retry = another full worker spawn + context replay.

**Mitigations:**

- **Cap retries** at 2-3. Beyond that, escalate to the lead instead of looping.
- **Pass only the evaluator's findings** to the retry worker, not the full prior attempt.
- **Prefer a planner→generator→evaluator pipeline** over unbounded self-correction loops when quality is hard to verify.

## Session Lifecycle Cost

### The 8-Hour-Session Problem

Sessions active for many hours commonly accumulate:

- Stale subagent contexts still counted in parent
- Forgotten `/loop` or scheduled triggers still spawning workers
- Tool-result noise from exploration that's no longer relevant
- Multiple task contexts interleaved with no clear boundary

**Session hygiene rules:**

1. **Task-scoped sessions** — treat `/clear` as the default task boundary, not session end. A fresh session with 5k task context is cheaper than an 8h session with 400k accumulated context.
2. **Audit automation at session start** — run `/schedule list` and check for active loops. Forgotten automation is the single largest unexplained cost source for heavy users.
3. **Review `~/.claude/plans/` periodically** — stale plan files often correspond to loops or schedules that should be stopped.
4. **Set `fastModePerSessionOptIn: true`** so fast mode doesn't silently persist across task boundaries.

### Hosted Session-Hour Cost (Claude Managed Agents)

Claude Managed Agents charges a session-hour fee on top of token rates, plus a per-search fee for web-search tool calls. Check the current Managed Agents pricing page for up-to-date figures — rates change. Implication: forgetting to end a session is the new analogue of forgetting to stop a `/loop`. Audit active sessions the same way you audit active schedules.

Implications for orchestration:

- A long-running Managed Agent workflow (e.g. 8-hour overnight research run) costs ~$0.64 in session-hours alone before any tokens or searches. Cheap individually, meaningful at fleet scale.
- Prefer explicit session-end signals in worker contracts: the worker emits `done` and the lead closes the session, rather than relying on inactivity timeouts.

### Loops and Schedules

`/loop` and `/schedule` are the highest-leverage cost surfaces because they're **unattended**. A loop set to run every 5 minutes for 24 hours = 288 spawns.

**Defensive defaults:**

- Always set an explicit end condition or max iteration count on loops.
- Prefer `ScheduleWakeup` (one-shot with explicit `delaySeconds`) over open-ended `/loop` when the task is truly one-off.
- For dynamic-pacing loops, bias toward longer `delaySeconds` (1200-1800s) to reduce cache-miss frequency; avoid the 300s anti-sweet-spot (cache miss without amortization).
- Document why a loop exists in its prompt so session handoff doesn't accidentally leave it running.

## Orchestration Config Recommendations

At the swarm layer, the relevant config surface is small but high-leverage.

### Claude Code (`~/.claude/settings.json`)

```json
{
  "autoCompactWindow": 150000,
  "showClearContextOnPlanAccept": true,
  "fastModePerSessionOptIn": true
}
```

Combined with the subagent-layer config from [../../agents-subagents/references/cost-control.md](../../agents-subagents/references/cost-control.md), this gives:

- Subagent spawns cap at Sonnet (never silently Opus).
- Lead context auto-compacts before bloat compounds across waves.
- Plan acceptance surfaces `/clear` as the cheap default task-reset.
- Fast mode is an explicit per-session choice, not a persistent state.

### Codex CLI (`~/.codex/config.toml`)

```toml
model_auto_compact_token_limit = 150000
tool_output_token_limit = 50000
plan_mode_reasoning_effort = "low"

[profiles.cheap-loop]
model = "<current-mini-model>"  # check developers.openai.com/api/docs/models
model_reasoning_effort = "low"
service_tier = "flex"
```

Codex-specific orchestration levers:

- **`model_auto_compact_token_limit`** — equivalent to Claude Code's `autoCompactWindow`. Triggers history compaction at the threshold; prevents wave-on-wave context inflation.
- **`tool_output_token_limit`** — caps individual tool outputs in history. One noisy tool output (large grep, log dump) otherwise inflates context for every subsequent worker spawn.
- **`plan_mode_reasoning_effort = "low"`** — keeps planning cheap; reserve `high` reasoning for actual execution. Plan-mode loops are a common silent cost source.
- **`service_tier = "flex"`** for unattended/background profiles — slower but cheaper than `fast`. Right default for loops and overnight runs.
- **Profiles** (`[profiles.<name>]`) — switch whole config bundles per workflow. Activate with `codex --profile cheap-loop` for known-cheap workloads (loops, batch reviews).

### Cross-platform parity

| Concern | Claude Code | Codex CLI |
| --- | --- | --- |
| Cap subagent model | `CLAUDE_CODE_SUBAGENT_MODEL` env | Per-agent `model` in `~/.codex/agents/*.toml` (no global env) |
| Auto-compact context | `autoCompactWindow` (settings.json) | `model_auto_compact_token_limit` (config.toml) |
| Cap noisy tool output | (no equivalent) | `tool_output_token_limit` |
| Reasoning depth control | (model-implicit) | `model_reasoning_effort`, `plan_mode_reasoning_effort` |
| Cost-tier service | (single tier) | `service_tier = "flex" \| "fast"` |
| Workflow-scoped config bundles | (manual `--agent` swap) | `[profiles.<name>]` blocks |

## Decision Heuristics

Use these before dispatching a wave:

| Question | If yes | If no |
| --- | --- | --- |
| Can the main thread finish in <3 tool calls? | Don't spawn | Continue |
| Is the parent context >100k? | `/compact` first, then spawn | Spawn directly |
| Is the task read-only and bounded? | Use a Haiku or Sonnet worker | Use Sonnet or inherit |
| Will N>5 workers spawn in this wave? | Consider sequential or chunked waves | Parallel OK |
| Will the loop run >1 hour unattended? | Add explicit cap and end condition | Proceed |

## Observability

Without telemetry, heavy users rely on post-hoc usage reports for cost signals. Watch for these recurring patterns in your reports:

- **"X% of usage from subagent-heavy sessions"** → subagent layer (see [cost-control.md](../../agents-subagents/references/cost-control.md))
- **"X% of usage at >Nk context"** → session hygiene (this doc, §Session Lifecycle Cost)
- **"X% of usage from Y-hour+ sessions"** → session hygiene + loops audit (this doc, §The 8-Hour-Session Problem)

Treat these signals as system feedback — they name the exact failure mode and the exact lever.

## Cross-References

- Subagent-level cost levers (model selection, env override): [../../agents-subagents/references/cost-control.md](../../agents-subagents/references/cost-control.md)
- Operational safety and stop conditions: [operational-guardrails.md](operational-guardrails.md)
- Fresh-context principle (why worker briefs beat transcripts): `agents-subagents` §Fresh Context Principle
- Platform field matrix (`model:`, `effort`, resolution order): [platform-patterns.md](platform-patterns.md)
