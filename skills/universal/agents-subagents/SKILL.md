---
name: agents-subagents
description: "Chooses subagent, team, workflow, or debate and launches it on Claude Code or Codex. Use when delegating, running agent review boards, or installing shared agents."
compatibility: Claude Code + Codex. Claude Code and Codex subagent/team conventions — runtime-specific invocation.
version: "1.5"
last_validated: 2026-09-02
---

# Universal Agent Skill (Claude Code + Codex)

Default entry point for agent work in this repo.

Use this skill as the main entry point for agent work on Claude Code or Codex:
- reuse global agents already installed in `~/.claude/agents/` or `~/.codex/agents/`
- create or update repo-local agents in `.claude/agents/` or `.codex/agents/`
- install or refine shared members and repository team recipes
- distribute members and workflows natively: a plugin serves agents from `agents/` and workflows from `workflows/` at its root (namespaced `plugin-name:agent-name`), and a `.claude-plugin/plugin.json` dropped into a skill folder loads it as `<name>@skills-dir` so the skill itself can bundle `agents/`, hooks, and MCP servers. `scripts/deploy-preset.sh` is the bulk/legacy route for the installed member pairs
- run structured debates
- select the correct agent, member, team, or debate mode for a scenario
- prepare the initial launch prompt that starts the chosen agent or team cleanly
- define delegation boundaries, context handoff quality, tools, and safety boundaries

For parallel execution plans, wave dispatch, and conflict resolution, escalate to [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md). For skill packaging and `SKILL.md` frontmatter, use [../agents-skills/SKILL.md](../agents-skills/SKILL.md).

## Quick Reference

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

