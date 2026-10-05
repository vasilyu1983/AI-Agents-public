# Evidence (Dated Citations)

_Dated citations with each study's own caveat: METR 2025 RCT, METR Feb 2026 update, METR May 2026 survey, DORA 2025 AI report, DORA 2026 ROI report, DX Core 4, Faros 2026 telemetry, and SlopCodeBench v1. Before quoting any figure as current, open the primary source and check whether a newer edition supersedes it; the figures here are evidence for the durable rules in SKILL.md, not targets._

Durable rules these sources support (kept in SKILL.md): AI amplifies existing system strengths and weaknesses; perceived gains can differ from measured gains; throughput gains can shift load to review and incidents.

## SlopCodeBench v1 (extension robustness)

The March 2026 preprint evaluates coding agents across evolving specifications while carrying forward each agent's own workspace and starting each checkpoint without the prior conversation context. Its central measurement implication is that snapshot pass rates can miss degrading extensibility; trajectory-level structural erosion and verbosity reveal a different dimension of performance. Its prompt intervention improved initial quality but did not halt degradation, so planning or quality prompts are not substitutes for longitudinal evaluation. Primary URL: https://arxiv.org/abs/2603.24755v1

Use the paper to justify checkpoint-level extension-robustness, quality-slope, cost, and review-burden measurement. Do not use its model averages as organizational targets or infer that the quality signals cause correctness or ROI outcomes. The reported experiments are Python-only, and the article is a preprint.

## METR RCT (the 2025 baseline)

METR's randomized controlled trial (data Feb–Jun 2025, published 2025-07-10) found experienced open-source developers were **~19% slower** with early-2025 AI tools than without them — the opposite of developer self-predictions. Primary URL: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

## METR 2026 Update (selection bias caveat)

In their 2026-02-24 update, METR stated they believe developers are likely **more sped up** in early 2026 than early-2025 estimates. However, their new experiment is unreliable: **30–50% of participating developers declined to submit tasks they didn't want to do without AI** — METR argues this selection likely biases estimated AI-assisted speedup downwards, because high-expected-uplift tasks and enthusiastic developers are missing. Do not cite as clean evidence of productivity gains. Primary URL: https://metr.org/blog/2026-02-24-uplift-update/

**Combined METR read**: the 2025 generation of tools caused slowdowns in real conditions; the 2026 generation likely improves this, but the measurement problem is now worse, not better.

## DORA 2025 AI-Assisted Report

DORA's dedicated AI-assisted software development report (Google Cloud, 2025) reinforces the conditional-impact model: AI amplifies existing strengths and weaknesses rather than being a universal accelerant. Load the full report before quoting adoption or time-use figures; the prior figures are unverified against the landing page and removed. Canonical URL: https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report

## DORA 2026: ROI of AI-Assisted Software Development

Published by Google Cloud's DORA program (report dated 2026.01, widely covered from April-May 2026), this is a distinct follow-up to the 2025 AI-assisted report and should be cited separately, not conflated with it. Canonical URL: https://dora.dev/ai/roi/report/

The primary landing page describes an initial productivity dip and provides an ROI calculator. Load the report and its errata before using scenario figures, financial assumptions, or task-complexity estimates. The previously quoted first-year ROI, payback, downtime, and productivity percentages are unverified here and have been removed. Use internally measured costs and conservative/base/upside assumptions; a report's illustrative model is not a transferable benchmark.

## DX Core 4

DX Core 4 is a vendor measurement framework. Load the publisher's framework definition before adopting its dimensions or scoring; its page was unavailable during this check. Previously quoted AI-code and hours-saved figures are unverified and removed. URL: https://getdx.com/research/measuring-developer-productivity-with-the-dx-core-4/

## METR May 2026 Self-Reported Survey

Survey of 349 technical workers (87 engineers, 71 researchers, 129 academics/PhD students, 48 founders/managers), conducted Feb–Apr 2026, published 2026-05-11. Median self-reported value-of-work change: **1.4–2x** (retrospective 1.3x for Mar 2025, 2x for Mar 2026, forecast 2.5x for Mar 2027). METR notes significant reasons for skepticism: their 2025 RCT found participants overestimated AI's time effect by 40 percentage points on average. Do not cite these as controlled evidence of productivity gains. Primary URL: https://metr.org/blog/2026-05-11-ai-usage-survey/

**Combined METR read (2025 RCT, 2026 update, 2026 survey)**: self-reported gains are rising but consistently overestimated vs. controlled measures; the measurement problem is getting harder, not easier, as willingness to work without AI declines.

## Faros AI 2026 Telemetry

Faros's publisher page reports increased throughput alongside rising bugs, incidents, review time, and churn. This is vendor observational telemetry, not randomized evidence that AI caused the changes. Its page links a subsequent update; load the report edition and verify the cohort, comparison, denominators, and uncertainty before quoting magnitudes. Previously quoted precise percentages not visible in the checked landing-page text are unverified and removed. Source: https://www.faros.ai/research/ai-acceleration-whiplash

## Key implication for measurement

The 2025→2026 period makes the measurement case stronger, not weaker: faster output without paired review-capacity and incident-tracking instrumentation produces a misleading picture. Any scorecard built with this skill should include review burden, PR-merge-without-review rate, and defect-escape metrics alongside delivery speed.
