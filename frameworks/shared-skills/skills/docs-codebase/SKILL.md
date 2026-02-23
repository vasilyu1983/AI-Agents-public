---
name: docs-codebase
description: Technical writing patterns for README files, API documentation, architecture decision records (ADRs), changelogs, contributing guides, code comments, and docs-as-code workflows. Covers documentation structure, style guides, Markdown best practices, and documentation testing.
---

# Technical Documentation

Execution-ready patterns for clear, maintainable technical documentation.

**Modern best practices (January 2026)**: docs-as-code, ownership + review cadence, documentation QA gates (links/style/spelling), AI-assisted drafting + review, OpenAPI 3.2.0 where streaming schemas matter, and GEO (Generative Engine Optimization) for AI search.

## Quick Reference

| Documentation Type | Template | When to Use |
|-------------------|----------|-------------|
| **Project README** | [readme-template.md](assets/project-management/readme-template.md) | New project, onboarding |
| **Architecture Decision** | [adr-template.md](assets/architecture/adr-template.md) | Technical decisions |
| **API Reference** | [api-docs-template.md](assets/api-reference/api-docs-template.md) | REST/GraphQL APIs |
| **Changelog** | [changelog-template.md](assets/project-management/changelog-template.md) | Version history |
| **Contributing Guide** | [contributing-template.md](assets/project-management/contributing-template.md) | Open source, teams |

## Workflow

1. Identify the documentation type and audience.
2. Find existing patterns in the repo; follow local conventions.
3. Start from the closest template in `assets/` and adapt.
4. Add ownership + review cadence for critical docs (runbooks, onboarding, API reference).
5. Run documentation QA (links, formatting, spelling, examples) before merging.

## Decision Tree

```text
User needs: [Documentation Task]
    ├─ New project? → **README.md**
    ├─ Technical decision? → **ADR**
    ├─ Building API? → **OpenAPI spec** + api-docs-template
    ├─ New version? → **CHANGELOG.md**
    ├─ Team collaboration? → **CONTRIBUTING.md**
    ├─ Documenting code? → **Docstrings** (JSDoc, Python)
    └─ Building docs site? → **MkDocs** (Python) or **Docusaurus** (JS)
```

## Cross-Platform AI Documentation

### AGENTS.md Standard

Prefer `AGENTS.md` as the cross-tool source of truth. If a specific tool requires a different filename (example: Claude Code uses `CLAUDE.md`), keep it aligned via a symlink only when you want identical content across tools.

```bash
# If `CLAUDE.md` does not exist and you want identical content:
ln -s AGENTS.md CLAUDE.md
```

## Do / Avoid

### Do

- Assign owners and review cadences to critical docs
- Add CI checks for links, style, and staleness
- Prefer small, task-oriented docs over big wiki pages
- Use Keep a Changelog format with semantic versioning

### Avoid

- Docs without owners (guaranteed to rot)
- Stale runbooks (dangerous during incidents)
- Copy/paste docs that drift from code

## LLM-First Documentation Patterns

When documentation is consumed primarily by AI agents (AGENTS.md, CLAUDE.md, canonical docs for coding assistants), stale docs become a distinct category of bug.

### Stale Docs = Agent Bugs

An agent reading stale docs will:
- Attempt to fix problems that are already solved (e.g., "9 open gating gaps" that were all sealed)
- Use wrong model names (e.g., "Claude Haiku" when code uses `gpt-4o`)
- Apply wrong limits (e.g., "fully gated" when free tier actually gets 3/week)
- Re-implement features that already exist

**Rule:** Treat doc updates as part of the feature PR, not as a follow-up task.

### Report Integration Lifecycle

Temporary investigation docs (QA reports, research exports, audit findings) must not become permanent false sources of truth.

Every dated report file must carry lifecycle metadata:

```yaml
---
Status: pending-integration | integrated | superseded
Integrates-into: docs/product/pricing-feature-matrix.md
Owner: @username
Delete-by: 2026-03-15
---
```

Workflow:
1. Create report with `Status: pending-integration`
2. Extract durable findings into canonical docs
3. Mark report `Status: integrated` with date
4. Delete after `Delete-by` date (git history preserves everything)