| Decision | Default |
|----------|---------|
| Need one universal entry point for agents, teams, and debates | Use this skill first |
| Need help choosing the correct agent or team for a scenario | Use this skill to classify the task before launching anything |
| Need a clean first prompt to start a team or debate | Use this skill to draft the launch prompt with context, ownership, synthesis rules, and cleanup expectations |
| Built an app/product but do not know how to penetrate the market or get serious users | Run `expert-board` in `growth` mode with the [market-penetration workflow contract](references/workflow-contracts.md#market-penetration-review) |
| One bounded task with a clear output | Use a built-in or custom subagent |
| Existing long-lived Claude sessions need a direct handoff | Use cross-session messaging. Use Agent Teams only when teammates need a shared task list and self-claiming; Codex remains parent-led unless the active surface exposes peer messaging |
| Need specialists to argue before choosing a direction | Prefer a debate-enabled team with explicit triggers; skip debate when disagreement is unlikely |
| Need parallel edits on separate files | Use `isolation: worktree` for Claude **subagents**; Agent Team teammates share the lead checkout. With agent teams enabled, pass `isolation` on the Agent call itself (frontmatter alone is ignored) to launch a worktree-isolated subagent instead of a teammate. On Codex, assign owned files explicitly |
| Several independent tasks to hand off and check back on later | Third surface: **background sessions** (agent view, `/bg`, `claude --bg`); each isolates itself in a git worktree before editing. Mechanics: [references/runtime-surfaces.md](references/runtime-surfaces.md) §"Background sessions and routines" |
| Runtime surfaces, field matrix, or built-in subagent list | [references/runtime-surfaces.md](references/runtime-surfaces.md) + [../agents-swarm-orchestration/references/platform-patterns.md](../agents-swarm-orchestration/references/platform-patterns.md) |
| Long-running, hosted agent where the operator is not at a terminal (inbox triage, scheduled research, document processing) | Try Claude Code **routines** (`/schedule`) before building a harness. Scope tools as if no approval prompt exists, prune connectors to the ones the routine needs, and make the saved prompt treat the fire payload as untrusted data. Mechanics and the Claude Managed Agents escalation: [references/runtime-surfaces.md](references/runtime-surfaces.md) §"Background sessions and routines" |
| Agent-file fields | The catalog sets `name`, `description`, `tools`/`disallowedTools`, `maxTurns`, `model`, `effort`, `skills`, and (implementer-class only) `permissionMode` / `isolation`. Worth adopting: `color` (distinguishes concurrent rows), `experimental.cacheTtl`, and opt-in `memory` (it grants file-edit capability for the memory directory). `mcpServers`, `hooks`, `background`, and `initialPrompt` stay deliberately unset. Check field support for the running version in [references/agent-tools.md](references/agent-tools.md); template: [agents/templates/member-claude.md.template](../../../agents/templates/member-claude.md.template) |
| Need the caller to use a subagent's result before continuing | Foreground vs background differs by session mode (interactive, fork mode, `-p`, Agent SDK) and has changed between releases, so never rely on a default. Before a step that consumes the result, determine whether this session backgrounds subagents (docs for the running version plus the [runtime smoke test](references/runtime-smoke-tests.md)); if it does, force the foreground where a lever exists or wait explicitly for the completion notification. The same definition can resolve to a different tool set in the background. Levers: [references/agent-tools.md](references/agent-tools.md) §"background"; blocking forked skills: [references/skill-subagent-patterns.md](references/skill-subagent-patterns.md) |
| Repeatable fan-out, deterministic loops, or verify stages | Claude: use the saved Workflows in [agents/workflows/](../../../agents/workflows/), synced to `~/.claude/workflows/`. Runtime controls, caps, and the `agent()` option surface: [references/workflow-runtime.md](references/workflow-runtime.md). Codex: run the `run-workflow` skill, which executes the generated `<id>.codex-plan.json` with spawn/wait/follow-up from the parent session; every workflow except the `validate-library` command has one. A plan is an adapter, not a native saved workflow. Both resolve the same manifest and named-member roster |
| About to hand-edit a saved workflow script | Run the bundled `/workflow-authoring` skill first. Keep `export const meta` the first statement and a plain object literal with `name` and `description`, or `/<name>` drops out of `/` autocomplete; a script containing `import()` fails before the run starts. Read the current concurrency, per-call item, and per-run agent limits in [references/workflow-runtime.md](references/workflow-runtime.md) §"Runtime caps" before sizing |
| Skill ↔ subagent delegation (`skills:` preload, `context: fork`) | [references/skill-subagent-patterns.md](references/skill-subagent-patterns.md) |
| Team/member/debate scenarios, prompts, and installation | [references/team-selection-guide.md](references/team-selection-guide.md), [references/team-scenarios.md](references/team-scenarios.md), [references/team-prompt-patterns.md](references/team-prompt-patterns.md) |
| Refresh only existing installer-owned members after policy/template changes | Preview with `scripts/deploy-all-teams.sh --refresh-installed-managed --platform both --user --dry-run`; real writes additionally require `--confirm-bulk-deploy`. Missing, modified, unowned, or unsafe files are never adopted or overwritten |
| Visual team diagrams (Mermaid flowchart per team, auto-generated from manifests) | [references/team-diagrams.md](references/team-diagrams.md) — regenerate with `python3 scripts/generate-team-diagrams.py` |
| Validate a new niche or greenfield opportunity | See [references/team-selection-guide.md](references/team-selection-guide.md) §"Niche Validation" for repo-specific team mapping |
| Live product needs market entry or a growth plan | Run `expert-board` in `growth` mode — see [references/workflow-contracts.md](references/workflow-contracts.md) |
| Debate, topology, decision masks, context, cost, and governance details | [references/navigation-index.md](references/navigation-index.md) |

Long-tail scenario rows (coverage map, lifecycle, smoke tests, system diagrams) are indexed in [references/team-coverage.md](references/team-coverage.md); the member/team inventory lives in [references/team-member-matrix.md](references/team-member-matrix.md).

## Runtime Terminology Firewall

- **Native Claude:** subagent definition, subagent, Agent Team, teammate, live team state.
- **Native Codex:** custom agent, subagent workflow, agent thread.
- **Repository-only:** member, team recipe, `team.yaml`, debate overlay, workflow contract, `family` metadata.

With `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, any subagent Claude *names* launches as a teammate, so a team can form during ordinary named-member delegation nobody framed as team work: set the variable to `0` in user `settings.json` to keep named members as subagents (it is re-read on each spawn, so no restart is needed; higher-precedence project/local/managed settings can still re-enable it).

Never call `team.yaml` a native runtime manifest. Installing a recipe installs native member definitions and stores launcher metadata; the runtime does not discover the YAML itself.

## When Not To Use

- Plan execution across multiple waves or resolve merge conflicts between many workers → [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md)
- Design `SKILL.md` files, skill packaging, or skill frontmatter → [../agents-skills/SKILL.md](../agents-skills/SKILL.md)
- Build hooks or MCP servers themselves → [../agents-hooks/SKILL.md](../agents-hooks/SKILL.md), [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md)
- One-off task the parent thread can finish in a few turns without delegation

## Workflow

1. Apply the canonical routing ladder in [Scenario Selection Rule](#scenario-selection-rule).
2. Inventory installed global/plugin and project agents before creating one: `~/.claude/agents/`, `.claude/agents/`, `~/.codex/agents/`, `.codex/agents/`.
3. Choose the runtime target and define tool, MCP, isolation, and context-artifact boundaries. Record the actual startup mode as `fresh`, `forked`, or `runtime-defined`; never infer transcript, skill, memory, or permission inheritance from the word “subagent.”
4. For a team or debate, map the scenario with [team-selection-guide.md](references/team-selection-guide.md), then choose the sequence with [universal-team-playbook.md](references/universal-team-playbook.md).
5. Draft the launch contract: goal, required and optional context, ownership, execution mode, context-start mode, debate trigger, synthesis owner, evidence, and cleanup.
6. Run the applicable [runtime smoke tests](references/runtime-smoke-tests.md) when repository validation is not enough.

## Fan-Out and Verification

- Do not delegate work the main thread can finish in a few tool calls.
- Avoid generic self-verification instructions; use a named clean-context verifier only for hard-to-reverse decisions.
- Preserve single-writer ownership even when runtime coordination improves.

Model-generation behavior traps and the MAST failure taxonomy live in [references/traps-and-antipatterns.md](references/traps-and-antipatterns.md) and [references/mast-failure-taxonomy.md](references/mast-failure-taxonomy.md).

## Traps and Anti-Patterns

The load-bearing failure modes (trusting tool output as instructions, accepting "done" without evidence, context rot well before the window is full, MCP token bloat in the parent, stale agent files after runtime upgrade, approval fatigue, duplicating sibling-skill patterns) live in [references/traps-and-antipatterns.md](references/traps-and-antipatterns.md). Consult it before launching a worker or team, and when reviewing an existing agent.

Re-audit agent files after runtime upgrades; recursion, background execution, field support, and model defaults are not portable invariants. Use [references/runtime-surfaces.md](references/runtime-surfaces.md), [references/agent-tools.md](references/agent-tools.md), and [references/model-governance-and-maintenance.md](references/model-governance-and-maintenance.md).

## Relationship To Swarm Orchestration

Use this skill first.

- Use `agents-subagents` to select the correct global agent, repo-local agent, shared member, shared team, or debate mode.
- Use `agents-subagents` to prepare the initial launch prompt and context contract.
- Switch to [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md) only when the plan requires multi-wave fan-out, worker dependencies, verifier passes, or merge/conflict coordination.

Simple rule:
- `agents-subagents` = what to run
- `agents-swarm-orchestration` = how to run many workers safely

## Scenario Selection Rule

When the user gives a scenario, this skill should help choose the smallest correct mode.

Use this routing ladder in order; stop at the first sufficient surface:

1. Stay in the **main thread** when it can finish the work in a few tool calls or when the task depends heavily on the live conversation.
2. Use a **built-in subagent** (`Explore`, `Plan`, `general-purpose` on Claude Code; `default`, `worker`, `explorer` on Codex) when a generic research, planning, or implementation worker fits.
3. Use a **global or plugin-provided agent** when one installed specialist fits cleanly.
4. Use a **repo-local agent** for repository conventions or a temporary override; use a **shared member** for a reusable specialist.
5. Use a saved **Workflow** for repeatable scripted fan-out with known control flow and no peer-coordination requirement. Size it with the smallest tier that covers the fan-out; read the current tier limits and concurrency cap in the workflows docs or `/config` before choosing. The surface can be plan-gated or disabled by the organization, a *new* workflow needs an explicit opt-in, and `claude -p` / Agent SDK launches need a `Workflow` or `Workflow(<name>)` allow rule because no approval prompt is ever shown. Details and the `/workflow-authoring` rules: [references/workflow-runtime.md](references/workflow-runtime.md).
6. Only now check [references/team-selection-guide.md](references/team-selection-guide.md) and [references/team-scenarios.md](references/team-scenarios.md). Use a **shared team** when multiple specialists need distinct outputs or direct coordination.
7. Use a **debate-enabled team** or **debate overlay** only when disagreement, challenge, and synthesis create the value.

Greenfield niche discovery ("should I build X in niche Y") reaches step 5 as `expert-board` in `founder-blindspot` mode; fill the required context and demand the scorecard output listed in [references/team-selection-guide.md](references/team-selection-guide.md#niche-validation) so members return canonical startup artifacts instead of narrative lenses.

If multiple teams could fit, prefer the one whose output contract matches the user request most directly.

## Runtime Surfaces

Runtime detail lives in references so the skill stays lean:

- [references/runtime-surfaces.md](references/runtime-surfaces.md) — Claude Code paths, Codex `.toml` format, field mapping, cross-platform rules, session-scoped `--agents`, whole-session `--agent <name>`, plugin precedence, Claude Agent SDK, OpenAI Agents SDK.
- [../agents-swarm-orchestration/references/platform-patterns.md](../agents-swarm-orchestration/references/platform-patterns.md) — field matrix, built-in subagent table, agent-teams availability (experimental, env-gated by `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), Codex multi-agent model examples, OpenAI Agents SDK manager/handoff.

