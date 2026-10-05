---
description: Confidence-point staking overlay for synthesis weighting (claims weighted by stake, not volume).
last_verified: 2026-09-16
status: stable
---

# Prediction Market / Confidence Betting

Agents stake confidence points on their claims before synthesis. Higher stakes = stronger conviction. Synthesis owner uses confidence as a weighting signal, not just content quality.

## Why It Works
"Wisdom of the Silicon Crowd" (Science Advances 2024): LLM ensemble predictions rival human crowd accuracy. Fake prediction market research (arxiv 2512.05998): in a pilot study, the paper reports large bets correct ~99% of the time and small bets 74%. Confidence tracking separates genuine conviction from filler output.

## Mechanism
Each agent gets 100 confidence points per team run. After producing findings, they allocate points across their claims:
- 80+ points on a claim = "I would bet my credibility on this"
- 40-79 points = "Likely correct but some uncertainty"
- <40 points = "Plausible but uncertain"

Synthesis owner: weight findings by confidence allocation, not by output length. A 90-point finding from one agent outweighs a 30-point finding from three agents.

## Protocol
Round 1: Agents produce findings normally
Round 1.5: Each agent allocates their 100 points across their findings
Synthesis: Owner uses confidence-weighted aggregation. Report both the recommendation and the confidence distribution.
Post-synthesis: Compare confidence to outcome (if verifiable). Track calibration over time.

## When To Use
- Any team with debate: enabled. Layer on top of existing debate.
- Especially useful when synthesis tends to weight by output volume (verbose agent dominates)
- Good for `expert-board` growth mode (growth projections) and monetization mode (pricing-impact estimates)

## When NOT To Use
- When all findings are equally uncertain (no calibration signal)
- When the question is creative (no right/wrong to bet on)

## Key Finding: Calibration as Quality Signal
Agents that are well-calibrated (high confidence = correct, low confidence = uncertain) are more reliable than agents that are always high-confidence. Track calibration across runs to identify which agents to trust more over time. This connects to the Reputation-Gated Autonomy mechanism in game-theory-agent-teams.md.

## Common Mistakes
- Treating confidence as a proxy for quality (high confidence + wrong = dangerous)
- Not tracking calibration over time (one-shot confidence is noisy)
- Allowing agents to spread points evenly (defeats the purpose — force rank ordering)

## Sources
- Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, November 2024 (doi 10.1126/sciadv.adp1528).
- Fake Prediction Markets, Real Confidence Signals. arxiv 2512.05998.
- AIA Forecaster: agentic search + supervisor + calibration.
