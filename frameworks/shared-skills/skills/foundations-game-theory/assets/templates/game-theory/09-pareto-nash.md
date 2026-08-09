# Mechanism: Pareto-Nash Equilibrium for Multi-Objective Teams

**Source**: Game-theoretic multi-objective research (2025-2026), DeepMind asymmetric games.

## Domain Applications

- **Pricing strategy**: objectives include revenue, retention, and competitive positioning; Pareto frontier maps non-dominated price points; decision-maker picks from the efficient set, not from the global maximum of any single metric.
- **Product roadmap tradeoffs**: speed vs. quality vs. cost; map Pareto frontier across release options; flag dominated options (worse on all objectives) for elimination before prioritization discussion.
- **Regulatory vs. growth decisions**: compliance cost vs. market opportunity; Pareto-dominant options satisfy both constraints better than alternatives; non-dominated set presented to decision-maker.
- **Agent team multi-objective synthesis**: when team members optimize for different objectives, Pareto-Nash maps the efficient frontier rather than forcing a single synthetic answer.

## Problem

Agent teams often optimize for a single objective (accuracy, speed, cost) when real decisions involve tradeoffs across multiple objectives (quality vs. speed vs. cost, security vs. UX, growth vs. monetization).

## Concept

A Pareto-Nash Equilibrium is a policy profile where no agent can unilaterally improve one objective without sacrificing another. It merges Nash stability (no one wants to deviate) with Pareto optimality (no waste).

## Applying to Team Synthesis

```
Multi-objective synthesis protocol:

Step 1: Each member states their findings along the objectives they own
  - growth-specialist: growth impact (high/medium/low) + evidence
  - pricing-advisor: revenue impact (high/medium/low) + evidence
  - security-reviewer: risk impact (high/medium/low) + evidence

Step 2: Synthesis owner maps the Pareto frontier
  - Option A: high growth, medium revenue, high risk
  - Option B: medium growth, high revenue, low risk
  - Option C: low growth, low revenue, low risk (status quo)

Step 3: Identify dominated options (worse on ALL objectives)
  - Remove dominated options

Step 4: Present remaining Pareto-optimal options with explicit tradeoffs
  - "Option A beats B on growth but loses on risk — here's what you're trading"

Step 5: Decision-maker (user or lead) picks based on current priorities
```

## When To Use

| Team | Multi-Objective Applies? | Objectives |
|------|:------------------------:|------------|
| startup-monetization-board | Yes | Revenue vs. UX vs. churn risk |
| software-architecture-rfc | Yes | Performance vs. maintainability vs. delivery speed |
| startup-growth-board | Yes | Growth vs. monetization vs. retention |
| software-code-review-board | No — single objective (correctness) | Not needed |
| dev-feature-delivery | No — execution, not tradeoff | Not needed |

## Formal Theory Note — Convex Markov Games

Standard Pareto-Nash analysis assumes agents have scalar reward objectives in a standard Markov game. Convex Markov games (ICML 2025, arXiv 2410.16600) extend Nash existence to agents with **convex preferences over occupancy measures** — meaning fairness constraints, behavioral diversity goals, and safety requirements can be expressed natively as objectives without requiring scalar reward reduction. Pure-strategy Nash equilibria are proven to exist despite infinite horizons. Approximate equilibria are computable via gradient descent on an exploitability upper bound.

**Implication for this primitive**: when team members' objectives include fairness, safety, or diversity constraints that cannot be reduced to a scalar metric, the Pareto-Nash frontier analysis still applies — but equilibrium existence now rests on convex preference theory rather than standard reward-function Nash existence. The gradient-descent approximation provides a computable path even when the Pareto frontier is non-convex under scalar projection.

**Calibration note**: the exploitability upper bound from the gradient-descent algorithm may be loose in practice; treat the approximate equilibrium as a starting point and verify empirically.

## Related

- [`12-negotiation-zopa-batna.md`](12-negotiation-zopa-batna.md) — when the tradeoff requires bargaining, not just frontier mapping
- [`07-mechanism-design-synthesis.md`](07-mechanism-design-synthesis.md) — synthesis protocol that preserves dissent
