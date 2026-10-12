---
description: How to add a saved workflow to the library: pick an engine, write the manifest that binds a team, generate, test, sync.
last_verified: 2026-10-10
status: stable
---

# Add a Workflow

A library workflow is three files in `agents/workflows/`: `<id>.manifest.json` (hand-written), `<id>.js` (generated, the Claude Code saved workflow) and `<id>.codex-plan.json` (generated, the plan a Codex parent thread follows by hand). You write the manifest only. The generator, `skills/universal/agents-subagents/scripts/generate_workflows.py`, validates it and renders the other two; every rule below is one it enforces, so a wrong manifest fails at generation, not at run time.

Build order for a hive: members first (`agents/templates/README.md`), then the team recipe in `agents/teams/<team>/team.yaml`, then the manifest that binds the team. A manifest can only name members the bound team lists.

## 1. Pick the engine

| Engine | Shape | Exemplar | Codex plan |
|---|---|---|---|
| `review` | Parallel reviewers per dimension, refuters per finding, optional fix loop with fresh agents each round | `source-check`, `adversarial-review` (no loop) | yes |
| `staged` | Ordered stages with a gate each; writers run one at a time; a stage may embed a review loop | `feature-delivery`, `marketing-campaign` | yes |
| `waves` | A planner splits an epic into tasks, then delivers them in dependency waves, each through a staged pipeline | `epic-delivery` | yes |
| `department` | GC triage, blind specialist memos by lane, citation check, synthesis | client-specific workflow | yes |
| `board` | Blind panel memos, optional challenge, chaired synthesis; many boards in one manifest | `expert-board` | yes |
| `command` | Runs one shell command with enumerated options; no agents | `validate-library` | no |

Default to `review` for "check X and fix the confirmed defects" and `staged` for "produce X through gated steps". Use `waves` only when one run must deliver several independently owned tasks. Copy the exemplar manifest and change it; do not start from an empty file. Evidence for these defaults is in `audit/hive-pdlc-research-2026-10-10/REPORT.md` section 1.

## 2. Write the manifest

Every manifest has `version` and a `workflow` block: `engine`, `description`, `whenToUse` (the args contract the user reads), `phases` (titles the runtime calls, in order) and `codex: "parent-led"` when Codex should get a plan. `max_agents` caps fan-out.

Engine blocks and what the generator refuses:

- **review**: `review.dimensions`, each with `name` and `brief`; `review.refuters` of 1 or more; an optional nonblank `review.refuter_model` is the Agent tool's model override for refuter calls only in the Claude saved workflow, while a Codex plan is parent-led and cannot mix vendors, so its plan file records `refuter_model` as "same vendor" and the parent uses its own model; `review.rules` containing the `{target_note}` placeholder; `review.schemas.review` and `review.schemas.refute`. `review.extends: "<id>"` inherits another manifest's block, local keys override. A `loop` block needs `modes` exactly `review` and `build`, a `default_mode`, and positive `max_rounds_default` and `plateau_rounds`; an optional nonblank `loop.test_command` is the default command that gates a build pass (`args.testCommand` overrides it), and a build run with `args.frozen` or hidden checks and no command stops `INCOMPLETE`, `no_test_command`; an optional `loop.hidden_checks` (or `args.hiddenChecks`, which overrides it) is an array of tracked test files the runtime removes from the tree before the first builder and runs only after the visible command passes (`hidden_check_failed`, `hidden_unknown`); they must be tracked in git, so a killed run is recovered with `git show HEAD:<path> > <path>`, never a path checkout. Hidden checks are hidden from the builder's brief and working tree, not from a builder that searches the temp directory or git history; a builder that does so commits a protocol breach, not a defeated control. Phases are then `Review, Verify, Fix, Build, Judge`, otherwise `Review, Verify`.
- **staged**: `bindings.<key>.team` names a team; every stage member must be a member or candidate of that team. Each stage has a unique `id`, a `binding`, a `title`, `members` (or `team_stage` from the team's `execution_stages`), a `task`, an output `schema` and a `gate`. A writing stage sets `parallel: false` and its members need an `Edit` or `Write` tool. A loop stage names `mode` and `max`; a build loop also needs `for_each` over an earlier stage. `staged.pass_verdict` and gate verdicts must be in the team's `verdict_options`.
- **department**: `department.guardrails`, `memo_sections`, `fallback_binding` and `hold_policy` (`verdict`, `default_deadline_days`, `escalate_on_deadline`, equal to the team's). Each binding names a `team`, a `gc` (member id or null) and `lanes`: one dispatch brief per roster member and candidate, no extras. Phases are `Triage, Memos, Verify, Synthesize, Baseline`.
- **board**: `boards.<key>` (alias `bindings`) names a `team` or lists `members`, `candidates`, `verdicts`, `max_dynamic_members` and `algedonic`; `defaults.member_execution` sets the panel's run mode.
- **command**: `command.run` and `command.options`, each option's `default` among its `choices`; exactly one phase.

When a binding names a team, the generator reads members, candidates, verdicts and the expansion cap from `team.yaml`; a field set on the binding overrides the team. An unknown team or member is an error.

## 3. Generate, test, sync

From the repository root:

```bash
python3 skills/universal/agents-subagents/scripts/generate_workflows.py
python3 skills/universal/agents-subagents/scripts/generate_workflows.py --check
node agents/workflows/test-saved-workflows.mjs
python3 -m unittest discover -s skills/universal/agents-subagents/scripts -p 'test_*.py'
```

`--check` fails when any generated file is stale, and the pre-commit hook runs it. The workflow test also compares manifest rosters with team recipes, so a renamed member fails here rather than at launch. Never hand-edit the `.js` or the `.codex-plan.json`; a runtime bug belongs in `scripts/<engine>_runtime.js`, then regenerate.

`scripts/distribution/sync-skills.sh` links the `.js` files into `~/.claude/workflows/`, where Claude Code lists them as `/<id>`. Codex has no workflow runtime: the parent thread reads the `.codex-plan.json` and runs it with `spawn_agent` and `wait_agent` (see [workflow-contracts.md](workflow-contracts.md)).

## 4. Register

Add the workflow to the router scenario that owns the task (a `**Run:**` line, as K19 does for `/epic-delivery`), to the teams README mapping when it replaces install recipes, and regenerate the graph with `python3 scripts/graph-export.py`. Commit the manifest, both generated files and the graph together.
