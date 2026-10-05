# Large Portfolio Strategy

For 100+ repos:

1. Inventory all repos first.
2. Deep-scan only high-priority or low-confidence repos.
3. Use incremental rescans after bootstrap.
4. Separate active, legacy, archived, and vendor repos early.
5. Generate graph outputs from structured data, not markdown parsing.
6. Keep one canonical profile per repo and derive all other views from it.
7. Keep the root hub instructions small and use nearest-scope overrides only where local behavior changes.
8. Split portable instructions from platform-specific layers instead of maintaining multiple drifting root files.

When time is limited:
- full scan metadata for all repos
- manual review for the top 10 highest-risk or most-central repos
