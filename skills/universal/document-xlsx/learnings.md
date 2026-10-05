# document-xlsx — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] (corrected 2026-09-29) XlsxWriter is write-only (can't edit files); `data_only=True` reads stored caches, which may be empty or placeholder zeros rather than calculated results. Recalculate in the target engine and compare independent control totals; use write_only/read_only + lxml for large exports.
## Open Questions

## Consolidated Principles

