# Industry Benchmarks

## Table of Contents

- [Commit-Level Metrics (GitClear, 211M Lines, 2020-2024 + 2026 Cohort)](#commit-level-metrics-gitclear-211m-lines-2020-2024--2026-cohort)
- [DORA Metrics](#dora-metrics)
- [DORA 2025 and Vendor Telemetry](#dora-2025-and-vendor-telemetry)
- [DX Core 4 Framework](#dx-core-4-framework)
- [AI Productivity Paradox (METR, 2025)](#ai-productivity-paradox-metr-2025)
- [CodeScene Code Health (25+ Factors)](#codescene-code-health-25-factors)

Calibration data from research and commercial tools for interpreting contribution quality scores.

---

## Commit-Level Metrics (GitClear, 211M Lines, 2020-2024 + 2026 Cohort)

| Metric | 2020 | 2024 | Change | Interpretation |
|--------|------|------|--------|----------------|
| Code addition % | 39% | 46% | +7 pts | More new code, less modification |
| Copy/paste (clone) % | 8.3% | 12.3% | +48% relative | AI accelerating duplication |
| Refactored (moved) lines % | 24.1% | 9.5% | -60.6% | Dramatic decline in refactoring |
| Code churn (2-week revision) | 3.1% | 5.7% | +83.9% | Code being rewritten faster |
| New code churn (2-week) | 5.5% | 7.9% | +43.6% | New additions less durable |
| Code longevity (>1mo old revisions) | 30% | 20% | -33% | Less work on established code |
| Duplicated code blocks | Baseline | 8x baseline | +700% | AI generating similar blocks |

### How to Use These Numbers

These are dated cohort figures (GitClear, 2025), not fixed norms. Before citing one as a threshold, check GitClear's most recent report and say which year you compared against.

- Against the 2024 cohort, a person's 14-day churn of 5.7% sat at the average; below 3% was well under it
- Against the same cohort, a refactoring ratio above 15% was well above the 9.5% average
- Duplication above 12% sat at or above the 2024 average; below 5% was well under it

### GitClear 2026 Cohort (2,172 Developer-Weeks, Jan 2026)

Analysis of Cursor, GitHub Copilot, and Claude Code API-integrated developer data:

| Finding | Value |
|---------|-------|
| Durable code output: power AI users vs. non-users | 4.2x more durable code |
| Output increase 2024 to 2025 (AI power users) | +25% |
| Churn ratio: AI power users vs. non-users | 9x higher churn (but absolute output is also much higher) |

**Critical interpretation**: The 4.2x durable code advantage reflects a selection effect — high-output engineers adopted AI first. AI widened a pre-existing performance gap; it did not uniformly uplift all users. When comparing developers, check whether the AI-user cohort was already higher-performing before adoption.

### GitClear "The Maintainability Gap" (2026, 623M code changes)

Dated cohort figures (GitClear, 2026); check the report's current edition before using them as cut-points for structural quality in AI-heavy cohorts:

| Finding | Value |
|---------|-------|
| Refactored/moved-code share, YTD 2026 | 3.8% (down from 13% in 2023) |
| Copy/paste share, H1 2026 | 15.7% |
| Error-masking constructs | +47% |
| Cross-file code reuse | -35% |

---

## DORA Metrics

Use [the planning skill's DORA metric definitions](../../dev-workflow-planning/references/flow-metrics.md) for the five-metric set. Before an external comparison, open the [DORA metrics guide](https://dora.dev/guides/dora-metrics/) and the specific report edition. DORA measures software delivery at the team or service level; do not apply its clusters as person-level score cut-points.

---

## DORA 2025 and Vendor Telemetry

The DORA 2025 AI-assisted report (DORA, Sep 2025) replaced the elite/high/medium/low clusters with team archetypes and framed AI as a "mirror and multiplier": it amplifies a team's existing strengths and dysfunctions. Its adoption and throughput figures, and the Faros AI 2026 telemetry figures, are kept as dated citations in [dev-ai-coding-metrics evidence](../../dev-ai-coding-metrics/references/evidence-update.md), which owns them.

### Interpretation for D2-D4 Scoring

- **Do not attribute vendor telemetry to DORA.** Cite survey findings to DORA and proprietary telemetry to its vendor.
- Rising bug and incident rates in vendor telemetry mean churn and rework thresholds still deserve scrutiny, even where a survey shows throughput improving.
- Teams with strong automated testing and review usually gain most from AI; teams without these controls usually see AI amplify existing quality gaps.

---

## DX Core 4 Framework

Framework introduced by DX (DX, 2024) that groups DORA- and SPACE-style measures into four oppositional dimensions:

| Dimension | Measures | Source |
|-----------|---------|--------|
| Speed | Diffs per engineer, deployment frequency, lead time | System metrics |
| Effectiveness | Developer Experience Index (DXI) — 14 standardized survey items | Self-reported |
| Quality | Change failure rate | System metrics |
| Impact | % time on new capabilities, initiative progress/ROI | Mixed |

### Key Insight

Nicole Forsgren (DORA creator, Nov 2025): "AI broke our developer productivity metrics. Lines of code? Meaningless. Commits? Not the point."

The contribution quality skill accounts for this by:
- Measuring quality outcomes (churn, duplication, test presence) not raw volume
- Keeping delivery cadence as context rather than a quality score
- Role-calibrating expectations rather than applying uniform thresholds

---

## AI Productivity Paradox (METR, 2025)

Study: "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity" (arxiv 2507.09089). Randomized controlled trial, 16 experienced OS developers, 246 tasks.

| Metric | Finding |
|--------|---------|
| Developer forecast | "allowing AI will reduce completion time by 24%" |
| Post-study self-estimate | "allowing AI reduced completion time by 20%" |
| Measured actual effect | "allowing AI actually increases completion time by 19%" (confidence interval not re-verified in the HTML text; see the paper's Figure 1 / Appendix D) |
| Gap between perception and reality | roughly 39 percentage points (20% self-estimated speedup vs. 19% measured slowdown; derived, not a paper figure) |

### Follow-Up

METR's later follow-up and survey results, with their selection-bias caveats, are kept as dated citations in [dev-ai-coding-metrics evidence](../../dev-ai-coding-metrics/references/evidence-update.md). Treat the 2025 RCT as a result for early-2025 tools, not a standing effect size.

### Implications

- Developers using AI feel more productive but may be slower on complex tasks with older tools
- AI increases commit frequency but may decrease code durability
- Quantity metrics (commits, lines, PRs) become less reliable as productivity indicators
- Quality metrics (churn, rework, test coverage) become more important regardless of tool generation

---

## CodeScene Code Health (25+ Factors)

CodeScene scores files on a 1-10 scale using:

1. Function length and complexity
2. Module coupling
3. Deeply nested logic
4. Number of function parameters
5. Code duplication within and across files
6. Comment-to-code ratio
7. File length
8. Change frequency (churn)
9. Knowledge distribution (bus factor)
10. Temporal coupling (files that always change together)

### How to Use

CodeScene's file-level health scores complement this skill's person-level quality scores. A person who consistently touches low-health files may be working in technical debt zones rather than producing low-quality code. Cross-reference D2 (Code Quality) scores with CodeScene hotspot data when available.

---
