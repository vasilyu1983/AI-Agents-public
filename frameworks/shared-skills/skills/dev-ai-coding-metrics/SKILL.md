---
name: dev-ai-coding-metrics
description: "Measures AI coding impact across adoption, delivery, quality, cost, and experience. Use when building ROI scorecards, pilot metrics, or leadership reports for AI coding programs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# AI Coding Metrics

Measures coding assistants and coding agents without collapsing results into vanity metrics or one blended score.

The critical distinction is **mode**: assistants help inline or in chat; agents execute multi-step work and need task-level measurement. Do not measure them as if they were the same thing.

## When to Use This Skill

| Trigger | Example |
|---------|---------|
| Designing a pilot or rollout scorecard | "We're rolling out Copilot to 200 engineers — what do we measure?" |
| Diagnosing usage-up / outcomes-flat | "Seat utilization is 80% but PR throughput is unchanged" |
| Comparing assistant vs. agent workflows | "Should we instrument these separately?" |
| Building an ROI model or leadership report | "Finance wants a renewal decision by Q3" |
| Designing an experiment better than vendor benchmarks | "We can't trust the vendor's numbers — how do we run our own study?" |

## Defaults

| Rule | Rationale |
|------|-----------|
| Start from the decision, not the telemetry available | Prevents instrument-what-is-easy bias |
| Separate assistant and agent funnels | Mixing hides which workflow drives results |
| Pair every speed metric with quality + experience | Speed alone is misleading |
| Aggregate at team level | Individual dashboards become surveillance |
| Treat benchmarks as capability signals, not business KPIs | Benchmark gaps do not equal production gaps |

## Workflow

1. Define the decision.
2. Pick the program mode: assistant, agent, or mixed.
3. Build the minimum viable scorecard.
4. Choose the study design.
5. Produce one deliverable.

## ASCII Flow

```text
AI coding metrics request
  -> decision to support: buy, renew, improve, prove, or diagnose
  -> split mode: assistant, agent, or mixed
  -> select scorecard families: adoption, delivery, quality, economics, experience
  -> choose study design and baseline window
  -> collect team-level and task-level evidence
  -> report confidence, sample size, and confounds
  -> deliver ROI model, dashboard, experiment plan, or executive report
```

## Quick Reference

## Decision to Deliverable Map

| Decision | Default Output |
|----------|----------------|
| buy, renew, or cut a tool | ROI model plus executive report |
| improve adoption | adoption metrics plus survey |
| prove delivery impact | productivity metrics plus experiment plan |
| check quality drift | quality metrics plus dashboard |
| understand trust or friction | developer-experience metrics plus survey |
| evaluate coding agents | agent-execution metrics plus experiment plan |

## Program Modes

| Mode | Unit of Analysis | Primary Emphasis |
|------|------------------|------------------|
| assistant | developer-day, team-week, repo-month | adoption, delivery, quality, experience |
| agent | task, PR, workflow run | task success, merge, revert, review burden, cost per accepted change |
| mixed | team-week plus task-level samples | separate the two funnels before combining results |

## Metric Families

Use the smallest scorecard that can answer the decision:

| Family | What It Tells You |
|--------|-------------------|
| adoption | whether usage is real and sustained |
| delivery | whether software flow is faster where AI actually touches the path |
| quality | whether speed gains are offset by defects, rework, or review burden |
| economics | whether the value justifies tool and operating cost |
| experience | whether developers trust the tool and want to keep using it |
| agent execution | whether autonomous workflows succeed in production, not just in demos |

## Study Design Defaults

Minimum baseline: **8 weeks** of pre-intervention data. Two-week baselines produce noisy causal inference — week-to-week variance in PR throughput, review lag, and defect escape routinely exceeds the signal size of AI tooling effects.

| Situation | Design |
|-----------|--------|
| new pilot, no control group | before/after with ≥8 weeks baseline |
| enough comparable teams | matched A/B or stratified assignment |
| teams resist permanent denial of tools | crossover design |
| agent workflow change on one task family | task-level shadow comparison or reviewer-blind evaluation |
| leadership wants a fast answer | balanced scorecard with explicit caveats, not a causal claim |

## Measurement Checklist

Use before publishing any AI coding report:

- [ ] Baseline established (≥8 weeks before intervention)
- [ ] Assistant and agent funnels tracked separately
- [ ] Every speed metric paired with at least one quality metric
- [ ] Sample size, confidence level, and study design stated
- [ ] Confounds documented (team changes, release pressure, policy changes)
- [ ] Vendor evidence labeled as vendor evidence
- [ ] Usage measured after stabilization (not week-1 novelty period)
- [ ] Review burden and rework cost included in ROI model
- [ ] Aggregated at team level (no manager-visible individual dashboards)

## Current Evidence Posture (as of 2026-07-11)

