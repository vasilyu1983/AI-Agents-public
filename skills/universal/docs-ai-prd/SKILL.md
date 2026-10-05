---
name: docs-ai-prd
description: Writes PRDs and specs optimized for coding assistants. Use when authoring requirements or project context for Claude Code, Cursor, Copilot, or Codex.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.4"
last_validated: 2026-07-11
---

# PRDs, Specs, and Project Context

## Workflow

1. Pick the deliverable.
2. Gather evidence, constraints, and dependencies.
3. Choose the canonical context surface for the target tool or team workflow.
4. Write decisions first.
5. Add acceptance criteria, rollout gates, and source-backed facts. For delivery across more than one session or worker, add a [delivery-milestones table](references/delivery-milestones.md).
6. Validate with the relevant checklist before handoff. For source inventories, run `python3 scripts/validate_sources.py --scan-only`; it excludes archives and symlinks and exits 2 for invalid or empty scan roots and unreadable source files. Inventory success does not verify claims or live URLs.

## Quick Reference

| Need | Start Here |
|------|------------|
| core PRD | [assets/prd/prd-template.md](assets/prd/prd-template.md) |
| AI feature PRD | [assets/prd/ai-prd-template.md](assets/prd/ai-prd-template.md) |
| technical design | [assets/spec/tech-spec-template.md](assets/spec/tech-spec-template.md) |
| story map or backlog framing | [assets/stories/story-mapping-template.md](assets/stories/story-mapping-template.md) |
| acceptance criteria | [assets/stories/gherkin-example-template.md](assets/stories/gherkin-example-template.md) |
| delivery milestones (multi-session work) | [references/delivery-milestones.md](references/delivery-milestones.md) |
| planning checklist | [assets/planning/planning-checklist.md](assets/planning/planning-checklist.md) |
| agentic handoff | [assets/planning/agentic-session-template.md](assets/planning/agentic-session-template.md) |
| minimal agent context files | [assets/minimal-claudemd.md](assets/minimal-claudemd.md), [assets/minimal-agents.md](assets/minimal-agents.md) |
| cross-tool context layering | [assets/cross-tool-context.md](assets/cross-tool-context.md) |
| stack-specific project context (fill in the blanks, don't write from scratch) | [assets/web-app-context.md](assets/web-app-context.md), [assets/api-service-context.md](assets/api-service-context.md), [assets/cli-context.md](assets/cli-context.md), [assets/library-context.md](assets/library-context.md), [assets/react-context.md](assets/react-context.md), [assets/nodejs-context.md](assets/nodejs-context.md), [assets/python-context.md](assets/python-context.md), [assets/go-context.md](assets/go-context.md) |

## Expert Judgment: Why Specs Fail Coding Agents

Before handoff, check whether an agent can satisfy the written requirements while producing behavior the author did not intend.

### Ambiguity classes that kill agent runs

Scan for these six ambiguity classes:

1. **Referential ambiguity** — "the user," "the form," "it" without a fixed noun-phrase, ID, or schema reference. The agent binds to the nearest plausible referent, which is wrong for the case the author had in mind.
2. **Silent-default ambiguity** — a case is never mentioned (duplicate email, empty list, concurrent edit), so the agent invents a default. That default is rarely audited against the rest of the system.
3. **Scope-boundary ambiguity** — the spec describes new behavior but never states what must stay unchanged. Agents over-refactor adjacent code or leave a now-dead path that nobody asked them to remove.
4. **Temporal/ordering ambiguity** — steps are implied but not sequenced ("validate and save" — validate before or after the side effect that can't be undone?).
5. **Measurement ambiguity** — "fast," "reliable," "secure," "clean" with no unit, threshold, percentile, or test method attached.
6. **Authority ambiguity** — the spec and the existing code disagree, and nothing states which one wins. The agent picks one; the next agent (or the next session) may pick the other.

### Over-specification vs. under-specification: the calibration judgment

- **Over-specification** dictates implementation (a named library, exact variable names, line-level pseudocode) when only the outcome mattered. Cost: the agent thrashes when the mandated approach doesn't fit the codebase, or ships literally what was written instead of what was meant, and the mismatch isn't visible until review.
- **Under-specification** gives a title and one paragraph and leaves every non-happy-path implicit. Cost: the agent invents contract details (error shape, retry count, empty-state behavior) that conflict with assumptions already baked into three other call sites — expensive to discover after the fact, not before.

Calibrate detail level to three variables, not to habit or template length:

| Blast radius | Reversibility | Agent autonomy | Right level of detail |
|---|---|---|---|
| High (payments, auth, deletion, PII) | Low (hard to roll back) | Any | Spec every edge case explicitly, plus a "must NOT" list |
| Medium | Medium | Supervised turn-by-turn (human reviews each step) | State decisions + open questions; let the review loop resolve remaining edge cases |
| Low (prototype, internal tool, behind a flag) | High (cheap to revert) | Any | Outcome + happy path; let the agent propose and flag edge cases |
| Medium or High | Any | Unattended/autonomous run (no human in the loop until done) | Spec every edge case — there is no reviewer to catch drift mid-run |

### Acceptance-criteria testability: the judgment beyond the checklist

[references/acceptance-criteria-patterns.md](references/acceptance-criteria-patterns.md) covers format and common mistakes. Two judgment calls sit above that checklist:

- **The "can't picture the failing test" tell.** An AC that reads well but generates zero tests is unfalsifiable. If you cannot describe the specific test that would fail if the behavior were wrong, the AC is not done — rewrite it before handoff, don't ship it and hope the agent infers the missing half.
- **The "two competent engineers" tell.** The most common single point of spec failure is not a missing AC — it's an AC that is simultaneously true for two materially different implementations. Ask: "could two competent engineers build different things and both honestly claim this AC is satisfied?" If yes, add a discriminating clause (a concrete input/output pair, a specific error code, an explicit ordering) until the answer is no.

### Decision and unknown ledger

Keep unresolved product choices out of declarative requirements. For each unknown, record the decision needed, current assumption, owner, deadline or blocking milestone, affected requirements, and what evidence will close it. Mark acceptance criteria that depend on the assumption so an implementer cannot mistake a placeholder for approved behavior.

A repository shows how the system behaves today, not what the business requires. Never infer SLAs, pricing, compliance or retention duties, priorities or target users from code; enter them in the ledger as assumptions to confirm until the user or an authoritative document states them. Block on the user only for unknowns whose wrong guess risks security exposure, data loss, an irreversible migration, contract or API breakage, material cost, or a destructive external action; otherwise record the assumption and proceed.

When implementation shows an acceptance criterion cannot be met, do not drop it or work around it silently. Mark it `[revised]`, state the constraint, adjust its scope or verification method, bump the spec revision, and re-present only the changed criteria. Require explicit confirmation only when the revision changes a blocking decision or weakens a safety or correctness guarantee.

When the decision lands, update the requirement and its acceptance criteria together, then close the ledger entry with the decision source. A PRD is implementation-ready only when every blocking unknown is closed, explicitly deferred outside scope, or represented as a safe runtime/configuration choice with a named default and fallback.

## Cross-Tool Context Rules

Treat project memory as layered. The table names each tool's usual surfaces; which files a runtime actually loads, and in what precedence, is a lookup owned by [agents-memory](../agents-memory/references/loading-and-layers.md#other-runtimes-lookup-step).

| Tool | Primary Surface | Supporting Surfaces |
|------|-----------------|---------------------|
| Claude Code | `AGENTS.md` when native loading is verified for every contributor; otherwise `CLAUDE.md` importing `AGENTS.md` | scoped Claude files, agents, skills, hooks |
| GitHub Copilot | `.github/copilot-instructions.md` | additional GitHub instructions, `AGENTS.md` |
| Cursor | `.cursor/rules/` or root `AGENTS.md` | root `CLAUDE.md`, scoped rule files |
| portable baseline | `AGENTS.md` | link outward instead of duplicating deep guidance |

Whether Claude Code reads `AGENTS.md` natively, and what takes precedence when both files exist, changes between releases: do not state a support status in a spec. Keep `AGENTS.md` the single source. Follow the [agents-memory lookup step](../agents-memory/references/loading-and-layers.md#agentsmd-in-claude-code-lookup-step) and verify loaded files with `/memory` for every contributor's version, provider, and configuration. If native loading is verified for all and no `CLAUDE.md`-family file suppresses it, no bridge is needed. Otherwise import `@AGENTS.md` at the top of `CLAUDE.md` (Claude-only content below) or use a `CLAUDE.md` → `AGENTS.md` symlink.

## Quality Gates

### PRD and spec quality

- clear problem statement and evidence
- named owner and success criteria
- measurable acceptance criteria
- metrics with formula, timeframe, and source
- explicit risks, rollout gates, and rollback conditions

### AI feature quality

- baseline alternative documented
- eval objective and dataset plan defined before build
- permission, prompt-injection, and data-exfiltration risks covered
- monitoring, incident response, and kill switch specified

### Project-context quality

- file paths and commands match the repo
- guidance is routed to the correct tool surface
- no secrets or sensitive data
- shared and tool-specific instructions do not conflict

## Navigation

**References — Core (load first)**

- [references/agentic-coding-best-practices.md](references/agentic-coding-best-practices.md) — agent-aware writing rules; load for any spec or context-file task
- [references/requirements-checklists.md](references/requirements-checklists.md) — gating checklists for PRD, spec, and context-file quality
- [references/acceptance-criteria-patterns.md](references/acceptance-criteria-patterns.md) — Gherkin, EARS, table, and binary-check patterns
- [references/security-review-checklist.md](references/security-review-checklist.md) — permission, injection, and data-exfiltration gate for AI features
- [references/tool-comparison-matrix.md](references/tool-comparison-matrix.md) — Claude Code vs Copilot vs Cursor vs Codex capability comparison
- [references/code-graph-spec-patterns.md](references/code-graph-spec-patterns.md) — spec patterns for code-graph and multi-repo context
- [references/docs-audit-commands.md](references/docs-audit-commands.md) — shell commands for auditing existing project documentation
- [references/operational-guide.md](references/operational-guide.md) — quick-start entrypoints and common workflow recipes; load when orientation is needed

**References — Spec-driven & prompt craft**

- [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md) — GitHub Spec Kit, EARS notation, Kiro, BMAD-METHOD: pipeline shapes and a lookup step; load for spec-gated agentic pipelines
- [references/prompt-engineering-patterns.md](references/prompt-engineering-patterns.md) — task-contract, context-packaging, and output-contract patterns for chat and coding agents; load when authoring prompts embedded in specs, alongside [assets/prompting/prompt-playbook.md](assets/prompting/prompt-playbook.md) and [assets/prompting/structured-prompt-examples.md](assets/prompting/structured-prompt-examples.md)
- [references/vibe-coding-patterns.md](references/vibe-coding-patterns.md) — iterative prompt-agent loops, human/agent role split, and hygiene rules; load for rapid-prototyping or vibe-coding workflows

**References — Codebase context extraction**

- [references/architecture-extraction.md](references/architecture-extraction.md) — step-by-step commands to extract entry points, layers, and data flows from an existing codebase; load when writing a tech spec cold, then fill [assets/architecture-context.md](assets/architecture-context.md)
- [references/convention-mining.md](references/convention-mining.md) — scripts to detect naming, file, and import conventions from a codebase; load when populating a conventions section, then fill [assets/conventions-context.md](assets/conventions-context.md)
- [references/tribal-knowledge-recovery.md](references/tribal-knowledge-recovery.md) — git-history and comment-mining techniques to recover undocumented decisions; load when onboarding to a legacy codebase, then fill [assets/tribal-knowledge-context.md](assets/tribal-knowledge-context.md)

**Stakeholder & team process (owned by product-management)**

- product-management's references/prd-review-facilitation.md — review-type selection, agenda template, feedback labeling, and iteration workflow; load when running a PRD review
- product-management's references/prd-stakeholder-alignment.md — RACI mapping, async/sync review patterns, conflict resolution, and decision-log template; load when managing multi-stakeholder sign-off
- product-management's references/pm-collaboration-guide.md — interview debrief structure and PRD handoff for human PM teams; load for stakeholder-interview-to-PRD tasks
- product-management's references/traditional-prd-writing.md — section-by-section PRD guidance for human teams (Cagan/Wiegers lineage); load when the audience is a PM team, not a coding agent

- [data/sources.json](data/sources.json)

**Additional assets**

- [assets/metrics/agentic-coding-metrics-template.md](assets/metrics/agentic-coding-metrics-template.md) — load when a spec or pilot must measure coding-assistant impact
- [assets/key-files-context.md](assets/key-files-context.md) — load when documenting the files an agent must know in CLAUDE.md or AGENTS.md
- [assets/dependencies-context.md](assets/dependencies-context.md) — load when documenting external services and integrations in CLAUDE.md or AGENTS.md

## Output Format: HTML vs Markdown for Spec Artifacts

Agent-consumed context files (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`) stay Markdown. For long, read-once, human-facing artifacts (PRDs over ~100 lines, exploration specs comparing options, interactive specs), consider HTML, keep acceptance criteria extractable as a table or code block, and end interactive specs with an export control ("copy as JSON / prompt / diff"). Decision table, tradeoffs, and recipe: [references/html-vs-markdown-output.md](references/html-vs-markdown-output.md).

## Boundary: docs-ai-prd vs docs-codebase

- `docs-ai-prd` owns requirements, specs, acceptance criteria, and context-file strategy
- `docs-codebase` owns README, runbooks, API reference, changelogs, and canonical documentation quality

If you are deciding what context an agent needs or how a spec should be structured, stay here. If you are rewriting repository docs, use `docs-codebase`.

## Related Skills

- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md)
- [../dev-context-engineering/SKILL.md](../dev-context-engineering/SKILL.md)
- [../dev-workflow-planning/SKILL.md](../dev-workflow-planning/SKILL.md)
- [../qa-docs-coverage/SKILL.md](../qa-docs-coverage/SKILL.md)
- [../product-management/SKILL.md](../product-management/SKILL.md)
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
