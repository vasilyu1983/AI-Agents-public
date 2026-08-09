---
description: Theory of Constraints applied to AI coding metrics. Five Focusing Steps on the developer-flow bottleneck before instrumenting AI lift, throughput accounting for ROI, DBR for code-review queue protection, CRT for stalled rollouts, and evaporating cloud for adoption-vs-quality tensions.
foundation: foundations-theory-of-constraints
last_verified: 2026-05-03
status: stable
---

# Theory of Constraints Applied to AI Coding Metrics

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-03._

See [foundations-theory-of-constraints](../../foundations-theory-of-constraints/SKILL.md) for canonical primitive definitions, playbooks, and worked examples.

## Table of Contents

- [Why TOC Applies to AI Coding Metrics](#why-toc-applies-to-ai-coding-metrics)
- [Primitive Coverage Map](#primitive-coverage-map)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Developer-Flow Bottleneck Identification Before Measuring AI Lift](#p1--developer-flow-bottleneck-identification-before-measuring-ai-lift)
  - [P2 — Throughput Accounting for AI-Coding ROI](#p2--throughput-accounting-for-ai-coding-roi)
  - [P3 — Drum-Buffer-Rope for Code-Review Queue Protection](#p3--drum-buffer-rope-for-code-review-queue-protection)
  - [P4 — Evaporating Cloud for Adoption-vs-Quality Tensions](#p4--evaporating-cloud-for-adoption-vs-quality-tensions)
  - [P5 — Current Reality Tree for Stalled AI-Tool Rollouts](#p5--current-reality-tree-for-stalled-ai-tool-rollouts)
  - [P6 — Subordinating Non-Bottleneck Metrics to Avoid Local Optimisation](#p6--subordinating-non-bottleneck-metrics-to-avoid-local-optimisation)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Lines-of-Code Dashboards](#a1--lines-of-code-dashboards)
  - [A2 — Isolated Tool-Adoption Metrics Ignoring Delivery](#a2--isolated-tool-adoption-metrics-ignoring-delivery)
  - [A3 — Celebrating PR Throughput When Review Is the Bottleneck](#a3--celebrating-pr-throughput-when-review-is-the-bottleneck)
  - [A4 — AI-Quality Gates Measured Without Baseline](#a4--ai-quality-gates-measured-without-baseline)
  - [A5 — Cost-of-Delay Ignored in AI-Coding Investment Cases](#a5--cost-of-delay-ignored-in-ai-coding-investment-cases)
- [Recipes](#recipes)
  - [R1 — Diagnose Your AI-Coding Bottleneck in 5 Questions Before Instrumenting](#r1--diagnose-your-ai-coding-bottleneck-in-5-questions-before-instrumenting)
  - [R2 — ROI Scorecard Structured by Throughput / OE / Inventory](#r2--roi-scorecard-structured-by-throughput--oe--inventory)
  - [R3 — Pilot-to-Rollout Metric Plan Using CRT and FRT](#r3--pilot-to-rollout-metric-plan-using-crt-and-frt)
- [Composition](#composition)
- [Sources](#sources)

---

## Why TOC Applies to AI Coding Metrics

An AI-coding programme is a multi-step delivery system. Writing code is one step; review, merge, QA, deploy, and production validation are the rest. AI assistants and agents can accelerate individual steps — but system throughput (features shipped, bugs resolved, value delivered) is set by the slowest link, not by the fastest tool.

This creates a measurement trap: teams instrument where AI is visible (code generation, acceptance rate, lines accepted) rather than where the constraint lives. If code review is the bottleneck, an AI tool that doubles authoring speed doubles the queue in front of review without increasing delivery. The metric looks great; the system gets worse.

TOC gives AI metrics three things cost-accounting or velocity-only measurement cannot:

1. **A reason to measure the system before measuring the tool** — 5FS identifies the constraint first; AI lift is only meaningful if it moves the constraint.
2. **A financial frame** — Throughput Accounting (T, I, OE) evaluates AI investment by delivery impact, not by licence cost or lines-of-code output.
3. **A conflict-resolution method** — Evaporating Cloud dissolves the recurring tension between adoption speed and quality gates without compromising either.

The primitives below are domain-specific applications of the canonical TOC tools. Full playbooks are in [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/).

---

## Primitive Coverage Map

| Primitive | # | Applied in Patterns / Recipes |
|-----------|---|-------------------------------|
| Five Focusing Steps | 1 | P1, R1 |
| Drum-Buffer-Rope | 2 | P3 |
| Throughput Accounting | 3 | P2, A1, A2, A5, R2 |
| Evaporating Cloud | 4 | P4 |
| Current Reality Tree | 5 | P5, R3 |
| Future Reality Tree | 6 | R3 |
| Policy Constraints | 10 | P5, A3 |

Full primitive playbooks: [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/)

---

## Pattern Catalog

### P1 — Developer-Flow Bottleneck Identification Before Measuring AI Lift

**Primitive**: #1 Five Focusing Steps → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md)

**When to use.** Before instrumenting any AI coding tool — assistant or agent — run 5FS on the team's delivery pipeline to identify where work actually stalls. Measuring AI lift before knowing the constraint produces metrics that are accurate about the tool and irrelevant to the system.

**The problem it solves.** Adoption metrics and code-generation stats tell you about one step. If that step is not the constraint, improving it does not increase throughput. A team that ships AI-assisted code 40% faster but whose review queue grows 40% longer has not improved delivery; it has moved the queue.

**5FS applied to a delivery pipeline:**

1. **Identify** — Map the full path from task-start to production. Measure cycle time and queue time at each stage: specification → code → review → QA → deploy. The constraint is the stage where WIP accumulates — not the slowest average stage, but the stage whose queue grows while upstream stages drain.

   Concrete signals:
   - PRs waiting for review for > 1 day while authoring is < 4 hours → review is the constraint.
   - Code complete in hours but QA backlog spans days → QA is the constraint.
   - Story cycle times long but individual stage times short → a handoff or approval policy is the constraint.

2. **Exploit** — Before deploying AI tooling, squeeze maximum throughput from the constraint with existing resources: pair-review on high-complexity PRs, async review SLA agreements, review checklist standardisation, draft-PR workflow to surface early feedback.

3. **Subordinate** — Confirm that any AI tooling investment is directed at the constraint stage. If review is the constraint, the highest-value AI application is review assistance (automated code review, AI-generated PR summaries, AI-flagged diff risks) — not code generation at the authoring stage.

4. **Elevate** — If exploitation is insufficient, invest in constraint capacity: hire reviewers, rotate review duty, adopt AI review tooling with real constraint impact. Evaluate elevation by whether the constraint stage's queue clears — not by whether the AI tool's utilisation metrics look good.

5. **Repeat** — After the constraint is broken, re-run the measurement pass. The constraint shifts. Authoring may become the new bottleneck once review is unblocked; that is the right time to invest in code-generation AI.

**Failure mode to avoid.** Measuring AI acceptance rate and code-generation speed as primary outcomes before identifying the delivery constraint. These are local metrics; they cannot tell you whether system throughput improved.

---

### P2 — Throughput Accounting for AI-Coding ROI

**Primitive**: #3 Throughput Accounting → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/03-throughput-accounting.md)

**When to use.** When building or reviewing an AI coding investment case, pilot ROI scorecard, or renewal decision. Throughput Accounting reframes the ROI question from "what does the tool cost?" to "does the tool move the constraint and increase system throughput?"

**The problem it solves.** Cost-accounting-based AI ROI models calculate: (seat cost) vs. (time saved × hourly rate). This conflates operating expense with throughput. A tool that saves 10 developer-hours per week but does not move the delivery constraint has T/IU ≈ 0: the system ships no more software.

**TOC financial triad applied to AI coding:**

| TOC term | AI-coding meaning |
|----------|------------------|
| Throughput (T) | Rate at which working software reaches production and generates business value: features shipped, bugs resolved, deployment frequency at the constraint |
| Investment (I) | In-flight work: PRs open, tasks in-progress, agent runs not yet merged |
| Operating Expense (OE) | All costs to keep the system running: seat licences, infrastructure, review time, rework, model API costs |

**T/CU (Throughput per Constraint Unit)** becomes: delivery throughput increase per unit of constraint-stage time consumed by AI tooling. To compute:

1. Identify the constraint stage (from P1).
2. Measure baseline throughput at the constraint: PRs merged/week, features shipped/sprint.
3. After AI rollout, measure the same throughput signal at the constraint.
4. Divide throughput delta by incremental OE (total cost of the AI programme).

**Decision rules:**

- An AI tool that increases authoring speed but does not increase constraint-stage throughput has T/IU ≈ 0. Licence cost is pure OE with no T return.
- An AI tool that reduces review burden at the constraint (automated code review, AI PR summaries, risk triage) directly increases constraint throughput. T/IU is positive and measurable.
- An AI tool that reduces rework (better quality at generation time, catching defects before review) reduces OE and may increase T if rework was consuming constraint time.

**Cost-of-delay framing for investment cases.** When building the ROI case for leadership, anchor on cost of delay: what is the throughput cost per sprint of not addressing the constraint? If the constraint prevents two features per sprint from shipping, and each feature is worth £X in revenue or cost-avoidance, the investment case is: does this AI tool justify its total OE by removing or reducing that constraint? Seat-cost comparisons against engineer-hour savings miss this entirely.

**Failure mode to avoid.** Calculating ROI as (hours saved × hourly rate) when hours saved are in non-constraint authoring time. This produces a compelling number that measures local efficiency at a step that does not gate delivery.

---

### P3 — Drum-Buffer-Rope for Code-Review Queue Protection

**Primitive**: #2 Drum-Buffer-Rope → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/02-drum-buffer-rope.md)

**When to use.** When AI coding tools have increased authoring speed and the code-review queue has grown correspondingly — or is projected to grow. DBR protects the review constraint from being flooded by upstream AI-accelerated output.

**The problem it solves.** Without WIP control, increasing authoring speed through AI directly increases review queue depth. More PRs arrive than reviewers can process; each PR waits longer; review quality degrades under pressure; defect escape rises. The AI tool appears to help delivery; the system outcome is worse review, higher rework, and no throughput gain.

**DBR translation for code review:**

| DBR term | Code-review meaning |
|----------|-------------------|
| Drum | Reviewer capacity: PRs reviewable per day at target quality without reviewer burnout |
| Buffer | WIP cap on the review queue: the maximum number of open PRs allowed before authoring intake is paused |
| Rope | The mechanism that limits new PR submission to the drum rate: a WIP limit enforced in the project board, a PR-per-author daily cap, or an AI triage gate that queues low-priority PRs |

**Mechanic.**

1. **Set the drum.** Measure reviewer capacity: how many PRs can the review team process per day at the team's target quality standard (not under pressure)? This is the drum rate. Example: a team of 3 reviewers, each reviewing 2 PRs/day at quality = 6 PRs/day.

2. **Set the buffer.** Determine the maximum acceptable review queue depth before throughput degrades. Rule of thumb: 1.5× the drum rate. At 6 PRs/day drum rate, buffer = 9 open PRs before the intake rope triggers.

3. **Set the rope.** Configure the intake limit. Options:
   - A WIP limit label on the project board: no more than N PRs can move to "Ready for Review" simultaneously.
   - An AI triage gate: AI-assisted pre-review flags PRs as HIGH/MEDIUM/LOW review priority; LOW-priority PRs enter a deferred queue rather than the main review column when the buffer is reached.
   - A team norm: authors who finish a PR while the buffer is full pick up a review before opening the next PR.

4. **Subordinate authoring to review.** When the buffer is full, authors stop opening new PRs and shift to reviewing. This is the hardest cultural change: it feels like slowing down, but it is the correct TOC response to a flooded constraint. Measure it: the team's WIP at review should not grow week-over-week.

**Metric to track.** Review queue depth (P85 age of open PRs awaiting review) is the primary health signal. If it is growing after AI tooling adoption, the rope is not set or not respected. AI-accelerated authoring without DBR at review is a local optimisation that harms the system.

---

### P4 — Evaporating Cloud for Adoption-vs-Quality Tensions

**Primitive**: #4 Evaporating Cloud → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/04-evaporating-cloud.md)

**When to use.** When an AI coding rollout is deadlocked between two camps: those pushing for broad adoption now versus those requiring quality gates, safety reviews, or security sign-off before expansion. Both positions are well-reasoned; the team is in a compromise loop that satisfies neither.

**The problem it solves.** Compromise between adoption speed and quality gates typically produces a slow rollout with gates that are not rigorous enough to satisfy the quality camp, and not fast enough to satisfy the adoption camp. The underlying assumption that makes the two positions appear irresolvable is never surfaced.

**Cloud structure:**

```
Shared Goal (A): Capture AI coding productivity gains without introducing quality or security regressions

Requirement B (adoption camp): Maximise tool adoption to realise throughput benefits
  → Prerequisite D:  Roll out AI coding tools to all teams with minimal friction

Requirement C (quality camp): Protect code quality, security posture, and developer trust
  → Prerequisite D′: Require quality gate review, security assessment, and baseline measurement before any team onboards

Conflict: D and D′ appear mutually exclusive — broad rollout and gated rollout cannot both be true.
```

**Arrow challenges:**

| Arrow | Assumption | Challenge |
|-------|-----------|-----------|
| B → D | Productivity benefit requires broad adoption | Controlled rollout to high-readiness teams first captures most throughput benefit; marginal benefit from forcing adoption on resistant teams is small |
| C → D′ | Quality protection requires a gate before any adoption | Quality measurement can run in parallel with adoption if a rollback plan is in place; gates before every team are not the only way to protect quality |
| A → B | Throughput benefit requires rapid adoption | Throughput benefit is a function of adoption at the constraint, not adoption breadth; targeted adoption at the constraint stage yields T gain faster than broad shallow rollout |
| A → C | Protecting quality requires slowing adoption | Automated quality baselines (defect escape rate, rework rate, review burden) can be established quickly and monitored continuously — gating does not have to be a manual checkpoint |

**Injection.** Progressive adoption with automated quality monitoring: roll out to constraint-stage teams first (P1) with automated baseline metrics running from day one. Quality gates are continuous dashboards, not one-time approval checkpoints. Security review runs in parallel on the first cohort, not as a prerequisite to all cohorts. If a quality metric degrades beyond a threshold, the rollout pauses — automatically, not by committee.

This satisfies B (adoption proceeds at the highest-value constraint stages) and C (quality is protected by continuous automated monitoring and automatic pause, not by manual gates that throttle adoption).

**Signal to apply.** The rollout has been "in discussion" for more than two sprint cycles; the two camps keep restating the same positions; solutions are half-measures that both camps accept reluctantly.

---

### P5 — Current Reality Tree for Stalled AI-Tool Rollouts

**Primitive**: #5 Current Reality Tree → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/05-current-reality-tree.md)

**When to use.** An AI coding tool rollout has stalled: adoption is plateauing, usage is not sustaining, or the programme has been running for months without measurable delivery impact. Multiple explanations have been offered (training, change management, context quality, management support) but none has resolved the problem.

**The problem it solves.** Stalled rollouts have multiple visible symptoms — low acceptance rate, team resistance, reverting to old workflows — that are treated as independent problems with independent solutions. The CRT traces all symptoms to a single Core Problem, allowing one injection to unblock the entire rollout rather than patching symptoms one by one.

**Mechanic.**

Step 1: Collect 5–8 UDEs from the rollout. Write each as a concrete, negative, observable outcome:

```
UDE 1: "AI suggestion acceptance rate has been below 20% for 8 weeks despite training"
UDE 2: "Developers report suggestions are irrelevant to the codebase context"
UDE 3: "Three teams disabled the plugin after the first week and have not re-enabled it"
UDE 4: "Review burden increased after rollout — reviewers report more AI-generated noise in diffs"
UDE 5: "Engineering leads are not tracking AI usage in their team metrics"
UDE 6: "Pilot teams cannot articulate a business outcome the tool has changed"
```

Step 2: Build "If…Then" chains. Trace from UDEs toward a shared root:

```
IF  the tool receives minimal codebase context (IDE setup incomplete, no project .clinerules or CLAUDE.md)
THEN  suggestions are semantically irrelevant to the actual codebase → UDE 2
THEN  developers do not accept suggestions → UDE 1
THEN  developers disable the plugin → UDE 3

IF  authoring speed increases but review WIP is uncapped
THEN  diff noise increases → UDE 4
THEN  reviewers report negative experience → reinforces UDE 3

IF  no T-level metric is tracked (only acceptance rate)
THEN  leads cannot connect usage to outcomes → UDE 5, UDE 6
THEN  the programme cannot make a delivery-impact case → continued stall
```

Step 3: Identify the Core Problem. In most stalled rollouts, the core is one of two causes:
- **Context gap**: the tool was deployed without configuring the context layer (codebase conventions, project memory, tool instructions) that makes suggestions relevant. Fix: invest in context engineering before re-expanding adoption.
- **Metric mismatch**: the programme is measured on tool-adoption metrics (acceptance rate, seat activation) rather than delivery-system metrics (constraint throughput, defect escape, rework rate). Fix: redefine success criteria as T-level outcomes before the next rollout phase.

Step 4: Design the injection and validate with a Future Reality Tree before implementing, confirming that the injection resolves all UDE chains without introducing new undesirable effects.

**Policy constraint variant.** If the Core Problem traces to a policy — "AI tools require security review before use on any codebase containing PII" — apply policy-constraint analysis (primitive #10) before treating it as a fixed obstacle. Challenge the assumption: does the policy need to apply to all AI tools equally, or can a risk-tiered policy allow lower-risk tools to proceed while the security review covers high-risk agent capabilities?

---

### P6 — Subordinating Non-Bottleneck Metrics to Avoid Local Optimisation

**Primitive**: #1 Five Focusing Steps (step 3 — subordinate) → [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/01-five-focusing-steps.md)

**When to use.** When the AI coding programme has an established metric set and teams are optimising individual metrics without improving delivery. Subordination ensures that non-bottleneck metrics are treated as supporting signals, not targets, once the constraint is identified.

**The problem it solves.** Once the constraint is identified, every other step in the pipeline should be subordinated to it: managed to keep the constraint fed and protected, not optimised independently. Metric systems that incentivise non-constraint steps to maximise their own output create local optimisation at the cost of system throughput — the classic Goldratt "local optima" failure.

**Application to an AI coding metric set:**

After running P1, the constraint is known. Example: review is the constraint.

| Metric | Constraint relationship | Correct treatment |
|--------|------------------------|-------------------|
| AI suggestion acceptance rate | Non-constraint (authoring) | Report as context; do not set improvement targets that drive authoring volume above review capacity |
| PRs merged per sprint | Constraint-stage output | Primary throughput signal; set targets and track trends here |
| PR review cycle time | Constraint efficiency | Drive improvement directly; this is where AI investment should focus |
| Lines of AI-generated code | Non-constraint | Eliminate from the dashboard or treat as a diagnostic, never a goal |
| Rework rate post-merge | Quality signal (affects constraint) | Track — rework that lands in the constraint queue inflates constraint OE |
| Deployment frequency | Downstream of constraint | Tracks whether constraint improvements are reaching production; secondary signal |

**Subordination rule.** If a metric is for a non-constraint step, it has one valid purpose: confirming the step is feeding the constraint adequately. It should never be a primary KPI or improvement target until the constraint shifts to that step.

---

## Anti-Pattern Catalog

### A1 — Lines-of-Code Dashboards

**Primitives implicated**: #3 Throughput Accounting, #1 Five Focusing Steps

**Description.** Engineering leadership publishes a dashboard tracking lines of code generated by AI tools, lines accepted, and AI-authored code as a percentage of total commits. These metrics become the primary evidence of AI programme success.

**Why it fails.** Lines of code is a classic cost-accounting proxy. It measures a byproduct of authoring, not throughput. Under Throughput Accounting, T is the rate at which working software reaches production and generates value — not the rate at which lines are written. An AI tool that generates 5,000 lines per sprint that never merge (still in review, failing tests, reverted) has produced T = 0 despite impressive LoC metrics.

Worse: optimising for LoC incentivises high-volume low-quality generation — the exact pattern that floods the review constraint and degrades system throughput.

**Fix.** Replace LoC dashboards with delivery-system metrics: PRs merged/week at the constraint stage, review cycle time, rework rate, deployment frequency. AI tool contribution shows up in these metrics when and only when it is actually moving the system. If the tool is not showing up in delivery metrics, it is not at the constraint.

---

### A2 — Isolated Tool-Adoption Metrics Ignoring Delivery

**Primitives implicated**: #3 Throughput Accounting

**Description.** The AI coding programme is measured entirely on adoption signals: seat activation, daily active users, prompts per user, acceptance rate. Delivery metrics — cycle time, merge rate, defect escape, deployment frequency — are tracked separately and not connected to the AI programme's reporting.

**Why it fails.** Adoption metrics measure I (inventory in the system — developers using the tool) and OE (are we getting usage out of the seats we are paying for?). They do not measure T. A programme that achieves 80% seat activation and 35% acceptance rate but has no measurable effect on delivery cycle time or defect escape has demonstrated usage, not value.

Disconnecting adoption from delivery metrics makes it structurally impossible to detect the failure mode where the tool is being used but the constraint is elsewhere and delivery is unchanged.

**Fix.** Pair every adoption metric with at least one delivery metric scoped to the same team and time window. Adoption without delivery movement is a signal to investigate the constraint, not a success story.

---

### A3 — Celebrating PR Throughput When Review Is the Bottleneck

**Primitives implicated**: #10 Policy Constraints, #1 Five Focusing Steps

**Description.** After AI tooling adoption, the programme celebrates an increase in PR-open rate (number of PRs opened per sprint) as evidence of productivity improvement. Review queue depth, review cycle time, and merge rate are not tracked.

**Why it fails.** PR-open rate is a non-constraint output metric when review is the bottleneck. Increasing the number of PRs opened without increasing review capacity floods the constraint. Each additional PR that opens adds to review queue depth, increases the age of all open PRs, and forces reviewers into time-pressure review that degrades quality.

A visible success metric (more PRs, more activity) disguises a system deterioration (review backlog, lower quality, higher rework). This is a policy constraint variant: the implicit policy of "more PRs = more productivity" throttles throughput by ignoring the constraint.

**Fix.** Track PR-open rate only in conjunction with merge rate, review cycle time, and review queue depth. If open rate rises and merge rate does not, the system is accumulating WIP at review. Apply P3 (DBR) to protect the review constraint before reporting open rate as a success metric.

---

### A4 — AI-Quality Gates Measured Without Baseline

**Primitives implicated**: #1 Five Focusing Steps, #3 Throughput Accounting

**Description.** A team adopts AI coding tools and introduces a quality gate — a defect escape threshold or rework rate ceiling — to confirm AI-generated code meets quality standards. However, the gate is set based on intuition or vendor benchmarks, with no pre-rollout baseline from the team's own delivery data.

**Why it fails.** Without a baseline, the quality gate cannot distinguish between:
- Quality that was already at or above the gate threshold before AI (the gate adds no signal).
- Quality that was below the gate and the AI is making it worse (the gate fires but cannot attribute causation without a baseline).
- Quality that was below the gate and the AI is improving it (passes the gate, but the programme cannot prove the improvement is attributable to the tool).

Gates without baselines are compliance theatre: they create a sense of measurement rigour without producing actionable signal.

**Fix.** Establish an 8-week pre-intervention baseline for all quality metrics in the scorecard before any AI tool is switched on in a team. The minimum baseline period is enforced because week-to-week variance in defect escape and rework routinely exceeds the signal size of AI tooling effects (see the SKILL.md measurement rules). Quality gate thresholds are set from actual baseline distributions, not benchmarks.

---

### A5 — Cost-of-Delay Ignored in AI-Coding Investment Cases

**Primitives implicated**: #3 Throughput Accounting

**Description.** The AI coding investment case compares tool licence cost against developer time saved (a cost-accounting frame). The cost of delay — the throughput lost per sprint by not addressing the delivery constraint — is never computed or presented.

**Why it fails.** A cost-accounting investment case produces a threshold: "the tool pays for itself if it saves N hours per developer per month." This frame is indifferent to whether the hours saved are at the constraint or not, and it ignores the throughput cost of the status quo.

If the constraint is causing two features per sprint to slip, and each feature represents £Y in revenue or cost-avoidance, the opportunity cost of inaction is 2 × £Y per sprint. An AI investment that removes the constraint may have a T/IU that is 5–10× the cost-savings frame — or it may have T/IU ≈ 0 if it addresses a non-constraint step. The cost-accounting frame cannot tell you which.

**Fix.** Build the investment case in two frames simultaneously: (a) the standard cost-savings frame for stakeholders who think in OE reduction, and (b) the throughput frame: what constraint does this investment address, by how much, and what is the throughput value of breaking that constraint? Present both. The throughput frame is the one that drives actual business impact; the cost-savings frame is the one that passes finance approval.

---

## Recipes

### R1 — Diagnose Your AI-Coding Bottleneck in 5 Questions Before Instrumenting

**Goal.** Identify the delivery-system constraint before designing an AI coding metric plan, so the metric set is anchored to the right stage of the pipeline.

**Inputs.** Team's current delivery process (task-start to production), at least 4 weeks of PR and deployment history.

**Step 1: Map the delivery pipeline.**

List every stage from task-start to production: specification, authoring, self-review, PR open, peer review, QA/CI, merge, deploy, production validation. For each stage, measure average cycle time and average queue time (time waiting to enter the stage after the prior stage completes).

→ verify: you have cycle time and queue time for at least 4 stages; data spans at least 4 weeks.

**Step 2: Answer the 5 diagnostic questions.**

Ask these in order. Stop when the first answer points to a bottleneck:

1. **Where does WIP accumulate?** Count open items by stage at the end of each week. The stage with the most consistently-high WIP count is the constraint candidate.

2. **Where is queue time longest?** If a stage has a short average cycle time but a long queue time (the work waits to enter the stage longer than it takes to complete it), the constraint is there — or immediately downstream.

3. **Does adding AI authoring speed increase the WIP at another stage?** If so, the downstream stage is the constraint. Adding more authoring speed will worsen it.

4. **Where do handoff delays occur?** Manual approval gates, batch release windows, or single-reviewer dependencies are policy constraint signals.

5. **What does the team complain about?** "We write code fast but can't get it reviewed" → review is the constraint. "Reviews are fast but QA takes forever" → QA is the constraint. "Deploys are infrequent despite code being ready" → deploy process is the constraint.

→ verify: at least one question points unambiguously to a stage. If not, extend the measurement window to 8 weeks.

**Step 3: Name the constraint.**

State it explicitly: "The constraint in this delivery pipeline is [stage]. Evidence: [queue time / WIP count / team feedback]." Document this as the anchor for the metric plan.

→ verify: the constraint is a named stage, not a vague description like "everything is slow."

**Step 4: Design AI investments for the constraint.**

Once the constraint is named, identify which AI capabilities address it:
- Review constraint → AI code review, PR summary generation, AI-assisted diff triage.
- QA constraint → AI test generation, AI-assisted defect detection, automated regression coverage.
- Authoring constraint (rare; only if authoring is truly the bottleneck) → code generation, AI refactoring, AI documentation.
- Deploy constraint → AI-assisted pipeline repair, AI incident triage, auto-rollback signal.

→ verify: every AI investment in the plan has a line connecting it to the named constraint stage.

**Step 5: Define the primary metric.**

The primary metric is the throughput signal at the constraint: PRs merged per week (if review is the constraint), deployments per week (if deploy is the constraint), QA-passed tickets per sprint (if QA is the constraint). Secondary metrics (acceptance rate, LoC, suggestion frequency) are diagnostic context, not success criteria.

→ verify: the primary metric is a constraint-stage throughput signal, not a tool-usage signal.

**Output.** A one-page constraint diagnosis document: constraint stage, evidence, AI investment map, and primary metric. This document replaces a vendor benchmark as the baseline for the AI coding programme.

---

### R2 — ROI Scorecard Structured by Throughput / OE / Inventory

**Goal.** Build an AI coding ROI scorecard that measures programme value in throughput terms rather than cost-savings terms, suitable for both engineering and finance audiences.

**Inputs.** Constraint diagnosis from R1, 8-week delivery baseline, AI programme costs (licence, infrastructure, context engineering, training, ongoing maintenance).

**Step 1: Establish the three TOC accounts.**

Map every measurable signal in the programme to T, I, or OE:

| Signal | Account | Measurement |
|--------|---------|-------------|
| Features shipped per sprint at constraint | T | Constraint-stage merge rate; deployment frequency |
| Defects reaching production | T (negative) | Defect escape rate; severity-weighted bug count |
| Reduction in rework cycles | T + OE | Rework PRs as % of total; rework hours |
| Open PRs / in-flight tasks at sprint end | I | WIP count at constraint stage at sprint end |
| AI tool licence cost | OE | Monthly seat cost |
| Model / API / infrastructure cost (agents) | OE | Token cost, compute cost per merged PR |
| Developer review time on AI-generated diffs | OE | Review hours at constraint stage |
| Training and onboarding time | OE | Hours per developer onboarded |

→ verify: every metric in the scorecard is assigned to exactly one account; no metric appears in both T and OE.

**Step 2: Compute the baseline and target T/IU.**

Baseline T: features shipped per sprint at the constraint stage, averaged over 8 pre-intervention weeks.

Total programme investment (I in the ROI sense, not the TOC inventory sense): sum of all OE increments attributable to the AI programme per sprint.

Baseline T/IU: T ÷ incremental OE. This is the throughput return on AI programme spend.

Target T/IU: set the minimum acceptable T/IU before programme renewal. Example: "We will renew if T/IU ≥ 1.5× baseline after 12 weeks."

→ verify: T/IU is computed from the constraint-stage throughput signal, not from a blended "productivity score."

**Step 3: Structure the scorecard.**

| Dimension | Signal | Baseline | 4-week | 8-week | 12-week | Target |
|-----------|--------|----------|--------|--------|---------|--------|
| **T — Delivery** | Constraint-stage merge rate | — | | | | +15% |
| **T — Quality** | Defect escape rate | — | | | | ≤ baseline |
| **T — Flow** | Review cycle time (P85) | — | | | | −20% |
| **I — WIP** | Open PRs at sprint end | — | | | | ≤ 5 |
| **OE — Tool** | Licence + infra cost/sprint | — | | | | fixed |
| **OE — Review** | Review hours at constraint | — | | | | −10% |
| **T/IU** | T delta ÷ incremental OE | 1.0× | | | | ≥ 1.5× |

**Step 4: Add the cost-of-delay row.**

For finance stakeholders, add a cost-of-delay calculation: estimated value of features not shipped per sprint at the pre-AI baseline, compared to the post-AI target. Express in revenue or cost-avoidance terms appropriate to the business. This row answers the question "what is the cost of not acting?" without replacing the T/IU row.

→ verify: the scorecard has at least one T signal, one I signal, one OE signal, and a T/IU composite. No LoC metric appears on the scorecard.

**Step 5: Track and review cadence.**

Review the scorecard at 4, 8, and 12 weeks post-rollout. Before week 8, treat all signals as directional — sample size is insufficient for causal claims (see SKILL.md study design defaults). A T/IU that is flat or declining by week 8 is the signal to run P5 (CRT) on the rollout before the 12-week renewal decision.

---

### R3 — Pilot-to-Rollout Metric Plan Using CRT and FRT

**Goal.** Design a metric plan for an AI coding pilot that produces credible evidence for rollout decisions, using CRT to surface the real problems the pilot must test and FRT to validate that the proposed rollout will resolve them.

**Inputs.** Proposed pilot scope (team, AI tool, duration), delivery system constraint from R1, existing concerns from stakeholders (quality, security, adoption, review burden).

**Step 1: Build a pre-pilot CRT from existing UDEs.**

Before the pilot begins, collect the undesirable effects stakeholders are attributing to the current (no-AI) state:

```
Example UDEs:
  UDE 1: "Feature cycle time has grown from 3 to 5 days over the past two quarters"
  UDE 2: "Senior developers spend > 30% of time in code review"
  UDE 3: "Onboarding new developers to the codebase takes 8+ weeks"
  UDE 4: "Defect escape rate has increased since the team doubled in size"
  UDE 5: "Two experienced developers are leaving; knowledge transfer is blocking delivery"
```

Trace "If…Then" chains to the Core Problem. In this example: *Codebase context is not accessible to developers at authoring and review time — relying instead on synchronous knowledge transfer via senior developers — making review the constraint and senior-developer time the critical resource.*

The Core Problem tells you what the pilot must test: not "does AI generate code?" but "does AI coding tooling reduce senior-developer review burden and accelerate codebase onboarding without increasing defect escape?"

→ verify: the Core Problem is a single statement that, if resolved, would weaken at least three of the UDEs.

**Step 2: Design pilot metrics from the CRT.**

Each UDE that the AI tool claims to address becomes a pilot metric. Each metric needs a baseline and a success threshold:

| UDE addressed | Metric | Baseline period | Success threshold |
|---------------|--------|----------------|-------------------|
| UDE 1 (cycle time) | Feature cycle time (P85) | 8 weeks pre-pilot | −15% vs. baseline |
| UDE 2 (review burden) | Senior-developer review hours/sprint | 8 weeks pre-pilot | −20% vs. baseline |
| UDE 3 (onboarding) | Time to first solo PR for new devs | Last 3 cohorts | −25% vs. cohort average |
| UDE 4 (defect escape) | Defects per sprint in production | 8 weeks pre-pilot | ≤ baseline |
| UDE 5 (knowledge transfer) | Context-quality score (codebase Q&A eval) | Pre-pilot benchmark | Measurable improvement |

→ verify: every metric maps to a named UDE; no metric is a tool-usage signal without a delivery or quality link.

**Step 3: Build a pre-rollout FRT.**

Before committing to full rollout, build a Future Reality Tree: assume the pilot injection (AI coding tooling with context engineering) is applied at scale.

```
Injection: AI coding tools with full codebase context deployed to all teams

→ IF  context-quality reduces irrelevant suggestions
  AND  AI-assisted review reduces senior-developer review time
  THEN  review cycle time decreases → resolves UDE 1
  THEN  senior developers have capacity for deeper design review → resolves UDE 2
  THEN  new developers can get faster answers from the tool → resolves UDE 3

  Check for Negative Branch Reservations:
  → Could AI suggestions create more noise at review if context is incomplete?
    Mitigation: context engineering is a prerequisite to rollout; measured by suggestion acceptance rate during pilot as a proxy for relevance.
  → Could reducing review burden inadvertently reduce the mentor relationship that senior developers provide?
    Mitigation: track developer experience metric on mentorship satisfaction; if it degrades, review-assistance scope is adjusted.
```

→ verify: the FRT resolves all Core Problem-linked UDEs; every Negative Branch Reservation has a named mitigation with a metric.

**Step 4: Set the pilot-to-rollout decision criteria.**

State explicitly: the rollout proceeds if and only if, by the end of the pilot:
- T is at or above threshold for the two highest-priority UDE metrics.
- Defect escape rate is ≤ baseline (quality gate with baseline, not intuition — see A4).
- No Negative Branch Reservation has materialised without a mitigation in place.

If these criteria are not met, run P5 (CRT) on the pilot results before redesigning the rollout scope.

**Output.** A pilot design document containing: the pre-pilot CRT, the metric set with baselines and thresholds, the FRT with Negative Branch Reservations and mitigations, and the explicit pilot-to-rollout decision criteria. This replaces vendor pilot templates as the measurement foundation for AI coding programmes.

---

## Composition

| Workflow | Entry primitive | Secondary | Close with |
|----------|----------------|-----------|-----------|
| New AI programme design | P1 (5FS) → constraint identification | P2 TA for investment framing | R1 + R2 for metric plan |
| Review queue overloaded after AI adoption | P3 DBR → set rope | P1 to confirm review is the constraint | A3 as diagnostic check |
| Rollout adoption plateau | P5 CRT → Core Problem | P4 EC if conflict is sustaining the Core Problem | R3 FRT before redesigning rollout |
| Leadership ROI case | P2 TA → T/IU calculation | A5 as frame for cost-of-delay row | R2 for full scorecard |
| Adoption-vs-quality deadlock | P4 EC → surface the sustaining assumption | P1 to redirect adoption to the constraint | P6 to subordinate non-constraint metrics |

**Never start with metrics before identifying the constraint.** Applying Throughput Accounting (P2) or building a scorecard (R2) before running 5FS (P1) produces a metric set that optimises for the wrong stage. 5FS is always step zero.

---

## Sources

These sources underpin the TOC primitives applied here. Full citation list is in
[`../../foundations-theory-of-constraints/references/primitives-overview.md`](../../foundations-theory-of-constraints/references/primitives-overview.md).

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press. — Origin of 5FS and throughput accounting; the core argument that system throughput is set by the constraint, not average performance.
- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press. — Throughput Accounting formalisation: T, I, OE and the inversion of cost-accounting logic applied in P2 and R2.
- Goldratt, E.M. (1994). *It's Not Luck*. North River Press. — Evaporating Cloud and the "challenge every assumption" discipline applied in P4.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press. — Policy constraint detection and DBR mechanics applied in P3 and P5.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. — CRT, EC, and FRT construction methodology applied in P5 and R3.
- Kim, G., Behr, K. & Spafford, G. (2013). *The Phoenix Project*. IT Revolution Press. — TOC applied to IT operations and software delivery; the "three ways" and WIP control in development pipelines.
- Forsgren, N., Humble, J. & Kim, G. (2018). *Accelerate*. IT Revolution Press. — Empirical evidence on delivery performance metrics; grounds the constraint-stage throughput signals in P2 and R2 in research-validated outcomes.
- McKinsey & Company. (2023). *The economic potential of generative AI*. McKinsey Global Institute. — Baseline productivity research framing; grounds the throughput-vs-cost-savings distinction in A5.
- Primitive playbooks in [`../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/) — canonical per-primitive definitions, failure modes, and worked examples for all 11 TOC primitives.
