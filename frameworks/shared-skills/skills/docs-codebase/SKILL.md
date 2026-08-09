---
name: docs-codebase
description: Writes and reorganizes docs-as-code for software repos. Use when updating READMEs, runbooks, onboarding docs, API references, or agent instruction files.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Technical Documentation

Use this skill to write, restructure, and verify software-repo documentation: READMEs, runbooks, API references, changelogs, onboarding docs, instruction files, and canonical docs libraries for humans and coding agents.

The goal is durable docs, not document sprawl. Keep one canonical doc per subject, wire in ownership and review cadence, and verify filesystem-backed claims before publishing summary docs.

## Quick Reference

| Documentation Type | Template | Notes |
|-------------------|----------|-------|
| project README | [assets/project-management/readme-template.md](assets/project-management/readme-template.md) | onboarding and project navigation |
| ADR or architecture note | [assets/architecture/adr-template.md](assets/architecture/adr-template.md) | decision record |
| gap analysis or migration assessment | [assets/architecture/gap-analysis-template.md](assets/architecture/gap-analysis-template.md) | architecture and readiness work |
| API reference | [assets/api-reference/api-docs-template.md](assets/api-reference/api-docs-template.md) | REST, GraphQL, gRPC, AsyncAPI |
| changelog | [assets/project-management/changelog-template.md](assets/project-management/changelog-template.md) | release history |
| contributing guide | [assets/project-management/contributing-template.md](assets/project-management/contributing-template.md) | team and OSS contribution |
| docs IA or consolidation plan | [assets/docs-as-code/docs-structure-template.md](assets/docs-as-code/docs-structure-template.md) | large doc sets |
| ownership and review model | [assets/docs-as-code/ownership-model.md](assets/docs-as-code/ownership-model.md) | runbooks and critical docs |
| doc sync checklist | [assets/project-management/template-doc-sync-checklist.md](assets/project-management/template-doc-sync-checklist.md) | status and path integrity |
| operational runbook | [assets/operational/runbook-template.md](assets/operational/runbook-template.md) | SLO, alerts → response, rollback, escalation, postmortems; use `{{PLACEHOLDER}}` format |
| CI markdownlint config | [assets/ci/.markdownlint.yaml](assets/ci/.markdownlint.yaml) | drop into repo root; MD013 off, MD024 siblings_only, sensible defaults |
| CI Vale prose config | [assets/ci/.vale.ini](assets/ci/.vale.ini) | Microsoft style base; passive voice as suggestion; per-rule overrides documented |
| CI docs quality workflow | [assets/ci/docs-quality.yml](assets/ci/docs-quality.yml) | GitHub Actions: markdownlint + markdown-link-check + vale on docs/ PRs |

## When to Use This Skill

Use this skill when the main task is:

- writing or refactoring canonical technical docs
- consolidating messy `docs/` folders
- adding or fixing README, onboarding, runbook, changelog, or API docs
- keeping instruction files and canonical docs aligned
- publishing AI-readable documentation with stable navigation

Route elsewhere when the main task is:

- auditing docs freshness or coverage rather than rewriting docs
- deciding product requirements, specs, or PRD structure

## Defaults

- one subject, one canonical doc
- update an existing canonical doc before creating a new Markdown file
- owners and review cadence on critical docs
- doc updates in the same delivery cycle as the feature or change
- summary docs may not claim complete inventory unless counts and paths were re-verified from the repo
- temporary reports are lifecycle-managed, not permanent sources of truth
- thin platform entry files are better than duplicated giant instruction files

## Markdown Creation Gate

Before creating any new `*.md` file, prove all of these:

- no existing canonical doc owns the subject
- the target path has a clear doc type: README/navigation, runbook, reference, explanation, ADR/spec, report, or generated context
- the file has an owner, review cadence, and lifecycle state if it can go stale
- the file is linked from the right index, README, nav, or context hub
- generated outputs are under a generated artifact root such as `docs/context/` and have a rebuild path

If any item fails, update an existing doc, add a small section to a canonical page, or keep the answer in chat. Do not create per-session notes, one-off summaries, or root-level Markdown reports unless the user explicitly asks for that artifact.

## Docs vs Agent Operations