The main difference between Claude and Codex is orchestration, not role design:
- Claude can support direct teammate collaboration where runtime agent-teams are enabled.
- Codex uses spawn, follow-up, wait, and synthesis primitives. Delegation may follow a direct user request or applicable `AGENTS.md`/skill policy; do not require the user to type a spawn command when policy already requests delegation.
- Both should reuse the same context-first inputs, team selection logic, and initial prompt contract.

Platform-specific settings are runtime-scoped, not portable defaults. The authoritative field matrix lives in [../agents-swarm-orchestration/references/platform-patterns.md](../agents-swarm-orchestration/references/platform-patterns.md) — refresh there first.

## Initial Prompt Contract

This skill owns the first launch prompt. Use the 8-field contract in [references/initial-prompt-contract.md](references/initial-prompt-contract.md), keep each child budget below the parent's remaining budget, and make the brief executable without the parent transcript. For retrieval workers, pass the objective, judge each return, and stop after a bounded number of follow-ups ([retrieval follow-ups](references/initial-prompt-contract.md#retrieval-follow-ups)). Reusable prompts and scenarios live in [references/team-prompt-patterns.md](references/team-prompt-patterns.md) and [references/team-scenarios.md](references/team-scenarios.md).

## Shared Members and Teams

Canonical members live in `agents/`; `agents/teams/*/team.yaml` composes them as repository metadata, not runtime configuration. Install persistent members when their native model, tools, or skill bindings matter. Workflows dispatch those named members first and use embedded role briefs only when the active runtime reports that named-agent selection is unavailable. Full rules: [references/members-and-teams.md](references/members-and-teams.md) and [references/team-lifecycle.md](references/team-lifecycle.md).

