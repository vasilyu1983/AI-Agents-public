# Agent Execution Metrics

Use this reference when the workflow involves coding agents that can plan, edit files, run tests, open PRs, or complete multi-step tasks. These metrics are different from assistant metrics because the unit of value is usually a **task** or **accepted change**, not a suggestion.

---
## Table of Contents

- [Why Agent Metrics Need Their Own Model](#why-agent-metrics-need-their-own-model)
- [The Agent Funnel](#the-agent-funnel)
- [Core Metrics](#core-metrics)
- [Recommended Event Model](#recommended-event-model)
- [Interpreting the Funnel](#interpreting-the-funnel)
- [Minimum Viable Scorecards](#minimum-viable-scorecards)
- [Scorecard A: Early Agent Pilot](#scorecard-a-early-agent-pilot)
- [Scorecard B: Scaling Agent Workflow](#scorecard-b-scaling-agent-workflow)
- [Scorecard C: Executive Decision](#scorecard-c-executive-decision)
- [Reviewer Burden](#reviewer-burden)
- [Quality and Safety](#quality-and-safety)
- [Benchmark Use](#benchmark-use)
- [Segmentation](#segmentation)
- [Study Designs That Work Well for Agents](#study-designs-that-work-well-for-agents)
- [Executive Summary Template](#executive-summary-template)
- [Anti-Patterns](#anti-patterns)
- [What to Do Next](#what-to-do-next)


## Why Agent Metrics Need Their Own Model

Assistant metrics answer:

- did the tool help a developer in the flow of work?

Agent metrics answer:

- did the workflow complete useful work with acceptable human oversight and acceptable downstream quality?

This means the key questions change:

- what percentage of runs actually finish?
- how often does a human need to intervene?
- how much reviewer effort is required for accepted output?
- how often does accepted output survive after merge?

---

## The Agent Funnel

Measure the full funnel:

```text
task created
  -> task started
  -> run completes
  -> human accepts for review
  -> PR opens
  -> PR merges
  -> no revert / no hotfix / no policy exception
```

If you only measure the first half of the funnel, you will overstate value.

---

## Core Metrics

| Metric | Definition | Why It Matters |
|--------|------------|----------------|
| Task completion rate | completed runs / started runs | top-of-funnel outcome |
| Human takeover rate | runs requiring rescue / started runs | reliability and scope fit |
| Acceptance-for-review rate | outputs accepted for PR or handoff / completed runs | catches superficial "success" |
| PR merge rate | merged PRs / PRs opened by agent | real-world acceptance |
| Revert or hotfix rate | reverted or hotfixed merged PRs / merged PRs | downstream reliability |
| Reviewer effort per accepted task | reviewer minutes, comments, or rounds / accepted task | hidden human cost |
| Policy / security exception rate | exceptions / started runs | safety boundary signal |
| Cost per accepted task | total operating cost / accepted tasks | unit economics |
| Cost per merged PR | total operating + reviewer cost / merged agent PRs | scaling decision |
| Benchmark-to-production gap | benchmark score vs merge / revert outcomes | anti-self-deception metric |
| Extension robustness | retained correctness and acceptable quality across an evolving-spec, carried-workspace checkpoint sequence | reveals deterioration hidden by one-shot completion |
| Structural erosion slope | change in structural-erosion signal across ordered checkpoints | detects complexity concentrating as the workspace evolves |
| Verbosity slope | change in locally defined redundancy/clone signal across ordered checkpoints | detects redundant code accumulating over time |
| Late-checkpoint cost and review burden | runtime cost and reviewer or remediation effort in late/final checkpoints | exposes compounding maintenance cost |

---

## Recommended Event Model

For internal agents, define these events:

- `task_created`
- `task_started`
- `task_completed`
- `task_failed`
- `human_takeover`
- `handoff_accepted`
- `pr_opened`
- `pr_merged`
- `pr_reverted`
- `policy_exception`
- `security_exception`
- `trajectory_checkpoint_completed`

Recommended properties:

- `agent_name`
- `model_name`
- `repo`
- `team`
- `task_type`
- `risk_level`
- `runtime_seconds`
- `input_cost`
- `output_cost`
- `human_rework_minutes`
- `trajectory_id`
- `checkpoint_id`
- `parent_checkpoint_id`
- `spec_version`
- `workspace_identity`
- `workspace_hash`
- `progress_phase`
- `strict_correct`
- `isolated_correct`
- `core_correct`
- `regression_correct`
- `erosion`
- `verbosity`
- `cost`
- `duration`

Without these events, you cannot build reliable agent metrics.

---

## Interpreting the Funnel

| Pattern | Interpretation | Likely Action |
|---------|----------------|---------------|
| high start rate, low completion | workflow is unstable or over-scoped | narrow task envelope |
| high completion, low acceptance-for-review | "complete" does not mean useful | tighten success definition |
| high PR open rate, low merge rate | reviewers do not trust the output | improve guardrails and task selection |
| high merge rate, high revert rate | reviewers are missing real problems | add stronger quality gates |
| good merge rate, rising reviewer effort | agent output is acceptable but expensive | improve prompt/context quality or reduce scope |
| low completion, low takeover | tasks may be abandoned silently | improve failure tagging |

---

## Minimum Viable Scorecards

### Scorecard A: Early Agent Pilot

Use when the goal is to learn whether the workflow is viable.

Track:

- task completion rate
- human takeover rate
- acceptance-for-review rate
- PR merge rate
- reviewer effort per accepted task
- policy / security exceptions
- extension-robustness sequence result for edit-capable agents
- structural erosion and verbosity slopes across checkpoints

### Scorecard B: Scaling Agent Workflow

Use when the pilot is already technically viable.

Track:

- all Scorecard A metrics
- revert / hotfix rate
- cost per accepted task
- cost per merged PR
- completion rate by task type
- benchmark-to-production gap
- late/final checkpoint cost and reviewer or remediation burden

### Scorecard C: Executive Decision

Use when leadership needs a program-level call.

Track:

- accepted tasks per month
- merged PRs per month
- reviewer effort trend
- quality / exception trend
- cost per accepted task
- extension-robustness trend by task class
- late-checkpoint cost and review-burden trend
- recommendation: expand, narrow, or stop

---

## Reviewer Burden

Reviewer burden is often the most important agent metric.

Measure at least one of:

- review time per accepted PR
- review rounds per accepted PR
- requested-changes rate
- substantive comments per accepted PR

Interpretation:

- if output volume rises while reviewer burden rises faster, net value may be negative
- if merge rate is stable and reviewer burden falls, the workflow is improving

Do not claim autonomy gains without reviewer-burden data.

For iterative agent evaluations, segment cost and review or remediation effort by progress phase. Stable aggregate cost can conceal a late-checkpoint spike caused by accumulated design debt.

---

## Quality and Safety

Agent metrics must include safety.

Recommended safety metrics:

- security findings introduced on agent-created code
- policy exceptions or manual overrides
- test failures after agent completion
- incidents or hotfixes attributable to agent-created changes

If a workflow crosses a security or production boundary, this section is mandatory.

---

## Benchmark Use

Use benchmarks as capability evidence only.

Good benchmark uses:

- compare models before a controlled internal test
- identify whether a task envelope is plausibly automatable
- watch capability regressions after a model or prompt change

Bad benchmark uses:

- calling a high benchmark score proof of ROI
- using benchmark wins to skip reviewer-burden measurement
- assuming benchmark gains transfer to messy internal repos

Better framing:

> Benchmarks tell us what the agent may be capable of. Production acceptance tells us whether that capability survives contact with our repos, standards, and reviewers.

For edit, refactor, and migration agents, add at least one evolving-spec sequence with three or more checkpoints. Use a fresh conversation/context at each checkpoint, carry the same agent-created workspace forward, and retain prior regression tests. Report the correctness trajectory beside structural-erosion and verbosity slopes plus late-checkpoint cost and review burden. A one-shot green suite or a planning/quality prompt is not evidence of long-run extension robustness.

SlopCodeBench v1 motivates this measurement shape, but its paper averages are not organizational targets and its trajectory signals do not establish causal ROI. Use `qa-agent-testing` for benchmark protocol, `ai-coding-agents-observability-evals` for lineage and telemetry, and `software-clean-code-standard` for metric interpretation.

---

## Segmentation

Segment agent metrics by:

- task type: bugfix, test, refactor, migration, docs, incident
- repo or service
- risk level
- agent or model version
- reviewer group

Do not compare all task types in one blended acceptance rate.

---

## Study Designs That Work Well for Agents

Best options:

- blind reviewer comparison on paired outputs
- shadow workflow on the same task class
- staggered rollout by task type
- production funnel tracking with mandatory reviewer tags

Useful task-level questions:

- which tasks complete cleanly?
- which tasks complete but fail review?
- which tasks should remain assistant-only rather than agentic?

Cross-reference: `benchmarking-methodology.md`

---

## Executive Summary Template

When summarizing agent performance, use this structure:

1. what task envelope was in scope
2. how many runs started
3. how many produced accepted work
4. what reviewer effort was required
5. what quality and safety signals looked like
6. cost per accepted task or merged PR
7. recommendation on scope expansion or narrowing

Suggested one-line summary:

> The agent completed 61% of scoped tasks, 34% were accepted into review, 22% merged, reviewer effort per merged PR fell after narrowing the task envelope, and post-merge quality remained stable; expand only within the current task class.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|--------------|
| counting all completed runs as wins | many "successful" runs are not accepted |
| tracking starts without takeovers | hides hidden human rescue |
| using merge rate without revert rate | misses downstream reliability |
| calling benchmark gains business value | benchmark != accepted production work |
| ignoring reviewer cost | overstates ROI materially |
| blending task types | high-volume easy tasks hide hard-task failures |
| using preprint averages as targets | substitutes another benchmark's task/model mix for local evidence |
| reporting only final-checkpoint quality | hides when and how degradation or cost accumulated |

---

## What to Do Next

- For broader team delivery metrics, use `productivity-metrics.md`.
- For cost modeling, use `roi-framework.md`.
- For experiments, use `benchmarking-methodology.md`.
