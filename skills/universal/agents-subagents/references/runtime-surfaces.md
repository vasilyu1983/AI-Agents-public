---
description: Claude Code and Codex surfaces, field mapping, Agent SDK pointers, Managed Agents.
last_verified: 2026-09-16
status: stable
---

# Runtime Surfaces

Compact reference for the runtime-specific behavior behind `agents-subagents`.

The authoritative field matrix (including every optional frontmatter key, the built-in subagent table, Agent Teams availability and version gate, and the OpenAI Agents SDK manager/handoff pattern) lives in [`../../agents-swarm-orchestration/references/platform-patterns.md`](../../agents-swarm-orchestration/references/platform-patterns.md). This file stays compact and focuses on **decision and portability rules** — read it alongside `platform-patterns.md` when shaping an agent file.

## Table of Contents

- [Claude Code](#claude-code)
- [Codex](#codex)
- [Agent SDKs](#agent-sdks)
- [Claude Managed Agents](#claude-managed-agents)
- [Cross-Platform Rules](#cross-platform-rules)

The Workflow tool — the script-driven fan-out surface — has its own runtime reference: [`workflow-runtime.md`](workflow-runtime.md).

## Claude Code

### Creation paths and precedence

Claude Code resolves agent definitions in this order (highest-priority first):

1. **Managed settings** — organization-wide agents injected by admin policy.
2. **Session-scoped** — definitions passed through `--agents` as JSON on the CLI, used for one session (automation, CI runs, or temporary fan-out).
3. **Project** — `.claude/agents/*.md`, version-controllable per repo.
4. **Personal** — `~/.claude/agents/*.md`, reused across all your repos.
5. **Plugin** — agents shipped inside enabled plugins; treat these like managed specialists and reuse before authoring a project override.

Recent Claude Code releases removed the `/agents` interactive editor; check the changelog for your version. Create or edit agent Markdown files directly. Changes hot-reload within seconds when the containing agent directory already existed at session start; restart only when adding the first agent directory, adding a directory through `--add-dir`, or when slash commands are disabled. A custom agent that shares a name with a built-in overrides it silently, so keep names distinct unless the override is intentional.

### Whole-session agent mode

Use `--agent <name>` (or the `agent` setting) to start the session as a selected agent so one role owns the whole interaction. Combine with `initialPrompt` frontmatter to auto-submit a first turn.

### Built-in subagents

Claude Code ships three directly usable built-in subagents, plus three auto-invoked ones. Try these before authoring a custom agent — a custom agent is only justified when you need repo-specific behavior, a custom output contract, or restricted tool/MCP scope that the built-ins cannot provide.

| Subagent | Model | Tools | Purpose |
|----------|-------|-------|---------|
| `Explore` | Inherits parent model | Read-only | File discovery, code search, codebase exploration |
| `Plan` | Inherits | Read-only | Codebase research during plan mode |
| `general-purpose` | `CLAUDE_CODE_SUBAGENT_MODEL` if set, else the main conversation's model | All | Complex research, multi-step operations, code modifications |
| `claude` | "None of its own; follows the model order" | Every tool available to subagents | Catch-all when a task doesn't fit a more specialized agent; also **the default agent for a dispatched background session** |
| `statusline-setup` | Sonnet | Read, Edit | Auto-invoked to configure the Claude Code status line — not for direct use |
| `claude-code-guide` | Haiku | Docs lookup | Auto-invoked for "how do I…" questions about Claude Code, the Agent SDK, and the Claude API — not for direct use |

To turn built-ins **off** (the opposite decision, and the one this file previously omitted):

| Goal | Lever |
|---|---|
| Block one type | `permissions.deny: ["Agent(Explore)"]` — the same form works for a custom type, `Agent(my-custom-agent)` |
| Prevent all subagent delegation | deny the `Agent` tool itself in `permissions.deny` |
| Remove only `Explore` and `Plan` | `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` — "Claude reads and explores files directly instead." Check the sub-agents docs for the minimum version |
| Remove all built-ins in non-interactive / SDK runs | `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` — "This removes all built-in types; supply only your own." |

See [`../../agents-swarm-orchestration/references/platform-patterns.md`](../../agents-swarm-orchestration/references/platform-patterns.md) §"Built-in agents" for the field matrix and additional behavior notes. Source: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents).

### Subagents vs Agent Teams

- Use a subagent when the parent thread can issue one clear brief and wait for a result.
- Use agent teams when specialists need to coordinate directly, challenge each other, or self-claim tasks.
- **Agent Teams is experimental** and disabled by default. Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or environment. Behaviour below has changed between releases: before relying on any of it, read the agent-teams docs and the changelog for the running version (`claude --version`). Do not assume a lead-model gate unless the docs state one.
- **Two behaviours that surprise operators.** First, the flag changes *ordinary* delegation: "Claude may name a subagent on its own, and while agent teams are enabled, a subagent that Claude names launches as a teammate, so teams can form even when you didn't ask for one." To get subagents back, set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` to `0` — no new session needed, since Claude Code reapplies settings-file `env` values to the running session on save and rereads the variable on each spawn. Note the precedence trap: `0` in *user* settings overrides a shell export, but project settings, local settings, `--settings`, and managed settings all apply later and a `1` in any of them wins.
- **Teammate plan approval is not a human gate.** "When a teammate finishes planning, it sends a plan approval request to the lead. Claude Code approves the plan in the lead's session as soon as the request arrives, without the lead reviewing it." The teammate's edits and commands still hit ordinary permission prompts. Read the `TeammateIdle` / `TaskCreated` / `TaskCompleted` hooks as the *only* enforceable gate on teammate work — plan approval is not one.
- Spawning teammates **requires an interactive session**. Under `-p` and in the Agent SDK, Claude doesn't spawn teammates and a named subagent runs as an ordinary subagent even with the flag on.
- Setup and cleanup are now automatic: spawning a teammate needs no setup step, and team state is removed when the session ends. The old `TeamCreate`/`TeamDelete` tools and the manual "name a team first" flow no longer exist.
- **No nested teams** — a teammate cannot spawn its own teammates or its own background subagents (an in-process teammate's subagents always run in the foreground, since they can't outlive the lead's process). Only the lead manages team composition.
- Default display mode is **in-process** (all teammates in one terminal, arrow keys + Enter to view/message a teammate). **Split-pane mode is a hard requirement, not just "unreliable"**: it needs tmux or iTerm2 with the `it2` CLI, and is unsupported in VS Code's integrated terminal, Windows Terminal, and Ghostty regardless of configuration — don't design a launch flow that assumes split panes will work in an arbitrary terminal. The configuration surface is the `teammateMode` setting in `~/.claude/settings.json`, or the experimental `--teammate-mode` flag for one session (it "doesn't appear in `claude --help`"). Documented values: `"in-process"` (read the docs for the current default; older releases defaulted to `"auto"`), `"auto"` (split panes when already inside tmux, or in iTerm2 with the `it2` CLI installed, falling back to in-process), `"tmux"` (split panes, auto-detecting tmux vs iTerm2), and `"iterm2"` (explicit iTerm2 native split panes; errors with an install command when `it2` is missing).
- **Teammate model resolution — this file owns the fact.** Claude Code picks each teammate's model from the first of these that applies: "1. The model your spawn prompt names for that teammate. 2. For a teammate spawned from a subagent definition, the definition's `model`, where `inherit` selects the lead's model. 3. `CLAUDE_CODE_SUBAGENT_MODEL`, when it's set to anything other than `inherit`. 4. The lead's current model." **The order has changed between releases** (older releases put `CLAUDE_CODE_SUBAGENT_MODEL` first); read the order in the docs for the running version. Practical consequence for any repo that sets `CLAUDE_CODE_SUBAGENT_MODEL` globally *and* declares `model:` on its members: where the definition ranks first, the declared per-member tier wins, so the global override does not flatten the fleet onto one tier. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`, where supported, restores the override: it forces subagents, teammates, and workflow agents onto `CLAUDE_CODE_SUBAGENT_MODEL` regardless of definition or invocation (a fork and a skill with `model: inherit` still run on the main conversation's model). A removed `teammateDefaultModel` setting is ignored if left over in older configs.
- Teammates inherit the lead's **effort** level, not its `/model` selection — a teammate's model and fast mode are fixed at spawn time. Check the docs for whether split-pane teammates inherit effort on your version.
- Keep orchestration in the parent thread when the task is short, iterative, or heavily dependent on existing conversation state.

### Teammate reuse rules

- A subagent definition can be reused as a teammate.
- Which parts of the definition apply — and **two of them depend on the display mode**:

| Field | In-process teammate | Split-pane teammate |
|---|---|---|
| `tools` | Limited to the definition's list, plus `SendMessage` and (where the session has them) `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` | Limited to the definition's list |
| `model` | Applied in either mode when the spawn prompt names none — see §"Subagents vs Agent Teams" for the full resolution order |
| Body | **Appended** to the default system prompt as additional instructions | **Replaces** the default system prompt |
| `skills` | Not applied in either mode; the teammate loads skills from project and user settings |
| `mcpServers` | **Ignored** — loads MCP servers from project and user settings | **Applied**, under the ordinary rules for that field |

  The body and `mcpServers` splits are the ones that bite: the same member definition is a *system-prompt override with its own MCP scope* as a split-pane teammate and an *appended instruction block with no MCP scope* in-process.
- Teammates start from fresh task context plus project context, not the full lead transcript.
- Teammates share the lead's working directory. A reused definition's `isolation: worktree` does not isolate a teammate; assign disjoint files or use ordinary subagents when worktree isolation is required.

### Cross-session messaging (no team required)

Claude Code sessions can message each other without a team: `ListAgents` enumerates reachable sessions and `SendMessage` addresses one by name. It does **not** require Agent Teams or its experimental flag. Availability differs by OS, provider, and sign-in method, and reach beyond the local machine depends on Remote Control. **Lookup before designing on it:** read [code.claude.com/docs/en/cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging) and the changelog for the running version; where the two disagree on a version floor, trust the shipped changelog.

Design consequence: peer-to-peer coordination is no longer a reason on its own to reach for the experimental team surface. When two long-running sessions already hold useful context, messaging may avoid rebuilding it inside one lead's team, but compare message, cache, synthesis, and rework usage before claiming a saving. Keep using teams when you need the shared task layer and self-claiming — not merely because workers must talk.

### Background sessions and routines

Both surfaces change between releases; read the docs for the running version before relying on a command, setting, or safety default below.

- **Background sessions** — several independent tasks to hand off and check back on later. Started from agent view (`claude agents`), `/bg` / `/background`, or `claude --bg`. Each session moves itself into an isolated git worktree under `.claude/worktrees/` before editing, with no `isolation:` field on any definition; a per-repository setting (`worktree.bgIsolation`) turns that off. Check the worktree base as in [agent-tools.md](agent-tools.md) §"isolation".
- **Routines** — hosted, unattended runs (inbox triage, scheduled research, document processing) on Anthropic-managed infrastructure, created with `/schedule`, triggered by a cron cadence, an HTTP endpoint, or repository events. Three safety checks before saving one: a run has no interactive approval step, so scope tools as if permission prompts do not exist; connected connectors may be included by default, so prune them to the ones the routine needs; and trigger text arrives as an untrusted payload block, so the saved prompt must name that block and treat it as data. Escalate to [Claude Managed Agents](#claude-managed-agents) only when you need your own hosting.

### Do not pre-author team runtime config

Agent Teams stays experimental and env-gated, and its runtime state is created and torn down by the session itself (see above). There is no supported `~/.claude/teams` file to author ahead of time. Reusable roles belong in **subagent definitions** (`agents/`), which both runtimes read; `agents/teams/*/team.yaml` in this repo is installer metadata that neither Claude nor Codex reads as native runtime configuration. Source: [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams).

## Codex

### Creation paths

- Project agents live in `.codex/agents/*.toml`.
- Personal agents live in `~/.codex/agents/*.toml`.
- Codex built-ins are `default`, `worker`, and `explorer`; a custom agent with the same name overrides the built-in.
- Current Codex subagent surfaces support named custom-agent selection through the spawn contract. Verify the exact registered name and run one smoke test after installation; fall back to a self-contained role brief only when the active surface reports that named selection is unavailable.
- Codex refuses to delegate unless the user or applicable `AGENTS.md`/skill instructions explicitly authorize sub-agents — a skill that expects members to fire must grant delegation in its own text.

### Core behavior

- Codex delegates after a direct request or when applicable `AGENTS.md`/skill instructions request delegation. Do not assume proactive delegation without either signal.
- Keep the main thread focused on requirements, decision framing, and final synthesis.
- Prefer read-heavy workers first; escalate to write-capable workers only after owned files and verification are explicit.
- Use shared teams to choose roles and ownership, even when orchestration stays in the parent thread.
- Subagents inherit the parent session's sandbox policy. Turn-level overrides (`--yolo`, approval changes) reapply to children.
- Approval requests from inactive threads surface in the main thread — press `o` to switch to the requesting thread.
- Keep nesting bounded by prompt and repository policy. Current public documentation does not establish a universal no-nesting rule, and supported collaboration surfaces may allow a child to spawn children.
- Codex cloud background work is real, but open internet should stay opt-in. Current OpenAI docs say agent internet access is blocked by default during the agent phase; if you enable it, restrict domains and HTTP methods, and treat fetched content as untrusted because prompt injection, secret exfiltration, malware, and license-risk become part of the threat model.

### Field mapping

| Concept | Claude Code | Codex |
|---|---|---|
| Project location | `.claude/agents/*.md` | `.codex/agents/*.toml` |
| Personal location | `~/.claude/agents/*.md` | `~/.codex/agents/*.toml` |
| Name | frontmatter `name` | `name` |
| Description | frontmatter `description` | `description` |
| Instructions (required) | markdown body | `developer_instructions` (required) |
| Permission control | `permissionMode` | `sandbox_mode` |
| MCP access | `mcpServers` | `[mcp_servers.<name>]` |
| Model override | `model` | `model` + `model_reasoning_effort` |
| Background | `background: true` | thread-based |
| Isolation | `isolation: worktree` | agent threads share the checkout; use a separate Worktree chat/environment for filesystem isolation |
| Display labels | `color` | runtime-managed thread labels |
| Skills | `skills` list (content injected at startup) | `skills.config` controls per-skill enablement; discovery and activation still apply |

In this repo, canonical Codex files carry catalog skill metadata in prose. Installed `[[skills.config]]` entries are native per-skill enablement overrides, not eager skill-content injection. Normal discovery and activation still apply, so the inline role brief remains the portable fallback.
Codex skill wiring should follow the documented `.agents/skills` model: repository installs materialize `$REPO_ROOT/.agents/skills/<skill-id>` and user installs can use `$HOME/.agents/skills/<skill-id>` when explicit skill configs are needed.
At every Codex scope (user, project, repo), install an installer-owned TOML rather than symlinking the canonical file: the installer materializes model tier, `[[skills.config]]`, and rewritten reference links, none of which a symlink can carry. Record ownership so upgrades and pruning cannot confuse an installer artifact with a user-authored custom agent.

### Practical Codex config

The documented `[agents]` keys are these five — all optional:

| Key | Type | Purpose | Default |
|---|---|---|---|
| `agents.enabled` | boolean | "Enable or disable multi-agent tools." | `true` |
| `agents.max_concurrent_threads_per_session` | number | "Cap concurrently open spawned-agent threads, excluding the primary." | Codex's own default when unset |
| `agents.default_subagent_model` | string | "Set the default model for spawned agents." | — |
| `agents.default_subagent_reasoning_effort` | string | "Set the default reasoning effort for spawned agents." | — |
| `agents.interrupt_message` | boolean | "Record a model-visible message when an agent turn is interrupted." | `true` |

```toml
[agents]
# enabled defaults to true; set it explicitly only to turn multi-agent tools off.
# Operator policy — omit any line to keep Codex's default.
# max_concurrent_threads_per_session = 6
# default_subagent_model = "<standard-tier-model>"   # see data/model-policy.json for current tiers
# default_subagent_reasoning_effort = "low"
# interrupt_message = true
```

Set the two `default_subagent_*` keys as the fleet-wide cost floor and pin only the roles that need more — see [`cost-control.md`](cost-control.md) §"Codex Equivalents". Source: [learn.chatgpt.com/docs/agent-configuration/subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Use prompt or `AGENTS.md` policy to cap nesting and keep leaf roles from delegating when that is the intended topology. Do not invent undocumented `max_depth` or job-runtime keys.

When concurrent write-capable workers exceed the lead's merge and approval capacity, move to explicit waves through [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md) or separate Worktree chats. Do not mistake agent threads for filesystem isolation.

## Agent SDKs

Shared skills are used from both CLIs and from SDK-driven agent hosts. The role design, handoff contract, and team/debate assets in this skill apply to SDK builds too — only the orchestration surface changes.

### Claude Agent SDK (Python and TypeScript)

- Build agents as **harnesses around the Claude model**: you own the loop, provide tool results, and stream messages. Skills, system prompts, and agent-file roles map cleanly onto SDK configuration.
- Use when a product needs to embed an agent, not drive a CLI. The selection order (main-loop completion → built-in → installed specialist → repo-local/shared member → scripted workflow → team → debate) still applies; the SDK just replaces the interactive runtime.
- See [`../../ai-agents/references/claude-agent-sdk-patterns.md`](../../ai-agents/references/claude-agent-sdk-patterns.md) for patterns.

#### Claude Agent SDK gotchas (re-read the SDK docs for the running version before relying on one)

- **Package names**: `claude-agent-sdk` (Python, PyPI) and `@anthropic-ai/claude-agent-sdk` (TypeScript, npm). The pre-rename names `claude-code-sdk` / `@anthropic-ai/claude-code` are legacy — migrate. Source: [code.claude.com/docs/en/agent-sdk/subagents](https://code.claude.com/docs/en/agent-sdk/subagents).
- **`Agent` tool in `allowedTools`**: `AgentDefinition` subagents fail silently if the parent session does not include `Agent` in `allowedTools`. Include it explicitly when programmatically defining agents.
- **Recursive spawn is allowed and configurable.** The default depth has changed between releases; read it, and whether `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` is honoured, in the sub-agents docs for the running version. To keep a role from spawning children, omit `Agent` from its `tools` array or add it to `disallowedTools`. Treat nested fan-out as a cost and context-rot risk rather than relying on the runtime maximum.
- **Background behavior depends on the session mode.** Interactive sessions, fork mode, `-p`, and the Agent SDK can differ in whether a subagent runs in the background, and the defaults have changed between releases, so do not pin one. Before a step that consumes a subagent's result, determine the mode for this session (docs for the running version plus the [runtime smoke test](runtime-smoke-tests.md)); if subagents run in the background, force the foreground where a lever exists or wait explicitly for the completion notification. `background: true` in an agent file forces background execution. See [agent-tools.md](agent-tools.md) §"background".
- **Scaling past a handful of agents**: the Agent SDK's `Workflow` tool (check the SDK changelog for availability) moves orchestration of dozens-to-hundreds of agents into a script the runtime executes outside the conversation context, instead of turn-by-turn `Agent` calls. Reach for it when a single conversation would need to coordinate more agents than a human reviewer could meaningfully steer turn-by-turn; below that, turn-by-turn subagent delegation stays simpler to reason about and debug.
- **Windows command-line cap**: long inline SDK prompts can hit the Windows command-line length limit; move long prompts to filesystem agent files.
- **Spend and concurrency caps exist — use them**: the SDK documents a concurrent-subagent cap (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; excess calls error rather than queue) and a hard budget cap (`maxBudgetUsd` / `max_budget_usd`). Read the current default in the SDK docs before sizing a fan-out. Any cost-control design that throttles fan-out by prompt discipline alone is leaving the enforced levers unused.
- **Tool-name log drift**: the delegation tool was renamed `Task` → `Agent` (check the tools reference for which name the running version emits where). `system:init` and `permission_denials` streams still emit `"Task"` even though `tool_use` blocks now emit `"Agent"`. Match both names when parsing tool-use logs or writing eval graders.

### OpenAI Agents SDK

Two broad orchestration patterns, documented in [`../../agents-swarm-orchestration/references/platform-patterns.md`](../../agents-swarm-orchestration/references/platform-patterns.md) §"OpenAI Agents SDK":

- **Manager / agents-as-tools** — one orchestrator keeps control; specialist agents are exposed as tools. Best when the user should experience one coherent owner.
- **Handoffs** — a specialist receives the conversation history and takes over. Best when ownership should move by domain, queue, or workflow stage.

Repository team recipes can be adapted to either pattern, but the mapping is not automatic. Agents-as-tools keeps the manager as conversation owner; a handoff makes the specialist active for the remainder of the turn. A handoff is not a debate overlay. An SDK adapter must translate the recipe into agents-as-tools, handoffs, code-driven sequencing, or parallel execution.

#### Capability additions

From the SDK docs ([Sandbox agents](https://openai.github.io/openai-agents-python/sandbox_agents/), [Sessions](https://openai.github.io/openai-agents-python/sessions/); checked 2026-09-27):

- **Sandbox agents** — "give the model a persistent workspace where it can search large document sets, edit files, run commands, generate artifacts, and pick work back up from saved sandbox state." Aligns with this skill's worker-isolation guidance, but the confinement is client-dependent: the local Unix client "adds no OS-level confinement to commands" on Linux and on macOS "does not provide network isolation." Pick the sandbox client for the isolation you need; do not assume the default isolates.
- **Sessions as memory** — "built-in session memory to automatically maintain conversation history across multiple agent runs", with backends from SQLite through Redis, SQLAlchemy, MongoDB, and OpenAI-hosted conversations. Matches the opt-in `memory:` guidance in [agent-tools.md](agent-tools.md): choose the backend and its retention explicitly rather than accepting the default.

Verify the exact API surface against the current SDK docs before building on these.

## Claude Managed Agents

Anthropic's hosted REST runtime for production agents. The agent, environment, session, event, memory, limits, and pricing surfaces are documented in the official [Managed Agents reference](https://platform.claude.com/docs/en/managed-agents/reference) and [memory guide](https://platform.claude.com/docs/en/managed-agents/memory).

Unlike Claude Code agents (local filesystem) or the Claude Agent SDK (you own the harness), Managed Agents **runs on Anthropic infrastructure**. The handoff contract from this skill still applies — only the runtime surface changes.

### Four-piece model

| Piece | Role | Equivalent in local agents |
|---|---|---|
| **Agent** | Job description: model, instructions, tools | `.claude/agents/*.md` frontmatter + body |
| **Environment** | Sandboxed workspace pre-loaded with software, file persistence, code execution, web search | Your local shell + MCP servers |
| **Session** | Persistent conversation — remembers across hours, files survive, survives connection drops | Your terminal session (but durable) |
| **Events** | Inbound tasks and streamed outbound status/results/approval requests | Tool calls + your read of the transcript |

### Permission modes

Two modes, mixable within the same agent:

- **Auto-run** — agent executes without interruption. Use for internal workflows where the operation is trusted.
- **Approval-required** — agent pauses before specific actions and waits for sign-off. Use for external or irreversible actions (send email, push code, hit production APIs).

Mix: let the agent research and draft automatically, require approval before external effects. This maps onto the Claude Code `permissionMode` + per-tool approval pattern but is enforced by the hosted runtime rather than the CLI.

### When to reach for it

| Scenario | Prefer Managed Agents | Prefer local Claude Code agent | Prefer Claude Agent SDK |
|---|---|---|---|
| Long-running (hours) background workflows | ✓ | | |
| Scheduled/cron-like runs without a host machine | ✓ | | |
| Operator not in a terminal during the run | ✓ | | |
| Deep repo access, local FS, editor integration | | ✓ | |
| One-off interactive coding tasks | | ✓ | |
| Embedding an agent inside your own product | | | ✓ |

### Onboarding path

From Claude Code, type: `start onboarding for managed agents in Claude API`. The onboarding creates the agent, sets up the environment, and runs a test session. Otherwise use the console at `platform.claude.com`.

### Cost note

Standard token rates plus a per-session-hour charge for active runtime, plus a per-search charge if web search is enabled; read the current rates on the pricing page. Because sessions persist for hours, the session-hour charge is a new cost vector distinct from token-only runs — budget for it in long-running or always-on agents. See also [`../../agents-swarm-orchestration/references/cost-discipline.md`](../../agents-swarm-orchestration/references/cost-discipline.md).

### Trade-offs

- **You give up**: direct filesystem access, your local tooling, full offline control of the harness.
- **You get**: managed sandboxing, durable sessions that survive connection drops, hosted scheduling, and no ops burden for the agent runtime.

Stay on Claude Code or the Agent SDK when the work is inherently local (repo edits, IDE-adjacent flows) or when you need to own the loop. Move to Managed Agents when the agent is essentially a hosted service (inbox triage, meeting prep, content research, document processing, scheduled code review) and the operator is rarely at a terminal.

### Memory stores

Managed Agents persists cross-session memory through **memory stores** — workspace-scoped collections of text files that outlive any single session. The design choice is deliberate: rather than ship a specialized memory tool, the platform mounts a directory and lets Claude use its standard file tools to organize memory however it wants. See [`../../ai-context-layer/references/filesystem-as-memory.md`](../../ai-context-layer/references/filesystem-as-memory.md) for the underlying thesis and the Pokémon longitudinal evidence.

| Aspect | Behavior |
|---|---|
| Mount path | `/mnt/memory/<slug>/` inside the managed session |
| Discovery | A short note about the mount is auto-injected into the system prompt so Claude knows it's there |
| Reuse | Attach a store to multiple sessions to share durable workspace-scoped context |
| Versioning | Every change to a memory creates an immutable memory version (retained 30 days, with recent versions of a live memory always kept); a session may attach a store `read_only` |
| Limits | Up to 8 stores per session and 10,000 memories per store; each individual memory is capped at 100 kB (~25k tokens) |
| Interpretability | Files are plain text and downloadable — debuggable and shareable like any folder |

Operating rules:

- Treat memory stores as the L2 "flat files" rung of the memory ladder ([`../../agents-memory/references/memory-architecture-ceilings.md`](../../agents-memory/references/memory-architecture-ceilings.md)) when Managed Agents is the runtime — the local-disk equivalent moves to the hosted mount.
- Per [`../../ai-context-layer/references/managed-memory-boundaries.md`](../../ai-context-layer/references/managed-memory-boundaries.md), do not let memory-store contents become canonical product truth (entitlements, billing, account state). Hosted memory holds learned context; the system of record stays in your app.
- Apply the "memory is an exception, not a default" rule from [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md) — only attach a store when the role benefits from durable cross-run priors. Reviewers, verifiers, and short-lived workers should run without one.

## Cross-Platform Rules

- Keep work in the main thread or host loop when it can finish directly; otherwise reuse a built-in subagent, installed global or project agent, or plugin-provided agent before creating a new one.
- Prefer one bounded subagent over a team when only the result matters.
- Prefer a saved scripted workflow over a team when control flow is repeatable and workers do not need peer coordination.
- Use artifact paths and small context packets instead of forcing workers to reread the whole codebase.
- Assign owned files explicitly for any write-capable worker.
- Treat isolation, backgrounding, and skill wiring as runtime-scoped behavior, not portable defaults.
- Send a self-contained worker brief and record the runtime's context-start mode. Use fresh history for independent review; use a documented fork only when inherited history is required (see SKILL.md §Forking Parent Context Into Subagents).
