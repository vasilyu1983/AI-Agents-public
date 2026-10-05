---
name: qa-docs-coverage
description: "Audits and enforces documentation quality. Use when checking coverage, freshness, runbook validity, AI-instruction coverage, or cleaning stale/duplicate markdown after LLM edits."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# QA Docs Coverage

Use this skill to audit documentation as a quality system: discover what should exist, map what exists, rank the gaps, and add checks so critical documentation does not regress. It complements [docs-codebase](../docs-codebase/SKILL.md), which is better for writing or restructuring the docs you decide to fix.

## Quick Reference

| Task | Use |
|------|-----|
| Discovery and audit flow | [references/discovery-patterns.md](references/discovery-patterns.md), [references/audit-workflows.md](references/audit-workflows.md) |
| Prioritization and metrics | [references/priority-framework.md](references/priority-framework.md), [references/documentation-quality-metrics.md](references/documentation-quality-metrics.md) |
| AI-instruction, llms.txt, and freshness checks | [references/ai-instruction-coverage.md](references/ai-instruction-coverage.md), [references/freshness-tracking.md](references/freshness-tracking.md) |
| Runbook and contract validation | [references/runbook-testing.md](references/runbook-testing.md), [references/api-docs-validation.md](references/api-docs-validation.md) |
| CI/CD gates | [references/cicd-integration.md](references/cicd-integration.md) |
| Scripts and templates | `scripts/check_local_links.py`, `scripts/check_external_links.py`, `scripts/docs_freshness_report.py`, [assets/coverage-report-template.md](assets/coverage-report-template.md), [assets/documentation-backlog-template.md](assets/documentation-backlog-template.md) |

## Navigation

- Writing or restructuring the docs themselves: use [docs-codebase](../docs-codebase/SKILL.md).
- PRDs, implementation specs, or project memory layers: use [docs-ai-prd](../docs-ai-prd/SKILL.md).
- Pure code-risk review with docs as a secondary concern: use [software-code-review](../software-code-review/SKILL.md).
- Test-suite quality, including mutation-score gating: use [qa-testing-strategy](../qa-testing-strategy/SKILL.md).

## Defaults

