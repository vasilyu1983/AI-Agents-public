---
name: product-management
description: "Founder-PM toolkit for discovery, roadmaps, prioritization, and PMF measurement. Use when planning product strategy, metrics, or roadmaps."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Product Management

Use this skill for product decisions that need evidence, trade-offs, and a concrete artifact. It owns discovery framing, PMF measurement, outcome roadmaps, prioritization, and stakeholder decision support. It is not a general PM theory skill.

## Quick Reference

| Task | Use |
|------|-----|
| Discovery and interviews | [assets/discovery/customer-interview-template.md](assets/discovery/customer-interview-template.md), [assets/discovery/assumption-test-template.md](assets/discovery/assumption-test-template.md), [assets/discovery/opportunity-solution-tree.md](assets/discovery/opportunity-solution-tree.md) |
| PMF and retention | [assets/discovery/pmf-survey-template.md](assets/discovery/pmf-survey-template.md), [references/pmf-measurement.md](references/pmf-measurement.md) |
| PMF scorecard (B2B / SaaS) | [assets/pmf-scorecard-b2b.yaml](assets/pmf-scorecard-b2b.yaml) — 10 dimensions, 100 weight, 2026 board benchmarks |
| PMF scorecard (B2C / Consumer) | [assets/pmf-scorecard-b2c.yaml](assets/pmf-scorecard-b2c.yaml) — viral coefficient + short-payback weighting |
| PMF bet memo (engine digest → single experiment) | [assets/pmf-bet-memo-template.md](assets/pmf-bet-memo-template.md) |
| Diamond Discovery (four-lens find of hidden product gems + disconfirmation gate + priced bet; works with zero analytics) | [references/diamond-discovery.md](references/diamond-discovery.md) |
| Prioritization and kill criteria | [assets/prioritization/prioritization-scorecard.md](assets/prioritization/prioritization-scorecard.md), [assets/prioritization/kill-criteria-template.md](assets/prioritization/kill-criteria-template.md), `python3 scripts/product_scorer.py rice --help` |
| Roadmaps and strategy | [assets/roadmap/outcome-roadmap.md](assets/roadmap/outcome-roadmap.md), [assets/strategy/product-vision-template.md](assets/strategy/product-vision-template.md), [assets/strategy/positioning-template.md](assets/strategy/positioning-template.md), [assets/strategy/quarterly-product-review.md](assets/strategy/quarterly-product-review.md) |
| Metrics and OKRs | [assets/metrics/metric-tree.md](assets/metrics/metric-tree.md), [assets/metrics/okr-template.md](assets/metrics/okr-template.md) |
| Stakeholder and leadership artifacts | [assets/ops/1-1-template.md](assets/ops/1-1-template.md), [assets/ops/feedback-template.md](assets/ops/feedback-template.md), [assets/ops/a3-debrief.md](assets/ops/a3-debrief.md), [assets/ops/negotiation-one-sheet.md](assets/ops/negotiation-one-sheet.md) |
| PMF or backlog scoring script | `python3 scripts/product_scorer.py --help` |

## When to Use This Skill

- Turn founder notes, customer inputs, or market signals into a roadmap, PMF plan, or decision brief.
- Define activation, retention, guardrails, and business metrics for a product area.
- Prioritize a backlog, set kill criteria, or cut low-value work.
- Build a quarterly product review, opportunity assessment, or strategy narrative.
- Write a product-facing artifact that needs clear trade-offs and measurable outcomes.

## Route Elsewhere

- PRDs and implementation-ready specs: use [docs-ai-prd](../docs-ai-prd/SKILL.md).
- GTM motion, ICP choice, or channel strategy: use `startup-gtm-strategy`.
- Growth experiments and acquisition loops: use `startup-growth-execution`.
- Product analytics instrumentation and event design: use `marketing-product-analytics`.
- Architecture or technical target-state design: use [software-architecture-design](../software-architecture-design/SKILL.md).

## Defaults

- Start from the decision, not the document.
- Define metrics with formula, timeframe, and data source.
- Use evidence labels such as strong, medium, and weak when confidence matters.
- Prefer outcome roadmaps over feature lists.
- Require kill criteria or rollback conditions for material bets.
- Measure PMF by segment, not as one blended company-wide score.

## Workflow

1. Clarify the decision, horizon, owner, and what would change the recommendation.
2. Choose the artifact type: discovery plan, roadmap, PMF assessment, prioritization, strategy note, or stakeholder brief.
3. Gather only the evidence needed to support that decision.
4. Define success metrics, guardrails, and explicit non-goals.
5. Rank options with one consistent method and document the trade-offs.
6. Produce the artifact plus the next review trigger, not just a static document.

