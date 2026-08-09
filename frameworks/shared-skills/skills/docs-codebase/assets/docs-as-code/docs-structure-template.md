# Docs-as-Code Structure Template (Core, Non-AI)

Purpose: define a maintainable documentation structure with ownership and freshness mechanisms.

## Inputs

- Product/repo scope (modules, audiences, support burden)
- Tooling constraints (MkDocs/Docusaurus/README-only, CI availability)

## Outputs

- Docs information architecture (IA) and folder structure
- Ownership model and freshness SLAs (who updates what, when)

## Core

### 1) Suggested Information Architecture (Diátaxis-style)

- Tutorials: step-by-step learning paths
- How-to guides: task-oriented procedures
- Reference: exhaustive API/config specs
- Explanation: conceptual context and rationale

### 2) Suggested Repo Layout

```
docs/
  index.md
  tutorials/
  how-to/
  reference/
  explanation/
  runbooks/
  adr/
  _assets/
```

If docs live in the root:
- `README.md` (quick start + links)
- `docs/` for deeper content

### 3) Required “Freshness” Metadata (per page)

- Owner: team or individual
- Last reviewed: date
- Review cadence: monthly / quarterly / yearly

### 4) CI Checks (recommended)

- Link checker (internal + external if allowed)
- Markdown linting and style guide checks
- “Stale docs” check (fails if last reviewed > cadence)

## Decision Rules

- No docs without owners.
- Prefer small, frequently updated docs over giant “wiki pages”.
- If a runbook exists, it must be testable (commands verified and current).

## Risks

- Docs drift: code changes, docs don’t
- Over-documentation: too much text, no one reads/updates
- Tooling lock-in: docs format prevents contribution

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Generate doc diffs and summarize PR changes; humans review before merging.
- Suggest missing docs based on code changes; do not auto-publish without review.
