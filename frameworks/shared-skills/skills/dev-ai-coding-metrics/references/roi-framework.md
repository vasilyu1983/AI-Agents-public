# ROI Framework for AI Coding Programs

Use this reference when the user needs an investment decision, renewal recommendation, or executive summary. The goal is not to prove AI is valuable. The goal is to estimate whether a specific program creates enough value to justify its cost under realistic assumptions.

---
## Table of Contents

- [Evidence Standard](#evidence-standard)
- [ROI Questions This File Helps Answer](#roi-questions-this-file-helps-answer)
- [Cost Model](#cost-model)
- [1. Direct Tooling Cost](#1-direct-tooling-cost)
- [2. Enablement Cost](#2-enablement-cost)
- [3. Review and Governance Cost](#3-review-and-governance-cost)
- [4. Transition Cost](#4-transition-cost)
- [5. Failure Cost](#5-failure-cost)
- [Benefit Model](#benefit-model)
- [1. Time Saved on Accepted Work](#1-time-saved-on-accepted-work)
- [2. Review Efficiency](#2-review-efficiency)
- [3. Quality Savings](#3-quality-savings)
- [4. Knowledge and Onboarding Gains](#4-knowledge-and-onboarding-gains)
- [5. Strategic Option Value](#5-strategic-option-value)
- [Minimum Viable ROI Formulas](#minimum-viable-roi-formulas)
- [Program ROI](#program-roi)
- [Payback Period](#payback-period)
- [Cost per Accepted Change](#cost-per-accepted-change)
- [Cost per Merged Agent PR](#cost-per-merged-agent-pr)
- [The J-Curve: Do Not Judge ROI From the First Quarter](#the-j-curve-do-not-judge-roi-from-the-first-quarter)
- [Scenario Planning](#scenario-planning)
- [What to Count as Benefit](#what-to-count-as-benefit)
- [Review Cost Is Not Optional](#review-cost-is-not-optional)
- [Benchmark and Research Caveats](#benchmark-and-research-caveats)
- [Executive Reporting Structure](#executive-reporting-structure)
- [Common ROI Failure Modes](#common-roi-failure-modes)
- [Recommended Default Deliverables](#recommended-default-deliverables)
- [For a pilot](#for-a-pilot)
- [For an agent rollout](#for-an-agent-rollout)
- [For renewal](#for-renewal)
- [What to Do Next](#what-to-do-next)


## Evidence Standard

Default:

- do not use a single headline ROI number without a scenario table
- do not use vendor benchmarks as the main evidence base
- do not assume positive net delivery impact
- do not treat benchmark scores as business value

Strong evidence order:

1. internal production data
2. controlled or staggered internal comparisons
3. peer-reviewed or independent external studies
4. first-party tool telemetry docs
5. vendor marketing or consulting estimates

If an assumption comes from level 4 or 5, label it clearly.

---

## ROI Questions This File Helps Answer

- should we buy or renew this tool?
- should we expand from pilot to broad rollout?
- is the agent workflow worth the review overhead?
- is the current program creating enough accepted value for its cost?

---

## Cost Model

Always include visible and hidden costs.

### 1. Direct Tooling Cost

Typical components:

- seat or subscription spend
- premium admin / enterprise tier spend
- API or model inference spend
- sandbox / runner / compute cost for agents
- storage and observability cost for traces, logs, and artifacts

### 2. Enablement Cost

Typical components:

- rollout and onboarding time
- documentation and playbook creation
- champion or enablement owner time
- training sessions and office hours

### 3. Review and Governance Cost

Typical components:

- security and legal review
- admin overhead
- policy maintenance
- reviewer time spent checking AI-produced work

### 4. Transition Cost

Typical components:

- learning curve slowdown
- dual-tool overlap during transition
- workflow churn from changing tools or policies

### 5. Failure Cost

Typical components:

- reverted PRs
- production incidents
- security exceptions
- wasted agent runs
- duplicated work after handoff failure

---

## Benefit Model

Only count benefits that are credible in your environment.

### 1. Time Saved on Accepted Work

Use when you can observe:

- faster delivery on retained work
- lower time to first meaningful artifact
- fewer manual steps for repeated workflows

Do not count time "saved" on output that is later rewritten or rejected.

### 2. Review Efficiency

Use when:

- review cycles decline without quality loss
- reviewer effort per accepted change falls

This is especially important for coding agents. An agent that creates more PRs but consumes more reviewer time may destroy ROI.

### 3. Quality Savings

Use when you can show:

- fewer escaped defects
- fewer hotfixes
- lower revert rate
- fewer security findings on new code

### 4. Knowledge and Onboarding Gains

Use when you can show:

- faster time to first meaningful contribution
- fewer blockers for less familiar codebases
- faster issue triage or codebase orientation

### 5. Strategic Option Value

Use cautiously. This includes:

- faster prototyping
- more experiments per quarter
- faster incident triage

This can matter, but it is easier to overstate than hard savings.

---

## Minimum Viable ROI Formulas

### Program ROI

```text
ROI (%) =
  (Total realized benefit - Total program cost)
  / Total program cost
  x 100
```

### Payback Period

```text
Payback period (months) =
  Initial and rollout cost
  / Average monthly net benefit
```

### Cost per Accepted Change

Useful for mixed or agent-heavy programs.

```text
Cost per accepted change =
  total tool + operational cost in period
  / accepted changes in period
```

Accepted change should be one of:

- merged PR
- shipped task
- completed run with accepted human handoff

Pick one and stay consistent.

### Cost per Merged Agent PR

```text
Cost per merged agent PR =
  agent operating cost + allocated reviewer cost
  / merged agent-created PRs
```

This is often more decision-useful than top-level ROI during an early agent rollout.

---

## The J-Curve: Do Not Judge ROI From the First Quarter

DORA's 2026 ROI of AI-Assisted Software Development report names a pattern this skill already implies through its baseline and ramp-up rules: AI programs typically show a productivity **dip** before they show a gain. Three costs drive the dip:

1. **Learning curve** — teams are still adapting workflows to the tool.
2. **Verification tax** — reviewers spend more time checking a higher volume of AI-generated output before trusting it.
3. **Downstream friction** — testing, approval, and release processes have not yet adapted to the new code volume, so they become the bottleneck (see `theory-of-constraints-applied.md`).

Treat this dip as "tuition," not failure. Budget for it explicitly in the ROI model rather than pausing or cutting the program after a disappointing first quarter. Do not compare month-1 numbers to the target state; compare them to the pre-rollout baseline and expect the trend line, not the point estimate, to justify the investment. This is why the Study Design Defaults above require an 8+ week stabilized-usage window before judging impact.

## Scenario Planning

Use three scenarios, not one.

| Scenario | Assumptions | Typical Use |
|----------|-------------|-------------|
| Conservative | lower adoption, lower retained value, higher review cost | board or finance review |
| Base | observed adoption and observed quality-adjusted gains | operating plan |
| Upside | higher adoption and validated workflow expansion | planning, not commitment |

For each scenario vary:

- adoption rate
- retained time savings
- reviewer effort
- defect / revert cost
- infrastructure or inference cost

Do not vary only the upside assumptions.

---

## What to Count as Benefit

Count it when:

- the work was accepted, retained, or deployed
- the quality cost is known or bounded
- the evidence comes from observed data or a defensible sample

Do not count it when:

- it comes from a benchmark score only
- it comes from raw suggestion acceptance alone
- it comes from self-report with no operational corroboration
- it comes from a task that produced follow-up rework or policy exceptions

---

## Review Cost Is Not Optional

Most weak AI ROI models ignore reviewer time. Do not.

For assistants:

- measure review rounds
- measure requested-changes rate
- sample reviewer effort on accepted AI-heavy PRs

For agents:

- measure reviewer minutes per PR or per accepted task
- measure takeover and rework after "successful" completion
- allocate reviewer cost into unit economics

If reviewer effort rises faster than accepted value, the program is not scaling cleanly.

---

## Benchmark and Research Caveats

Use external research to bound assumptions, not to replace internal evidence.

Apply these rules:

1. If a study uses simple or lab-style tasks, discount its transferability to your repos.
2. If a benchmark is saturated, treat it as capability evidence, not ROI evidence.
3. If a claim comes from a vendor study, say it is vendor evidence.
4. If internal usage is assistant-heavy but the external study is agent-heavy, do not transfer the number directly.

Suggested language:

> External studies inform the assumption range, but the business case is anchored to our own accepted-work and review-cost data.

---

## Executive Reporting Structure

A good executive summary answers four questions:

1. What did we spend?
2. What accepted value did we get?
3. What risks or hidden costs offset that value?
4. What is the decision recommendation?

Use this sequence:

- program scope and measurement period
- scenario table
- top drivers of value
- top drivers of cost
- quality and safety caveats
- recommendation: expand, hold, narrow, or stop

---

## Common ROI Failure Modes

| Failure Mode | Why It Breaks the Model |
|-------------|--------------------------|
| counting all generated code as value | generated code is not accepted value |
| ignoring rework and revert cost | inflates benefit materially |
| ignoring reviewer labor | especially bad for agents |
| counting benchmark wins as dollars | benchmark != business impact |
| assuming all teams benefit equally | task mix and repo quality matter |
| using a honeymoon period | novelty inflates the early signal |
| mixing assistant and agent costs in one bucket | hides which workflow actually pays |

---

## Recommended Default Deliverables

### For a pilot

- conservative / base / upside ROI table
- cost per active user
- cost per accepted change
- recommendation with caveats

### For an agent rollout

- cost per merged PR
- reviewer effort trend
- takeover rate
- revert / exception rate
- recommendation on task envelope expansion

### For renewal

- trailing 2-3 quarter trend
- adoption by segment
- accepted work per dollar spent
- comparison to next-best alternative or to no-tool baseline

---

## What to Do Next

- For operating metrics, pair this file with `productivity-metrics.md`.
- For agentic unit economics, pair this file with `agent-execution-metrics.md`.
- For experiments, pair this file with `benchmarking-methodology.md`.
- For executive packaging, use `assets/executive-report-template.md` and `assets/roi-calculator-template.md`.
