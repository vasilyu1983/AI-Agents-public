---
description: Subagent model and effort selection, CLAUDE_CODE_SUBAGENT_MODEL, per-role tier matrix, and cost levers for Claude Code and Codex fan-out.
last_verified: 2026-09-24
status: stable
---

# Subagent Cost Control

## Table of Contents

- [Lookups Before Assigning Tiers](#lookups-before-assigning-tiers)
- [Why Subagent Cost Varies](#why-subagent-cost-varies)
- [Dynamic Workflow Cost Controls](#dynamic-workflow-cost-controls)
- [The Three Signals and Their Levers](#the-three-signals-and-their-levers)
- [Model-Family Cost Levers](#model-family-cost-levers)
- [Prompt Cache Levers for Multi-Agent Runs](#prompt-cache-levers-for-multi-agent-runs)
- [Recommended Global Configuration](#recommended-global-configuration)
- [Codex Equivalents](#codex-equivalents)
- [Cost Anti-Patterns](#cost-anti-patterns)
- [Cross-References](#cross-references)

## Lookups Before Assigning Tiers

This file holds the levers and the decision rules, not the model lineup or prices, which change with every release.

- **Operator policy.** The repository's tier policy (which model and effort each tier uses on Claude Code and Codex, and the allowlisted global subagent override) lives in [data/model-policy.json](../data/model-policy.json). The installers and `scripts/validate_catalog_integrity.py` read it; do not restate it in prose.
- **Current models and rates.** Before assigning or changing a tier, read the provider's models overview and pricing page (Claude: platform.claude.com models overview and pricing; OpenAI: the models guide and API pricing page). This skill keeps no price table; the rates on those pages feed the tier decision directly.
- **The decision it feeds.** Pick the cheapest model-and-effort pair that holds quality for the role on your own evals, measured as cost per accepted result, not per-token price.

## Why Subagent Cost Varies

Subagent startup is runtime- and mode-specific. A named Claude Code subagent starts with fresh conversation history plus runtime-selected instructions, memory, skills, tools, and a delegation message; a documented conversation fork inherits parent history and shares its first-request prompt-cache prefix. Codex and other runtimes have their own context-fork settings. Therefore:

- Parent context size is a cost input only when the chosen mode actually inherits or re-encodes it.
- A shared cache prefix can reduce billed input, but does not establish lower total task cost after cache writes or misses, output, tools, retries, and coordination.
- Model and effort choices affect both rates and token consumption, so per-token price alone cannot rank cost per completed task.

Record the context-start mode, model, effort, returned usage categories, tool fees, retries, and outcome for each spawn. Optimize cost per accepted result, not a universal "spawn multiplier."

## Dynamic Workflow Cost Controls

Repeatable fan-out routed to a saved [dynamic workflow](https://code.claude.com/docs/en/workflows) has its own sizing surface. The `workflowSizeGuideline` setting tells Claude how many agents to aim for; it is advice, not a cap. Above it sit an advisory `Large workflow` warning and runtime caps on concurrency, items per `parallel()`/`pipeline()` call, and agents per run. Read the current tier counts, warning thresholds, and caps in the workflows docs before sizing a large fan-out, and size to the smallest tier that covers it. Detail and the resume/rerun cost behavior live in [workflow-runtime.md](workflow-runtime.md).

## The Three Signals and Their Levers

Heavy users of Claude Code and Codex see three recurring cost signals in usage reports. Each maps to a configuration lever in the subagent layer.

### Signal 1 — "X% of usage came from subagent-heavy sessions"

**Mechanism:** Each Agent call creates another model execution, but its input depends on the runtime and startup mode. Named and forked subagents do not have the same conversation or cache behavior.

**Model resolution order is a lookup.** The order between a definition's `model:` frontmatter, the per-invocation model, and the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable has changed between releases. Read it in the [sub-agents docs](https://code.claude.com/docs/en/sub-agents#choose-a-model) for the running version before predicting which model a member runs on. Two consequences to check every time:

- If the environment variable ranks below frontmatter, a global override does not reach members that declare `model:`; it only sets a floor for definition-less subagents (plugin agents, `--agents` specs).
- A `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` switch, where the running version supports it, overrides every per-role tier at once and turns the tier matrix into a flat bill. Do not set it without a deliberate decision. The docs also note that the environment variable alone may not change the built-in Explore and Plan subagents' model.

Without frontmatter or an override, subagents inherit the parent session's model — often the most expensive outcome.

**Levers (apply all three):**

**1. Per-agent frontmatter** — pin each agent's tier with a runtime alias in its `.md` file:

```yaml
---
name: dev-feature-researcher
model: sonnet  # or haiku for read-only/verifier roles
---
```

**2. Global env override** — sets a floor for built-in subagents, plugin agents without frontmatter, and session-scoped `--agents` specs. Use the value allowlisted in [data/model-policy.json](../data/model-policy.json):

```json
"env": {
  "CLAUDE_CODE_SUBAGENT_MODEL": "<standard-tier-model>"
}
```

Do not describe the override as giving uniform quality across the fleet unless the force switch is set; count how many members declare `model:` before making that claim.

**3. Behavioral gate** — before every Agent call, ask: "Could the main thread finish this in fewer than 3 tool calls?" If yes, don't spawn. The skill's §Scenario Selection Rule names this as the first line of defense. If a model generation delegates more readily on its own, the parent's restraint is what keeps spawn count honest.

**Role-to-tier matrix for frontmatter.** Tiers map to models through [data/model-policy.json](../data/model-policy.json):

| Role | Tier | Rationale |
| --- | --- | --- |
| Reviewers, researchers, verifiers, doc auditors | mechanical, or critical at low effort where review quality is load-bearing | Read-only, bounded output |
| Bulk mechanical fan-out (renames, char-cap checks, format conversions, placeholder sweeps) | mechanical | Low reasoning need; scales to wide parallel batches |
| Implementers, architects, debaters | standard | Need reasoning depth |
| Synthesizers with high-stakes decisions | critical, or inherit | Final-answer quality matters |

Checks for the mechanical tier:

- **Effort support.** Read the model-config effort table: a model it does not list does not support effort, so an `effort:` field on a member pinned to it is inert and the saving comes from the model choice alone.
- **Retirement date.** Read the model's deprecation or retirement date on the models overview. When one is announced, name a fallback tier for every member pinned to it before the date.

Where review quality is load-bearing, compare a strong model at `low`/`medium` effort against a cheaper model at high effort on your own review set; the stronger model at lower effort often wins on accepted findings per token.

### Signal 2 — "X% of usage was at >150k context"

**Mechanism:** Long sessions with many tool results bloat context. Each subagent spawn that inherits the parent context inherits that bloat. Cached tokens are cheaper but still paid; uncached portions (most new work) are full price.

**Levers:**

**1. `autoCompactWindow`** in `~/.claude/settings.json` — triggers auto-compaction as context approaches the threshold. It can also be set with `/autocompact <value>`, the `--autocompact` launch flag, or `CLAUDE_CODE_AUTO_COMPACT_WINDOW`; `/autocompact auto` returns to the window tuned for the active model. Claude Code caps the window at the model's own context window, so a value above it has no effect. Read the accepted range and precedence in the [model-config docs](https://code.claude.com/docs/en/model-config#set-the-auto-compact-window).

```json
"autoCompactWindow": <value below the active model's context window; read the accepted range in the model-config docs>
```

**Threshold strategy** (read the active model's context window first):

- Small window: leave it unset, or set it somewhat below the ceiling so compaction happens while deep in a task.
- Large window, quality-first daily driver: roughly a third of the window — compact before attention degrades, not at the hard limit.
- Large window, bulk or research workloads: most of the window — fewer compactions, at the cost of degraded reasoning on long threads.
- Aggressive cost minimization: the lowest accepted value — cheap, but loses mid-task nuance.

Why a large window still warrants a threshold well below it:

- Each auto-compaction is a full-context read plus a summary write, so one compaction at a smaller context costs less than one at a larger context.
- Long-context quality is a real constraint even where the window allows more. Treat the threshold as a cost heuristic first and a quality heuristic second, and raise it if your evals hold.
- Check the pricing page for a long-context premium. Where there is none, compact as low as the task tolerates; where there is one, the premium is a further reason to compact early.

Auto-compaction can be disabled outright with the boolean setting `autoCompactEnabled: false`, and the `DISABLE_COMPACT` environment variable disables all compaction. Setting the window to the model's context ceiling is an obsolete workaround.

**2. `/clear` on task switch** — removes prior conversation from the new task's active context, while `/compact` preserves a summary for continuation. Use `/clear` for a genuinely new task and `/compact` when the current task must continue; compare usage rather than describing either operation itself as free.

**3. `showClearContextOnPlanAccept: true`** — offers `/clear` when accepting a plan, making the cheap option the easy option.

### Signal 3 — "X% of usage came from sessions active for 8+ hours"

**Mechanism:** Long-running sessions accumulate context, keep subagents warm, and often hide forgotten automation (`/loop`, `/schedule`, `ralph-loop`).

**Levers:**

1. **Audit active automation** at session start:
   - `/schedule list` — surfaces scheduled remote agents.
   - `/loop` (no args, then cancel) — shows active loop sessions.
   - Check `~/.claude/plans/` for stale plan files referenced by loops.
2. **Intentional session boundaries** — treat sessions as task-scoped, not day-scoped. `/clear` or a new session often reduces unrelated input for a new task, but the saving depends on the runtime's retained state, cache behavior, and the context that must be rebuilt.
3. **`fastModePerSessionOptIn: true`** — forces fast-mode opt-in per session so it doesn't silently persist across task switches. Fast mode bills at a premium rate, and the docs state that the first time you enable it in a conversation you pay the fast-mode uncached input price for the entire conversation context, so the deeper the conversation, the more it costs. The guardrail stops a persisted preference from re-paying that charge in every new session. Read the current rates and supported models in the [fast-mode docs](https://code.claude.com/docs/en/fast-mode).

## Model-Family Cost Levers

Cost dynamics that shift with each model generation. Each item names what to look up and the decision it feeds.

### Effort

- **Default effort is per model.** Read the default for each model you run in the [model-config docs](https://code.claude.com/docs/en/model-config#adjust-effort-level). Subagents inherit the session effort unless overridden; frontmatter effort overrides the session level but not the `CLAUDE_CODE_EFFORT_LEVEL` environment variable.
- **Session effort resolves through a chain** — an explicit choice (`CLAUDE_CODE_EFFORT_LEVEL`, `--effort`, or `/effort`), possibly a per-model sticky hold on some models, then your settings, then the model default. Read the current chain in the docs before predicting a member's effort; a prediction that skips a sticky hold mispredicts on the models that have one.
- **Treat the default as a starting point in both directions.** Step down where quality holds to save tokens and latency; step up for the most demanding work. Per role:
  - **Readers, explorers, verifiers, doc auditors** → `low` or `medium`
  - **Implementers, architects** → the default, or step down if evals hold
  - **Synthesizers, adversarial reviewers** → `xhigh` or `max`
- At `xhigh` or `max`, give `max_tokens` generous headroom: thinking counts against `max_tokens`. Check the docs for the recommended minimum.
- Some models reject disabling thinking at higher effort levels, and some do not allow disabling it at all. Check the model's docs before pairing a thinking setting with an effort level.

### Task budgets

An advisory per-loop token ceiling set in `output_config` (`task_budget: {type: "tokens", total: N}`). The model sees a server-injected running countdown and paces itself; `max_tokens` remains the enforced ceiling. Read [Task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) for the beta header, minimum, supported models, and which surfaces expose it before designing on it.

- **Cache footgun:** the countdown marker is injected server-side per turn. If you decrement `task_budget.remaining` on each follow-up, the changed value invalidates any cache prefix containing it. Set the budget **once** and let the model self-regulate. Pass `remaining` only when your loop compacts or rewrites context, since the server cannot then track spend across the rewrite.
- **Sizing footgun:** a budget clearly too small for the task can read as refusal — the model may decline, aggressively scope down, or stop early rather than start work it cannot finish. Size against your measured p99 per-task spend, not a fixed default.

### Tokenizer changes

Tokenizers can change between model generations, so the same text can produce a different token count. When you move to a new generation, recount `autoCompactWindow`, `max_tokens`, and instruction-file budgets that were calibrated on the old one (the models overview states the words-per-token ratio).

### Agent-team token multiplier

The Claude Code [costs docs](https://code.claude.com/docs/en/costs#manage-agent-team-costs) report that agent teams use several times more tokens than a standard session, and more again when teammates run in plan mode, because each teammate keeps its own context window and runs as a separate instance. Parallel fan-out is not free: N parallel subagents cost roughly N sessions, plus coordination. Follow the docs' guidance: a cheaper model for teammates, small teams, focused spawn prompts, and shutting teammates down when their work is done.

### MCP server overhead per spawn

MCP context overhead varies with server count, schema size, transport, deferred-loading support, and which tools are invoked. Current Claude Code can defer eligible tool schemas, but remote-server behavior has had gaps; do not apply a fixed tokens-per-server multiplier. Scope `mcp_servers` per agent, run `/context` or inspect usage to measure what entered context, and compare a CLI alternative only when it provides the same capability and permission boundary ([costs](https://code.claude.com/docs/en/costs#reduce-mcp-server-overhead)).

**Quality cost, not just token cost.** Field reports (StackOne, Atlassian) describe tool-selection accuracy falling sharply as tool counts grow, and tool descriptions taking a large share of the context window in MCP-heavy parents. The fix is the same — scope per worker — but the impact is degraded model behavior, not just a higher bill.

**MCP-wrapper subagent pattern (Cra.mr, 2026).** When one MCP server bloats every parent turn, wrap it inside a dedicated subagent. The parent calls the subagent with a task; the subagent owns the MCP and its tool descriptions; the parent never sees the descriptions. This converts MCP overhead from "every turn" to "once per delegated task." See [harness-patterns.md](harness-patterns.md) §"MCP-Wrapper Subagent".

### Hooks as result shapers (underused lever)

A Claude Code `PostToolUse` hook can return `updatedToolOutput` to replace test or log output before the next model request. The replacement must match the tool's output schema; retain the complete original result in an artifact or telemetry outside model context, and test malformed replacements because Claude Code can ignore an invalid shape and keep the original. Measure tokens before and after on the target command and record what evidence was removed. `PreToolUse` sees input rather than returned content; use it for this purpose only when it rewrites `updatedInput` to a vetted wrapper, and account for the wrapper's permission and execution-boundary implications.

### Runaway-session guardrail

Anecdotal practitioner reports (secondary, unverified blog posts; no primary figures) describe large unexpected bills from parallel subagents left running for hours or unattended over days. Treat the magnitude as unmeasured; the mechanism (no automatic stop on a runaway fan-out) is what matters. Mitigations:

- Set `maxTurns` on every subagent (20 is a reasonable starting point for bounded tasks)
- Avoid unattended `/loop` or `/schedule` wrappers around parallel teams on the most expensive tier
- Audit `/schedule list` and active loops at session start (see Signal 3 above)
- Use the enforced levers where the runtime has them (concurrency caps, budget caps) rather than prompt discipline alone

## Prompt Cache Levers for Multi-Agent Runs

Three cache levers govern fan-out spend, and none of them is the main conversation's cache. Read the current values and version gates in the [agent-teams](https://code.claude.com/docs/en/agent-teams#token-usage), sub-agents, and workflows docs.

- **`subagentPromptCacheTtl`** — in-process teammates and workflow agents fall outside the main conversation's cache TTL bucket, so their cache lasts only the short default lifetime. Set it to `1h` to keep it longer. Longer-lived cache writes are billed at a higher rate (check the pricing page), so `1h` pays off only when the prefix is read enough times: right for a long fan-out, wrong for a handful of short spawns.
- **`experimental.cacheTtl`** — the per-agent frontmatter equivalent, written inside the `experimental` map in subagent files only. Check the accepted values, when a `1h` value is ignored, and the minimum version in the sub-agents docs.
- **`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`** — governs whether a fan-out shares one cached prefix or pays for it N times. When a fan-out starts several matching agents at once, Claude Code holds all but the first until the first agent's response begins, then releases the rest so their first requests read the shared prefix. The variable caps the hold; `0` disables it. Two agents share a prefix only when they match on model, effort level, agent type, tools, output schema, and working directory, so a fan-out of heterogeneous roles gets no sharing at all — a reason to keep a wide batch homogeneous.

```json
{
  "subagentPromptCacheTtl": "1h"
}
```

## Recommended Global Configuration

Pick the baseline that matches the context window of the main-thread model you actually use; take the model value from [data/model-policy.json](../data/model-policy.json).

```json
{
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "<standard-tier-model>"
  },
  "autoCompactWindow": "<look up: model-config docs, below the active model's context window>",
  "showClearContextOnPlanAccept": true,
  "fastModePerSessionOptIn": true
}
```

Lower `autoCompactWindow` below the ceiling for a small-window main thread (see Signal 2). The baseline sets a floor for definition-less subagents (leaving the main thread on whatever model you prefer), triggers compaction before context bloat compounds across spawns, makes the cheap context-reset action visible at plan time, and prevents fast mode from silently persisting across sessions. Add `"subagentPromptCacheTtl": "1h"` if you run long teammate or workflow fan-outs.

Whether the env value reaches installed members depends on the resolution order (Signal 1): where frontmatter wins, the per-role tier matrix is what members actually run.

## Codex Equivalents

Codex uses agent `.toml` files in `~/.codex/agents/` (personal) or `.codex/agents/` (project-scoped). Each file defines one custom agent. Codex exposes more granular subagent cost control than Claude Code because both `model` and `model_reasoning_effort` can be pinned per agent.

### Inheritance rule

Optional fields — `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config` — are resolved per spawn in this order:

1. Explicit value in the agent `.toml`
2. The corresponding `[agents]` default in `config.toml`
3. The parent session's value

Set the fleet-wide tier once in `config.toml` rather than in every agent file, using the standard tier from [data/model-policy.json](../data/model-policy.json):

```toml
[agents]
default_subagent_model = "<standard-tier-model>"
default_subagent_reasoning_effort = "<standard-tier-effort>"
max_concurrent_threads_per_session = <cap>
```

Then omit `model` and `model_reasoning_effort` from the agent files. One line changes on a model release instead of every member. Pin in an individual file only when a role genuinely needs a different tier — and record it in `MODEL_PIN_EXEMPT` in `scripts/validate_catalog_integrity.py`, which fails the build on undeclared pins.

Only if **neither** the agent file nor `[agents]` sets a value does the subagent fall through to the lead session's (often expensive) settings.

### Per-agent model pinning

```toml
# ~/.codex/agents/reviewer.toml — critical judgment role
name = "reviewer"
model = "<critical-tier-model>"
model_reasoning_effort = "<critical-tier-effort>"

# ~/.codex/agents/implementer.toml — standard execution role
name = "implementer"
# Omit model and effort: inherit the [agents] defaults.

# ~/.codex/agents/explorer.toml — bounded mechanical scan
name = "explorer"
model = "<mechanical-tier-model>"
model_reasoning_effort = "<mechanical-tier-effort>"
```

The repository's Codex tier policy (critical, standard, mechanical, and the general fallback) is read from [data/model-policy.json](../data/model-policy.json); `scripts/deploy-preset.sh` materializes it into installed TOMLs. It is a local operator policy, not a provider mandate or a benchmark-proven optimum. Before changing it, read the [OpenAI models guide](https://learn.chatgpt.com/docs/models) and [API pricing page](https://developers.openai.com/api/docs/pricing) for current models and rates, then validate task outcomes, rework, latency, and usage on your own runs. Model and effort must be evaluated together: a lower per-token rate does not prove that a high-effort run costs less overall, and read-only status alone does not make a role mechanical.

### Codex-specific cost levers (no Claude Code equivalent)

| Field | Effect |
| --- | --- |
| `model_reasoning_effort` | Controls reasoning depth; supported values depend on model and client. |
| `plan_mode_reasoning_effort` | Overrides planning effort independently. Choose it for the planning task rather than lowering it automatically. |
| `model_verbosity` (`low` \| `medium` \| `high`) | Output verbosity. Lower = fewer output tokens. |
| `model_auto_compact_token_limit` | Codex's equivalent of Claude Code's `autoCompactWindow`. Triggers history compaction at the named token threshold. Keep it below the model's context window, and do not treat a threshold as proof that a request of that size is supported. |
| `tool_output_token_limit` | Caps individual tool outputs stored in history. Prevents one noisy tool from inflating context for every subsequent turn. |
| `service_tier` (string) | Preferred service tier for new turns. The tier list is model-dependent; write only a tier the active model advertises, or it is rejected or silently ignored. |

The [subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents) and the [config reference](https://learn.chatgpt.com/docs/config-file/config-reference) can enumerate different effort values. Do not infer blanket rejection from one table; verify the installed client and selected model. Higher effort can increase latency and token use.

Operator-specific `~/.codex/config.toml` values (main-agent model, compaction threshold, concurrency cap) are local configuration, not skill guidance. Merge `[agents]` entries into existing tables rather than duplicating them, and align role files in `~/.codex/agents/*.toml` with the policy file.

### Profiles for situational cost control

Codex layers separate `$CODEX_HOME/<name>.config.toml` files over the base config with `--profile <name>` (check `codex --help` for the running version). Use separate files for deep review and quick fixes:

```toml
# ~/.codex/deep-review.config.toml
model = "<critical-tier-model>"
model_reasoning_effort = "<critical-tier-effort>"
```

```toml
# ~/.codex/cheap-loop.config.toml
model = "<mechanical-tier-model>"
model_reasoning_effort = "low"
```

Leave `service_tier` out of `cheap-loop` unless the active model advertises the tier you want.

Activate with `codex --profile cheap-loop` or `codex --profile deep-review`.

### Documented cost warnings

OpenAI's docs explicitly warn:

- _"Because each subagent does its own model and tool work, subagent workflows consume more tokens than comparable single-agent runs."_
- _"Raising [delegation depth] can turn broad delegation instructions into repeated fan-out, which increases token usage, latency, and local resource consumption."_

Treat these as the same signal Claude Code's subagent-heavy usage warning surfaces — same failure mode, different surface.

## Cost Anti-Patterns

Fast reference list. Each one compounds the other signals above.

- **Most-expensive model everywhere via inheritance** — the most common cost error; always pin `model:` or set `CLAUDE_CODE_SUBAGENT_MODEL` (a floor for definition-less subagents, not a fleet-wide override where frontmatter wins — see §Signal 1)
- **Assuming `CLAUDE_CODE_SUBAGENT_MODEL` outranks frontmatter** — check the resolution order for the running version; only the force switch overrides every tier
- **Writing `effort:` on a member pinned to a model without effort support** — the field is inert
- **Heterogeneous wide fan-out** — agents share a prompt-cache prefix only when model, effort, agent type, tools, output schema and working directory all match
- **High effort on bounded read-only roles** — reviewers, explorers, file-walkers should drop to `low`/`medium` where evals hold
- **Carried-over verification instructions** — "add a final verification step" / "use a subagent to verify" can cause over-verification on models that already self-verify; re-test agent files written for an older generation
- **Spawning subagents for <3 tool-call tasks** — startup cost (context replay + MCP descriptions) exceeds task value
- **Parallel subagents with overlapping file ownership** — causes merge conflicts and rework
- **No `maxTurns` ceiling** — unbounded loops are how the runaway incidents happen
- **Mutating `task_budget.remaining` per turn** — breaks prompt cache without providing useful control
- **Deep subagent trees / recursive spawning** — context cost compounds multiplicatively
- **Redundant file reads across parallel workers** — fix with file-based handoffs (`REVIEW.md`) or `memory: project`
- **Plan-mode agent teams for bounded work** — team size, model, runtime mode, and task shape determine the multiplier; measure total usage against the single-agent control and reserve teams for genuinely multi-owner tasks
- **Inheriting the parent's full MCP surface** — scope `mcp_servers` per agent and measure the schema/context overhead that each target runtime actually loads and repeats
- **Verbose tool output sent straight to the model** — use a schema-valid `PostToolUse.updatedToolOutput` replacement while retaining the complete result outside model context, or route input through a vetted wrapper before execution

## Cross-References

- Agent field matrix and `model:` resolution order: [../../agents-swarm-orchestration/references/platform-patterns.md](../../agents-swarm-orchestration/references/platform-patterns.md)
- Per-role model policy governance: [model-governance-and-maintenance.md](model-governance-and-maintenance.md)
- Scenario selection (smallest-correct-mode rule): [../SKILL.md](../SKILL.md) §Scenario Selection Rule
- Session-level cost discipline (long sessions, context hygiene): [../../agents-swarm-orchestration/references/operational-guardrails.md](../../agents-swarm-orchestration/references/operational-guardrails.md)
- Fresh context principle (why subagent spawns are expensive): [context-first-protocol.md](context-first-protocol.md)
