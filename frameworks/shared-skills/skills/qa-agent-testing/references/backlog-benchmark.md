# Coding-Agent Backlog Benchmark

## Table of Contents

- [Purpose and boundary](#purpose-and-boundary)
- [Benchmark contract](#benchmark-contract)
- [Select a representative backlog](#select-a-representative-backlog)
- [Prevent leakage](#prevent-leakage)
- [Prepare comparable arms](#prepare-comparable-arms)
- [Predeclare trials and grading](#predeclare-trials-and-grading)
- [Run and record every outcome](#run-and-record-every-outcome)
- [Grade accepted work](#grade-accepted-work)
- [Account for time and cost](#account-for-time-and-cost)
- [Cutoff, censoring, and analysis](#cutoff-censoring-and-analysis)
- [Report evidence and limits](#report-evidence-and-limits)
- [Illustrative record](#illustrative-record)
- [Related references](#related-references)

## Purpose and boundary

Use this bounded protocol when a coding-agent benchmark must answer whether backlog work becomes accepted, reviewable work at a tolerable human and operating cost. A green test suite, a completed run, an opened or merged PR, or a deployment is evidence about one stage only; none is acceptance by itself.

The unit is a selected backlog task run in a named arm and trial. Keep task-level records, including failed, `not_started`, abandoned, and censored work. Report the funnel and the strata; do not select only tasks that eventually succeeded.

This is a task-level benchmark. Use [`agent-execution-metrics.md`](../../dev-ai-coding-metrics/references/agent-execution-metrics.md) for the wider event vocabulary, reviewer-burden scorecards, and program metrics, and [`benchmarking-methodology.md`](../../dev-ai-coding-metrics/references/benchmarking-methodology.md) for team or organisation experiments. Do not substitute a team-level productivity claim for this protocol.

## Benchmark contract

Write and freeze a protocol before running any task. At minimum, record:

| Contract item | Required decision |
|---|---|
| Objective | The task-level outcome and comparator question |
| Population | Source backlog, snapshot or cutoff, inclusion/exclusion, and representative strata |
| Primary estimand | For example, acceptance among selected tasks, with the denominator stated |
| Acceptance contract | Functional checks, constraints or policy checks, and independent review evidence |
| Arms | The one variable being compared and every other fixed configuration |
| Trials | Trial count, independence, order, retry and worker limits, and stop rules |
| Grading | External owner, immutable or append-only record, blinding, and calibration plan |
| Cutoff | Date/time, treatment of open work, and when a final rate is allowed to be reported |

Use the existing `FAIL` / `PASS` / `CONDITIONAL` model from [`scoring-rubric.md`](scoring-rubric.md) for quality or suite status. Acceptance is a separate outcome field. Do not invent an 80–90% pass target or turn a quality band into a business result.

The JSON template is an authoring form, not a schema, validator, or permission grant. Missing mandatory design decisions block a run: an unavailable reason cannot replace a task identifier, pre-fix commit, cutoff, acceptance contract, or budget. Review nonempty required strings and lists, unique identifiers, bounded limits, grader isolation, and the full protocol as well as the path list. Optional fields and unobserved measurements may remain `null` with reasons in `missingness_reasons`. Randomised selection, interval estimates, real model calls, and model judges have conditional requirements recorded in the template.

## Select a representative backlog

1. Define the source population from an issue tracker, PR queue, or equivalent dated export. Each selected task must retain its source issue or PR key/URL and the pre-fix commit that the agent receives.
2. Define representative strata before sampling. Useful strata include task type, risk, repository, language or framework, and difficulty. Use observed population proportions where the claim is proportional; oversample rare high-risk work only when that is declared and reported.
3. Use prospective random selection or freeze a historical sample at a stated cutoff. Record the query/export hash, selection seed, strata counts, replacements, and exclusions with reasons.
4. Keep every selected task in the ledger. `not_started` and `abandoned` are results about the workflow, not reasons to remove a task. Never replace a hard task because an easier task succeeded without recording the replacement.
5. For a historical task, pin the pre-fix commit and the task wording available at selection time. A baseline checkout alone is insufficient if later git history, merged PRs, comments, fixtures, or external grader answers reveal the fix.

Do not call the final acceptance rate known while selected tasks remain unresolved under the declared cutoff policy. An observed-to-date diagnostic can be useful, but it must show its denominator and the excluded or unresolved counts.

## Prevent leakage

Create an agent-visible task bundle and an evaluator-only bundle. The agent-visible bundle may contain the source issue/PR statement, pre-fix tree, allowed documentation, and declared acceptance contract. Keep later commits, later PR diffs, maintainer comments, hidden tests, gold patches, external grader prompts, and human scores outside the agent context.

Before each trial, verify:

- the workspace is a clean checkout of the pinned pre-fix commit;
- git log, branches, tags, remotes, caches, fixtures, and package artifacts cannot expose the later answer;
- hidden tests and grader inputs are mounted or queried only by the external grader;
- the agent cannot edit, suppress, or rewrite its grade, review record, or cost ledger;
- traces preserve prompts, tools, outputs, retries, approvals, side effects, and errors without leaking protected answers back to the agent.

Record a leakage incident as an invalid trial and preserve it in the ledger. Do not silently rerun it as if the original trial had not happened.

## Prepare comparable arms

Use a clean isolated workspace per task, arm, and trial. Keep repository state, dependency lockfiles, time, locale, network, tool mocks, permissions, approval policy, model/provider, prompt, context window, token and wall-time budgets, and worker limits equal unless the named variable requires a difference.

Change one variable at a time. If comparing a prompt, hold model, tools, budget, task order, and grader constant. If comparing a model, hold prompt, tools, budget, and task order constant. Randomise or counterbalance arm order where order effects are plausible, and record the assignment.

Filling or statically checking the template does not require model calls or production writes. An actual offline benchmark may invoke a real model under the user's existing authorization and declared budget while mocking external tools. Record the model and usage; do not ask again for standing authorization. Mocked agent answers test the scorer, not candidate performance. Live external tools belong in a separately identified, authorized canary; this protocol does not authorize production writes.

## Predeclare trials and grading

Set the number of independent trials per task before inspecting results. A repeated-trial measure such as accepted-on-all-`k`-trials is meaningful only when `k`, independence assumptions, and failure handling are fixed in advance. Record all retries and worker or subagent runs; a retry is work and is part of cost even when the final trial succeeds.

Predeclare per-task limits: wall time, token or compute budget, tool-call budget, retry count, worker count, and the stopping condition for a stalled run. A limit hit produces a recorded status; it does not justify extending only unsuccessful tasks.

The grader must be external to the agent process and write to an append-only or access-controlled store. Grade functional behavior through black-box tests or a served contract, constraints and policy through objective oracles, and maintainability or ambiguous quality through an independent human reviewer. Calibrate any model judge on a human-labeled slice and escalate disagreement or high-stakes decisions to a person.

## Run and record every outcome

Maintain an event ledger plus one outcome row for each selected task, arm, and trial. Preserve these primary states:

| State | Meaning |
|---|---|
| `accepted` | Functional and constraint checks pass, required evidence exists, and an independent reviewer accepts the deliverable |
| `failed` | A terminal result exists but an objective, functional, constraint, evidence, or review requirement fails |
| `not_started` | Selected, but no agent run started before the declared cutoff |
| `abandoned` | Started, but stopped without a terminal deliverable or an accepted outcome |
| `censored` | Still unresolved at the declared observation cutoff; reason and next observation date are recorded |

If useful, record `completed_unaccepted` as a detail or reason under `failed`; do not collapse open work into failure merely because a report is being prepared. A task may have a merged PR or deployment as a downstream event while its acceptance state remains `failed`, `censored`, or unknown.

At task level, retain source key, pre-fix SHA, arm, trial, status, reason, timestamps, workspace hash, trace references, grader references, selected stratum, run/retry/worker counts, and human review or rework minutes.

## Grade accepted work

An accepted result requires all of the following. If a particular check is genuinely not applicable, record the explicit `not_applicable` result and reason in the frozen contract; do not omit independent review or acceptance evidence:

1. Functional evidence: current and retained regression behavior meets the task contract in an external test, black-box check, or equivalent artifact.
2. Constraint evidence: scope, safety, policy, format, dependency, and approval requirements pass their objective checks.
3. Independent review: a reviewer who did not produce the run confirms the result and records findings, review rounds, and any requested rework.

Merge, deployment, a self-reported “done”, or a high rubric score can be attached as evidence, but cannot replace the three acceptance components. Keep the existing rubric dimensions and `PASS` / `CONDITIONAL` / `FAIL` status in the review record when used; do not infer acceptance from a single automated score.

## Account for time and cost

Separate outcome, time, and money. Count all agent runs, retries, workers, subagents, failed attempts, and abandoned work across every assigned task-trial in an arm. Count human review minutes and rework minutes separately; include both across the full cohort and report their distributions, not only an average.

Record money only when observed from billing or a declared allocation rule:

- `api_usage_cost` is usage-billed spend for calls made by the benchmark;
- `subscription_or_seat_cost` is a plan or seat charge and must not be divided per task without a predeclared allocation rule;
- `money_available: false` means monetary cost is `null`, not zero;
- distinguish API usage from subscription or seat cost and preserve unknown components as `null`.

Keep time units and money units separate. Keep unique-task counts separate from task-arm-trial row counts when repetitions are used. For each arm, sum agent runs/retries/workers and human review/rework across all assigned task-trials, including failed, abandoned, and censored work that incurred them. A monetary `total_cost` is a full-cost claim only when every required money component is observed or allocated by the frozen policy; otherwise report the observed partial cost and list unknown components. If `accepted_count = 0`, `cost_per_accepted` is undefined, not zero. If the cutoff is incomplete and at least one task is accepted, report `observed_to_date_cost_per_accepted` with its scope; it is not a final cost. Retain cost for every completed, failed, abandoned, and censored run that incurred work.

For each arm, let `A` be accepted task-trial rows and `C` the sum of the stated cost components across **all assigned rows**, including retries and workers. When `A > 0`, report `C / A` with its cost scope and partial or observed-to-date label. Human minutes per accepted result likewise equal all review plus rework minutes divided by `A`. Do not divide pooled trial costs by unique accepted tasks unless separately declaring that task-level metric. Unknown cost components remain unknown.

## Cutoff, censoring, and analysis

Treat cutoff and aggregate status as different fields. The cutoff is the observation rule; `censored` is the task state produced when that rule ends before acceptance can be determined. Never silently count censored work as accepted, failure, or missing data.

Report, by arm and stratum, at least:

- unique selected-task counts and assigned task-trial counts separately;
- selected, started, terminal, accepted, failed, `not_started`, abandoned, and censored counts;
- observed-to-date acceptance rate with its exact denominator and date;
- final acceptance rate only when the frozen resolution policy permits it, otherwise `unknown`;
- human review minutes, rework minutes, agent runs/retries/workers, duration, and money fields with their availability status;
- absolute arm differences and confidence limits using a method declared before the run, or an explicit descriptive-only pilot analysis.

For a small pilot, describe uncertainty plainly and avoid power or generalisation claims the sample cannot support. Keep strata visible; do not hide failures in a pooled average. For repeated trials, report per-trial acceptance and accepted-on-all-`k`-trials, preserving incomplete trial sets. A zero denominator yields `undefined`, never an invented rate.

Use evidence labels already used by this skill: `static` (harness/schema), `offline` (mocked or recorded tasks), `replay` (captured production-like traces), `canary` (bounded real tools and policies), and `online` (monitored production outcomes). This protocol's default is `offline`; no live paid calls or production writes are required.

## Report evidence and limits

The report should link the frozen protocol, source snapshot, task manifest, arm configuration hashes, workspace hashes, traces, external grades, human review records, and cost ledger. State what was actually observed, what remains censored or unknown, and whether any trial was invalidated for leakage or infrastructure failure.

Do not claim productivity, ROI, deployment safety, or customer impact from this benchmark alone. A task-level acceptance result supports a bounded workflow decision. Broader adoption requires the program-level evidence and reviewer-burden accounting described in the related metrics reference.

## Illustrative record

The following is illustrative only; it is not a measured result or a default threshold:

```text
Task source: issue/example-42 (illustrative)
Pre-fix commit: 0123456 (illustrative)
Stratum: bugfix / medium risk (illustrative)
Arm: prompt-B; comparator differs only in prompt version (illustrative)
Assigned task-trials: 4; status counts: 1 accepted / 1 failed / 1 abandoned / 1 censored (illustrative)
Functional: 1 pass / 1 fail / 1 not run / 1 unknown; constraints and review recorded per row
Agent runs/retries/workers: 2 / 1 / 1 for the accepted row (illustrative)
Human review/rework minutes: 20 / 10 across all four assigned rows (illustrative)
Observed API usage cost: GBP 12 across all four rows, retries, and workers (illustrative)
Cost scope: API only; subscription allocation and human monetary cost unknown
Observed-to-date acceptance rate: 1 / 4 assigned task-trials = 0.25; censored count = 1
Final acceptance rate: unknown while the censored task-trial remains unresolved
Observed-to-date API cost per accepted: GBP 12 / 1 = GBP 12 (illustrative)
Observed-to-date human minutes per accepted: (20 + 10) / 1 = 30 minutes (illustrative)
Final cost per accepted: unknown while work or required cost components remain unresolved
```

## Related references

This original local protocol is informed by Daniel Vaughan's *Agentic Coding with OpenAI Codex CLI*, chapters 19 and 25. The worked numbers above are synthetic, not empirical performance results.

- [`eval-dataset-design.md`](eval-dataset-design.md) — representative strata, sampling, annotation, contamination, and held-out data.
- [`../assets/backlog-benchmark-template.json`](../assets/backlog-benchmark-template.json) — fillable machine-readable contract and outcome ledger; null design fields must be completed before a run.
- [`coding-agent-regression-testing.md`](coding-agent-regression-testing.md) — pre-fix source-to-test context and separate regression rate.
- [`iterative-coding-agent-evals.md`](iterative-coding-agent-evals.md) — carried workspaces and strict, isolated, core, and regression slices.
- [`regression-protocol.md`](regression-protocol.md) — rerun scope, baseline, and recovery records.
- [`tool-sandboxing.md`](tool-sandboxing.md) — isolation, tool faults, and approval boundaries.
- [`../../dev-ai-coding-metrics/references/agent-execution-metrics.md`](../../dev-ai-coding-metrics/references/agent-execution-metrics.md) — event and reviewer-burden vocabulary; it owns team/program methodology.
- [`../../dev-ai-coding-metrics/references/benchmarking-methodology.md`](../../dev-ai-coding-metrics/references/benchmarking-methodology.md) — team-level study designs; do not duplicate them here.
- [OpenAI best practices for Codex](https://learn.chatgpt.com/guides/best-practices) — context, constraints, done criteria, validation/review, isolated workspaces, and reusable workflows.
