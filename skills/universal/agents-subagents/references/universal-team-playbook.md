---
description: Any-repo review cadence, intake pack, and team anti-patterns.
last_verified: 2026-09-02
status: stable
---

# Universal Team Playbook

Operating system for running review cycles across any repo, product, or startup — regardless of stage or portfolio.

For the full decision map (common questions → correct team) and custom team/agent recipes, see [team-selection-guide.md](team-selection-guide.md).

## Table of Contents

- [Purpose](#purpose)
- [How It Works](#how-it-works)
- [Default Review Sequence](#default-review-sequence)
- [System Diagram](#system-diagram)
- [Minimum Evidence Pack](#minimum-evidence-pack)

## Purpose

This playbook is for one recurring question:

> Which repo or product should I push next, what am I missing, and what is the smallest move that can improve growth or monetization?

It is intentionally evidence-gated. The goal is to avoid early-agent failure modes:

- running too many boards without a clear question
- accepting confident but weakly evidenced recommendations
- browsing endlessly when the answer should come from your own product data
- changing pricing without a test design
- confusing analysis quality with actual growth leverage

## How It Works

The startup system has five layers:

1. Shared startup, marketing, and product skills provide the reusable domain knowledge.
2. Canonical members turn those skills into distinct working lenses such as pricing, pain-point discovery, or trend analysis.
3. Teams combine those members into a review board with clear debate and synthesis rules.
4. Launchers decide the correct order to run those boards.
5. Execution teams ship the chosen opportunity after the review selects one concrete move.

The main discipline is that the workflow contract controls sequence and teams do not self-expand into an uncontrolled swarm.

## Default Review Sequence

Run one stage at a time.

1. `expert-board` in `startup-strategy` mode
   - define the business question
   - frame the real bottleneck
   - decide what “success in the next 30 days” means

2. `expert-board` in `marketing-diagnostics` mode
   - test whether the issue is discoverability, message clarity, acquisition, or funnel-quality

3. `expert-board` in `product-discovery` mode
   - test whether the issue is activation, retention, roadmap fit, or weak user evidence

4. Branch to exactly one:
   - `expert-board` in `founder-blindspot` mode
   - `expert-board` in `monetization` mode

5. Execution handoff
   - `product-surface`
   - `dev-feature-delivery`
   - `expert-board` in `mobile-product` mode
   - `expert-board` in `architecture-rfc` mode before a hard-to-reverse design handoff

In practice, this means:

- do not start with the blindspot board unless the problem is already clearly ambiguous
- do not start with the monetization board unless users already reach the product and revenue is the weak point
- do not hand work to engineering until one board names one concrete opportunity

## System Diagram

See [startup-growth-system-diagram.md](startup-growth-system-diagram.md) for the visual system map and the staged review flow.

## Minimum Evidence Pack

Every review should start with:

- startup name and repo family
- target customer / ICP
- current revenue model
- current bottleneck
- acquisition snapshot
- signup to activation snapshot
- retention snapshot
- monetization snapshot
- top 3 complaints, objections, or friction signals
- top 3 recent experiments or launches

If these are missing, the first team should say so explicitly instead of guessing.

Evidence should be pulled from your own product and customer context first:

- product analytics and funnel snapshots
- support tickets, chats, or emails
- sales objections
- reviews and public feedback only after internal evidence is exhausted

The system should not browse widely by default when the missing answer should come from your own product data.

## Branch Rules

Choose `expert-board` in `founder-blindspot` mode when:

- the growth problem is ambiguous
- the signals contradict each other
- the founder suspects “something important is missing”
- there may be hidden segments, weak signals, or ignored objections

Choose `expert-board` in `monetization` mode when:

- people sign up or use the product, but revenue lags
- upgrades are weak or confusing
- pricing objections are increasing
- packaging and value communication seem broken

Do not run both branch boards in the same cycle unless the first branch ends with insufficient evidence.

## Output Contract

Every team in the sequence should return the same compact shape:

- bottleneck
- evidence
- top 3 opportunities
- smallest next experiment
- expected impact
- confidence
- data gap
- recommended execution team

This keeps synthesis comparable across teams.

## Team Responsibilities

- `expert-board` in `startup-strategy` mode
  - define the real business question
  - decide what success means in the next 30 days
  - stop the workflow if the input problem is still vague
- `expert-board` in `marketing-diagnostics` mode
  - test discoverability, message quality, acquisition, and funnel capture
  - avoid broad SEO advice when the issue is really funnel trust or ICP mismatch
- `expert-board` in `product-discovery` mode
  - test activation, retention, roadmap fit, and evidence quality
  - identify where product intuition is not backed by evidence
- `expert-board` in `founder-blindspot` mode
  - surface weak signals, ignored objections, hidden segments, or timing shifts
  - challenge founder-normalized assumptions
- `expert-board` in `monetization` mode
  - diagnose pricing, packaging, paywall, and value-communication issues
  - recommend only measurable experiments, not comfort-pricing guesses
- execution teams
  - implement only the chosen opportunity, not the full brainstorm list

## Repo Context Overlay

Project-specific skills (anything under `project-*` in the shared-skills catalog) are overlays, not replacements. When a review runs against a repo that has matching project skills, load them into the parent thread context so team members can reference them — but the workflow, branch rules, and output contract still come from this playbook.

Do not wire project skills into shared team recipes or member frontmatter. Keep project skills isolated per CLAUDE.md guidance.

## Anti-Patterns

Avoid these:

- launching every startup board because “more opinions are better”
- treating web research as better evidence than your own funnel or user feedback
- asking the monetization board to recommend price changes without cohort or test framing
- letting a strategy board browse widely before it has the intake pack
- handing execution to engineering before the review selects one concrete opportunity
- accepting outputs that do not identify a data gap
- using both branch boards in one cycle before the first branch fails to produce a clear next move
- confusing “more agent opinions” with “better founder judgment”

## Suggested Cadence

- Weekly: one portfolio review cycle for the startup with the best near-term leverage
- Monthly: one blind-spot review for the startup that feels the most ambiguous
- Before major pricing or paywall changes: a dedicated monetization review

## Where To Start

Use these in order:

1. [team-selection-guide.md](team-selection-guide.md) to map your concrete question to the correct team before launching anything
2. [Universal growth sequence](workflow-contracts.md#universal-growth-sequence) for the sequential multi-team review cadence
3. [Startup growth review](workflow-contracts.md#startup-growth-review) when the main issue is growth prioritization
4. [Startup monetization review](workflow-contracts.md#startup-monetization-review) when the main issue is pricing, paywall, or upgrades

## Research Basis

This operating model reflects current agent guidance and startup-growth practice:

- purpose-built workflows with evals beat broad autonomous swarms
- human oversight matters most on ambiguity and high-stakes choices
- output quality should be judged on evidence and outcomes, not rigid tool order
- product analytics should be directly useful to founders, PMs, and marketers
- pricing changes should be cohort-tested and value-based rather than driven by guesswork