Codex installs materialize managed TOMLs with model tier, `[[skills.config]]`, and rewritten links at every scope. Delegation still requires the user or applicable `AGENTS.md`/skill policy. Verify named-agent support on the active Codex surface before depending on it.

## Shared Context Pattern

For engineering packs, prefer shared artifacts over repeated cold reads. Every subagent starts with a **self-contained brief**, not the parent's transcript — this is a current operating rule.

Full pattern (fresh-context principle, preferred inputs from `dev-context-*` skills, default handoff order, discovery rule): [references/context-first-protocol.md](references/context-first-protocol.md).

## Current Runtime Model

Working rules not already captured by the routing ladder:
- prefer clean-context helper roles for review, verification, and scoped research; do not default those roles to persistent memory
- keep write ownership single-threaded unless files and interfaces are isolated
- treat isolation, skill wiring, saved workflows, and peer communication as runtime-specific capabilities
- keep the standing roster small; install team core members by default and expansion candidates only with an intentional `--include-candidates`
- use generic role briefs only for ephemeral work or explicit named-agent unavailability

For debates specifically, existing domain agents are usually better participants than generic wrappers because they already carry the right role identity and skill context.

## Agent File Fields and Frontmatter

Claude Code agent files are markdown with YAML frontmatter. Codex agents are `.toml` with similar fields under different names.

Field reference and selection rules live in [references/agent-tools.md](references/agent-tools.md) (tool allow-lists, `permissionMode`, `maxTurns`, `mcpServers`, `memory`, `background`, `isolation`, Codex `sandbox_mode` mapping, and the full anti-pattern list).

