---
name: qa-docs-coverage
description: "Audits and enforces documentation quality. Use when checking coverage, freshness, runbook validity, AI-instruction coverage, or cleaning stale/duplicate markdown after LLM edits."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
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
| Scripts and templates | `scripts/check_local_links.py`, `scripts/check_external_links.py`, `scripts/docs_freshness_report.py`, [assets/coverage-report-template.md](assets/coverage-report-template.md), [assets/documentation-backlog-template.md](assets/documentation-backlog-template.md) |

## When to Use

- Audit a repo for missing, stale, duplicated, or unowned documentation.
- Validate runbooks, instruction files, and API docs as part of release or repo hygiene.
- Add CI gates for link health, doc freshness, or contract drift.
- Clean up large doc sets after AI-assisted editing.

## Route Elsewhere

- Writing or restructuring the docs themselves: use [docs-codebase](../docs-codebase/SKILL.md).
- PRDs, implementation specs, or project memory layers: use [docs-ai-prd](../docs-ai-prd/SKILL.md).
- Pure code-risk review with docs as a secondary concern: use [software-code-review](../software-code-review/SKILL.md).

## Defaults

- Discover components before judging missing docs.
- Rank by risk and operating impact, not document count.
- Block on critical external contracts and runbooks; backlog the rest.
- Treat AI-generated docs as drafts until links, commands, and claims are checked.
- For externally consumed APIs, audit for a current `/llms.txt`; its absence is a coverage gap for agent-facing APIs.
- Test runbooks must declare the canonical start, targeted-run, cleanup/reset, and deploy-gate commands.
- Keep one canonical document per topic and one owner per critical area.

## Workflow

1. Discover services, contracts, runbooks, instruction files, and critical workflows.
2. Map current docs to the audit model and identify real gaps, duplicates, and stale areas.
3. Rank the gaps by severity and fix order.
4. Validate links, runbooks, contracts, and freshness signals with scripts or CI tools.
5. Produce actionable outputs with owners, status, and next gates.

## Core Decisions

### Audit Model

Use three priority levels:

- P1: external contracts and failure behavior
- P2: internal integration and operational docs
- P3: developer reference and convenience docs

Default policy:

- block on missing or invalid P1 docs
- warn on P2 and P3 gaps
- track non-blocking debt in a backlog instead of failing every change

### Coverage vs. Usefulness

A coverage percentage is a proxy, not the goal. Do not let it substitute for judgment:

- 100% docstring or endpoint coverage can still be near-0% useful if every entry is a restated
  function signature (`"""Gets the user."""` on `get_user()`) with no failure modes, units,
  side effects, or caller-relevant detail. Tools like `interrogate` or `docstr-coverage` catch
  *absence*, not *quality* — the same trap flagged for AI-generated test coverage vs. mutation
  score in this skill. Spot-check a sample of "covered" items for actual content before trusting
  the percentage in a report.
- Treat a coverage number as a screening signal, not a verdict: use it to find candidate gaps,
  then read the highest-traffic or highest-risk items to judge whether they would actually help
  someone.
- When a coverage tool and a usefulness read disagree, report both numbers rather than
  collapsing to one score. A coverage report that only shows the percentage hides the gap.

### Prioritizing What to Document

Component type (P1/P2/P3) sets a floor, not the whole ranking. Within a priority tier, use
real usage signal to sequence the work:

- Support-ticket and Slack-question frequency for a topic outranks component type when
  the two disagree — a P3 config option that generates two tickets a week belongs above an
  undocumented P2 internal service nobody has asked about yet.
- Onboarding friction is a leading indicator: if new hires consistently ask the same question
  in their first two weeks, that is a documentation gap even if no ticket was ever filed.
- Incident postmortems that cite "unclear docs" or "wrong runbook step" as a contributing
  factor should immediately re-prioritize the cited doc to P1, regardless of its original tier.
- Absence of signal is not evidence of low priority — it can mean nobody has discovered they
  need the component yet (new integration, upcoming launch). Cross-check against the roadmap,
  not just historical tickets.

### When Not to Document

Documentation has a maintenance cost; do not recommend it reflexively.

- Skip inline documentation for code that is self-evident from its name, type signature, and
  immediate context (a well-named pure function with typed arguments rarely needs a docstring
  restating its signature). Flag this in a report as "appropriately undocumented," not a gap.
- Skip a dedicated doc page for a component with a single internal caller and no independent
  failure mode — the calling code is the documentation.
- Prefer fixing the interface over documenting around it: if a gap exists because an API is
  confusing (inconsistent naming, hidden side effects, surprising defaults), the durable fix is
  often to simplify the code, not to write more prose explaining the confusion.
- Do not recommend documenting deprecated or soon-to-be-removed components; recommend removal
  or an explicit deprecation notice instead.

### Freshness and Ownership

Critical docs should have enough metadata to re-verify them:

- owner
- last verified date
- review cadence
- related code paths or systems

For multi-repo hubs, freshness should follow repo sync events, not only a calendar schedule.

### Doc-Rot Signals Beyond Age

A doc can be young by `last_verified` and still be wrong. Age-based freshness thresholds
(see [references/freshness-tracking.md](references/freshness-tracking.md)) catch neglect;
they do not catch rot from a fast-moving change that landed after the last verification.
Treat these as rot signals independent of age:

- the doc references a function, flag, endpoint, or config key that no longer exists in the
  code paths listed in its frontmatter
