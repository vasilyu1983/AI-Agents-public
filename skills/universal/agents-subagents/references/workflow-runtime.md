---
description: Dynamic Workflow tool runtime: enablement, ultracode, size guidelines, runtime caps, agent() options, resume, headless launch.
last_verified: 2026-09-02
status: stable
---

# Workflow Runtime

Practitioner reference for the **Workflow tool** — the fourth way Claude Code runs many agents, alongside subagents, agent view, and agent teams. Read this before authoring or running one. Choosing *whether* to use a workflow at all belongs to [`subagents-vs-teams-architecture.md`](subagents-vs-teams-architecture.md); the script API belongs to Claude Code's own bundled `/workflow-authoring` skill.

Sources: [code.claude.com/docs/en/workflows](https://code.claude.com/docs/en/workflows) and [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents). Values such as tier counts, caps, and version gates change between releases: read them in those pages, `/config`, or the changelog before relying on one. Facts marked *per the tool's own reference* come from the in-session Workflow tool description and the bundled `/workflow-authoring` skill, not a public doc page.

## Table of Contents

- [What it is](#what-it-is)
- [Enablement and gating](#enablement-and-gating)
- [Opting in per task: `ultracode`](#opting-in-per-task-ultracode)
- [Plan gating and approval](#plan-gating-and-approval)
- [Size guideline and the large-workflow warning](#size-guideline-and-the-large-workflow-warning)
- [Runtime caps](#runtime-caps)
- [The `agent()` option surface](#the-agent-option-surface)
- [Pipeline vs parallel](#pipeline-vs-parallel)
- [Script constraints](#script-constraints)
- [Saved workflows](#saved-workflows)
- [Resume semantics](#resume-semantics)
- [Headless and SDK launch](#headless-and-sdk-launch)
- [Turning workflows off](#turning-workflows-off)
- [Related](#related)

## What it is

"A dynamic workflow is a JavaScript script that orchestrates many subagents at once. Claude writes the script for the task you describe, and a runtime executes it in the background while your session stays responsive."

The distinction that matters for design: with subagents, skills, and teams, Claude holds the plan and every intermediate result lands in a context window. A workflow moves the plan into code — "the loop, the branching, and the intermediate results" live in script variables, "so Claude's context holds only the final answer." Scale is "dozens to hundreds of agents per run", and what is repeatable is "the orchestration itself".

Claude Code bundles one workflow, `/deep-research`, which "runs only when you invoke it."

## Enablement and gating

- Available "on all paid plans, with Anthropic API access, and on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry."
- **On Pro, turn them on from the Dynamic workflows row in `/config`.**
- Surfaces: the CLI, the Desktop app, the IDE extensions, non-interactive mode with `claude -p`, and the Agent SDK.

## Opting in per task: `ultracode`

Two opt-in routes, and they are not the same thing.

**Per prompt.** Include the keyword `ultracode` in a prompt you type, or just ask in your own words ("use a workflow"); "Claude treats a direct request as the same opt-in." Older releases used a different keyword; if it does not trigger, check the changelog for the running version. The keyword "only chooses how Claude structures the work" — agents' tool calls get the same permission checks and sandboxing as any other tool call.

The keyword is an opt-in **only in a prompt you type yourself**: the interactive prompt, an IDE extension panel, a Remote Control client, or an Agent SDK app that stamps input `origin` as `{ kind: "human" }`. It does *not* start a workflow from a `-p` prompt, an unstamped SDK prompt, a scheduled task prompt, or "a webhook payload or pull request comment relayed into the conversation" (older releases did — a real injection surface, so check the running version before trusting relayed text).

Dismiss a highlighted keyword with `Option+W` / `Alt+W`, or backspace with the cursor right after it. Turn the trigger off entirely via "Ultracode keyword trigger" in `/config`.

**Per session.** `/effort ultracode` is "a Claude Code setting that combines `xhigh` reasoning effort with automatic workflow orchestration. With it on, Claude plans a workflow for each substantive task instead of waiting for you to ask." Launch with `claude --effort ultracode`. It lasts the current session; the `ultracode` setting makes it the default for every session. Drop back with `/effort high`.

Cost consequence, stated plainly in the docs: "A single request can turn into several workflows in a row… each request uses more tokens and takes longer than at lower effort levels." Available only on models that support `xhigh`.

## Plan gating and approval

In the CLI the per-run prompt shows the planned phases with four options: **Yes, run it**; **Yes, and don't ask again for `<name>` in `<path>`** (offered only for a bundled, saved, or plugin workflow invoked by name — not for a script Claude just wrote); **View raw script**; **No**. `Ctrl+G` opens the script in your editor; `Tab` lets you adjust the prompt first.

Whether you are prompted depends on permission mode:

| Permission mode | When you're prompted |
|---|---|
| Auto | First launch only; any **Yes** records consent in user settings. "Skipped entirely when ultracode is on" |
| Manual, accept edits | Every run, unless you chose **Yes, and don't ask again** for that workflow in this project |
| Bypass permissions | Not prompted; the run starts immediately |
| `claude -p`, Agent SDK | Not prompted |

Claude "can start a workflow only from a script file the session is already allowed to read" — to run a script outside the working directory, add its directory with `/add-dir` or a Read allow rule first.

The subagents a workflow spawns use your ordinary permission rules, and their permission mode follows the normal subagent rules. Pre-approve the tools the agents need before a long run.

## Size guideline and the large-workflow warning

`workflowSizeGuideline` "tells Claude how many agents to aim for" — **advice, not a cap**: "a prompt that calls for a different scale still overrides it."

The setting takes named tiers (`unrestricted`, `small`, `medium`, `large`); each maps to a target agent count, and one tier is the default. **Lookup before sizing:** read the current tier counts and the default in the workflows docs or the `/config` row, then pick the smallest tier that covers the fan-out. Do not copy a tier count into a prompt or skill. Set it in `/config`, with `/config workflowSizeGuideline=small`, or as the `workflowSizeGuideline` settings key — the settings value takes precedence over `/config`, and Claude Code hides the `/config` row while a settings file provides one. Changes take effect on the next prompt.

**Large-workflow warning.** When a workflow's scheduled agent count or projected token total passes a documented threshold, its progress line shows a `Large workflow` warning pointing at `/workflows`, where you can stop the run. It is advisory: "it doesn't pause or limit the run." Two things change it — a size guideline you chose replaces the default agent threshold with its own count, and sessions with ultracode on don't show the warning at all "because turning ultracode on already opts you in to large runs."

## Runtime caps

These are runtime constraints and apply regardless of the size guideline. Read the current values in the workflows docs before sizing a run; a cap the docs call a default may be adjustable in settings, so treat none of them as a fixed hard limit:

| Cap | Detail |
|---|---|
| Concurrency | A per-workflow concurrent-agent cap that shrinks when fewer CPUs are available, including inside a CPU-limited container; excess calls queue rather than fail |
| Items per call | A per-call item limit on `parallel()` / `pipeline()`; a longer list is rejected with an explicit error, never silently truncated |
| Agents per run | A total-agents-per-run limit — a runaway-loop backstop |
| No mid-run input | "Only agent permission prompts can pause a run. For sign-off between stages, run each stage as its own workflow" |
| No filesystem or shell from the script | "Agents read, write, and run commands. The script coordinates the agents" |
| No module loading | "A script that contains `import()` fails before the run starts" |
| Cache stagger | Agents sharing the first agent's prompt-cache prefix start slightly after it; tune with `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS` (`0` disables) |

## The `agent()` option surface

`agent(prompt, opts)` spawns one subagent. Per the tool's own reference, the options are:

| Option | Effect |
|---|---|
| `label` | Overrides the display label in the progress view |
| `phase` | Explicitly assigns the agent to a progress group. Use it inside `pipeline()`/`parallel()` stages to avoid races on the global `phase()` state — same phase string, same group box |
| `schema` | A JSON Schema. The subagent is forced to call a StructuredOutput tool and `agent()` returns the validated object; validation happens at the tool-call layer, so the model retries on mismatch. Without a schema, `agent()` returns the final text as a string |
| `model` | Per-call model override. **Default to omitting it** — the agent inherits the resolved session model, which is almost always correct |
| `effort` | `low` / `medium` / `high` / `xhigh` / `max`. Omit to inherit session effort; `low` for cheap mechanical stages, higher tiers only for the hardest verify/judge stages |
| `isolation: 'worktree'` | Runs the agent in a fresh git worktree. **Expensive** (setup time plus disk per agent) — use only when agents mutate files in parallel and would otherwise conflict. The worktree is auto-removed if unchanged |
| `agentType` | Uses a custom subagent type instead of the default workflow subagent, resolved from the same registry as the Agent tool. Composes with `schema` |

`agent()` "resolves to `null` if you stop it mid-run or it hits an unrecoverable API error", and `pipeline()` keeps that `null` in the results array — hence the `.filter(Boolean)` in every documented example.

Model choice follows the ordinary subagent order: "a model the script names for a stage counts as the per-invocation model in that order", and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` overrides both where the running version supports it. When an `availableModels` allowlist blocks the requested model, the agent runs on a substituted one and the `/workflows` progress view "shows a warning naming both the requested and substituted models."

## Pipeline vs parallel

- `pipeline(items, stage1, stage2, …)` runs each item through all stages **independently, with no barrier between stages** — item A can be in stage 3 while item B is still in stage 1. This is the default for multi-stage work; wall-clock is the slowest single-item chain, not the sum of per-stage worst cases. A stage that throws drops that item to `null` and skips its remaining stages. *(Per the tool's own reference.)*
- `parallel(thunks)` runs tasks concurrently and **is a barrier** — it awaits all thunks. A throwing thunk resolves to `null` rather than rejecting the call.

A barrier is correct only when stage N needs cross-item context from all of stage N−1: dedup or merge across the full result set, an early exit on a zero total, or a prompt that references "the other findings". It is *not* justified by needing to flatten/map/filter first (do that inside a pipeline stage), by stages being conceptually separate, or by cleaner code — "barrier latency is real." *(Per the tool's own reference.)*

`phase(title)` groups the agents that follow under a title in the progress view; `log(message)` shows a narrator line above the phases.

## Script constraints

- **`meta` must be a pure literal.** Keep `export const meta` as the first statement and a plain object literal with `name` and `description`. "If it contains anything other than literal values, such as a variable, a function call, or a spread, Claude Code drops `/<name>` from `/` autocomplete." Optional: `whenToUse`, `phases`.
- **Phase titles are matched exactly.** Each `meta.phases` entry must carry exactly the title passed to `phase()`; "a `phase()` title with no entry gets a progress group of its own."
- **Forbidden globals.** "Claude Code makes `Date.now()`, `Math.random()`, and a no-argument `new Date()` throw inside the script, so that a relaunched run repeats the same `agent()` calls." Pass a timestamp in through `args`, stamp results after the workflow returns, and vary randomness by index instead.
- **Plain JavaScript, not TypeScript** — type annotations, interfaces, and generics fail to parse. Top-level `await` works. *(Per the tool's own reference.)*
- **`args`** is read as a global, `undefined` when omitted. Pass arrays and objects as real JSON values, not a JSON-encoded string, or `args.map`/`args.filter` throw. *(Per the tool's own reference.)*

## Saved workflows

Save a run's script from `/workflows` by selecting the run and pressing `s`. Two locations, toggled with Tab in the save dialog:

- `.claude/workflows/` in the project — "shared with everyone who clones the repo"
- `~/.claude/workflows/` — every project, visible only to you (under `CLAUDE_CONFIG_DIR` when set)

A saved workflow runs as `/<name>`. If a project and a personal workflow share a name, the project one runs. In a monorepo, saving to the project location writes to the closest existing `.claude/workflows/` between the working directory and the repo root, project workflows load from every `.claude/workflows/` along that path, and the one closest to the working directory wins on a name collision.

Claude Code refuses to write through a symlink: for the project location it refuses if `.claude`, `.claude/workflows`, or the target file is a symlink; for the personal location only if the target file itself is. Older releases followed the link, which could place the file outside the chosen location; check the running version before saving into a symlinked tree.

**Plugin distribution:** put the script in a `workflows/` directory at the plugin root (or point at another location with the `workflows` manifest field). Plugin workflows are namespaced — plugin `acme-tools` with `meta.name` `release-audit` runs as `/acme-tools:release-audit`.

To edit a saved script, run the bundled **`/workflow-authoring`** skill first to load the script-writing reference Claude works from, then edit the `.js` file or ask Claude to. Run `/reload-skills` to re-read the workflow directories in the current session.

## Resume semantics

"The runtime tracks each agent's result as the run progresses, which is what makes a run resumable within the same session." Resume a paused run from `/workflows` with `p`. On relaunch, "Claude Code replays the run in the order agents started", and each agent either returns its saved result or runs again:

- **Completed** — returns the saved result. "The first agent whose prompt differs from the previous run… runs again, and so does every agent after it, even ones that completed."
- **Still running when you stopped** — starts over. Stopping the whole run counts no agent as failed.
- **Failed** — runs again, and so does every agent that started after it. Stopping one agent alone (`x` in `/workflows`) counts as failing.

The consequence to plan for: "a failure in the middle of a fan-out reruns work that already finished."

Leaving the session: backgrounding it continues the run in the background session. Exiting with a workflow running and agent view on offers `Move to background and exit`, which carries the run over; `Exit and stop tasks` stops it with the session. Saved results stay under that session's directory in `~/.claude/projects/`, so a `claude --resume` session can replay them while a fresh session starts the workflow over.

Every run writes its script to a file under the session's directory in `~/.claude/projects/`, and Claude receives the path when the run starts — ask for it to read, diff, or edit the orchestration. Per the tool's own reference, the tool result also includes a `runId`, and the resume call is `Workflow({scriptPath, resumeFromRunId})`: the longest unchanged prefix of `agent()` calls returns cached results instantly, same script plus same args gives a 100% cache hit, and `<transcriptDir>/journal.jsonl` records each agent's actual return value — read it before concluding a completed workflow returned nothing.

## Headless and SDK launch

In `claude -p` and the Agent SDK, "Claude Code never shows this prompt." The Workflow tool call goes through the same permission evaluation as any other tool call, so deny rules, ask rules, and `dontAsk` mode apply to the launch. To let it start, use one of:

- a permission rule — `Workflow` in your allow rules approves every workflow, `Workflow(<name>)` approves one saved workflow by name
- auto permission mode, where the classifier can approve the call
- bypass permissions mode
- a `PreToolUse` hook returning `allow`
- your host — a `--permission-prompt-tool`, or the SDK's `canUseTool` callback or `PermissionRequest` hook

Two more headless gotchas: the `ultracode` keyword does **not** opt in from a `-p` prompt or an unstamped SDK prompt, so name the workflow or use a saved one; and per the tool's own reference, interactively-authenticated MCP servers may be absent in headless or cron runs even though workflow agents can otherwise reach session-connected MCP tools via ToolSearch.

## Turning workflows off

- Toggle "Dynamic workflows" off in `/config` — persists across sessions
- `"disableWorkflows": true` in `~/.claude/settings.json` — persists across sessions
- `CLAUDE_CODE_DISABLE_WORKFLOWS=1` — read at startup, "so it applies wherever you set it"
- Organization-wide: `"disableWorkflows": true` in managed settings, or the toggle on the Claude Code admin settings page

"When workflows are disabled, the bundled workflow commands and the `/workflow-authoring` skill are unavailable, the `ultracode` keyword no longer triggers a run, and `ultracode` is removed from the `/effort` menu."

## Related

- [`runtime-surfaces.md`](runtime-surfaces.md) — subagent and teammate model resolution, built-ins, Agent Teams surfaces
- [`subagents-vs-teams-architecture.md`](subagents-vs-teams-architecture.md) — choosing between the delegation surfaces
- [`cost-control.md`](cost-control.md) §"Dynamic Workflow Cost Controls" — spend levers for large runs
- [`../../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md) — wave planning when concurrent writers exceed merge capacity
