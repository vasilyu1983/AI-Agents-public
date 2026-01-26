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
