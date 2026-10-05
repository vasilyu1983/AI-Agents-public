# document-docx — Learnings

## Patterns That Work

- [2026-08-11] For generated employee DOCX guides, update and validate the canonical Markdown source, generator metadata, and binary output together; otherwise a later rebuild can silently restore obsolete UI guidance.
## Mistakes to Avoid

- [2026-08-11] When a user supplies a current product UI screenshot, treat its visible labels as authoritative over inferred or stale model names; inspect every document occurrence before publishing the correction.
## Domain Knowledge

- [2026-07-11] Verified Jul 2026: python-docx add_comment() needs v1.2.0+; InlineShape still has no public alt-text property (only height/width/type), so the OOXML workaround uses the private _inline attribute.
## Open Questions

## Consolidated Principles

