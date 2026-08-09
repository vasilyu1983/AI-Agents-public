# Mechanism: Courtroom-Style Progressive Debate (PROClaim Pattern)

**Source**: PROClaim (March 2026) — +10pp accuracy over standard multi-agent debate on claim verification.

## Domain Applications

- **Security vulnerability assessment**: plaintiff argues exploitation feasibility, defense argues mitigations; court/judge roles enforce evidence standards; progressive RAG adds external CVE data mid-debate.
- **Legal and regulatory risk go/no-go**: plaintiff builds the regulatory violation case, defense the compliance argument; critic challenges both; judges produce a decision with audit trail.
- **Medical / clinical claim verification**: two clinician perspectives + a methodologist critic; court role enforces evidence-quality standards at each claim.
- **Agent team high-stakes decisions**: primary agent-team use case — plaintiff/defense/court structure with role-switching prevents position lock and forces evidence grounding.

## Problem

Standard debate uses static evidence. Over rounds, agents rehash the same arguments with no new information. Evidence stagnation causes confident convergence on wrong answers.

## Architecture

Five roles with mandatory heterogeneity (different models per role):

| Role | Function | Maps to Agent Teams |
|------|----------|-------------------|
| **Plaintiff Counsel** | Argues for the claim | Domain specialist who supports the hypothesis |
| **Defense Counsel** | Argues against the claim | Domain specialist who challenges it |
| **The Court** | Refines retrieval queries, manages flow | Orchestrator / lead |
| **Critic Agent** | Independently evaluates both sides | Third-party reviewer (not aligned with either side) |
| **Judicial Panel** | 3 heterogeneous judges, majority vote on verdict | Synthesis through diverse models or diverse role perspectives |

## Progressive RAG (P-RAG)

Instead of one-shot evidence retrieval, P-RAG dynamically expands evidence during debate:

```
Each round:
  1. Both sides identify evidence gaps from previous arguments
  2. Court refines retrieval queries based on gaps + reflection
  3. P-RAG retrieves, filters by novelty score: novelty(d) = 1 - max(cos(e_d, e_pool))
  4. Admits evidence only when relevance × credibility > 0.5
  5. Stops when: novelty < 0.20, redundancy ratio hit, or iteration cap

Impact: +7.5pp accuracy from P-RAG alone (prevents evidence stagnation)
```

## Role-Switching Consistency Test

After primary debate, plaintiff and defense swap positions and re-run. An analyzer checks whether arguments contradict the original position — surfaces whether reasoning is evidence-driven or position-anchored.

**Impact**: -4.2pp accuracy without role-switching.

## When To Use

- The question has a clear for/against structure (pricing change, architecture migration, feature kill)
- Evidence quality matters more than opinion diversity
- You need audit trail for the decision (compliance, board decision)

## Launch Prompt

```
Courtroom debate prompt:
  Plaintiff (startup-growth-specialist): argue FOR the proposed pricing change
  Defense (startup-pricing-advisor): argue AGAINST with evidence
  Court (product-strategist): manage rounds, refine evidence queries
  Critic (marketing-product-analytics-lead): evaluate both sides independently
  Judicial panel: lead synthesizes with dissent noted

  After round 2: swap plaintiff and defense, re-run one round
  Flag any argument that contradicts the swapped position
```

## Key Finding: Negativity Bias in LLMs

PROClaim discovered LLMs exhibit structural negativity bias: REFUTE claims converge 0.2-0.3 rounds faster than SUPPORT claims. Teams should be aware that "against" positions may reach false consensus faster than "for" positions.

## Related

- [`02-adversarial-debate.md`](02-adversarial-debate.md) — lighter-weight debate variant
- [`../debate-methods/courtroom.md`](../debate-methods/courtroom.md) — debate-method overlay equivalent
