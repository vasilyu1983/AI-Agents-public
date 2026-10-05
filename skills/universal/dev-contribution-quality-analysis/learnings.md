# dev-contribution-quality-analysis — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-09-01] A corrupt .git husk makes extract-commits.sh die mid-scan (set -e, git exit 128), silently truncating raw-commits.csv; mismatched repo counts vs mr-acceptances.csv are the tell. Check exit code, not just output.
- [2026-07-11] (corrected 2026-09-25) The 1.75x logic-error and 2.74x security-issue stats are both CodeRabbit's (2025-12-17, 470 PRs: "up to 2.74× higher" security issues), not Veracode's, and 2.74x is not XSS-specific. Veracode's figures are 45% of AI samples failing security checks and 86% XSS-class failures. The original entry wrongly called 2.74x a Veracode XSS stat.
- [2026-07-11] The '54% bugs / 242.7% incidents' figures cited alongside DORA 2025 are from Faros AI's 2026 telemetry report, not DORA's own survey — verify before citing as DORA.
## Domain Knowledge

- [2026-07-11] By mid-2026, fully agent-authored PRs (Devin, Codex cloud, Claude Code delegated sessions) merged under a human identity are common; score them as a distinct provenance class, not blended human craft.
## Open Questions

## Consolidated Principles

