# Operational Guide

Operational patterns and reference entrypoints for `docs-ai-prd`.

## Start Here

- **PRDs and specs**: `assets/prd/`, `assets/spec/`, `assets/stories/`
- **Project context**: `assets/minimal-agents.md`, `assets/minimal-claudemd.md`, `assets/cross-tool-context.md`
- **Measurement**: `assets/metrics/agentic-coding-metrics-template.md`
- **Validation and review**: `references/requirements-checklists.md`, `references/acceptance-criteria-patterns.md`, `references/security-review-checklist.md`

## Reference Order

1. [agentic-coding-best-practices.md](agentic-coding-best-practices.md)
2. [prompt-engineering-patterns.md](prompt-engineering-patterns.md)
3. [tool-comparison-matrix.md](tool-comparison-matrix.md)
4. [requirements-checklists.md](requirements-checklists.md)
5. [security-review-checklist.md](security-review-checklist.md)

## Common Workflows

### Draft a non-AI PRD

Use:
- `assets/prd/prd-template.md`
- `references/requirements-checklists.md`
- `references/acceptance-criteria-patterns.md`

### Draft an AI PRD

Use:
- `assets/prd/ai-prd-template.md`
- `references/security-review-checklist.md`
- `data/sources.json` for current eval and governance references

### Refresh repo memory

Use:
- `assets/minimal-agents.md`
- `assets/minimal-claudemd.md`
- `assets/cross-tool-context.md`

### Audit doc freshness

Use:
- `references/docs-audit-commands.md`
- `python3 scripts/validate_sources.py --scan-only`
- `python3 scripts/validate_sources.py` when network access is available

## Operating Rules

- Prefer canonical docs over duplicated summaries.
- Treat external facts as volatile unless verified from primary sources.
- Keep shared context portable and tool-specific overlays small.
- Separate final decisions from open questions.
- Require measurable success criteria for anything that might ship.

## External Sources

See `../data/sources.json` for the curated source registry.