## ASCII Flow

```text
Product decision or planning request
  -> Clarify decision, horizon, owner, and review trigger
  -> Select artifact type
     +-- discovery plan -> assumptions, interviews, opportunity map
     +-- PMF assessment -> segment signals, retention, activation, scorecard
     +-- roadmap -> outcomes, bets, guardrails, non-goals
     +-- prioritization -> scoring method, rank, kill criteria
     +-- strategy brief -> recommendation, evidence, trade-offs
  -> Gather only decision-relevant evidence
  -> Define success metrics, data source, timeframe, and guardrails
  -> Rank options and document what will not be done
  -> Return artifact plus next decision or experiment checkpoint
```

## Core Decisions

### Discovery and Evidence

Use discovery to de-risk value before building:
- customer interviews for pain, switching behavior, and decision criteria
- assumption tests for risky beliefs
- opportunity mapping when multiple problems compete for attention

If the evidence is thin, say so and define what would increase confidence.

Running the discovery cadence is not the same as learning. Check for [discovery theatre](references/discovery-best-practices.md#17-discovery-theatre--warning-signs) — interviews that only confirm, an opportunity tree that hasn't changed shape in a quarter, experiments with no real fail condition — before trusting the artifact.

### Prioritization and Saying No

Use one framework consistently:
- RICE or ICE for ranked backlogs
- opportunity scoring for discovery-heavy work
- cost-of-delay or WSJF for time-sensitive flow problems

Minimum control set:
- a scorecard
- kill criteria
- one sentence explaining why lower-ranked work is not being done now

Do not allow stakeholder pressure to replace trade-off documentation.

A scored ranking is not a substitute for judgment. RICE and similar formulas produce false precision from point-estimate guesses — see [RICE Precision Theatre](references/prioritization-frameworks.md#rice-precision-theatre-what-a-sharp-cpo-catches) for the tells (rankings that never change, ties broken by seniority instead of evidence, zero-to-one bets scored against tactical work on the same stack). Use the framework to force an explicit trade-off conversation, not to end one.

### PMF and Retention

PMF is not one survey result. Check:
- Sean Ellis style disappointment or must-have signal
- retention curve shape
- activation that predicts durable retention
- segment-specific PMF rather than blended averages

If the product is liked but not indispensable, tighten the must-have path before adding breadth.

For data-rich products, run the PMF Insight Engine in `marketing-product-analytics` (`assets/pmf-insight-engine.md` + 10 blind-spot detectors) to surface signals the team cannot see by intuition. Then score against the appropriate path:

- **Path A (B2B / SaaS)** — [assets/pmf-scorecard-b2b.yaml](assets/pmf-scorecard-b2b.yaml). Heavier weights on retention curve, NRR, CAC payback (top-quartile is <=6 months; 2025 median is ~16 months; <12 months is a strong/goal benchmark but not top-quartile — do not report it as such at board level), ICP concentration, and value-metric alignment. For usage-based or AI-native products, seat-based PMF assumptions misdiagnose consumption products — use the UBP signals in [references/pmf-measurement.md](references/pmf-measurement.md#usage-based--ai-native-pmf-signals) alongside this scorecard.
- **Path B (B2C / Consumer)** — [assets/pmf-scorecard-b2c.yaml](assets/pmf-scorecard-b2c.yaml). Heavier weights on Week-4 retention, switching trigger evidence, viral coefficient, 6-month payback, and category entry point.

The scorecard outputs a 0-100 readiness score plus the weakest dimension. The weakest dimension that also has a detector hit becomes the candidate for a [bet memo](assets/pmf-bet-memo-template.md). The bet memo is the contract that converts evidence into one experiment with a kill criterion.

### Roadmaps and Strategy

Prefer:
- outcome roadmap
- theme roadmap when uncertainty is higher
- strategy artifact only when it changes sequencing, focus, or the target customer

Every roadmap should state:
- target outcome
- key bets
- metric and guardrail
- what is intentionally out of scope

**Commitment trade-off**: every date on a roadmap is a promise that trades away discovery flexibility. A "Now" horizon with hard dates is appropriate once a bet has passed discovery — committing dates on unvalidated "Later" bets converts hypotheses into obligations the team will ship regardless of what evidence says. When a stakeholder asks for a date on a "Later" item, the honest answer is a range plus the validation gate that must clear first, not a date under pressure. High-integrity commitments (Cagan, *Empowered*) are the exception granted only after value, usability, feasibility, and viability risk have been addressed — not the default operating mode for a roadmap.

### Stakeholder Management

Good stakeholder work means:
- decisions are documented
- trade-offs are visible
- asks are explicit
- commitments are separated from exploration

Lead with what was learned and what decision follows, not a list of shipped items.

### AI and Automation

In 2026, AI product work is a primary PM domain — not an add-on. Use [references/ai-product-patterns.md](references/ai-product-patterns.md) for the full operational guide covering AI product lifecycle, agentic patterns, RAG, risk governance, experiment types, and the decision tree for when to use AI vs. rules. Key operating principles:

- Use AI support only when explicitly needed and keep it bounded: scoring candidate opportunities, structuring interview notes, comparing options, spotting anomalies in feedback or usage.
- For AI features, require: problem validation, data readiness score, evaluation metrics, safety guardrails, human-in-the-loop path, and drift monitoring before launch.
- For agentic products, define agent role, tool access, constraints, success criteria, failure modes, and escalation path explicitly.

Human judgment still owns prioritization, ethics, and irreversible product bets.

## Output Modes

Default to one of these:

- Product decision brief:
  recommendation, evidence, trade-offs, metrics, and next review point.
- Outcome roadmap:
  now, next, later with outcomes, bets, and guardrails.
- PMF assessment:
  segment-level signal review, retention view, activation definition, and recovery loop.
- PMF scorecard + bet memo:
  scored readiness against the B2B or B2C scorecard, with a single bet memo per active experiment. Tied to detector evidence from the PMF Insight Engine.
- Prioritization package:
  ranked backlog, kill criteria, and explicit non-goals.

## Anti-Patterns

- Roadmap theater with no measurable outcomes.
- Vanity metrics without activation or retention definitions.
- Building first and searching for evidence later.
- Expanding scope without adjusting trade-offs.
- Treating PMF as one binary milestone.
- Saying yes to everything because a stakeholder asked.
- Scoring a zero-to-one bet on the same RICE/WSJF stack as tactical backlog work — the denominators structurally punish anything new and unproven (see [Strategic Bets vs Tactical Backlog](references/prioritization-frameworks.md#strategic-bets-vs-tactical-backlog)).
- Committing a hard date on a "Later" bet that has not cleared discovery, just to end a scoping argument.

**What a checklist misses and an experienced operator catches**: whether the artifact answers the actual decision in front of the business, or just satisfies the template. A RICE stack, an OST, and an OKR sheet can all be filled in correctly and still miss the point if the underlying decision — build vs. buy, expand vs. focus, fund this team vs. that one — was never named. Before producing any artifact, state the decision it is meant to inform in one sentence; if that sentence cannot be written, the artifact is busywork.

## Navigation

> **Gate before invoking any foundation below:** Each foundation has a `When to Apply` / `When to Skip` section. If your task matches a skip-condition, route to the foundation it names instead — don't pull in primitives the task doesn't need.

- Discovery: [references/discovery-best-practices.md](references/discovery-best-practices.md), [references/interviewing-patterns.md](references/interviewing-patterns.md), [assets/discovery/customer-interview-template.md](assets/discovery/customer-interview-template.md), [assets/discovery/assumption-test-template.md](assets/discovery/assumption-test-template.md), [assets/discovery/opportunity-solution-tree.md](assets/discovery/opportunity-solution-tree.md), [assets/discovery/pmf-survey-template.md](assets/discovery/pmf-survey-template.md)
- PMF scoring and bets: [assets/pmf-scorecard-b2b.yaml](assets/pmf-scorecard-b2b.yaml), [assets/pmf-scorecard-b2c.yaml](assets/pmf-scorecard-b2c.yaml), [assets/pmf-bet-memo-template.md](assets/pmf-bet-memo-template.md), [references/pmf-measurement.md](references/pmf-measurement.md)
- Diamond Discovery: [references/diamond-discovery.md](references/diamond-discovery.md) — four-lens method (anomaly / jobs / friction / value-capture) to surface non-obvious product gems, a disconfirmation gate that filters fool's gold, diamond scoring (leverage × value_signal × differentiation), and a Diamond Brief that feeds the bet memo. Trigger: "what am I missing?", "find the hidden gem", "what could 10x this?". Pairs with `marketing-product-analytics` detectors 11–14 when data exists; works from screenshots/tickets/interviews when it doesn't.
- Strategy and positioning: [references/strategy-patterns.md](references/strategy-patterns.md), [references/positioning-patterns.md](references/positioning-patterns.md), [assets/strategy/product-vision-template.md](assets/strategy/product-vision-template.md), [assets/strategy/positioning-template.md](assets/strategy/positioning-template.md), [assets/strategy/opportunity-assessment.md](assets/strategy/opportunity-assessment.md), [assets/strategy/PRFAQ-template.md](assets/strategy/PRFAQ-template.md), [assets/strategy/quarterly-product-review.md](assets/strategy/quarterly-product-review.md)
- Roadmaps, metrics, and prioritization: [references/roadmap-patterns.md](references/roadmap-patterns.md), [references/metrics-best-practices.md](references/metrics-best-practices.md), [references/prioritization-frameworks.md](references/prioritization-frameworks.md), [references/pmf-measurement.md](references/pmf-measurement.md), [assets/roadmap/outcome-roadmap.md](assets/roadmap/outcome-roadmap.md), [assets/roadmap/theme-roadmap.md](assets/roadmap/theme-roadmap.md), [assets/metrics/metric-tree.md](assets/metrics/metric-tree.md), [assets/metrics/okr-template.md](assets/metrics/okr-template.md), [assets/prioritization/prioritization-scorecard.md](assets/prioritization/prioritization-scorecard.md), [assets/prioritization/kill-criteria-template.md](assets/prioritization/kill-criteria-template.md)
- Leadership and operations: [references/stakeholder-management.md](references/stakeholder-management.md), [references/leadership-decision-frameworks.md](references/leadership-decision-frameworks.md), [references/operational-guide.md](references/operational-guide.md), [assets/ops/1-1-template.md](assets/ops/1-1-template.md), [assets/ops/feedback-template.md](assets/ops/feedback-template.md), [assets/ops/a3-debrief.md](assets/ops/a3-debrief.md), [assets/ops/negotiation-one-sheet.md](assets/ops/negotiation-one-sheet.md)
- Scripts and sample data: `scripts/product_scorer.py`, `scripts/README.md`, [data/sample-features.json](data/sample-features.json), [data/sample-pmf-data.json](data/sample-pmf-data.json)
- Causal toolkit: [references/causal-inference-applied.md](references/causal-inference-applied.md) — Causal-inference applied recipes for PM: feature impact under non-random adoption, mediation, regional rollout retention.
- Decision-theory toolkit: [references/decision-theory-applied.md](references/decision-theory-applied.md) — Decision-theory applied recipes for PM: VoI gating, MAB resource reallocation, real-options launches.
- Behavioral-economics toolkit: [references/behavioral-economics-applied.md](references/behavioral-economics-applied.md) — Behavioral-econ applied recipes for PM: activation defaults with reversibility, retention nudges with ethical gates.
- Theory-of-constraints toolkit: [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) — TOC applied recipes for PM: roadmap re-rank by bottleneck, funnel debug via CRT, T/CU scoring.
- Cybernetics-VSM toolkit: [references/cybernetics-vsm-applied.md](references/cybernetics-vsm-applied.md) — VSM, Ashby's law, feedback loops, algedonic channels applied to product management and operating model design.
- AI and agentic product patterns: [references/ai-product-patterns.md](references/ai-product-patterns.md) — Operational guide for AI, GenAI, and agentic product development: lifecycle phases, agentic orchestration patterns (planner/executor, multi-agent, guardrail critic), RAG templates, risk and governance checklists, experiment types, and decision trees for when to use AI.
- Data product patterns: [references/data-product-best-practices.md](references/data-product-best-practices.md) — Data product canvas, lifecycle phases, data contracts, governance checklists, ML pipeline templates, and definition of done for data products.
- Cognitive-load toolkit: [references/cognitive-load-product-design.md](references/cognitive-load-product-design.md) — Cognitive load theory applied to product design and AI-assisted workflows: intrinsic/extraneous/germane load, human-AI load distribution, amplification vs. delegation, and the verification-tax test.
- Delivery and handoff: [references/delivery-best-practices.md](references/delivery-best-practices.md) — Checklist for PM-to-engineering handoff: acceptance criteria, backlog quality, engineering handoff artifacts, execution cadence, quality gates, and post-launch review.
- Consumer-neuroscience foundation: [../foundations-consumer-neuroscience/SKILL.md](../foundations-consumer-neuroscience/SKILL.md) — attention/salience, reward-anticipation, narrative transportation, and DMCC ethical audit primitives for activation, engagement, and habit-design decisions.

## Fact-Checking

- Primary sources live in [data/sources.json](data/sources.json).
- Framework relevance, benchmark claims, tooling recommendations, and market-specific best practices should be refreshed against current primary sources before making definitive recommendations.
- If current external data cannot be checked, mark the recommendation as based on durable patterns rather than current market verification.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