Two owners, split by question so they cannot contradict each other. [../agents-swarm-orchestration/references/platform-patterns.md](../agents-swarm-orchestration/references/platform-patterns.md) owns **field shapes**: which fields exist, their accepted values, `skills`/`hooks`/`initialPrompt`/`color`, plugin-agent restrictions, and the `CLAUDE_CODE_SUBAGENT_MODEL` resolution order. [references/cost-control.md](references/cost-control.md) owns **`effort` and cost**: which levers to pull and how to look up the per-model default. Where platform-patterns quotes an effort default, cost-control wins.

Safe defaults:
- Prefer `tools` allow-list over broad inheritance; use either `tools` or `disallowedTools` for general scoping, not both. When both are set, `disallowedTools` is applied first and `tools` resolves against the remaining pool, so a tool named in both is removed. One sanctioned exception: leaf roles add `disallowedTools: [Agent]` alongside their allow-list, per §Traps — spawn denial is a policy statement, not tool scoping, and must not depend on the allowlist's inheritance behavior.
- Keep `maxTurns` low for reviewer and research agents.
- Treat `memory` as opt-in — it automatically grants file-edit capability for the memory directory.
- Scope `mcpServers` to the one worker that needs it. A `stdio` server turns its launch config into an OS command by design (CVE-2026-30623 was one 2026 instance): never wire a worker to a `stdio` server whose launch config derives from model or tool output; sandbox the host.
- Use `isolation: worktree` for parallel or risky **subagent** edits on Claude Code. Agent Team teammates do not receive worktree isolation and share the lead checkout, even when spawned from a definition that declares `isolation`. When agent teams are enabled, passing `isolation` on the Agent call itself (or forking) launches a subagent rather than a teammate, so the worktree applies (sub-agents docs, checked 2026-09-27).
- Check the worktree base before fan-out: an isolated worktree may start from the default branch, not the parent's `HEAD`. Commit (and push if needed) the parent state or set the base to `HEAD`, then confirm each worker's base SHA equals the parent `HEAD`; otherwise workers silently miss unpushed work. Details: [references/agent-tools.md](references/agent-tools.md) §"isolation".

## Skill ↔ Subagent Delegation

Skills and subagents can reference each other in two directions:

- **Role pattern**: a subagent preloads skills with `skills:` in agent frontmatter, so the role always starts with the same domain context.
- **Task pattern**: a skill spawns a subagent with `context: fork` + `agent: <type>`, so the skill body becomes the task prompt and the subagent runs in isolation.

Full selection guide, constraints, and examples: [references/skill-subagent-patterns.md](references/skill-subagent-patterns.md).

## Forking Parent Context Into Subagents

By default, a Claude Code subagent starts with a blank context. With agent view enabled, `/subtask` creates a background subagent from the current context; `/fork` instead copies the whole session into a separate background session. Anthropic documents prompt-cache reuse for forked context but does not promise a fixed cost multiplier.

Default to blank context. Fork only when you can name the understanding the parent has built that the subagent needs and cannot cheaply recompute. Reviewers and verifiers should always start blank. Forking can leak parent secrets; audit allowed tools before forking.

Full operating rules and the built-in `Explore`/`Plan` flow: [references/subagent-context-forking.md](references/subagent-context-forking.md). Known model-pin issue for forked skills: [references/skill-subagent-patterns.md](references/skill-subagent-patterns.md). Session-lifecycle implications: [`../ai-coding-agents-state/references/context-forking.md`](../ai-coding-agents-state/references/context-forking.md). Command-runtime implications: [`../ai-coding-agents-runtime-core/references/command-dispatch-forking-and-remote-safety.md`](../ai-coding-agents-runtime-core/references/command-dispatch-forking-and-remote-safety.md).

## Decompose by Context, Not Role

Split by **context boundaries**, not role labels. If two tasks share deep context, keep them in the same agent. Decomposing by planner/developer/tester creates context loss at every handoff. One exception: a subagent runs to completion and cannot pause mid-run for the user to approve a plan, so when the user must sign off before implementation, either plan in the main thread or have the subagent return the plan and stop; write the approved plan to a file and pass that file to the implementer and the reviewer. Full framing and architecture decision guide: [references/subagents-vs-teams-architecture.md](references/subagents-vs-teams-architecture.md).

## When a Single Strong Agent Beats a Team

Apply two results as a pre-team gate:

- **Token-Budget Equivalence Rule** — at equal token budget, default to one strong agent: a single agent matches or beats multi-agent on multi-hop reasoning *while it can use its context effectively* (Data Processing Inequality; Tran & Kiela, 2026, arXiv:2604.02460). Switch to a team only when the working context exceeds what one agent can use effectively, or when subtasks are context-disjoint — not because the task has several roles.
- **Expert-Leveraging Gap** — self-organizing teams underperformed their single best member on the reported benchmarks, which the authors attribute to "integrative compromise": consensus-seeking that averages expert and non-expert views instead of weighting expertise. Prefer a single agent when one specialist holds clear expertise (arXiv:2602.01011, 2026).

Both preprints are not peer-reviewed; scope is text-only and self-organizing teams respectively. Full analysis and "when NOT to use multi-agent" rules: [references/subagents-vs-teams-architecture.md](references/subagents-vs-teams-architecture.md).

## Description Writing Rules

Use `[What it does]. Use when [concrete triggers, artifacts, or task shapes]. Produces [output]; does not [boundary].` Write `Use proactively when` only for roles the runtime should self-trigger without a routing decision (reviewers, verifiers). Routed catalog members are dispatched by a lead or workflow, so the plain form is the convention there. Name the responsibility and boundary; avoid generic helper descriptions. Detailed patterns and trigger evaluation: [references/agent-patterns.md](references/agent-patterns.md).

## Design Checklist

Before launch, confirm one responsibility, concrete triggers, minimal tools/MCP, bounded turns, explicit output, owned files, an explicit context-start mode, and runtime-appropriate isolation. Use [references/agent-patterns.md](references/agent-patterns.md) and [references/initial-prompt-contract.md](references/initial-prompt-contract.md) for the full checklist.

## Recommended Patterns

- Reviewer/researcher: read-heavy, bounded, evidence-first.
- Implementer: owned files, verification command, no unrelated cleanup.
- Debate: 2-4 independent perspectives plus a synthesis owner.
- Engineering delivery: prepare shared context artifacts before parallel work.

Start from `agents/templates/` and [references/agent-patterns.md](references/agent-patterns.md).

## Harness Architecture Patterns

Use [references/harness-patterns.md](references/harness-patterns.md) for orchestrator-worker, evaluator-optimizer, planner-generator-evaluator, manager/handoff, reflection, debate, and blueprint selection. Multi-wave voting and hierarchical swarms belong to [agents-swarm-orchestration](../agents-swarm-orchestration/SKILL.md). Cap retries and escalate capability at the cap.

## Resources

Full categorized list of references, templates, members, teams, scripts, and sources: [references/navigation-index.md](references/navigation-index.md).

Most-used entry points:

- Decision: [references/team-selection-guide.md](references/team-selection-guide.md)
- Launch: [references/team-prompt-patterns.md](references/team-prompt-patterns.md) + [references/initial-prompt-contract.md](references/initial-prompt-contract.md)
- Runtime: [references/runtime-surfaces.md](references/runtime-surfaces.md) + [references/agent-tools.md](references/agent-tools.md)
- Cost: [references/cost-control.md](references/cost-control.md) + [references/model-governance-and-maintenance.md](references/model-governance-and-maintenance.md)
- Traps: [references/traps-and-antipatterns.md](references/traps-and-antipatterns.md)
- Templates: [agents/templates/](../../../agents/templates/)
- Sources: [data/sources.json](data/sources.json)

Other references (load the one whose decision is open):