| Claim | Evidence | Caveat |
|-------|----------|--------|
| AI amplifies existing strengths and weaknesses | DORA 2025 AI report; conditional-impact model confirmed | Not a universal accelerant |
| Experienced developers ~19% slower with early-2025 tools (RCT) | METR July 2025 RCT, realistic open-source tasks | Specific to early-2025 tooling generation |
| METR believes developers more sped-up in 2026 than 2025 | METR Feb 2026 update | 30-50% of participants declined no-AI tasks (selection bias); unreliable signal |
| Self-reported: median 1.4-2x value of work from AI (2026) | METR May 2026 survey, n=349 | Self-report; METR found 40pp gap between perceived and actual gains in 2025 study |
| Throughput +66%, PR review time +441%, incidents per PR +243% | Faros AI 2026 telemetry, 22k devs / 4k teams | Organizational telemetry, not RCT; PRs merged without review up +31% |
| DORA 2025: 90% of developers use AI daily | DORA 2025 AI report | Adoption does not equal delivery impact |
| Modeled first-year AI ROI ~39% (500-person org); adoption raises change-failure rate (5%->6%), an "instability tax" | DORA 2026 ROI of AI-Assisted Software Development report (Apr 2026) | Vendor-modeled scenario, not a cross-org RCT; treat the 39% figure as an illustrative scenario, not a universal benchmark |
| AI yields 35-40% gains on simple tasks but ~10% on complex legacy code | DORA 2026 ROI report | Reinforces task-complexity segmentation already required by this skill's study design defaults |
| DX Core 4 unifies DORA + SPACE + DevEx into 4 dimensions (Speed, Effectiveness, Quality, Business Impact) | DX Core 4, formalized publicly Apr 2026 | Vendor framework; specific benchmarks need independent replication |

## Anti-Gaming Checklist

Reject a scorecard or report if any of the following apply:

- [ ] Single blended AI productivity score mixing usage, speed, sentiment, and quality
- [ ] Seat activation or prompt volume cited as delivery impact
- [ ] Cross-team comparison without controlling for stack, task mix, staffing, or release pressure
- [ ] Measurement period is <8 weeks or includes week-1 novelty window
- [ ] Vendor benchmark cited as production ROI evidence
- [ ] Review burden excluded from ROI model
- [ ] Individual-level AI usage visible to managers
- [ ] Directional before/after movement stated as causal without controlled design

## Navigation

**References**

- [references/adoption-metrics.md](references/adoption-metrics.md) — assistant and agent adoption funnels, metric definitions, stall patterns, privacy rules
- [references/productivity-metrics.md](references/productivity-metrics.md) — DORA and SPACE applied to AI workflows, delivery stack decomposition, confound management
- [references/quality-metrics.md](references/quality-metrics.md) — defect, complexity, test, security, and technical debt metrics with targets and alert thresholds
- [references/roi-framework.md](references/roi-framework.md) — full cost model (including review burden), benefit model, scenario planning, executive report structure
- [references/developer-experience-metrics.md](references/developer-experience-metrics.md) — satisfaction surveys, cognitive load, friction indicators, trust calibration, DX anti-patterns
- [references/agent-execution-metrics.md](references/agent-execution-metrics.md) — agent funnel, core metrics, reviewer burden, scorecards for pilot / scaling / executive decisions
- [references/benchmarking-methodology.md](references/benchmarking-methodology.md) — A/B, before/after, crossover, shadow designs; statistical rigor; confound management
- [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) — bottleneck identification before instrumenting, throughput accounting for ROI, DBR for review-queue protection, CRT for stalled rollouts, evaporating cloud for adoption-vs-quality tensions
- [references/evidence-update.md](references/evidence-update.md) — load when citing current research: METR RCT (2025 baseline), METR 2026 update (selection-bias caveat), DORA 2025 AI report, DX Core 4, Faros 2026 telemetry

**Assets and data**

- [assets/metric-dashboard-template.md](assets/metric-dashboard-template.md)
- [assets/adoption-survey-template.md](assets/adoption-survey-template.md)
- [assets/roi-calculator-template.md](assets/roi-calculator-template.md)
- [assets/executive-report-template.md](assets/executive-report-template.md)
- [assets/experiment-design-template.md](assets/experiment-design-template.md)
- [data/sources.json](data/sources.json)
- [data/sample-ai-metrics.json](data/sample-ai-metrics.json)

**Scripts**

- [scripts/roi_calculator.py](scripts/roi_calculator.py)
- [scripts/README.md](scripts/README.md)

## Cross-References

- [../dev-context-engineering/SKILL.md](../dev-context-engineering/SKILL.md)
- [../ai-agents/SKILL.md](../ai-agents/SKILL.md)
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md)
- [../product-management/SKILL.md](../product-management/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current research claims, benchmark status, and vendor telemetry specifics before final advice.
- Prefer peer-reviewed, official, and first-party telemetry docs over social or vendor marketing claims.
- If live verification is unavailable, mark current-evidence claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

