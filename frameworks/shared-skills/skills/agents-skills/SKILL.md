---
name: agents-skills
description: Creates and audits agent skills with SKILL.md, references, scripts, and platform-scoped metadata. Use when creating, updating, or validating shared skills.
version: "1.1"
last_validated: 2026-08-15
---

# Agent Skills

Use this skill to create or modernize skill bundles without conflating the portable core contract with runtime-specific extensions.

> **Scope — this is a delta on the standard, not a replacement.** Generic skill authoring, scaffolding, and eval mechanics are owned by the [Agent Skills open spec](https://agentskills.io/specification) and the standard `skill-creator` skill (and `plugin-dev:skill-development`). Use those for boilerplate. This skill owns only the repo-specific delta the standard cannot provide: dual-runtime portability (Claude Code + Codex), catalog/graph gating, and router/composition patterns. Do not replicate the standard here — link to it.

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Scaffold a new skill | `skill-creator` (standard skill) | Generates the boilerplate; then apply portability discipline from `references/frontmatter-reference.md` |
| Modernize an existing skill | `python3 scripts/validate_skill.py <skill-dir>` | Finds contract drift, broken links, stale sources, and missing TOCs |
| Add runtime-specific metadata | `references/frontmatter-reference.md` | Scopes extensions to the target runtime instead of treating them as universal |
| Decide how to split content | `references/skill-patterns.md` | Keeps `SKILL.md` small and moves detail into `references/` or `scripts/` |
| Validate behavior, not just syntax | `references/skill-validation.md` | Builds trigger, non-trigger, and navigation evals |
| Check Anthropic-specific details | `references/anthropic-skills-guide.md` | Uses Anthropic guidance without treating it as the portable baseline |
| Ship one skill to multiple runtimes without drift | `references/dual-distribution.md` | Single canonical system prompt + wrapper distributions + drift-check gate |
| Design router/composable skill flow | `references/skill-patterns.md#pattern-10-stage-based-selection-pipeline` | Separates sources, enrichment, filters, scoring, selection, validation, and side effects |

## Core Contract

Portable baseline:

- `skill-name/SKILL.md` is required.
- `name` and `description` are the portable required frontmatter fields.
- `license`, `compatibility`, and `metadata` are portable optional fields in the open spec.
- `allowed-tools` is part of the open spec, but implementation support may vary by runtime.
- `references/`, `scripts/`, `assets/`, and `data/sources.json` are optional support directories.
- Keep the main skill body focused on workflow and navigation; move long detail into support files.

Runtime extensions:

- Treat fields such as `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `when_to_use`, `context`, `agent`, `model`, `effort`, `hooks`, `paths`, `shell`, and `disallowed-tools` as runtime-specific until verified in that runtime's current official docs.
- In Anthropic runtimes, also verify invocation semantics and substitutions before copying examples: `user-invocable`, `disable-model-invocation`, `$ARGUMENTS`, `$name` (from `arguments`), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, and `${CLAUDE_PROJECT_DIR}` are not portable assumptions.
- If you use runtime-specific fields, add a scoped `compatibility` note naming the target runtime.
- A skill that uses runtime-specific headers (`argument-hint`, `arguments`, `disable-model-invocation`, `context`, `agent`, `model`, `effort`, `hooks`, `paths`, `shell`, `disallowed-tools`) is runtime-scoped: add a `compatibility` note naming the target runtime and remove any claim of portability.
- Even portable-baseline fields carry a nuance worth catching: the open spec requires `name` and `description`, but Claude Code alone treats every frontmatter field (including those two) as optional and falls back to the directory name for display. Keep setting both explicitly — the portable contract is stricter than any single runtime's tolerance.

Repo-local Codex metadata:

- Treat `agents/openai.yaml` as adjunct metadata, not as part of the portable core.
- Keep `SKILL.md` `description` trigger-rich and portable.
- Keep `agents/openai.yaml` `short_description` brief enough for UI surfaces.
- Keep `agents/openai.yaml` `default_prompt` focused on when Codex should load the skill.
- Revalidate semantic alignment when the skill intent changes; do not require exact string equality between these fields.

## Authoring Modes

Shared skills in this repo should default to a **functional reference** style:

- matter-of-fact
- outcome-oriented
- explicit about inputs, outputs, and navigation
- light on persona, coaching voice, or motivational framing

That is the safest portable baseline across runtimes, especially for Codex-style skill loading.

Some runtimes also benefit from a **problem-approach overlay**:

- how to think about the task
- ambiguity-handling rules
- coaching or teaching tone
- richer behavioral framing

Use that style only in runtime-specific layers, references, or scoped extensions. Do not let the portable core become a blend of incompatible authoring philosophies.

## Workflow

1. Start with 2-3 concrete user tasks and write the evals first.
2. Draft the portable core: folder name, `SKILL.md`, `name`, `description`, and minimal instructions.
3. Keep the portable core functional and reference-like unless the runtime explicitly benefits from a richer overlay.
4. Add runtime-specific metadata only after choosing the target runtime.
5. Put reusable detail in `references/`, deterministic helpers in `scripts/`, and output templates in `assets/`.
6. Run static validation before review: links, frontmatter, TOCs, and `sources.json`.
7. Run behavioral evals: trigger, non-trigger, navigation, and runtime-specific checks.
8. Observe real usage and iterate based on under-triggering, over-triggering, or poor file navigation.
9. For engineering and debugging-oriented skills, explicitly require verification of known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance against current primary web sources before treating them as current fact.
10. For routers, teams, and composable skills, model the workflow as a stage-based selection pipeline: gather candidates, enrich them, filter ineligible options with reasons, score remaining options independently, select the smallest correct output, run post-selection validation, then keep learning/eval updates as side effects.
11. When discovery / routing structure changes, regenerate `frameworks/shared-skills/graph/` via `scripts/graph-export.py` and refresh `audit-baseline.json`; do not shorten full `SKILL.md` bodies to fit discovery budgets.

## Typical Scenarios

Each row maps a real request to the smallest correct action. Pick the row, load only what it names.

| Scenario | First action | Then | Done when |
|----------|-------------|------|-----------|
| Create a new portable skill | Copy `Minimal Template` above; set `name` + trigger-rich `description` | Write 2-3 evals (`references/skill-validation.md`), then split detail into `references/` | Validator passes and a trigger eval fires on real user language |
| Audit / modernize an existing skill | `python3 scripts/validate_skill.py <skill-dir>` | Fix contract drift, broken links, stale `sources.json`; re-verify field semantics against live docs | 0 errors and no unscoped runtime field alongside a portability claim |
| Skill must use Claude-only fields | Add the field (`disable-model-invocation`, `paths`, `context: fork`, `agent`, `shell`) | Add a `compatibility` note naming the runtime; drop any portability claim | Field appears only inside a runtime-scoped layer |
| Turn a reference skill into a `/command` workflow | Set `disable-model-invocation: true` + use `$ARGUMENTS` in the body | Keep the body as the task prompt (see `Invocation Control`) | `/name arg` runs the procedure; model no longer auto-triggers it |
| Ship one skill to Claude Code **and** Codex | Keep portable core canonical; mirror intent into `agents/openai.yaml` | Run drift gate from `references/dual-distribution.md` | Both surfaces describe the same intent; no field copied across runtimes unverified |
| Build a router / composable skill | Model it as Pattern 10 (stage-based selection pipeline) | Keep sources → hydrators → filters → scorers → selector → validation → side effects separate | Every dropped candidate has a named filter reason; selection is traceable |
| `SKILL.md` grew past ~500 lines | Apply progressive disclosure (`references/skill-patterns.md`) | Move reference detail to `references/`, helpers to `scripts/`, templates to `assets/`; wire each into Navigation | Body is navigation-first; no orphan support files |
| Skill under-triggers or over-triggers | Rewrite `description` per `Description Rules` (what + when + real trigger words) | Add a non-trigger eval for the over-fire case | Trigger and non-trigger evals both pass |
| Discovery / routing structure changed | Regenerate `frameworks/shared-skills/graph/` via `scripts/graph-export.py` | Refresh `audit-baseline.json`; do not shrink full bodies to fit budgets | `audit-coverage.py --check` passes |
| Skill needs cross-session state | Use Pattern 7; store under `${CLAUDE_PLUGIN_DATA}/` | Degrade gracefully when state is missing; never store secrets | First run works with no state present |

If a request matches no row, treat it as "create" or "audit" and fall back to the `Workflow` section.

## ASCII Flow

```text
Skill change request
  -> Define 2-3 real trigger tasks
  -> Draft portable core: folder, SKILL.md, name, description
  -> Split support material
     +-- reference detail -> references/
     +-- deterministic helper -> scripts/
     +-- templates/assets -> assets/
  -> Add runtime metadata only in scoped layers
  -> Validate structure, links, sources, and behavior
  -> Update catalog when names, counts, or router ownership change
```

## Known Traps

- claiming a skill is portable while relying on runtime-only fields, substitutions, or invocation semantics
- packing reference material, examples, and policy prose into `SKILL.md` instead of progressive disclosure files
- writing descriptions that sound broad but fail to trigger on the real user language
- keeping `data/sources.json` present but stale, secondary-only, or disconnected from the actual workflow
- copying frontmatter or examples from one runtime into another without re-verifying current official docs
- letting enrichment steps silently remove candidate skills, routes, or evidence instead of using a named filter with an explicit reason
- choosing between adjacent skills before each candidate has been evaluated independently against the user request

## Common Anti-Patterns

- universal "do everything" skills with no bounded task shape
- runtime-specific metadata treated as the portable baseline
- support directories (`references/`, `scripts/`, `assets/`) created but not wired into navigation
- validation limited to syntax and broken links, with no trigger/non-trigger behavior checks
- source lists that encode rankings, prices, or volatile product claims as durable truth
- routing by keyword pile-up instead of a stage contract with eligibility filters, independent scoring, post-selection validation, and traceable side effects
- solving runtime discovery budget by deleting useful workflow context from mature skills instead of adding a compact generated discovery layer

## Description Rules (repo delta)

Generic description craft — third person, what + when, trigger words, single-line YAML, `<1024` chars, good/bad examples — is owned by the open spec and `skill-creator`. Do not re-derive it here. This repo adds one rule on top:

- Keep descriptions inside shared discovery budgets: roughly 120-180 characters and about 25 words, unless the target runtime's docs require otherwise. Over-long descriptions inflate the always-loaded discovery layer for every other skill.

## Scaffolding

Do not hand-author boilerplate. For a fresh `SKILL.md` skeleton (frontmatter, Quick Reference, Workflow, Navigation), invoke the standard `skill-creator` skill, then apply this skill's portability discipline before handoff:

- Add `compatibility: Portable core only. Add runtime-specific notes if extensions are used.` unless the skill is deliberately runtime-scoped.
- Wire every `references/`, `scripts/`, and `assets/` file into Navigation.
- If targeting Codex too, add the `agents/openai.yaml` adjunct (see Core Contract).

## Invocation Control (runtime-specific)

Field mechanics — `disable-model-invocation`, `user-invocable`, `paths`, `argument-hint`, `context: fork` / `agent`, `$ARGUMENTS` — are Claude Code features. The when-to-disable decision and field semantics live in the Claude Code skills docs, `references/frontmatter-reference.md`, and `skill-creator`. Do not duplicate them here. The repo-specific rules:

- These fields are **runtime-scoped, not portable.** A skill that uses any of them must carry a `compatibility` note and drop any portability claim.
- Side-effecting workflows (deploy, production writes, sends) should set `disable-model-invocation: true` so the model cannot auto-trigger them.

### Runtime Portability

`disable-model-invocation`, `user-invocable`, `paths`, `disallowed-tools`, and `when_to_use` are Claude Code fields. For Codex, the equivalent behavior comes from how you register the skill in the runtime layer. Keep the flag in the Claude frontmatter and document the Codex equivalent in a compatibility note if you're targeting both runtimes.

## Compatibility Rules

| Target | Safe assumptions | What to verify separately |
|--------|------------------|---------------------------|
| Portable core | `name`, `description`, optional `license` / `compatibility` / `metadata`, `SKILL.md`, support folders | Runtime-specific fields and any implementation-specific behavior |
| Anthropic / Claude Code | Portable core plus: `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `when_to_use`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell` | Exact field semantics, hook behavior, model controls, UI behavior; verify each in current Claude Code docs |
| VS Code | Portable core and VS Code's documented skill packaging | Any metadata beyond the official VS Code docs |
| Codex in this repo | Portable core; adjunct metadata may live outside frontmatter | Repo-local conventions such as `agents/openai.yaml` when present |

Rules of thumb:

- Keep the portable example clean. Do not mix Anthropic-only fields into the default example.
- Keep the portable voice functional. If the target runtime wants more coaching or framing, add it in a scoped layer rather than inflating the shared core.
- If a field is not confirmed by current official docs for the target runtime, label it as repo-local or provisional.
- When supporting multiple runtimes, document the shared core first and the extensions second.

## Support Files

When to split:

- Put reference material, decision trees, and variant-specific guidance in `references/`.
- Put deterministic helpers, validators, and generators in `scripts/`.
- Put templates, boilerplate, and artifacts used in final output in `assets/`.
- Keep `SKILL.md` under 500 lines and bias toward navigation over duplication.

## Validation Defaults

Run the validator before handoff:

```bash
python3 scripts/validate_skill.py .
python3 scripts/test_validate_skill.py
python3 scripts/validate_catalog.py /path/to/skills/root
python3 scripts/audit_skill_metadata.py /path/to/skills/root
python3 scripts/build_skill_graph.py /path/to/skills/root --check
```

What the validator checks:

- `SKILL.md` exists and has valid portable frontmatter
- canonical core sections are present (`Quick Reference`, workflow, `Navigation`, `Fact-Checking`)
- folder name matches `name`
- runtime-specific fields do not appear alongside unscoped portability claims
- markdown links resolve locally
- long reference files include a table of contents
- `data/sources.json` is valid and fresh enough to trust
- project and domain skills do not cross-link
- exact duplicate registry triggers are either removed or explicitly disambiguated
- registry skill references resolve to real skill directories (gated by `scripts/audit-coverage.py --check`)
- metadata and Codex UI descriptions stay within local budget targets
- graph edges in `metadata.graph` resolve to real skill directories when graph metadata is present

Behavioral checks still require human review. Use `references/skill-validation.md` for the eval matrix.

Pilot benchmark commands:

```bash
# Deterministic harness check
python3 frameworks/shared-skills/evals/test_run_skill_bench.py

# Live Codex-backed pilot benchmark
python3 frameworks/shared-skills/evals/run_skill_bench.py \
  frameworks/shared-skills/evals/tasks/pilot-router-and-long-skills.json \
  --adapter codex \
  --repo-root . \
  --output frameworks/shared-skills/evals/outputs/pilot-router-and-long-skills-codex-YYYY-MM-DD.jsonl
```

Store benchmark runs as JSONL artifacts in `frameworks/shared-skills/evals/outputs/`. Do not create standalone Markdown run summaries unless explicitly requested.

## Navigation

Resources:

- [references/frontmatter-reference.md](references/frontmatter-reference.md) - Portable core and runtime-specific header guidance
- [references/skill-patterns.md](references/skill-patterns.md) - Patterns for splitting, scripting, and compatibility scoping
- [references/skill-validation.md](references/skill-validation.md) - Static checks plus behavioral evals
- [references/anthropic-skills-guide.md](references/anthropic-skills-guide.md) - Anthropic-specific reference
- [references/skill-vs-agent-decision.md](references/skill-vs-agent-decision.md) - Decision matrix: when to write a skill vs a subagent vs both
- [data/sources.json](data/sources.json) - Official sources to verify against

Scripts:

- `scripts/validate_skill.py`
- `scripts/validate_catalog.py`
- `scripts/audit_skill_metadata.py`
- `scripts/build_skill_graph.py`
- `scripts/test_validate_skill.py`

Standard skills to defer to (not in this repo; invoke via the Skill tool):

- `skill-creator` - Scaffold, modify, and benchmark/eval skills (generic authoring mechanics)
- `plugin-dev:skill-development` - Authoring skills inside plugins
- Agent Skills open spec: https://agentskills.io/specification - Portable frontmatter and structure baseline

Related skills:

- `agents-subagents` - Agent creation and delegation contracts
- [../agents-hooks/SKILL.md](../agents-hooks/SKILL.md) - Hook automation
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) - MCP server integration

Repo-local note:

- If this repo also carries Codex system skills, check `.codex/skills/.system/skill-creator/SKILL.md` locally. Do not treat that path as portable.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current external facts, field semantics, runtime limits, and packaging behavior before final answers.
- Prefer primary sources and label runtime-specific guidance with platform and date when it may drift.
- If web access is unavailable, state the limitation and mark any runtime-specific claim as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
