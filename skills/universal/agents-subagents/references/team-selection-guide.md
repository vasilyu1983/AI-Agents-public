---
description: Universal decision map for retained teams, saved workflow modes, debate rules, and custom compositions.
last_verified: 2026-09-02
status: stable
---

# Team Selection Guide

Universal decision map, debate rules, and custom team/agent recipes for any repo or product.

Use this file first whenever you want to run a retained team or saved workflow mode. It maps concrete questions to the smallest correct execution surface, tells you whether debate is worth the cost, and gives recipes for composing custom teams or agents when nothing in the shared catalog fits.

## Table of Contents

- [A. Decision Map](#a-decision-map)
- [B. Selection Rule (Smallest Mode First)](#b-selection-rule-smallest-mode-first)
- [B1. Candidate Pipeline Discipline](#b1-candidate-pipeline-discipline)
- [C. Debate Or Not?](#c-debate-or-not)
- [D. Universal Intake Pack](#d-universal-intake-pack)
- [E. Custom Team Recipe](#e-custom-team-recipe)
- [F. Custom Agent Recipe](#f-custom-agent-recipe)
- [G. Analytics Tool Neutrality](#g-analytics-tool-neutrality)
- [H. Orchestrator Master Criteria — When & What to Use](#h-orchestrator-master-criteria--when--what-to-use)
- [Niche Validation](#niche-validation)

## A. Decision Map

When the real question is in the first column, start with the primary team. Use the second-opinion team only when the first team ends with contradictions, low confidence, or a flagged data gap.

| Question you want answered | Primary team | Second-opinion team | Debate? |
|---|---|---|---|
| Is my monetization OK? | `expert-board` (`monetization`) | `expert-board` (`growth`) | yes |
| Am I competitive in my space? | `expert-board` (`product-discovery`) | `expert-board` (`startup-strategy`) | yes |
| Is my SEO/AEO good? | `expert-board` (`marketing-diagnostics`) | — | yes |
| Are my product analytics trustworthy? (PostHog, GA, Mixpanel, any) | `expert-board` (`marketing-diagnostics`) | `expert-board` (`data-analytics`) | on data disputes |
| How do I run A/B tests properly? | `expert-board` (`growth-experiments`) | — | on prioritization |
| What should I change to boost growth — and why? | `expert-board` (`growth`) | `expert-board` (`startup-strategy`) | yes |
| I built the product, but how do I penetrate the market and get serious users? | `expert-board` (`growth`, `market-penetration`) via the [market-penetration contract](workflow-contracts.md#market-penetration-review) | `expert-board` (`founder-blindspot`) | yes |
| Am I missing something non-obvious? | `expert-board` (`founder-blindspot`) | — | yes |
| Should I enter this new niche / build this new app? | `expert-board` (`founder-blindspot`, new-niche scenario — see [Niche Validation](#niche-validation)) | `expert-board` (`startup-strategy`) | yes |
| What are the recurring pain points in this category? | `expert-board` (`founder-blindspot`; `painpoint-scan-report.md` artifact required from `research-painpoint-scanner`) | — | no |
| Is there real switching-trigger evidence in this market? | `expert-board` (`founder-blindspot`; `switching-trigger-analysis.md` artifact required from `research-review-mining`) | — | no |
| Is my product doing the right thing? | `expert-board` (`product-discovery`) | — | yes |
| Am I enterprise-ready for this customer? | `expert-board` (`enterprise-readiness`) | — | no |
| Outage, regression, or incident | `expert-board` (`incident`) | — | on rollback vs fix-forward |
| Architecture / RFC decision | `expert-board` (`architecture-rfc`) | — | yes |
| Code review on a PR or diff | `software-code-review-board` | — | on disagreements |
| Release gating | `expert-board` (`release-readiness`) | — | on go/no-go with conflicting signals |
| Feature delivery (research → implement → review) | `dev-feature-delivery` | — | no |
| Mobile app surface / release | `expert-board` (`mobile-product`) | — | no |
| Data and analytics pipeline design | `expert-board` (`data-analytics`) | — | no |
| Is this model or forecast good enough to ship? | `expert-board` (`data-science`) | `expert-board` (`ai-systems`) for LLM-based models | on baseline vs complex model |
| Should we use quantum computing (QML, QAOA) for this? | `ai-quantum-data-scientist` alone; `expert-board` (`data-science`) when a classical model is also in play | — | on pilot vs classical baseline |
| Migration or cutover planning | `dev-migration-map` | — | on sequencing/cutover tradeoffs |
| Context preparation before engineering work | `dev-context-preparation` | — | no |
| AI system design (agents, RAG, evals) | `expert-board` (`ai-systems`) | — | yes |
| Build a bot with persistent memory / knowledge base | `ai-knowledge-bot-builder` | `expert-board` (`ai-systems`) | yes (on memory pattern + framework choice) |
| How many users/revenue in 6 months? | `expert-board` (`growth`, Delphi method) | — | no (estimation, not debate) |
| What assumptions are we not testing? | `expert-board` (`founder-blindspot`, Socratic method) | — | no (questions, not positions) |
| Can we find middle ground on a tradeoff? | relevant team (Negotiation mode) | — | no (compromise, not winner) |
| Is our code review catching real issues? | `software-code-review-board` (Purple Team mode) | — | continuous (find→fix→verify) |

Rule: if two modes seem to fit, pick the one whose output contract matches your question most directly. The monetization mode will talk about pricing even if you asked about growth; the growth mode will talk about monetization even if you asked about SEO. Start from the output you actually need.

### Mode Before Method

Before picking a debate method, check whether debate is the right mode at all. The orchestrator's [Mode Selection Guide](../../../../agents/templates/debate-orchestrator.md) routes:
- **Estimation questions** → Delphi (anonymous iterative convergence, not adversarial debate)
- **Untested assumptions** → Socratic Questioning (probing questions, not positions)
- **Continuous tradeoffs** → Negotiation Protocol with ZOPA/BATNA (compromise, not winner)
- **Claim verification** → Courtroom / PROClaim (progressive evidence, role-switching)
- **Continuous security** → Purple Team (find→fix→verify cycle)
- **Binary decisions** → standard debate methods (Six Hats, Pre-Mortem, Devil's Advocate, etc.)

Using the wrong mode is the most common mistake: running adversarial debate for an estimation question produces arguments instead of numbers. Check the mode first, then pick the method.

### The Seven Core Decisions (Expanded)

These are the recurring reviews that should run on a schedule. Each one has a clear team, a clear signal of health, and a clear next action.

#### 1. "Is my monetization OK?"

- **Workflow mode**: `expert-board` with `monetization`
- **Members**: `startup-pricing-advisor`, `marketing-product-analytics-lead`, `marketing-strategist`, `startup-operating-system-reviewer`, `startup-business-developer`
- **Synthesis owner**: `startup-pricing-advisor`
- **Signals of health**: stable or improving free→paid conversion, LTV:CAC ≥ 3, low involuntary churn, pricing objections declining, expansion revenue present
- **Red flags**: users reach the product but revenue lags, upgrade paths are unclear, pricing objections increasing, packaging decisions being made without cohort data
- **Debate triggers**: price-vs-value-communication disagreements, packaging-vs-activation disagreements, experiments with meaningful churn or cash-flow downside
- **Output contract**: bottleneck, top 3 monetization opportunities, smallest safe experiment, expected impact, confidence, data gap, recommended execution team

#### 2. "Am I competitive in my space?"

- **Primary board**: `expert-board` (`product-discovery`)
- **Key member**: `startup-competitive-analyst`
- **Second opinion**: `expert-board` (`startup-strategy`) — broader positioning lens
- **Signals of health**: clear wedge, differentiated messaging, switching triggers understood, win/loss reasons documented, defensible moat visible
- **Red flags**: losing deals to a specific competitor repeatedly, positioning is copy-paste of leader, no documented reason to choose you, founder can't name top 3 alternatives buyers consider
- **Debate triggers**: major roadmap or ICP tradeoffs, conflicting user signal vs business pressure, "build vs differentiate" choices
- **Output contract**: competitive position (strong/neutral/weak), top 3 competitive threats, positioning recommendations, user-evidence gaps

#### 3. "Is my SEO/AEO good?"

- **Workflow mode**: `expert-board` with `marketing-diagnostics`
- **Members**: `marketing-product-analytics-lead`, `startup-growth-specialist`, `marketing-seo-strategist`, `marketing-aeo-strategist`
- **Synthesis owner**: `startup-growth-specialist`
- **Signals of health**: organic traffic growth, keyword coverage for core intent, pages appearing in AI answers with correct citations, entity clarity for your brand
- **Red flags**: flat or declining organic, zero AI-answer visibility, competitors cited instead of you, technical SEO issues (crawl errors, thin pages)
- **Debate triggers**: SEO-vs-AEO prioritization, acquisition-vs-activation tradeoffs, conflicting metric interpretations
- **Output contract**: discoverability read, SEO priority list, AEO priority list, smallest next experiment

#### 4. "Are my product analytics trustworthy?"

- **Light check mode**: `expert-board` with `marketing-diagnostics` (is the funnel read correct?)
- **Deep check board**: `expert-board` (`data-analytics`) — is the instrumentation correct?
- **Key members**: `marketing-product-analytics-lead` (funnel trust) + `data-instrumentation-analyst` (event quality)
- **Signals of health**: event schema versioned, activation event defined and instrumented, funnels reproducible across tools, no silent drops between client and warehouse
- **Red flags**: numbers differ between dashboards, no canonical event dictionary, events fire on the wrong trigger, activation metric keeps being redefined
- **Debate triggers**: conflicting interpretations of product metrics between marketing and data
- **Output contract**: measurement trust score, instrumentation gaps, events to add/fix, tracking plan proposal

This decision is analytics-tool-neutral. Pass your tool as context (see section G).

#### 5. "How do I run A/B tests properly?"

- **Board**: `expert-board` (`growth-experiments`)
- **Members**: `startup-growth-specialist`, `marketing-product-analytics-lead`, `marketing-paid-acquisition-strategist`, `marketing-strategist`
- **Synthesis owner**: `startup-growth-specialist`
- **Signals of health**: experiments have pre-registered hypotheses, sample size calculated upfront, one variable changed per test, stopping rules defined, losing variants actually stopped
- **Red flags**: peeking at results before sample size, running multiple experiments on overlapping audiences, calling wins at 80% confidence, no holdout groups
- **Debate triggers**: channel prioritization, activation vs acquisition tradeoffs, which experiment to run next
- **Output contract**: experiment design critique, minimum detectable effect, expected runtime, sample size, decision criteria

#### 6. "I built the product. How do I penetrate the market?"

- **Workflow mode**: `expert-board` with `growth` / `market-penetration`, using the [market-penetration workflow contract](workflow-contracts.md#market-penetration-review)
- **Members**: `product-strategist`, `startup-growth-specialist`, `marketing-product-analytics-lead`, `startup-product-marketing-strategist`, `startup-business-developer`
- **Synthesis owner**: `product-strategist`
- **Signals of health**: a narrow ICP, clear first-value behavior, one primary channel producing activated users, first proof assets, and a 30-day learning loop
- **Red flags**: more feature work used as a substitute for distribution, broad audience claims, channel spraying, paid traffic before activation quality is measurable, App Store or landing-page tests judged only by installs/signups
- **Debate triggers**: product-vs-positioning-vs-channel disagreements, whether the wedge is too broad, whether paid acquisition is premature, whether the current promise has enough proof
- **Output contract**: growth stage, first market wedge, positioning, primary channel, activation-quality metric, 30-day plan, instrumentation gaps, strongest dissent, recommended execution team
- **Template**: use [agents/templates/growth/market-entry-wedge.md](../../../../agents/templates/growth/market-entry-wedge.md); if the channel choice is still ambiguous, run [agents/templates/growth/channel-experiment-scorecard.md](../../../../agents/templates/growth/channel-experiment-scorecard.md)

#### 7. "What should I change to boost growth, and why?"

- **Workflow mode**: `expert-board` with `growth`
- **Members**: `product-strategist`, `startup-growth-specialist`, `marketing-product-analytics-lead`, `startup-product-marketing-strategist`, `startup-business-developer`
- **Synthesis owner**: `product-strategist`
- **Signals of health**: growth is loop-based (not paid-only), at least one channel compounding, retention stable or improving, monetization not blocking growth
- **Red flags**: growth is channel-dependent on one paid source, retention declining while acquisition grows, "vanity growth" (activity up, revenue flat), no clear next bet
- **Debate triggers**: healthy-vs-vanity growth disagreements, product-vs-distribution-vs-monetization prioritization, founder sequencing decisions
- **Output contract**: growth read (healthy/fragile/misleading), strongest bottleneck, 3 highest-leverage opportunities, smallest next experiment, strongest dissent, recommended execution team
- **Template**: use [agents/templates/growth/activation-retention-diagnosis.md](../../../../agents/templates/growth/activation-retention-diagnosis.md) when the bottleneck may be activation or retention; use [agents/templates/growth/pricing-paywall-experiment.md](../../../../agents/templates/growth/pricing-paywall-experiment.md) when monetization is the likely bottleneck

## B. Selection Rule (Smallest Mode First)

Always pick the smallest mode that cleanly fits the task. Escalate only when the smaller mode is clearly insufficient.

1. **Installed global agent** — one specialist already solves it. Check `~/.claude/agents/` and `~/.codex/agents/` first.
2. **Shared member** — one canonical reusable specialist from `agents/` without a full team.
3. **Saved workflow mode or global team** — use `expert-board` for bounded generic reviews; install a retained 3-5-specialist recipe via `scripts/deploy-preset.sh` for repeatable delivery work or named-agent configuration.
4. **Debate overlay** — the selected workflow mode or team argues before synthesis. Worth the extra turns only when disagreement is the point.
5. **Custom team** — compose on the fly from existing members (see section E). Only when no installed team covers the shape.
6. **Custom agent** — only when no existing member covers the role (see section F).

Do not skip levels. Creating a custom team when a saved mode or retained team would work is the most common failure mode and produces inconsistent results across sessions.

## B1. Candidate Pipeline Discipline

Use this when two or more agents, members, teams, or debate modes could fit. It keeps selection traceable and prevents a broad team from winning just because it was named first.

```text
team-launch request
  -> hydrate context: goal, output contract, constraints, repo/runtime, risk
  -> source candidates: built-ins, global agents, shared members, shared teams, debate overlays
  -> hydrate candidates: owner, skill links, tool scope, evidence needs, expected artifact
  -> filter ineligible: wrong owner, missing tool, unsafe permission, no output match
  -> score independently: output fit, cost, risk, evidence readiness, reuse value
  -> select smallest correct mode
  -> post-selection validation: context pack, ownership, synthesis owner, cleanup expectation
  -> side effects: eval case, catalog note, learning proposal
```

Selection rules:

- Score each candidate mode against the user's required output before comparing modes.
- A candidate can be removed only by a named filter reason; enrichment alone must not drop it.
- Prefer the smallest mode that satisfies the output contract, not the most impressive team.
- Run post-selection validation before launch: every chosen agent/team needs a self-contained brief, owned files or read-only scope, synthesis owner, evidence requirement, and cleanup expectation.
- Keep side effects separate. Updating team catalogs, evals, or learnings happens after the launch decision and should not change the chosen mode silently.

Known traps:

- choosing debate because several specialists exist, even though the question is execution
- selecting a saved mode or global team before checking whether one installed specialist already owns the artifact
- comparing teams to each other before scoring each team against the actual output contract
- letting an agent with broad skills override a narrower specialist on the same topic
- launching without post-selection validation of context, permissions, and cleanup scope

## C. Debate Or Not?

Debate doubles or triples the cost of a review. Use it deliberately.

### Use Debate When

- The decision is reversible-expensive or irreversible: pricing changes, pivots, architecture splits, schema migrations, re-platforming
- Signals contradict each other: growth looks healthy on one metric and weak on another
- Founder intuition is strong but unvalidated by evidence
- Two different lenses will likely reach different answers (growth vs monetization, product vs distribution, security vs velocity)
- The output is a recommendation you will act on, not just a status check

### Skip Debate When

- The task is pure execution with a clear spec and no meaningful cross-lens disagreement
- One specialist cleanly owns the deliverable
- The team's manifest has `debate: enabled: false`. The three teams with debate fully disabled are: `dev-context-preparation`, `dev-feature-delivery`, and `docs-knowledge`. Every `expert-board` board is debate-on-trigger.
- You are running a recurring status check, not a decision
- You are budget-constrained and the decision is reversible-cheap

### Debate-On-Trigger (The Middle Ground)

Retained team recipes and `expert-board` modes use this pattern: debate is enabled with named triggers, but fires only when a listed trigger condition is hit. Examples:

- `expert-board` (`incident`) — debate fires on "rollback vs fix-forward" and "containment and remediation tradeoffs", not during active triage
- `dev-migration-map` — debate fires on "sequencing and cutover choices" and "backward-compatibility tradeoffs", not during dependency mapping
- `expert-board` (`release-readiness`) — debate fires on "go/no-go decisions" and "rollout window or rollback strategy", not during test review
- `expert-board` (`ops-platform`) — debate fires on "cost vs reliability" and "platform simplification vs control", not during telemetry reviews

This is the [discipline GitHub recommends](https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/): debate earns its cost only when genuine disagreement is likely. When composing a new team, prefer debate-on-trigger over default-on debate, and list at least 2 explicit trigger conditions.

### Debate Discipline

When debate runs:
- Each participant reads independently first (no cross-talk in round 1)
- Round 2: identify points of disagreement, not points of agreement
- Synthesizer writes a single memo with the disagreement explicit, not smoothed over
- Record the dissent. "Strongest opposing view" is a required output field.

## D. Universal Intake Pack

Every review starts by filling this, regardless of team. This is the evidence floor. If fewer than 5 fields are available, the first team's job is to say so and stop the review.

```text
Repo / product name: [NAME]
One-line description: [WHAT IT IS]
Target customer / ICP: [WHO IT IS FOR]
Current revenue model: [HOW IT MAKES MONEY]
Current bottleneck: [ONE SENTENCE]

Funnel snapshot:
- Acquisition: [TRAFFIC / LEADS / SIGNUPS]
- Activation: [KEY ACTION RATE]
- Retention: [D7 / D30 / CHURN]
- Monetization: [CONVERSION TO PAID / ARPU / LTV]

Top 3 complaints, objections, or friction signals:
1. [CLAIM]
2. [CLAIM]
3. [CLAIM]

Last 3 meaningful experiments or launches:
1. [WHAT / RESULT]
2. [WHAT / RESULT]
3. [WHAT / RESULT]

Analytics surface in use: [PostHog / GA4 / Mixpanel / Amplitude / custom]
```

Rule: teams should refuse to browse the open web for evidence that should have come from the intake pack. Your own product data beats public speculation.

See [universal-team-playbook.md](universal-team-playbook.md) for the full evidence-gated workflow and branch rules.

## E. Custom Team Recipe

When the decision map has no clear match, compose an ad-hoc team from existing members. Do not create new members or checked-in team recipes unless the composition will repeat ≥3 times.

### Steps

1. **Name the decision in one sentence.** Write the output contract — what the team must return — before picking members. If you can't write the output contract, the question is not yet clear enough to run a team on.

2. **Pick 3-5 existing canonical members.** Browse `agents/claude/` (Claude) or `agents/codex/` (Codex). Always reuse; do not create new roles for a one-off review. Common combinations the installed teams do not cover:
   - Pricing + legal + compliance: `startup-pricing-advisor` + `startup-compliance-readiness-lead` + `startup-business-developer`
   - Content strategy + SEO + brand: `marketing-strategist` + `marketing-seo-strategist` + `startup-competitive-analyst`
   - Mobile + performance + accessibility: `software-ios-specialist` or `software-android-specialist` + `software-performance-reviewer` + `software-accessibility-reviewer`

   **Single-voice rule**: when a specialist and a generalist overlap on a skill, the specialist owns the authoritative voice. Examples:
   - In any team that includes `marketing-seo-strategist` or `marketing-aeo-strategist`, `marketing-strategist` contributes only positioning, message architecture, and cross-cutting strategy — not SEO/AEO opinions.
   - In any team that includes `marketing-product-analytics-lead`, `data-instrumentation-analyst` contributes instrumentation and event-quality only — not funnel interpretation.

   This is enforced in Claude member frontmatter (`skills:` lists). Codex installs can derive the same skill mapping through `[[skills.config]]` when those skill paths are available, but the inline brief remains the fallback and the single-voice rule still matters most in team runs.

3. **Decide synthesis owner.** One member writes the final memo. Usually the member closest to the output format (`product-strategist` for product memos, `startup-pricing-advisor` for pricing memos, `software-solution-architect` for architecture memos).

4. **Decide concurrency mode.**
   - `parallel` for independent lenses (each member reads independently, then synthesis)
   - `hybrid` when one member produces a data artifact that the others interpret (e.g., analytics lead → others)

5. **Decide debate.** Enable only if disagreement is the value. Define 2-4 explicit perspectives (e.g., pricing, analytics, marketing) and named trigger conditions.

6. **Write an ad-hoc team recipe in memory.** Use the shape from any file in `agents/teams/*/team.yaml`. No need to check in a new file. Example in-memory shape:
   ```yaml
   name: ad-hoc-<purpose>
   members: [member-1, member-2, member-3]
   required_context: [...]
   concurrency_mode: parallel
   synthesis_owner: member-1
   debate:
     enabled: true
     triggers: [trigger-1, trigger-2]
     perspectives: [lens-1, lens-2]
   ```

7. **Launch via template.** Use the short-form or full-form templates in [team-prompt-patterns.md](team-prompt-patterns.md).

8. **Promote if it repeats.** If the same composition runs three times, convert it to a real `agents/teams/<name>/team.yaml` and add a row to [team-coverage.md](team-coverage.md).

## F. Custom Agent Recipe

Only when no existing member covers the role. This should be rare.

### Steps

1. **Inventory before creating.** Check in this order:
   - `~/.claude/agents/` (installed global Claude agents)
   - `.claude/agents/` (repo-local Claude agents)
   - `~/.codex/agents/` (installed global Codex agents)
   - `.codex/agents/` (repo-local Codex agents)
   - `agents/claude/` and `agents/codex/` (canonical shared members)
   A similar role usually exists. Stronger `description` wording on an existing agent often solves the gap without a new file.

2. **Start from a canonical member or a template.**
   - For **reviewer** and **implementer** roles, copy a canonical member from `agents/claude/` or `agents/codex/` (e.g. `dev-feature-reviewer`, `dev-feature-implementer`, `software-security-reviewer`, `qa-test-reviewer`) — fully wired with `skills:` and family-prefix naming.
   - For **role-only shapes** that are instantiated per task, use `agents/templates/`:
     - `browser-verifier.md` for scoped MCP browser roles
     - `perspective-agent.md` for debate participants
     - `debate-orchestrator.md` / `debate-synthesizer.md` for debate infrastructure

3. **Apply the Design Checklist from `SKILL.md`:**
   - One clear responsibility
   - Concrete delegation triggers in the description
   - Minimal tool access
   - Scoped MCP only if needed
   - Explicit output contract
   - Handoff template with owned files and verification steps

4. **Link the right skill.** Add the same skill ids to each runtime member: Claude frontmatter `skills:` and the Codex footer parsed by `deploy-preset.sh`. Reuse ids from the shared-skills catalog under `skills/`. Do not inline skill content into the agent file.

5. **Decide scope before writing.**
   - **Global** (`~/.claude/agents/` or `~/.codex/agents/`): reusable across repos, stable behavior
   - **Repo-local** (`.claude/agents/` or `.codex/agents/`): overrides global, repo-specific conventions

6. **If it should appear in team recipes**, also drop canonical copies under `agents/claude/<name>.md` + `agents/codex/<name>.toml` so recipes can reference the member id.

See [agent-patterns.md](agent-patterns.md) for reusable subagent patterns and anti-patterns, and [agent-tools.md](agent-tools.md) for tool/permission/MCP guidance.

## G. Analytics Tool Neutrality

The two analytics-facing members — `marketing-product-analytics-lead` and `data-instrumentation-analyst` — are not tied to any specific product-analytics tool. They work equally well against:

- PostHog
- Google Analytics 4
- Mixpanel
- Amplitude
- Segment
- Heap
- Snowplow
- Custom warehouse stacks (Snowflake/BigQuery/Redshift + dbt)

### Rule

Pass the tool name as context in the prompt:

```text
Analytics surface: PostHog
Event schema source: posthog.com/project/<id>/data-management
Primary dashboard: [LINK]
```

The member adapts tool-specific recommendations (PostHog insights, GA4 explorations, Mixpanel reports) to the surface you name. Do not create tool-specific agents — it fragments the library and drifts from the shared catalog.

### What Members Cover

- **`marketing-product-analytics-lead`**: funnel trust, event map quality, activation metric definition, attribution logic, cross-tool reconciliation, dashboard hygiene
- **`data-instrumentation-analyst`**: event dictionary, schema versioning, client-to-warehouse integrity, sampling issues, PII/scrubbing compliance, instrumentation gaps

Both cover PostHog-specific features (feature flags, cohorts, session replay, experiments) when the prompt names PostHog as the surface.

## H. Orchestrator Master Criteria — When & What to Use

This is the unified decision matrix the orchestrator runs **before** dispatching a team. It picks topology, synthesis, stopping rule, mask, and mechanism overlays from the question shape.

Read top to bottom: each row is independent. Default rule for every column: pick the **smallest** option that fits.

### H.1 — Topology selection (one row per task)

| Question shape | Topology | Why |
|---|---|---|
| One specialist owns the deliverable | **Single agent** | Coordination cost > value |
| 2-5 specialists, lead synthesizes | **Conductor** (orchestrator-worker) | Lowest coordination overhead |
| 6+ workers, independently parallelizable sub-tasks | **Swarm** (Agent Teams or explicit fan-out) | Parallelism amortizes coordination cost |
| Cross-domain pipeline that summarizes upward (portfolio → repo → feature) | **Holonic** (nested-summary) | Each layer's summary is the next layer's input |
| Single-answer, high-stakes, can't decompose (architecture call, security verdict, strategic recommendation) | **MoA-layered** (proposers + aggregator) | 5-10× tokens for 5-15pp accuracy lift |
| Verifiable single-answer task (math, code, structured reasoning) | **Self-MoA** (one strong model × N samples + aggregator) | Beats heterogeneous debate when oracle exists |
| Two perspectives clash and you need a decision | **Conductor + Debate-Before-Dispatch** | Argue once, then dispatch |
| Live tradeoff with no winning side | **Conductor + Negotiation Protocol** | ZOPA/BATNA over A-or-B |

Cross-link: [`subagents-vs-teams-architecture.md`](subagents-vs-teams-architecture.md) for the full vocabulary, [`harness-patterns.md`](harness-patterns.md) for MoA variants (Standard / Self / Pyramid / Attention).

### H.2 — Synthesis selection (one row per team)

The synthesis owner aggregates members' outputs. Pick by answer shape:

| Answer shape | Synthesis rule | Mechanism | When NOT to use |
|---|---|---|---|
| Discrete (yes/no, A/B/C/D, classification label) | **BMV** (Optimal Weight + Inverse Surprising Popularity) | G18 | N < 3 candidates; verifiable oracle present (use oracle) |
| Open-ended generation, multiple wordings express same idea | **RCS** (embedding centroid) | G19 | N < 5; categorical answers; outlier-correct tasks |
| Soft judgment, mixed claim quality, no clear winner | **Mechanism-design synthesis** + **prediction-market stakes** | G07 + G11 | Trivial decisions; agents can't honestly stake |
| Heterogeneous evidence with conflicting reasoning chains | **Reasoning-Tree Audit** (FPD adjudication) | G13 | Homogeneous models; no real branching |
| Cross-citation between members, semantic merges | **Graph-of-Thoughts audit** (G13 extension) | G13-GoT | Pure tree-shape reasoning (use plain G13) |
| Numeric forecast | **Delphi** (anonymous iterative convergence) | — | Open-ended or qualitative answers |
| Compromise across non-overlapping interests | **Negotiation Protocol** (ZOPA/BATNA) | G12 | Single-correct-answer questions |

### H.3 — Stopping rule selection (one row per team)

| Synthesis shape | Stopping rule | Source |
|---|---|---|
| Vote-based, discrete answer space | **EMS** — stop when leader > N/2 + √N | arxiv 2604.02863 |
| Open-ended, soft judgment | **Adaptive stability** (KS p > 0.10 over 2 rounds) | OpenReview Vusd1Hw2D9 |
| Numeric forecast | Delphi IQR < 20% of median | classic |
| Position-shift heuristic (cheap proxy) | 2 rounds with no new arguments AND no shifts | operator approximation |
| Hard cap whatever the rule | **5 rounds maximum** | beyond this agents restate, don't reason |

### H.4 — Decision-mask selection (one row per agent)

Masks decorate one agent's brief. Pick by reasoning bias likely in that role:

| Reasoning bias / role need | Mask | Use when |
|---|---|---|
| Over-weighted happy path | **Inversion** | Agent likely to imagine success scenarios |
| Legacy analogies dominate | **First-Principles** | Agent grounded in past projects, may carry forward outdated assumptions |
| Decision reversibility unclear | **Regret Minimization** | Pricing, irreversible-cost, one-way-door choices |
| 1st-order win celebrated, no cascade analysis | **Second-Order** | Strategy, platform decisions, multi-agent ripples |
| Anchored to first number / first option seen | **Anchoring Reset** | Estimation under prior numbers, retrospective bias |
| Ignoring base rates / outside view | **Base-Rate Reset** | Decisions that resemble a class of past projects |
| Solo reviewer with hard non-negotiables (security, compliance, brand) | **Constitutional** | Single agent operating without debate behind it |

Cap: **2 masks max per agent**. Methods are team-wide; masks are per-agent. Three agents in one team can wear three different masks.

### H.5 — Game-theory mechanism overlays (orthogonal, stack as needed)

Mechanisms are cross-cutting — they always run alongside whatever method/topology you picked. Pick by the failure mode you're trying to prevent:

| Failure mode | Mechanism | When to layer in |
|---|---|---|
| Verbose agent dominates synthesis | **G11 prediction market** + **CritiCal NL critique** | Always when synthesis has > 2 sources |
| Members hallucinate the same answer (correlated bias) | **G02 adversarial debate** + **G13 reasoning-tree audit** | Heterogeneous teams on soft tasks |
| Single agent over-confident, miscalibrated stakes | **CritiCal** (G11 sub-step) | Always for prediction-market overlay |
| Evidence-light arguments dominate | **G14 credibility scoring** | High-stakes verdicts |
| Same agent always wins synthesis weight | **G05 reputation gating** + **G04 Shapley contribution** | Long-running teams (10+ runs) |
| Adversarial / red-team / probe needed | **G06 cooperation-defection** + **Purple Team** | Security, robustness, compliance |
| Debate loops without converging | **G16 meta-debate routing** + **EMS stopping** | When teams hit > 3 rounds without progress |
| Prompts drift, agents stop improving | **G17 online Shapley prompt evolution** | Continuous improvement on recurring teams |
| One-off compromise needed across non-overlapping interests | **G12 ZOPA/BATNA negotiation** | Pricing, scope, resource allocation |
| Synthesis flat-voting hides minority-correct insight | **G18 BMV** (replaces majority vote) | Always when synthesis aggregates 3+ candidates |
| Multi-wording answers cluster but no plurality | **G19 RCS** | Open-ended best-of-N over 5+ candidates |
| Wrong consensus could trigger irreversible action | **G20 conformal social choice** | Legal, payments, security, release, regulator, or other act/escalate gates |
| Delegate can self-claim quality or authority | **G21 attested delegation contracts** | Cross-runtime, plugin, MCP, external-agent, or marketplace-style routing |
| Large flat team overloads synthesis | **G22 coalition formation routing** | 6+ members or distinct legal/technical/ops/commercial workstreams |

### H.6 — Question-shape → full stack lookup

Use this when you want a one-shot stack recommendation. Each row gives Topology + Synthesis + Stopping + Default Mask + Mechanisms.

| Question shape | Topology | Synthesis | Stopping | Default mask | Mechanism overlays |
|---|---|---|---|---|---|
| Architecture RFC (mutually exclusive options) | Conductor + Debate | Reasoning-tree audit (G13) | Adaptive stability | First-Principles | G11+CritiCal, G14 |
| Pricing change (irreversible, high-blast) | Conductor + Debate (Pre-Mortem) | Mechanism-design (G07) + BMV (G18) | Adaptive stability | Regret Minimization | G11+CritiCal, G12 if compromise needed |
| Code review on PR | Conductor (Code Review Board) | RCS (G19) on verdicts | EMS | Constitutional (per reviewer) | G14, G18 if verdicts split |
| Incident rollback vs fix-forward | Conductor + Debate (Devil's Advocate) | Reasoning-tree audit (G13) | EMS | Second-Order | G11+CritiCal, G06 |
| Release go/no-go | Conductor + Debate (Pre-Mortem) | BMV (G18) + act/escalate (G20) | EMS | Second-Order | G11+CritiCal, G14 |
| Strategy / market positioning | Conductor + Debate (Scenario 2×2) | Mechanism-design (G07) | Adaptive stability | First-Principles | G11+CritiCal, G16 |
| Estimation / forecast (numeric) | Conductor + Delphi | Delphi median + IQR | IQR < 20% of median | Anchoring Reset, Base-Rate Reset | G11+CritiCal |
| Verifiable math / code task | Self-MoA (one model × N) | RCS or oracle | EMS | — | G18 if no oracle |
| High-stakes single-answer no-decompose (e.g., critical security verdict) | MoA-layered (heterogeneous) | BMV (G18) or RCS (G19) | EMS | Constitutional | G11+CritiCal, G14 |
| Cross-team handoff with summary chain | Holonic | Per-level summary contracts | per-layer | First-Principles at each layer | G14 across layers, G21 when delegate identity/authority matters |
| Untested assumptions probe | Conductor + Socratic | Question-list synthesis | Position-shift heuristic | Inversion | — |
| Bot with persistent memory (architecture) | MoA-layered (heterogeneous proposers) | BMV (G18) | EMS | First-Principles | G11+CritiCal, G14, G21 for external tools |

### H.7 — Composition rules (don't violate)

1. **One method per debate, max 2 masks per agent.** Beyond that, synthesis becomes noise.
2. **Method first, then mask, then mechanism.** Method shapes the team; masks decorate agents; mechanisms run cross-cutting.
3. **Default to smallest topology.** Single agent → Conductor → Swarm/MoA. Don't escalate without evidence.
4. **Verifiable oracle present → Self-MoA wins, not heterogeneous debate.** Don't burn tokens on diversity when an oracle settles the answer.
5. **Discrete answer space → BMV. Open-ended → RCS. Numeric → Delphi.** Don't run BMV on prose, don't run RCS on yes/no.
6. **Always layer G11+CritiCal on synthesis with 2+ sources.** Cheap, large calibration gain.
7. **Reasoning-tree audit (G13) replaces majority vote whenever members are heterogeneous.** Plain majority vote is the wrong default for heterogeneous teams.
8. **Stop at 5 rounds, hard.** Beyond that, agents restate. If the team isn't converged, the question isn't ready.
9. **Constitutional mask is for solo reviewers without debate behind them.** Inside a debate team, the debate already provides external critique.
10. **MoA aggregator picks BMV for discrete, RCS for open-ended, mechanism-design for soft-mixed.** Never raw plurality vote in an MoA aggregator.
11. **Consensus is not authorization.** For irreversible actions, add G20 and treat multi-answer sets as escalation, not failure.
12. **Self-claimed quality never grants authority.** For cross-trust delegation, apply G21 before auction routing, reputation updates, or autonomy changes.
13. **Flat panels are not departments.** For 6+ member teams, run G22 coalition formation before final synthesis unless the question is truly single-threaded.

### H.8 — Cross-references

- Topology details: [`subagents-vs-teams-architecture.md`](subagents-vs-teams-architecture.md), [`harness-patterns.md`](harness-patterns.md) §"Mixture-of-Agents (MoA)"
- Synthesis mechanisms: [`game-theory-agent-teams.md`](game-theory-agent-teams.md) (master index of 22 mechanisms)
- Per-mechanism playbooks: [`foundations-game-theory/assets/templates/game-theory/`](../../foundations-game-theory/assets/templates/game-theory/)
- Decision-mask catalog: [`agents/templates/decision-masks/`](../../../../agents/templates/decision-masks/)
- Method catalog: [`agents/templates/debate-methods/`](../../../../agents/templates/debate-methods/)
- Stopping rules: [`debate-quickstart.md`](debate-quickstart.md) §"Adaptive Stopping" (with EMS for vote-based)
- Failure modes: [`mast-failure-taxonomy.md`](mast-failure-taxonomy.md), [`traps-and-antipatterns.md`](traps-and-antipatterns.md)
- Operator-level tip sheet: [`methods-masks-mechanisms-playbook.md`](methods-masks-mechanisms-playbook.md)

## Niche Validation

Use this section when the question is "should I build X in niche Y?" — no
existing product, no analytics, no users. It is the repo-specific team mapping
for the greenfield rows of [section A](#a-decision-map).

| Sub-question | Mode | Second opinion | Debate? |
|---|---|---|---|
| Should I enter this new niche / build this new app? | `expert-board` (`founder-blindspot`, new-niche scenario) | `expert-board` (`startup-strategy`) | yes |
| What are the recurring pain points in this category? | `expert-board` (`founder-blindspot`) with a required `painpoint-scan-report.md` artifact from `research-painpoint-scanner` | — | no |
| Is there real switching-trigger evidence in this market? | `expert-board` (`founder-blindspot`) with a required `switching-trigger-analysis.md` artifact from `research-review-mining` | — | no |
| I built it — how do I penetrate the market? | `expert-board` (`growth`, `market-penetration`) via the [market-penetration contract](workflow-contracts.md#market-penetration-review) | `expert-board` (`founder-blindspot`) | yes |

Rules that differ from the analytics-driven paths:

- **No upstream analytics.** Evidence comes from public sources, so every member
  must be pinned to its canonical skill artifact — a narrative memo is not an
  acceptable substitute for the named artifact.
- **Tool precheck before scanning.** `research-painpoint-scanner` aborts with a
  `GATING DATA GAP` rather than producing narrative when a required tool is
  missing. Silent tool failure is the known failure mode here.
- **Debate on verdict mismatch only.** Run discovery mode first; escalate to
  debate when members disagree on the verdict, not by default.
- **Adjacent-product data is optional but valuable.** If a related app already
  exists, its store and product-analytics curves raise the confidence of the
  founder-market-fit and unit-economics rows in the scorecard.

- **Fill the required context before launch:** the niche in one sentence,
  job-to-be-done, founder stack and skill fit, geography, time-to-revenue
  constraint, and 3–5 named competitors.
- **Output contract:** an auditable validation scorecard with a verdict and a
  riskiest-assumption test, not a narrative memo.

Launch prompt: start from the `expert-board` founder-blindspot prompt in
[team-prompt-patterns.md](team-prompt-patterns.md#expert-board-founder-blindspot)
and add the required context and output contract above.

## Related

- [universal-team-playbook.md](universal-team-playbook.md) — the review sequence, branch rules, and anti-patterns
- [team-coverage.md](team-coverage.md) — canonical team → skill mapping
- [team-scenarios.md](team-scenarios.md) — scenario-to-team examples
- [team-prompt-patterns.md](team-prompt-patterns.md) — short-form and full-form launch prompts
- [team-lifecycle.md](team-lifecycle.md) — setup, run, and cleanup
- [runtime-topology-diagram.md](runtime-topology-diagram.md) — source→runtime flow diagram
- [agent-patterns.md](agent-patterns.md) — reusable subagent patterns
- [debate-quickstart.md](debate-quickstart.md) — debate setup across runtimes
