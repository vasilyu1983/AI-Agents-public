---
name: docs-ai-prd
description: Writes PRDs and specs optimized for coding assistants. Use when authoring requirements or project context for Claude Code, Cursor, Copilot, or Codex.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# PRDs, Specs, and Project Context

Use this skill to create decision-first PRDs, tech specs, acceptance criteria, and tool-aware project context for coding assistants.

This skill owns what the implementation agent needs to know and how that context should be structured. It does not own general documentation cleanup or canonical docs maintenance.

## Workflow

1. Pick the deliverable.
2. Gather evidence, constraints, and dependencies.
3. Choose the canonical context surface for the target tool or team workflow.
4. Write decisions first.
5. Add acceptance criteria, rollout gates, and source-backed facts.
6. Validate with the relevant checklist before handoff.

## ASCII Flow

```text
Request
  |
  v
Classify deliverable
  |-- PRD / brief -------------------> assets/prd/
  |-- technical spec ----------------> assets/spec/
  |-- story / acceptance criteria ---> assets/stories/
  |-- agent handoff context ---------> assets/planning/ + tool context files
  |
  v
Gather evidence + constraints + dependencies
  |
  v
Choose context surface
  |-- Claude Code -----> CLAUDE.md / scoped Claude files
  |-- Codex -----------> AGENTS.md / scoped instructions
  |-- Copilot ---------> .github/copilot-instructions.md
  |-- Cursor ----------> .cursor/rules/ or AGENTS.md
  |
  v
Write decisions first
  |
  v
Add measurable acceptance criteria + rollout / rollback gates
  |
  v
Validate paths, claims, risks, and handoff readiness
```

## Quick Reference

| Need | Start Here |
|------|------------|
| core PRD | [assets/prd/prd-template.md](assets/prd/prd-template.md) |
| AI feature PRD | [assets/prd/ai-prd-template.md](assets/prd/ai-prd-template.md) |
| technical design | [assets/spec/tech-spec-template.md](assets/spec/tech-spec-template.md) |
| story map or backlog framing | [assets/stories/story-mapping-template.md](assets/stories/story-mapping-template.md) |
| acceptance criteria | [assets/stories/gherkin-example-template.md](assets/stories/gherkin-example-template.md) |
| planning checklist | [assets/planning/planning-checklist.md](assets/planning/planning-checklist.md) |
| agentic handoff | [assets/planning/agentic-session-template.md](assets/planning/agentic-session-template.md) |
| minimal agent context files | [assets/minimal-claudemd.md](assets/minimal-claudemd.md), [assets/minimal-agents.md](assets/minimal-agents.md) |
| cross-tool context layering | [assets/cross-tool-context.md](assets/cross-tool-context.md) |

## Defaults

- decision-first beats narrative-first
- acceptance criteria must be binary or measurable
- AI features need evals, rollback rules, and permission boundaries
- shared context should stay small; tool-specific behavior belongs in tool-specific files
- cross-tool portability is useful, but no single context file is universal

## Expert Judgment: Why Specs Fail Coding Agents

Checklists catch missing sections. They do not catch the judgment calls that make the difference between a spec an agent can execute unattended and one that silently produces the wrong thing while satisfying every checklist item. Apply this before handoff, especially for agentic/autonomous runs where no reviewer sees the intermediate state.

### Ambiguity classes that kill agent runs

A non-expert reviewer reads a spec for completeness of sections. An expert reads it for these six ambiguity classes, because each one lets a competent agent produce plausible-looking, contract-breaking output while technically following the text:

