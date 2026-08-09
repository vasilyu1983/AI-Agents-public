---
name: Conformal Social Choice Act/Escalate
mechanism_id: 20
layer: synthesis
status: emerging
last_verified: 2026-05-08
sources:
  - https://arxiv.org/abs/2604.07667
---

# Conformal Social Choice — Calibrated Act/Escalate

Post-debate decision layer that converts several agent opinions into an action set with a calibrated refusal-to-act boundary.

## Problem

Multi-agent debate can converge on a wrong answer. Agreement is useful evidence, but it is not a guarantee. If the synthesis owner treats consensus as permission to act, a wrong majority can trigger deployment, legal advice, payment movement, release approval, or customer communication with no safety valve.

## Solution

Ask each member for a probability distribution over candidate answers or actions. Aggregate the distributions, calibrate the combined set against a held-out or shadow-scored case set, then map the result to:

- **singleton set**: act autonomously on that answer
- **multi-answer set**: escalate, gather evidence, or ask the operator
- **empty/unstable set**: no decision; rerun with better evidence

The point is not to make debate smarter. The point is to make debate failure actionable.

## When to Use

- High-stakes team verdicts: release gates, legal/regulatory posture, security approval, payments, fraud, medical-like review, financial decisions.
- Cases where agents agree but the cost of a wrong action is high.
- Heterogeneous panels where member confidence scales are not directly comparable.
- Any team already collecting confidence, prediction-market stakes, or per-claim probabilities.

## When NOT to Use

- A deterministic oracle exists: test suite, compiler, schema, calculator, official source lookup.
- Low-stakes reversible actions where escalation cost exceeds failure cost.
- No calibration set or shadow history exists and the action is irreversible. Use a hold/escalate default until enough cases accumulate.
- Pure ideation where diversity matters more than calibrated correctness.

## Protocol

```yaml
synthesis:
  protocol: conformal_social_choice
  inputs:
    candidates: [A, B, C]
    member_distributions:
      member_1: {A: 0.70, B: 0.20, C: 0.10}
      member_2: {A: 0.45, B: 0.40, C: 0.15}
      member_3: {A: 0.60, B: 0.25, C: 0.15}
    calibration_alpha: 0.05
  output_policy:
    singleton: act
    multiple: escalate
    unstable: gather_evidence
```

Minimum implementation:

1. Generate candidate actions.
2. Collect independent probability distributions from each member.
3. Pool probabilities linearly or with calibrated member weights.
4. Compare pooled confidence against a calibration table from shadow cases.
5. Act only when the conformal prediction set has one answer.

## Agent-Team Pattern

Add this when the team manifest has a high-stakes verdict:

```yaml
synthesis:
  protocol: conformal-social-choice
  confidence_calibration: true
  escalation_policy: multi_answer_set
```

The final answer must include:

- candidate set
- selected singleton or escalation reason
- confidence/calibration note
- evidence gaps that would shrink the set

## Anti-Patterns

- **Consensus-as-correctness**: three agents agree, so the system acts. This is exactly what the mechanism prevents.
- **Verbal confidence without calibration**: "high confidence" from different models is not a common unit.
- **Escalation hidden as failure**: a multi-answer set is a valid result, not a failed run.
- **Calibrating on synthetic cases only**: useful for bootstrapping, weak for production gating.

## Composition

- **Pairs with G11 (Prediction Market)** for probability elicitation.
- **Pairs with G13 (Reasoning-Tree Audit)** to create candidate actions and evidence gaps.
- **Pairs with G15 (Generative Social Choice)** when the output must satisfy several stakeholders.
- **Replaces raw consensus stopping** in high-stakes debate.

## Sources

- arXiv 2604.07667 — *From Debate to Decision: Conformal Social Choice for Safe Multi-Agent Deliberation*.
