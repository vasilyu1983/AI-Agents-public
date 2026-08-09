# Productivity and Delivery Metrics for AI-Augmented Teams

Operational guidance for measuring how AI coding assistants and agents affect software delivery. This file keeps the DORA and SPACE framing, but it does **not** assume AI automatically improves throughput.

---
## Table of Contents

- [Evidence Posture](#evidence-posture)
- [The Delivery Stack](#the-delivery-stack)
- [Core Delivery Metrics](#core-delivery-metrics)
- [Recommended Companion Metrics](#recommended-companion-metrics)
- [DORA Metrics Applied Carefully](#dora-metrics-applied-carefully)
- [Deployment Frequency](#deployment-frequency)
- [Lead Time for Changes](#lead-time-for-changes)
- [Change Failure Rate](#change-failure-rate)
- [Mean Time to Recovery](#mean-time-to-recovery)
- [SPACE Applied to AI Workflows](#space-applied-to-ai-workflows)
- [Satisfaction and Well-Being](#satisfaction-and-well-being)
- [Performance](#performance)
- [Activity](#activity)
- [Communication and Collaboration](#communication-and-collaboration)
- [Efficiency and Flow](#efficiency-and-flow)
- [Assistant vs Agent Delivery Metrics](#assistant-vs-agent-delivery-metrics)
- [Assistant-Heavy Teams](#assistant-heavy-teams)
- [Agent-Heavy Teams](#agent-heavy-teams)
- [Benchmark-to-Production Gap](#benchmark-to-production-gap)
- [Study Design Guidance](#study-design-guidance)
- [Before / After](#before-after)
- [Matched A/B or Stratified Assignment](#matched-ab-or-stratified-assignment)
- [Crossover](#crossover)
- [Task-Level Shadow or Blind Review](#task-level-shadow-or-blind-review)
- [Confounds That Frequently Break AI Delivery Analysis](#confounds-that-frequently-break-ai-delivery-analysis)
- [Reporting Rules](#reporting-rules)
- [What to Do Next](#what-to-do-next)


## Evidence Posture

Use this as the starting stance:

- DORA 2025 treats AI as an amplifier of existing system quality and accessibility, not a guaranteed accelerator.
- METR's July 2025 randomized trial found experienced open-source developers were slower on realistic tasks in that setting.
- Benchmark performance and production delivery performance diverge quickly.

Therefore:

- do not start with a positive expected impact
- start with a falsifiable hypothesis and a baseline
- decompose the delivery system instead of using one topline number

---

## The Delivery Stack

AI can affect different parts of delivery differently. Always decompose the path.

```
task assigned
  -> active work starts
  -> first meaningful artifact
  -> PR opened
  -> review completed
  -> merged
  -> deployed
  -> production stable
```

Good measurement usually finds that AI helps some segments and leaves others unchanged.

---

## Core Delivery Metrics

| Metric | Default Definition | Why It Matters |
|--------|--------------------|----------------|
| Time to first meaningful artifact | task start -> draft code / plan / PR | catches inner-loop acceleration |
| PR open latency | task start -> PR opened | useful for assistant and agent workflows |
| Review turnaround time | review request -> approval / changes requested | often the hidden bottleneck |
| Lead time for changes | commit -> production | standard DORA metric |
| Cycle time | active work start -> deploy | broad delivery signal |
| Deployment frequency | deploys per service or team per period | detects system-level acceleration |
| Change failure rate | failed deploys / total deploys | speed without stability is not success |
| Mean time to recovery | incident detection -> restored service | tests whether AI helps incident response |

### Recommended Companion Metrics

Pair delivery metrics with:

- defect escape rate
- revert rate
- review burden
- satisfaction or trust burden

Do not publish a delivery-only dashboard.

---

## DORA Metrics Applied Carefully

### Deployment Frequency

Use:

- deploys per team or service per week
- segmented by change type if possible: feature, fix, config, dependency, docs

Interpretation:

- increased deployment frequency can be real improvement
- it can also be caused by smaller PRs, service sprawl, or release process changes

### Lead Time for Changes

Measure:

- commit -> production
- plus a decomposed view:
  - task start -> first meaningful artifact
  - PR open -> merge
  - merge -> production

Interpretation:

- AI often affects the first two segments more than the last one
- if only the first segment improves, infrastructure or approval flow may be the real constraint

### Change Failure Rate

Measure:

- failed deploys / total deploys
- and, when feasible, compare AI-assisted vs non-AI-assisted changes by task type

Interpretation:

- a flat or rising change failure rate can erase delivery gains
- do not treat more deployments as success if failure rate rises

### Mean Time to Recovery

Measure:

- incident detection -> service restored
- optionally split diagnosis time vs fix time

Interpretation:

- AI may help diagnosis, log search, or code search even when it does not improve feature delivery

---

## SPACE Applied to AI Workflows

### Satisfaction and Well-Being

Ask:

- do AI tools reduce toil?
- do they increase pressure or trust burden?

Use `developer-experience-metrics.md`.

### Performance

Measure outcomes, not output volume.

Good:

- time to customer-visible improvement
- bugs fixed
- incidents resolved
- reviewer effort for accepted changes

Avoid:

- lines of code
- raw prompt count
- raw PR count without quality context

### Activity

Useful activity measures:

- PRs merged by task type
- test cases created and retained
- documentation updates completed
- incidents diagnosed with AI assistance

Activity is only useful when paired with performance and quality.

### Communication and Collaboration

AI can shift coordination burden rather than remove it.

Measure:

- review rounds per PR
- comments per accepted AI-generated PR
- follow-up clarification requests
- time spent explaining agent output

### Efficiency and Flow

Measure:

- uninterrupted coding block time
- handoff frequency
- context switching caused by tool failures or retries

This is where many "it feels faster" claims live. Validate them with sampled task data.

---

## Assistant vs Agent Delivery Metrics

### Assistant-Heavy Teams

Good default metrics:

- time to first meaningful artifact
- PR open latency
- review turnaround
- lead time for changes
- defect escape rate

### Agent-Heavy Teams

Good default metrics:

- task completion rate
- human takeover rate
- reviewer effort per accepted task
- PR merge rate
- post-merge revert rate
- cost per accepted change

If the workflow is agent-heavy, see `agent-execution-metrics.md` first and only then roll up to team delivery metrics.

---

## Benchmark-to-Production Gap

Always track the gap between benchmark performance and production acceptance.

| Signal | Why It Matters |
|--------|----------------|
| benchmark score | capability ceiling, often on narrow tasks |
| task completion in your repos | practical usefulness |
| reviewer acceptance | real-world quality threshold |
| revert / hotfix rate | downstream reliability |

Common failure mode:

- benchmark performance rises
- invocation rises
- merge rate stays flat
- review burden rises

That is not a delivery win.

---

## Study Design Guidance

### Before / After

Use when:

- tool is already rolling out
- you cannot withhold access

Requirements:

- 8-12 week baseline
- same metric definitions before and after
- stable team composition where possible

### Matched A/B or Stratified Assignment

Use when:

- you have enough comparable teams
- leadership wants stronger causal evidence

Control for:

- team size
- stack
- project type
- seniority mix
- release cadence

### Crossover

Use when:

- teams object to permanent denial of tooling
- you can tolerate a longer study

### Task-Level Shadow or Blind Review

Use when:

- evaluating coding agents on a narrow workflow
- reviewer acceptance is the key business question

See `benchmarking-methodology.md`.

---

## Confounds That Frequently Break AI Delivery Analysis

| Confound | Failure Mode |
|----------|--------------|
| review policy change | looks like AI sped delivery when policy did |
| team composition change | senior hire or attrition distorts trend |
| release calendar / crunch period | short-term throughput spike misread as tool effect |
| service or repo restructuring | changes deployment frequency mechanically |
| measurement novelty | developers change behavior because they know they are measured |
| tool mandate | adoption rises while satisfaction and quality worsen |

Document confounds in every report.

---

## Reporting Rules

When summarizing delivery impact:

1. report the baseline period
2. state the unit of analysis
3. show at least one quality metric next to each speed metric
4. include sample size and data coverage
5. distinguish measured effects from self-reported effects
6. separate assistant and agent workflows if both are in scope

Suggested one-line summary format:

> Over a 12-week stabilized period, assistant usage increased time-to-first-artifact speed while review time and defect escape were unchanged; agent usage increased PR creation but not merge rate, so net delivery impact remains mixed.

---

## What to Do Next

- For causal rigor, use `benchmarking-methodology.md`.
- For quality guardrails, use `quality-metrics.md`.
- For agent-level operational metrics, use `agent-execution-metrics.md`.
- For leadership decisions, pair this file with `roi-framework.md`.
