# qa-docs-coverage — Learnings

## Patterns That Work

- [2026-07-11] Rank docs gaps by support-ticket/onboarding-question frequency and incident postmortem mentions, not just P1/P2/P3 component type, when the two disagree.
## Mistakes to Avoid

- [2026-07-11] sources.json metadata.total_sources drifted from the actual category item count; recompute the sum on every edit instead of hand-editing the number.
## Domain Knowledge

- [2026-07-11] llms.txt adoption/citation-impact numbers vary wildly by methodology (BuiltWith 844k+ vs ~5-10% of Tranco top-10k); treat any single figure as unverified.
- [2026-07-11] interrogate and docstr-coverage measure Python docstring presence, not quality; report a coverage % alongside a manual spot-check, never alone.
- [2026-07-11] Vale's GitHub org moved from errata-ai to vale-cli in 2026; pin CI to vale-cli/vale and re-check version, older refs to errata-ai are stale.
## Open Questions

## Consolidated Principles