1. **Referential ambiguity** — "the user," "the form," "it" without a fixed noun-phrase, ID, or schema reference. The agent binds to the nearest plausible referent, which is wrong for the case the author had in mind.
2. **Silent-default ambiguity** — a case is never mentioned (duplicate email, empty list, concurrent edit), so the agent invents a default. That default is rarely audited against the rest of the system.
3. **Scope-boundary ambiguity** — the spec describes new behavior but never states what must stay unchanged. Agents over-refactor adjacent code or leave a now-dead path that nobody asked them to remove.
4. **Temporal/ordering ambiguity** — steps are implied but not sequenced ("validate and save" — validate before or after the side effect that can't be undone?).
5. **Measurement ambiguity** — "fast," "reliable," "secure," "clean" with no unit, threshold, percentile, or test method attached.
6. **Authority ambiguity** — the spec and the existing code disagree, and nothing states which one wins. The agent picks one; the next agent (or the next session) may pick the other.

When reviewing a draft spec, scan specifically for these six classes rather than re-reading for tone or completeness — completeness checklists (see [references/requirements-checklists.md](references/requirements-checklists.md)) do not surface any of them.

### Over-specification vs. under-specification: the calibration judgment

Both failure modes are common, and they look opposite but come from the same root cause: guessing the right level of detail instead of deriving it from risk.

- **Over-specification** dictates implementation (a named library, exact variable names, line-level pseudocode) when only the outcome mattered. Cost: the agent thrashes when the mandated approach doesn't fit the codebase, or ships literally what was written instead of what was meant, and the mismatch isn't visible until review.
- **Under-specification** gives a title and one paragraph and leaves every non-happy-path implicit. Cost: the agent invents contract details (error shape, retry count, empty-state behavior) that conflict with assumptions already baked into three other call sites — expensive to discover after the fact, not before.

Calibrate detail level to three variables, not to habit or template length:

| Blast radius | Reversibility | Agent autonomy | Right level of detail |
|---|---|---|---|
| High (payments, auth, deletion, PII) | Low (hard to roll back) | Any | Spec every edge case explicitly, plus a "must NOT" list |
| Medium | Medium | Supervised turn-by-turn (human reviews each step) | State decisions + open questions; let the review loop resolve remaining edge cases |
| Low (prototype, internal tool, behind a flag) | High (cheap to revert) | Any | Outcome + happy path; let the agent propose and flag edge cases |
| Medium or High | Any | Unattended/autonomous run (no human in the loop until done) | Spec every edge case — there is no reviewer to catch drift mid-run |

The common mistake is applying "prototype-level" detail to an unattended, high-blast-radius run, or applying "payments-level" detail to a two-hour supervised prototype. Ask blast radius and autonomy first; let those answers set the spec's length, not the other way around.

### Acceptance-criteria testability: the judgment beyond the checklist

[references/acceptance-criteria-patterns.md](references/acceptance-criteria-patterns.md) covers format and common mistakes. Two judgment calls sit above that checklist:

- **The "can't picture the failing test" tell.** An AC that reads well but generates zero tests is unfalsifiable. If you cannot describe the specific test that would fail if the behavior were wrong, the AC is not done — rewrite it before handoff, don't ship it and hope the agent infers the missing half.
- **The "two competent engineers" tell.** The most common single point of spec failure is not a missing AC — it's an AC that is simultaneously true for two materially different implementations. Ask: "could two competent engineers build different things and both honestly claim this AC is satisfied?" If yes, add a discriminating clause (a concrete input/output pair, a specific error code, an explicit ordering) until the answer is no.

## Cross-Tool Context Rules

Treat project memory as layered:

| Tool | Primary Surface | Supporting Surfaces |
|------|-----------------|---------------------|
| Claude Code | `CLAUDE.md` | scoped Claude files, agents, skills, hooks |
| GitHub Copilot | `.github/copilot-instructions.md` | additional GitHub instructions, `AGENTS.md` |
| Cursor | `.cursor/rules/` or root `AGENTS.md` | root `CLAUDE.md`, scoped rule files |
| portable baseline | `AGENTS.md` | link outward instead of duplicating deep guidance |

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

- [references/spec-driven-dev-landscape.md](references/spec-driven-dev-landscape.md) — current landscape: GitHub Spec Kit, EARS notation, Kiro, BMAD-METHOD (verified 2026-07-11); load for spec-gated agentic pipelines
- [references/prompt-engineering-patterns.md](references/prompt-engineering-patterns.md) — task-contract, context-packaging, and output-contract patterns for chat and coding agents; load when authoring prompts embedded in specs
- [references/vibe-coding-patterns.md](references/vibe-coding-patterns.md) — iterative prompt-agent loops, human/agent role split, and hygiene rules; load for rapid-prototyping or vibe-coding workflows

**References — Codebase context extraction**

- [references/architecture-extraction.md](references/architecture-extraction.md) — step-by-step commands to extract entry points, layers, and data flows from an existing codebase; load when writing a tech spec cold
- [references/convention-mining.md](references/convention-mining.md) — scripts to detect naming, file, and import conventions from a codebase; load when populating `conventions-context.md`
- [references/tribal-knowledge-recovery.md](references/tribal-knowledge-recovery.md) — git-history and comment-mining techniques to recover undocumented decisions; load when onboarding to a legacy codebase

**References — Stakeholder & team process**

- [references/prd-review-facilitation.md](references/prd-review-facilitation.md) — review-type selection, agenda template, feedback labeling, and iteration workflow; load when running a PRD review
- [references/stakeholder-alignment.md](references/stakeholder-alignment.md) — RACI mapping, async/sync review patterns, conflict resolution, and decision-log template; load when managing multi-stakeholder sign-off
- [references/pm-team-collaboration.md](references/pm-team-collaboration.md) — discovery interview templates and debrief structure for human PM teams; load for user-research or stakeholder-interview tasks
- [references/traditional-prd-writing.md](references/traditional-prd-writing.md) — section-by-section PRD guidance for human teams (Cagan/Wiegers lineage); load when the audience is a PM team, not a coding agent

- [data/sources.json](data/sources.json)

**Additional assets**

- [assets/metrics/agentic-coding-metrics-template.md](assets/metrics/agentic-coding-metrics-template.md)
- [assets/key-files-context.md](assets/key-files-context.md)
- [assets/dependencies-context.md](assets/dependencies-context.md)
- [assets/conventions-context.md](assets/conventions-context.md)

## Output Format: HTML vs Markdown for Spec Artifacts

Markdown is the default for most context-file surfaces (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`), but it is not always the right format for the *human-facing artifacts* this skill produces (PRDs, tech specs, exploration docs, planning briefs, code-review writeups). For artifacts intended to be read by humans rather than parsed by the next agent, consider HTML.

This guidance is based on [Thariq, *Using Claude Code: The Unreasonable Effectiveness of HTML*](https://x.com/trq212/status/2052809885763747935) (Claude Code team, 2026-05-08).

### When HTML wins over Markdown

- The artifact will exceed ~100 lines and needs to actually be read by stakeholders (most PRDs and tech specs cross this threshold).
- The spec benefits from visual structure: tables, SVG diagrams, color-coded findings, side-by-side comparisons, annotated code diffs.
- The artifact will be shared via link (S3, internal storage) rather than read in a repo viewer.
- The spec is **exploratory** — multiple design options compared in a grid, mockups, data-flow diagrams.
- The artifact is interactive — sliders, drag-drop reordering, form-based configuration with a "copy as JSON / prompt / diff" export button at the end.

### When Markdown still wins

- Agent-consumed context files (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`) stay markdown — agents parse markdown reliably and HTML adds no signal for them.
- Artifacts that live in version control and need clean diffs — HTML diffs are noisy and hard to review.
- Short artifacts (≤100 lines) where added expressiveness is not worth the 2–4× generation cost.
- Acceptance criteria meant to be evaluated programmatically (Gherkin, JSON Schema), where structure matters more than rendering.

### Concrete tradeoffs

| Dimension | Markdown | HTML |
|---|---|---|
| Generation time | Baseline | 2–4× longer |
| Token cost | Lower | Higher (frontier large-context models absorb it for most artifacts) |
| Read-through likelihood for >100-line specs | Low — author of [Thariq's article](https://x.com/trq212/status/2052809885763747935) reports "I tend to not actually read more than a 100-line markdown file" | Much higher — visual structure invites reading |
| Shareability | Poor — most browsers don't render natively | Excellent — upload + link |
| Version-control diffs | Clean | Noisy |
| Interactive elements | None | Sliders, drag-drop, forms, copy buttons |
| Agent re-ingestion | Native | Works, but markdown is denser per token |

### The export-button pattern (interactive specs)

When generating an interactive HTML artifact, always end with an export control: *"copy as JSON"*, *"copy as prompt"*, *"copy diff"*, *"copy as markdown"*. The button turns UI manipulation back into pasteable text that closes the loop into the next prompt or PR description. Interactive specs without an export button create a one-way artifact the user can't act on.

### Recipe — HTML spec authoring

1. Decide format up front based on the table above. Default to markdown for context-file surfaces; default to HTML for read-once human artifacts >100 lines.
2. For HTML, point Claude at the codebase's existing UI or design system. Maintain one **design-system HTML file** per project that other HTML artifacts can reference to match company style.
3. For exploration specs, request a grid layout with multiple options side-by-side, each labeled with the tradeoff it makes.
4. For interactive HTML, specify the export control explicitly in the prompt — do not assume the agent will add it.
5. For implementation handoff, write the HTML spec for the human reviewer; then in the next session, pass the HTML file to the implementation agent along with markdown acceptance criteria. The implementation agent gets binary criteria; the human gets the richer artifact.

### Related skills

- Interactive HTML with controls + export button: [`../playground:playground`](../) (interactive playground pattern is the same shape)
- Frontend design for matching company style: `frontend-design:frontend-design` plugin skill
- Plan output format selection (HTML vs markdown for plan documents): [`../dev-workflow-planning/SKILL.md`](../dev-workflow-planning/SKILL.md)

### What not to do

- Do not build a forced `/html` skill or rule that everything must be HTML — Thariq's own caution. Prompting fluency beats a forced abstraction.
- Do not put PRDs and context files in the same format by default — the right format depends on the audience (human vs agent).
- Do not lose acceptance criteria in HTML decoration — the binary, measurable parts must remain extractable, ideally as a code block or table the implementation agent can parse cleanly.

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

## Fact-Checking

- Verify volatile vendor, standard, and tool-behavior claims before final advice.
- Prefer primary sources and the curated `data/sources.json` registry.
- If live verification is unavailable, mark external claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

