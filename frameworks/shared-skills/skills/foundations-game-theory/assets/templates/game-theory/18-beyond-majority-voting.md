---
name: Beyond Majority Voting (BMV)
mechanism_id: 18
layer: synthesis
status: stable
last_verified: 2026-05-01
sources:
  - https://arxiv.org/abs/2510.01499
  - https://arxiv.org/abs/2406.04692
---

# Beyond Majority Voting — Optimal Weight + Inverse Surprising Popularity

Replaces flat plurality vote in best-of-N synthesis with two cooperating signals:

1. **Optimal Weight (OW)** — each candidate answer is weighted by its estimated correctness probability, derived from agent confidence and historical calibration, not by raw vote count.
2. **Inverse Surprising Popularity (ISP)** — when a minority answer is judged "surprisingly correct" by the agents who *did not* pick it (i.e., they admit it might be right), the minority answer is upweighted instead of suppressed.

Combined output beats majority voting on multi-step reasoning benchmarks where the correct answer is rare but recognizable post-hoc.

## When to Use

- Any best-of-N synthesis step over 3+ heterogeneous proposals.
- Reasoning tasks where the popular answer is often the obvious-but-wrong one (math word problems, planning puzzles, logic riddles, ambiguous spec interpretation).
- After a debate round where the synthesizer must pick a winner across non-overlapping arguments.
- Whenever you would otherwise default to plurality vote in a Conductor-topology team.

## When NOT to Use

- Single-proposal flows. BMV needs N ≥ 3 candidates.
- Verifiable tasks with a hard oracle (compile, test pass, schema validate). Use the oracle directly.
- Highly correlated proposals from the same model with low temperature — the "minority" signal is noise, not insight.

## How It Plugs In

```yaml
synthesis:
  method: beyond_majority_voting
  inputs:
    candidates: <list of N answers + agent_id + confidence>
  steps:
    - optimal_weight:
        weight = confidence * historical_calibration[agent_id]
    - inverse_surprising_popularity:
        for each minority candidate:
          ask non-supporters: "Is this answer plausibly correct?"
          isp_score = mean(plausibility_from_non_supporters)
        upweight minority candidate by isp_score
    - rank: by (optimal_weight + lambda * isp_score)
  output:
    winner: top-ranked candidate
    runner_up: second-ranked (kept for diff-check)
```

`lambda` defaults to 0.5. Raise to 0.8 in domains where minority-correct outcomes are common (security review, edge-case design); lower to 0.2 where consensus is usually right (style, formatting, naming).

## Composition

- **Pairs well with G02 (Adversarial Debate)** — BMV is the natural synthesis layer when debate ends with no clear winner.
- **Pairs well with G11 (Prediction Market)** — confidence stakes feed directly into the Optimal Weight calculation.
- **Pairs well with G13 (Reasoning-Tree Audit)** — ISP plausibility-check question reuses the audit interface.
- **Replaces** flat majority voting wherever you previously wrote `synthesis: majority_vote`.

## Anti-Patterns

- **Confidence theater.** Agents that always say 0.9 confidence break OW. Calibrate first (G11 or CritiCal NL-critique).
- **ISP spam loop.** Asking every non-supporter about every minority answer is O(N²). Cap minority candidates at 3 per round.
- **Weight monoculture.** If all agents share the same training prior, OW becomes a flat re-vote. Force heterogeneity (different model families, different system prompts).

## Calibration

Track per-agent calibration over 20+ tasks: `correct_share / mean_confidence`. Use as multiplier in OW. Reset when system prompt or model changes.

## Sources

- arxiv 2510.01499 — *Beyond Majority Voting: LLM Aggregation by Leveraging Higher-Order Information* (2025).
- arxiv 2406.04692 — *Mixture-of-Agents Enhances Large Language Model Capabilities* (Together AI, 2024) — establishes the layered aggregation context BMV plugs into.