- Discover components before judging missing docs.
- Rank by risk and operating impact, not document count.
- Block on critical external contracts and runbooks; backlog the rest.
- Treat AI-generated docs as drafts until links, commands, and claims are checked.
- For agent-facing docs, check whether a maintained `llms.txt` at the relevant site path helps agents find the canonical pages; the [format](https://llmstxt.org/) also permits path-scoped files such as `/docs/llms.txt`.
- Test runbooks must declare the canonical start, targeted-run, cleanup/reset, and deploy-gate commands.
- Keep one canonical document per topic and one owner per critical area.

## Workflow

1. Discover services, contracts, runbooks, instruction files, and critical workflows.
2. Map current docs to the audit model and identify real gaps, duplicates, and stale areas; exclude archives from the inventory.
3. Rank the gaps by severity and fix order.
4. Validate links, runbooks, contracts, and freshness signals with scripts or CI tools. Label evidence `inventory`, `static`, `executed`, or `operator-validated`; Markdown, links, and command syntax do not prove that a runbook reaches its stated end state.
5. For executed runbooks, record prerequisites, environment, exact command, observed output, cleanup result, and any destructive or privileged step intentionally left untested.
6. Produce a coverage map, runbook validation, or AI-docs cleanup report with owners, status, and next gates.

## Core Decisions

### Audit Model

Use three priority levels:

- P1: external contracts and failure behavior
- P2: internal integration and operational docs
- P3: developer reference and convenience docs

Default policy — this is the canonical freshness threshold set for this skill; the thresholds
in [freshness-tracking.md](references/freshness-tracking.md), `scripts/docs_freshness_report.py`,
and CI examples all use it:

- P1: 30 days, blocking. Run `docs_freshness_report.py --fail-on P1` (the script's default) so CI fails only on stale P1 docs.
- P2: 60 days, warn.
- P3: 90 days, warn.
- Track non-blocking debt in a backlog instead of failing every change.

### Coverage vs. Usefulness

A coverage percentage is a screening signal, not a verdict — see
[api-docs-validation.md](references/api-docs-validation.md#docstring-and-code-level-doc-coverage)
for the spot-check method and the same trap in AI-generated test coverage.

### Prioritizing What to Document

Component type (P1/P2/P3) sets a floor, not the whole ranking. Within a tier, real usage signal
sequences the work: support-ticket/Slack-question frequency for a topic can outrank component
type (a P3 config option with two tickets a week beats an undocumented P2 service nobody has
asked about); onboarding friction is a leading indicator even with no ticket filed; an incident
postmortem citing "unclear docs" re-prioritizes that doc to P1 regardless of its original tier;
and absence of signal is not evidence of low priority — cross-check against the roadmap, since
it can mean nobody has discovered they need the component yet.

### When Not to Document

Documentation has a maintenance cost; do not recommend it reflexively. Skip inline docs for
code that is self-evident from its name, type signature, and context (flag as "appropriately
undocumented," not a gap). Skip a dedicated page for a component with a single internal caller
and no independent failure mode. Prefer fixing a confusing interface over documenting around
it. Do not recommend documenting deprecated or soon-to-be-removed components; recommend removal
or an explicit deprecation notice instead.

### Freshness and Ownership

Critical docs should have enough metadata to re-verify them: owner, last verified date, review
cadence, related code paths or systems. For multi-repo hubs, freshness should follow repo sync
events, not only a calendar schedule.

### Doc-Rot Signals Beyond Age

A doc can be young by `last_verified` and still be wrong — see
[freshness-tracking.md](references/freshness-tracking.md#doc-rot-vs-staleness) for the rot
signals (vanished identifier, silent code drift, contradicted example, ticket conflict) and why
a rot signal should override a fresh badge.

### Ownership Models That Keep Docs Alive

An owner listed in frontmatter is necessary but not sufficient. Judge whether the ownership
model creates a feedback loop: **author-owns-until-handoff** (fails once the author moves
teams), **docs-on-call rotation** (survives turnover), **CODEOWNERS-enforced** (catches drift at
commit time), **team-charter-embedded** (survives turnover best). A named owner with no
enforcement mechanism is the weakest model — flag it as a gap, not just an owner-present
checkbox.

### Runbooks and AI Instructions

Runbooks are only acceptable if someone new can execute them and reach a clear end state.

Test runbooks (P1 when stale) must declare: the canonical dev-server or environment bootstrap
command, the canonical targeted spec or batch command, the canonical cleanup or reset command,
the canonical deploy-gate replay command, and artifact locations for traces, logs, or failure
context. Treat stale "run the whole suite first" guidance as P1 when it materially wastes time,
causes environment collisions, or bypasses the intended deploy-gate flow.

Instruction-file audits should verify: the active agent/runtime files actually match the tools
in use (see [ai-instruction-coverage.md](references/ai-instruction-coverage.md) for Claude Code
and Codex specifics), duplicated instruction layers are intentional, external claims have
sources and verification dates, and AI-generated edits still match the current code and
workflow reality.

## Anti-Patterns

- Documenting everything at once instead of ranking by impact.
- Merging AI-generated docs without execution or link checks.
- Keeping unowned docs that never get re-verified.
- Assuming a large docs folder is healthy because it is large.
- Reporting docstring or endpoint coverage percentage without spot-checking a sample for actual content.
- Recommending documentation for self-evident code, or documentation as a substitute for fixing a confusing interface.
- Leaving stale test commands or batch names in a canonical runbook after the runner topology changed.
- Treating one tool's instruction-file pattern as universal.
- Ranking gaps by component type alone when support-ticket volume, onboarding friction, or an incident postmortem already show which gap is actually hurting people.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
