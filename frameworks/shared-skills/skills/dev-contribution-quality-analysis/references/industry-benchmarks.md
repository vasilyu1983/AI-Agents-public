# Industry Benchmarks

## Table of Contents

- [Commit-Level Metrics (GitClear, 211M Lines, 2020-2024)](#commit-level-metrics-gitclear-211m-lines-2020-2024)
- [Ghost Engineering Thresholds (Stanford, 50K+ Engineers)](#ghost-engineering-thresholds-stanford-50k-engineers)
- [DORA Metrics (2024 State of DevOps)](#dora-metrics-2024-state-of-devops)
- [DX Core 4 Framework](#dx-core-4-framework)
- [Code Review Benchmarks](#code-review-benchmarks)
- [AI Productivity Paradox (METR, 2025)](#ai-productivity-paradox-metr-2025)
- [CodeScene Code Health (25+ Factors)](#codescene-code-health-25-factors)
- [Candidate-Side Evaluation Tools](#candidate-side-evaluation-tools)

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

- A person's 14-day churn rate of 5.7% matches the 2024 industry average
- Churn below 8% is good by current standards; below 3% is exceptional
- Refactoring ratio above 15% is now significantly above average (industry is at 9.5%)
- Duplication above 12% is at or above average; below 5% is excellent

### GitClear 2026 Cohort (2,172 Developer-Weeks, Jan 2026)

Analysis of Cursor, GitHub Copilot, and Claude Code API-integrated developer data:

| Finding | Value |
|---------|-------|
| Durable code output: power AI users vs. non-users | 4.2x more durable code |
| Output increase 2024 to 2025 (AI power users) | +25% |
| Churn ratio: AI power users vs. non-users | 9x higher churn (but absolute output is also much higher) |

**Critical interpretation**: The 4.2x durable code advantage reflects a selection effect — high-output engineers adopted AI first. AI widened a pre-existing performance gap; it did not uniformly uplift all users. When comparing developers, check whether the AI-user cohort was already higher-performing before adoption.

### GitClear "The Maintainability Gap" (2026, 623M code changes)

Newer release; use these as the current cut-points for structural quality in AI-heavy cohorts (verified 2026-07-13, `https://www.gitclear.com/the_ai_code_quality_maintainability_gap`):

| Finding | Value |
|---------|-------|
| Refactored/moved-code share, YTD 2026 | 3.8% (down from 13% in 2023) |
| Copy/paste share, H1 2026 | 15.7% |
| Error-masking constructs | +47% |
| Cross-file code reuse | -35% |

---

## Ghost Engineering Thresholds (Stanford, 50K+ Engineers)

> **Caveat**: As of June 2026, this study has not been published in a peer-reviewed venue — findings were shared on social media by the researcher. Apply thresholds with caution; treat as directional, not definitive.

| Category | % of Engineers | Definition |
|----------|---------------|------------|
| Ghost engineers | ~9.5% | At or below 10-20% of median productivity |
| Low contributors | ~48.5% (cumulative with ghost) | Fewer than 3 meaningful contributions per month |
| Remote ghost rate | 14% | Ghost rate among fully remote engineers |
| In-office ghost rate | 6% | Ghost rate among in-office engineers |

### Methodology (as reported)

- Simulates 10-expert panel evaluating each commit
- Predicts coding time (r=0.82 with expert judgment, unverified claim)
- Predicts implementation time (r=0.86, unverified claim)
- Analyzes commit content and quantifies impact on codebase

### How to Use

- These thresholds define "not contributing" rather than "low quality"
- Someone in the bottom 10-20% of productivity may still produce high-quality code (just less of it)
- The contribution quality skill measures quality, not quantity — use D1 (Delivery Consistency) for volume calibration

---

## DORA Metrics (2024 State of DevOps)

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment frequency | Multiple/day | Weekly-daily | Monthly-weekly | < Monthly |
| Lead time for changes | < 1 hour | < 1 week | 1-6 months | > 6 months |
| Change failure rate | < 5% | 10-15% | -- | > 30% |
| Time to restore | < 1 hour | < 1 day | < 1 week | > 1 week |

### AI Impact Finding (DORA 2024)

**7.2% decrease in delivery stability for every 25% increase in AI adoption** (DORA 2024). This suggests that AI-assisted code may introduce more failures at the team level even when individual velocity increases.

---

## DORA 2025: State of AI-Assisted Software Development

Released Dec 2025 / published on dora.dev. Methodology changed: moved from low/medium/high/elite clusters to seven team archetypes. Key AI-specific findings, from the report itself:

| Finding | Statistic |
|---------|-----------|
| AI adoption rate | 90% of respondents use AI in daily dev work (up from ~76% the prior year) |
| Throughput direction | AI adoption now correlates with *higher* software delivery throughput — a reversal from the 2024 finding |
| Core narrative | "AI is a mirror and a multiplier" — it amplifies each team's existing strengths or dysfunctions rather than fixing or uniformly improving them |

**Do not attribute vendor telemetry to DORA.** The specific figures "bugs per developer +54%", "incidents per PR +242.7%", and "epics completed per developer +66.2%" are widely repeated alongside DORA 2025 coverage but originate from a separate source: Faros AI's *AI Engineering Report 2026: The Acceleration Whiplash* (proprietary telemetry across 22,000+ developers / 4,000+ teams, published mid-2026), not the DORA survey itself. See the Faros entry below.

### Faros AI 2026: The Acceleration Whiplash (vendor telemetry, not DORA)

| Finding | Statistic |
|---------|-----------|
| Bugs per developer | +54% (vs. +9% in Faros's prior-year dataset) |
| Incidents per PR | +242.7% — production incident probability more than tripled per merged change |
| Epics completed per developer | +66% |
| PR merge rate per developer | +16.2% |
| PR size | +51.3% |
| Median time in PR review | +441% |

This is a single vendor's proprietary telemetry analysis, not a peer-reviewed or industry-consensus study — treat it as directional and re-verify before citing in a formal report.

### Interpretation for D2-D4 Scoring

- Rising bug and incident rates (per Faros telemetry) mean churn and rework thresholds established in DORA 2024 still deserve scrutiny, even where DORA's own 2025 survey shows throughput improving.
- Teams with user-centric focus and strong automated testing show the strongest performance gains; teams without these controls see AI amplify existing quality gaps.
- Whichever source is cited, the shared conclusion holds: AI amplifies what is already there. Strong teams get stronger; struggling teams see existing problems intensify.

---

## DX Core 4 Framework

Unified framework replacing standalone DORA/SPACE with four oppositional dimensions:

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
- Using coefficient of variation for delivery consistency rather than raw commit counts
- Role-calibrating expectations rather than applying uniform thresholds

---

## Code Review Benchmarks

### Google Engineering Practices

- Small CLs: < 200 LOC ideal, never > 1000 LOC
- Review speed: < 1 business day target
- 75% of review value comes from catching maintainability issues, not bugs

### Review Quality (Qodo)

- Optimal review turnaround: within 1 hour
- Reviews lasting 2-3 days lose context
- Shallow reviews (few comments relative to changes) miss issues
- Code review effectiveness degrades sharply above 400 LOC

---

## AI Productivity Paradox (METR, 2025)

Study: "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity" (arxiv 2507.09089). Randomized controlled trial, 16 experienced OS developers, 246 tasks.

| Metric | Finding |
|--------|---------|
| Developer forecast | AI would reduce time by ~24% |
| Post-study self-estimate | AI reduced time by ~20% |
| Measured actual effect | AI increased task time by +19% (CI: +2% to +39%) |
| Gap between perception and reality | 39-44% |

### Follow-Up (Feb 2026)

METR launched a larger follow-up in Aug 2025 using latest AI tools. Recruitment was compromised because developers refused to participate if they could not use AI, making the control group unreliable. Among original-study participants, the effect was -18% speedup (CI: -38% to +9%); among newly recruited developers it was -4% (CI: -15% to +9%). Effect direction is uncertain for 2025-era tools at scale.

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

## Candidate-Side Evaluation Tools

Candidates now use AI agents to evaluate employers with the same rigor that employers use to evaluate candidates.

**Example:** career-ops (github.com/santifer/career-ops, ~60K GitHub stars as of mid-2026, up from ~23K earlier in the year — re-verify before citing, star counts move fast) is a multi-agent Claude Code system that scores job opportunities and companies on a 1.0-5.0 rubric across dimensions including match, comp, culture, and red flags, tailors CVs, and batch-processes listings. Candidates grade companies A-F on criteria including engineering culture, technical challenge, growth trajectory, and compensation.

### Implications for Contribution Quality Analysis

| Employer-Side Metric | Candidate-Side Equivalent | What This Means |
|---------------------|--------------------------|-----------------|
| D1 Delivery Consistency | Company shipping cadence signals | Companies with erratic delivery may be filtered out by candidate AI |
| D2 Code Quality | Tech stack and code health signals | Candidates infer code quality from public repos, tech blog posts, and Glassdoor reviews |
| D5 AI Usage Patterns | Employer AI adoption posture | Companies that ban or poorly integrate AI tools may lose candidates who screen for this |

### Practical Impact

- Engineering quality benchmarks are no longer employer-internal metrics. They are now visible to candidate-side AI through public signals (job descriptions, tech blogs, GitHub repos, employee reviews).
- Companies with strong engineering quality signals attract higher-quality applicants because candidate-side AI ranks them higher.
- When interpreting contribution quality results, consider that the talent pool itself is pre-filtered: the best candidates may never apply to companies with weak public engineering signals.
