# Mechanism: Prediction Market / Confidence Betting

**Sources**: "Wisdom of the Silicon Crowd" (Science Advances 2025), Fake Prediction Markets (arxiv 2512.05998), **PolyBench** ([2604.14199](https://arxiv.org/abs/2604.14199), Feb 2026), **LLM-as-a-Prophet / Prophet Arena** ([2510.17638](https://arxiv.org/html/2510.17638v1)).

## Domain Applications

- **Demand and revenue forecasting**: multiple models or analysts stake confidence on their forecast; ensemble weighted by conviction × calibration history, not equal weight.
- **Hiring decisions**: multiple interviewers stake confidence on candidate quality; synthesis weights by past prediction accuracy per interviewer, not by seniority.
- **Risk calibration for insurance or credit**: underwriter models stake on claim probability; CritiCal calibration step before staking reduces overconfidence bias 30-50%.
- **Agent team synthesis**: members stake confidence on findings before synthesis; synthesis owner weights by conviction, not output length; verbose agents cannot dominate.

## Problem

Synthesis owners weight findings by output length or by loudness. Verbose agents dominate synthesis regardless of evidence quality.

## Solution

Each agent stakes confidence points (0-100) on their claims. Synthesis uses confidence as a weighting signal.

## How It Works

```
Each agent gets 100 confidence points per team run.
After producing findings, allocate points across claims:
  80+ points = "I would bet my credibility on this"
  40-79 points = "Likely correct but uncertain"
  <40 points = "Plausible but speculative"

Synthesis owner: weight by confidence, not by volume.
A 90-point claim from one agent > a 30-point claim from three agents.
```

## Key Finding

Use confidence stakes as calibration signals, not as guaranteed accuracy. Track calibration across runs; agents that are consistently well-calibrated deserve higher trust tiers.

## Calibration Reality Check (PolyBench)

PolyBench (Feb 2026) evaluated seven SOTA LLMs on **36,165 live prediction-market predictions** under timestamp-locked market states. Headline finding: **only 2 of 7 models** achieved positive financial returns — MiMo-V2-Flash at +17.6% Confidence-Weighted Return and Gemini-3-Flash at +6.2%. The other 5 models lost money **despite uniformly high stated confidence**.

Operational implications for synthesis weighting:

1. **Stated confidence is systematically over-stated** in losing models. Track per-agent calibration over time and discount confidence stakes from agents whose realized accuracy diverges from stated probabilities.
2. **Hybrid is better than pure-LLM**: synthesis that combines a member's confidence stake with an external base-rate (market probability, base-rate from prior runs, calibration history) outperforms pure stated-confidence weighting.
3. **LLMs are conservative at the extremes**: even when ground-truth probability is near-certain, models cluster around 70-85%. Treat 90+% stakes as the genuine "I'd bet my credibility" signal; treat 60-80% as the noisy default.

Action: in any team using mechanism 11, log stated-confidence-vs-realized-accuracy per agent across runs. Promote agents whose calibration is good (and who can stake at the extremes when warranted) into higher reputation tiers via mechanism 5.

## CritiCal — Natural-Language Critique for Confidence Calibration

Source: *CritiCal — NL Critique for LLM Confidence Calibration* (OpenReview nkCbYg6P5p, 2025).

Numeric stakes alone do not calibrate. CritiCal adds a natural-language critique step *before* the stake is finalized:

```text
Step A — Draft claim + draft confidence (e.g., 0.85).
Step B — NL critique: "List the specific reasons this claim could be wrong.
         For each reason, estimate how it would lower confidence."
Step C — Revise confidence based on the critique. The revised number is the stake.
Step D — Synthesis owner reads the critique log alongside the stake.
```

CritiCal results: stated-vs-realized calibration error drops 30-50% across reasoning benchmarks. The critique step forces the agent to enumerate failure modes rather than emit a vibes-based number.

Plug into mechanism 11 anywhere stakes feed downstream weighting (synthesis, BMV, prediction market). Especially valuable for the verbose-but-overconfident agent class flagged by PolyBench.

## When To Use

Layer on top of any team with `debate: enabled`. Especially valuable when synthesis tends to be dominated by the most verbose agent.

## Related

- [`05-reputation-gating.md`](05-reputation-gating.md) — calibration history feeds reputation tier assignment
- [`07-mechanism-design-synthesis.md`](07-mechanism-design-synthesis.md) — confidence-weighted synthesis protocol
- [`../../../references/prediction-market-confidence.md`](../../../references/prediction-market-confidence.md) — full confidence-betting overlay
