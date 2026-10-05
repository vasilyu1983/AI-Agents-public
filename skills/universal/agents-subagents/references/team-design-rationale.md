---
description: Theory bindings for retained team recipes and migrated expert-board modes.
last_verified: 2026-09-16
status: stable
---

# Team Design Rationale

Design rationale for retained recipes in `agents/teams/` and bounded panels now
implemented as `expert-board` workflow modes. Each retained `team.yaml` carries
a `design_rationale:` pointer into this file; migrated entries preserve the
policy reasoning that should remain visible when their workflow modes change.

These `theory_edges` blocks previously lived inline in each `team.yaml`. Nothing in
`scripts/` or either runtime consumed them: they were documentation shipped as
configuration, accounting for roughly a quarter of every recipe. They are preserved here
verbatim so the reasoning behind each team's composition stays available to a human or
skill author, without being loaded on every install.

Read an entry when you are changing a team's membership, its expansion gate, or its
stopping rule, and you need to know which foundations skill justified the current shape.

`use_for` lists the conditions under which the linked foundations skill earns its context
cost for that team. `skip_for` lists the cases where loading it is waste.

## Table of Contents

- [Outside Perspective: Team-Boundary Thinking Applied to Agent Fleets](#outside-perspective-team-boundary-thinking-applied-to-agent-fleets)
- [ai-knowledge-bot-builder](#ai-knowledge-bot-builder)
- [expert-board: ai systems](#expert-board-ai-systems)
- [expert-board: data and analytics](#expert-board-data-and-analytics)
- [expert-board: data science](#expert-board-data-science)
- [dev-context-preparation](#dev-context-preparation)
- [dev-feature-delivery](#dev-feature-delivery)
- [dev-migration-map](#dev-migration-map)
- [docs-knowledge](#docs-knowledge)
- [expert-board: idea evaluation](#expert-board-idea-evaluation)
- [marketing-campaign](#marketing-campaign)
- [expert-board: marketing diagnostics](#expert-board-marketing-diagnostics)
- [expert-board: growth experiments](#expert-board-growth-experiments)
- [expert-board: incident response](#expert-board-incident-response)
- [expert-board: platform ops](#expert-board-platform-ops)
- [expert-board: product discovery](#expert-board-product-discovery)
- [product-surface](#product-surface)
- [expert-board: release readiness](#expert-board-release-readiness)
- [expert-board: architecture RFC](#expert-board-architecture-rfc)
- [software-code-review-board](#software-code-review-board)
- [expert-board: mobile product](#expert-board-mobile-product)
- [expert-board: payments platform](#expert-board-payments-platform)
- [expert-board: enterprise readiness](#expert-board-enterprise-readiness)
- [expert-board: founder blindspot](#expert-board-founder-blindspot)
- [expert-board: growth](#expert-board-growth)
- [expert-board: monetization](#expert-board-monetization)
- [expert-board: startup strategy](#expert-board-startup-strategy)

---

## Outside Perspective: Team-Boundary Thinking Applied to Agent Fleets

Matthew Skelton and Manuel Pais close *Team Topologies*, 2nd ed. (2025) with an Afterword
that extends their human team-boundary argument to groups of AI agents. This is their
stated 2025 perspective on an open question, not a validated design rule, and it is
recorded here as one outside view to weigh against the per-team rationale below — not as a
constraint on any recipe.

Their framing is trust by analogy: "A key consideration for people designing
AI-augmented organizations will therefore be how to trust groups of AI agents to execute
autonomously. Team Topologies points the way here. By considering how groups of humans are
trusted to execute autonomously, we can get a sense of how groups of AI agents can be
trusted: clear domain boundaries, constrained operating context (think small language
models, not large models), explainable decisions, clear audit trails and attestation data,
high-fidelity operational telemetry like event-based logging, and a sense of stewardship of
a given service or area, with clear responsibility for fixing mistakes or incidents."

Two items are worth separating:

- **Anti-handoff** — the claim carried over from their human-team work: "If the history of
  DevOps since 2008 has taught us anything, it's that it is vital to avoid handoffs from
  one group to another; the same will be true for groups of AI agents." Note the tense:
  "will be" is a projection, and they offer no agent-fleet evidence for it. It rhymes with
  the handoff costs this library already tracks in team composition, which is why it is
  worth holding, not why it is proven.
- **Small language models** — "constrained operating context (think small language models,
  not large models)" is a **prediction to pressure-test, not a settled finding**. The
  authors give no benchmark, cost model, or failure analysis behind it, and current routing
  practice in this library selects model tier per role rather than defaulting small. Treat
  it as a hypothesis worth measuring against real routing data before acting on it.

They also keep humans in the loop rather than out: "even if AI replaces significant human
efforts, the role of human teams will not disappear. If anything, the role of humans will
become even more important: defining the mission and success criteria of AI agent fleets
and overseeing their successful operation using tools (as yet) to be invented." The
stewardship point — an owner accountable for fixing an agent's mistakes — maps directly onto
the ownership boundaries the team recipes below already encode.

## ai-knowledge-bot-builder

Family: `ai`. Members: `ai-bot-builder-lead`, `ai-context-architect`, `ai-retrieval-architect`, `ai-agent-architect`.

Build AI bots with persistent knowledge bases — from architecture to production. Covers memory pattern selection, conversation design, retrieval engineering, and agent topology.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - staged information structure where architecture, retrieval, context, and bot-flow members observe
      different evidence
    - value-of-communication check before letting retrieval/context members expand peer discussion beyond
      their stage outputs
    skip_for:
    - single-framework bot builds where one implementer can own the answer
  foundations-grounding-communication:
    use_for:
    - acceptance checkpoint between knowledge-layer design and bot implementation
    - repair path when "memory", "knowledge base", or "grounding" means different things to stakeholders
    skip_for:
    - the stakeholder vocabulary is already defined and the bot handoff has no ambiguous memory or grounding
      terms
  foundations-behavioral-economics:
    use_for:
    - anchoring-reset and base-rate checks on familiar memory or bot frameworks
    skip_for:
    - deterministic integration work after vendor and pattern are fixed
  foundations-decision-theory:
    use_for:
    - EVPI and regret-minimization around vendor lock-in, P2/P4/P6/P7 pattern choice, and eval hold decisions
    skip_for:
    - reversible prompt copy changes
  foundations-information-theory:
    use_for:
    - retrieval, memory compression, knowledge compilation, and context-window tradeoffs
    skip_for:
    - UI-only bot shell work
  foundations-network-science:
    use_for:
    - knowledge graph, entity relationship, and citation-neighborhood design for bot memory
    skip_for:
    - flat FAQ bots with no relationship retrieval
```


## Expert Board: AI Systems

Board panel: `ai-agent-architect`, `ai-context-architect`, `ai-retrieval-architect`, `ai-evals-observer`.

AI systems design team for agent topology, context strategy, retrieval, and evals.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - agent-topology decisions where context, retrieval, and eval members have partitioned observations
      but one shared product payoff
    - communication-channel pricing before adding peer-agent scratchpads, shared memory, or critic loops
    skip_for:
    - isolated prompt edits with no multi-agent topology choice
  foundations-grounding-communication:
    use_for:
    - aligning definitions of "context", "retrieval quality", "eval pass", and "agent boundary" before
      synthesis
    - explicit repair when a member's proposal assumes context unavailable to another member
    skip_for:
    - the agent boundary, context contract, and evaluation vocabulary are already explicit and shared
      by every member
  foundations-behavioral-economics:
    use_for:
    - pre-mortem, inversion, and anchoring-reset when agent architecture locks in around the first plausible
      topology
    skip_for:
    - routine eval-threshold tuning
  foundations-decision-theory:
    use_for:
    - EVPI, regret-minimization, and MCDA for topology, retrieval, and eval tradeoffs
    skip_for:
    - one-provider configuration cleanup
  foundations-information-theory:
    use_for:
    - context budget, compression, retrieval signal quality, and eval-noise analysis
    skip_for:
    - tool naming or minor prompt edits
  foundations-distributed-systems:
    use_for:
    - agent topology, tool boundary, state consistency, idempotency, and retry design
    skip_for:
    - single-agent flows without shared state
  foundations-reliability-theory:
    use_for:
    - eval coverage, fallback policy, error budgets, and production failure-mode review
    skip_for:
    - exploratory prototypes with no release path
  foundations-game-theory:
    use_for:
    - attested delegation contracts when agent, tool, plugin, or MCP-server routing crosses a trust boundary
    - coalition formation when large agent topologies split into architecture, context, retrieval, eval,
      and production workstreams
    - anti-collusion checks when multiple agents can reinforce the same unsupported architecture claim
    skip_for:
    - single-owner AI design with static local agents and no dynamic delegation or adversarial incentive
      surface
```


## Expert Board: Data and Analytics

Board panel: `data-analytics-engineer`, `data-sql-optimizer`, `data-streaming-architect`, `data-instrumentation-analyst`.

Data and analytics team for metrics, SQL performance, event quality, and streaming design.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - partitioning observations across KPI model, SQL plan, streaming freshness, and instrumentation evidence
    - deciding whether analyst-to-optimizer communication pays off or whether late synthesis is cheaper
    skip_for:
    - one slow query with a clear owner and no metric-definition dispute
  foundations-grounding-communication:
    use_for:
    - resolving metric-name, event-name, and "source of truth" presuppositions before any schema or KPI
      recommendation
    - repair when dashboard symptoms conflict with warehouse or event evidence
    skip_for:
    - metric names, event names, owners, and source-of-truth tables are already defined and no evidence
      conflicts need repair
  foundations-causal-inference:
    use_for:
    - deciding whether metric movement is caused by a product or marketing change rather than seasonality,
      selection, or instrumentation drift
    skip_for:
    - descriptive KPI catalog cleanup
  foundations-decision-theory:
    use_for:
    - EVPI for adding data sources and regret-minimization for KPI/schema changes
    skip_for:
    - query formatting work
  foundations-information-theory:
    use_for:
    - event entropy, redundancy, missing signal, and compression of dashboard evidence
    skip_for:
    - source-of-truth decisions already backed by complete lineage
  foundations-queueing-theory:
    use_for:
    - streaming lag, warehouse backlog, query contention, and freshness/capacity tradeoffs
    skip_for:
    - static metric definitions with no pipeline latency issue
  foundations-theory-of-constraints:
    use_for:
    - identifying whether the analytics bottleneck is instrumentation, lineage, SQL cost, or synthesis
      capacity
    skip_for:
    - one-off dashboard copy edits
```


## Expert Board: Data Science

Board panel: `ai-data-scientist`, `ai-forecasting-scientist`, `ai-mlops-engineer`. Expansion candidates: `ai-quantum-data-scientist`, `data-analytics-engineer`, `data-governance-privacy-lead`.

Data science board for model evaluation, forecasting, and quantum-fit decisions. The quantum member is an expansion candidate rather than a panel seat: most modelling questions have no quantum arm, and a standing quantum memo would anchor every run toward "classical only".
```yaml
theory_edges:
  foundations-statistical-inference:
    use_for:
    - model comparison across folds, interval coverage, and whether a claimed gain exceeds noise
    skip_for:
    - framing questions where no evaluation evidence exists yet
  foundations-decision-theory:
    use_for:
    - tying the metric to the decision threshold and pricing a research pilot against its option value
    skip_for:
    - a model swap with a one-command rollback and no user-facing change
  foundations-mathematical-optimization:
    use_for:
    - the classical arm of a QAOA or scheduling question
    skip_for:
    - prediction problems with no optimization step
```


## dev-context-preparation

Family: `dev`. Members: `dev-portfolio-mapper`, `dev-repo-context-curator`, `dev-code-graph-builder`, `dev-context-packet-synthesizer`.

Build and refresh reusable context artifacts before engineering work.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - staged context-building where portfolio, repo, graph, and packet roles observe different slices
      and should not duplicate reads
    - keeping communication mostly stage-bound because peer chatter rarely improves deterministic context
      artifacts
    skip_for:
    - single-repo context refresh that one curator can complete
  foundations-grounding-communication:
    use_for:
    - handoff from graph/profile builders to packet synthesizer so generated artifacts are grounded before
      downstream agents consume them
    - repair when repo scope, target audience, or "canonical context" is underspecified
    skip_for:
    - repo scope, target audience, and canonical sources are already explicit and the packet is a mechanical
      extraction
  foundations-information-theory:
    use_for:
    - deciding what to compress into context packets and what to leave as cold evidence
    skip_for:
    - tiny repos where full context fits cheaply
  foundations-network-science:
    use_for:
    - repo dependency graphs, call graphs, ownership neighborhoods, and portfolio relationship maps
    skip_for:
    - flat single-package repos with no meaningful graph
  foundations-distributed-systems:
    use_for:
    - multi-repo context where ownership, service boundaries, consistency, and idempotency shape the context
      packet
    skip_for:
    - docs-only repositories
  foundations-theory-of-constraints:
    use_for:
    - deciding whether graph build, portfolio scan, or packet synthesis is the actual constraint
    skip_for:
    - already-generated context refreshes
```


## dev-feature-delivery

Family: `dev`. Members: `dev-feature-researcher`, `dev-feature-implementer`, `dev-feature-reviewer`.

Staged research, implementation, and review pipeline.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - staged research -> implementation -> review information structure where each member should observe
      only the evidence needed for its action
    - deciding whether to add a specialist only when their observation can change the ship/request_changes
      verdict
    skip_for:
    - trivial single-file fixes with clear tests
  foundations-grounding-communication:
    use_for:
    - acceptance-criteria paraphrase before implementation when the spec is ambiguous or bug reports conflict
    - repair channel from implementer back to researcher/reviewer when file ownership, expected behavior,
      or test oracle is unclear
    skip_for:
    - acceptance criteria, file ownership, expected behavior, and test oracle are already explicit
  foundations-decision-theory:
    use_for:
    - EVPI for adding security, performance, or QA reviewers and regret thresholds for ship/request_changes
    skip_for:
    - deterministic fixes with complete tests
  foundations-reliability-theory:
    use_for:
    - bug fixes touching failure modes, retries, fallbacks, or release-facing behavior
    skip_for:
    - style-only refactors
  foundations-theory-of-constraints:
    use_for:
    - diagnosing whether research, implementation, review, or missing context is blocking delivery
    skip_for:
    - single-pass implementation with no handoff
```


## dev-migration-map

Family: `dev`. Members: `dev-portfolio-mapper`, `dev-dependency-auditor`, `dev-migration-planner`, `ops-rollout-reviewer`.

Migration planning team for repo, framework, and platform transitions.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - nested information structure across portfolio map, dependency audit, migration plan, and rollout
      review
    - identifying non-classical signaling when one phase's migration note becomes another phase's observation
    skip_for:
    - dependency inventory with no sequencing or cutover decision
  foundations-grounding-communication:
    use_for:
    - grounding cutover terms, rollback boundaries, compatibility promises, and "done" criteria before
      plan synthesis
    - repair when old-system/new-system references or version constraints are ambiguous
    skip_for:
    - old-system/new-system terms, cutover target, compatibility rules, and rollback boundary are already
      explicit
  foundations-decision-theory:
    use_for:
    - regret-minimization and EVPI for phased migration, rollback, and hold-for-evidence choices
    skip_for:
    - inventory-only dependency scans
  foundations-distributed-systems:
    use_for:
    - service partitioning, compatibility, idempotency, consistency, and cutover protocols
    skip_for:
    - local library upgrades with no distributed boundary
  foundations-reliability-theory:
    use_for:
    - rollback evidence, failure modes, availability impact, and migration safety margins
    skip_for:
    - non-runtime documentation migrations
  foundations-cybernetics-vsm:
    use_for:
    - escalation channels and control loops during phased cutover
    skip_for:
    - one-shot migrations with no operational feedback loop
  foundations-theory-of-constraints:
    use_for:
    - finding whether dependency graph, rollout window, test coverage, or owner capacity is the bottleneck
    skip_for:
    - migration options already constrained to one feasible path
```


## docs-knowledge

Family: `docs`. Members: `docs-codebase-architect`, `docs-ai-prd-writer`, `docs-notes-retrieval-curator`, `docs-quality-auditor`.

Documentation and knowledge-ops team for codebase docs, PRDs, note retrieval, and doc quality.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - staged docs architecture, PRD, note-retrieval, and quality-audit roles where each observes a different
      knowledge surface
    - deciding whether broader note-vault scanning has enough value to justify the extra observation cost
    skip_for:
    - typo fixes or single-document edits
  foundations-grounding-communication:
    use_for:
    - audience-design checks where docs, PRDs, and retrieval artifacts will be consumed by downstream
      agents
    - repair when the user says "docs", "canonical", or "source of truth" without naming the exact audience
      and owner
    skip_for:
    - audience, owner, canonical source, and consumption path are already named for every artifact
  foundations-information-theory:
    use_for:
    - deciding what belongs in hot docs, retrieval indexes, summaries, or cold evidence
    skip_for:
    - single runbook correction
  foundations-network-science:
    use_for:
    - note-vault retrieval, doc graph, backlink, citation, and ownership-neighborhood work
    skip_for:
    - isolated prose edits
  foundations-decision-theory:
    use_for:
    - EVPI for broader vault scans and regret-minimization for canonical-doc ownership changes
    skip_for:
    - typo-level docs cleanup
```


## Expert Board: Idea Evaluation

Family: `evaluation`. Members: `product-strategist`, `startup-painpoint-scout`, `startup-competitive-analyst`, `software-solution-architect`, `ops-cost-optimizer`, `dev-feature-researcher`.

Universal first-evaluation workflow mode. Six role briefs (strategy, pain, competition, feasibility, economics, prior-art) assess whether an idea, product, or IT system is worth pursuing and how to select between options.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - six-lens evaluation where strategy, pain, competition, feasibility, economics, and prior-art members
      observe different option evidence
    - preserving independent first reads before MCDA so a preferred option does not collapse the information
      structure
    skip_for:
    - implementation after an option has already been selected
  foundations-grounding-communication:
    use_for:
    - grounding candidate options, decision constraints, and evaluation criteria before the first pass
    - repair when "adopt", "build", "pilot", or "reject" means different commitment levels to different
      members
    skip_for:
    - options, constraints, and decision commitment level are already formalized before the team reads
  foundations-behavioral-economics:
    use_for:
    - anchoring-reset, inversion, base-rate reset, and pre-mortem for early idea enthusiasm
    skip_for:
    - mature option with complete comparative evidence
  foundations-decision-theory:
    use_for:
    - MCDA, EVPI, real-options pilot logic, and regret-minimization across adopt/build/reject
    skip_for:
    - preference-only brainstorming
  foundations-causal-inference:
    use_for:
    - separating evidence that the problem causes the business outcome from correlation or anecdote
    skip_for:
    - first-pass market description without outcome claims
  foundations-information-theory:
    use_for:
    - assessing evidence quality, redundancy, and missing signal across candidate options
    skip_for:
    - already-validated options with complete source packets
```


## marketing-campaign

Family: `marketing`. Members: `startup-competitive-analyst`, `startup-review-miner`, `marketing-strategist`, `startup-product-marketing-strategist`, `marketing-email-automation-lead`, `marketing-paid-acquisition-strategist`, `marketing-creative-director`, `marketing-product-analytics-lead`.

Opt-in staged team for one campaign: research, then a positioning lock, then channel drafts in parallel, then a conversion and brand review.

**Decision step: lock the positioning before the parallel work.** The positioning and the message hierarchy are the one surface every channel draft shares. `foundations-team-theory` (primitive #8a, `references/primitives-overview.md`) says to centralize the parts of a task that touch a shared surface, such as a shared brand promise, and to decentralize the rest. It also names the failure: each local holder decides alone when consistency across decisions has its own payoff, such as brand. Primitive #8b gives the fix for a coupled shared interface: a single decision owner for that interface, so the effective coordination graph stays sparse. This recipe applies both. `marketing-strategist` alone owns the locked positioning. Each channel owner then sees the lock and its own channel only, so it coordinates with one member, not with every other channel. A channel owner who thinks the lock is wrong raises `reopen_positioning` with evidence and does not write around it.

**Review.** The two stage-4 reviewers drafted no channel asset, so their check is heterogeneous. `marketing-creative-director` checks brand and message fidelity against the lock. `marketing-product-analytics-lead` checks that each draft's call to action maps to a conversion event the campaign can measure. A finding that a draft contradicts the lock blocks `ready_for_launch` (the `debate.gate_rule` in the recipe).

**Write scope.** No member holds Edit or Write. `owned_files` assigns each channel path to one member; the parent thread writes the returned draft to that path only.

Adapted from the stage order of a third-party marketing-campaign command (MIT). No text or thresholds were copied; the regret thresholds follow this library's existing recipes.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - giving the shared positioning a single owner before channel owners work in parallel
    - limiting each channel owner's observation to the lock and its own channel
    skip_for:
    - a single-channel draft where the positioning is already given
  foundations-decision-theory:
    use_for:
    - EVPI for adding SEO, PR, or competitor-creative specialists
    - regret thresholds for ready_for_launch versus revise_channels or reopen_positioning
    skip_for:
    - a copy edit that changes no claim, offer, or call to action
```


## Expert Board: Marketing Diagnostics

Family: `marketing`. Members: `marketing-product-analytics-lead`, `startup-growth-specialist`, `marketing-seo-strategist`, `marketing-aeo-strategist`.

Debate-ready workflow mode for product metrics, AEO, SEO, and concrete growth improvements.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - analytics, growth, SEO, and AEO members observing different acquisition evidence before one improvement
      verdict
    - deciding whether cross-member communication clarifies the funnel bottleneck or just creates attribution
      noise
    skip_for:
    - single-channel audit with clear measurement
  foundations-grounding-communication:
    use_for:
    - grounding target funnel stage, metric definition, page/surface scope, and "improvement" before diagnostics
    - repair when SEO, AEO, and analytics evidence point to different user journeys
    skip_for:
    - funnel stage, metric definition, surface scope, and evidence source are already aligned
  foundations-behavioral-economics:
    use_for:
    - anchoring-reset, base-rate reset, and cognitive-bias checks in acquisition and funnel diagnosis
    skip_for:
    - purely technical crawl/indexing checks
  foundations-causal-inference:
    use_for:
    - deciding whether a channel, page, or positioning change caused metric movement
    skip_for:
    - descriptive traffic inventory
  foundations-information-theory:
    use_for:
    - SEO/AEO signal clarity, query intent, content redundancy, and answer-engine citation evidence
    skip_for:
    - direct paid-channel budget execution
  foundations-network-science:
    use_for:
    - backlink/citation graph, AEO entity neighborhood, competitor network, and internal-link diagnostics
    skip_for:
    - single landing-page copy review
  foundations-theory-of-constraints:
    use_for:
    - identifying whether instrumentation, search data, channel fit, or synthesis load is the growth diagnostic
      bottleneck
    skip_for:
    - already-known bottleneck with one obvious next test
```


## Expert Board: Growth Experiments

Board panel: `startup-growth-specialist`, `marketing-product-analytics-lead`, `marketing-paid-acquisition-strategist`, `marketing-strategist`.

Growth, analytics, and channel experiment team.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - growth, analytics, paid, and content members observing partitioned channel evidence under one experiment-payoff
      function
    - deciding whether to add monetization or AEO specialists only when their observation can flip the
      experiment choice
    skip_for:
    - already-selected experiment implementation
  foundations-grounding-communication:
    use_for:
    - grounding funnel stage, target metric, baseline, and experiment hypothesis before prioritization
    - repair when acquisition, activation, and monetization labels are being used inconsistently
    skip_for:
    - experiment brief already defines the funnel stage, baseline, target metric, and hypothesis without
      label drift
  foundations-behavioral-economics:
    use_for:
    - defaults, framing, scarcity, social proof, and cognitive-load checks in experiment design
    skip_for:
    - infrastructure-only tracking tasks
  foundations-causal-inference:
    use_for:
    - experiment design, confounding checks, power/measurement concerns, and impact attribution
    skip_for:
    - non-causal content calendar planning
  foundations-decision-theory:
    use_for:
    - bandit-style allocation, EVPI, and regret-minimization across competing experiments
    skip_for:
    - already-approved experiment implementation
  foundations-consumer-neuroscience:
    use_for:
    - attention, arousal, narrative transport, and reward anticipation in consumer acquisition experiments
    skip_for:
    - enterprise procurement experiments where buyer process dominates
```


## Expert Board: Incident Response

Family: `ops`. Members: `ops-incident-commander`, `qa-debugger`, `qa-observability-lead`, `qa-resilience-reviewer`.

Runtime incident workflow mode for triage, debugging, and remediation strategy.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - incident command where operations, debugging, observability, and resilience members observe partitioned
      signals under one containment payoff
    - deciding when centralized commander synthesis must override peer discussion because latency dominates
      information gain
    skip_for:
    - low-severity known-runbook incidents with one clear owner
  foundations-grounding-communication:
    use_for:
    - grounding symptoms, blast radius, rollback target, and customer impact before rollback/fix-forward
      choice
    - repair when logs, traces, and user reports imply different incident timelines
    skip_for:
    - the incident runbook already fixes symptoms, blast radius, customer impact, timeline, and rollback
      target
  foundations-control-theory:
    use_for:
    - feedback-loop, damping, rollback/fix-forward, and mitigation stability choices during incidents
    skip_for:
    - static postmortem writing after service recovery
  foundations-cybernetics-vsm:
    use_for:
    - algedonic escalation when data loss, payment block, or breach evidence bypasses normal routing
    skip_for:
    - low-severity incidents inside one team boundary
  foundations-queueing-theory:
    use_for:
    - backlog, saturation, latency, throughput, or retry-storm incidents
    skip_for:
    - pure correctness regressions with no load symptom
  foundations-reliability-theory:
    use_for:
    - availability impact, MTTR, redundancy, error-budget burn, and failure-mode assessment
    skip_for:
    - non-production investigation
  foundations-decision-theory:
    use_for:
    - regret-min rollback/fix-forward/hold decisions under uncertainty
    skip_for:
    - known runbook actions with no decision fork
```


## Expert Board: Platform Ops

Board panel: `ops-platform-engineer`, `ops-cost-optimizer`, `qa-observability-lead`, `qa-resilience-reviewer`.

Platform operations team for delivery systems, observability, resilience, and infrastructure cost control.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - platform, cost, observability, and resilience members holding different evidence about the same
      infrastructure decision
    - deciding whether more cross-member communication improves the decision or just replays the cost-vs-reliability
      debate
    skip_for:
    - narrow cost cleanup with no reliability or observability tradeoff
  foundations-grounding-communication:
    use_for:
    - grounding "SLO", "cost saving", "resilience", and "rollback" before synthesis
    - repair when billing evidence and operational evidence describe different scopes
    skip_for:
    - SLO, cost, resilience, and rollback terms are already scoped to the same systems and evidence window
  foundations-control-theory:
    use_for:
    - autoscaling, feedback control, rate limiting, rollout control, and stability tradeoffs
    skip_for:
    - one-time billing cleanup
  foundations-queueing-theory:
    use_for:
    - capacity, utilization, saturation, latency, and platform throughput choices
    skip_for:
    - static infra inventory
  foundations-reliability-theory:
    use_for:
    - SLOs, error budgets, redundancy, failure modes, and resilience investments
    skip_for:
    - cosmetic platform docs
  foundations-cybernetics-vsm:
    use_for:
    - escalation loops, algedonic signals, and operational control-channel design
    skip_for:
    - simple cost report generation
  foundations-distributed-systems:
    use_for:
    - consistency, partition, lease, idempotency, and service-boundary platform decisions
    skip_for:
    - single-host setup
```


## Expert Board: Product Discovery

Board panel: `product-manager`, `product-user-researcher`, `startup-competitive-analyst`, `marketing-product-analytics-lead`.

Product discovery team for roadmap questions, user evidence, competitive framing, and measurement.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - parallel product, research, competition, and analytics observations before a shared roadmap verdict
    - deciding whether to centralize synthesis when one evidence stream changes all roadmap options
    skip_for:
    - already-scoped feature execution
  foundations-grounding-communication:
    use_for:
    - grounding target user, problem statement, evidence quality, and success metric before member reads
    - repair when user evidence and business constraints refer to different segments or jobs
    skip_for:
    - target user, problem statement, evidence standard, and success metric are already aligned
  foundations-behavioral-economics:
    use_for:
    - roadmap anchoring, loss aversion, defaults, and feature-prioritization bias checks
    skip_for:
    - purely technical feasibility spikes
  foundations-causal-inference:
    use_for:
    - distinguishing causal user need or feature impact from correlation, cohort mix, or measurement drift
    skip_for:
    - qualitative exploration without impact claims
  foundations-decision-theory:
    use_for:
    - MCDA, EVPI, real options, and regret-minimization for build/defer/hold decisions
    skip_for:
    - backlog grooming with fixed priorities
  foundations-consumer-neuroscience:
    use_for:
    - consumer attention, narrative, habit, reward, or anxiety mechanisms in product discovery
    skip_for:
    - B2B workflow features where operational fit dominates
```


## product-surface

Family: `product`. Members: `software-frontend-lead`, `software-ux-designer`, `software-accessibility-reviewer`, `software-localisation-reviewer`.

Product surface team for frontend architecture, UX quality, accessibility, and localization readiness.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - frontend, UX, accessibility, and localization reviewers observing different UI failure surfaces
      before one surface verdict
    - deciding whether performance, iOS, or Android specialists can change the approval/request_changes
      outcome
    skip_for:
    - one-component visual tweak with no accessibility or localization surface
  foundations-grounding-communication:
    use_for:
    - grounding user flow, target locale/audience, accessibility bar, and implementation scope before
      review
    - repair when design references, screenshots, and code imply different intended behavior
    skip_for:
    - user flow, target audience or locale, accessibility bar, and implementation scope are already explicit
  foundations-behavioral-economics:
    use_for:
    - default choices, cognitive load, anchoring, and choice-architecture review in user-facing UI
    skip_for:
    - internal debug tooling
  foundations-consumer-neuroscience:
    use_for:
    - attention, arousal, salience, embodied cognition, and anxiety risk in consumer surfaces
    skip_for:
    - utilitarian admin surfaces where these effects are not design goals
  foundations-decision-theory:
    use_for:
    - EVPI for extra accessibility/localization/performance review and regret thresholds for approval
    skip_for:
    - trivial copy-only changes
```


## Expert Board: Release Readiness

Family: `qa`. Members: `qa-test-reviewer`, `docs-runbook-auditor`, `software-performance-reviewer`, `ops-rollback-planner`.

Workflow-backed readiness gate for releases, cutovers, and rollback planning.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - release-readiness team decisions where mobile, rollout, resilience, and test evidence are partitioned
      but the go/no-go payoff is shared
    - choosing centralized synthesis when one failure mode changes every member's verdict
    skip_for:
    - isolated test-suite triage with one owner
  foundations-grounding-communication:
    use_for:
    - grounding "ship", "hold", "rollback ready", and "parity" evidence before a release verdict
    - repair when a member reports missing evidence rather than silently treating it as pass
    skip_for:
    - release criteria, parity expectations, and required evidence are already explicit and complete
  foundations-decision-theory:
    use_for:
    - regret-min go/no-go, EVPI for extra tests, and hold-for-evidence release choices
    skip_for:
    - local test triage with no release decision
  foundations-reliability-theory:
    use_for:
    - release risk, failure modes, rollback readiness, and error-budget exposure
    skip_for:
    - documentation-only releases
  foundations-control-theory:
    use_for:
    - staged rollout, kill-switch, feature-flag, and feedback-monitoring design
    skip_for:
    - fully offline deliverables
  foundations-distributed-systems:
    use_for:
    - release surfaces crossing services, mobile/backend compatibility, queues, or consistency boundaries
    skip_for:
    - single binary with no external integration
  foundations-game-theory:
    use_for:
    - conformal social choice act/escalate gates when release consensus could still be wrong and rollback
      cost is high
    - anti-herding checks when readiness reviewers share the same test evidence and may converge on a
      false go verdict
    skip_for:
    - low-risk patch release with deterministic passing gates and trivial rollback
```


## Expert Board: Architecture RFC

Family: `software`. Members: `software-solution-architect`, `dev-api-designer`, `data-architect`, `software-risk-reviewer`.

Architecture decision workflow mode for RFCs, major refactors, and target-state design.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - hybrid information structure where API, data, risk, and architecture members hold partitioned evidence
      but share one architecture payoff
    - value-of-communication check before adding peer debate loops to already high-coupling RFCs
    skip_for:
    - narrow implementation choices that do not change system boundaries
  foundations-grounding-communication:
    use_for:
    - grounding "service boundary", "source of truth", "owner", and "rollback" terms before accepting
      the RFC frame
    - repair when one member's recommendation assumes constraints not present in the shared RFC brief
    skip_for:
    - RFC glossary, constraints, service boundaries, owners, and rollback terms are already explicit
  foundations-decision-theory:
    use_for:
    - MCDA, EVPI, regret-minimization, and real-options deferral for irreversible architecture choices
    skip_for:
    - local implementation details with one obvious option
  foundations-distributed-systems:
    use_for:
    - API, data, consistency, idempotency, service-boundary, and messaging topology decisions
    skip_for:
    - single-process UI architecture
  foundations-reliability-theory:
    use_for:
    - availability, redundancy, failure-mode, and rollback implications of target-state designs
    skip_for:
    - purely internal type/API cleanup
  foundations-information-theory:
    use_for:
    - data-contract signal quality, event payload shape, and observability/logging information sufficiency
    skip_for:
    - architecture decisions with no data or observability boundary
```


## software-code-review-board

Family: `software`. Members: `software-security-reviewer`, `software-performance-reviewer`, `qa-test-reviewer`.

Multi-perspective review team using canonical reviewer members.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - partitioning correctness, security, and performance observations so reviewers do not reread the
      whole diff by default
    - adding reviewers only when their observation can change the merge verdict
    skip_for:
    - one obvious bug fix review where a single reviewer has the full oracle
  foundations-grounding-communication:
    use_for:
    - grounding review scope, owned files, and severity definitions before synthesis
    - repair when a finding depends on unclear expected behavior or missing test oracle
    skip_for:
    - diff scope, owned files, severity definitions, expected behavior, and test oracle are already explicit
  foundations-decision-theory:
    use_for:
    - EVPI for adding specialist reviewers and regret-minimization for merge verdicts
    skip_for:
    - typo-level PRs
  foundations-reliability-theory:
    use_for:
    - release-facing bugs, failure modes, retries, recovery, and error-budget risk
    skip_for:
    - non-runtime docs reviews
  foundations-information-theory:
    use_for:
    - deciding whether diff, graph, logs, or tests provide enough signal for a finding
    skip_for:
    - self-evident syntactic defects
```


## Expert Board: Mobile Product

Board panel: `software-mobile-architect`, `software-ios-specialist`, `software-android-specialist`, `qa-mobile-release-reviewer`.

Mobile product team for cross-platform architecture, iOS and Android implementation, and release readiness.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - mobile architecture, iOS, Android, and release-review members observing platform-specific evidence
      under one release payoff
    - deciding when platform parity requires centralized synthesis versus independent platform recommendations
    skip_for:
    - single-platform native bug fix
  foundations-grounding-communication:
    use_for:
    - grounding "parity", "ship", "release ready", device matrix, and rollout constraints before synthesis
    - repair when iOS, Android, and release reviewers interpret feature scope differently
    skip_for:
    - platform scope, parity bar, device matrix, release criteria, and rollout constraints are already
      explicit
  foundations-decision-theory:
    use_for:
    - regret-minimization for ship/hold/parity decisions and EVPI for extra specialist review
    skip_for:
    - single-platform implementation with no release question
  foundations-reliability-theory:
    use_for:
    - crash risk, release readiness, rollback constraints, and store-release failure modes
    skip_for:
    - design-only mobile exploration
  foundations-consumer-neuroscience:
    use_for:
    - attention, anxiety, reward, and habit-loop risks in consumer mobile surfaces
    skip_for:
    - operational admin apps or infrastructure-only mobile changes
```


## Expert Board: Payments Platform

Board panel: `software-payments-architect`, `software-billing-ops-reviewer`, `software-security-reviewer`, `software-risk-reviewer`.

Payments and billing team for checkout, recurring revenue flows, finance operations, and risk control.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - payments, billing, security, and risk members observing different failure surfaces under one shared
      money-movement payoff
    - deciding whether extra communication channels are worth their latency when ledger or fraud decisions
      are tightly coupled
    skip_for:
    - low-risk copy or UI changes outside payment flow
  foundations-grounding-communication:
    use_for:
    - grounding "authorization", "capture", "refund", "ledger", "reconciliation", and "PCI scope" before
      synthesis
    - repair when finance, security, and product terms refer to different operational states
    skip_for:
    - payment state machine, ledger model, reconciliation owner, and PCI scope are already explicit
  foundations-decision-theory:
    use_for:
    - regret-minimization and MCDA for provider, billing-model, fraud-control, and ledger-schema choices
    skip_for:
    - copy-only checkout changes
  foundations-distributed-systems:
    use_for:
    - idempotency, retries, ledgers, webhook consistency, and settlement/reconciliation boundaries
    skip_for:
    - non-transactional UI work
  foundations-reliability-theory:
    use_for:
    - payment availability, double-charge risk, reconciliation failure modes, and recovery paths
    skip_for:
    - sandbox-only payment prototypes
  foundations-game-theory:
    use_for:
    - fraud, chargeback, dispute, and incentive conflicts among users, merchants, processors, and schemes
    - conformal act/escalate gates for money-movement or dispute decisions where wrong consensus is costly
    - attested delegation contracts before routing work to external payment, risk, ledger, or processor
      tools
    skip_for:
    - purely cooperative internal finance workflow with deterministic reconciliation checks
```


## Expert Board: Enterprise Readiness

Family: `startup`. Members: `startup-compliance-readiness-lead`, `software-security-reviewer`, `startup-growth-execution-operator`, `startup-operating-system-reviewer`.

Trust, compliance, and operating-readiness workflow mode for B2B SaaS.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - compliance, security, customer-success, and finance members observing different enterprise-readiness
      evidence under one shared deal-risk payoff
    - deciding whether adding privacy, appsec, or payments specialists changes the readiness verdict enough
      to justify delay
    skip_for:
    - simple questionnaire answer extraction with no operating commitment
  foundations-grounding-communication:
    use_for:
    - grounding customer commitments, control evidence, trust posture, and "ready" definitions before
      synthesis
    - repair when commercial promises and actual controls do not refer to the same scope
    skip_for:
    - customer commitments, control scope, diligence standard, and readiness definition are already explicit
  foundations-decision-theory:
    use_for:
    - regret-minimization and EVPI for readiness commitments, control evidence, and customer-scope decisions
    skip_for:
    - simple questionnaire drafting with settled controls
  foundations-reliability-theory:
    use_for:
    - operational readiness, support failure modes, control evidence, and trust-risk exposure
    skip_for:
    - purely commercial copy review
  foundations-game-theory:
    use_for:
    - enterprise negotiation, security-questionnaire concessions, buyer-vendor incentive conflicts, and
      attested delegation of diligence evidence
    - conformal act/escalate gates before committing to customer-facing control claims or remediation
      dates
    skip_for:
    - internal control inventory with no buyer commitment, external diligence response, or delegated evidence
      collection
  foundations-theory-of-constraints:
    use_for:
    - identifying whether compliance evidence, security gaps, support handoff, or finance ops blocks enterprise
      readiness
    skip_for:
    - already-scoped control remediation
```


## Expert Board: Founder Blindspot

Family: `startup`. Members: `startup-painpoint-scout`, `startup-review-miner`, `startup-trend-analyst`, `startup-competitive-analyst`, `product-strategist`.

Evidence-gated workflow mode for uncovering hidden growth opportunities, ignored objections, and weak signals founders tend to miss.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - parallel evidence lenses where pain, review, trend, competition, and product members observe different
      weak-signal streams
    - preserving decentralized first reads before synthesis so one founder frame does not collapse the
      information structure
    skip_for:
    - direct execution tasks after the blindspot has already been validated
  foundations-grounding-communication:
    use_for:
    - grounding target segment, current bottleneck, and evidence source definitions before interpreting
      weak signals
    - repair when a member hits a gating data gap or tool-access failure
    skip_for:
    - target segment, bottleneck, evidence source, and tool-access status are already explicit
  foundations-behavioral-economics:
    use_for:
    - inversion, anchoring-reset, base-rate reset, and founder blindspot bias checks
    skip_for:
    - execution after a validated wedge is already chosen
  foundations-causal-inference:
    use_for:
    - separating true switching triggers from noisy review correlations or trend anecdotes
    skip_for:
    - raw evidence collection before any impact claim
  foundations-consumer-neuroscience:
    use_for:
    - consumer anxiety, reward, narrative, social bonding, or habit signals hidden in reviews and weak
      signals
    skip_for:
    - B2B infrastructure categories
  foundations-network-science:
    use_for:
    - competitor clusters, review-source neighborhoods, community signals, and adjacent-user discovery
    skip_for:
    - single known customer segment with complete evidence
```


## Expert Board: Growth

Family: `startup`. Members: `product-strategist`, `startup-growth-specialist`, `marketing-product-analytics-lead`, `startup-product-marketing-strategist`, `startup-business-developer`.

Debate-ready founder review mode for checking whether growth is healthy and deciding what to improve next.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - deciding whether product, growth, analytics, positioning, and business lenses should run independently
      or share intermediate state
    - pricing cross-member communication when each extra round delays a concrete growth decision
    skip_for:
    - execution-level channel test design owned by one growth operator
  foundations-grounding-communication:
    use_for:
    - grounding "healthy growth", "serious users", "activation", and "retention" before comparing member
      recommendations
    - repair when metrics and qualitative claims point to different funnel stages
    skip_for:
    - funnel stage, activation and retention definitions, metric owner, and qualitative evidence scope
      are already aligned
  foundations-behavioral-economics:
    use_for:
    - founder optimism, vanity metrics, defaults, framing, and retention habit-loop checks
    skip_for:
    - pure finance/admin work
  foundations-causal-inference:
    use_for:
    - separating real growth drivers from seasonality, cohort mix, channel noise, or tracking drift
    skip_for:
    - qualitative-only strategy discussion
  foundations-consumer-neuroscience:
    use_for:
    - consumer engagement, shareability, anxiety, reward, and narrative mechanics in growth loops
    skip_for:
    - enterprise sales-led growth without consumer behavior surface
  foundations-decision-theory:
    use_for:
    - EVPI, bandit dispatch, MCDA, and regret-minimization for next-growth-bet selection
    skip_for:
    - already-committed experiment execution
  foundations-theory-of-constraints:
    use_for:
    - deciding whether growth is constrained by activation, retention, channel, positioning, pricing,
      or evidence quality
    skip_for:
    - one-channel campaign tuning
```


## Expert Board: Monetization

Family: `startup`. Members: `startup-pricing-advisor`, `marketing-product-analytics-lead`, `marketing-strategist`, `startup-operating-system-reviewer`, `startup-business-developer`.

Evidence-gated workflow mode for pricing, packaging, upgrade logic, and revenue mechanics.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - partitioning pricing, analytics, marketing, finance, and business observations before a shared monetization
      verdict
    - deciding whether competitor-pricing or billing-infra specialists have enough expected value to join
    skip_for:
    - one-off copy edits to pricing-page messaging
  foundations-grounding-communication:
    use_for:
    - grounding "value", "conversion", "churn", "plan restructure", and "paywall change" so members compare
      the same monetization object
    - repair when price/value disagreements are really audience-design or terminology failures
    skip_for:
    - price object, plan object, paywall object, audience segment, and value metric are already aligned
  foundations-behavioral-economics:
    use_for:
    - anchoring, decoys, loss aversion, framing, and default-plan effects in pricing/packaging
    skip_for:
    - back-office billing cleanup
  foundations-causal-inference:
    use_for:
    - attributing conversion, churn, or ARPU movement to price/paywall changes rather than cohort mix
    skip_for:
    - competitor-price inventory only
  foundations-consumer-neuroscience:
    use_for:
    - consumer perceived value, reward anticipation, anxiety, and paywall-emotion effects
    skip_for:
    - enterprise contract pricing
  foundations-decision-theory:
    use_for:
    - regret-minimization, EVPI, and real-options pilot design for price and paywall changes
    skip_for:
    - pricing copy edits with no plan change
  foundations-game-theory:
    use_for:
    - strategic competitor response, negotiation, discounts, and multi-sided pricing incentives
    skip_for:
    - fixed one-sided subscription pricing with no strategic interaction
```


## Expert Board: Startup Strategy

Board panel: `marketing-strategist`, `startup-business-developer`, `startup-growth-specialist`, `product-strategist`, `software-ux-designer`.

Cross-functional startup analysis team built from shared members.
```yaml
theory_edges:
  foundations-team-theory:
    use_for:
    - shared-payoff startup decisions where product, growth, business, marketing, and UX members observe
      different market signals
    - deciding when peer communication improves synthesis versus just amplifies founder framing
    skip_for:
    - narrow execution tasks with one responsible function
  foundations-grounding-communication:
    use_for:
    - grounding target customer, positioning claim, and "what to improve next" before debate starts
    - repair when members infer different startup stage, market category, or success metric
    skip_for:
    - startup stage, target customer, market category, positioning claim, and success metric are already
      explicit
  foundations-behavioral-economics:
    use_for:
    - founder anchoring, framing, base-rate reset, inversion, and strategic overconfidence checks
    skip_for:
    - narrow operational execution
  foundations-causal-inference:
    use_for:
    - judging whether observed traction is caused by product, channel, market timing, or founder-led sales
    skip_for:
    - pre-traction idea brainstorming
  foundations-decision-theory:
    use_for:
    - MCDA, EVPI, real options, and regret-minimization for strategic next bets
    skip_for:
    - tasks with a single mandated path
  foundations-game-theory:
    use_for:
    - competitor response, partnership, negotiation, pricing, or platform-power questions
    skip_for:
    - internal sequencing decisions with no strategic counterparty
  foundations-theory-of-constraints:
    use_for:
    - identifying whether product, distribution, monetization, positioning, or capacity is the actual
      bottleneck
    skip_for:
    - already-diagnosed bottlenecks with execution plan
```
