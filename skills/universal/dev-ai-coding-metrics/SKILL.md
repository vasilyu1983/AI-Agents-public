---
name: dev-ai-coding-metrics
description: "Measures AI coding impact and extension robustness. Use when tracking delivery, quality trajectories, cost, experience, pilots, scorecards, or leadership reporting."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-08-21
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
| Aggregate at team level | Individual dashboards become surveillance; see [Individual-Data Policy](#individual-data-policy) |
| Treat benchmarks as capability signals, not business KPIs | Benchmark gaps do not equal production gaps |

## Workflow

1. Define the decision.
2. Pick the program mode: assistant, agent, or mixed.
3. Build the minimum viable scorecard.
4. Choose the study design.
5. Produce one deliverable.

## Quick Reference

Decision to deliverable:

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
| quality | whether speed gains are offset by defects, rework, review burden, or declining extension robustness |
| economics | whether the value justifies tool and operating cost |
| experience | whether developers trust the tool and want to keep using it |
| agent execution | whether autonomous workflows succeed in production, not just in demos |

## Study Design Defaults

Planning default: **8 weeks** of pre-intervention data. This is a local planning floor, not a research-derived sufficiency threshold: before a causal pilot, compute the minimum detectable effect from the baseline's own week-to-week variance and the number of team-weeks. If that MDE is larger than any effect you would act on, do not run a causal study; report a descriptive scorecard labelled directional.

| Situation | Design |
|-----------|--------|
| new pilot, no control group | difference-in-differences against non-adopting or late-adopting teams, or an interrupted time series with ≥8 pre-period points; a single before/after delta is directional only (it absorbs freezes, reorgs, and hiring waves) |
| enough comparable teams | matched A/B or stratified assignment |
| teams resist permanent denial of tools | crossover design |
| agent workflow change on one task family | task-level shadow comparison or reviewer-blind evaluation |
| leadership wants a fast answer | balanced scorecard with explicit caveats, not a causal claim |

### Cohort and denominator contract

Freeze the measurement population before reading outcomes. Record the eligible population, assignment rule, actual exposure, observation window, and accepted outcome for each metric. Report `eligible`, `assigned`, `exposed`, and `observed` counts side by side; never silently replace the assigned cohort with active users, completed tasks, or merged PRs. That survivor-only denominator makes adoption and success look better precisely when setup failures, abandoned agent runs, or unmerged changes are the problem.

For incomplete observations, name the reason (`not_started`, `abandoned`, `still_open`, `telemetry_missing`, or `excluded_by_rule`) and keep it in the funnel. Treat still-open work as right-censored rather than failed until the outcome window closes. A report may be directional with imperfect telemetry, but it must state which denominator supports each percentage and how missing cases could change the decision.

When exporting GitHub PRs, retain open, closed-unmerged, and merged outcomes in the opened-since cohort. A PR export cannot recover assigned tasks that never produced a PR; join it to the task registry before reporting agent success. Treat author-level CSV as restricted source data under the Individual-Data Policy.

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
- [ ] Edit-capable agents measured across evolving-spec checkpoints, including late-checkpoint cost and quality slopes
- [ ] Aggregated at team level (no manager-visible individual dashboards)

## Evidence Rules

Durable rules from the research; the dated studies, figures, and caveats live in [references/evidence-update.md](references/evidence-update.md):

- AI amplifies existing system strengths and weaknesses; it is not a universal accelerant.
- Perceived and measured gains can differ; never report self-reported gains as measured impact.
- Throughput gains can shift load to review and incidents; pair any throughput gain with review-burden and incident metrics.

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
- [ ] SlopCodeBench averages or trajectory signals used as organizational targets or causal ROI evidence

## Individual-Data Policy

This is the one policy for person-level data, shared with `dev-contribution-quality-analysis` (which points here):

- Team level by default. AI usage and AI-assist metrics are never shown to managers per person and never feed performance, promotion, or staffing decisions.
- Person-level output is allowed only as opt-in self-review or coaching, shown to the person first, with the sampled evidence and a correction path.
- Questions about individuals ("who uses AI well", "per-engineer quality") route to `dev-contribution-quality-analysis` under these limits; team-level AI-tool impact stays here.

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
- [references/evidence-update.md](references/evidence-update.md) — dated citations with caveats: METR RCT (2025), METR 2026 update (selection-bias caveat), DORA 2025 AI report, DORA 2026 ROI report, DX Core 4, Faros 2026 telemetry, SlopCodeBench

**Assets and data**

- [assets/metric-dashboard-template.md](assets/metric-dashboard-template.md)
- [assets/adoption-survey-template.md](assets/adoption-survey-template.md)
- [assets/roi-calculator-template.md](assets/roi-calculator-template.md)
- [assets/executive-report-template.md](assets/executive-report-template.md)
- [assets/experiment-design-template.md](assets/experiment-design-template.md)
- [data/sources.json](data/sources.json)
- [data/sample-ai-metrics.json](data/sample-ai-metrics.json)

**Scripts**

- [scripts/roi_calculator.py](scripts/roi_calculator.py) — when calculating a capacity-value scenario, supply the observation period and both measured burden terms; zero-cost ROI is undefined. Per-family rating bands are illustrative local rubrics, not validated constructs.
- [scripts/extract_github_events.py](scripts/extract_github_events.py) — when collecting the PR outcome cohort or commit telemetry; look up GitHub endpoint permissions and rate-limit guidance before a live export.
- [scripts/README.md](scripts/README.md)

## Cross-References

- [../dev-contribution-quality-analysis/SKILL.md](../dev-contribution-quality-analysis/SKILL.md) — per-person or team contribution quality from commit and PR history, under the [Individual-Data Policy](#individual-data-policy)
- [../dev-context-engineering/SKILL.md](../dev-context-engineering/SKILL.md)
- [../ai-agents/SKILL.md](../ai-agents/SKILL.md)
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md)
- [../product-management/SKILL.md](../product-management/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
