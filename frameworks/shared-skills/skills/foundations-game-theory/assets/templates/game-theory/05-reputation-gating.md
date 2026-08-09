# Mechanism: Reputation-Gated Autonomy

**Source**: Intelligent AI Delegation frameworks, principal-agent theory (2025-2026).

## Domain Applications

- **Supplier / vendor qualification**: new suppliers start on probationary tier with mandatory review; consistent delivery earns reduced oversight and higher autonomy limits.
- **Fraud and risk gating**: transaction counterparties scored by historical accuracy and dispute rate; low-reputation counterparties trigger manual review thresholds.
- **API consumer trust tiers**: developers start at rate-limited sandbox; demonstrated responsible usage earns production access.
- **Agent team oversight**: members with low Shapley contribution scores or prior errors receive closer synthesis scrutiny or reduced autonomy scope.

## Problem

All members get the same level of trust and oversight, regardless of track record.

## Solution

Build a trust score per member role. Higher trust = more autonomy. Lower trust = more oversight.

## Trust Tiers

| Tier | Trust Level | Oversight | Applies When |
|------|:----------:|-----------|-------------|
| **Proven** | High | Synthesis owner reviews final output only | Member has consistently high Shapley contributions |
| **Standard** | Medium | Synthesis owner reviews key findings | Default for established members |
| **Probationary** | Low | Synthesis owner validates each claim against evidence | New member, or member with recent low-quality output |
| **Adversarial** | Verified | Output must be confirmed by an independent member | High-stakes decisions, or member with known bias |

## Principal-Agent Problem in Teams

The synthesis owner is the **principal** — they want accurate, useful analysis. Members are **agents** — they produce output but may have misaligned incentives (over-confidence, scope creep, hallucination).

**Mechanism design fix**: Make it easier for members to be honest about uncertainty than to fake confidence.

In launch prompts, add:

```
Confidence calibration rule:
- State confidence level for each finding (high/medium/low)
- "I don't have enough evidence" is a valid and valued output
- Confident but wrong outputs are worse than honest uncertainty
- Synthesis owner will weight honest uncertainty HIGHER than confident guesses
```

## Launch Prompt Template

```
You are [MEMBER_ROLE] operating under [TRUST_TIER] oversight.

Task: [TASK_DESCRIPTION]
Your trust tier: [PROVEN | STANDARD | PROBATIONARY | ADVERSARIAL]

Trust tier instructions:
- PROVEN: Complete the task and flag any finding you are less than 80% confident in.
- STANDARD: For each major finding, rate your confidence (high/medium/low) and cite supporting evidence.
- PROBATIONARY: For every claim, state your confidence level and the specific evidence behind it. "I don't have enough evidence" is a valid and valued output.
- ADVERSARIAL: Your output will be independently verified. Provide your full reasoning chain so it can be audited step-by-step.

Confident-but-wrong outputs are penalized more heavily than honest uncertainty.
```

## Kill Criteria

Skip this mechanism when:
- All team members are new with no track record — you have no Shapley history to set tiers from. Fall back to STANDARD for all and build history first.
- The task is low-stakes and single-use — tier overhead not worth it for one-off queries.
- The team has only one member — gating without alternatives to route to creates a dead-end review loop.
- Adversarial tier is triggered for all members simultaneously — this signals a team composition problem, not a reputation problem. Rebuild the team.

## Related

- [`04-shapley-contribution.md`](04-shapley-contribution.md) — feeds the trust score
- [`11-prediction-market.md`](11-prediction-market.md) — calibration tracking refines reputation
- [`../../../references/principal-agent-delegation.md`](../../../references/principal-agent-delegation.md) — full principal-agent treatment
