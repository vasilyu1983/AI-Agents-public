# qa-resilience — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] A minutes-per-month constant used inconsistently across sections (43,800 min "average month" vs. 43,200 min "exact 30-day month") silently produced MTTR sub-targets off by ~2% in reliability-theory-applied.md. When a reference file recomputes the same derived quantity in more than one section, grep for the raw constant across the whole file during an audit rather than re-deriving the arithmetic locally in only one place.

## Domain Knowledge

## Open Questions

## Consolidated Principles