### Living Docs: Audit Tables with Status Columns

Instead of deleting audit findings, add a Status column:

| Gap | Status | Sealed In |
|-----|--------|-----------|
| Chart aspects visible to free | Sealed | PR #26 |
| Dreams unlimited for free | Sealed | PR #26 |
| Ask Cosmos no rate limit | Open | — |

This preserves the audit trail while showing current state. Agents can quickly scan for `Open` items.

### Two-Pass Consolidation

When consolidating planning docs into canonical docs:

1. **First pass:** Follow the plan — extract content, delete source files, fix cross-references
2. **Second pass:** Audit deleted content against canonical destinations
   - `git show` deleted files to recover any unique data missed in planning
   - Compare code to docs for drift (e.g., feature marked "Planned" but code shows it's implemented)

Even thorough consolidation plans miss unique data that only lived in one source doc.

### Staleness Disclaimers Over Wrong Numbers

For externally-sourced data (competitor pricing, API rate limits, third-party capabilities):

```markdown
> Prices as of Feb 2026 — verify current pricing at [source].
```

A staleness disclaimer is safer than a potentially wrong number. Wrong numbers in agent-consumed docs cause incorrect implementation decisions.

### Decision Log Collision Prevention

When adding entries to a decision log (e.g., `### D039 — Feature Name`):

```bash
# Always check the latest entry number before adding
grep -o '### D[0-9]*' docs/decision-log.md | tail -1
```

Numbering collisions happen when two decisions are logged in rapid succession without checking.

## Resources

| Resource | Purpose |
|----------|---------|
| [references/readme-best-practices.md](references/readme-best-practices.md) | README structure, badges |
| [references/adr-writing-guide.md](references/adr-writing-guide.md) | ADR lifecycle, examples |
| [references/changelog-best-practices.md](references/changelog-best-practices.md) | Keep a Changelog format |
| [references/api-documentation-standards.md](references/api-documentation-standards.md) | REST, GraphQL, gRPC docs |
| [references/code-commenting-guide.md](references/code-commenting-guide.md) | Docstrings, inline comments |
| [references/contributing-guide-standards.md](references/contributing-guide-standards.md) | CONTRIBUTING.md structure |
| [references/docs-as-code-setup.md](references/docs-as-code-setup.md) | MkDocs, Docusaurus, CI/CD |
| [references/writing-best-practices.md](references/writing-best-practices.md) | Clear communication |
| [references/markdown-style-guide.md](references/markdown-style-guide.md) | Markdown formatting |
| [references/documentation-testing.md](references/documentation-testing.md) | Vale, markdownlint, cspell |
| [references/ai-documentation-tools.md](references/ai-documentation-tools.md) | Mintlify, DocuWriter, GEO |
| [references/production-gotchas-guide.md](references/production-gotchas-guide.md) | Documenting platform issues |
| [references/documentation-metrics.md](references/documentation-metrics.md) | Doc quality, freshness, coverage scoring |
| [references/onboarding-documentation.md](references/onboarding-documentation.md) | Developer ramp-up guides, Day 1-Week 4 |
| [references/runbook-writing-guide.md](references/runbook-writing-guide.md) | Operational runbooks, incident response |

## Templates

| Category | Templates |
|----------|-----------|
| Architecture | [adr-template.md](assets/architecture/adr-template.md) |
| API Reference | [api-docs-template.md](assets/api-reference/api-docs-template.md) |
| Project Management | [readme-template.md](assets/project-management/readme-template.md), [changelog-template.md](assets/project-management/changelog-template.md), [contributing-template.md](assets/project-management/contributing-template.md) |
| Docs-as-Code | [docs-structure-template.md](assets/docs-as-code/docs-structure-template.md), [ownership-model.md](assets/docs-as-code/ownership-model.md) |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-docs-coverage](../qa-docs-coverage/SKILL.md) | Documentation gap audit |
| [dev-api-design](../dev-api-design/SKILL.md) | REST API patterns |
| [git-workflow](../git-workflow/SKILL.md) | Conventional Commits |
| [docs-ai-prd](../docs-ai-prd/SKILL.md) | PRD templates |
