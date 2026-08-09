# Hub AGENTS.md Template

Use this template for the master coordination repo, not for source repos.

## Purpose

This repo is the canonical context hub for a portfolio of repositories. It stores generated repo profiles, cross-repo architecture views, and refresh workflows.

## Canonical Sources

- `profiles/` = machine-readable repo truth
- `catalog/` = human-readable repo summaries generated from profiles
- `graphs/` = system relationships
- `reports/` = freshness and coverage

## Rules

- Do not hand-edit generated files unless the workflow says they are curated.
- Update schemas and generation scripts before changing output formats.
- Keep root instructions navigation-focused; do not paste large inventories here.
- Prefer evidence-backed summaries over inferred prose.