- Directory entry and frontmatter conventions: [references/README.md](references/README.md)
- Team protocols: [clarification questions](references/clarification-questions-protocol.md), [debate quickstart](references/debate-quickstart.md), [dynamic team expansion](references/dynamic-team-expansion.md), [negotiation (ZOPA/BATNA)](references/negotiation-protocol.md), [prediction-market confidence betting](references/prediction-market-confidence.md)
- Review cycles: [multi-agent reflexion](references/multi-agent-reflexion.md), [OODA loop review cycles](references/ooda-loop-team-cycles.md), [purple team (continuous red+blue)](references/purple-team-pattern.md)
- Memory and context: [shared context pattern](references/shared-context-pattern.md), [subagent interruption recovery](references/subagent-interruption-recovery.md)
- Design rationale: [team design rationale](references/team-design-rationale.md), [principal-agent delegation](references/principal-agent-delegation.md), [methods, masks and mechanisms playbook](references/methods-masks-mechanisms-playbook.md)
- Diagrams: [runtime topology](references/runtime-topology-diagram.md), [startup growth system](references/startup-growth-system-diagram.md)
- Team scenario playbooks ([index](references/team-scenarios/README.md)):
  - Engineering: [AI knowledge bot builder](references/team-scenarios/ai-knowledge-bot-builder.md), [AI systems](references/team-scenarios/ai-systems.md), [architecture RFC](references/team-scenarios/architecture-rfc.md), [code review](references/team-scenarios/code-review.md), [context engineering](references/team-scenarios/context-engineering.md), [feature dev](references/team-scenarios/feature-dev.md), [migration map](references/team-scenarios/migration-map.md)
  - Data and docs: [data analytics](references/team-scenarios/data-analytics.md), [data science](references/team-scenarios/data-science.md), [docs knowledge](references/team-scenarios/docs-knowledge.md)
  - Operations and release: [incident response](references/team-scenarios/incident-response.md), [ops platform](references/team-scenarios/ops-platform.md), [payments platform](references/team-scenarios/payments-platform.md), [release readiness](references/team-scenarios/release-readiness.md), [enterprise readiness](references/team-scenarios/enterprise-readiness.md)
  - Product and growth: [product discovery](references/team-scenarios/product-discovery.md), [product surface](references/team-scenarios/product-surface.md), [mobile product](references/team-scenarios/mobile-product.md), [growth experiment](references/team-scenarios/growth-experiment.md), [marketing diagnostics](references/team-scenarios/marketing-diagnostics.md)
  - Startup boards: [founder blindspot](references/team-scenarios/startup-founder-blindspot-board.md), [growth](references/team-scenarios/startup-growth-board.md), [monetization](references/team-scenarios/startup-monetization-board.md), [strategy](references/team-scenarios/startup-strategy.md), esoteric consumer-product founding team

## Related Skills

- [../agents-swarm-orchestration/SKILL.md](../agents-swarm-orchestration/SKILL.md) - Parallel execution, waves, and conflict resolution
- [../agents-skills/SKILL.md](../agents-skills/SKILL.md) - Skill packaging and `SKILL.md` conventions
- [../agents-hooks/SKILL.md](../agents-hooks/SKILL.md) - Hook guardrails and lifecycle automation
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) - MCP server design and security
- [../agents-memory/SKILL.md](../agents-memory/SKILL.md) - Project memory strategy for shared conventions
- [../ai-agents/SKILL.md](../ai-agents/SKILL.md) - Agent SDK patterns, context rotation, and principal-agent theory referenced throughout this skill's references

## Navigation

Full categorized map: [references/navigation-index.md](references/navigation-index.md).

Use a foundation only when its returned artifact resolves a specific orchestration decision; skip theory expansion for routine independent delegation.

- [Planning/search](../foundations-ai-planning-search/SKILL.md) — Load for interacting action preconditions, effects, dependencies, or resource conflicts. Return the initial/goal state, action contract, resource bounds, and replayable valid plan or explicit infeasibility; a task list alone is insufficient.
- [Formal methods](../foundations-formal-methods/SKILL.md) — Load for a concrete handoff, cancellation, lease, or retry protocol whose invariant needs checking. Return invariant, finite model boundary, and counterexample or bounded result. A graph check proves neither implementation conformance nor liveness.
- [Mathematical optimization](../foundations-mathematical-optimization/SKILL.md) — Load when assignment/concurrency choices have explicit competing objectives and binding constraints. Return variables, objective, constraints, feasible candidate, and certificate/solver limits. Use a simple ownership-aware allocation for routine fan-out; do not invent objective weights.
- Theory-applied references — load one only when its named decision is open (topic labels in [navigation-index.md](references/navigation-index.md#theory-layers-foundations-applied)): [control](references/control-theory-applied.md), [queueing](references/queueing-theory-applied.md), [distributed systems](references/distributed-systems-applied.md), [cybernetics/VSM](references/cybernetics-vsm-applied.md), [network science](references/network-science-applied.md), [decision theory](references/decision-theory-applied.md), [theory of constraints](references/theory-of-constraints-applied.md), [behavioral economics](references/behavioral-economics-applied.md), [team theory](references/team-theory-applied.md), [grounding](references/grounding-communication-applied.md), [game theory](references/game-theory-agent-teams.md).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
