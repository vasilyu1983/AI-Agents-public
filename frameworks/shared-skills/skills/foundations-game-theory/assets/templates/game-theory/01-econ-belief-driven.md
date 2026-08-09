# Mechanism: Belief-Driven Coordination (ECON Pattern)

**Source**: ECON (ICML 2025) — +11.2% accuracy, -21.4% tokens vs. multi-agent debate.

## Problem

Standard team coordination requires expensive multi-round communication between members. Each round consumes tokens and context window.

## Solution

Each member optimizes independently based on **beliefs about what co-members will produce**, rather than waiting for their actual output.

## How It Works

```
Coordinator sets priors:
  "pricing-advisor will focus on unit economics"
  "growth-specialist will focus on channel efficiency"
  "product-strategist will focus on activation"

Each member reads priors + context → produces output independently
  (No inter-member communication needed)

Coordinator aggregates using hierarchical synthesis
  (Not majority voting — structured integration)
```

## Applying to Team Manifests

| Standard Approach | ECON Enhancement |
|-------------------|------------------|
| Members run in parallel, each reads full context | Members run in parallel, each reads context + **belief brief** about what other members will cover |
| Synthesis owner reads all outputs sequentially | Synthesis owner uses **structured aggregation** — identifies agreements, disagreements, and gaps |
| Debate triggers when any member disagrees | Debate triggers only at **critical divergence points** — saves cost |

## Implementation in Launch Prompts

Add to the launch prompt's member ownership section:

```
Belief brief for each member:
- pricing-advisor: focus on revenue mechanics. Expect growth-specialist to cover CAC/channel.
  Don't duplicate channel analysis.
- growth-specialist: focus on acquisition and retention loops. Expect pricing-advisor to cover
  packaging. Don't duplicate pricing analysis.
- product-strategist: focus on user journey and activation. Expect others to cover economics.
  Challenge their assumptions if activation evidence contradicts economic assumptions.
```

**Why it works**: Members produce complementary (not redundant) outputs because each knows its lane. The belief brief is the coordination mechanism — cheaper than inter-member chat.

## Related

- [`02-adversarial-debate.md`](02-adversarial-debate.md) — debate-on-trigger composes naturally with belief briefs
- [`04-shapley-contribution.md`](04-shapley-contribution.md) — measure whether belief-brief lanes were honored