- `AGENTS.md` / `CLAUDE.md`: hot execution policy, exact commands, constraints, and pointers. Not a codebase catalog, report archive, or general docs folder.
- `README.md`: human and agent navigation. Not a deep handbook.
- `docs/`: durable product, technical, operational, API, ADR, and onboarding docs.
- `docs/operations/` or `docs/runbooks/`: operational procedures with owners and verification steps.
- `docs/reports/`: temporary evidence or analysis with `pending-integration`, `integrated`, or `superseded` status.
- `docs/context/` or `context/`: generated or compiled LLM context artifacts. Prefer rebuild scripts and structured inputs; do not hand-edit generated pages as canonical truth.
- `.archive/`: historical material excluded from normal search and context unless explicitly requested.

## Workflow

1. Identify the document type and audience.
2. Inspect the repo’s current conventions and existing canonical docs.
3. Run the Markdown Creation Gate before adding a new file.
4. Start from the closest template in `assets/` only when a new or replacement doc is justified.
5. Consolidate duplicates into one canonical page per topic.
6. Add ownership, review cadence, and publishing expectations where the doc matters operationally.
7. Run documentation QA and integrity checks before handoff.

## ASCII Flow

```text
Docs request
  |
  v
Classify document type + audience
  |-- README / onboarding ------> project-management templates
  |-- runbook / operations -----> operational templates
  |-- API reference ------------> api-reference templates
  |-- ADR / architecture -------> architecture templates
  |-- docs IA / cleanup --------> docs-as-code templates
  |
  v
Inspect existing canonical docs
  |
  v
Markdown Creation Gate
  |-- existing owner found -----> update canonical doc
  |-- no owner, justified ------> create linked doc with owner + cadence
  |-- temporary evidence -------> docs/reports with lifecycle state
  |
  v
Verify paths, links, counts, commands, and status claims
  |
  v
Publish through README / index / context hub
```

## Revamp Mode for Large or Messy Docs Folders

Use this mode when a repo has too many overlapping or LLM-generated docs:

1. inventory every file and classify it by doc type
2. pick the canonical doc for each subject
3. move durable facts into the canonical doc
4. mark temporary reports as `pending-integration`, `integrated`, or `superseded`
5. remove integrated drafts instead of preserving duplicate mirrors
6. re-check links, counts, moved paths, and canonical references before publishing a summary

## AI-Readable Documentation Rules

- keep `README.md` as the navigation anchor
- keep `AGENTS.md` and `CLAUDE.md` thin when possible, with shared guidance factored into canonical docs
- keep LLM operational files as routers to canonical docs, not mirrors of those docs
- publish stable URLs, stable headings, and `last_verified` markers for volatile pages
- prefer concise task-oriented docs over prose-heavy essays
- treat stale docs as execution bugs for humans and agents alike
- keep generated context hubs rebuildable from source artifacts rather than manually patched markdown

## Judgment Calls: Docs Rot, Agent Consumers, and Ownership That Sticks

Rot detection beyond "old timestamp":

- A doc edited yesterday can still be wrong. Correlate the doc's git history against the git history of the code path it describes; a code file that moved on without a matching doc commit is a stronger rot signal than age alone.
- Treat "the doc still reads fine" as a false negative test. Verify referenced commands, flags, paths, and dependency versions actually run or exist — prose can read smoothly while describing a system that no longer exists.
- A doc that names people ("ask Sarah"), specific tickets, or an org chart is a rot magnet. Move time-bound references into buddy notes or dated reports, not canonical docs.
- Treat a deprecated-but-undeleted doc as more dangerous than a missing one: readers and agents trust what they find, and a wrong doc actively misleads where a gap only leaves a question.

Agents and humans read the same doc differently; serve both:

- Agents execute instructions literally and immediately — a stale command in `AGENTS.md` or `CLAUDE.md` gets run, not questioned, the way a human skimming a wiki might self-correct. Hold instruction files to a higher freshness bar than narrative docs.
- Agents need stable anchors (headings, IDs, paths) they can cite and re-fetch; humans tolerate prose that moves around. Do not casually reshuffle a canonical doc's headings once tooling or agent memory links into it.
- An agent cannot tell an example from a prescription unless the doc says so. Label illustrative code, counts, and inventories explicitly, or an unlabeled example becomes ground truth for the next agent that reads it.
- Humans need the "why" (rationale, trade-offs, links to ADRs); agents mostly need the "what" and the exact command. Keep both, but do not let one crowd out the other in the same file — narrative belongs in `docs/`, execution policy belongs in the thin instruction file.

