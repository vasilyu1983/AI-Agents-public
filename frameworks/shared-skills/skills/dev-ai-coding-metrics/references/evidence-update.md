# What Changed Since 2025 (as of 2026-07)

_Verified 2026-07-11. Synthesizes METR 2025 RCT, METR Feb 2026 update, METR May 2026 survey, DORA 2025 AI report, DORA 2026 ROI report, DX Core 4, and Faros 2026 telemetry._

## METR RCT (the 2025 baseline)

METR's randomized controlled trial (data Feb–Jun 2025, published 2025-07-10) found experienced open-source developers were **~19% slower** with early-2025 AI tools than without them — the opposite of developer self-predictions. Primary URL: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

## METR 2026 Update (selection bias caveat)

In their 2026-02-24 update, METR stated they believe developers are likely **more sped up** in early 2026 than early-2025 estimates. However, their new experiment is unreliable: **30–50% of participating developers declined to submit tasks they didn't want to do without AI** — a self-selection mechanism that inflates apparent AI benefit. Do not cite as clean evidence of productivity gains. Primary URL: https://metr.org/blog/2026-02-24-uplift-update/

**Combined METR read**: the 2025 generation of tools caused slowdowns in real conditions; the 2026 generation likely improves this, but the measurement problem is now worse, not better.

## DORA 2025 AI-Assisted Report

DORA's dedicated AI-assisted software development report (Google Cloud, 2025) reinforces the conditional-impact model: AI amplifies existing strengths and weaknesses rather than being a universal accelerant. Canonical URL: https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report

## DORA 2026: ROI of AI-Assisted Software Development

Published by Google Cloud's DORA program (report dated 2026.01, widely covered from April-May 2026), this is a distinct follow-up to the 2025 AI-assisted report and should be cited separately, not conflated with it. Canonical URL: https://dora.dev/ai/roi/report/

Three load-bearing contributions for this skill:

1. **The J-Curve model.** Organizations see an initial productivity *dip* after AI rollout before gains materialize, driven by three costs: the learning curve as teams adapt workflows, a "verification tax" from reviewing higher-volume AI-generated output, and downstream process friction (testing, approvals) that has not yet adapted to the new code volume. The report frames this as "the tuition cost of transformation" and recommends budgeting for it explicitly rather than treating a slow first quarter as a rollout failure. This directly supports this skill's existing "before/after" study design defaults (do not compare baseline to the ramp-up period).
2. **Scenario-based ROI, not a single number.** The report's own illustrative model (500-person engineering org) shows a ~39% first-year ROI ($11.6M value against $8.4M investment, ~8-month payback) — but explicitly frames this as one scenario among conservative/realistic/optimistic ranges, reinforcing this skill's existing rule against a single headline ROI figure.
3. **The "instability tax."** AI adoption is associated with higher individual effectiveness and code quality in the report's model, but also with rising delivery instability — the sample model shows change failure rate rising from 5% to 6%, producing a modeled ~$344K negative downtime impact. The report also finds AI yields 35-40% productivity gains on simple, well-scoped tasks but only ~10% on complex legacy code, reinforcing this skill's task-complexity segmentation rule (`benchmarking-methodology.md`, C1-C4 complexity levels).

Use this report to strengthen `roi-framework.md` scenario planning and the anti-gaming checklist's ban on single blended ROI numbers — but treat the specific dollar and percentage figures as an illustrative vendor model, not a transferable benchmark for any given organization.

## DX Core 4

DX Core 4's four dimensions (Speed, Effectiveness, Quality, Business Impact) were formalized and publicly presented at the DX Annual 2026 conference (April 16, 2026), unifying DORA, SPACE, and DevEx into one framework with a Developer Experience Index (DXI) composite under "Effectiveness." Treat this as a later formalization than earlier DX Core 4 commentary; cite 2026, not 2024, as the reference point going forward. Treat specific DX benchmark figures (e.g. "27.4% of production code is AI-generated," "developers save ~3h45m/week") as vendor evidence pending independent replication. URL: https://getdx.com/research/dx-core-4/

## METR May 2026 Self-Reported Survey

Survey of 349 technical workers (87 engineers, 71 researchers, 129 academics/PhD students, 48 founders/managers), conducted Feb–Apr 2026, published 2026-05-11. Median self-reported value-of-work change: **1.4–2x** (retrospective 1.3x for Mar 2025, 2x for Mar 2026, forecast 2.5x for Mar 2027). METR notes significant reasons for skepticism: their 2025 RCT found participants overestimated AI's time effect by 40 percentage points on average. Do not cite these as controlled evidence of productivity gains. Primary URL: https://metr.org/blog/2026-05-11-ai-usage-survey/

**Combined METR read through June 2026**: self-reported gains are rising but consistently overestimated vs. controlled measures; the measurement problem is getting harder, not easier, as willingness to work without AI declines.

## Faros AI 2026 Telemetry

Organizational telemetry (not RCT) from Faros AI, covering 22,000 developers across 4,000 teams. Key figures at highest vs. lowest AI adoption within each org:

- Average PR size: **+51.3%**
- Files touched per developer per month: **+149.9%**
- PRs merged without any review: **+31.3%**
- Lead time commit to production: **+480.4%**
- Throughput (epics per developer): **+66%** (also reported as +66.2%; task completion per developer +33.7%; PR merge rate per developer +16.2%)
- Incidents per PR: **+243%** (also reported as +242.7%)
- Bugs per developer: **+54%**
- Median PR review time: **+441.5%**
- Code churn: **+861%**

The review-bypass, lead-time, and code-churn figures are the most operationally significant. Throughput rises; downstream review capacity, quality gates, and incident load do not keep pace. Source: https://www.faros.ai/research/ai-acceleration-whiplash

## Key implication for measurement

The 2025→2026 period makes the measurement case stronger, not weaker: faster output without paired review-capacity and incident-tracking instrumentation produces a misleading picture. Any scorecard built with this skill should include review burden, PR-merge-without-review rate, and defect-escape metrics alongside delivery speed.