- a recent PR touched a `code_paths` glob the doc declares, but the doc's `last_verified` did
  not move
- the doc's example output, error message, or screenshot no longer matches what the current
  code produces
- a support ticket or incident explicitly contradicts a documented behavior
- the doc still describes a deprecated flow alongside the current one without marking which is
  authoritative

### Ownership Models That Keep Docs Alive

An owner listed in frontmatter is necessary but not sufficient. Judge whether the ownership
model itself creates a feedback loop:

- **Author-owns-until-handoff**: the engineer who wrote the code owns its docs until an
  explicit handoff; works well for young, single-team components, fails once the original
  author moves teams and no handoff happens.
- **Docs-on-call rotation**: folded into an existing on-call or support rotation so freshness
  reviews happen on a cadence backed by a real calendar reminder, not "whoever remembers."
  Tends to outlast individual ownership changes.
- **CODEOWNERS-enforced**: a `CODEOWNERS` entry over the docs path requires the owning team's
  review on every PR that touches it; catches drift at commit time instead of at the next
  audit.
- **Team-charter-embedded**: documentation upkeep is a named responsibility in the team's
  charter or onboarding checklist, not a side favor; survives individual turnover better than
  an owner name in frontmatter.
- A named owner with no enforcement mechanism (no CODEOWNERS, no rotation, no charter line) is
  the weakest model — flag it as a gap in the ownership map, not just an owner-present checkbox.

### Runbooks and AI Instructions

Runbooks are only acceptable if someone new can execute them and reach a clear end state.

### Test Runbooks (P1 When Stale)

For QA and automation runbooks, verify:

- the canonical dev-server or environment bootstrap command
- the canonical targeted spec or batch command
- the canonical cleanup or reset command
- the canonical deploy-gate replay command
- artifact locations for traces, logs, or failure context

Treat stale “run the whole suite first” guidance as P1 when it materially wastes time, causes environment collisions, or bypasses the intended deploy-gate flow.

Instruction-file audits should verify:

- the active agent/runtime files actually match the tools in use
- duplicated instruction layers are intentional
- external claims have sources and verification dates
- AI-generated edits still match the current code and workflow reality
- AI-generated tests detect behavior, not just execute it: a high coverage number from
  AI/agent-authored tests is reach, not correctness. The quality signal is mutation score
  (does a reverted behavior fail a test?), not line coverage. Flag suites where coverage is
  high but mutation score is unknown or low as a P1 quality-gap, distinct from a docs gap.

### Automation and Output

Default scripts:

- `scripts/check_local_links.py`
- `scripts/check_external_links.py`
- `scripts/docs_freshness_report.py`

Default outputs:

- coverage report
- prioritized backlog
- targeted doc fixes in repo-native locations

## Output Modes

Default to one of these:

- Coverage audit:
  current-state map, critical gaps, and fix order.
- Runbook validation report:
  execution issues, missing prerequisites, and rollback gaps.
- AI-docs cleanup pass:
  duplicate topics, stale claims, and canonicalization actions.

## Anti-Patterns

- Documenting everything at once instead of ranking by impact.
- Merging AI-generated docs without execution or link checks.
- Keeping unowned docs that never get re-verified.
- Assuming a large docs folder is healthy because it is large.
- Reading a high coverage percentage as a quality verdict — for AI-generated tests it routinely is not (high line coverage, near-zero defect detection); demand a mutation-score signal before trusting it.
- Reporting docstring or endpoint coverage percentage without spot-checking a sample for actual content — a high `interrogate`/`docstr-coverage` score can mean every function has a one-line restatement of its own name.
- Recommending documentation for self-evident code, or documentation as a substitute for fixing a confusing interface.
- Leaving stale test commands or batch names in a canonical runbook after the runner topology changed.
- Treating one tool’s instruction-file pattern as universal.
- Ranking gaps by component type alone when support-ticket volume, onboarding friction, or an incident postmortem already show which gap is actually hurting people.

## ASCII Flow

```text
Docs quality request
  -> Discover required docs from product, code, runbooks, APIs, and agents
  -> Inventory existing docs while excluding archives
  -> Map coverage, freshness, ownership, links, and executable commands
  -> Rank gaps by operational, release, user, or AI-agent impact
  -> Fix or canonicalize the smallest valuable doc set
  -> Add checks: links, freshness, command validation, and ownership review
```

## Navigation

- Discovery and prioritization: [references/discovery-patterns.md](references/discovery-patterns.md), [references/audit-workflows.md](references/audit-workflows.md), [references/priority-framework.md](references/priority-framework.md)
- Validation and maintenance: [references/ai-instruction-coverage.md](references/ai-instruction-coverage.md), [references/freshness-tracking.md](references/freshness-tracking.md), [references/api-docs-validation.md](references/api-docs-validation.md), [references/runbook-testing.md](references/runbook-testing.md), [references/cicd-integration.md](references/cicd-integration.md), [references/documentation-quality-metrics.md](references/documentation-quality-metrics.md)
- Templates and source map: [assets/coverage-report-template.md](assets/coverage-report-template.md), [assets/documentation-backlog-template.md](assets/documentation-backlog-template.md), [data/sources.json](data/sources.json)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify volatile tool behavior, documentation-lint tooling, and external standards before presenting them as current fact.
- Prefer primary specifications and official tool documentation over summaries.
- If live verification is unavailable, mark current-tooling claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

