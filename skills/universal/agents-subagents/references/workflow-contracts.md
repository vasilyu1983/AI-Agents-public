---
description: Canonical ownership, evidence, sequencing, output, and cleanup contracts for retained team and workflow scenarios.
last_verified: 2026-09-16
status: stable
---

# Workflow Contracts

Canonical launch contracts retained from the retired `assets/team-launchers/`
playbooks. Use these contracts with Claude saved workflows, Claude Agent Teams,
or explicit parent-led Codex subagents. The execution surface may change; the ownership,
evidence gates, sequencing, outputs, and cleanup rules below must not.

## Contents

- [Common Runtime Contract](#common-runtime-contract)
- [Universal Growth Sequence](#universal-growth-sequence)
- [Market Penetration Review](#market-penetration-review)
- [Startup Growth Review](#startup-growth-review)
- [Startup Monetization Review](#startup-monetization-review)
- [Code Review](#code-review)
- [Startup Analysis](#startup-analysis)
- [Feature Delivery](#feature-delivery)
- [Context Preparation](#context-preparation)

## Common Runtime Contract

Every run must resolve the eight fields in
[initial-prompt-contract.md](initial-prompt-contract.md): goal, required context,
optional context, member ownership, execution mode, debate rule, synthesis
owner, and cleanup. Work independently before cross-challenge when a contract
calls for a blind first round. Read-only reviewers must not edit. Writers need
exclusive file ownership. The parent closes one team before opening another;
for orphaned Claude team state use `bash scripts/teardown-team.sh`.

Install a retained team recipe with `bash scripts/deploy-preset.sh <team-name>`.
Claude saved workflows may instead use generic role-brief workers where no named
specialist configuration is required. Codex has no native saved-workflow parity
claim here. For bounded expert boards, use the generated
`agents/workflows/expert-board.codex-plan.json` launcher contract: select the
board and mode, launch each planned worker with its self-contained brief and
`fork_turns: "none"`, wait for the blind memos, issue the planned challenge with
`send_input` (`features.multi_agent` is on by default and documents only
`spawn_agent`, `send_input`, `resume_agent`, `wait_agent`, and `close_agent`;
there is no separate follow-up primitive), and synthesize in the parent. Regenerate or verify that adapter
with `python3 scripts/generate_codex_expert_board_plan.py [--check]`. Its strict
context, algedonic bypass, exact debate-trigger, EVPI expansion, verification,
and regret gates are executable parent obligations, not descriptive suggestions.
If a planned named `agent_type` is unavailable, retry once with the default
agent by omitting `agent_type` while preserving the same role brief, skill ids,
and read-only constraint.

## Universal Growth Sequence

Use this evidence-gated sequence when the true product bottleneck is unknown.
It is a workflow, not one large team. Run exactly one stage at a time:

1. `expert-board` (`startup-strategy`) frames the real business question.
2. `expert-board` (`marketing-diagnostics`) tests acquisition, discoverability, and funnel quality.
3. `expert-board` (`product-discovery`) tests the product, roadmap, and user evidence.
4. Branch to exactly one board:
   - `expert-board` (`founder-blindspot`) for an ambiguous or hidden constraint;
   - `expert-board` (`monetization`) when usage exists but money does not follow;
   - `expert-board` (`growth`) in `market-penetration` mode when the product exists
     but the first market, channel, and 30-day route are unclear.
5. Hand exactly one winning opportunity to `product-surface`,
   `dev-feature-delivery`, `expert-board` (`mobile-product`), or
   `expert-board` (`architecture-rfc`).

Required intake: product/repo family, ICP, revenue model, current bottleneck,
funnel, activation, retention and monetization snapshots, top three complaints,
and the last three meaningful experiments. Do not begin a stage until the prior
stage names a bottleneck. Do not run multiple branch boards unless the first
returns `insufficient evidence`. All stages 1-4 are read-only; debate happens
inside each stage, never between stages. Return the bottleneck after every
stage, winning hypothesis, smallest next experiment, and execution-team handoff.

## Market Penetration Review

Use when a product exists but the route to serious users is unclear. Do not use
for a wholly unbuilt idea or a pure pricing diagnosis.

Evidence gate: diagnose activation and retention before scaling acquisition.
Paid traffic is out until users can reach first value and show credible return
behaviour. If fewer than five intake fields are known, return a data-gap and
instrumentation plan before recommending channels.

Required intake includes the product promise, ICP guess, wedge, revenue model,
pricing, channel results, first-value event and time-to-value, retention,
monetization, complaints, competitors, recent experiments, analytics surfaces,
and founder constraints.

Ownership:

- `product-strategist`: wedge, segment choice, and synthesis.
- `startup-growth-specialist`: traction stage, loops, channels, and 30-day plan.
- `marketing-product-analytics-lead`: activation, retention, attribution, and
  metric trustworthiness.
- `startup-product-marketing-strategist`: category frame, positioning, proof,
  and launch narrative.
- `startup-business-developer`: commercial fit, buyer quality, partnerships,
  and repeatability.

Run independent parallel reads, then force-rank product, positioning, channel,
and monetization explanations. Select one exact audience/use case/trigger and
anti-ICP, one primary channel and one backup. Judge channels by activated users
or another serious downstream signal, not impressions, traffic, or signups.
Treat onboarding, App Store fit, plan mix, renewal, and billing recovery as
mobile growth levers. Treat SEO/AEO/GEO as demand capture layered on clear proof.

Return: growth stage (0-3) with evidence; exact market wedge; category/promise/
proof/objection; primary and backup channels plus channels to avoid; one
activation-quality metric; weekly 30-day plan; instrumentation gaps; strongest
dissent and flip evidence; and the named execution team/owner. Route activation
work to product/mobile/delivery, pricing to monetization, discoverability to
marketing diagnostics, hidden-wedge risk to founder blindspot, and a ready
channel experiment to `expert-board` (`growth-experiments`).

## Startup Growth Review

Use for “why is growth not working?”, “what should improve next?”, or “is growth
healthy or misleading?” Start with the universal sequence or startup analysis
when the problem is still vague; use market penetration when market/channel
selection is the sharper question.

Required context: startup, stage, ICP, concern, and current funnel, activation,
retention, and revenue metrics. Optional context: pricing/paywall, acquisition
surfaces, 30-60 day experiment history, and instrumentation caveats.

Run independent reads by `product-strategist`, `startup-growth-specialist`,
`marketing-product-analytics-lead`, `startup-product-marketing-strategist`, and
`startup-business-developer`. Debate healthy-versus-vanity growth and product
versus distribution versus monetization. `product-strategist` synthesizes:
healthy/fragile/misleading, strongest bottleneck, three highest-leverage
opportunities, smallest experiment, strongest dissent, and execution-team handoff.

## Startup Monetization Review

Use when activation exists but revenue is weak, upgrades are confusing,
pricing objections rise, or packaging needs a safer change path.

Required context: startup, ICP, current plans/paywall/sales motion, pricing and
packaging, revenue/conversion snapshot, and main concern. Add paywall placement,
copy, churn/expansion, cohort behaviour, competitor pricing, prior experiments,
and sales objections when available.

Run independent reads by `startup-pricing-advisor` (price, packaging, value
metric, synthesis), `marketing-product-analytics-lead` (conversion and cohort
evidence), `marketing-strategist` (value communication),
`startup-operating-system-reviewer` (billing, cash flow, payback and downside),
and `startup-business-developer` (willingness to pay and commercial fit). Debate
packaging, value communication, paywall timing, and price level. Return the
diagnosis, top gaps, three experiments with expected impact, risks/guardrails,
and measurement requirements.

## Code Review

Use for an important PR, module, pre-release, or security-sensitive change.
Reviewers are read-only:

- `software-security-reviewer`: auth, input validation, secrets, OWASP risks.
- `software-performance-reviewer`: queries, memory, caching, algorithmic cost.
- `qa-test-reviewer`: coverage, edge cases, and test reliability.

Required context is the PR/diff/module. Prefer existing code graphs, query
reports, repo profiles, and catalogs before cold discovery. Run a blind parallel
first round, then cross-share only findings affecting another lane. Debate
severity disagreements and security-versus-performance/delivery conflicts. The
parent returns one severity-ordered report.

For PRs, focus on the diff and use graph artifacts for callers and affected
tests. For a pre-release audit, scan the whole source tree and prioritize release
blockers. For a module review, read the module and tests and include architectural
impact. Headless alternative: `bash scripts/headless-review.sh [path]`.

## Startup Analysis

Use `expert-board` (`startup-strategy`) to frame the real business question before choosing a
narrower board. Required context: startup, stage, ICP, revenue model, and review
concern. Add funnel/activation/retention, pricing, experiments, and competitors
when available.

Run independent parallel reads by `marketing-strategist` (position/message),
`startup-business-developer` (model/commercial leverage),
`startup-growth-specialist` (loops/channels), `product-strategist` (wedge/
roadmap/synthesis), and `software-ux-designer` (flows/usability). Cross-challenge
GTM, product direction, growth health, and product-versus-distribution priority;
record unresolved dissent.

Supported tasks include idea evaluation (positionability, payer, acquisition,
PMF validation, core flow), launch planning (timeline, owners, success criteria),
GTM review (what works, what is broken, one high-impact change per lane),
competitive battlecards, and pricing/business-model review. Return the winning
question and hand it to one narrower board rather than reusing this team.

## Feature Delivery

Use `dev-feature-delivery` for a bounded feature, bug, or refactor that benefits
from research → implementation → review. Required context: task, acceptance
criteria, and the exact files the implementer may own. Prefer existing profiles,
catalogs, system/knowledge/code graphs, query reports, tests, and related PRs.

Run sequentially:

1. `dev-feature-researcher` maps relevant behaviour, APIs, callers, and risk.
2. `dev-feature-implementer` writes only assigned files and runs verification.
3. `dev-feature-reviewer` checks acceptance criteria, regressions, and tests.

Researcher and reviewer are read-only; stages do not overlap and debate is off.
For a feature, reviewer rejects missing tests on new paths. For a bug, reproduce
first and add a regression test. For a refactor, map every caller, preserve
behaviour, and reject unintended API changes. Leave the branch for human
inspection. A single implementation subagent is cheaper for a small, understood
change.

## Context Preparation

Use `dev-context-preparation` to create durable artifacts before implementation,
review, or migration. Required context: repo/repo set and output locations. Use
existing `AGENTS.md`, `CLAUDE.md`, catalogs, or profiles as update inputs.

Run staged with disjoint ownership:

1. `dev-portfolio-mapper` → `code-profiles/**`, `catalog/**`.
2. `dev-repo-context-curator` → `AGENTS.md`, `CLAUDE.md`, `docs/context/**`.
3. `dev-code-graph-builder` → `graphs/**`, `reports/code-graph-*.md`.
4. `dev-context-packet-synthesizer` → `reports/query-*.md`, `packets/**` and
   final synthesis.

Keep raw evidence, normalized metadata, and Markdown summaries separate. Prefer
graphs/profiles/catalogs to prose dumps; never paste inventories into AGENTS.md.
For code review, refresh the graph and create a packet of callers/tests/modules.
For feature work, identify context layers, owned files, blast radius, constraints,
and verification targets. For a portfolio hub, build normalized repo profiles,
catalogs, compiled context boundaries, and an operator index. Return artifact
paths, stale/coverage gaps, and the single packet downstream workers should read
first. Artifacts persist after team cleanup.
