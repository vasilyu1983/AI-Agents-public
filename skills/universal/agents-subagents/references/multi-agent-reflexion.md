---
description: Post-synthesis quality check via critic debate (MAR Reflexion overlay).
last_verified: 2026-09-02
status: stable
---

# Multi-Agent Reflexion (MAR)

Post-synthesis quality check. After a team produces its recommendation, spawn 2-3 critics who debate whether the synthesis was fair, complete, and evidence-grounded. Prevents "degeneration of thought" where single-agent reflection repeats the same flawed reasoning.

## Why Standard Reflection Fails
Single-agent reflection is vulnerable to self-consistency trap: the agent defends its own output confidently across iterations. Sycophantic reflection: the agent agrees with itself. MAR fixes this by replacing self-critique with cross-critic debate — different personas critique the same synthesis.

## Mechanism
After team synthesis is complete:
1. Spawn 2-3 critic agents with different evaluation lenses
2. Each critic reads the synthesis + original member outputs
3. Critics evaluate independently, then debate disagreements
4. Output: synthesis quality score + specific issues found + recommended revisions

## Critic Lenses
- Evidence Auditor: Did synthesis cite evidence accurately? Did it fabricate consensus?
- Dissent Inspector: Was the minority position fairly represented? Was it suppressed or strawmanned?
- Gap Finder: What questions did NO member address? What evidence was available but unused?

## Protocol
Round 0: Team produces synthesis normally
Round 1 (reflexion): Spawn critics. Each reads synthesis + original outputs independently.
Round 2 (critic debate): If critics disagree on quality, they debate (one round max).
Output: Pass/Fail/Revise + specific issues + revised synthesis if Revise.

## When To Use
- High-stakes decisions only (2-3x additional compute cost)
- `expert-board` architecture-rfc mode (irreversible architecture changes)
- `expert-board` startup-strategy mode (GTM direction changes)
- `expert-board` monetization mode (pricing changes)
- Any time the synthesis feels "too clean" or reaches consensus suspiciously fast

## When NOT To Use
- Routine reviews (cost not justified)
- When the team had genuine debate with clear dissent already recorded
- dev-feature-delivery (execution, not tradeoff decisions)

## Key Findings
- MAR (arxiv 2512.20845): persona-based critics generate richer reflections than self-critique
- Reflexion (Shinn et al., arXiv 2303.11366): verbal self-reflection stored as episodic memory raised coding-benchmark pass rates over the same model without it; read the paper for the magnitudes before quoting one
- Inner monologue patterns: reflection helps on multi-step tasks (direction only; no source here quantifies the gain)
- Over-reflection risk: too many rounds introduces NEW errors. Cap at 1 critic debate round.

## Common Mistakes
- Using MAR on every team run (too expensive for routine work)
- Using only one critic (degenerates to self-reflection — need 2+ for cross-debate)
- Running more than 1 debate round among critics (diminishing returns, new errors)
- Letting critics revise the synthesis themselves (they audit, the synthesis owner revises)

## Sources
- MAR: Multi-Agent Reflexion. arxiv 2512.20845.
- AI Agent Reflection Patterns. Zylos Research, March 2026.
- Debate-Reflection Cycles. Emergent Mind 2026.
