# software-performance — Learnings

## Patterns That Work

## Mistakes to Avoid

## Domain Knowledge

- [2026-07-11] lhci's documented config flag is --config, not --config-path; verify CLI flags via --help on the pinned version before hardcoding into CI scripts.
- [2026-09-23] Skill cut to diagnosis only; CWV, Lighthouse CI, and k6 content moved to qa-testing-performance. Removed an unsourced "2026 CWV update" claim (the Chromium INP changelog shows no aggregation change) and an invalid LHCI config (inline `budgets` inside `assert`; budgetsFile cannot be combined with other assert options). check_perf_budget.py now exits 2 when no metric matches instead of passing with 0 checks.

## Open Questions

## Consolidated Principles

