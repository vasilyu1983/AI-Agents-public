---
name: agents-skills
description: Creates and audits agent skills with SKILL.md, references, scripts, and platform-scoped metadata. Use when creating, updating, or validating shared skills.
version: "1.2"
last_validated: 2026-09-11
---

# Agent Skills

Create or modernize skill bundles while keeping the portable core separate from runtime extensions. This skill supplies this repository's dual-runtime, catalog, graph, and composition rules. Use the Agent Skills open spec and the standard `skill-creator` for generic scaffolding and eval mechanics.

## Quick Reference

| Task | Load or run |
|------|-------------|
| Scaffold a skill | Standard `skill-creator`, then [frontmatter-reference.md](references/frontmatter-reference.md) |
| Fix truncated or omitted skill listings | [skill-context-budgets.md](references/skill-context-budgets.md) |
| Audit a skill | `python3 scripts/validate_skill.py <skill-dir>` and [maintenance-workflows.md](references/maintenance-workflows.md) |
| Choose support-file boundaries | [skill-patterns.md](references/skill-patterns.md) |
| Add runtime-specific metadata | [frontmatter-reference.md](references/frontmatter-reference.md) |
| Test trigger and navigation behavior | [skill-validation.md](references/skill-validation.md) |
| Maintain Claude-specific behavior | [anthropic-skills-guide.md](references/anthropic-skills-guide.md) |
| Ship across runtimes | [dual-distribution.md](references/dual-distribution.md) |
| Choose skill, agent, or both | [skill-vs-agent-decision.md](references/skill-vs-agent-decision.md) |

## Core Contract

Portable baseline:

- Require `skill-name/SKILL.md` with explicit `name` and trigger-rich `description`.
- Treat `license`, `compatibility`, and `metadata` as portable optional fields. `allowed-tools` belongs to the open spec, but runtime support may vary.
- Keep the main body focused on selection, workflow, completion criteria, and navigation. Put reference detail in `references/`, deterministic helpers in `scripts/`, and templates in `assets/`.
- Keep the bundle usable when copied by itself. Every support file must be linked from the workflow or Navigation.

Runtime extensions:

- Verify runtime-specific fields and substitutions in current official documentation before copying them.
- Name the target runtime in `compatibility` when a skill depends on runtime-specific headers or invocation behavior; remove unqualified portability claims.
- Keep Anthropic-only mechanics in [frontmatter-reference.md](references/frontmatter-reference.md) and [anthropic-skills-guide.md](references/anthropic-skills-guide.md), not in the portable example.
- Treat `agents/openai.yaml` as Codex-facing adjunct metadata. `SKILL.md` remains canonical and independently valid; revalidate semantic alignment when intent changes.

## Workflow

1. Write two or three concrete user tasks, including a nearby case that should not trigger the skill.
2. Search the graph and existing bundles before creating anything. Extend an existing owner when it already covers the capability.
3. Scaffold the portable core: folder, `SKILL.md`, `name`, `description`, minimal workflow, and completion criteria.
4. Choose the target runtimes, then add only verified runtime-scoped metadata.
5. Split long detail and reusable artifacts into support files; link each file at the stage where it is needed.
6. Run the static checks that match the edit, then trigger, non-trigger, navigation, and runtime-specific evals.
7. If the body or routing changed, regenerate and validate the repository graph and eval manifest.
8. Inspect the diff and fix failures caused by the change before handoff. Record observed routing behavior in the repository routing log.

For each completion claim, name its evidence level: static bundle validation, live runtime loading, observed routing, or task-quality evaluation. Passing `validate_skill.py` proves structure and local links; it does not prove that a runtime loaded the skill, selected it for a prompt, or produced a better answer.

For the exact create, audit, runtime, router, state, and graph recipes, load [maintenance-workflows.md](references/maintenance-workflows.md). For eval design and negative controls, load [skill-validation.md](references/skill-validation.md).

## Design Rules

- Default shared skills to a matter-of-fact, outcome-oriented reference style. Put coaching voice or richer behavioral framing in a runtime-specific layer when needed.
- Keep descriptions specific enough to select the skill from real user language. Stay within this catalog's approximate 120–180 character and 25-word discovery target unless a runtime requires otherwise.
- Model routers and composed workflows as explicit stages: candidate sources, enrichment, eligibility filters with reasons, independent scoring, selection, post-selection validation, then side effects.
- Never let enrichment silently drop candidates or evidence. Preserve the input or report a named filter reason.
- Evaluate adjacent candidates independently before selecting among them.
- Do not shrink useful full-body instructions merely to fit a discovery listing. Use host-specific catalog controls and progressive disclosure; the generated compact map does not filter native startup discovery.
- Do not publish model-quality or token-saving numbers unless the exact claim has a reproducible control, dated evidence, and disclosed limits.

## Completion Contract

A skill change is complete when:

- portable frontmatter, local links, support-file navigation, and source metadata pass applicable static checks;
- runtime-specific fields are scoped and verified rather than presented as portable;
- trigger and non-trigger behavior is covered when selection semantics changed;
- graph, catalog, and long-skill manifest artifacts are synchronized when affected;
- known bugs, current runtime behavior, and version-specific workarounds used in the answer were checked against current primary sources;
- any remaining failure is identified as pre-existing or outside scope with evidence.

## Navigation

Load only the resource needed for the current decision:

- [skill-context-budgets.md](references/skill-context-budgets.md) — Codex catalog overflow, host-specific controls, and verification
- [maintenance-workflows.md](references/maintenance-workflows.md) — repository recipes, validation commands, completion criteria, and recurring traps
- [frontmatter-reference.md](references/frontmatter-reference.md) — portable and runtime-specific header contracts
- [skill-patterns.md](references/skill-patterns.md) — progressive-disclosure, script-backed, stateful, and composable patterns
- [skill-validation.md](references/skill-validation.md) — static, trigger, non-trigger, navigation, and effectiveness-claim evals
- [anthropic-skills-guide.md](references/anthropic-skills-guide.md) — Anthropic-only behavior
- [dual-distribution.md](references/dual-distribution.md) — canonical source and wrapper drift controls
- [skill-vs-agent-decision.md](references/skill-vs-agent-decision.md) — placement and execution-boundary decisions
- [data/sources.json](data/sources.json) — dated sources used by this skill

Scripts:

- `scripts/validate_skill.py` — one bundle
- `scripts/validate_catalog.py` — a catalog root
- `scripts/audit_skill_metadata.py` — metadata, local inventory thresholds, and compact-index structure
- `scripts/build_skill_graph.py` — local skill graph
- `scripts/test_validate_skill.py` — validator regressions

Related skills: `agents-subagents`, [agents-hooks](../agents-hooks/SKILL.md), and [agents-mcp](../agents-mcp/SKILL.md).

## Fact-Checking

- Verify current external facts, field semantics, runtime limits, packaging behavior, known bugs, and version-specific workarounds against primary sources.
- Label runtime-specific guidance with platform and verification date when it may drift.
- If current verification is unavailable, state that limitation and mark the claim unverified.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both. Add a durable new observation with `agents-skills-feedback-loop/scripts/append_learning.py`; do not use the main skill body as a task log.
