---
description: Short-form and full-form launch prompts for installed teams and saved expert-board modes.
last_verified: 2026-09-16
status: stable
---

# Team Prompt Patterns

Use this reference when you already know which installed team or saved workflow mode to run and need either:

- a **short prompt** to get moving quickly
- a **full prompt** with stronger structure, constraints, and synthesis instructions

The short prompts are good for daily use when the required named members are
installed or the selected workflow uses generic role briefs. The full prompts
are better for higher-stakes work, handoff-heavy tasks, or repeatable operating
playbooks.

This file is the default source for the **initial launch prompt** after `agents-subagents` has selected the correct team or debate-enabled team for a scenario.

See [team-scenarios.md](team-scenarios.md) for scenario-driven examples.

## Table of Contents

- [Shared Prompt Pattern](#shared-prompt-pattern)
- [Selection to Prompt Flow](#selection-to-prompt-flow)
- [Startup Strategy](#startup-strategy)
- [Expert Board: Growth](#expert-board-growth)
- [Expert Board: Founder Blindspot](#expert-board-founder-blindspot)
- [Expert Board: Monetization](#expert-board-monetization)
- [Code Review](#code-review)
- [Feature Dev](#feature-dev)
- [Context Engineering](#context-engineering)
- [Expert Board: Architecture RFC](#expert-board-architecture-rfc)
- [Expert Board: Incident Response](#expert-board-incident-response)
- [Migration Map](#migration-map)
- [Expert Board: Release Readiness](#expert-board-release-readiness)
- [Growth Experiment](#growth-experiment)
- [Expert Board: Marketing Diagnostics](#expert-board-marketing-diagnostics)
- [Expert Board: Enterprise Readiness](#expert-board-enterprise-readiness)
- [AI Systems](#ai-systems)
- [Data Analytics](#data-analytics)
- [Docs Knowledge](#docs-knowledge)
- [Product Discovery](#product-discovery)
- [Product Surface](#product-surface)
- [Ops Platform](#ops-platform)
- [Payments Platform](#payments-platform)
- [Mobile Product](#mobile-product)
- [Ad-hoc Specialists (No Named Team)](#ad-hoc-specialists-no-named-team)

## Shared Prompt Pattern

## Selection to Prompt Flow

Use this sequence:

1. Use `agents-subagents` to decide whether the job needs a single agent, shared member, shared team, or debate mode.
2. If a team is the right mode, use this file to prepare the first prompt.
3. Start with the short prompt when the runtime can fill small gaps interactively.
4. Use the full prompt when you need explicit ownership, debate rules, or synthesis control.

### Short prompt

Use this when you want the runtime to help fill in small gaps:

```text
Use the installed `<team>` team for [goal].

Context:
- [repo, diff, problem, or business context]
- [optional artifacts or evidence]

Return:
- top findings or recommendation
- key risks
- next actions
```

### Full prompt

Use this when you want predictable behavior and clean synthesis:

```text
Use the installed `<team>` team.

Goal:
- [what decision or output is needed]

Required context:
- [must-have task context]

Optional context:
- [artifacts, graphs, logs, docs, market inputs]

Instructions:
- [member 1] owns [...]
- [member 2] owns [...]
- [member 3] owns [...]
- [member 4] owns [...]
- [parallel or staged execution rule]
- [debate rule if needed]
- [synthesis owner or parent-thread synthesis rule]

Return:
- recommendation or findings
- major risks and open questions
- exact next actions
```

## Startup Strategy

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "startup-strategy"` to evaluate this startup idea: [idea].

Context:
- target customer: [customer]
- main problem: [problem]
- constraint: [constraint]

Return:
- viability read
- best wedge
- next validation steps
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "startup-strategy"`.

Goal:
- Evaluate whether this idea is worth validating now and what the best first wedge is.

Required context:
- Idea: [idea]
- Target customer: [customer]
- Main pain: [problem]
- Constraint: [constraint]

Instructions:
- marketing-strategist assesses category framing, message clarity, and differentiation
- startup-business-developer assesses buyer, revenue model, and partnership opportunities
- startup-growth-specialist assesses distribution and activation feasibility
- product-strategist assesses PMF signal and validation order
- software-ux-designer assesses learnability and first-run friction
- Run in parallel first, then challenge assumptions across members
- product-strategist synthesizes the final recommendation

Return:
- go / validate / pivot recommendation
- strongest wedge
- top risks
- next 3 validation steps
```

## Expert Board: Growth

### Short prompt

```text
Run the saved `expert-board` workflow in `growth` mode to challenge whether the company is growing in a healthy way.

Context:
- stage: [stage]
- latest growth metrics: [metrics]
- main concern: [concern]

Return:
- honest growth read
- what to improve next
- strongest disagreement
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "growth"`.

Goal:
- Challenge whether the company is actually growing in a healthy way and decide the next improvement priority.

Required context:
- Stage: [stage]
- Target customer: [customer]
- Latest growth metrics: [metrics]
- Main concern: [concern]

Optional context:
- funnel trends
- active experiments
- pricing notes
- channel performance

Instructions:
- product-strategist challenges the current wedge, priorities, and product direction
- startup-growth-specialist challenges whether the current loops and experiments actually compound
- marketing-product-analytics-lead challenges whether the metric interpretation is trustworthy
- startup-product-marketing-strategist challenges demand capture, positioning, category frame, launch narrative, and proof assets
- startup-business-developer challenges monetization, buyer quality, and partnership leverage
- Run in parallel first
- Then force a debate on what should improve next: product, distribution, or monetization
- product-strategist synthesizes the founder memo

Return:
- healthy / misleading / fragile growth read
- strongest improvement priority
- strongest dissent
- next 3 operating moves
```

## Expert Board: Founder Blindspot

### Short prompt

```text
Run the saved `expert-board` workflow in `founder-blindspot` mode to surface what we may be missing.

Context:
- startup: [name]
- current bottleneck: [bottleneck]
- qualitative evidence: [reviews, tickets, objections, notes]

Return:
- hidden opportunities
- strongest weak signals
- best narrow wedge to investigate next
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "founder-blindspot"`.

Goal:
- Find the hidden opportunities, ignored objections, or timing signals that the founder may be missing.

Required context:
- Startup: [name]
- Current bottleneck: [bottleneck]
- Target customer: [customer]
- Qualitative or market evidence: [evidence]

Optional context:
- Competitor references
- Funnel snapshots
- Retention or monetization notes
- Sales objections

Instructions:
- startup-painpoint-scout maps repeated pain and workflow friction
- startup-review-miner mines explicit user language for switching triggers and value objections
- startup-trend-analyst checks whether timing or external shifts matter
- startup-competitive-analyst checks whether a competitor or adjacent player is already exploiting the wedge
- product-strategist synthesizes what matters for PMF and prioritization
- Run in parallel first
- Then debate whether the best next move is a narrower wedge, a new segment, a timing adjustment, or simply a messaging correction
- product-strategist synthesizes the final memo

Return:
- hidden opportunities
- strongest evidence
- best narrow wedge
- what not to chase
- missing data
```

## Expert Board: Monetization

### Short prompt

```text
Run the saved `expert-board` workflow in `monetization` mode to diagnose why monetization is weaker than expected.

Context:
- startup: [name]
- current pricing or paywall: [summary]
- monetization concern: [concern]

Return:
- monetization diagnosis
- pricing or packaging gaps
- best next experiments
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "monetization"`.

Goal:
- Diagnose the main monetization constraint and recommend the safest useful pricing or packaging experiments.

Required context:
- Startup: [name]
- Target customer: [customer]
- Current pricing/paywall structure: [summary]
- Main monetization concern: [concern]

Optional context:
- Free-to-paid funnel
- Upgrade and downgrade behavior
- Competitor pricing
- Sales objections
- Cohort notes

Instructions:
- startup-pricing-advisor leads the monetization diagnosis and synthesis
- marketing-product-analytics-lead validates cohort and funnel trustworthiness
- marketing-strategist checks value communication and pricing-page clarity
- startup-operating-system-reviewer checks downside risk and revenue quality
- startup-business-developer checks willingness-to-pay and commercial fit
- Run in parallel first
- Then debate whether the next move should be packaging, value communication, paywall timing, or price level
- startup-pricing-advisor synthesizes the final memo

Return:
- monetization diagnosis
- strongest pricing and packaging gaps
- top 3 experiments
- risks and guardrails
- measurement requirements
```

## Code Review

### Short prompt

```text
Use the installed `software-code-review-board` team to review [diff, PR, or module].

Context:
- focus area: [area]
- optional artifacts: [graph/report paths]

Return:
- prioritized findings
- likely regressions
- smallest safe fixes
```

### Full prompt

```text
Use the installed `software-code-review-board` team.

Goal:
- Review [diff, PR, or module] before merge.

Required context:
- Review target: [target]
- Focus area: [area]

Optional context:
- graphs/code-graph.json
- reports/query-*.md

Instructions:
- software-security-reviewer checks auth boundaries, data exposure, abuse paths, and unsafe assumptions
- software-performance-reviewer checks latency, hot paths, query behavior, and caching regressions
- qa-test-reviewer checks coverage gaps, edge cases, and release confidence
- Run in parallel
- Parent thread synthesizes the final review report

Return:
- findings grouped by severity
- rationale
- smallest safe fix for each issue
```

## Feature Dev

### Short prompt

```text
Use the installed `dev-feature-delivery` team to deliver [feature].

Context:
- acceptance criteria: [criteria]
- repo: [repo]
- optional artifacts: [graph/profile/report paths]

Return:
- research summary
- implementation summary
- review verdict
```

### Full prompt

```text
Use the installed `dev-feature-delivery` team.

Goal:
- Deliver [feature or fix] with bounded research and final review.

Required context:
- Acceptance criteria: [criteria]
- Repo target: [repo]

Optional context:
- profiles/*.json
- graphs/code-graph.json
- reports/query-*.md

Instructions:
- dev-feature-researcher goes first and maps modules, constraints, and existing patterns
- dev-feature-implementer works only after the research handoff
- dev-feature-reviewer reviews the implementation for correctness and regression risk
- Keep the workflow staged

Return:
- research output
- implementation summary
- review findings
- remaining work before merge, if any
```

## Context Engineering

### Short prompt

```text
Use the installed `dev-context-preparation` team to prepare reusable context for [repos or scope].

Context:
- target area: [area]
- target repos: [repos]

Return:
- artifact paths
- stale or missing evidence
- the packet downstream teams should read first
```

### Full prompt

```text
Use the installed `dev-context-preparation` team.

Goal:
- Build or refresh reusable context artifacts for [repos or scope].

Required context:
- Target repos: [repos]
- Focus area: [area]

Optional context:
- existing profiles, catalog pages, and graphs

Instructions:
- dev-portfolio-mapper inventories and normalizes repo/portfolio context
- dev-repo-context-curator identifies hot, warm, and cold context sources
- dev-code-graph-builder refreshes code graphs and query reports where needed
- dev-context-packet-synthesizer builds the small downstream packet
- Keep the workflow staged and artifact-first

Return:
- artifact paths created or refreshed
- stale areas
- the single packet downstream workers should consume first
```

## Expert Board: Architecture RFC

### Short prompt

```text
Run the saved `expert-board` workflow in `architecture-rfc` mode to evaluate [architecture decision].

Context:
- constraints: [constraints]
- affected repos or systems: [scope]
- optional artifacts: [graph/profile paths]

Return:
- preferred option
- tradeoffs
- phased recommendation
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "architecture-rfc"`.

Goal:
- Produce an RFC-style recommendation for [architecture decision].

Required context:
- Decision: [decision]
- Constraints: [constraints]
- Scope: [scope]

Optional context:
- profiles/*.json
- graphs/system-edges.json
- graphs/code-graph.json

Instructions:
- software-solution-architect compares target-state options and transition paths
- dev-api-designer evaluates interface and contract implications
- data-architect evaluates data ownership, consistency, and migration risk
- software-risk-reviewer evaluates security, resilience, and operational risks
- Run analysis in parallel
- If the decision is hard to reverse, run a debate round before synthesis
- software-solution-architect synthesizes the final RFC recommendation

Return:
- preferred option
- decision matrix
- main risks
- phased migration or adoption path
```

## Expert Board: Incident Response

### Short prompt

```text
Run the saved `expert-board` workflow in `incident` mode for this incident: [incident].

Context:
- symptoms: [symptoms]
- timeline: [timeline]
- optional evidence: [logs/traces/dashboards]

Return:
- likely root cause
- immediate action
- missing evidence
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "incident"`.

Goal:
- Triage the incident and recommend the safest immediate response.

Required context:
- Symptoms: [symptoms]
- Timeline: [timeline]
- Impacted services: [services]

Optional context:
- logs
- traces
- dashboards
- recent deploy history

Instructions:
- ops-incident-commander owns synthesis and next-action recommendation
- qa-debugger traces likely failure points in code and recent changes
- qa-observability-lead inspects failure signatures in logs, traces, and metrics
- qa-resilience-reviewer evaluates rollback, containment, and mitigation options
- Run the first analysis round in parallel
- If rollback vs fix-forward is genuinely disputed, run a debate round before the final recommendation

Return:
- likely failure chain
- confidence level
- safest immediate action
- evidence still needed
```

## Migration Map

### Short prompt

```text
Use the installed `dev-migration-map` team to plan [migration].

Context:
- target state: [target]
- compatibility constraints: [constraints]
- optional artifacts: [graph/profile paths]

Return:
- migration phases
- dependency hotspots
- rollback strategy
```

### Full prompt

```text
Use the installed `dev-migration-map` team.

Goal:
- Produce a migration plan for [migration].

Required context:
- Migration goal: [goal]
- Timeline: [timeline]
- Compatibility constraints: [constraints]

Optional context:
- profiles/*.json
- graphs/system-edges.json
- graphs/code-graph.json

Instructions:
- dev-portfolio-mapper identifies affected repos and ownership boundaries
- dev-dependency-auditor maps package and call-site dependencies
- dev-migration-planner proposes sequencing, cutover model, and target-state path
- ops-rollout-reviewer validates testability, rollout safety, and rollback constraints
- Keep the workflow staged with parallel discovery where useful
- Run debate only if sequencing or cutover strategy is contested

Return:
- phased migration plan
- dependency hotspots
- compatibility strategy
- rollback and validation gates
```

## Expert Board: Release Readiness

### Short prompt

```text
Run the saved `expert-board` workflow in `release-readiness` mode to assess this release candidate.

Context:
- release scope: [scope]
- evidence: [evidence]
- rollback path: [rollback]

Return:
- go/no-go recommendation
- blockers
- pre-release actions
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "release-readiness"`.

Goal:
- Decide whether this release candidate is ready for production.

Required context:
- Release scope: [scope]
- Verification evidence: [evidence]
- Rollback path: [rollback]

Optional context:
- graphs/code-graph.json
- reports/query-*.md
- runbooks
- release notes

Instructions:
- qa-test-reviewer checks coverage, edge cases, and confidence level
- docs-runbook-auditor checks operator clarity and runbook completeness
- software-performance-reviewer checks likely regressions and hot-path risk
- ops-rollback-planner checks blast radius and rollback safety
- Run checks in parallel
- Parent thread synthesizes the go/no-go recommendation
- Use debate only if the team is genuinely split on ship vs delay

Return:
- go/no-go recommendation
- blockers
- non-blocking risks
- exact actions before release
```

## Growth Experiment

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "growth-experiments"` to choose the next experiment for [metric or funnel stage].

Context:
- target metric: [metric]
- funnel issue: [issue]
- optional context: [analytics map, landing pages, paid channel data]

Return:
- ranked experiments
- expected impact
- instrumentation needs
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "growth-experiments"`.

Goal:
- Diagnose the funnel issue and choose the next best experiment.

Required context:
- Funnel stage: [stage]
- Target metric: [metric]
- Main issue: [issue]

Optional context:
- analytics event map
- landing pages
- paid channel performance

Instructions:
- startup-growth-specialist identifies leverage points in the funnel
- marketing-product-analytics-lead validates instrumentation and interpretation quality
- marketing-paid-acquisition-strategist checks traffic quality and acquisition-side distortion
- marketing-strategist checks promise-to-product message mismatch
- Run in parallel
- startup-growth-specialist synthesizes the ranked experiment list
- Use debate if the disagreement is acquisition quality versus onboarding/activation quality

Return:
- top experiments
- expected impact
- confidence
- required instrumentation or prerequisite changes
```

## Expert Board: Marketing Diagnostics

### Short prompt

```text
Run the saved `expert-board` workflow in `marketing-diagnostics` mode to diagnose [metrics, SEO, and AEO problem].

Context:
- metrics: [metrics]
- target pages or surfaces: [pages]
- main question: [question]

Return:
- diagnosis
- what to improve first
- why that order wins
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "marketing-diagnostics"`.

Goal:
- Diagnose product metrics, SEO, and AEO performance and decide what to improve first.

Required context:
- Current metrics: [metrics]
- Target funnel stage: [stage]
- Pages or surfaces under review: [pages]

Optional context:
- Search Console exports
- AI-answer examples
- event maps
- experiment history

Instructions:
- marketing-product-analytics-lead validates whether the metric read and attribution are trustworthy
- startup-growth-specialist identifies the highest-leverage funnel or conversion improvements
- marketing-seo-strategist identifies the strongest technical and content SEO gaps
- marketing-aeo-strategist identifies the strongest answer-engine visibility and citation gaps
- Run in parallel first
- Then force a debate on what should improve first: analytics cleanup, SEO, AEO, or funnel conversion
- startup-growth-specialist synthesizes the final plan

Return:
- diagnosis by domain
- first improvement priority
- rationale for the ordering
- expected impact and next actions
```

## Expert Board: Enterprise Readiness

### Short prompt

```text
Run the saved `expert-board` workflow in `enterprise-readiness` mode to assess readiness for [customer or enterprise motion].

Context:
- customer requirements: [requirements]
- trust posture: [posture]
- operating constraints: [constraints]

Return:
- blockers
- quick wins
- 30-day readiness plan
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "enterprise-readiness"`.

Goal:
- Assess readiness for [customer or enterprise motion] and define the shortest credible plan to close gaps.

Required context:
- Customer requirements: [requirements]
- Trust posture: [posture]
- Operating constraints: [constraints]

Optional context:
- security docs
- support workflows
- finance ops notes

Instructions:
- startup-compliance-readiness-lead owns the final readiness plan
- software-security-reviewer identifies procurement and trust blockers
- startup-growth-execution-operator identifies onboarding and support gaps
- startup-operating-system-reviewer identifies commercial and operational maturity gaps
- Run the first analysis round in parallel
- Use debate if the key decision is "sell now with workarounds" versus "delay until readiness improves"
- startup-compliance-readiness-lead synthesizes the final plan

Return:
- readiness level
- blockers
- quick wins
- 30-day readiness plan
```

## AI Systems

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "ai-systems"` to design [AI workflow or agent system].

Context:
- users: [users]
- constraints: [constraints]
- existing context or eval assets: [assets]

Return:
- recommended topology
- context/retrieval contract
- eval and rollout gate
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "ai-systems"`.

Goal:
- Design [AI workflow or agent system] so it is grounded, permission-safe, and measurable.

Required context:
- Users: [users]
- Core workflow: [workflow]
- Constraints: [constraints]

Optional context:
- prompts
- traces
- current retrieval assets
- current evals

Instructions:
- ai-agent-architect defines the agent and tool topology
- ai-context-architect defines hot, warm, and cold context layers
- ai-retrieval-architect defines retrieval and citation design
- ai-evals-observer defines evals, trace capture, and rollout gates
- Run parallel analysis, then synthesize
- Use debate for major architecture or retrieval tradeoffs
- ai-agent-architect owns the final synthesis

Return:
- architecture recommendation
- context and retrieval contract
- eval plan
- rollout gate
```

## Data Analytics

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "data-analytics"` to diagnose [metric, pipeline, or instrumentation problem].

Context:
- business question: [question]
- current pain: [pain]
- available models or dashboards: [artifacts]

Return:
- trust issues
- root causes
- minimum fix plan
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "data-analytics"`.

Goal:
- Restore trust in [metric, pipeline, or instrumentation problem].

Required context:
- Business question: [question]
- Current pain: [pain]
- Data consumers: [consumers]

Optional context:
- warehouse models
- dashboards
- query plans
- event definitions

Instructions:
- data-analytics-engineer reviews semantic and modeling contracts
- data-sql-optimizer reviews expensive or suspicious SQL paths
- data-streaming-architect reviews data flow and replayability
- data-instrumentation-analyst reviews event quality and identity joins
- Run in hybrid mode
- data-analytics-engineer synthesizes the final trust-restoration plan

Return:
- source-of-truth issues
- root causes
- minimum fix plan
- verification steps
```

## Docs Knowledge

### Short prompt

```text
Use the installed `docs-knowledge` team to improve [docs surface or knowledge system].

Context:
- audience: [audience]
- current pain: [pain]
- note/doc sources: [sources]

Return:
- target doc structure
- retrieval improvements
- highest-priority fixes
```

### Full prompt

```text
Use the installed `docs-knowledge` team.

Goal:
- Make [docs surface or knowledge system] more trustworthy and usable.

Required context:
- Audience: [audience]
- Current pain: [pain]

Optional context:
- docs folders
- runbooks
- note vaults
- current PRD or planning docs

Instructions:
- docs-codebase-architect proposes the doc architecture
- docs-ai-prd-writer writes or tightens the implementation-ready PRD
- docs-notes-retrieval-curator identifies which notes should become retrievable context
- docs-quality-auditor checks coverage and freshness
- Keep the workflow staged
- docs-codebase-architect synthesizes the final plan

Return:
- target doc structure
- curated note sources
- PRD readiness notes
- highest-priority fixes
```

## Product Discovery

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "product-discovery"` to evaluate [product decision].

Context:
- user/problem: [context]
- business constraint: [constraint]
- optional evidence: [evidence]

Return:
- recommended priority
- supporting evidence
- next evidence to gather
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "product-discovery"`.

Goal:
- Choose the best next product decision for [decision].

Required context:
- User and problem: [context]
- Business constraint: [constraint]

Optional context:
- research notes
- funnel data
- competitor references

Instructions:
- product-manager frames the decision and sequencing logic
- product-user-researcher interprets behavior and usability evidence
- startup-competitive-analyst assesses external pressure and differentiation
- marketing-product-analytics-lead checks what the data really says
- Run in parallel
- Use debate if user, competitive, and analytics signals conflict materially
- product-manager synthesizes the recommendation

Return:
- recommended priority
- strongest evidence
- main counterargument
- next evidence to gather
```

## Product Surface

### Short prompt

```text
Use the installed `product-surface` team to review [UI surface or product flow].

Context:
- target flow: [flow]
- implementation scope: [scope]
- locales: [locales]

Return:
- biggest surface problems
- affected flows
- smallest high-leverage fixes
```

### Full prompt

```text
Use the installed `product-surface` team.

Goal:
- Improve [UI surface or product flow] across implementation, UX, accessibility, and localization.

Required context:
- Target flow: [flow]
- Implementation scope: [scope]

Optional context:
- screenshots
- design references
- component map
- locale list

Instructions:
- software-frontend-lead checks structure, state boundaries, and implementation fit
- software-ux-designer checks clarity and user friction
- software-accessibility-reviewer checks semantics, focus, and keyboard safety
- software-localisation-reviewer checks externalization, formatting, and locale safety
- Run in parallel
- software-frontend-lead synthesizes the improvement plan

Return:
- biggest surface problems
- affected flows
- smallest high-leverage fixes
```

## Ops Platform

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "ops-platform"` to review [platform or operations problem].

Context:
- current pain: [pain]
- cost concern: [cost]
- available telemetry: [artifacts]

Return:
- platform changes worth making
- safe savings
- telemetry and resilience gaps
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "ops-platform"`.

Goal:
- Improve [platform or operations problem] without weakening delivery reliability.

Required context:
- Current pain: [pain]
- Cost concern: [cost]
- Operating constraints: [constraints]

Optional context:
- logs
- traces
- bills
- incident history

Instructions:
- ops-platform-engineer reviews the platform operating model
- ops-cost-optimizer reviews waste and right-sizing opportunities
- qa-observability-lead reviews telemetry quality and signal gaps
- qa-resilience-reviewer reviews failure handling and reliability posture
- Run in hybrid mode
- Use debate for cost-versus-reliability or simplification-versus-control decisions
- ops-platform-engineer synthesizes the final plan

Return:
- platform changes worth making
- safe savings
- telemetry and resilience gaps
- rollout order
```

## Payments Platform

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "payments-platform"` to review [billing or payment change].

Context:
- billing model: [model]
- provider constraints: [constraints]
- finance requirements: [requirements]

Return:
- recommended architecture
- operational concerns
- required controls before rollout
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "payments-platform"`.

Goal:
- Design or review [billing or payment change] so it is operationally and risk-wise credible.

Required context:
- Billing model: [model]
- Provider constraints: [constraints]
- Finance requirements: [requirements]

Optional context:
- reconciliation notes
- refund policy
- fraud controls
- compliance notes

Instructions:
- software-payments-architect reviews payment and billing architecture
- software-billing-ops-reviewer reviews finance operations and reconciliation impact
- software-security-reviewer reviews auth, data exposure, and abuse paths
- software-risk-reviewer reviews resilience and operational risk
- Run in hybrid mode
- Use debate for speed-versus-control tradeoffs
- software-payments-architect synthesizes the final recommendation

Return:
- recommended architecture
- finance operations concerns
- security and resilience risks
- required controls before rollout
```

## Mobile Product

### Short prompt

```text
Run the saved `expert-board` workflow with `board: "mobile-product"` to review [mobile feature or release].

Context:
- target platforms: [platforms]
- scope: [scope]
- release timeline: [timeline]

Return:
- architecture recommendation
- iOS and Android issues
- release confidence
```

### Full prompt

```text
Run the saved `expert-board` workflow with `board: "mobile-product"`.

Goal:
- Plan or review [mobile feature or release] across architecture, native implementation, and release readiness.

Required context:
- Platforms: [platforms]
- Scope: [scope]
- Release timeline: [timeline]

Optional context:
- screenshots
- build notes
- test evidence

Instructions:
- software-mobile-architect defines the cross-platform delivery approach
- software-ios-specialist reviews iOS-native implications
- software-android-specialist reviews Android-native implications
- qa-mobile-release-reviewer reviews test confidence and release risk
- Run in hybrid mode
- software-mobile-architect synthesizes the final recommendation

Return:
- architecture recommendation
- iOS issues
- Android issues
- release confidence and missing evidence
```

## Ad-hoc Specialists (No Named Team)

Use only when no named team's output contract fits, or when a named team would hide real lane ownership.

```text
Goal: <specific outcome> for <project-repo>.
Mode: debate
Required context: repo path, the measured signal (real numbers, screenshots, code paths), why now, constraints.
Specialists (4-6 named lanes, each with one reference file):
1. <lead A> — owns <lane>; do not duplicate <lead B>.
2. <lead B> — owns <lane>; challenge <lead A> if <condition>.
3. Causal analyst (when the evidence is analytics data) — separate causation from correlation; flag confounders.
4. Devil's advocate — steelman the opposite recommendation.
Debate triggers: <named disagreement>, <high-blast-radius decision>, a flagged confounder.
Synthesis: reasoning-tree audit, not voting; keep dissent; confidence per finding.
Output contract: deliverables with confidence and evidence, how to measure after ship, kill criteria, what would reverse the recommendation.
```

If the launch comes back generic: state `mode: debate` explicitly, name the installed agents to use, paste the real evidence, name every lane, and end with the output contract.