Ownership models fail in predictable ways:

- A named team with no allocated review time is ownership theater; the doc drifts regardless of who is listed as DRI.
- Ownership tied only to a calendar cadence misses the trigger that actually causes rot: the underlying system changed. Pair calendar review with an event trigger (schema change, deploy, incident) for anything used under pressure, such as runbooks or on-call docs.
- When a team is renamed, merged, or a person leaves, transfer ownership explicitly and date the transfer. An orphaned doc with a listed-but-gone owner is worse than an admittedly unowned doc — it signals false confidence.

## Integrity and Anti-Fluff Gates

Before merging:

- verify file paths, moved-path references, and template paths exist
- verify counts and `complete list` claims against the filesystem
- mark examples as examples instead of presenting them as exhaustive truth
- remove duplicate narrative, vague future-idea prose, and unsupported claims
- keep status in one canonical source and link to it from secondary docs
- reject new Markdown files that lack a placement, owner, lifecycle, and index link

## Navigation

**Core references**

- [references/readme-best-practices.md](references/readme-best-practices.md)
- [references/adr-writing-guide.md](references/adr-writing-guide.md)
- [references/api-documentation-standards.md](references/api-documentation-standards.md)
- [references/runbook-writing-guide.md](references/runbook-writing-guide.md)
- [references/docs-as-code-setup.md](references/docs-as-code-setup.md)
- [references/documentation-testing.md](references/documentation-testing.md)

**Craft and style**

- [references/writing-best-practices.md](references/writing-best-practices.md) — load when drafting new docs; covers audience-first framing, Diátaxis doc types, and prose style
- [references/markdown-style-guide.md](references/markdown-style-guide.md) — load when enforcing Markdown conventions; ATX headings, tables, code blocks, common linter pitfalls
- [references/code-commenting-guide.md](references/code-commenting-guide.md) — load when improving inline comments or docstrings; covers JSDoc, TSDoc, Google-style Python, Go godoc, and anti-patterns
- [references/changelog-best-practices.md](references/changelog-best-practices.md) — load when writing or restructuring changelogs; Keep-a-Changelog format and semantic versioning categories
- [references/contributing-guide-standards.md](references/contributing-guide-standards.md) — load when creating or updating CONTRIBUTING.md; structure, dev-setup, workflow, and OSS contribution norms
- [references/onboarding-documentation.md](references/onboarding-documentation.md) — load when writing developer onboarding docs; Day 1→Week 4 structure, quickstart templates, anti-patterns, and effectiveness measures

**Advanced and AI-aware**

- [references/ai-documentation-tools.md](references/ai-documentation-tools.md)
- [references/backlog-status-sync-pattern.md](references/backlog-status-sync-pattern.md)
- [references/code-graph-documentation-patterns.md](references/code-graph-documentation-patterns.md)
- [references/documentation-metrics.md](references/documentation-metrics.md)
- [references/production-gotchas-guide.md](references/production-gotchas-guide.md)
- [data/sources.json](data/sources.json)

## Boundary: docs-codebase vs docs-ai-prd

- `docs-codebase` owns technical documentation quality, structure, and canonicalization
- `docs-ai-prd` owns requirements, specs, acceptance criteria, and what context an implementation agent needs

If you are writing or cleaning docs, stay here. If you are deciding feature requirements or context strategy, use `docs-ai-prd`.

## Related Skills

- [../qa-docs-coverage/SKILL.md](../qa-docs-coverage/SKILL.md)
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md)
- [../dev-context-engineering/SKILL.md](../dev-context-engineering/SKILL.md)
- [../dev-git-workflow/SKILL.md](../dev-git-workflow/SKILL.md)
- [../docs-ai-prd/SKILL.md](../docs-ai-prd/SKILL.md)

## Verification Gate

Before delivering output, verify:

- every local file path and template path exists
- any counts or inventory claims were re-checked against the filesystem
- commands and code blocks either match repo reality or are marked as examples
- the output matches the intended doc type and calls out any follow-up review or publishing step

## Fact-Checking

- Verify volatile external facts, platform behavior, and version-sensitive guidance before final advice.
- Prefer primary docs over summaries.
- If live verification is unavailable, mark external claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

