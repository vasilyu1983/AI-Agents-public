# software-code-review — Learnings

## Patterns That Work

- [2026-07-11] The psychological-safety claim traces to a real Empirical Software Engineering paper (423-person survey); cite it directly instead of stating the finding as a bald, unlinked claim.
## Mistakes to Avoid

- [2026-07-11] large-pr-review-strategies.md had a fabricated-looking defect-detection-rate table (specific % by PR size, no source) -- replaced with qualitative guidance; only the Cisco/SmartBear size/pace/time limits have real backing.
- [2026-07-11] (corrected 2026-09-23) Cisco/SmartBear numbers drifted. The July fix to "200-400 LOC / 60-90 min" went the wrong way: the Cisco chapter's recommendations are review under 200 LOC, never over 400; under 60 minutes per session, never over 90; best detection below ~300 LOC/h (under 500 still acceptable); top advice 100–300 LOC in 30–60 minutes. 200-400 and 60-90 are ceilings, not targets.
## Domain Knowledge

- [2026-07-11] Amazon CodeGuru Reviewer stopped accepting new customers/repo associations on 2025-11-07; existing associations still work. Point new adopters to Amazon Q Developer.
- [2026-07-11] GitHub Copilot code review moved to an agentic tool-calling architecture (2026) with reasoning-tier routing by change complexity; don't assume the old diff-only behavior.
- [2026-07-11] Qodo transferred PR-Agent governance to an independent community org in 2026 (repo moved to The-PR-Agent); re-verify repo location before citing it again.
## Open Questions

## Consolidated Principles

