# software-code-review — Learnings

## Patterns That Work

- [2026-07-11] The psychological-safety claim traces to a real Empirical Software Engineering paper (423-person survey); cite it directly instead of stating the finding as a bald, unlinked claim.
## Mistakes to Avoid

- [2026-07-11] large-pr-review-strategies.md had a fabricated-looking defect-detection-rate table (specific % by PR size, no source) -- replaced with qualitative guidance; only 200-400 LOC has real backing.
- [2026-07-11] Cisco/SmartBear numbers had drifted to a wrong-but-adjacent figure in 3 files (200-250 LOC/~60min/1500 LOC-hr) instead of the correct 200-400 LOC/60-90min/~400-450 LOC-hr cutoff.
## Domain Knowledge

- [2026-07-11] Amazon CodeGuru Reviewer stopped accepting new customers/repo associations on 2025-11-07; existing associations still work. Point new adopters to Amazon Q Developer.
- [2026-07-11] GitHub Copilot code review moved to an agentic tool-calling architecture (2026) with reasoning-tier routing by change complexity; don't assume the old diff-only behavior.
- [2026-07-11] Qodo transferred PR-Agent governance to an independent community org in 2026 (repo moved to The-PR-Agent); re-verify repo location before citing it again.
## Open Questions

## Consolidated Principles

